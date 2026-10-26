"""
Custom Multi-Criteria A* Engine & Baseline Search Implementations (Phase 2).
Implements A*, Dijkstra (h=0), Greedy Best-First (g=0), and Breadth-First Search (BFS)
from scratch using heapq with multi-criteria path cost formulations.
"""

import time
import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from src.spatial_graph import SpatialGraph, haversine_distance

# Base average pedestrian walking speed on flat campus paths (~4.32 km/h)
BASE_WALKING_SPEED_MPS = 1.20  # meters per second


@dataclass
class SearchResult:
    """Encapsulates the output and performance metrics of a graph search."""
    algorithm: str
    routing_mode: str
    start_node: str
    goal_node: str
    success: bool
    path: List[str] = field(default_factory=list)
    path_names: List[str] = field(default_factory=list)
    path_coords: List[Tuple[float, float]] = field(default_factory=list)
    total_cost: float = 0.0
    total_distance_meters: float = 0.0
    estimated_time_seconds: float = 0.0
    node_expansions: int = 0
    nodes_generated: int = 0
    explored_nodes: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Algorithm": self.algorithm,
            "Success": self.success,
            "Path Length (Nodes)": len(self.path),
            "Total Distance (m)": round(self.total_distance_meters, 2),
            "Estimated Time (min)": round(self.estimated_time_seconds / 60.0, 2),
            "Total Cost": round(self.total_cost, 2),
            "Node Expansions": self.node_expansions,
            "Nodes Generated": self.nodes_generated,
            "Execution Time (ms)": round(self.execution_time_ms, 4)
        }


