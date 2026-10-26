"""
Embedded Data and UI Fallbacks for Serverless & Container Environments.
Guarantees zero-dependency startup on Vercel without relying on filesystem asset bundling.
"""

import os

LOCATIONS_CSV = """id,name,latitude,longitude,node_type,wheelchair_accessible,indoor,description
GATE_1,Main Gate 1 (Jaipur-Ajmer Expressway),26.8415,75.5642,gate,True,False,Main campus vehicle and pedestrian entrance on highway
GATE_2,Hostel Gate 2 (West Perimeter),26.8432,75.5618,gate,True,False,Access gate near student residence area
GATE_3,Sports Complex Service Gate,26.8461,75.5658,gate,True,False,Service and athletic field access
JUNC_MAIN_BOULEVARD,Main Boulevard Roundabout,26.8423,75.5645,junction,True,False,Primary vehicular and pedestrian circulation ring
DOME_BUILDING,The Grand Dome (Central Admin),26.8431,75.5649,academic,True,True,Iconic administrative dome and chancellor office
AB1_MAIN,Academic Block 1 - Main Atrium,26.8438,75.5646,academic,True,True,Engineering block ground floor entrance and atrium
AB1_EAST_STAIRS,AB-1 East Staircase (Level 1-2),26.84395,75.5651,academic,False,True,Stair-only indoor access connecting AB1 labs to Library walkway
AB1_RAMP_ENTRANCE,AB-1 West Accessible Ramp,26.8437,75.5641,academic,True,False,Dedicated wide wheelchair ramp connecting to AB1
AB2_MAIN,Academic Block 2 - Science & Design,26.8446,75.5644,academic,True,True,Architecture and basic sciences block main atrium
AB2_RAMP,AB-2 East Accessible Entrance,26.8447,75.5649,academic,True,False,Sloped ramp access to AB-2 lecture halls
LIBRARY_CENTRAL,Central Library & Digital Hub,26.8442,75.5655,academic,True,True,3-story air-conditioned central library and digital reading room
LIBRARY_PLAZA,Library Front Plaza,26.8438,75.5656,junction,True,False,Shaded pedestrian promenade near fountain
AUDITORIUM,TMA Pai Central Auditorium,26.8428,75.5658,facility,True,True,1500-seat multi-purpose university auditorium
OAT_BOTTOM,Open Air Theatre (OAT Stage),26.8448,75.5661,facility,True,False,Amphitheater performance arena ground level
OAT_TOP_STEPS,OAT Upper Tier Steps,26.8451,75.5663,facility,False,False,Steep concrete seating steps (stairs only route)
FOOD_COURT,Main Food Court (FC),26.8435,75.5668,dining,True,True,Central multi-cuisine food court and student lounge
MESS_GRAND,Grand Student Mess 1,26.8439,75.5672,dining,True,True,Primary hostel student dining hall
TAPRI_CORNER,Student Plaza & Tapri Canteen,26.8431,75.5665,dining,True,False,Outdoor seating and evening snacks pavilion
NESCAFE_KIOSK,Nescafe Green Kiosk,26.8443,75.5648,dining,True,False,Quick beverage kiosk between AB1 and Library
HOSTEL_CIRCLE,Hostel Central Circle Junction,26.8435,75.563,junction,True,False,Hub connecting boys and girls hostel clusters
HOSTEL_B1_B2,Boys Hostels Cluster (B1-B2),26.8442,75.5626,hostel,True,True,First-year boys residential wing
HOSTEL_B3_B4,Boys Hostels Cluster (B3-B4),26.8449,75.5624,hostel,True,True,Senior boys residential wing
HOSTEL_B5_B6,Boys Hostels Cluster (B5-B6),26.8456,75.5622,hostel,True,True,Boys hostel block with gym annex
HOSTEL_G1_G2,Girls Hostels Cluster (G1-G2),26.8426,75.5632,hostel,True,True,Girls residential complex 1
HOSTEL_G3_G4,Girls Hostels Cluster (G3-G4),26.842,75.5629,hostel,True,True,Girls residential complex 2
HOSTEL_MESS_B,Boys Mess & Recreational Hall,26.8447,75.5631,dining,True,True,Hostel mess serving blocks B1-B6
SPORTS_COMPLEX_INDOOR,Indoor Sports Complex & Badminton,26.8458,75.5648,sports,True,True,Squash badminton and indoor gymnasium
FOOTBALL_GROUND,MUJ Football & Athletic Arena,26.8465,75.5638,sports,True,False,Grass football stadium with running track
CRICKET_GROUND,MUJ Cricket Pavilion,26.847,75.5654,sports,True,False,Standard cricket ground and practice nets
BASKETBALL_COURTS,Outdoor Basketball & Tennis Courts,26.8453,75.5641,sports,True,False,Synthetic outdoor illuminated sports courts
SWIMMING_POOL,Olympic Standard Swimming Pool,26.8462,75.565,sports,True,False,Aquatic center with ramp entrance
HEALTH_CENTRE,Campus Medical & Emergency Centre,26.8422,75.5638,facility,True,True,24x7 medical clinic and ambulance bay
INCUBATION_CENTRE,Atal Incubation Centre (AIC-MUJ),26.8427,75.5642,facility,True,True,Startup incubator and innovation lab
LAUNDRY_HUB,Central Student Laundry & Tuck Shop,26.8431,75.5624,facility,True,False,Student utility hub and laundry center
ATM_BLOCK,Banking Kiosks & ATM Centre,26.842,75.5646,facility,True,True,Bank branches and 24/7 ATMs"""

