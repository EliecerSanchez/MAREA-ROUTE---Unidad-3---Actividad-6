"""Facade: Navigator orquesta el sistema y actua como observador del trafico."""

from __future__ import annotations

from typing import List, Optional

from .domain import NavigationGraph, PlaceId, Route
from .iterator import RouteIterator
from .routing import RoutePlanner, RouteStrategy
from .traffic import Observer, TrafficControlCenter


class Navigator(Observer):
    """Cara unica hacia el sistema de navegacion; observa el trafico."""

    def __init__(self, planner: RoutePlanner, traffic: TrafficControlCenter) -> None:
        self.planner = planner
        self.traffic = traffic
        self.position: Optional[PlaceId] = None
        self.destination: Optional[PlaceId] = None
        self.route: Optional[Route] = None
        self.notifications: List[str] = []
        self.pending_replan = False
        traffic.attach(self)

    def set_destination(self, start: PlaceId, end: PlaceId) -> Route:
        if start not in self.traffic.graph.places or end not in self.traffic.graph.places:
            raise KeyError(f"Origen '{start}' o destino '{end}' no existen en el grafo")
        self.position = start
        self.destination = end
        self.route = self.planner.plan(self.traffic.graph, start, end)
        return self.route

    def reroute(self, strategy: Optional[RouteStrategy] = None) -> Route:
        if strategy is not None:
            self.planner.set_strategy(strategy)
        if self.position is None or self.destination is None:
            raise RuntimeError("No hay un viaje activo para replanificar")
        self.route = self.planner.plan(self.traffic.graph, self.position, self.destination)
        self.pending_replan = False
        self.notifications.append(
            f"[Navigator] Ruta replanificada con estrategia '{self.planner.strategy.name}'."
        )
        return self.route

    def set_route(self, route: Optional[Route], planner_flag: bool = True) -> None:
        self.route = route
        if planner_flag:
            self.pending_replan = False

    def restore(self, start: Optional[PlaceId], end: Optional[PlaceId], route: Optional[Route]) -> None:
        self.position = start
        self.destination = end
        self.route = route

    def steps(self) -> RouteIterator:
        if self.route is None:
            raise RuntimeError("No hay ruta activa por la cual navegar")
        return RouteIterator(self.route)

    def update(self, subject: TrafficControlCenter, event: str, payload: object) -> None:
        if event != "congestion":
            return
        source, target, value = payload
        self.notifications.append(
            f"[Navigator] Cambio de trafico detectado en {source}-{target} "
            f"(congestion={value:.2f})."
        )
        if self.route is None:
            return
        for parent, seg in self.route.legs:
            if (parent == source and seg.target == target) or (
                parent == target and seg.target == source
            ):
                if value >= 0.5:
                    self.pending_replan = True
                    expected = self.route.total_time_min
                    self.notifications.append(
                        f"[Navigator] ALERTA: la ruta actual pasa por un tramo "
                        f"congestionado ({parent}-{seg.target}). Se recomienda replanificar."
                    )