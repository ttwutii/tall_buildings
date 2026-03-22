import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Thai Structural Design Code (B.E. 2566)", layout="wide")

st.title("🏗️ Load Combinations & Design Guidelines")
st.subheader("Based on Ministerial Regulation B.E. 2566 (2023)")
st.markdown("---")

# --- Create Tabs for Navigation ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Live Loads", 
    "2. LL Reduction & Impact", 
    "3. Wind Load", 
    "4. Load Combinations", 
    "5. Strength Reduction", 
    "6. Fire Resistance"
])

# ==========================================
# TAB 1: Minimum Live Loads (Comprehensive list from Table 11)
# ==========================================
with tab1:
    st.header("Minimum Live Loads Table")
    st.markdown("Reference: Clause 11, Table of minimum live loads for various parts of buildings. [cite: 169, 170]")
    
    # Complete data according to the Ministerial Regulation B.E. 2566
    data = {
        "Building Group / Category": [
            # 1. Assembly
            "1. Assembly", "1. Assembly", "1. Assembly", "1. Assembly", 
            "1. Assembly", "1. Assembly", "1. Assembly",
            "1. Assembly", "1. Assembly", "1. Assembly", "1. Assembly", "1. Assembly",
            # 2. Commercial / Office
            "2. Commercial / Office", "2. Commercial / Office", "2. Commercial / Office", "2. Commercial / Office",
            "2. Commercial / Office", "2. Commercial / Office", "2. Commercial / Office", "2. Commercial / Office", "2. Commercial / Office",
            "2. Commercial / Office", "2. Commercial / Office", "2. Commercial / Office",
            # 3. Educational
            "3. Educational", "3. Educational", "3. Educational", "3. Educational", 
            "3. Educational", "3. Educational", "3. Educational", "3. Educational",
            # 4. Healthcare
            "4. Healthcare", "4. Healthcare", "4. Healthcare", "4. Healthcare", 
            "4. Healthcare", "4. Healthcare",
            # 5. Industrial
            "5. Industrial", "5. Industrial",
            # 6. Residential
            "6. Residential", "6. Residential",
            "6. Residential", "6. Residential", "6. Residential", "6. Residential", "6. Residential",
            # 7. Others
            "7. Others", "7. Others", "7. Others", "7. Others", "7. Others", "7. Others", "7. Others"
        ],
        "Parts of Building": [
            # 1. Assembly [cite: 170-173]
            "Meeting rooms: Fixed seats", 
            "Meeting rooms: Movable seats", 
            "Assembly areas: Halls, stairs, corridors", 
            "Assembly areas: Stages and performance areas", 
            "Libraries: Reading rooms", 
            "Libraries: Reading rooms with bookshelves", 
            "Libraries: Book storage",
            "Stadiums/Museums/Galleries: Areas with fixed seats",
            "Stadiums/Museums/Galleries: Grandstand rows, outdoor seats",
            "Stadiums/Museums/Galleries: Gymnasiums, stadiums, museums",
            "Stadiums/Museums/Galleries: Stages and performance areas",
            "Stadiums/Museums/Galleries: Halls, stairs, corridors",
            # 2. Commercial / Office [cite: 173-174]
            "Offices/Banks: Office areas",
            "Offices/Banks: Halls, stairs, corridors",
            "Offices/Banks: Mainframe computer rooms",
            "Offices/Banks: Document and parcel storage",
            "Markets/Malls: Retail areas",
            "Markets/Malls: Wholesale areas",
            "Markets/Malls: Halls",
            "Markets/Malls: Stairs, corridors",
            "Markets/Malls: Storage areas",
            "Shophouses/Rowhouses: Commercial parts",
            "Shophouses/Rowhouses: Stairs, corridors",
            "Shophouses/Rowhouses: Residential parts",
            # 3. Educational [cite: 175]
            "Schools/Institutions: Classrooms",
            "Schools/Institutions: Lecture halls/rooms",
            "Schools/Institutions: Offices, staff rooms",
            "Schools/Institutions: Laboratories, kitchens, laundries",
            "Schools/Institutions: Halls, stairs, corridors",
            "Schools/Institutions: Computer rooms",
            "Schools/Institutions: Mainframe computer rooms",
            "Schools/Institutions: Document and parcel storage",
            # 4. Healthcare [cite: 175]
            "Hospitals/Clinics: Special patient rooms",
            "Hospitals/Clinics: Offices, staff rooms",
            "Hospitals/Clinics: General wards",
            "Hospitals/Clinics: X-Ray rooms, operating rooms, equipment rooms",
            "Hospitals/Clinics: Laboratories, kitchens, laundries",
            "Hospitals/Clinics: Halls, stairs, corridors",
            # 5. Industrial [cite: 179]
            "Factories/Warehouses: Storage areas, warehouses",
            "Factories/Warehouses: Industrial factory areas",
            # 6. Residential [cite: 179]
            "Houses: General rooms",
            "Houses: Balconies, stairs",
            "Hotels/Condos/Dorms: Bedrooms, living rooms, bathrooms, dressing rooms",
            "Hotels/Condos/Dorms: Offices, office areas",
            "Hotels/Condos/Dorms: Service areas (Restaurants, kitchens, laundries, clubs, etc.)",
            "Hotels/Condos/Dorms: Halls, stairs, corridors",
            "Hotels/Condos/Dorms: Storage areas",
            # 7. Others [cite: 186]
            "Parking: Passenger cars (up to 7 seats) and motorcycles",
            "Parking: Other passenger buses / Empty trucks",
            "Fire escape stairs (Must not be less than the building group's stairs)",
            "Walkways connecting between buildings",
            "Dance floors",
            "Roofs",
            "Concrete canopies / Flat roofs (Decks)"
        ],
        "Live Load (kg/m²)": [
            # 1
            "300", "400", "500", "500", "300", "400", "600",
            "300", "500", "500", "500", "500",
            # 2
            "250", "300", "500", "500", "400", "500", "500", "400", "500", "300", "300", "200",
            # 3
            "250", "300", "250", "300", "400", "250", "500", "500",
            # 4
            "200", "250", "300", "300", "300", "400",
            # 5
            "500", "500",
            # 6
            "200", "200", "200", "250", "400", "400", "500",
            # 7
            "300", "Calculate based on actual load", "400", "500", "500", "50", "100 / 200"
        ]
    }
    df = pd.DataFrame(data)
    
    # Dropdown to filter by building group
    selected_group = st.selectbox("📌 Filter by Building Category:", ["Show All"] + list(df["Building Group / Category"].unique()))
    
    if selected_group != "Show All":
        display_df = df[df["Building Group / Category"] == selected_group].reset_index(drop=True)
    else:
        display_df = df.reset_index(drop=True)
        
    st.table(display_df)
    
    # Additional guidelines from the regulation
  # Additional guidelines exactly as stated in the regulation
    st.info("""
    **Additional Design Guidelines (Based strictly on the Ministerial Regulation):**
    * **Heavier Loads (Clause 12):** In design and calculation, if it appears that any area must support the weight of machinery, equipment, or other live loads that are greater than the live loads specified in Clause 11, the greater live load value shall be used specifically for the part that must support the increased weight. 
    * **Fire Escape Stairs (Table 11, Group 7):** The minimum live load is 400 kg/m²; however, it must not be less than the live load of the stairs in the building group under consideration. 
    * **Walkways Connecting Buildings (Table 11, Group 7):** Walkways connecting between buildings must be designed for a live load of 500 kg/m². 
    """)
