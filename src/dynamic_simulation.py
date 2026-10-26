"""
Dynamic Edge Simulation and Live Campus Event Module (Phase 4).
Simulates real-time campus events such as peak-hour class transitions,
pathway maintenance/construction blockages, heavy rain/waterlogging,
and mess rush hours to stress-test real-time rerouting capabilities.
"""

from typing import Dict, List, Tuple, Optional, Any
from src.spatial_graph import SpatialGraph


class CampusEventSimulator:
    """
    Simulates real-time dynamic conditions and disruptions on the campus graph.
    """

    def __init__(self, spatial_graph: SpatialGraph):
        self.sg = spatial_graph
        self.active_events: Dict[str, Dict[str, Any]] = {}

    def get_active_events(self) -> List[Dict[str, Any]]:
        """Return list of currently active events."""
        return list(self.active_events.values())

    def clear_all_events(self) -> None:
        """Reset all edges to pristine baseline state and clear event registry."""
        self.sg.reset_dynamic_conditions()
        self.active_events.clear()

    def apply_peak_hour_rush(self, crowd_multiplier: float = 2.0) -> Dict[str, Any]:
        """
        Simulate peak-hour class transition rush.
        Dramatically increases crowd factors along academic corridors,
        library plaza, food court, and central connectors.
        """
        academic_corridors = [
            ("DOME_BUILDING", "AB1_MAIN"),
            ("AB1_MAIN", "AB2_MAIN"),
            ("AB1_MAIN", "NESCAFE_KIOSK"),
            ("NESCAFE_KIOSK", "LIBRARY_CENTRAL"),
            ("LIBRARY_CENTRAL", "LIBRARY_PLAZA"),
            ("LIBRARY_PLAZA", "FOOD_COURT"),
            ("FOOD_COURT", "MESS_GRAND"),
            ("HOSTEL_CIRCLE", "AB1_RAMP_ENTRANCE"),
            ("HOSTEL_B1_B2", "HOSTEL_MESS_B")
        ]

        affected_edges = []
        for u, v in academic_corridors:
            if self.sg.graph.has_edge(u, v):
                current_crowd = self.sg.graph[u][v].get("base_crowd_factor", 1.0)
                new_crowd = round(current_crowd * crowd_multiplier, 2)
                self.sg.update_edge_condition(u, v, crowd_factor=new_crowd)
                affected_edges.append(f"{u} <-> {v} (Crowd: {new_crowd}x)")

        event_info = {
            "id": "peak_hour_rush",
            "name": "Peak-Hour Class Transition Rush",
            "type": "crowd_surge",
            "multiplier": crowd_multiplier,
            "description": f"Academic and cafeteria arteries crowded ({crowd_multiplier}x multiplier).",
            "affected_count": len(affected_edges),
            "affected_edges": affected_edges
        }
        self.active_events["peak_hour_rush"] = event_info
        return event_info

    def apply_pathway_construction(self, blocked_pairs: Optional[List[Tuple[str, str]]] = None) -> Dict[str, Any]:
        """
        Simulate temporary pathway construction or maintenance blockage.
        Default targets the primary central spine between Dome, AB1, and Library.
        """
        if blocked_pairs is None:
            blocked_pairs = [
                ("DOME_BUILDING", "AB1_MAIN"),
                ("AB1_MAIN", "NESCAFE_KIOSK"),
                ("LIBRARY_PLAZA", "FOOD_COURT")
            ]

        affected_edges = []
        for u, v in blocked_pairs:
            if self.sg.graph.has_edge(u, v):
                self.sg.update_edge_condition(u, v, is_blocked=True)
                affected_edges.append(f"{u} <-> {v}")

        event_info = {
            "id": "pathway_construction",
            "name": "Pathway Maintenance & Construction",
            "type": "blockage",
            "description": f"Critical walkways blocked for pavement repairs ({len(affected_edges)} edges closed).",
            "affected_count": len(affected_edges),
            "affected_edges": affected_edges
        }
        self.active_events["pathway_construction"] = event_info
        return event_info

    def apply_rain_and_waterlogging(self, outdoor_penalty: float = 3.0,
                                    block_low_lying: bool = True) -> Dict[str, Any]:
        """
        Simulate heavy monsoon rain / waterlogging.
        Penalizes exposed open-air pathways and floods low-lying amphitheatre / sports steps.
        """
        affected_edges = []

        for u, v, data in self.sg.graph.edges(data=True):
            is_indoor = data.get("is_indoor", False)
            if not is_indoor:
                current_crowd = data.get("base_crowd_factor", 1.0)
                # Severe movement penalty in heavy rain
                self.sg.update_edge_condition(u, v, crowd_factor=current_crowd * outdoor_penalty)
                affected_edges.append(f"{u} <-> {v}")

        flooded_paths = []
        if block_low_lying:
            # Waterlogged outdoor low points (e.g. OAT steps & open sports field paths)
            waterlogged = [
                ("OAT_BOTTOM", "OAT_TOP_STEPS"),
                ("OAT_TOP_STEPS", "GATE_3"),
                ("BASKETBALL_COURTS", "FOOTBALL_GROUND")
            ]
            for u, v in waterlogged:
                if self.sg.graph.has_edge(u, v):
                    self.sg.update_edge_condition(u, v, is_blocked=True)
                    flooded_paths.append(f"{u} <-> {v}")

        event_info = {
            "id": "monsoon_rain",
            "name": "Monsoon Rain & Waterlogging",
            "type": "weather",
            "description": f"Heavy rain: Outdoor paths slowed ({outdoor_penalty}x); {len(flooded_paths)} low-lying paths flooded.",
            "affected_count": len(affected_edges) + len(flooded_paths),
            "flooded_paths": flooded_paths
        }
        self.active_events["monsoon_rain"] = event_info
        return event_info

    def toggle_edge_blockage(self, u: str, v: str, is_blocked: bool) -> bool:
        """Manually toggle blockage on a specific edge."""
        if self.sg.graph.has_edge(u, v):
            self.sg.update_edge_condition(u, v, is_blocked=is_blocked)
            event_key = f"custom_block_{u}_{v}"
            if is_blocked:
                self.active_events[event_key] = {
                    "id": event_key,
                    "name": f"Manual Closure: {u} - {v}",
                    "type": "manual_block",
                    "description": f"Path {u} <-> {v} manually marked closed.",
                    "edge": (u, v)
                }
            else:
                self.active_events.pop(event_key, None)
            return True
        return False
