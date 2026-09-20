"""Demo por consola del sistema MAREA ROUTE.

Ejecutar desde la raiz del proyecto:
    python -m navigation.demo
"""

from __future__ import annotations

from .city_map import build_city, build_groups, build_traffic
from .commands import ChangeDestinationCommand, CommandHistory, RerouteCommand
from .facade import Navigator
from .routing import (
    AStarLiveStrategy,
    FastestBaseStrategy,
    FastestLiveStrategy,
    NaiveBeatStrategy,
    RoutePlanner,
    ShortestDistanceStrategy,
)
from .traffic import TrafficLogger

ROUTE_HEADER = ["Estrategia", "km", "min plano", "min marea", "nodos", "ms"]


def _fmt(value) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def print_table(headers, rows):
    headers = list(headers)
    rows = [[_fmt(c) for c in row] for row in rows]
    widths = [max(len(h), *(len(rw[i]) for rw in rows)) for i, h in enumerate(headers)]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(line)
    print("| " + " | ".join(h.center(w) for h, w in zip(headers, widths)) + " |")
    print(line)
    for rw in rows:
        print("| " + " | ".join(c.ljust(w) for c, w in zip(rw, widths)) + " |")
    print(line)


def run():
    print("=" * 78)
    print("  MAREA ROUTE - Sistema de navegacion inteligente (U3 - Actividad 6)")
    print("=" * 78)

    graph = build_city()
    traffic = build_traffic(graph)
    logger = TrafficLogger()
    traffic.attach(logger)

    print(f"\n[1] CIUDAD CARGADA: {graph.node_count()} lugares, {len(graph.all_road_segments())} tramos de via")
    print_table(
        ["id", "Lugar", "Categoria"],
        [(pid, p.name, p.category) for pid, p in graph.places.items()],
    )

    groups = build_groups(graph)
    grupo = groups["norte"]
    print("\n[2] PATRON COMPOSITE: agrupacion de destinos")
    print(f"    Grupo '{grupo.name}' con {len(grupo)} destinos hijos.")
    print("    Iterator interno -> recorre los destinos del grupo:")
    for i, place in enumerate(grupo, start=1):
        print(f"      {i}. {place.name} ({place.category})")

    traffic.reset(0.05)
    traffic.simulate_marea(volume=1.2)
    print("\n[3] PATRON OBSERVER: se activa la 'marea' de trafico en el centro")
    for message in logger.messages[:8]:
        print("    " + message)

    planner = RoutePlanner()
    navigator = Navigator(planner, traffic)

    origen, destino = "UNAB", "Estadio"
    print(f"\n[4] PATRON STRATEGY: comparacion de estrategias {origen} -> {destino}")
    estrategias = [
        NaiveBeatStrategy(),
        ShortestDistanceStrategy(),
        FastestBaseStrategy(),
        FastestLiveStrategy(),
        AStarLiveStrategy(),
    ]
    filas_cache = [
        (
            estrategia.name,
            ruta.total_distance_km,
            ruta.total_base_time_min,
            ruta.total_time_min,
            ruta.nodes_expanded,
            ruta.execution_ms,
        )
        for estrategia in estrategias
        for ruta in [planner.set_strategy(estrategia).plan(graph, origen, destino)]
    ]
    print_table(ROUTE_HEADER, filas_cache)

    por_nombre = {row[0]: row for row in filas_cache}
    min_dist = por_nombre[ShortestDistanceStrategy().name]
    live = por_nombre[FastestLiveStrategy().name]
    ahorro = min_dist[3] - live[3]
    print(f"\n    La estrategia en vivo ahorra {ahorro:.2f} min vs. la de minima distancia "
          f"({live[3]:.2f} vs {min_dist[3]:.2f}) con {live[1]:.2f} km.")

    planner.set_strategy(FastestLiveStrategy())
    navigator.set_destination(origen, destino)
    ruta_inicial = navigator.route
    print(f"\n[5] RUTA ACTIVA (FastestLive): {ruta_inicial.total_distance_km:.2f} km, "
          f"{ruta_inicial.total_time_min:.2f} min.")

    print("\n[6] PATRON OBSERVER: sube la congestion sobre un tramo de la ruta actual")
    primer_tramo = ruta_inicial.legs[0]
    traffic.raise_congestion(primer_tramo[0], primer_tramo[1].target, 0.6)
    for message in navigator.notifications[-3:]:
        print("    " + message)

    history = CommandHistory()
    print("\n[7] PATRON COMMAND: replanificacion con soporte de undo")
    history.execute(RerouteCommand(navigator))
    nueva = navigator.route
    print(f"    ({history.size}) RerouteCommand -> nueva ruta: {nueva.total_time_min:.2f} min, "
          f"{nueva.total_distance_km:.2f} km")

    print("\n[8] PATRON ITERATOR: navegacion paso a paso de la ruta replanificada")
    for paso in navigator.steps():
        print("    " + paso.describe())

    print("\n[9] COMMAND + UNDO: otros comandos del historial")
    history.execute(ChangeDestinationCommand(navigator, "UNAB", "Aeropuerto"))
    print(f"    ({history.size}) ChangeDestinationCommand -> destino ahora: {navigator.destination}")
    history.undo()
    print(f"    ({history.size}) undo -> destino vuelto a: {navigator.destination}")
    history.undo()
    print(f"    ({history.size}) undo -> ruta replanificada revertida a: "
          f"{navigator.route.strategy_name}")


if __name__ == "__main__":
    run()
