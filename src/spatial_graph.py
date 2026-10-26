"""
Spatial Graph Representation and Data Ingestion Module (Phase 1).
Manages campus nodes, pathways, Haversine spatial calculations,
and OpenStreetMap / CSV data ingestion using NetworkX.
"""

import math
import logging
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import networkx as nx

logger = logging.getLogger(__name__)

# Constants
EARTH_RADIUS_METERS = 6371000.0  # Mean radius of Earth in meters


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two geographic points
    on Earth using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of point 1 in decimal degrees.
        lat2, lon2: Latitude and longitude of point 2 in decimal degrees.

    Returns:
        Physical straight-line distance in meters.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c


class SpatialGraph:
    """
    Spatial Graph representation of a campus walkway network using NetworkX.
    Supports node/edge spatial indexing, accessibility criteria,
    dynamic condition multipliers, and dual ingestion (CSV & OSMnx).
    """

    def __init__(self):
        self.graph: nx.Graph = nx.Graph()
        self.source_type: str = "uninitialized"
        self.metadata: Dict[str, Any] = {}

    @property
    def nodes(self):
        return self.graph.nodes

    @property
    def edges(self):
        return self.graph.edges

    def __len__(self):
        return len(self.graph)

    def load_from_csv(self, locations_path: str, connections_path: str) -> None:
        """
        Ingest campus layout from curated locations.csv and connections.csv.
        """
        self.graph.clear()
        self.source_type = "csv"

        # 1. Load Nodes (Locations)
        df_locs = pd.read_csv(locations_path)
        for _, row in df_locs.iterrows():
            node_id = str(row['id']).strip()
            self.graph.add_node(
                node_id,
                name=str(row.get('name', node_id)).strip(),
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                node_type=str(row.get('node_type', 'generic')).strip().lower(),
                wheelchair_accessible=bool(row.get('wheelchair_accessible', True) in [True, 'True', 'true', 1, '1']),
                indoor=bool(row.get('indoor', False) in [True, 'True', 'true', 1, '1']),
                description=str(row.get('description', '')).strip()
            )

        # 2. Load Edges (Connections)
        df_conns = pd.read_csv(connections_path)
        for _, row in df_conns.iterrows():
            u = str(row['source']).strip()
            v = str(row['target']).strip()

            if u not in self.graph or v not in self.graph:
                logger.warning(f"Skipping edge ({u}, {v}): One or both nodes not found in graph.")
                continue

            node_u = self.graph.nodes[u]
            node_v = self.graph.nodes[v]

            # Compute physical length if not explicitly provided or invalid
            dist_val = row.get('distance_meters')
            if pd.isna(dist_val) or float(dist_val) <= 0:
                dist_val = haversine_distance(
                    node_u['latitude'], node_u['longitude'],
                    node_v['latitude'], node_v['longitude']
                )
            else:
                dist_val = float(dist_val)

            has_stairs = bool(row.get('has_stairs', False) in [True, 'True', 'true', 1, '1'])
            wheelchair_acc = bool(row.get('wheelchair_accessible', not has_stairs) in [True, 'True', 'true', 1, '1'])
            is_indoor = bool(row.get('is_indoor', False) in [True, 'True', 'true', 1, '1'])
            crowd_factor = float(row.get('crowd_factor', 1.0))
            is_blocked = bool(row.get('is_blocked', False) in [True, 'True', 'true', 1, '1'])
            weather_exposed = bool(row.get('weather_exposed', not is_indoor) in [True, 'True', 'true', 1, '1'])
            path_name = str(row.get('path_name', f'{u} <-> {v}')).strip()

            self.graph.add_edge(
                u, v,
                physical_length=dist_val,
                base_length=dist_val,
                has_stairs=has_stairs,
                wheelchair_accessible=wheelchair_acc,
                is_indoor=is_indoor,
                crowd_factor=crowd_factor,
                base_crowd_factor=crowd_factor,
                is_blocked=is_blocked,
                weather_exposed=weather_exposed,
                path_name=path_name
            )

        self.metadata = {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "source": "CSV Ingestion",
            "locations_file": locations_path,
            "connections_file": connections_path
        }
        logger.info(f"Loaded {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges from CSV.")

    def load_from_osmnx(self, place_name: str = "Manipal University Jaipur, India",
                         network_type: str = "walk",
                         fallback_to_csv: bool = True,
                         csv_locations: Optional[str] = None,
                         csv_connections: Optional[str] = None) -> bool:
        """
        Query OpenStreetMap for campus walkway graph using OSMnx.
        Falls back to CSV if query fails or network is unavailable.
        """
        try:
            import osmnx as ox
            logger.info(f"Querying OSMnx for: '{place_name}' (network_type='{network_type}')...")
            ox.settings.use_cache = True
            ox.settings.log_console = False

            osm_graph = ox.graph_from_place(place_name, network_type=network_type, simplify=True)
            self.graph.clear()
            self.source_type = "osmnx"

            for node_id, data in osm_graph.nodes(data=True):
                lat = float(data.get('y', data.get('lat', 0.0)))
                lon = float(data.get('x', data.get('lon', 0.0)))
                self.graph.add_node(
                    str(node_id),
                    name=str(data.get('name', f'OSM Node {node_id}')),
                    latitude=lat,
                    longitude=lon,
                    node_type='walkway_junction',
                    wheelchair_accessible=True,
                    indoor=False,
                    description=f'OSM Walkway Node ({node_id})'
                )

            for u, v, data in osm_graph.edges(data=True):
                u_str, v_str = str(u), str(v)
                if u_str not in self.graph or v_str not in self.graph:
                    continue

                length = float(data.get('length', 0.0))
                if length <= 0:
                    nu = self.graph.nodes[u_str]
                    nv = self.graph.nodes[v_str]
                    length = haversine_distance(nu['latitude'], nu['longitude'], nv['latitude'], nv['longitude'])

                highway = data.get('highway', 'footway')
                has_stairs = (highway == 'steps')
                wheelchair = not has_stairs

                if not self.graph.has_edge(u_str, v_str):
                    self.graph.add_edge(
                        u_str, v_str,
                        physical_length=length,
                        base_length=length,
                        has_stairs=has_stairs,
                        wheelchair_accessible=wheelchair,
                        is_indoor=False,
                        crowd_factor=1.0,
                        base_crowd_factor=1.0,
                        is_blocked=False,
                        weather_exposed=True,
                        path_name=str(data.get('name', f'Walkway {u_str}-{v_str}'))
                    )

            self.metadata = {
                "num_nodes": self.graph.number_of_nodes(),
                "num_edges": self.graph.number_of_edges(),
                "source": f"OSMnx: {place_name}",
                "network_type": network_type
            }
            logger.info(f"Successfully ingested OSM graph: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges.")
            return True

        except Exception as e:
            logger.warning(f"OSMnx ingestion failed for '{place_name}': {e}.")
            if fallback_to_csv and csv_locations and csv_connections:
                logger.info("Falling back to local curated CSV dataset...")
                self.load_from_csv(csv_locations, csv_connections)
                return False
            raise e

    def get_nearest_node(self, lat: float, lon: float,
                         wheelchair_only: bool = False,
                         max_distance_m: Optional[float] = None) -> Tuple[Optional[str], float]:
        """
        Map arbitrary user coordinate inputs to the nearest valid graph node.

        Args:
            lat, lon: User coordinate in decimal degrees.
            wheelchair_only: Filter only nodes that are marked wheelchair accessible.
            max_distance_m: Optional cutoff threshold in meters.

        Returns:
            Tuple of (nearest_node_id, distance_in_meters).
            Returns (None, infinity) if no valid node is found.
        """
        if len(self.graph) == 0:
            return None, float('inf')

        nearest_node = None
        min_dist = float('inf')

        for node_id, data in self.graph.nodes(data=True):
            if wheelchair_only and not data.get('wheelchair_accessible', True):
                continue

            node_lat = data.get('latitude')
            node_lon = data.get('longitude')
            if node_lat is None or node_lon is None:
                continue

            dist = haversine_distance(lat, lon, node_lat, node_lon)
            if dist < min_dist:
                min_dist = dist
                nearest_node = node_id

        if max_distance_m is not None and min_dist > max_distance_m:
            return None, min_dist

        return nearest_node, min_dist

    def get_node_coords(self, node_id: str) -> Tuple[float, float]:
        """Return (lat, lon) for a given node id."""
        data = self.graph.nodes[node_id]
        return data['latitude'], data['longitude']

    def update_edge_condition(self, u: str, v: str,
                              crowd_factor: Optional[float] = None,
                              is_blocked: Optional[bool] = None,
                              weather_exposed: Optional[bool] = None) -> None:
        """Update dynamic edge attributes in real-time."""
        if self.graph.has_edge(u, v):
            edge_data = self.graph[u][v]
            if crowd_factor is not None:
                edge_data['crowd_factor'] = max(0.1, float(crowd_factor))
            if is_blocked is not None:
                edge_data['is_blocked'] = bool(is_blocked)
            if weather_exposed is not None:
                edge_data['weather_exposed'] = bool(weather_exposed)

    def reset_dynamic_conditions(self) -> None:
        """Reset all crowd factors and blockages to baseline state."""
        for _, _, data in self.graph.edges(data=True):
            data['crowd_factor'] = data.get('base_crowd_factor', 1.0)
            data['is_blocked'] = False

    def get_bounding_box(self) -> Dict[str, float]:
        """Get bounding box of the graph coordinates."""
        lats = [data['latitude'] for _, data in self.graph.nodes(data=True) if 'latitude' in data]
        lons = [data['longitude'] for _, data in self.graph.nodes(data=True) if 'longitude' in data]
        if not lats or not lons:
            return {'min_lat': 0.0, 'max_lat': 0.0, 'min_lon': 0.0, 'max_lon': 0.0,
                    'center_lat': 0.0, 'center_lon': 0.0}
        return {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lon': min(lons),
            'max_lon': max(lons),
            'center_lat': sum(lats) / len(lats),
            'center_lon': sum(lons) / len(lons),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Return comprehensive topological and spatial summary metrics."""
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        connected_components = nx.number_connected_components(self.graph) if num_nodes > 0 else 0
        total_path_length = sum(data.get('physical_length', 0.0) for _, _, data in self.graph.edges(data=True))

        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'connected_components': connected_components,
            'is_connected': (connected_components == 1),
            'total_pathway_length_meters': round(total_path_length, 2),
            'average_degree': round((2 * num_edges / num_nodes), 2) if num_nodes > 0 else 0.0,
            'source_type': self.source_type,
            'bounding_box': self.get_bounding_box()
        }