# ==========================================
# TAB 2: Live Load Reduction & Impact Loads
# ==========================================
with tab2:
    col2_1, col2_2 = st.columns((0.6, 0.4))
    
    with col2_1:
        st.header("Live Load Reduction (Clause 13, 14)")
        st.markdown("For loads transferred to foundations, columns, or bearing walls.")
        
        is_excepted = st.checkbox("Is this an excepted building? (e.g., Assembly, Parking, Warehouse, Education, Healthcare, or areas with LL > 500 kg/m²)")
        
        if is_excepted:
            st.error("⚠️ **No Live Load Reduction Allowed** (Clause 14).")
        else:
            floor_from_roof = st.number_input("Number of floors down from the roof:", min_value=0, max_value=20, value=0, step=1)
            reduction = 0
            if floor_from_roof <= 2: reduction = 0
            elif floor_from_roof == 3: reduction = 10
            elif floor_from_roof == 4: reduction = 20
            elif floor_from_roof == 5: reduction = 30
            elif floor_from_roof == 6: reduction = 40
            else: reduction = 50
            
            st.success(f"📉 **Allowable Live Load Reduction: {reduction}%**")
            
    with col2_2:
        st.header("Impact Loads (Clause 16)")
        st.markdown("Additional load percentage for vibrations/impacts.")
        
        impact_type = st.radio("Select Structure/Equipment Type:", [
            "Elevators / Hoists",
            "Light machinery (shaft/motor driven)",
            "Reciprocating machinery / Generators",
            "Suspended floors / Balconies"
        ])
        
        if "Elevators" in impact_type: st.info("⬆️ Increase load by **100%**")
        elif "Light machinery" in impact_type: st.info("⚙️ Increase load by **20%**")
        elif "Reciprocating" in impact_type: st.info("🏭 Increase load by **50%**")
        elif "Suspended" in impact_type: st.info("🏗️ Increase load by **33%**")

