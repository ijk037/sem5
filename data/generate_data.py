import csv
import os

locations = [
    {
        "id": "GATE_1",
        "name": "Main Gate 1 (Jaipur-Ajmer Expressway)",
        "latitude": 26.84150,
        "longitude": 75.56420,
        "node_type": "gate",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Main campus vehicle and pedestrian entrance on highway"
    },
    {
        "id": "GATE_2",
        "name": "Hostel Gate 2 (West Perimeter)",
        "latitude": 26.84320,
        "longitude": 75.56180,
        "node_type": "gate",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Access gate near student residence area"
    },
    {
        "id": "GATE_3",
        "name": "Sports Complex Service Gate",
        "latitude": 26.84610,
        "longitude": 75.56580,
        "node_type": "gate",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Service and athletic field access"
    },
    {
        "id": "JUNC_MAIN_BOULEVARD",
        "name": "Main Boulevard Roundabout",
        "latitude": 26.84230,
        "longitude": 75.56450,
        "node_type": "junction",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Primary vehicular and pedestrian circulation ring"
    },
    {
        "id": "DOME_BUILDING",
        "name": "The Grand Dome (Central Admin)",
        "latitude": 26.84310,
        "longitude": 75.56490,
        "node_type": "academic",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Iconic administrative dome and chancellor office"
    },
    {
        "id": "AB1_MAIN",
        "name": "Academic Block 1 - Main Atrium",
        "latitude": 26.84380,
        "longitude": 75.56460,
        "node_type": "academic",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Engineering block ground floor entrance and atrium"
    },
    {
        "id": "AB1_EAST_STAIRS",
        "name": "AB-1 East Staircase (Level 1-2)",
        "latitude": 26.84395,
        "longitude": 75.56510,
        "node_type": "academic",
        "wheelchair_accessible": False,
        "indoor": True,
        "description": "Stair-only indoor access connecting AB1 labs to Library walkway"
    },
    {
        "id": "AB1_RAMP_ENTRANCE",
        "name": "AB-1 West Accessible Ramp",
        "latitude": 26.84370,
        "longitude": 75.56410,
        "node_type": "academic",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Dedicated wide wheelchair ramp connecting to AB1"
    },
    {
        "id": "AB2_MAIN",
        "name": "Academic Block 2 - Science & Design",
        "latitude": 26.84460,
        "longitude": 75.56440,
        "node_type": "academic",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Architecture and basic sciences block main atrium"
    },
    {
        "id": "AB2_RAMP",
        "name": "AB-2 East Accessible Entrance",
        "latitude": 26.84470,
        "longitude": 75.56490,
        "node_type": "academic",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Sloped ramp access to AB-2 lecture halls"
    },
    {
        "id": "LIBRARY_CENTRAL",
        "name": "Central Library & Digital Hub",
        "latitude": 26.84420,
        "longitude": 75.56550,
        "node_type": "academic",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "3-story air-conditioned central library and digital reading room"
    },
    {
        "id": "LIBRARY_PLAZA",
        "name": "Library Front Plaza",
        "latitude": 26.84380,
        "longitude": 75.56560,
        "node_type": "junction",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Shaded pedestrian promenade near fountain"
    },
    {
        "id": "AUDITORIUM",
        "name": "TMA Pai Central Auditorium",
        "latitude": 26.84280,
        "longitude": 75.56580,
        "node_type": "facility",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "1500-seat multi-purpose university auditorium"
    },
    {
        "id": "OAT_BOTTOM",
        "name": "Open Air Theatre (OAT Stage)",
        "latitude": 26.84480,
        "longitude": 75.56610,
        "node_type": "facility",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Amphitheater performance arena ground level"
    },
    {
        "id": "OAT_TOP_STEPS",
        "name": "OAT Upper Tier Steps",
        "latitude": 26.84510,
        "longitude": 75.56630,
        "node_type": "facility",
        "wheelchair_accessible": False,
        "indoor": False,
        "description": "Steep concrete seating steps (stairs only route)"
    },
    {
        "id": "FOOD_COURT",
        "name": "Main Food Court (FC)",
        "latitude": 26.84350,
        "longitude": 75.56680,
        "node_type": "dining",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Central multi-cuisine food court and student lounge"
    },
    {
        "id": "MESS_GRAND",
        "name": "Grand Student Mess 1",
        "latitude": 26.84390,
        "longitude": 75.56720,
        "node_type": "dining",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Primary hostel student dining hall"
    },
    {
        "id": "TAPRI_CORNER",
        "name": "Student Plaza & Tapri Canteen",
        "latitude": 26.84310,
        "longitude": 75.56650,
        "node_type": "dining",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Outdoor seating and evening snacks pavilion"
    },
    {
        "id": "NESCAFE_KIOSK",
        "name": "Nescafe Green Kiosk",
        "latitude": 26.84430,
        "longitude": 75.56480,
        "node_type": "dining",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Quick beverage kiosk between AB1 and Library"
    },
    {
        "id": "HOSTEL_CIRCLE",
        "name": "Hostel Central Circle Junction",
        "latitude": 26.84350,
        "longitude": 75.56300,
        "node_type": "junction",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Hub connecting boys and girls hostel clusters"
    },
    {
        "id": "HOSTEL_B1_B2",
        "name": "Boys Hostels Cluster (B1-B2)",
        "latitude": 26.84420,
        "longitude": 75.56260,
        "node_type": "hostel",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "First-year boys residential wing"
    },
    {
        "id": "HOSTEL_B3_B4",
        "name": "Boys Hostels Cluster (B3-B4)",
        "latitude": 26.84490,
        "longitude": 75.56240,
        "node_type": "hostel",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Senior boys residential wing"
    },
    {
        "id": "HOSTEL_B5_B6",
        "name": "Boys Hostels Cluster (B5-B6)",
        "latitude": 26.84560,
        "longitude": 75.56220,
        "node_type": "hostel",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Boys hostel block with gym annex"
    },
    {
        "id": "HOSTEL_G1_G2",
        "name": "Girls Hostels Cluster (G1-G2)",
        "latitude": 26.84260,
        "longitude": 75.56320,
        "node_type": "hostel",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Girls residential complex 1"
    },
    {
        "id": "HOSTEL_G3_G4",
        "name": "Girls Hostels Cluster (G3-G4)",
        "latitude": 26.84200,
        "longitude": 75.56290,
        "node_type": "hostel",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Girls residential complex 2"
    },
    {
        "id": "HOSTEL_MESS_B",
        "name": "Boys Mess & Recreational Hall",
        "latitude": 26.84470,
        "longitude": 75.56310,
        "node_type": "dining",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Hostel mess serving blocks B1-B6"
    },
    {
        "id": "SPORTS_COMPLEX_INDOOR",
        "name": "Indoor Sports Complex & Badminton",
        "latitude": 26.84580,
        "longitude": 75.56480,
        "node_type": "sports",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Squash badminton and indoor gymnasium"
    },
    {
        "id": "FOOTBALL_GROUND",
        "name": "MUJ Football & Athletic Arena",
        "latitude": 26.84650,
        "longitude": 75.56380,
        "node_type": "sports",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Grass football stadium with running track"
    },
    {
        "id": "CRICKET_GROUND",
        "name": "MUJ Cricket Pavilion",
        "latitude": 26.84700,
        "longitude": 75.56540,
        "node_type": "sports",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Standard cricket ground and practice nets"
    },
    {
        "id": "BASKETBALL_COURTS",
        "name": "Outdoor Basketball & Tennis Courts",
        "latitude": 26.84530,
        "longitude": 75.56410,
        "node_type": "sports",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Synthetic outdoor illuminated sports courts"
    },
    {
        "id": "SWIMMING_POOL",
        "name": "Olympic Standard Swimming Pool",
        "latitude": 26.84620,
        "longitude": 75.56500,
        "node_type": "sports",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Aquatic center with ramp entrance"
    },
    {
        "id": "HEALTH_CENTRE",
        "name": "Campus Medical & Emergency Centre",
        "latitude": 26.84220,
        "longitude": 75.56380,
        "node_type": "facility",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "24x7 medical clinic and ambulance bay"
    },
    {
        "id": "INCUBATION_CENTRE",
        "name": "Atal Incubation Centre (AIC-MUJ)",
        "latitude": 26.84270,
        "longitude": 75.56420,
        "node_type": "facility",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Startup incubator and innovation lab"
    },
    {
        "id": "LAUNDRY_HUB",
        "name": "Central Student Laundry & Tuck Shop",
        "latitude": 26.84310,
        "longitude": 75.56240,
        "node_type": "facility",
        "wheelchair_accessible": True,
        "indoor": False,
        "description": "Student utility hub and laundry center"
    },
    {
        "id": "ATM_BLOCK",
        "name": "Banking Kiosks & ATM Centre",
        "latitude": 26.84200,
        "longitude": 75.56460,
        "node_type": "facility",
        "wheelchair_accessible": True,
        "indoor": True,
        "description": "Bank branches and 24/7 ATMs"
    }
]

