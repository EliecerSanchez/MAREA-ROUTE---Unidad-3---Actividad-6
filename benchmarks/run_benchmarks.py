"""Benchmarks del sistema MAREA ROUTE.

Genera un mapa aleatorio, ejecuta las estrategias sobre multiples pares
origen-destino en dos escenarios (sin trafico y con marea) y guarda
los resultados en docs/results/benchmark.json.

Ejecutar: python -m benchmarks.run_benchmarks
"""

from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path

from navigation.city_map import build_grid_graph
from navigation.routing import (
    AStarLiveStrategy,
    FastestBaseStrategy,
    FastestLiveStrategy,
    NaiveBeatStrategy,
    RoutePlanner,
    ShortestDistanceStrategy,
)
from navigation.traffic import TrafficControlCenter

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "docs" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

GRID_N = 144
SEED = 20262
OD_PAIRS = 30

LIVE_NAME = FastestLiveStrategy().name
SHORTEST_NAME = ShortestDistanceStrategy().name
ASTAR_NAME = AStarLiveStrategy().name
EMPTY_NAME = ""


def _scenario_setup(traffic, scenario):
    traffic.reset(0.03)
    if scenario == "con_marea":
        traffic.simulate_marea(hotspots={"centro": (9.0, 9.0), "sur": (3.0, 4.0)}, radius=4.0, volume=1.2)


def _od_pairs(graph, count: int) -> list:
    nodes = list(graph.places.keys())
    rng = random.Random(SEED)
    pairs = set()
    while len(pairs) < count:
        a, b = rng.sample(nodes, 2)
        pairs.add((a, b))
    return list(pairs)


def _avg(data):
    return statistics.mean(data) if data else 0.0


def _hallazgo(results, scenario):
    con = {r["strategy"]: r for r in results[scenario]}
    return con


def run() -> dict:
    graph = build_grid_graph(GRID_N, seed=SEED)
    traffic = TrafficControlCenter(graph)
    planner = RoutePlanner()

    strategies = [
        NaiveBeatStrategy(),
        ShortestDistanceStrategy(),
        FastestBaseStrategy(),
        FastestLiveStrategy(),
        AStarLiveStrategy(),
    ]
    pairs = _od_pairs(graph, OD_PAIRS)
    resultados = {}

    for scenario in ("sin_marea", "con_marea"):
        _scenario_setup(traffic, scenario)
        rows = []
        for strategy in strategies:
            planner.set_strategy(strategy)
            metrics = []
            for a, b in pairs:
                started = time.perf_counter()
                ruta = planner.plan(graph, a, b)
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                metrics.append(
                    {
                        "od": f"{a}-{b}",
                        "distance_km": ruta.total_distance_km,
                        "time_min": ruta.total_time_min,
                        "nodes_expanded": ruta.nodes_expanded,
                        "exec_ms": max(elapsed_ms, ruta.execution_ms),
                    }
                )
            rows.append(
                {
                    "strategy": strategy.name,
                    "od_pairs": len(metrics),
                    "avg_distance_km": _avg(m["distance_km"] for m in metrics),
                    "avg_time_min": _avg(m["time_min"] for m in metrics),
                    "avg_nodes_expanded": _avg(m["nodes_expanded"] for m in metrics),
                    "avg_exec_ms": _avg(m["exec_ms"] for m in metrics),
                    "max_exec_ms": max(m["exec_ms"] for m in metrics),
                }
            )
        resultados[scenario] = rows

    hallazgos = {
        "pares_evaluados": len(pairs),
        "nodos_grafo": GRID_N,
        "seed_grafo": SEED,
        "ahorro_marea_min": round(
            _hallazgo(resultados, "con_marea")[SHORTEST_NAME]["avg_time_min"]
            - _hallazgo(resultados, "con_marea")[LIVE_NAME]["avg_time_min"],
            3,
        ),
        "ahorro_sin_marea_min": round(
            _hallazgo(resultados, "sin_marea")[SHORTEST_NAME]["avg_time_min"]
            - _hallazgo(resultados, "sin_marea")[LIVE_NAME]["avg_time_min"],
            3,
        ),
        "reduccion_nodos_astar_pct": round(
            100.0
            * (
                1.0
                - _hallazgo(resultados, "con_marea")[ASTAR_NAME]["avg_nodes_expanded"]
                / _hallazgo(resultados, "con_marea")[LIVE_NAME]["avg_nodes_expanded"]
            ),
            1,
        ),
        "mejora_vivo_vs_plano_pct": round(
            100.0
            * (
                1.0
                - _hallazgo(resultados, "con_marea")[LIVE_NAME]["avg_time_min"]
                / _hallazgo(resultados, "con_marea")[FastestBaseStrategy().name]["avg_time_min"]
            ),
            1,
        ),
    }
    resultados["hallazgos"] = hallazgos
    _save(resultados)
    _print(resultados)
    return resultados


def _save(resultados):
    (RESULTS_DIR / "benchmark.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False))


def _print(resultados):
    print("=" * 90)
    print("  BENCHMARKS MAREA ROUTE")
    print("=" * 90)
    for scenario in ("sin_marea", "con_marea"):
        print(f"\nESCENARIO: {scenario.upper()}")
        header = ["Estrategia", "km", "tiempo", "nodos", "ms prom", "ms max"]
        rows = [
            (
                r["strategy"],
                r["avg_distance_km"],
                r["avg_time_min"],
                r["avg_nodes_expanded"],
                r["avg_exec_ms"],
                r["max_exec_ms"],
            )
            for r in resultados[scenario]
        ]
        widths = [max(len(h), *(len(f"{c:.2f}" if isinstance(c, float) else str(c)) for c in row)) for h, row in zip(header, rows)]
        rows = [[f"{c:.2f}" if isinstance(c, float) else str(c) for c in row] for row in rows]
        line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        print(line)
        print("| " + " | ".join(h.center(w) for h, w in zip(header, widths)) + " |")
        print(line)
        for row in rows:
            print("| " + " | ".join(c.ljust(w) for c, w in zip(row, widths)) + " |")
        print(line)
    f = resultados["hallazgos"]
    print(
        f"\nHALLAZGOS\n"
        f"  ahorro de tiempo bajo marea (promedio, 30 pares OD):  {f['ahorro_marea_min']} min\n"
        f"  ahorro sin marea:                                    {f['ahorro_sin_marea_min']} min\n"
        f"  reduccion nodos expandidos A* vs Dijkstra (marea):   {f['reduccion_nodos_astar_pct']}%\n"
        f"  mejora ruta en vivo vs ruta plana (marea):           {f['mejora_vivo_vs_plano_pct']}%"
    )
    print(f"\nResultados guardados en: {RESULTS_DIR / 'benchmark.json'}")


if __name__ == "__main__":
    run()