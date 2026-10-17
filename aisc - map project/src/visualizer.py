"""
Geospatial Map Visualization and Route Rendering Module (Phase 3).
Renders campus graph nodes, walkways, computed optimal routes,
and algorithm exploration footprints using Folium / Leaflet.
"""

from typing import Dict, List, Tuple, Optional, Any, Set
import folium
from folium import plugins
from src.spatial_graph import SpatialGraph
from src.search_engine import SearchResult

# Color mapping for node categories
NODE_TYPE_COLORS = {
    "academic": "#2563EB",   # Vibrant Blue
    "hostel": "#EA580C",     # Orange
    "dining": "#16A34A",     # Green
    "sports": "#9333EA",     # Purple
    "gate": "#DC2626",       # Red
    "facility": "#0D9488",   # Teal
    "junction": "#64748B"    # Slate Gray
}

NODE_TYPE_ICONS = {
    "academic": "graduation-cap",
    "hostel": "bed",
    "dining": "utensils",
    "sports": "futbol",
    "gate": "door-open",
    "facility": "building",
    "junction": "circle-dot"
}


class CampusVisualizer:
    """
    Builds interactive Folium / Leaflet maps for campus navigation and search benchmarking.
    """

    def __init__(self, spatial_graph: SpatialGraph):
        self.sg = spatial_graph

    def create_base_map(self, zoom_start: int = 17, tiles: str = "CartoDB positron") -> folium.Map:
        """Create a centered base Folium map around MUJ campus."""
        bbox = self.sg.get_bounding_box()
        center_lat = bbox.get("center_lat", 26.8440)
        center_lon = bbox.get("center_lon", 75.5645)

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles=tiles,
            control_scale=True,
            prefer_canvas=True
        )
        return m

    def render_campus_graph(self,
                            m: folium.Map,
                            highlight_explored: Optional[List[str]] = None,
                            search_result: Optional[SearchResult] = None,
                            show_all_nodes: bool = True) -> folium.Map:
        """
        Render all nodes, walkways, blockages, route polylines, and search exploration footprint.
        """
        explored_set = set(highlight_explored or [])
        path_set = set(search_result.path if search_result else [])
        path_edges = set()
        if search_result and search_result.path:
            for i in range(len(search_result.path) - 1):
                u, v = search_result.path[i], search_result.path[i + 1]
                path_edges.add((u, v))
                path_edges.add((v, u))

        # 1. Feature Group for Campus Walkway Edges
        fg_edges = folium.FeatureGroup(name="Walkway Network", show=True)

        for u, v, data in self.sg.graph.edges(data=True):
            if (u, v) in path_edges or (v, u) in path_edges:
                continue  # Drawn separately with route styling

            nu = self.sg.graph.nodes[u]
            nv = self.sg.graph.nodes[v]
            coords = [[nu["latitude"], nu["longitude"]], [nv["latitude"], nv["longitude"]]]

            is_blocked = data.get("is_blocked", False)
            has_stairs = data.get("has_stairs", False)
            crowd = data.get("crowd_factor", 1.0)
            length = round(data.get("physical_length", 0.0), 1)
            pname = data.get("path_name", f"{u} - {v}")

            if is_blocked:
                color = "#EF4444"  # Red
                dash_array = "6, 6"
                weight = 3.5
                opacity = 0.9
                popup_text = f"<b>🚫 CLOSED: {pname}</b><br>Path Blocked for Maintenance/Flooding"
            elif has_stairs:
                color = "#A855F7"  # Purple
                dash_array = "4, 4"
                weight = 3.0
                opacity = 0.85
                popup_text = f"<b>🪜 STAIRS: {pname}</b><br>Length: {length}m<br>Wheelchair: No"
            elif crowd >= 2.0:
                color = "#F59E0B"  # Amber
                dash_array = None
                weight = 3.0
                opacity = 0.8
                popup_text = f"<b>👥 HIGH CROWD: {pname}</b><br>Length: {length}m<br>Crowd Factor: {crowd}x"
            else:
                color = "#94A3B8"  # Slate
                dash_array = None
                weight = 2.5
                opacity = 0.65
                popup_text = f"<b>🚶 {pname}</b><br>Length: {length}m<br>Crowd Factor: {crowd}x"

            folium.PolyLine(
                locations=coords,
                color=color,
                weight=weight,
                opacity=opacity,
                dash_array=dash_array,
                tooltip=f"{pname} ({length}m)",
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(fg_edges)

        fg_edges.add_to(m)

        # 2. Render Exploration Footprint (Nodes visited during search)
        if explored_set:
            fg_explored = folium.FeatureGroup(name="Exploration Footprint (Visited)", show=True)
            for node_id in explored_set:
                if node_id not in self.sg.graph:
                    continue
                ndata = self.sg.graph.nodes[node_id]
                # If node is on the final path, skip here (it will get route highlight)
                if node_id in path_set:
                    continue

                folium.CircleMarker(
                    location=[ndata["latitude"], ndata["longitude"]],
                    radius=7,
                    color="#F59E0B",
                    fill=True,
                    fill_color="#FDE68A",
                    fill_opacity=0.85,
                    weight=2,
                    tooltip=f"Explored Node: {ndata.get('name', node_id)}",
                    popup=f"<b>Explored State</b><br>{ndata.get('name', node_id)}"
                ).add_to(fg_explored)
            fg_explored.add_to(m)

        # 3. Render Route Polylines (if search succeeded)
        if search_result and search_result.success and search_result.path:
            fg_route = folium.FeatureGroup(name=f"Optimal Route ({search_result.algorithm})", show=True)

            coords = search_result.path_coords

            # Glowing base shadow polyline
            folium.PolyLine(
                locations=coords,
                color="#1E3A8A",
                weight=8,
                opacity=0.4
            ).add_to(fg_route)

            # Primary vibrant route line
            folium.PolyLine(
                locations=coords,
                color="#2563EB",
                weight=5,
                opacity=0.95,
                tooltip=f"Route: {search_result.total_distance_meters:.1f}m ({search_result.estimated_time_seconds/60:.1f} min)"
            ).add_to(fg_route)

            # Start Marker
            start_id = search_result.start_node
            start_data = self.sg.graph.nodes[start_id]
            folium.Marker(
                location=[start_data["latitude"], start_data["longitude"]],
                popup=folium.Popup(f"<b>🚀 START: {start_data.get('name')}</b>", max_width=250),
                tooltip=f"Start: {start_data.get('name')}",
                icon=folium.Icon(color="green", icon="play", prefix="fa")
            ).add_to(fg_route)

            # Goal Marker
            goal_id = search_result.goal_node
            goal_data = self.sg.graph.nodes[goal_id]
            folium.Marker(
                location=[goal_data["latitude"], goal_data["longitude"]],
                popup=folium.Popup(f"<b>🏁 DESTINATION: {goal_data.get('name')}</b>", max_width=250),
                tooltip=f"Destination: {goal_data.get('name')}",
                icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa")
            ).add_to(fg_route)

            # Intermediate Waypoint Markers on Route
            for i, node_id in enumerate(search_result.path[1:-1], start=1):
                ndata = self.sg.graph.nodes[node_id]
                folium.CircleMarker(
                    location=[ndata["latitude"], ndata["longitude"]],
                    radius=6,
                    color="#2563EB",
                    fill=True,
                    fill_color="#60A5FA",
                    fill_opacity=1.0,
                    weight=2,
                    tooltip=f"Step {i}: {ndata.get('name')}"
                ).add_to(fg_route)

            fg_route.add_to(m)

        # 4. Render All Campus POI Nodes
        if show_all_nodes:
            fg_nodes = folium.FeatureGroup(name="Campus Landmarks", show=True)
            for node_id, ndata in self.sg.graph.nodes(data=True):
                # If it's already start/goal marker, avoid duplicate marker
                if search_result and node_id in [search_result.start_node, search_result.goal_node]:
                    continue

                ntype = ndata.get("node_type", "junction")
                color = NODE_TYPE_COLORS.get(ntype, "#64748B")
                accessible = ndata.get("wheelchair_accessible", True)
                acc_badge = "♿ Wheelchair Accessible" if accessible else "⚠️ Stairs Only"
                indoor_badge = "🏠 Indoor" if ndata.get("indoor", False) else "🌳 Outdoor"

                popup_html = f"""
                <div style='font-family: sans-serif; font-size: 12px; min-width: 180px;'>
                    <b style='font-size: 14px; color: {color};'>{ndata.get('name', node_id)}</b><br>
                    <span style='color: #64748b;'>ID: {node_id} | Type: {ntype.title()}</span><br>
                    <p style='margin: 4px 0;'>{ndata.get('description', '')}</p>
                    <div style='margin-top: 4px; font-size: 11px;'>
                        <span style='background: #E2E8F0; padding: 2px 6px; border-radius: 4px;'>{indoor_badge}</span>
                        <span style='background: #E2E8F0; padding: 2px 6px; border-radius: 4px;'>{acc_badge}</span>
                    </div>
                </div>
                """

                folium.CircleMarker(
                    location=[ndata["latitude"], ndata["longitude"]],
                    radius=5,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8,
                    weight=1.5,
                    tooltip=f"{ndata.get('name')} ({ntype})",
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(fg_nodes)

            fg_nodes.add_to(m)

        # Layer Control
        folium.LayerControl(position="topright", collapsed=False).add_to(m)
        return m
