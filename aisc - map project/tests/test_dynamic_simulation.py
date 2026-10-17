"""
Unit tests for Phase 4: Dynamic Campus Event Simulation and Rerouting.
"""

import pytest
from src.spatial_graph import SpatialGraph
from src.search_engine import SearchEngine
from src.dynamic_simulation import CampusEventSimulator


def test_peak_hour_rush_event():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")
    simulator = CampusEventSimulator(sg)

    info = simulator.apply_peak_hour_rush(crowd_multiplier=2.5)
    assert info["multiplier"] == 2.5
    assert len(simulator.get_active_events()) == 1

    # Check crowd factor updated on affected edge
    assert sg.graph["DOME_BUILDING"]["AB1_MAIN"]["crowd_factor"] >= 2.5


def test_construction_blockage_and_reroute():
    sg = SpatialGraph()
    sg.load_from_csv("data/locations.csv", "data/connections.csv")
    engine = SearchEngine(sg)
    simulator = CampusEventSimulator(sg)

    start = "HOSTEL_B1_B2"
    goal = "LIBRARY_CENTRAL"

    # Initial baseline path
    res_base = engine.a_star_search(start, goal, "shortest")
    assert res_base.success is True

    # Apply construction blockage on the primary route
    simulator.apply_pathway_construction([("AB1_MAIN", "NESCAFE_KIOSK"), ("AB1_MAIN", "AB1_EAST_STAIRS")])

    # A* should dynamically reroute via alternative corridor (e.g. AB1 -> AB2 -> Ramp/Sports/Library)
    res_reroute = engine.a_star_search(start, goal, "shortest")
    assert res_reroute.success is True
    assert ("AB1_MAIN", "NESCAFE_KIOSK") not in zip(res_reroute.path, res_reroute.path[1:])
    assert ("AB1_MAIN", "AB1_EAST_STAIRS") not in zip(res_reroute.path, res_reroute.path[1:])

    # Clear events
    simulator.clear_all_events()
    assert len(simulator.get_active_events()) == 0
    assert sg.graph["AB1_MAIN"]["NESCAFE_KIOSK"]["is_blocked"] is False