CONNECTIONS_CSV = """source,target,has_stairs,wheelchair_accessible,is_indoor,crowd_factor,is_blocked,weather_exposed,path_name
GATE_1,ATM_BLOCK,False,True,False,1.0,False,True,Main Gate to ATM Walkway
GATE_1,JUNC_MAIN_BOULEVARD,False,True,False,1.1,False,True,Main Entry Boulevard
ATM_BLOCK,JUNC_MAIN_BOULEVARD,False,True,False,1.0,False,True,ATM to Boulevard Cross
JUNC_MAIN_BOULEVARD,HEALTH_CENTRE,False,True,False,1.0,False,True,Medical Centre Approach
HEALTH_CENTRE,INCUBATION_CENTRE,False,True,False,1.0,False,True,Health Clinic to AIC Walkway
INCUBATION_CENTRE,DOME_BUILDING,False,True,False,1.2,False,True,AIC to Dome South Plaza
JUNC_MAIN_BOULEVARD,DOME_BUILDING,False,True,False,1.2,False,True,Dome Main Entrance Boulevard
JUNC_MAIN_BOULEVARD,HOSTEL_G3_G4,False,True,False,1.0,False,True,Boulevard to Girls Hostel South
HOSTEL_G3_G4,HOSTEL_G1_G2,False,True,False,1.1,False,True,Girls Hostel Promenade
HOSTEL_G1_G2,HOSTEL_CIRCLE,False,True,False,1.3,False,True,Girls Hostel to Central Circle
HOSTEL_CIRCLE,GATE_2,False,True,False,1.0,False,True,Hostel Circle to West Gate 2
GATE_2,LAUNDRY_HUB,False,True,False,1.0,False,True,Gate 2 to Laundry Hub
HOSTEL_CIRCLE,LAUNDRY_HUB,False,True,False,1.1,False,True,Laundry Pathway
HOSTEL_CIRCLE,AB1_RAMP_ENTRANCE,False,True,False,1.4,False,True,Hostels to Academic Block 1 Ramp
HOSTEL_CIRCLE,HOSTEL_B1_B2,False,True,False,1.3,False,True,Hostel Circle to Boys Block B1-B2
HOSTEL_B1_B2,HOSTEL_B3_B4,False,True,False,1.2,False,True,Boys Hostel Spine Road
HOSTEL_B3_B4,HOSTEL_B5_B6,False,True,False,1.1,False,True,Boys Hostel North Extension
HOSTEL_B1_B2,HOSTEL_MESS_B,False,True,False,1.5,False,False,Covered Walkway to Boys Mess
HOSTEL_B3_B4,HOSTEL_MESS_B,False,True,False,1.4,False,False,Direct Mess Entry
HOSTEL_B1_B2,AB1_RAMP_ENTRANCE,False,True,False,1.3,False,True,Hostel B1 Pathway to AB1 Ramp
AB1_RAMP_ENTRANCE,AB1_MAIN,False,True,False,1.2,False,False,Accessible West Ramp into AB1
DOME_BUILDING,AB1_MAIN,False,True,True,1.3,False,False,Dome to AB1 Central Covered Corridor
AB1_MAIN,AB1_EAST_STAIRS,True,False,True,1.6,False,False,AB1 Ground to East Lab Stairs
AB1_MAIN,NESCAFE_KIOSK,False,True,False,1.4,False,True,AB1 East Exit to Nescafe Kiosk
AB1_MAIN,AB2_MAIN,False,True,True,1.7,False,False,AB1-AB2 Connected Indoor Galleria
AB1_EAST_STAIRS,LIBRARY_CENTRAL,False,True,False,1.3,False,True,East Exit to Library North Door
NESCAFE_KIOSK,LIBRARY_CENTRAL,False,True,False,1.5,False,True,Nescafe to Central Library Plaza
NESCAFE_KIOSK,AB2_MAIN,False,True,False,1.2,False,True,Nescafe to AB2 Front Porch
AB2_MAIN,AB2_RAMP,False,True,False,1.1,False,False,AB2 East Ramp Walkway
AB2_RAMP,SPORTS_COMPLEX_INDOOR,False,True,False,1.2,False,True,AB2 to Indoor Sports Walkway
AB2_MAIN,BASKETBALL_COURTS,False,True,False,1.1,False,True,AB2 North to Basketball Court
LIBRARY_CENTRAL,LIBRARY_PLAZA,False,True,False,1.4,False,False,Central Library Portico to Plaza
DOME_BUILDING,AUDITORIUM,False,True,False,1.1,False,True,Dome East Walkway to Auditorium
AUDITORIUM,FOOD_COURT,False,True,False,1.3,False,True,Auditorium to Food Court Path
LIBRARY_PLAZA,FOOD_COURT,False,True,False,1.6,False,True,Library Plaza to Food Court Boulevard
FOOD_COURT,MESS_GRAND,False,True,False,1.8,False,False,Food Court to Grand Mess Corridor
FOOD_COURT,TAPRI_CORNER,False,True,False,1.5,False,True,Food Court to Student Tapri Plaza
AUDITORIUM,TAPRI_CORNER,False,True,False,1.2,False,True,Auditorium to Tapri Pathway
LIBRARY_PLAZA,OAT_BOTTOM,False,True,False,1.2,False,True,Library to OAT Ground Level
OAT_BOTTOM,OAT_TOP_STEPS,True,False,False,1.1,False,True,OAT Amphitheatre Tier Stairs
OAT_BOTTOM,MESS_GRAND,False,True,False,1.3,False,True,OAT to Grand Mess Rear Path
OAT_TOP_STEPS,GATE_3,True,False,False,1.0,False,True,OAT Top Steps to Gate 3 Service Road
LIBRARY_PLAZA,SPORTS_COMPLEX_INDOOR,False,True,False,1.2,False,True,Library Plaza to Sports Arena
SPORTS_COMPLEX_INDOOR,SWIMMING_POOL,False,True,False,1.1,False,True,Sports Complex to Aquatic Center
SWIMMING_POOL,CRICKET_GROUND,False,True,False,1.0,False,True,Pool to Cricket Pavilion Path
SPORTS_COMPLEX_INDOOR,BASKETBALL_COURTS,False,True,False,1.2,False,True,Indoor Complex to Basketball Courts
BASKETBALL_COURTS,FOOTBALL_GROUND,False,True,False,1.1,False,True,Courts to Football Field
FOOTBALL_GROUND,HOSTEL_B5_B6,False,True,False,1.1,False,True,Football Ground to Hostel B5-B6 Spine
SWIMMING_POOL,GATE_3,False,True,False,1.0,False,True,Swimming Pool to Gate 3
CRICKET_GROUND,GATE_3,False,True,False,1.0,False,True,Cricket Ground to Gate 3"""
