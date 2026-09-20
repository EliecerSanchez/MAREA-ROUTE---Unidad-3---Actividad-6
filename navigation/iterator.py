"""Patron Iterator: recorrido paso a paso de una ruta calculada."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List

from .domain import PlaceId, RoadSegment, Route


@dataclass
class RouteStep:
    index: int
    origin: PlaceId
    destination: PlaceId
    segment: RoadSegment
    distance_km: float
    minutes: float

    def describe(self) -> str:
        return (
            f"Paso {self.index}: continua {self.distance_km:.2f} km "
            f"(~{self.minutes:.2f} min) hacia {self.destination}"
        )


class RouteIterator(Iterator[RouteStep]):
    """Itera sobre los pasos de una ruta sin exponer su estructura interna."""

    def __init__(self, route: Route):
        self._route = route
        self._legs = list(route.legs)
        self._index = 0

    def __iter__(self) -> "RouteIterator":
        return self

    def __next__(self) -> RouteStep:
        if self._index >= len(self._legs):
            raise StopIteration
        parent, seg = self._legs[self._index]
        step = RouteStep(
            index=self._index + 1,
            origin=parent,
            destination=seg.target,
            segment=seg,
            distance_km=seg.distance_km,
            minutes=seg.current_minutes,
        )
        self._index += 1
        return step

    def all_steps(self) -> List[RouteStep]:
        return list(iter(self))

    def remaining_minutes(self) -> float:
        return sum(seg.current_minutes for _, seg in self._legs[self._index :])