connections = [
    ("GATE_1", "ATM_BLOCK", False, True, False, 1.0, False, True, "Main Gate to ATM Walkway"),
    ("GATE_1", "JUNC_MAIN_BOULEVARD", False, True, False, 1.1, False, True, "Main Entry Boulevard"),
    ("ATM_BLOCK", "JUNC_MAIN_BOULEVARD", False, True, False, 1.0, False, True, "ATM to Boulevard Cross"),
    ("JUNC_MAIN_BOULEVARD", "HEALTH_CENTRE", False, True, False, 1.0, False, True, "Medical Centre Approach"),
    ("HEALTH_CENTRE", "INCUBATION_CENTRE", False, True, False, 1.0, False, True, "Health Clinic to AIC Walkway"),
    ("INCUBATION_CENTRE", "DOME_BUILDING", False, True, False, 1.2, False, True, "AIC to Dome South Plaza"),
    ("JUNC_MAIN_BOULEVARD", "DOME_BUILDING", False, True, False, 1.2, False, True, "Dome Main Entrance Boulevard"),
    ("JUNC_MAIN_BOULEVARD", "HOSTEL_G3_G4", False, True, False, 1.0, False, True, "Boulevard to Girls Hostel South"),
    ("HOSTEL_G3_G4", "HOSTEL_G1_G2", False, True, False, 1.1, False, True, "Girls Hostel Promenade"),
    ("HOSTEL_G1_G2", "HOSTEL_CIRCLE", False, True, False, 1.3, False, True, "Girls Hostel to Central Circle"),
    ("HOSTEL_CIRCLE", "GATE_2", False, True, False, 1.0, False, True, "Hostel Circle to West Gate 2"),
    ("GATE_2", "LAUNDRY_HUB", False, True, False, 1.0, False, True, "Gate 2 to Laundry Hub"),
    ("HOSTEL_CIRCLE", "LAUNDRY_HUB", False, True, False, 1.1, False, True, "Laundry Pathway"),
    ("HOSTEL_CIRCLE", "AB1_RAMP_ENTRANCE", False, True, False, 1.4, False, True, "Hostels to Academic Block 1 Ramp"),
    ("HOSTEL_CIRCLE", "HOSTEL_B1_B2", False, True, False, 1.3, False, True, "Hostel Circle to Boys Block B1-B2"),
    ("HOSTEL_B1_B2", "HOSTEL_B3_B4", False, True, False, 1.2, False, True, "Boys Hostel Spine Road"),
    ("HOSTEL_B3_B4", "HOSTEL_B5_B6", False, True, False, 1.1, False, True, "Boys Hostel North Extension"),
    ("HOSTEL_B1_B2", "HOSTEL_MESS_B", False, True, False, 1.5, False, False, "Covered Walkway to Boys Mess"),
    ("HOSTEL_B3_B4", "HOSTEL_MESS_B", False, True, False, 1.4, False, False, "Direct Mess Entry"),
    ("HOSTEL_B1_B2", "AB1_RAMP_ENTRANCE", False, True, False, 1.3, False, True, "Hostel B1 Pathway to AB1 Ramp"),
    ("AB1_RAMP_ENTRANCE", "AB1_MAIN", False, True, False, 1.2, False, False, "Accessible West Ramp into AB1"),
    ("DOME_BUILDING", "AB1_MAIN", False, True, True, 1.3, False, False, "Dome to AB1 Central Covered Corridor"),
    ("AB1_MAIN", "AB1_EAST_STAIRS", True, False, True, 1.6, False, False, "AB1 Ground to East Lab Stairs"),
    ("AB1_MAIN", "NESCAFE_KIOSK", False, True, False, 1.4, False, True, "AB1 East Exit to Nescafe Kiosk"),
    ("AB1_MAIN", "AB2_MAIN", False, True, True, 1.7, False, False, "AB1-AB2 Connected Indoor Galleria"),
    ("AB1_EAST_STAIRS", "LIBRARY_CENTRAL", False, True, False, 1.3, False, True, "East Exit to Library North Door"),
    ("NESCAFE_KIOSK", "LIBRARY_CENTRAL", False, True, False, 1.5, False, True, "Nescafe to Central Library Plaza"),
    ("NESCAFE_KIOSK", "AB2_MAIN", False, True, False, 1.2, False, True, "Nescafe to AB2 Front Porch"),
    ("AB2_MAIN", "AB2_RAMP", False, True, False, 1.1, False, False, "AB2 East Ramp Walkway"),
    ("AB2_RAMP", "SPORTS_COMPLEX_INDOOR", False, True, False, 1.2, False, True, "AB2 to Indoor Sports Walkway"),
    ("AB2_MAIN", "BASKETBALL_COURTS", False, True, False, 1.1, False, True, "AB2 North to Basketball Court"),
    ("LIBRARY_CENTRAL", "LIBRARY_PLAZA", False, True, False, 1.4, False, False, "Central Library Portico to Plaza"),
    ("DOME_BUILDING", "AUDITORIUM", False, True, False, 1.1, False, True, "Dome East Walkway to Auditorium"),
    ("AUDITORIUM", "FOOD_COURT", False, True, False, 1.3, False, True, "Auditorium to Food Court Path"),
    ("LIBRARY_PLAZA", "FOOD_COURT", False, True, False, 1.6, False, True, "Library Plaza to Food Court Boulevard"),
    ("FOOD_COURT", "MESS_GRAND", False, True, False, 1.8, False, False, "Food Court to Grand Mess Corridor"),
    ("FOOD_COURT", "TAPRI_CORNER", False, True, False, 1.5, False, True, "Food Court to Student Tapri Plaza"),
    ("AUDITORIUM", "TAPRI_CORNER", False, True, False, 1.2, False, True, "Auditorium to Tapri Pathway"),
    ("LIBRARY_PLAZA", "OAT_BOTTOM", False, True, False, 1.2, False, True, "Library to OAT Ground Level"),
    ("OAT_BOTTOM", "OAT_TOP_STEPS", True, False, False, 1.1, False, True, "OAT Amphitheatre Tier Stairs"),
    ("OAT_BOTTOM", "MESS_GRAND", False, True, False, 1.3, False, True, "OAT to Grand Mess Rear Path"),
    ("OAT_TOP_STEPS", "GATE_3", True, False, False, 1.0, False, True, "OAT Top Steps to Gate 3 Service Road"),
    ("LIBRARY_PLAZA", "SPORTS_COMPLEX_INDOOR", False, True, False, 1.2, False, True, "Library Plaza to Sports Arena"),
    ("SPORTS_COMPLEX_INDOOR", "SWIMMING_POOL", False, True, False, 1.1, False, True, "Sports Complex to Aquatic Center"),
    ("SWIMMING_POOL", "CRICKET_GROUND", False, True, False, 1.0, False, True, "Pool to Cricket Pavilion Path"),
    ("SPORTS_COMPLEX_INDOOR", "BASKETBALL_COURTS", False, True, False, 1.2, False, True, "Indoor Complex to Basketball Courts"),
    ("BASKETBALL_COURTS", "FOOTBALL_GROUND", False, True, False, 1.1, False, True, "Courts to Football Field"),
    ("FOOTBALL_GROUND", "HOSTEL_B5_B6", False, True, False, 1.1, False, True, "Football Ground to Hostel B5-B6 Spine"),
    ("SWIMMING_POOL", "GATE_3", False, True, False, 1.0, False, True, "Swimming Pool to Gate 3"),
    ("CRICKET_GROUND", "GATE_3", False, True, False, 1.0, False, True, "Cricket Ground to Gate 3")
]

# Write locations.csv
loc_headers = ["id", "name", "latitude", "longitude", "node_type", "wheelchair_accessible", "indoor", "description"]
with open("data/locations.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=loc_headers, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for loc in locations:
        writer.writerow(loc)

# Write connections.csv
conn_headers = ["source", "target", "has_stairs", "wheelchair_accessible", "is_indoor", "crowd_factor", "is_blocked", "weather_exposed", "path_name"]
with open("data/connections.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(conn_headers)
    for c in connections:
        writer.writerow(c)

print(f"Generated {len(locations)} locations and {len(connections)} connections with standard CSV formatting!")
