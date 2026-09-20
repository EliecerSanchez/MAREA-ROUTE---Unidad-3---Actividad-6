"""MAREA ROUTE - Sistema de navegacion inteligente sensible a las mareas de trafico.

Arquitectura de demostracion para la Unidad 3 - Actividad 6 del curso de
Arquitectura de Software. Integra los patrones de diseno Strategy, Observer,
Command, Iterator y Composite en torno a la optimizacion de rutas urbanas.
"""

from .domain import (
    NavigationGraph,
    Place,
    PlaceGroup,
    PlaceIterator,
    RoadSegment,
    Route,
)
from .facade import Navigator
from .commands import (
    ChangeDestinationCommand,
    CommandHistory,
    RerouteCommand,
)
from .routing import (
    AStarLiveStrategy,
    FastestBaseStrategy,
    FastestLiveStrategy,
    NaiveBeatStrategy,
    RoutePlanner,
    ShortestDistanceStrategy,
)
from .traffic import TrafficControlCenter
from .iterator import RouteIterator, RouteStep

__version__ = "1.0.0"

__all__ = [
    "AStarLiveStrategy",
    "ChangeDestinationCommand",
    "CommandHistory",
    "FastestBaseStrategy",
    "FastestLiveStrategy",
    "NaiveBeatStrategy",
    "NavigationGraph",
    "Navigator",
    "Place",
    "PlaceGroup",
    "PlaceIterator",
    "RerouteCommand",
    "RoadSegment",
    "Route",
    "RouteIterator",
    "RoutePlanner",
    "RouteStep",
    "ShortestDistanceStrategy",
    "TrafficControlCenter",
]