"""Patron Observer: Control central de trafico y sus observadores.

El TrafficControlCenter actua como Sujeto (Subject) y notifica a sus
observadores (Navigator y TrafficLogger) cada vez que cambia la congestion
de un tramo de calle.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from .domain import NavigationGraph, PlaceId, RoadSegment


class Observer(ABC):
    @abstractmethod
    def update(self, subject: "TrafficControlCenter", event: str, payload: object) -> None:
        ...


class TrafficControlCenter:
    """Sujeto que mantiene el estado de congestion y notifica cambios."""

    def __init__(self, graph: NavigationGraph) -> None:
        self.graph = graph
        self._observers: List[Observer] = []
        self._congestion: Dict[Tuple[PlaceId, PlaceId], float] = {}
        self._events: List[str] = []

    def attach(self, observer: Observer) -> "TrafficControlCenter":
        if observer not in self._observers:
            self._observers.append(observer)
        return self

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def set_congestion(self, source: PlaceId, target: PlaceId, value: float) -> None:
        bounded = max(0.0, min(0.95, value))
        seg = self.graph.segment(source, target)
        reverse = self.graph.segment(target, source)
        if seg:
            seg.congestion = bounded
        if reverse:
            reverse.congestion = bounded
        self._congestion[(source, target)] = bounded
        self._congestion[(target, source)] = bounded
        self._events.append(f"congestion {source}->{target} = {bounded:.2f}")
        self._notify("congestion", (source, target, bounded))

    def raise_congestion(self, source: PlaceId, target: PlaceId, delta: float) -> None:
        current = self._congestion.get((source, target), 0.0)
        self.set_congestion(source, target, current + delta)

    def congestion_of(self, source: PlaceId, target: PlaceId) -> float:
        return self._congestion.get((source, target), 0.0)

    def reset(self, level: float = 0.0) -> None:
        for source, target, seg in self._iter_segments():
            seg.congestion = min(max(level, 0.0), 0.95)
        self._congestion.clear()
        self._notify("reset", level)

    def simulate_marea(self, volume: float = 1.0, hotspots: Optional[Dict[str, Tuple[float, float]]] = None, radius: float = 3.0) -> None:
        """Incrementa la congestion en las calles cercanas a hotspots urbanos."""
        if hotspots is None:
            hotspots = {
                "Zona_Centro": (5.4, 5.0),
                "Parque_Principal": (4.5, 4.6),
                "Mercado_Principal": (2.4, 4.3),
            }
        for source, target, seg in self._iter_segments():
            place_s = self.graph.places.get(source)
            place_t = self.graph.places.get(target)
            if not place_s or not place_t:
                continue
            mid = ((place_s.x + place_t.x) / 2.0, (place_s.y + place_t.y) / 2.0)
            boost = 0.0
            for _, (hx, hy) in hotspots.items():
                dist = math_hypot(mid[0] - hx, mid[1] - hy)
                if dist < radius:
                    falloff = (1.0 - dist / radius) * volume
                    boost = max(boost, falloff)
            if boost > 0.0:
                self.raise_congestion(source, target, boost * 0.9)
        self._notify("marea", volume)

    def clear_events(self) -> None:
        self._events.clear()

    @property
    def event_log(self) -> List[str]:
        return list(self._events)

    def _iter_segments(self):
        seen = set()
        for source, target, seg in _walk(self.graph):
            key = tuple(sorted((source, target)))
            if key in seen:
                continue
            seen.add(key)
            yield source, target, seg

    def _notify(self, event: str, payload: object) -> None:
        for observer in list(self._observers):
            observer.update(self, event, payload)


def _walk(graph: NavigationGraph):
    for node in graph.places:
        for neighbor, seg, directed in graph._adj.get(node, []):
            if directed:
                yield node, neighbor, seg


def math_hypot(dx: float, dy: float) -> float:
    import math

    return math.hypot(dx, dy)


class TrafficLogger(Observer):
    """Registra los eventos de trafico recibidos (observador pasivo)."""

    def __init__(self) -> None:
        self.messages: List[str] = []

    def update(self, subject, event: str, payload: object) -> None:
        if event == "congestion":
            source, target, value = payload
            self.messages.append(f"[TrafficLogger] Subio congestion en {source}-{target}: {value:.2f}")
        elif event == "marea":
            self.messages.append(f"[TrafficLogger] Marea de trafico activada (volumen={payload}).")
        elif event == "reset":
            self.messages.append(f"[TrafficLogger] Estado de trafico reiniciado a {payload}.")