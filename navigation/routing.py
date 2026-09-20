"""Patron Strategy: algoritmos de camino optimo intercambiables.

El RoutePlanner es el contexto; los algoritmos (Dijkstra por distancia,
Dijkstra por tiempo plano, Dijkstra por tiempo en vivo, A* con heuristica y
una linea base BFS) son estrategias que se pueden conmutar en tiempo de
ejecucion sin modificar el resto del sistema.
"""

from __future__ import annotations

import heapq
import time
from abc import ABC, abstractmethod
from collections import deque
from typing import Callable, Dict, List, Optional, Tuple

from .domain import NavigationGraph, PlaceId, RoadSegment, Route

WeightFn = Callable[[RoadSegment], float]


class RouteStrategy(ABC):
    name: str = "strategy"
    description: str = ""

    @abstractmethod
    def plan(self, graph: NavigationGraph, start: PlaceId, end: PlaceId) -> Route:
        ...


def _reconstruct(start, end, prev) -> List[Tuple[PlaceId, RoadSegment]]:
    legs: List[Tuple[PlaceId, RoadSegment]] = []
    node = end
    while node != start:
        if node not in prev:
            return []
        parent, seg = prev[node]
        legs.append((parent, seg))
        node = parent
    legs.reverse()
    return legs


def _run_weighted(
    graph: NavigationGraph,
    start: PlaceId,
    end: PlaceId,
    weight: WeightFn,
    heuristic: Optional[Callable[[PlaceId], float]] = None,
    strategy_name: str = "weighted",
) -> Route:
    """Dijkstra generico (con heuristica opcional -> A*)."""

    start_t = time.perf_counter()
    if start not in graph.places or end not in graph.places:
        raise KeyError(f"Origen '{start}' o destino '{end}' no existen en el grafo")

    dist: Dict[PlaceId, float] = {start: 0.0}
    prev: Dict[PlaceId, Tuple[PlaceId, RoadSegment]] = {}
    nodes_expanded = 0
    visited = set()

    if heuristic:
        heap = [(0.0 + heuristic(start), 0.0, start)]
    else:
        heap = [(0.0, start)]

    while heap:
        if heuristic:
            _, g, node = heapq.heappop(heap)
        else:
            g, node = heapq.heappop(heap)

        if node in visited:
            continue
        visited.add(node)
        nodes_expanded += 1

        if node == end:
            break

        for neighbor, seg in graph.neighbors(node):
            if neighbor in visited:
                continue
            candidate = g + weight(seg)
            if neighbor not in dist or candidate < dist[neighbor]:
                dist[neighbor] = candidate
                prev[neighbor] = (node, seg)
                if heuristic:
                    heapq.heappush(heap, (candidate + heuristic(neighbor), candidate, neighbor))
                else:
                    heapq.heappush(heap, (candidate, neighbor))

    legs = _reconstruct(start, end, prev)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    route = Route(start=start, end=end, legs=legs, strategy_name=strategy_name)
    route.nodes_expanded = nodes_expanded
    route.execution_ms = elapsed_ms
    return route


def _run_bfs(graph: NavigationGraph, start: PlaceId, end: PlaceId, strategy_name: str = "BFS") -> Route:
    start_t = time.perf_counter()
    if start not in graph.places or end not in graph.places:
        raise KeyError(f"Origen '{start}' o destino '{end}' no existen en el grafo")

    prev: Dict[PlaceId, Tuple[PlaceId, RoadSegment]] = {}
    visited = {start}
    queue = deque([start])
    nodes_expanded = 0

    while queue:
        node = queue.popleft()
        nodes_expanded += 1
        if node == end:
            break
        for neighbor, seg in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                prev[neighbor] = (node, seg)
                queue.append(neighbor)

    legs = _reconstruct(start, end, prev)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    route = Route(start=start, end=end, legs=legs, strategy_name=strategy_name)
    route.nodes_expanded = nodes_expanded
    route.execution_ms = elapsed_ms
    return route


def _min_minutes_per_km(graph: NavigationGraph) -> float:
    best = 60.0 / 120.0
    for seg in graph.all_road_segments():
        if seg.distance_km > 0:
            best = min(best, seg.base_minutes / seg.distance_km)
    return best


class ShortestDistanceStrategy(RouteStrategy):
    name = "Dijkstra - minima distancia"
    description = "Minimiza la distancia recorrida ignorando el trafico."

    def plan(self, graph, start, end) -> Route:
        return _run_weighted(
            graph,
            start,
            end,
            weight=lambda seg: seg.distance_km,
            strategy_name=self.name,
        )


class FastestBaseStrategy(RouteStrategy):
    name = "Dijkstra - tiempo plano (sin trafico)"
    description = "Minimiza el tiempo con velocidades estaticas de la via."

    def plan(self, graph, start, end) -> Route:
        return _run_weighted(
            graph,
            start,
            end,
            weight=lambda seg: seg.base_minutes,
            strategy_name=self.name,
        )


class FastestLiveStrategy(RouteStrategy):
    name = "Dijkstra - tiempo en vivo (marea)"
    description = "Minimiza el tiempo teniendo en cuenta la congestion actual (marea)."

    def plan(self, graph, start, end) -> Route:
        return _run_weighted(
            graph,
            start,
            end,
            weight=lambda seg: seg.current_minutes,
            strategy_name=self.name,
        )


class AStarLiveStrategy(RouteStrategy):
    name = "A* - tiempo en vivo + heuristica"
    description = "Igual optimo que Dijkstra en vivo pero expande menos nodos."

    def plan(self, graph, start, end) -> Route:
        end_place = graph.places[end]
        unit_h = _min_minutes_per_km(graph)

        def heuristic(node: PlaceId) -> float:
            place = graph.places[node]
            return place.distance_to(end_place) * unit_h

        return _run_weighted(
            graph,
            start,
            end,
            weight=lambda seg: seg.current_minutes,
            heuristic=heuristic,
            strategy_name=self.name,
        )


class NaiveBeatStrategy(RouteStrategy):
    name = "BFS - saltos (linea base)"
    description = "Cuenta pasos sin considerar pesos (linea base no optima)."

    def plan(self, graph, start, end) -> Route:
        return _run_bfs(graph, start, end, strategy_name=self.name)


class RoutePlanner:
    """Contexto del patron Strategy: delega el calculo en la estrategia activa."""

    def __init__(self, strategy: Optional[RouteStrategy] = None) -> None:
        self._strategy: RouteStrategy = strategy or FastestLiveStrategy()

    @property
    def strategy(self) -> RouteStrategy:
        return self._strategy

    def set_strategy(self, strategy: RouteStrategy) -> "RoutePlanner":
        self._strategy = strategy
        return self

    def plan(self, graph: NavigationGraph, start: PlaceId, end: PlaceId) -> Route:
        return self._strategy.plan(graph, start, end)