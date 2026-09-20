"""Pruebas unitarias del sistema MAREA ROUTE.

Ejecutar: python -m unittest discover -s tests
"""

import random
import unittest

from navigation.city_map import build_city, build_traffic
from navigation.commands import ChangeDestinationCommand, CommandHistory, RerouteCommand
from navigation.domain import NavigationGraph, Place, PlaceGroup
from navigation.facade import Navigator
from navigation.iterator import RouteIterator
from navigation.routing import (
    AStarLiveStrategy,
    FastestBaseStrategy,
    FastestLiveStrategy,
    NaiveBeatStrategy,
    RoutePlanner,
    ShortestDistanceStrategy,
)
from navigation.traffic import TrafficControlCenter


def _tiny_graph() -> NavigationGraph:
    g = NavigationGraph()
    g.add_place(Place("A", "a", "x", 0, 0))
    g.add_place(Place("B", "b", "x", 1, 0))
    g.add_place(Place("C", "c", "x", 2, 0))
    g.add_place(Place("D", "d", "x", 1, 1))
    g.add_road("A", "B", 1.0, 2.0)
    g.add_road("B", "C", 1.0, 2.0)
    g.add_road("A", "D", 10.0, 20.0)
    g.add_road("D", "C", 10.0, 20.0)
    return g


class TestStrategy(unittest.TestCase):
    def test_shortest_path_known(self):
        g = _tiny_graph()
        ruta = ShortestDistanceStrategy().plan(g, "A", "C")
        self.assertAlmostEqual(ruta.total_distance_km, 2.0, places=6)
        self.assertEqual(ruta.waypoints, ["A", "B", "C"])

    def test_astar_equals_dijkstra_live(self):
        g = build_city()
        d = FastestLiveStrategy().plan(g, "UNAB", "Estadio")
        a = AStarLiveStrategy().plan(g, "UNAB", "Estadio")
        self.assertAlmostEqual(a.total_time_min, d.total_time_min, places=6)
        self.assertAlmostEqual(a.total_distance_km, d.total_distance_km, places=6)
        self.assertLessEqual(a.nodes_expanded, d.nodes_expanded)

    def test_live_beats_shortest_under_marea(self):
        g = build_city()
        t = build_traffic(g)
        t.reset(0.05)
        t.simulate_marea(volume=1.2)
        corta = ShortestDistanceStrategy().plan(g, "UNAB", "Estadio")
        viva = FastestLiveStrategy().plan(g, "UNAB", "Estadio")
        self.assertTrue(viva.total_time_min < corta.total_time_min)
        self.assertTrue(viva.total_distance_km > corta.total_distance_km)

    def test_bfs_ignores_weights(self):
        g = _tiny_graph()
        ruta = NaiveBeatStrategy().plan(g, "A", "C")
        self.assertEqual(len(ruta.legs), 2)


class TestObserver(unittest.TestCase):
    def test_observers_notified(self):
        g = build_city()
        t = build_traffic(g)
        logger = []
        pause = _Recorder(logger)
        t.attach(pause)
        t.set_congestion("UNAB", "UIS", 0.7)
        self.assertEqual(len(logger), 1)

    def test_navigator_flags_replan(self):
        g = build_city()
        t = build_traffic(g)
        t.reset(0.05)
        t.simulate_marea(volume=1.2)
        planner = RoutePlanner(FastestLiveStrategy())
        nav = Navigator(planner, t)
        nav.set_destination("UNAB", "Estadio")
        self.assertFalse(nav.pending_replan)
        t.raise_congestion("UNAB", "UIS", 0.6)
        self.assertTrue(nav.pending_replan)


class _Recorder:
    def __init__(self, sink):
        self._sink = sink

    def update(self, subject, event, payload):
        self._sink.append((event, payload))


class TestCommand(unittest.TestCase):
    def test_destination_undo(self):
        g = build_city()
        t = build_traffic(g)
        nav = Navigator(RoutePlanner(), t)
        nav.set_destination("UNAB", "Estadio")
        history = CommandHistory()
        history.execute(ChangeDestinationCommand(nav, "UNAB", "Aeropuerto"))
        self.assertEqual(nav.destination, "Aeropuerto")
        history.undo()
        self.assertEqual(nav.destination, "Estadio")

    def test_reroute_undo_restores_route(self):
        g = build_city()
        t = build_traffic(g)
        t.simulate_marea(volume=1.2)
        nav = Navigator(RoutePlanner(FastestLiveStrategy()), t)
        nav.set_destination("UNAB", "Estadio")
        before = nav.route
        history = CommandHistory()
        history.execute(RerouteCommand(nav))
        self.assertIsNot(nav.route, before)
        history.undo()
        self.assertIs(nav.route, before)


class TestIteratorAndComposite(unittest.TestCase):
    def test_route_iterator(self):
        g = _tiny_graph()
        ruta = ShortestDistanceStrategy().plan(g, "A", "C")
        steps = RouteIterator(ruta).all_steps()
        self.assertEqual([s.origin for s in steps], ["A", "B"])
        self.assertEqual([s.destination for s in steps], ["B", "C"])

    def test_composite_group(self):
        g = build_city()
        grupo = PlaceGroup("Comercial")
        grupo.add(PlaceGroup("Sur", [g.places["Estadio"], g.places["Cacique"]]))
        grupo.add(g.places["CentroC"])
        self.assertEqual(len(grupo), 3)
        leaves = list(grupo)
        self.assertEqual({l.place_id for l in leaves}, {"Estadio", "Cacique", "CentroC"})


class TestBenchmarkConsistency(unittest.TestCase):
    def test_random_graph_reachable_and_optimal(self):
        import navigation.city_map as cm

        g = cm.build_grid_graph(49, seed=11)
        start, end = "N000", "N048"
        d = FastestLiveStrategy().plan(g, start, end)
        a = AStarLiveStrategy().plan(g, start, end)
        self.assertTrue(len(d.legs) > 0)
        self.assertAlmostEqual(a.total_time_min, d.total_time_min, places=6)


if __name__ == "__main__":
    unittest.main()