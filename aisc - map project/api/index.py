"""
MUJ AI Campus Navigator - Vercel Serverless Function Entrypoint.
Self-contained Flask application connecting directly to the AISC search engine.
"""

import os
import sys
import io
import json
from flask import Flask, render_template, render_template_string, request, jsonify

# Add current directory and project roots to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Also check for subfolder if running from repo root
SUBFOLDER = os.path.join(BASE_DIR, "aisc - map project")
if os.path.isdir(SUBFOLDER) and SUBFOLDER not in sys.path:
    sys.path.insert(0, SUBFOLDER)

from src.spatial_graph import SpatialGraph
from src.search_engine import SearchEngine
from src.dynamic_simulation import CampusEventSimulator
from src.embedded_data import LOCATIONS_CSV, CONNECTIONS_CSV

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))


def get_csv_source(filename: str, fallback_data: str):
    """Return file path if available on disk, or in-memory fallback stream."""
    candidates = [
        os.path.join(BASE_DIR, "data", filename),
        os.path.join(SUBFOLDER, "data", filename),
        os.path.join(os.getcwd(), "data", filename),
        os.path.join(os.getcwd(), "aisc - map project", "data", filename),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return io.StringIO(fallback_data)


def get_template_html():
    """Retrieve template HTML safely from disk or fallback."""
    candidates = [
        os.path.join(BASE_DIR, "templates", "index.html"),
        os.path.join(SUBFOLDER, "templates", "index.html"),
        os.path.join(os.getcwd(), "templates", "index.html"),
        os.path.join(os.getcwd(), "aisc - map project", "templates", "index.html"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    return None


# Initialize Spatial Graph & Search Engine
sg = SpatialGraph()
loc_source = get_csv_source("locations.csv", LOCATIONS_CSV)
conn_source = get_csv_source("connections.csv", CONNECTIONS_CSV)
sg.load_from_csv(loc_source, conn_source)

engine = SearchEngine(sg)
simulator = CampusEventSimulator(sg)


@app.route("/")
def index():
    """Render main aesthetic map interface."""
    try:
        return render_template("index.html")
    except Exception:
        content = get_template_html()
        if content:
            return render_template_string(content)
        return "<h3>🌸 MUJ Campus Navigator is loading... Please refresh.</h3>"


@app.route("/api/health", methods=["GET"])
def health_check():
    """Diagnostic health check endpoint for deployment verification."""
    return jsonify({
        "status": "healthy",
        "nodes_count": len(sg.graph.nodes),
        "edges_count": len(sg.graph.edges),
        "source_type": getattr(sg, "source_type", "unknown")
    })


@app.route("/api/landmarks", methods=["GET"])
def get_landmarks():
    """Return all campus landmark POIs with metadata."""
    landmarks = []
    for node_id, data in sg.graph.nodes(data=True):
        landmarks.append({
            "id": node_id,
            "name": data.get("name", node_id),
            "latitude": float(data.get("latitude", 0.0)),
            "longitude": float(data.get("longitude", 0.0)),
            "node_type": data.get("node_type", "facility"),
            "wheelchair_accessible": bool(data.get("wheelchair_accessible", True)),
            "indoor": bool(data.get("indoor", False)),
            "description": data.get("description", "")
        })
    return jsonify(landmarks)


@app.route("/api/connections", methods=["GET"])
def get_connections():
    """Return all campus walkway segments for visual background graph."""
    connections = []
    seen = set()
    for u, v, data in sg.graph.edges(data=True):
        edge_key = tuple(sorted([u, v]))
        if edge_key in seen:
            continue
        seen.add(edge_key)

        u_data = sg.graph.nodes[u]
        v_data = sg.graph.nodes[v]
        connections.append({
            "source": u,
            "target": v,
            "source_coords": {"lat": u_data["latitude"], "lon": u_data["longitude"]},
            "target_coords": {"lat": v_data["latitude"], "lon": v_data["longitude"]},
            "has_stairs": bool(data.get("has_stairs", False)),
            "wheelchair_accessible": bool(data.get("wheelchair_accessible", True)),
            "is_indoor": bool(data.get("is_indoor", False)),
            "path_name": data.get("path_name", "")
        })
    return jsonify(connections)


@app.route("/api/route", methods=["POST"])
def calculate_route():
    """Execute heuristic search and return optimal path + performance metrics."""
    data = request.get_json() or {}
    start = data.get("start")
    goal = data.get("goal")
    mode = data.get("mode", "shortest")
    algo = data.get("algorithm", "A*")

    if not start or not goal:
        return jsonify({"success": False, "error_message": "Start and Goal are required."}), 400

    if algo == "Dijkstra":
        res = engine.dijkstra_search(start, goal, routing_mode=mode)
    elif algo == "Greedy Best-First":
        res = engine.greedy_best_first_search(start, goal, routing_mode=mode)
    elif algo == "BFS":
        res = engine.breadth_first_search(start, goal, routing_mode=mode)
    else:
        res = engine.a_star_search(start, goal, routing_mode=mode)

    explored_coords = []
    for node in res.explored_nodes:
        if node in sg.graph.nodes:
            nd = sg.graph.nodes[node]
            explored_coords.append([nd["latitude"], nd["longitude"]])

    return jsonify({
        "success": res.success,
        "algorithm": res.algorithm,
        "routing_mode": res.routing_mode,
        "path": res.path,
        "path_names": res.path_names,
        "path_coords": res.path_coords,
        "distance_meters": res.total_distance_meters,
        "time_seconds": res.estimated_time_seconds,
        "expansions": res.node_expansions,
        "nodes_generated": res.nodes_generated,
        "explored_coords": explored_coords,
        "execution_time_ms": round(res.execution_time_ms, 3),
        "error_message": res.error_message
    })


@app.route("/api/compare", methods=["POST"])
def compare_algorithms():
    """Run all 4 search algorithms on the same query for academic performance comparison."""
    data = request.get_json() or {}
    start = data.get("start")
    goal = data.get("goal")
    mode = data.get("mode", "shortest")

    if not start or not goal:
        return jsonify({"error": "Start and Goal required."}), 400

    results = engine.run_all(start, goal, routing_mode=mode)
    summary = {algo: res.to_dict() for algo, res in results.items()}
    return jsonify(summary)


@app.route("/api/simulation", methods=["POST"])
def set_simulation():
    """Apply dynamic event disruptions to campus graph."""
    data = request.get_json() or {}
    event_type = data.get("event", "none")

    simulator.clear_all_events()

    if event_type == "rush":
        simulator.apply_peak_hour_rush(crowd_multiplier=2.5)
    elif event_type == "rain":
        simulator.apply_rain_and_waterlogging(outdoor_penalty=3.0)
    elif event_type == "blockage":
        simulator.apply_pathway_construction([
            ("AB1_MAIN", "NESCAFE_KIOSK"),
            ("AB1_MAIN", "AB1_EAST_STAIRS")
        ])

    return jsonify({"status": "ok", "active_event": event_type})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
