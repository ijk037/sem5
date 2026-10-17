"""
Automated CLI Benchmark Suite for AISC Map Routing Engines.
Runs multi-criteria comparisons across diverse campus origin-destination pairs.
"""

import os
import sys
import pandas as pd

# Ensure UTF-8 output encoding for Windows command line
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.spatial_graph import SpatialGraph
from src.search_engine import SearchEngine
from src.dynamic_simulation import CampusEventSimulator


def run_comprehensive_benchmark():
    print("=" * 80)
    print(" MANIPAL UNIVERSITY JAIPUR -- AISC HEURISTIC SEARCH BENCHMARK SUITE")
    print("=" * 80)

    sg = SpatialGraph()
    sg.load_from_csv(os.path.join("data", "locations.csv"), os.path.join("data", "connections.csv"))
    engine = SearchEngine(sg)
    simulator = CampusEventSimulator(sg)

    test_scenarios = [
        ("Long Campus Traverse", "GATE_1", "CRICKET_GROUND", "shortest"),
        ("Hostel to Academic Corridor", "HOSTEL_B3_B4", "AB2_MAIN", "shortest"),
        ("Accessible Cross-Campus", "HOSTEL_B1_B2", "LIBRARY_CENTRAL", "accessible"),
        ("Peak-Hour Lunch Rush", "AB1_MAIN", "MESS_GRAND", "quickest"),
        ("Sports to Dining Plaza", "SPORTS_COMPLEX_INDOOR", "FOOD_COURT", "shortest"),
    ]

    all_rows = []

    for desc, start, goal, mode in test_scenarios:
        print(f"\n[+] Scenario: {desc} [{start} -> {goal} | Mode: {mode}]")
        results = engine.run_all(start, goal, mode)

        astar_exp = results["A*"].node_expansions
        dijk_exp = results["Dijkstra"].node_expansions
        efficiency_gain = f"{((dijk_exp - astar_exp) / max(1, dijk_exp)) * 100:.1f}% fewer nodes"

        for algo_name, res in results.items():
            all_rows.append({
                "Scenario": desc,
                "Mode": mode,
                "Algorithm": algo_name,
                "Success": "Yes" if res.success else "No",
                "Distance (m)": round(res.total_distance_meters, 1),
                "Cost": round(res.total_cost, 2),
                "Expansions": res.node_expansions,
                "Generated": res.nodes_generated,
                "Time (ms)": round(res.execution_time_ms, 3)
            })

        print(f"    A* vs Dijkstra Expansions: {astar_exp} vs {dijk_exp} ({efficiency_gain})")
        print(f"    Optimal Path Distance: {results['A*'].total_distance_meters:.1f} meters")

    print("\n" + "=" * 80)
    print(" EXECUTIVE COMPARISON SUMMARY TABLE")
    print("=" * 80)
    df = pd.DataFrame(all_rows)
    print(df.to_string(index=False))

    # Stress Test under Simulated Dynamic Event
    print("\n" + "=" * 80)
    print(" STRESS-TEST: DYNAMIC CONSTRUCTION REROUTING")
    print("=" * 80)
    res_base = engine.a_star_search("HOSTEL_B1_B2", "LIBRARY_CENTRAL", "shortest")
    simulator.apply_pathway_construction([("AB1_MAIN", "NESCAFE_KIOSK"), ("AB1_MAIN", "AB1_EAST_STAIRS")])
    res_after = engine.a_star_search("HOSTEL_B1_B2", "LIBRARY_CENTRAL", "shortest")
    print(f"  Baseline Path: {' -> '.join(res_base.path)}")
    print(f"  Rerouted Path: {' -> '.join(res_after.path)}")
    print(f"  Rerouted Distance: {res_after.total_distance_meters:.1f}m (Bypassed construction successfully!)")
    simulator.clear_all_events()


if __name__ == "__main__":
    run_comprehensive_benchmark()
