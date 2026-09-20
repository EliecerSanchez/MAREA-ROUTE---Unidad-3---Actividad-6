"""Construccion del mapa de demostracion (ciudad ficticia) y utilidades."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from .domain import NavigationGraph, Place
from .traffic import TrafficControlCenter

PLACES: List[Tuple[str, str, str, float, float]] = [
    ("UNAB", "Universidad", "educacion", 1.0, 8.0),
    ("Terminal", "Terminal de Transporte", "transporte", 1.2, 5.5),
    ("Mercado", "Mercado Principal", "comercio", 2.0, 4.2),
    ("Biblioteca", "Biblioteca Publica", "cultura", 3.0, 3.0),
    ("Parque", "Parque Principal", "recreacion", 4.5, 4.6),
    ("Hospital", "Hospital Central", "salud", 3.8, 7.2),
    ("Cacique", "CC Cacique", "comercio", 5.0, 2.0),
    ("CentroC", "CC Centro Ciudad", "comercio", 6.0, 4.2),
    ("Museo", "Museo del Oro", "cultura", 6.8, 6.0),
    ("ZonaG", "Zona Gastronomica", "ocio", 7.8, 7.0),
    ("PlazaCC", "CC Plaza", "comercio", 6.5, 7.8),
    ("UIS", "Universidad Industrial", "educacion", 8.5, 8.2),
    ("Estadio", "Estadio Municipal", "deporte", 7.5, 2.5),
    ("Aeropuerto", "Aeropuerto", "transporte", 9.5, 5.0),
    ("ZonaR", "Zona Rosa", "ocio", 4.0, 6.2),
    ("Alcaldia", "Alcaldia Municipal", "gobierno", 5.2, 5.5),
]

KM_PER_UNIT = 1.1

ROADS: List[Tuple[str, str, float]] = [
    ("UNAB", "UIS", 55),
    ("UNAB", "Terminal", 55),
    ("UNAB", "Hospital", 25),
    ("Terminal", "Cacique", 45),
    ("Terminal", "Hospital", 45),
    ("Terminal", "Mercado", 25),
    ("Cacique", "Estadio", 55),
    ("Cacique", "Biblioteca", 25),
    ("Cacique", "CentroC", 40),
    ("Estadio", "Aeropuerto", 55),
    ("Estadio", "CentroC", 35),
    ("Aeropuerto", "UIS", 55),
    ("Aeropuerto", "ZonaG", 45),
    ("UIS", "PlazaCC", 55),
    ("PlazaCC", "ZonaG", 45),
    ("PlazaCC", "Hospital", 45),
    ("Hospital", "ZonaR", 20),
    ("Hospital", "Parque", 20),
    ("ZonaR", "Parque", 25),
    ("ZonaR", "Alcaldia", 25),
    ("Parque", "Mercado", 25),
    ("Parque", "Biblioteca", 20),
    ("Parque", "CentroC", 35),
    ("Parque", "Alcaldia", 25),
    ("Parque", "Museo", 25),
    ("Mercado", "Biblioteca", 20),
    ("Biblioteca", "CentroC", 30),
    ("Museo", "CentroC", 25),
    ("Museo", "Alcaldia", 25),
    ("Museo", "ZonaG", 25),
    ("CentroC", "Alcaldia", 35),
]


def build_city() -> NavigationGraph:
    graph = NavigationGraph()
    for pid, name, category, x, y in PLACES:
        graph.add_place(Place(pid, name, category, x, y))

    for a, b, speed in ROADS:
        a_pt = graph.places[a]
        b_pt = graph.places[b]
        distance = a_pt.distance_to(b_pt) * KM_PER_UNIT
        base_minutes = distance / speed * 60.0
        graph.add_road(a, b, distance, base_minutes)
    return graph


def build_traffic(graph: NavigationGraph) -> TrafficControlCenter:
    return TrafficControlCenter(graph)


def build_groups(graph: NavigationGraph) -> Dict[str, object]:
    from .domain import PlaceGroup

    zona_norte = PlaceGroup("Zona de entregas Norte", [graph.places["UNAB"], graph.places["UIS"]])
    zona_centro = PlaceGroup(
        "Zona cultural Centro",
        [graph.places["Museo"], graph.places["Biblioteca"], graph.places["Parque"]],
    )
    comercial = PlaceGroup(
        "Corredor comercial",
        [graph.places["Cacique"], graph.places["CentroC"], graph.places["PlazaCC"]],
    )
    return {"norte": zona_norte, "centro": zona_centro, "comercial": comercial}


def distance_km_between(graph: NavigationGraph, a: str, b: str) -> float:
    return graph.places[a].distance_to(graph.places[b]) * KM_PER_UNIT


def build_grid_graph(n: int, seed: int = 20262, spacing: float = 1.5) -> NavigationGraph:
    """Genera una malla urbana con avenidas rapidas cada 3 lineas y calles locales."""
    import math as _math

    cols = int(_math.sqrt(n))
    rows = (n + cols - 1) // cols
    graph = NavigationGraph()
    arterial_every = 3

    for i in range(n):
        r, c = divmod(i, cols)
        graph.add_place(Place(f"N{i:03d}", f"Nodo {i:03d}", "nodo", c * spacing, r * spacing))

    def link(a: str, b: str, distance: float, speed: float) -> None:
        base_minutes = distance / speed * 60.0
        graph.add_road(a, b, distance, base_minutes)

    for i in range(n):
        r, c = divmod(i, cols)
        _local = spacing
        _arterial = spacing * arterial_every
        if c + 1 < cols:
            link(f"N{i:03d}", f"N{i+1:03d}", _local, 28)
        if r + 1 < rows and i + cols < n:
            link(f"N{i:03d}", f"N{i+cols:03d}", _local, 28)
        if c + arterial_every < cols:
            link(f"N{i:03d}", f"N{i+arterial_every:03d}", _arterial, 55)
        if r + arterial_every < rows and i + cols * arterial_every < n:
            link(f"N{i:03d}", f"N{i+cols*arterial_every:03d}", _arterial, 55)
    return graph