# ==========================================
# TAB 3: Wind Load Calculator
# ==========================================
with tab3:
    st.header(" Wind Load (Clause 17)")
    st.markdown("For primary structures (Height ≤ 40m, Height ≤ 3x minimum width).")
    
    col3_1, col3_2, col3_3 = st.columns(3)
    with col3_1:
        bldg_height = st.number_input("Building Height (m):", min_value=0.0, max_value=40.0, value=15.0, step=1.0)
    with col3_2:
        terrain = st.radio("Terrain Type:", ["City / Suburbs", "Open / Coastal"])
    with col3_3:
        is_large_public = st.checkbox("Public Building ≥ 1,000 sq.m (+15% Load)")

    wind_pressure = 0
    if terrain == "City / Suburbs":
        if bldg_height <= 10: wind_pressure = 60
        elif bldg_height <= 20: wind_pressure = 80
        else: wind_pressure = 120
    else: # Open / Coastal
        if bldg_height <= 10: wind_pressure = 100
        elif bldg_height <= 20: wind_pressure = 120
        else: wind_pressure = 160

    if is_large_public:
        wind_pressure *= 1.15

    st.success(f"🌪️ **Design Wind Pressure = {wind_pressure:.2f} kg/m²**")

# ==========================================
# TAB 4: Load Combinations
# ==========================================
with tab4:
    st.header(" Load Combinations (Clause 6, 7)")

    col4_res1, col4_res2 = st.columns(2)
    
    with col4_res1:
        st.subheader("WSD (Working Stress Design)")
        st.markdown("Based on Clause 6 of the regulation:")
        
        st.write(r"U = DL + LL" )
        st.write(r"U = DL + 0.75(LL + WL) " )
        st.write(r"U = 0.6DL + WL " )
        st.write(r"U = DL + 0.7EQ " )
        st.write(r"U = DL + 0.525EQ + 0.75LL " )
        st.write(r"U = 0.6DL + 0.7EQ " )
        
        
    with col4_res2:
        st.subheader("SDM (Strength Design Method)")
        st.markdown("Based on Clause 7 of the regulation:")
        
        st.write(r"U = 1.4DL + 1.7LL ")
        st.write(r"U = 0.75(1.4DL + 1.7LL) + 1.6WL ")
        st.write(r"U = 0.9DL + 1.6WL " )
        st.write(r"U = 0.75(1.4DL + 1.7LL) + 1.0EQ ")
        st.write(r"U = 0.9DL + 1.0EQ ")
        
    st.divider()

    st.subheader("Aprximate Load Combination Calculator")
    
    col4_1, col4_2, col4_3, col4_4 = st.columns(4)
    with col4_1: DL = st.number_input("Dead Load (DL)", value=100.0)
    with col4_2: LL = st.number_input("Live Load (LL)", value=200.0)
    with col4_3: WL = st.number_input("Wind Load (WL)", value=50.0)
    with col4_4: EQ = st.number_input("Earthquake (EQ)", value=0.0)

    # Calculate WSD Load Combinations
    wsd_1 = DL + LL
    wsd_2 = DL + 0.75 * (LL + WL)
    wsd_3 = 0.6 * DL + WL
    wsd_4 = DL + 0.7 * EQ
    wsd_5 = DL + 0.525 * EQ + 0.75 * LL
    wsd_6 = 0.6 * DL + 0.7 * EQ
    max_wsd = max(wsd_1, wsd_2, wsd_3, wsd_4, wsd_5, wsd_6)
    
    # Calculate SDM Load Combinations
    sdm_1 = 1.4 * DL + 1.7 * LL
    sdm_2 = 0.75 * (1.4 * DL + 1.7 * LL) + 1.6 * WL
    sdm_3 = 0.9 * DL + 1.6 * WL
    sdm_4 = 0.75 * (1.4 * DL + 1.7 * LL) + 1.0 * EQ
    sdm_5 = 0.9 * DL + 1.0 * EQ
    max_sdm = max(sdm_1, sdm_2, sdm_3, sdm_4, sdm_5)

    #st.divider()

    col4_res1, col4_res2 = st.columns(2)
    
    with col4_res1:
        st.subheader("WSD ")
        #st.markdown("Based on Clause 6 of the regulation:")
        
        st.write(r"U = DL + LL = " + f"{wsd_1:.2f}")
        st.write(r"U = DL + 0.75(LL + WL) = " + f"{wsd_2:.2f}")
        st.write(r"U = 0.6DL + WL = " + f"{wsd_3:.2f}")
        st.write(r"U = DL + 0.7EQ = " + f"{wsd_4:.2f}")
        st.write(r"U = DL + 0.525EQ + 0.75LL = " + f"{wsd_5:.2f}")
        st.write(r"U = 0.6DL + 0.7EQ = " + f"{wsd_6:.2f}")
        
        st.info(f"**Max Design Load (WSD) = {max_wsd:.2f}**")
        
    with col4_res2:
        st.subheader("SDM ")
        #st.markdown("Based on Clause 7 of the regulation:")
        
        st.write(r"U = 1.4DL + 1.7LL = " + f"{sdm_1:.2f}")
        st.write(r"U = 0.75(1.4DL + 1.7LL) + 1.6WL = " + f"{sdm_2:.2f}")
        st.write(r"U = 0.9DL + 1.6WL = " + f"{sdm_3:.2f}")
        st.write(r"U = 0.75(1.4DL + 1.7LL) + 1.0EQ = " + f"{sdm_4:.2f}")
        st.write(r"U = 0.9DL + 1.0EQ = " + f"{sdm_5:.2f}")
        
        st.error(f"**Max Design Load (SDM) = {max_sdm:.2f}**")
