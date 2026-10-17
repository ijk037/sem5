"""
Interactive UI and Geospatial Route Visualization Application (Phase 3 & Phase 4).
Streamlit Application for Manipal University Jaipur (MUJ) Campus AI Navigation.
"""

import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from src.spatial_graph import SpatialGraph, haversine_distance
from src.search_engine import SearchEngine, SearchResult
from src.dynamic_simulation import CampusEventSimulator
from src.visualizer import CampusVisualizer, NODE_TYPE_COLORS

# Streamlit Page Config
st.set_page_config(
    page_title="MUJ AI Campus Navigator | AISC Heuristic Search Engine",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .metric-box {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px 16px;
        border-left: 4px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .event-card {
        background: #FEF3C7;
        border: 1px solid #F59E0B;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_graph_and_engine():
    """Load base graph and initialize singleton engine."""
    sg = SpatialGraph()
    loc_path = os.path.join("data", "locations.csv")
    conn_path = os.path.join("data", "connections.csv")
    sg.load_from_csv(loc_path, conn_path)
    simulator = CampusEventSimulator(sg)
    engine = SearchEngine(sg)
    visualizer = CampusVisualizer(sg)
    return sg, simulator, engine, visualizer


sg, simulator, engine, visualizer = get_graph_and_engine()

# --- Sidebar Controls ---
st.sidebar.image("https://img.icons8.com/isometric/100/map-marker.png", width=60)
st.sidebar.markdown("### 🗺️ **Routing Controls**")

# Ingestion Source Selector
data_source = st.sidebar.radio(
    "Data Source Mode",
    ["Curated MUJ Campus Dataset (CSV)", "OpenStreetMap Live Query (OSMnx)"],
    index=0
)

if data_source == "OpenStreetMap Live Query (OSMnx)":
    if st.sidebar.button("📥 Query OSM for MUJ Walkways"):
        with st.spinner("Querying OpenStreetMap for 'Manipal University Jaipur, India'..."):
            success = sg.load_from_osmnx(
                place_name="Manipal University Jaipur, India",
                network_type="walk",
                fallback_to_csv=True,
                csv_locations=os.path.join("data", "locations.csv"),
                csv_connections=os.path.join("data", "connections.csv")
            )
            if success:
                st.sidebar.success(f"Loaded {len(sg.graph.nodes)} nodes from OSMnx!")
            else:
                st.sidebar.warning("OSMnx query timed out / unavailable. Loaded curated CSV fallback.")

# Node selection dictionary
node_options = {node_id: f"{data.get('name', node_id)} ({data.get('node_type', 'POI').title()})"
                for node_id, data in sg.graph.nodes(data=True)}
sorted_node_ids = sorted(node_options.keys(), key=lambda k: node_options[k])

col_start, col_goal = st.sidebar.columns(2)
with col_start:
    start_default_idx = sorted_node_ids.index("GATE_1") if "GATE_1" in sorted_node_ids else 0
    start_node = st.selectbox(
        "📍 Start Location",
        options=sorted_node_ids,
        index=start_default_idx,
        format_func=lambda x: node_options.get(x, x)
    )

with col_goal:
    goal_default_idx = sorted_node_ids.index("SPORTS_COMPLEX_INDOOR") if "SPORTS_COMPLEX_INDOOR" in sorted_node_ids else 1
    goal_node = st.selectbox(
        "🏁 Destination",
        options=sorted_node_ids,
        index=goal_default_idx,
        format_func=lambda x: node_options.get(x, x)
    )

st.sidebar.markdown("---")

# Routing Preference Mode
st.sidebar.markdown("### 🎯 **Routing Preference**")
routing_mode = st.sidebar.selectbox(
    "Optimization Objective",
    options=["shortest", "quickest", "accessible", "sheltered"],
    format_func=lambda x: {
        "shortest": "🏃 Shortest Distance (Meters)",
        "quickest": "⚡ Quickest Path (Crowd-Aware Travel Time)",
        "accessible": "♿ Accessible Path (Wheelchair / No Stairs)",
        "sheltered": "☔ Weather-Sheltered (Indoor Corridor Preference)"
    }.get(x, x),
    index=0
)

# Algorithm Choice
st.sidebar.markdown("### 🤖 **Search Algorithm**")
algo_choice = st.sidebar.selectbox(
    "Algorithm Engine",
    options=["A*", "Dijkstra", "Greedy Best-First", "BFS", "Compare All 4"],
    index=4
)

# Show explored footprint checkbox
show_exploration = st.sidebar.checkbox("🔍 Highlight Algorithm Explored Footprint", value=True)

st.sidebar.markdown("---")

# --- Dynamic Campus Event Simulation Panel ---
st.sidebar.markdown("### ⚡ **Live Campus Event Simulator**")
with st.sidebar.expander("🚨 Trigger Simulated Campus Events", expanded=False):
    rush_toggle = st.checkbox("👥 Peak-Hour Class Transition Rush (2.0x Crowd)")
    block_toggle = st.checkbox("🚧 Main Walkway Construction Blockage")
    rain_toggle = st.checkbox("🌧️ Heavy Monsoon Rain & Flood Steps")

    # Apply or reset simulation events
    simulator.clear_all_events()

    if rush_toggle:
        simulator.apply_peak_hour_rush(crowd_multiplier=2.0)
        st.info("Peak-hour crowd surge active along central arteries.")

    if block_toggle:
        simulator.apply_pathway_construction()
        st.warning("Pavement construction active: Central corridors blocked.")

    if rain_toggle:
        simulator.apply_rain_and_waterlogging(outdoor_penalty=3.0, block_low_lying=True)
        st.info("Monsoon mode: Outdoor paths slowed 3x; Amphitheatre steps flooded.")

    if st.button("🔄 Reset All Graph Conditions"):
        simulator.clear_all_events()
        st.rerun()

# --- Main App Header ---
st.markdown('<div class="main-header">🏛️ Manipal University Jaipur — AI Spatial Navigation System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Criteria Heuristic Search Engine (A*, Dijkstra, Greedy Best-First, BFS) on Campus Graph</div>', unsafe_allow_html=True)

# Active events alert banner
active_evs = simulator.get_active_events()
if active_evs:
    st.markdown("##### ⚠️ **Active Dynamic Campus Conditions:**")
    cols = st.columns(len(active_evs))
    for i, ev in enumerate(active_evs):
        with cols[i]:
            st.markdown(f"<div class='event-card'><b>{ev['name']}</b><br><small>{ev['description']}</small></div>", unsafe_allow_html=True)

# Execute Search Algorithms
if algo_choice == "Compare All 4":
    all_results = engine.run_all(start_node, goal_node, routing_mode)
    primary_result = all_results["A*"]
else:
    if algo_choice == "A*":
        primary_result = engine.a_star_search(start_node, goal_node, routing_mode)
    elif algo_choice == "Dijkstra":
        primary_result = engine.dijkstra_search(start_node, goal_node, routing_mode)
    elif algo_choice == "Greedy Best-First":
        primary_result = engine.greedy_best_first_search(start_node, goal_node, routing_mode)
    else:
        primary_result = engine.bfs_search(start_node, goal_node, routing_mode)
    all_results = {algo_choice: primary_result}

# Layout: Map on left (70%), Details & Metrics on right (30%)
col_map, col_metrics = st.columns([7, 5])

with col_map:
    st.markdown(f"#### 🗺️ **Interactive Campus Route Map ({primary_result.algorithm})**")

    # Generate Folium Map
    m = visualizer.create_base_map(zoom_start=17)
    explored_to_show = primary_result.explored_nodes if show_exploration else None
    visualizer.render_campus_graph(m, highlight_explored=explored_to_show, search_result=primary_result)

    # Render Map in Streamlit
    st_data = st_folium(m, width="100%", height=520)

with col_metrics:
    st.markdown("#### 📊 **Executive Route Performance**")

    if not primary_result.success:
        st.error(f"❌ **No valid path found from {start_node} to {goal_node}!**\n{primary_result.error_message or 'The destination is disconnected under current constraints.'}")
    else:
        # 4 Key Metric Cards
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(
                label="📏 Total Distance",
                value=f"{primary_result.total_distance_meters:.1f} m",
                delta=f"{primary_result.total_distance_meters/1000:.2f} km"
            )
            st.metric(
                label="🧠 Node Expansions",
                value=f"{primary_result.node_expansions} nodes",
                delta=f"{primary_result.nodes_generated} generated"
            )
        with m_col2:
            walk_mins = primary_result.estimated_time_seconds / 60.0
            st.metric(
                label="⏱️ Est. Walking Time",
                value=f"{walk_mins:.1f} min",
                delta=f"{primary_result.estimated_time_seconds:.0f} sec"
            )
            st.metric(
                label="⚡ Compute Time",
                value=f"{primary_result.execution_time_ms:.3f} ms"
            )

        # Turn-by-Turn Waypoints
        with st.expander("📍 **Turn-by-Turn Waypoint Directions**", expanded=True):
            for i, name in enumerate(primary_result.path_names, start=1):
                nid = primary_result.path[i-1]
                ndata = sg.graph.nodes[nid]
                badge = "🏠 Indoor" if ndata.get("indoor", False) else "🌳 Outdoor"
                if i == 1:
                    st.markdown(f"🟢 **Start:** {name} `[{badge}]`")
                elif i == len(primary_result.path_names):
                    st.markdown(f"🏁 **Arrive at:** {name} `[{badge}]`")
                else:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ **Step {i-1}:** {name} `[{badge}]`")

# --- Comparative Benchmark Section ---
st.markdown("---")
st.markdown("### 🏆 **Multi-Algorithm Benchmark & Optimality Comparison**")

benchmark_rows = []
for algo_name, res in all_results.items():
    benchmark_rows.append({
        "Algorithm": algo_name,
        "Success": "✅ Yes" if res.success else "❌ No",
        "Path Length (Hops)": len(res.path) - 1 if res.path else 0,
        "Total Distance (m)": f"{res.total_distance_meters:.2f}",
        "Est. Time (min)": f"{res.estimated_time_seconds / 60.0:.2f}",
        "Cost": f"{res.total_cost:.2f}",
        "Node Expansions (Fewer is Better)": res.node_expansions,
        "Nodes Generated": res.nodes_generated,
        "Execution Time (ms)": f"{res.execution_time_ms:.4f}"
    })

df_benchmarks = pd.DataFrame(benchmark_rows)

col_tbl, col_chart = st.columns([7, 5])
with col_tbl:
    st.dataframe(df_benchmarks, use_container_width=True)

with col_chart:
    # Bar chart comparing Node Expansions
    chart_data = pd.DataFrame({
        "Algorithm": list(all_results.keys()),
        "Node Expansions": [res.node_expansions for res in all_results.values()]
    }).set_index("Algorithm")
    st.bar_chart(chart_data, color="#2563EB")

# --- Campus Graph Topological Summary ---
with st.expander("📐 **Campus Graph Topological Summary & Admissibility Guarantee**", expanded=False):
    summary = sg.get_summary()
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    s_col1.metric("Total Landmarks / Nodes", summary["num_nodes"])
    s_col2.metric("Total Interconnected Walkways", summary["num_edges"])
    s_col3.metric("Total Network Length", f"{summary['total_pathway_length_meters']} m")
    s_col4.metric("Avg Degree (Connectivity)", summary["average_degree"])

    st.markdown("""
    **Heuristic Admissibility & Consistency Mathematical Guarantee:**
    - **Admissibility ($h(n) \le h^*(n)$):** The Haversine straight-line distance represents the shortest possible geodesic path between two points on the Earth's sphere. No physical walkable path can be shorter than this straight-line bound, ensuring $h(n)$ never overestimates the true remaining distance.
    - **Consistency / Monotonicity ($h(u) \le c(u, v) + h(v)$):** By the spherical triangle inequality, the direct geodesic distance from $u$ to $goal$ is always less than or equal to the actual edge distance $c(u, v)$ plus the geodesic distance from $v$ to $goal$.
    """)
