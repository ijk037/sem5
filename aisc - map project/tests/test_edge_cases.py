"""
Unit tests for edge cases: Disconnected subgraphs, Zero-weight paths,
Cyclic graphs, Complete blockages, and boundary inputs.
"""

import pytest
import networkx as nx
from src.spatial_graph import SpatialGraph
from src.search_engine import SearchEngine


def test_start_equals_goal():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")
    engine = SearchEngine(sg)

    res = engine.a_star_search("GATE_1", "GATE_1", "shortest")
    assert res.success is True
    assert res.path == ["GATE_1"]
    assert res.total_cost == 0.0
    assert res.total_distance_meters == 0.0


def test_disconnected_subgraph_termination():
    sg = SpatialGraph()
    # Build a tiny graph with an isolated island node
    sg.graph.add_node("NODE_A", latitude=26.84, longitude=75.56, wheelchair_accessible=True)
    sg.graph.add_node("NODE_B", latitude=26.85, longitude=75.56, wheelchair_accessible=True)
    sg.graph.add_node("ISOLATED_C", latitude=26.86, longitude=75.56, wheelchair_accessible=True)
    sg.graph.add_edge("NODE_A", "NODE_B", physical_length=100.0, crowd_factor=1.0, is_blocked=False, wheelchair_accessible=True)

    engine = SearchEngine(sg)
    res_astar = engine.a_star_search("NODE_A", "ISOLATED_C")
    res_dijkstra = engine.dijkstra_search("NODE_A", "ISOLATED_C")
    res_greedy = engine.greedy_best_first_search("NODE_A", "ISOLATED_C")
    res_bfs = engine.bfs_search("NODE_A", "ISOLATED_C")

    # All must cleanly terminate and report success=False without crashing or hanging
    assert res_astar.success is False
    assert res_dijkstra.success is False
    assert res_greedy.success is False
    assert res_bfs.success is False


def test_cyclic_graph_robustness():
    sg = SpatialGraph()
    # Construct a tight 3-node cycle
    sg.graph.add_node("C1", latitude=26.840, longitude=75.560, wheelchair_accessible=True)
    sg.graph.add_node("C2", latitude=26.841, longitude=75.561, wheelchair_accessible=True)
    sg.graph.add_node("C3", latitude=26.842, longitude=75.560, wheelchair_accessible=True)
    sg.graph.add_edge("C1", "C2", physical_length=50.0, crowd_factor=1.0, is_blocked=False, wheelchair_accessible=True)
    sg.graph.add_edge("C2", "C3", physical_length=50.0, crowd_factor=1.0, is_blocked=False, wheelchair_accessible=True)
    sg.graph.add_edge("C3", "C1", physical_length=60.0, crowd_factor=1.0, is_blocked=False, wheelchair_accessible=True)

    engine = SearchEngine(sg)
    res = engine.a_star_search("C1", "C3")
    assert res.success is True
    # Optimal direct path is C1 -> C3 (60m) vs C1 -> C2 -> C3 (100m)
    assert res.path == ["C1", "C3"]
    assert res.total_cost == pytest.approx(60.0)


def test_complete_pathway_blockage():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")
    engine = SearchEngine(sg)

    # Block both entry edges from GATE_1
    sg.update_edge_condition("GATE_1", "ATM_BLOCK", is_blocked=True)
    sg.update_edge_condition("GATE_1", "JUNC_MAIN_BOULEVARD", is_blocked=True)

    res = engine.a_star_search("GATE_1", "LIBRARY_CENTRAL")
    assert res.success is False