# ==========================================
# TAB 5: Strength Reduction Factors
# ==========================================
with tab5:
    st.header("Strength Reduction Factors (Clause 8)")
    
    mat_type = st.radio("Select Material:", ["Reinforced Concrete (RC)", "Structural Steel"])
    
    if mat_type == "Reinforced Concrete (RC)":
        st.markdown("**RC Strength Reduction Factors (Φ)**")
        rc_data = {
            "Type of Stress": ["Flexure (No axial)", "Axial Tension", "Axial Compression (Spiral tied)", "Axial Compression (Other tied)", "Shear & Torsion", "Bearing on Concrete"],
            "With Strict QA": [0.90, 0.90, 0.75, 0.70, 0.85, 0.70],
            "Without Strict QA": [0.75, 0.75, 0.625, 0.60, 0.70, 0.60]
        }
        st.table(pd.DataFrame(rc_data))
    else:
        st.markdown("**Steel Strength Reduction Factors (Φ)**")
        steel_data = {
            "Type of Stress / Member": ["Tension (Yielding)", "Tension (Fracture)", "Compression", "Flexure", "Shear", "Bolts/Joints (Tension/Shear)"],
            "Factor (Φ)": [0.90, 0.75, 0.90, 0.90, 0.90, 0.75]
        }
        st.table(pd.DataFrame(steel_data))

# ==========================================
# TAB 6: Fire Resistance Ratings
# ==========================================
with tab6:
    st.header(" Fire Resistance Ratings (Clause 23)")
    st.markdown("Required fire resistance for primary structural elements.")
    
    floor_level = st.radio("Select Floor Level:", [
        "1st to 4th floor from the top",
        "5th to 14th floor from the top",
        "15th floor and below (including basements)",
        "Roof Structure"
    ])
    
    is_special = st.checkbox("Is this a High-rise, Theater, Hospital, or Storage for flammable materials?")
    
    if floor_level == "1st to 4th floor from the top":
        rating = 2 if is_special else 1
        st.success(f"🔥 Columns, bearing walls, beams, joists, floors require **{rating} Hour(s)** of fire resistance.")
    elif floor_level == "5th to 14th floor from the top":
        st.success("🔥 Columns, bearing walls, beams, joists, floors require **2 Hours** of fire resistance.")
    elif floor_level == "15th floor and below (including basements)":
        st.success("🔥 Columns, bearing walls, beams require **3 Hours**. Joists and floors require **2 Hours**.")
    else:
        st.success("🔥 Roof structures generally require **1 Hour**. (Exemptions apply for small buildings < 1,000 sq.m or roofs > 8.00m high with sprinklers/heat protection).")
