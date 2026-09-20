"""Modelo de dominio: lugares, grafo de calles y rutas.

Incluye la implementacion del patron Composite (PlaceGroup) y los objetos
Route / RoadSegment que modelan el resultado de la navegacion.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

PlaceId = str


class Place:
    """Lugar identificable dentro del mapa de la ciudad."""

    def __init__(self, place_id: PlaceId, name: str, category: str, x: float, y: float):
        self.place_id = place_id
        self.name = name
        self.category = category
        self.x = x
        self.y = y

    def distance_to(self, other: "Place") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"Place({self.place_id!r}, {self.name!r})"


class PlaceGroup:
    """Patron Composite: agrupa destinos y los trata como un destino unico.

    Permite navegar hacia un conjunto de lugares (por ejemplo una zona de
    entregas) reutilizando la misma interfaz de un Place individual.
    """

    def __init__(self, name: str, children: Optional[Iterable[object]] = None):
        self.name = name
        self._children: List[object] = list(children or [])

    def add(self, child: object) -> "PlaceGroup":
        self._children.append(child)
        return self

    def remove(self, child: object) -> None:
        self._children.remove(child)

    def children(self) -> List[object]:
        return list(self._children)

    def leaves(self) -> Iterator[Place]:
        for child in self._children:
            if isinstance(child, PlaceGroup):
                yield from child.leaves()
            else:
                yield child

    def __iter__(self) -> Iterator[Place]:
        return PlaceIterator(self.leaves())

    def __len__(self) -> int:
        return sum(1 for _ in self.leaves())


class PlaceIterator(Iterator[Place]):
    """Patron Iterator: recorre la coleccion de lugares sin exponer su estructura."""

    def __init__(self, places: Iterable[Place]):
        self._items: List[Place] = list(places)
        self._index = 0

    def __iter__(self) -> "PlaceIterator":
        return self

    def __next__(self) -> Place:
        if self._index >= len(self._items):
            raise StopIteration
        item = self._items[self._index]
        self._index += 1
        return item


@dataclass
class RoadSegment:
    source: PlaceId
    target: PlaceId
    distance_km: float
    base_minutes: float
    congestion: float = 0.0

    @property
    def current_minutes(self) -> float:
        return self.base_minutes * (1.0 + self.congestion)

    @property
    def speed_kmh(self) -> float:
        if self.base_minutes <= 0:
            return 0.0
        return self.distance_km / (self.base_minutes / 60.0)


class NavigationGraph:
    """Grafo dirigido (con pares bidireccionales) sobre los lugares de la ciudad."""

    def __init__(self) -> None:
        self.places: Dict[PlaceId, Place] = {}
        self._adj: Dict[PlaceId, List[Tuple[PlaceId, RoadSegment, bool]]] = defaultdict(list)
        self._undirected_edges: List[RoadSegment] = []

    def add_place(self, place: Place) -> "NavigationGraph":
        self.places[place.place_id] = place
        return self

    def add_road(
        self,
        source: PlaceId,
        target: PlaceId,
        distance_km: float,
        base_minutes: float,
        bidirectional: bool = True,
    ) -> RoadSegment:
        fwd = RoadSegment(source, target, distance_km, base_minutes)
        self._adj[source].append((target, fwd, True))
        self._undirected_edges.append(fwd)
        if bidirectional:
            rev = RoadSegment(target, source, distance_km, base_minutes)
            self._adj[target].append((source, rev, True))
        return fwd

    def neighbors(self, node: PlaceId) -> List[Tuple[PlaceId, RoadSegment]]:
        return [(n, seg) for n, seg, _ in self._adj.get(node, [])]

    def segment(self, source: PlaceId, target: PlaceId) -> Optional[RoadSegment]:
        for n, seg, _ in self._adj.get(source, []):
            if n == target:
                return seg
        return None

    def all_road_segments(self) -> List[RoadSegment]:
        return self._undirected_edges

    def edge_time(self, source: PlaceId, target: PlaceId) -> Optional[float]:
        seg = self.segment(source, target)
        return seg.current_minutes if seg else None

    def node_count(self) -> int:
        return len(self.places)


@dataclass
class Route:
    start: PlaceId
    end: PlaceId
    legs: List[Tuple[PlaceId, RoadSegment]] = field(default_factory=list)
    strategy_name: str = "?"
    nodes_expanded: int = 0
    execution_ms: float = 0.0

    @property
    def waypoints(self) -> List[PlaceId]:
        pts = [self.start]
        for parent, seg in self.legs:
            pts.append(seg.target)
        return pts

    @property
    def total_distance_km(self) -> float:
        return sum(seg.distance_km for _, seg in self.legs)

    @property
    def total_time_min(self) -> float:
        return sum(seg.current_minutes for _, seg in self.legs)

    @property
    def total_base_time_min(self) -> float:
        return sum(seg.base_minutes for _, seg in self.legs)

    def road_names(self) -> set:
        return {seg.target for _, seg in self.legs}

    def __len__(self) -> int:
        return len(self.legs)

    def __repr__(self) -> str:
        return (
            f"Route({self.start}->{self.end}, legs={len(self.legs)}, "
            f"km={self.total_distance_km:.2f}, min={self.total_time_min:.2f})"
        )