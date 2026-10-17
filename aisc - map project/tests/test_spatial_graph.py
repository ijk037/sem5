"""
Unit tests for Phase 1: Spatial Graph and Ingestion.
"""

import math
import pytest
from src.spatial_graph import SpatialGraph, haversine_distance, EARTH_RADIUS_METERS


def test_haversine_distance_known_coordinates():
    # Same point should have 0 distance
    d_zero = haversine_distance(26.8438, 75.5646, 26.8438, 75.5646)
    assert d_zero == pytest.approx(0.0, abs=1e-5)

    # Symmetry property: d(A, B) == d(B, A)
    d1 = haversine_distance(26.8415, 75.5642, 26.8470, 75.5654)
    d2 = haversine_distance(26.8470, 75.5654, 26.8415, 75.5642)
    assert d1 == pytest.approx(d2, abs=1e-5)
    assert d1 > 500.0  # Approx 600m across MUJ campus


def test_spatial_graph_loading():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")

    summary = sg.get_summary()
    assert summary["num_nodes"] >= 30
    assert summary["num_edges"] >= 40
    assert summary["is_connected"] is True
    assert "GATE_1" in sg.graph
    assert "AB1_MAIN" in sg.graph
    assert "LIBRARY_CENTRAL" in sg.graph


def test_nearest_node_mapping():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")

    # Exact coordinates of AB1_MAIN
    ab1_data = sg.graph.nodes["AB1_MAIN"]
    node, dist = sg.get_nearest_node(ab1_data["latitude"], ab1_data["longitude"])
    assert node == "AB1_MAIN"
    assert dist == pytest.approx(0.0, abs=1e-3)

    # Slightly offset coordinate near Main Gate
    node_gate, dist_gate = sg.get_nearest_node(26.84151, 75.56421)
    assert node_gate == "GATE_1"
    assert dist_gate < 5.0


def test_nearest_node_wheelchair_filter():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")

    # OAT_TOP_STEPS is marked wheelchair_accessible=False
    oat_steps = sg.graph.nodes["OAT_TOP_STEPS"]
    # Query with wheelchair_only=True should skip OAT_TOP_STEPS
    node, _ = sg.get_nearest_node(oat_steps["latitude"], oat_steps["longitude"], wheelchair_only=True)
    assert node != "OAT_TOP_STEPS"
    assert sg.graph.nodes[node]["wheelchair_accessible"] is True


def test_dynamic_condition_updates():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")

    u, v = "GATE_1", "JUNC_MAIN_BOULEVARD"
    sg.update_edge_condition(u, v, crowd_factor=2.5, is_blocked=True)
    assert sg.graph[u][v]["crowd_factor"] == 2.5
    assert sg.graph[u][v]["is_blocked"] is True

    # Reset
    sg.reset_dynamic_conditions()
    assert sg.graph[u][v]["is_blocked"] is False
    assert sg.graph[u][v]["crowd_factor"] == sg.graph[u][v]["base_crowd_factor"]
