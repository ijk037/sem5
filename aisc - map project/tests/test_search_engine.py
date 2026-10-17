"""
Unit tests for Phase 2: Search Engine (A*, Dijkstra, Greedy, BFS) and Heuristic Guarantees.
"""

import pytest
from src.spatial_graph import SpatialGraph
from src.search_engine import SearchEngine


@pytest.fixture
def graph_and_engine():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")
    engine = SearchEngine(sg)
    return sg, engine


def test_a_star_optimality_vs_dijkstra(graph_and_engine):
    sg, engine = graph_and_engine
    start = "GATE_1"
    goal = "SPORTS_COMPLEX_INDOOR"

    res_astar = engine.a_star_search(start, goal, "shortest")
    res_dijkstra = engine.dijkstra_search(start, goal, "shortest")

    assert res_astar.success is True
    assert res_dijkstra.success is True
    # A* cost must match Dijkstra's optimal cost
    assert res_astar.total_cost == pytest.approx(res_dijkstra.total_cost, abs=1e-3)
    assert res_astar.total_distance_meters == pytest.approx(res_dijkstra.total_distance_meters, abs=1e-3)
    # A* should expand fewer or equal nodes compared to Dijkstra
    assert res_astar.node_expansions <= res_dijkstra.node_expansions


def test_all_algorithms_find_path(graph_and_engine):
    sg, engine = graph_and_engine
    start = "HOSTEL_B1_B2"
    goal = "MESS_GRAND"

    results = engine.run_all(start, goal, "shortest")
    for algo, res in results.items():
        assert res.success is True
        assert len(res.path) >= 2
        assert res.path[0] == start
        assert res.path[-1] == goal


def test_heuristic_admissibility_and_consistency(graph_and_engine):
    sg, engine = graph_and_engine
    goal = "FOOD_COURT"

    # For every node, h(n) <= true shortest distance h*(n)
    for node in sg.graph.nodes:
        if node == goal:
            continue
        h_val = engine.heuristic(node, goal, "shortest")
        res_dijkstra = engine.dijkstra_search(node, goal, "shortest")
        if res_dijkstra.success:
            true_cost = res_dijkstra.total_cost
            assert h_val <= true_cost + 1e-4, f"Heuristic overestimation at node {node}: h={h_val}, true={true_cost}"

    # Consistency (Monotonicity): h(u) <= c(u, v) + h(v) for all edges (u, v)
    for u, v, data in sg.graph.edges(data=True):
        if data.get("is_blocked", False):
            continue
        c_uv = float(data.get("physical_length", 0.0))
        h_u = engine.heuristic(u, goal, "shortest")
        h_v = engine.heuristic(v, goal, "shortest")
        assert h_u <= c_uv + h_v + 1e-4, f"Consistency violated on edge ({u}, {v}): h({u})={h_u} > {c_uv} + h({v})={h_v}"


def test_wheelchair_accessible_routing(graph_and_engine):
    sg, engine = graph_and_engine
    # AB1_EAST_STAIRS has stairs only
    res = engine.a_star_search("AB1_MAIN", "LIBRARY_CENTRAL", "accessible")
    assert res.success is True
    # The path must NOT contain the stairs-only node
    assert "AB1_EAST_STAIRS" not in res.path
    # It must route through the ramp or accessible kiosk walkway
    assert "NESCAFE_KIOSK" in res.path


def test_quickest_mode_crowd_scaling(graph_and_engine):
    sg, engine = graph_and_engine
    res = engine.a_star_search("GATE_1", "FOOD_COURT", "quickest")
    assert res.success is True
    assert res.estimated_time_seconds > 0.0
