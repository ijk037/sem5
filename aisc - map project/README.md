# 🏛️ Manipal University Jaipur (MUJ) AI Spatial Navigation System
### *Artificial Intelligence & Soft Computing (AISC) Heuristic Pathfinding Project*

A multi-criteria campus spatial graph search engine and interactive geospatial navigation dashboard built from scratch using Python, NetworkX, Folium, and Streamlit.

---

## 📌 Project Overview & Architecture

This project is organized across **4 distinct engineering phases**:

```
D:\vsc\aisc - map project\
├── data/
│   ├── locations.csv                  # 35 Campus Landmark nodes (Coordinates, POI type, accessibility)
│   ├── connections.csv                # 50 Interconnected pathways (Stairs, crowd factors, indoor flags)
│   └── generate_data.py               # Robust CSV data generator
├── src/
│   ├── spatial_graph.py              # Phase 1: Spatial Graph representation, Haversine, OSMnx & CSV ingestion
│   ├── search_engine.py              # Phase 2: A*, Dijkstra, Greedy Best-First, BFS with heapq & metrics
│   ├── visualizer.py                 # Phase 3: Folium Leaflet geospatial renderer & exploration footprint
│   └── dynamic_simulation.py         # Phase 4: Peak-hour rush, pathway blockages, monsoon rain simulator
├── tests/
│   ├── test_spatial_graph.py         # Unit tests for spatial ingestion & nearest neighbor
│   ├── test_search_engine.py         # Unit tests for optimality, admissibility & consistency
│   ├── test_edge_cases.py            # Edge cases: disconnected subgraphs, cycles, blockages
│   └── test_dynamic_simulation.py    # Event simulator stress-testing
├── app.py                            # Streamlit Interactive Web Application & Visualizer
├── run_benchmarks.py                 # Automated CLI benchmark suite
└── requirements.txt                  # Python dependencies
```

---

## 📐 Mathematical Formulation & Heuristic Guarantees

### 1. Haversine Straight-Line Distance
Calculates the exact great-circle distance between two geographic coordinates $(\phi_1, \lambda_1)$ and $(\phi_2, \lambda_2)$:
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$d = 2 R \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right) \quad (\text{where } R = 6,371,000 \text{ m})$$

### 2. Multi-Criteria Path Cost $g(n)$
- **Shortest Distance Mode**: $g(n) = \sum \text{physical\_length}$
- **Quickest Mode (Crowd-Aware)**:
  $$\text{Effective Speed } v_{\text{eff}} = \frac{v_0}{\text{crowd\_factor}}, \quad t(u, v) = \frac{\text{length}}{v_{\text{eff}}}$$
- **Accessible Mode (Wheelchair Friendly)**: Total pruning ($W = \infty$) if $\text{has\_stairs} = \text{True}$ or $\text{wheelchair\_accessible} = \text{False}$.
- **Weather-Sheltered Mode**: $3.0\times$ penalty applied on open-air pathways during rain.

### 3. Admissibility & Consistency of Heuristic $h(n)$
- **Admissibility ($h(n) \le h^*(n)$)**: The Haversine distance is the shortest physical distance connecting any two coordinates on the Earth sphere; therefore, it never overestimates the true remaining path cost.
- **Consistency / Monotonicity ($h(u) \le c(u, v) + h(v)$)**: Guaranteed by the spherical triangle inequality.

---

## 🚀 How to Run the Project

### 1. Run the Interactive Streamlit Web App
```powershell
streamlit run app.py
```

### 2. Run the Benchmark Comparison CLI Suite
```powershell
python run_benchmarks.py
```

### 3. Run the Automated Unit Test Suite (16 Tests)
```powershell
python -m pytest tests/ -v
```

---

## 📊 Benchmark Summary (A* vs Dijkstra vs Greedy vs BFS)

| Scenario | Mode | Optimal Distance | A* Expansions | Dijkstra Expansions | Efficiency Improvement |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Long Campus Traverse** | Shortest | 684.1 m | **13 nodes** | 35 nodes | **62.9% fewer expansions** |
| **Hostel to Academic Corridor** | Shortest | 381.2 m | **8 nodes** | 16 nodes | **50.0% fewer expansions** |
| **Accessible Cross-Campus** | Accessible | 339.1 m | **6 nodes** | 15 nodes | **60.0% fewer expansions** |
| **Peak-Hour Lunch Rush** | Quickest | 364.4 m | **13 nodes** | 34 nodes | **61.8% fewer expansions** |
| **Sports to Dining Plaza** | Shortest | 359.8 m | **4 nodes** | 18 nodes | **77.8% fewer expansions** |