class SearchEngine:
    """
    Multi-Criteria Spatial Search Engine.
    Supports Shortest, Quickest (Crowd-scaled), Wheelchair-Accessible,
    and Weather-Sheltered routing modes across A*, Dijkstra, Greedy, and BFS.
    """

    def __init__(self, spatial_graph: SpatialGraph):
        self.sg = spatial_graph

    def get_edge_weight(self, u: str, v: str, routing_mode: str = "shortest") -> Optional[float]:
        """
        Calculate dynamic edge traversal cost g(u, v) based on routing criteria.
        Returns None if edge is blocked or violates accessibility constraints.
        """
        if not self.sg.graph.has_edge(u, v):
            return None

        edge_data = self.sg.graph[u][v]

        # 1. Check if edge is explicitly blocked
        if edge_data.get("is_blocked", False):
            return None

        dist = float(edge_data.get("physical_length", 0.0))
        crowd = float(edge_data.get("crowd_factor", 1.0))
        has_stairs = bool(edge_data.get("has_stairs", False))
        wheelchair_edge = bool(edge_data.get("wheelchair_accessible", True))
        is_indoor = bool(edge_data.get("is_indoor", False))
        weather_exposed = bool(edge_data.get("weather_exposed", not is_indoor))

        node_v_data = self.sg.graph.nodes[v]
        wheelchair_node = bool(node_v_data.get("wheelchair_accessible", True))

        mode = routing_mode.lower().strip()

        if mode == "shortest":
            # Pure physical distance (meters)
            return dist

        elif mode == "quickest":
            # Time in seconds = distance / effective_speed
            # effective_speed = base_speed / crowd_factor
            # cost = distance * crowd_factor / base_speed
            effective_speed = max(0.1, BASE_WALKING_SPEED_MPS / max(0.2, crowd))
            time_cost = dist / effective_speed
            return time_cost

        elif mode == "accessible":
            # Wheelchair / Mobility-friendly mode:
            # Completely prune non-accessible segments or stairs
            if has_stairs or not wheelchair_edge or not wheelchair_node:
                return None
            return dist

        elif mode == "sheltered":
            # Weather-sheltered mode: Penalize exposed outdoor paths
            penalty = 3.0 if weather_exposed else 1.0
            return dist * penalty

        else:
            # Default to physical distance
            return dist

    def heuristic(self, node: str, goal: str, routing_mode: str = "shortest") -> float:
        """
        Admissible and consistent heuristic h(n):
        Calculates straight-line Haversine distance from node to goal.
        """
        node_lat, node_lon = self.sg.get_node_coords(node)
        goal_lat, goal_lon = self.sg.get_node_coords(goal)
        h_dist = haversine_distance(node_lat, node_lon, goal_lat, goal_lon)

        mode = routing_mode.lower().strip()
        if mode == "quickest":
            # For time cost, divide by maximum theoretical speed (speed with crowd_factor=1.0)
            # This guarantees h(n) <= true_time_cost, maintaining admissibility.
            return h_dist / BASE_WALKING_SPEED_MPS
        elif mode == "sheltered":
            # Baseline minimum multiplier is 1.0 (indoor/sheltered)
            return h_dist
        else:
            return h_dist

    def _reconstruct_path(self, parent: Dict[str, Optional[str]], current: str) -> List[str]:
        """Backtrack from goal to start using parent pointers."""
        path = []
        curr: Optional[str] = current
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)
        path.reverse()
        return path

    def _build_result(self, algorithm: str, routing_mode: str, start: str, goal: str,
                      path: List[str], total_cost: float, expansions: int,
                      generated: int, explored: List[str], exec_time_ms: float,
                      error_msg: Optional[str] = None) -> SearchResult:
        """Helper to package complete search results and compute physical metrics."""
        total_dist = 0.0
        est_time = 0.0
        path_names = []
        path_coords = []

        if path:
            for node in path:
                ndata = self.sg.graph.nodes[node]
                path_names.append(ndata.get("name", node))
                path_coords.append((ndata["latitude"], ndata["longitude"]))

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if self.sg.graph.has_edge(u, v):
                    edata = self.sg.graph[u][v]
                    length = float(edata.get("physical_length", 0.0))
                    crowd = float(edata.get("crowd_factor", 1.0))
                    total_dist += length
                    speed = BASE_WALKING_SPEED_MPS / max(0.2, crowd)
                    est_time += length / speed

        return SearchResult(
            algorithm=algorithm,
            routing_mode=routing_mode,
            start_node=start,
            goal_node=goal,
            success=len(path) > 0,
            path=path,
            path_names=path_names,
            path_coords=path_coords,
            total_cost=total_cost,
            total_distance_meters=total_dist,
            estimated_time_seconds=est_time,
            node_expansions=expansions,
            nodes_generated=generated,
            explored_nodes=explored,
            execution_time_ms=exec_time_ms,
            error_message=error_msg
        )

    def a_star_search(self, start: str, goal: str, routing_mode: str = "shortest") -> SearchResult:
        """
        Custom A* Heuristic Search using min-heap priority queue.
        Evaluation function: f(n) = g(n) + h(n).
        """
        t0 = time.perf_counter_ns()

        if start not in self.sg.graph or goal not in self.sg.graph:
            return self._build_result("A*", routing_mode, start, goal, [], 0, 0, 0, [], 0.0, "Start or goal not in graph.")

        if start == goal:
            t1 = time.perf_counter_ns()
            return self._build_result("A*", routing_mode, start, goal, [start], 0.0, 1, 1, [start], (t1 - t0) / 1e6)

        # Min-heap priority queue: entries are (f_score, g_score, counter, node)
        counter = 0
        frontier: List[Tuple[float, float, int, str]] = []
        h_start = self.heuristic(start, goal, routing_mode)
        heapq.heappush(frontier, (h_start, 0.0, counter, start))

        g_score: Dict[str, float] = {start: 0.0}
        parent: Dict[str, Optional[str]] = {start: None}
        explored_nodes: List[str] = []
        visited: Set[str] = set()
        nodes_generated = 1

        while frontier:
            f, current_g, _, current = heapq.heappop(frontier)

            if current in visited:
                continue

            visited.add(current)
            explored_nodes.append(current)

            if current == goal:
                t1 = time.perf_counter_ns()
                path = self._reconstruct_path(parent, goal)
                return self._build_result("A*", routing_mode, start, goal, path, g_score[goal],
                                           len(visited), nodes_generated, explored_nodes, (t1 - t0) / 1e6)

            for neighbor in self.sg.graph.neighbors(current):
                weight = self.get_edge_weight(current, neighbor, routing_mode)
                if weight is None:
                    continue  # Blocked or inaccessible edge

                tentative_g = current_g + weight
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    parent[neighbor] = current
                    h_val = self.heuristic(neighbor, goal, routing_mode)
                    f_val = tentative_g + h_val
                    counter += 1
                    nodes_generated += 1
                    heapq.heappush(frontier, (f_val, tentative_g, counter, neighbor))

        t1 = time.perf_counter_ns()
        return self._build_result("A*", routing_mode, start, goal, [], float("inf"),
                                   len(visited), nodes_generated, explored_nodes, (t1 - t0) / 1e6, "No valid path found.")

    def dijkstra_search(self, start: str, goal: str, routing_mode: str = "shortest") -> SearchResult:
        """
        Dijkstra's Algorithm (A* with h(n) = 0).
        Guarantees shortest path by exploring lowest cumulative cost g(n).
        """
        t0 = time.perf_counter_ns()

        if start not in self.sg.graph or goal not in self.sg.graph:
            return self._build_result("Dijkstra", routing_mode, start, goal, [], 0, 0, 0, [], 0.0, "Start or goal not in graph.")

        if start == goal:
            t1 = time.perf_counter_ns()
            return self._build_result("Dijkstra", routing_mode, start, goal, [start], 0.0, 1, 1, [start], (t1 - t0) / 1e6)

        counter = 0
        frontier: List[Tuple[float, int, str]] = []
        heapq.heappush(frontier, (0.0, counter, start))

        dist: Dict[str, float] = {start: 0.0}
        parent: Dict[str, Optional[str]] = {start: None}
        explored_nodes: List[str] = []
        visited: Set[str] = set()
        nodes_generated = 1

        while frontier:
            current_dist, _, current = heapq.heappop(frontier)

            if current in visited:
                continue

            visited.add(current)
            explored_nodes.append(current)

            if current == goal:
                t1 = time.perf_counter_ns()
                path = self._reconstruct_path(parent, goal)
                return self._build_result("Dijkstra", routing_mode, start, goal, path, dist[goal],
                                           len(visited), nodes_generated, explored_nodes, (t1 - t0) / 1e6)

            for neighbor in self.sg.graph.neighbors(current):
                weight = self.get_edge_weight(current, neighbor, routing_mode)
                if weight is None:
                    continue

                tentative_dist = current_dist + weight
                if neighbor not in dist or tentative_dist < dist[neighbor]:
                    dist[neighbor] = tentative_dist
                    parent[neighbor] = current
                    counter += 1
                    nodes_generated += 1
                    heapq.heappush(frontier, (tentative_dist, counter, neighbor))

        t1 = time.perf_counter_ns()
        return self._build_result("Dijkstra", routing_mode, start, goal, [], float("inf"),
                                   len(visited), nodes_generated, explored_nodes, (t1 - t0) / 1e6, "No valid path found.")

    def greedy_best_first_search(self, start: str, goal: str, routing_mode: str = "shortest") -> SearchResult:
        """
        Greedy Best-First Search (A* with g(n) = 0).
        Priority: f(n) = h(n). Fast heuristic exploration, but not guaranteed optimal.
        """
        t0 = time.perf_counter_ns()

        if start not in self.sg.graph or goal not in self.sg.graph:
            return self._build_result("Greedy Best-First", routing_mode, start, goal, [], 0, 0, 0, [], 0.0, "Start or goal not in graph.")

        if start == goal:
            t1 = time.perf_counter_ns()
            return self._build_result("Greedy Best-First", routing_mode, start, goal, [start], 0.0, 1, 1, [start], (t1 - t0) / 1e6)

        counter = 0
        frontier: List[Tuple[float, int, str]] = []
        h_start = self.heuristic(start, goal, routing_mode)
        heapq.heappush(frontier, (h_start, counter, start))

        parent: Dict[str, Optional[str]] = {start: None}
        explored_nodes: List[str] = []
        visited: Set[str] = set()
        nodes_generated = 1

        while frontier:
            h_val, _, current = heapq.heappop(frontier)

            if current in visited:
                continue

            visited.add(current)
            explored_nodes.append(current)

            if current == goal:
                t1 = time.perf_counter_ns()
                path = self._reconstruct_path(parent, goal)
                # Compute total cost of greedy path
                cost = 0.0
                for i in range(len(path) - 1):
                    w = self.get_edge_weight(path[i], path[i + 1], routing_mode)
                    if w is not None:
                        cost += w
                return self._build_result("Greedy Best-First", routing_mode, start, goal, path, cost,
                                           len(visited), nodes_generated, explored_nodes, (t1 - t0) / 1e6)

            for neighbor in self.sg.graph.neighbors(current):
                weight = self.get_edge_weight(current, neighbor, routing_mode)
                if weight is None:
                    continue

                if neighbor not in visited and neighbor not in parent:
                    parent[neighbor] = current
                    h_next = self.heuristic(neighbor, goal, routing_mode)
                    counter += 1
                    nodes_generated += 1
                    heapq.heappush(frontier, (h_next, counter, neighbor))

        t1 = time.perf_counter_ns()
        return self._build_result("Greedy Best-First", routing_mode, start, goal, [], float("inf"),
                                   len(visited), nodes_generated, explored_nodes, (t1 - t0) / 1e6, "No valid path found.")

    def bfs_search(self, start: str, goal: str, routing_mode: str = "shortest") -> SearchResult:
        """
        Breadth-First Search (BFS).
        Finds minimum unweighted edge hop count.
        """
        t0 = time.perf_counter_ns()

        if start not in self.sg.graph or goal not in self.sg.graph:
            return self._build_result("BFS", routing_mode, start, goal, [], 0, 0, 0, [], 0.0, "Start or goal not in graph.")

        if start == goal:
            t1 = time.perf_counter_ns()
            return self._build_result("BFS", routing_mode, start, goal, [start], 0.0, 1, 1, [start], (t1 - t0) / 1e6)

        queue = deque([start])
        visited: Set[str] = {start}
        parent: Dict[str, Optional[str]] = {start: None}
        explored_nodes: List[str] = []
        nodes_generated = 1

        while queue:
            current = queue.popleft()
            explored_nodes.append(current)

            if current == goal:
                t1 = time.perf_counter_ns()
                path = self._reconstruct_path(parent, goal)
                cost = 0.0
                for i in range(len(path) - 1):
                    w = self.get_edge_weight(path[i], path[i + 1], routing_mode)
                    if w is not None:
                        cost += w
                return self._build_result("BFS", routing_mode, start, goal, path, cost,
                                           len(explored_nodes), nodes_generated, explored_nodes, (t1 - t0) / 1e6)

            for neighbor in self.sg.graph.neighbors(current):
                weight = self.get_edge_weight(current, neighbor, routing_mode)
                if weight is None:
                    continue

                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    nodes_generated += 1
                    queue.append(neighbor)

        t1 = time.perf_counter_ns()
        return self._build_result("BFS", routing_mode, start, goal, [], float("inf"),
                                   len(explored_nodes), nodes_generated, explored_nodes, (t1 - t0) / 1e6, "No valid path found.")

    def run_all(self, start: str, goal: str, routing_mode: str = "shortest") -> Dict[str, SearchResult]:
        """
        Run all 4 algorithms on the exact same graph configuration and return comparison dict.
        """
        return {
            "A*": self.a_star_search(start, goal, routing_mode),
            "Dijkstra": self.dijkstra_search(start, goal, routing_mode),
            "Greedy Best-First": self.greedy_best_first_search(start, goal, routing_mode),
            "BFS": self.bfs_search(start, goal, routing_mode)
        }
