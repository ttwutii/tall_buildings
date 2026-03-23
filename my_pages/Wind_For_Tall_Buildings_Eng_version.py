import streamlit as st
import pandas as pd 
import numpy as np
import math
import scipy.integrate as integrate
import altair as alt

st.title('DPT Standard 1311-50: Wind Load for Tall Buildings')
st.caption('### Calculation of Equivalent Static Wind Loads using the Detailed Procedure')

st.divider()
st.subheader("Criteria for Detailed Procedure")
st.write("The detailed procedure shall be used if the structure meets any of the following:")

st.markdown("- **a) Building height** $H > 80$ m or $H > 3W$ (where $W$ is the width of the building).")
st.markdown("- **b) Flexible structures** with low natural frequency and low damping properties.")

st.write("---")
# ==========================================
# 1. Building Dimensions & Story Data
# ==========================================
inputs = st.container()
with inputs:
    st.write('### 1. Building Dimensions & Story Data')
    col1, col2 = st.columns([0.3, 0.7]) 
    
    with col1:
        Floor = st.number_input(label='Number of Stories', min_value=1, max_value=100, value=10, step=1)
        Wx = st.number_input(label='Width parallel to X-axis [m]', min_value=0.0, value=20.0, step=0.1)
        Wy = st.number_input(label='Width parallel to Y-axis [m]', min_value=0.0, value=20.0, step=0.1)
        Ds = min(Wy, Wx)
        st.write(f'Narrowest effective width, $D_s = {Ds:.2f}$ m')
        
    with col2:
        st.write("#### Define Story Data")
        st.caption("You can edit the numbers directly in the table or copy/paste from Excel.")
        
        # Initialize default dataframe
        init_data = pd.DataFrame({
            "Story": [i+1 for i in range(int(Floor))],
            "Height (m)": [4.0] * int(Floor),
            "Weight (tonne)": [125.0] * int(Floor) 
        })
        
        # Display data editor
        edited_df = st.data_editor(init_data, use_container_width=True, hide_index=True)
        
        # --- Data Processing ---
        heights = edited_df["Height (m)"].tolist()
        Floor_list = []
        current_h = 0
        for h in heights:
            current_h += h
            Floor_list.append(current_h)
            
        H = current_h
        
        # Calculate Average Building Density (rho_B) [cite: 220]
        total_weight_tonne = edited_df["Weight (tonne)"].sum()
        total_mass_kg = total_weight_tonne * 1000
        volume = Wx * Wy * H
        
        if volume > 0:
            rho_B = total_mass_kg / volume
        else:
            rho_B = 0
        
        # Display Summary
        col2_1, col2_2, col2_3 = st.columns(3)
        col2_2.info(f"Total Height, $H = {H:.2f}$ m")
        col2_3.info(f"Total Weight = {total_weight_tonne:,.2f} tonnes")
        col2_3.info(f"Building Density, $\\rho_B = {rho_B:,.2f}$ kg/m³")



# # ==========================================
# # 1. Building Dimensions (มิติอาคาร)
# # ==========================================

# inputs = st.container()
# with inputs:
#     st.write('### 1. Building Dimensions')
#     col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
#     with col2:
#         Floor = st.number_input(label='Number of Stories', min_value=1, max_value=100, value=10, step=1)
    
#     with col3:
#         Floor_list = []
#         H = 0
#         with st.expander("Define Story Heights (Default = 3m each)"):
#             for i in range(Floor):
#                 # แปลป้ายกำกับความสูงแต่ละชั้น
#                 Heigth = st.number_input(label=f'Story Height {i+1} [m]', min_value=0.0, value=3.0, step=0.1, key=f"floor{i}")
#                 H += Heigth
#                 Floor_list.append(H)
#         st.info(f"Total Height (H) = {H:.2f} m")

#     with col1:
#         Wx = st.number_input(label='Width parallel to X-axis [m]', min_value=0.0, value=20.0, step=0.1)
#         Wy = st.number_input(label='Width parallel to Y-axis [m]', min_value=0.0, value=20.0, step=0.1)
#         Ds = min(Wy, Wx)
#         st.write(f'Minimum Building Width, $D_s={Ds:.2f}$ m')

st.write("---")

# ==========================================
# 2. Importance and Wind Speed (ความสำคัญและความเร็วลม)
# ==========================================

# แปลหัวข้อใน DataFrame
df_important = pd.DataFrame({
    'Building Importance Category': ['Low', 'Normal', 'High', 'Essential'],
    'Ultimate Limit State': [0.8, 1.0, 1.1, 1.15],
    'Serviceability Limit State': [0.75, 0.75, 0.75, 0.75],
})

df_wind_speed = pd.DataFrame({
    'Zone Group': ['1', '2', '3', '4A', '4B'],
    'V50 [m/s]': [25, 27, 29, 25, 25],
    'T_F': [1.0, 1.0, 1.0, 1.2, 1.08],
})

col1, col2 = st.columns(2)
with col1:
    st.write('### 2. Importance Factor, $I_w$')
    important_type = st.selectbox(label='Importance Category', options=df_important['Building Importance Category'])
    cal_type = st.selectbox(label='Design Limit State', options=['Ultimate Limit State', 'Serviceability Limit State'])
    I_w = df_important.loc[df_important['Building Importance Category'] == important_type, cal_type].values[0]
    st.markdown(f'$I_w={I_w:.2f}$')

with col2:
    st.write('### 3. Reference Wind Speed, $\overline{V}$')
    area_group = st.selectbox(label='Area Zone Group', options=df_wind_speed['Zone Group'])
    V50 = df_wind_speed.loc[df_wind_speed['Zone Group'] == area_group, 'V50 [m/s]'].values[0]
    T_F = df_wind_speed.loc[df_wind_speed['Zone Group'] == area_group, 'T_F'].values[0]
    
    if cal_type == 'Ultimate Limit State':
        V_bar = V50 * T_F
        V_bar_mph = V_bar * 2.23694
    else:
        V_bar = V50
        V_bar_mph = V_bar * 2.23694
    st.markdown(f'$\overline{{V}}={V_bar:.2f}$ m/s')
    st.markdown(f'$\overline{{V}}={V_bar_mph:.2f}$ mph (for reference)')


st.write("---")

# ==========================================
# 3. Reference Velocity Pressure (q)
# ==========================================

rho = 1.25
g = 9.81
q = 0.5 * rho * (V_bar**2)
st.write('### 4. Reference Velocity Pressure, $q$')
st.markdown(f'$q=0.5\\rho\\overline{{V}}^2=0.5(1.25)({V_bar})^2={q:.2f}$ N/m²')

st.write("---")

# ==========================================
# 4. Exposure Factor (Ce)
# ==========================================
st.markdown('### 5. Exposure Factor, $C_e$ (Detailed Procedure)')
terrain_type = st.selectbox(label='Terrain Category', options=['A', 'B', 'C'], index=1)

def calculate_Ce(z, t_type):
    if t_type == 'A':
        return max(1.0, min((z/10)**0.28, 2.5))
    elif t_type == 'B':
        return max(0.5, min(0.5*(z/12.7)**0.5, 2.5))
    elif t_type == 'C':
        return max(0.4, min(0.4*(z/30)**0.72, 2.5))

Ce_list = [calculate_Ce(z, terrain_type) for z in Floor_list]
Ce_H = calculate_Ce(H, terrain_type)

Ce_table = pd.DataFrame({
    'Story': range(1, Floor+1),
    'Height above ground (z)': Floor_list,
    'Ce': [round(ce, 3) for ce in Ce_list]
})
with st.expander("View Ce Values per Story Table"):
    st.dataframe(Ce_table, hide_index=True, use_container_width=True)

st.write("---")

# ==========================================
# 5. Building Dynamics and Gust Response Factor (Cg)
# ==========================================
st.write('### 6. Gust Response Factor, $C_g$ (Windward direction)')
st.markdown("In the detailed procedure, $C_g$ depends on the natural frequency and the wind direction relative to the building face.")

col1, col2 = st.columns(2)
with col1:
    n_D = st.number_input("Natural Frequency $n_D$ (Hz)", value=44.0/H if H>0 else 1.0, step=0.1)
with col2:
    damping_ratio = st.number_input("Damping Ratio $\\beta_D$", value=0.015, step=0.005, format="%.3f")

def calculate_Cg_detailed(H, W_eff, V_bar, n_D, damping, t_type, Ce_H):
    V_H = V_bar * math.sqrt(Ce_H)
    K_dict = {'A': 0.08, 'B': 0.10, 'C': 0.14}
    K = K_dict[t_type]
    
    # Calculate B (Background turbulence factor)
    def integrand_B(x):
        term1 = 1 / (1 + (x * H / 457))
        term2 = 1 / (1 + (x * W_eff / 122))
        term3 = x / ((1 + x**2) ** (4/3))
        return term1 * term2 * term3
    upper_limit = 914 / H if H > 0 else 0
    B_val, _ = integrate.quad(integrand_B, 0, upper_limit)
    B = (4/3) * B_val
    
    # Calculate s, F, v, g_p
    s = (math.pi/3) * (1 / (1 + (8*n_D*H)/(3*V_H))) * (1 / (1 + (10*n_D*W_eff)/V_H))
    X_0 = (1220 * n_D) / V_H
    F = (X_0**2) / ((1 + X_0**2)**(4/3))
    
    v = n_D * math.sqrt((s * F) / (s * F + damping * B))
    g_p = math.sqrt(2 * math.log(v * 3600)) + 0.577 / math.sqrt(2 * math.log(v * 3600))
    
    sigma_mu = math.sqrt((K / Ce_H) * (B + (s * F / damping)))
    C_g = 1 + g_p * sigma_mu
    
    return C_g, K, s, F, g_p

# Cg for Wind on X-axis (Face width = Wy)
Cg_x, K_x, s_x, F_x, gp_x = calculate_Cg_detailed(H, Wy, V_bar, n_D, damping_ratio, terrain_type, Ce_H)
# Cg for Wind on Y-axis (Face width = Wx)
Cg_y, K_y, s_y, F_y, gp_y = calculate_Cg_detailed(H, Wx, V_bar, n_D, damping_ratio, terrain_type, Ce_H)

col1, col2 = st.columns(2)
col1.info(f"**Wind on X-axis** (W = {Wy}m)\n\n$C_{{gx}}={Cg_x:.3f}$")
col2.info(f"**Wind on Y-axis** (W = {Wx}m)\n\n$C_{{gy}}={Cg_y:.3f}$")

c_gi = 2.0 

st.write("---")
# ==========================================
# 6. Wind Pressure Coefficients Cp and Cpi (Ref: Figure B.9)
# ==========================================
st.write("---")
st.write('### 7. External ($C_p$) and Internal ($C_{pi}$) Wind Pressure Coefficients')

# Applicability Check based on Figure B.9 
col_chk1, col_chk2 = st.columns(2)
with col_chk1:
    st.markdown(f"**Height Check:** $H = {H:.2f}$ m")
    if H > 23:
        st.success(f"✅ $H > 23$ m (Passes criteria) ")
    else:
        st.error(f"❌ $H \le 23$ m (Not applicable for Figure B.9) ")
with col_chk2:
    HDs = H / Ds if Ds > 0 else 0
    st.markdown(f"**Slenderness Check:** $H/D_s = {HDs:.2f}$")
    if HDs >= 1:
        st.success(f"✅ $H/D_s \ge 1$ (Passes criteria) ")
    else:
        st.error(f"❌ $H/D_s < 1$ (Not applicable for Figure B.9) ")

# Function to calculate Cp based on Figure B.9 
def get_Cp_windward(HD_ratio):
    if HD_ratio <= 0.25: return 0.60
    elif HD_ratio < 1: return 0.27 * (HD_ratio + 2)
    else: return 0.80

def get_Cp_leeward(HD_ratio):
    if HD_ratio <= 0.25: return -0.30
    elif HD_ratio < 1: return -0.27 * (HD_ratio + 0.88)
    else: return -0.50

# Calculate Cp for each axis
C_px_wind = get_Cp_windward(H/Wx)
C_px_lee = get_Cp_leeward(H/Wx)
C_py_wind = get_Cp_windward(H/Wy)
C_py_lee = get_Cp_leeward(H/Wy)

# Display Cp and Local Cp*
st.markdown("**Average Pressure Coefficients ($C_p$) and Local Pressure Coefficients ($C_p^*$)**")
col_cp1, col_cp2, col_cp3 = st.columns(3)
col_cp1.info(f"**Wind parallel to X-axis ($D = {Wx}$)**\n- Windward ($C_p$): {C_px_wind:.2f}\n- Leeward ($C_p$): {C_px_lee:.2f}")
col_cp2.info(f"**Wind parallel to Y-axis ($D = {Wy}$)**\n- Windward ($C_p$): {C_py_wind:.2f}\n- Leeward ($C_p$): {C_py_lee:.2f}")
col_cp3.warning("**Side Walls and Roof**\n- Side Walls ($C_p$): -0.70 \n- Roof ($C_p$): -1.0 to -0.5 \n- Wall edges ($C_p^*$): -1.20 ")

# Internal Pressure Cpi
df_c_pi = pd.DataFrame({
    'Condition': ['Without large openings', 'With unevenly distributed leakage', 'With large openings'],
    'C_pi-': [-0.15, -0.45, -0.7],
    'C_pi+': [0, 0.3, 0.7]
})
c_pi_choice = st.selectbox(label='Internal Pressure Condition ($C_{pi}$)', options=df_c_pi['Condition'])
C_pi_minus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi-'].values[0]
C_pi_plus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi+'].values[0]

st.write("---")

# ==========================================
# 7. Net Wind Pressure (Updated Reference Heights for Ce based on Note 5)
# ==========================================
st.markdown('### 8. Net Wind Pressure ($P_{net}$)')
st.markdown('$P_{net}=I_w q C_e C_g C_p - I_w q C_e C_{gi} C_{pi}$')

# Calculate Reference Ce according to the specifications 
Ce_05H = calculate_Ce(0.5 * H, terrain_type) # For Leeward and Internal 
Ce_H = calculate_Ce(H, terrain_type)         # For Side walls, Roof, and Local Cg 

with st.expander("📌 View Reference Height Rules for $C_e$ "):
    st.markdown(f"""
    - **Windward walls:** Use height at each level ($z$) -> $C_e$ varies with height 
    - **Leeward walls:** Use $0.5H = {0.5*H:.2f}$ m -> $C_e = {Ce_05H:.3f}$ 
    - **Side walls and Roof:** Use $H = {H:.2f}$ m -> $C_e = {Ce_H:.3f}$ 
    - **Internal pressure:** Use $0.5H = {0.5*H:.2f}$ m -> $C_e = {Ce_05H:.3f}$ 
    """)

tab1, tab2 = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])

def plot_pressure(df, title):
    chart = alt.Chart(df).mark_bar(size=Floor*3, color='steelblue', opacity=0.8).encode(
        x=alt.X('Combine wind pressure (N/m²)', title='Combine Wind Pressure'),
        y=alt.Y('Height from ground (z)', title='Height (m)', sort='-y'),
        tooltip=['Height from ground (z)', 'Windward (N/m²)', 'Leeward (N/m²)', 'Combine wind pressure (N/m²)']
    ).configure_mark(orient='horizontal').properties(height=400, title=title)
    st.altair_chart(chart, use_container_width=True)

# def plot_force(df, title):
#     # เปลี่ยนกราฟให้แสดงค่าแรงกระทำ (kN) แทน Pressure จะเห็นภาพรวมของแรงเฉือนได้ดีกว่า
#     chart = alt.Chart(df).mark_bar(size=Floor*3, color='#E65100', opacity=0.8).encode(
#         x=alt.X('Force acting on the layer (kN)', title='Total Force (kN)'),
#         y=alt.Y('Floor', title='Number of Floors', sort='-y'),
#         tooltip=['Floor', 'Height from ground (z)', 'Wind-receiving area (m²)', 'Force acting on the layer (kN)']
#     ).configure_mark(orient='horizontal').properties(height=400, title=title)
#     st.altair_chart(chart, use_container_width=True)
def plot_force(df, title):
    # 1. สร้างส่วนของ "เส้นลูกศร" (วาดจากค่า Force ไปที่ x=0)
    lines = alt.Chart(df).mark_rule(
        color='#E65100', 
        strokeWidth=2 # ปรับความหนาของเส้นได้ที่นี่
    ).encode(
        x=alt.X('Force acting on the layer (kN)', title='Total Force (kN)'),
        x2=alt.value(0), # กำหนดให้ปลายเส้นอีกด้านอยู่ที่แกน Y (x=0)
        y=alt.Y('Floor', title='Number of Floors', sort='-y'),
        tooltip=['Floor', 'Height from ground (z)', 'Wind-receiving area (m²)', 'Force acting on the layer (kN)']
    )

    # 2. สร้างส่วนของ "หัวลูกศร" (ชี้เข้าหาแกน Y)
    heads = alt.Chart(df).mark_point(
        shape='triangle-left', # ใช้รูปสามเหลี่ยมชี้ไปทางซ้าย
        color='#E65100',
        filled=True,
        size=100, # ปรับขนาดของหัวลูกศรได้ที่นี่
        opacity=1
    ).encode(
        x=alt.value(0), # วางหัวลูกศรไว้ที่ฝั่งแกน Y (x=0)
        y=alt.Y('Floor', sort='-y'),
        tooltip=['Floor', 'Height from ground (z)', 'Wind-receiving area (m²)', 'Force acting on the layer (kN)']
    )

    # 3. นำกราฟเส้นและหัวลูกศรมาซ้อนกันด้วยเครื่องหมาย +
    chart = (lines + heads).properties(
        height=400, 
        title=title
    )
    
    st.altair_chart(chart, use_container_width=True)
with tab1:
    st.markdown(f'**Wind parallel to X-axis (Using $C_{{gx}}={Cg_x:.2f}$)**')
    # Using C_pi_minus as an example for designing the critical case
    df_px = pd.DataFrame()
    df_px['Floor'] = range(1, Floor+1)
    df_px['Height from ground (z)'] = Floor_list
    df_px['Story heights'] = heights
    df_px['Ce(z)'] = Ce_list
    
    # Calculate Net Pressure
    # Windward: Iw * q * Ce(z) * (Cg * Cp) - Iw * q * Ce(0.5H) * (Cgi * Cpi)
    df_px['Windward (N/m²)'] = I_w * q * df_px['Ce(z)'] * (Cg_x * C_px_wind) - (I_w * q * Ce_05H * c_gi * C_pi_minus)
    
    # Leeward: Iw * q * Ce(0.5H) * (Cg * Cp) - Iw * q * Ce(0.5H) * (Cgi * Cpi)
    df_px['Leeward (N/m²)'] = I_w * q * Ce_05H * (Cg_x * C_px_lee) - (I_w * q * Ce_05H * c_gi * C_pi_minus)
    
    # Combined Pressure
    df_px['Combine wind pressure (N/m²)'] = abs(df_px['Windward (N/m²)']) + abs(df_px['Leeward (N/m²)'])

    # Calculate Load for each floors
    df_px['Wind-receiving area (m²)'] = df_px['Story heights']*Wy
    df_px['Force acting on the layer (kN)'] = df_px['Combine wind pressure (N/m²)'] * df_px['Wind-receiving area (m²)'] / 1000
    
    st.dataframe(df_px.round(2), hide_index=True, use_container_width=True)
    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:
        plot_pressure(df_px, 'Net Pressure X-axis')
        plot_force(df_px, 'Wind Force X-axis')
        

with tab2:
    st.markdown(f'**Wind parallel to Y-axis (Using $C_{{gy}}={Cg_y:.2f}$)**')
    df_py = pd.DataFrame()
    df_py['Floor'] = range(1, Floor+1)
    df_py['Height from ground (z)'] = Floor_list
    df_py['Story heights'] = heights
    df_py['Ce(z)'] = Ce_list
    
    df_py['Windward (N/m²)'] = I_w * q * df_py['Ce(z)'] * (Cg_y * C_py_wind) - (I_w * q * Ce_05H * c_gi * C_pi_minus)
    df_py['Leeward (N/m²)'] = I_w * q * Ce_05H * (Cg_y * C_py_lee) - (I_w * q * Ce_05H * c_gi * C_pi_minus)
    df_py['Combine wind pressure (N/m²)'] = abs(df_py['Windward (N/m²)']) + abs(df_py['Leeward (N/m²)'])

    df_py['Wind-receiving area (m²)'] = df_py['Story heights']*Wx
    df_py['Force acting on the layer (kN)'] = df_py['Combine wind pressure (N/m²)'] * df_py['Wind-receiving area (m²)'] / 1000
    
    st.dataframe(df_py.round(2), hide_index=True, use_container_width=True)
    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:
        plot_pressure(df_py, 'Net Pressure Y-axis')
        plot_force(df_py, 'Wind Force Y-axis')

# # ==========================================
# # 6. Pressure Coefficients Cp and Cpi
# # ==========================================
# st.write('### 7. Pressure Coefficients, $C_p$ and $C_{pi}$')

# def get_Cp_leeward(HD_ratio):
#     if HD_ratio <= 0.25: return -0.30
#     elif HD_ratio < 1: return -0.27*(HD_ratio + 0.88)
#     else: return -0.50

# def get_Cp_windward(HD_ratio):
#     if HD_ratio <= 0.25: return 0.60
#     elif HD_ratio < 1: return 0.27*(HD_ratio + 2)
#     else: return 0.80

# C_px_wind = get_Cp_windward(H/Wx)
# C_px_lee = get_Cp_leeward(H/Wx)
# C_py_wind = get_Cp_windward(H/Wy)
# C_py_lee = get_Cp_leeward(H/Wy)

# df_c_pi = pd.DataFrame({
#     'Condition': ['No large openings', 'Unevenly distributed leakage', 'Large openings'],
#     'C_pi-': [-0.15, -0.45, -0.7],
#     'C_pi+': [0, 0.3, 0.7]
# })
# c_pi_choice = st.selectbox(label='Internal Pressure Case ($C_{pi}$)', options=df_c_pi['Condition'])
# C_pi_minus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi-'].values[0]
# C_pi_plus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi+'].values[0]

# st.write("---")

# # ==========================================
# # 7. Net Wind Pressure
# # ==========================================
# st.markdown('### 8. Net Wind Pressure ($P_{net}$)')
# st.markdown('$P_{net}=I_w q C_e C_g C_p - I_w q C_e C_{gi} C_{pi}$')

# tab1, tab2 = st.tabs(["Wind on X-axis", "Wind on Y-axis"])

# def plot_pressure(df, title):
#     chart = alt.Chart(df).mark_bar(size=Floor*3, color='steelblue', opacity=0.8).encode(
#         x=alt.X('Combine wind pressure (N/m²)', title='Combined Wind Pressure (N/m²)'),
#         y=alt.Y('Height above ground (z)', title='Height (m)', sort='-y'),
#         tooltip=['Height above ground (z)', 'Combine wind pressure (N/m²)']
#     ).configure_mark(orient='horizontal').properties(height=400, title=title)
#     st.altair_chart(chart, use_container_width=True)

# with tab1:
#     st.markdown(f'**Wind Direction: X-axis (using $C_{{gx}}={Cg_x:.2f}$)**')
#     df_px = pd.DataFrame()
#     df_px['Story'] = range(1, Floor+1)
#     df_px['Height above ground (z)'] = Floor_list
#     df_px['Ce'] = Ce_list
#     df_px['Windward'] = I_w * q * df_px['Ce'] * (Cg_x * C_px_wind) - (I_w * q * df_px['Ce'] * c_gi * C_pi_minus)
#     df_px['Leeward'] = I_w * q * Ce_H * (Cg_x * C_px_lee) - (I_w * q * Ce_H * c_gi * C_pi_minus)
#     df_px['Combine wind pressure (N/m²)'] = abs(df_px['Windward']) + abs(df_px['Leeward'])
    
#     st.dataframe(df_px.round(2), hide_index=True, use_container_width=True)
#     col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
#     with col2:
#         plot_pressure(df_px, 'Net Pressure X-axis')

# with tab2:
#     st.markdown(f'**Wind Direction: Y-axis (using $C_{{gy}}={Cg_y:.2f}$)**')
#     df_py = pd.DataFrame()
#     df_py['Story'] = range(1, Floor+1)
#     df_py['Height above ground (z)'] = Floor_list
#     df_py['Ce'] = Ce_list
#     df_py['Windward'] = I_w * q * df_py['Ce'] * (Cg_y * C_py_wind) - (I_w * q * df_py['Ce'] * c_gi * C_pi_minus)
#     df_py['Leeward'] = I_w * q * Ce_H * (Cg_y * C_py_lee) - (I_w * q * Ce_H * c_gi * C_pi_minus)
#     df_py['Combine wind pressure (N/m²)'] = abs(df_py['Windward']) + abs(df_py['Leeward'])
    
#     st.dataframe(df_py.round(2), hide_index=True, use_container_width=True)
#     col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
#     with col2:
#         plot_pressure(df_py, 'Net Pressure Y-axis')

st.write("---")

# ==========================================
# 8. Serviceability Check (Deflection & Acceleration)
# ==========================================
st.write('### 9. Lateral Deflection and Building Motion (Serviceability Check)')

# Display the automatically calculated rho_B
st.write(f"💡 **Average building density ($\\rho_B$)** used for this calculation is **{rho_B:.2f} kg/m³** "
        f"(Automatically calculated from the total mass divided by the volume $W \\times D \\times H$ according to DPT 1311-50).")

# Calculate deflection and acceleration (checking X-axis as an example)
alpha = 0.5 if terrain_type == 'B' else (0.28 if terrain_type == 'A' else 0.72) # Power law exponent for Ce
Delta_x = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * (C_px_wind - C_px_lee)) / (4 * math.pi**2 * n_D**2 * Wx * rho_B * H**2)

# Check to prevent Division by Zero errors if rho_B or other parameters are 0
if rho_B > 0 and damping_ratio > 0 and Ce_H > 0:
    a_Dx = 4 * math.pi**2 * n_D**2 * gp_x * math.sqrt((K_x * s_x * F_x) / (Ce_H * damping_ratio)) * (Delta_x / Cg_x)
else:
    a_Dx = 0

st.markdown(f'''
- **Maximum lateral deflection at the top, X-axis ($\\Delta_x$)**: `{Delta_x:.4f}` m (Allowable limit = $H/500$ = {H/500:.4f} m) 
  - {"✅ **Pass**" if Delta_x <= H/500 else "❌ **Fail**"}
- **Maximum peak acceleration, X-axis ($a_D$)**: `{a_Dx:.4f}` m/s² 
  - *(Allowable limit = 0.15 m/s² for residential buildings, 0.25 m/s² for commercial buildings)* 
''')

st.write("---")

# (You can append the st.expander details containing the LaTeX equations here as previously provided)

# # ==========================================
# # 8. Serviceability Check (Deflection & Acceleration)
# # ==========================================
# st.write('### 9. Lateral Deflection and Building Motion (Serviceability Check)')

# col1, col2 = st.columns([1, 3])
# with col1:
#     rho_B = st.number_input("Average density of the building, $\\rho_B$ (kg/m³)", value=200.0, step=10.0)
# with col2:
#     st.info("💡 **Reference: DPT Standard 1311-50 (Section 3.7):**\n\n"
#             "**$\\rho_B$ (Average density of the building)** is the total mass of the building divided by the enclosed volume ($Volume = W \\times D \\times H$). "
#             "Generally, it ranges between **150 - 300 kg/m³**.")

# # Calculate deflection and acceleration (checking X-axis as an example)
# alpha = 0.5 if terrain_type == 'B' else (0.28 if terrain_type == 'A' else 0.72) # Power law exponent for Ce
# Delta_x = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * (C_px_wind - C_px_lee)) / (4 * math.pi**2 * n_D**2 * Wx * rho_B * H**2)
# a_Dx = 4 * math.pi**2 * n_D**2 * gp_x * math.sqrt((K_x * s_x * F_x) / (Ce_H * damping_ratio)) * (Delta_x / Cg_x)

# st.markdown(f'''
# - **Maximum lateral deflection at the top, X-axis ($\\Delta_x$)**: `{Delta_x:.4f}` m (Allowable limit = $H/500$ = {H/500:.4f} m) 
#   - {"✅ **Pass**" if Delta_x <= H/500 else "❌ **Fail**"}
# - **Maximum peak acceleration, X-axis ($a_D$)**: `{a_Dx:.4f}` m/s² 
#   - *(Allowable limit = 0.15 m/s² for residential buildings, 0.25 m/s² for commercial buildings)* 
# ''')

# st.write("---")

# ---------------------------------------------------------
# Equation Details Expanders
# ---------------------------------------------------------
st.markdown("####  Equation Details from DPT Standard 1311-50")

with st.expander(" View Lateral Deflection Equation Details"):
    st.markdown("""
    **The maximum lateral deflection at the top of the building ($\\Delta$)** under equivalent static wind load can be estimated using Equation (3-12):
    """)
    st.latex(r"\Delta = \frac{3 \left( \frac{H^2}{2+\alpha} \right) I_w q C_{eH} C_p}{4 \pi^2 n_D^2 D \rho_B H^2}")
    st.markdown("""
    **Where:**
    * $I_w$ = Importance factor for wind load in serviceability limit state (use 0.75) 
    * $q$ = Reference velocity pressure ($q_H$)
    * $C_{eH}$ = Exposure factor at the building height 
    * $C_p$ = External pressure coefficient for windward and leeward walls combined (e.g., $0.8 - (-0.5) = 1.3$) 
    * $\\alpha$ = Power law exponent for the exposure factor 
    * $D$ = Depth of the building parallel to the wind direction 
    * $\\rho_B$ = Average density of the building 
    * $n_D$ = Natural frequency of the building
    * $H$ = Building height
    
    *Note: The total lateral deflection at the top must not exceed 1/500 of the building height.*
    """)

with st.expander(" View Building Motion (Acceleration) Equation Details"):
    st.markdown("""
    **The maximum along-wind peak acceleration at the top of the building ($a_D$)** in m/s² can be estimated using Equation (3-13):
    """)
    st.latex(r"a_D = 4 \pi^2 n_D^2 g_p \sqrt{\frac{K s F}{C_{eH} \beta_D}} \cdot \frac{\Delta}{C_g}")
    st.markdown("""
    **Where:**
    * $g_p$ = Peak factor
    * $K$ = Coefficient depending on terrain roughness
    * $s$ = Size reduction factor
    * $F$ = Gust energy ratio at the natural frequency
    * $\\beta_D$ = Damping ratio in the along-wind direction 
    * $\Delta$ = Maximum lateral deflection at the top 
    * $C_g$ = Gust effect factor 
    
    *Note: To prevent occupant discomfort, the peak acceleration must not exceed 0.15 m/s² for residential buildings or 0.25 m/s² for commercial buildings.*
    """)

#Chapter 4: Across-wind Response and Torsional Moment")


st.write("---")
st.header("Across-wind Response and Torsional Moment")
st.caption("This chapter evaluates the across-wind response and torsional effects on the building, which are critical for slender buildings under wind loads. The calculations follow the procedures outlined in DPT Standard 1311-50, Section 4.")

# Assuming these variables are already calculated/fetched from Chapters 1-3:
# H, Wx, Wy, Floor_list, heights, V_bar, Ce_H, q (from q_H), I_w, rho_B, Cg_x, Cg_y

# Calculate wind velocity at the top of the building (V_H) and q_H
V_H = V_bar * math.sqrt(Ce_H)
q_H = q * Ce_H

# ==========================================
# Pre-Check: Is the building slender enough?
# ==========================================
# W * D is the same for both X and Y axes (Wx * Wy == Wy * Wx)
slenderness_check = H / math.sqrt(Wx * Wy) if (Wx * Wy) > 0 else 0

if slenderness_check < 3.0:
    st.info(f"💡 **Building Slenderness Ratio:** $H/\\sqrt{{WD}} = {slenderness_check:.2f}$")
    st.success("✅ **Building is not slender enough ($< 3.0$). Across-wind and torsional effects are not significant.** \n\n**➡️ You can safely skip this chapter.**")
    
    # The rest of Chapter 4 will NOT be rendered.
else:
    # ==========================================
    # Step 1: Additional Dynamic Properties
    # ==========================================
    st.subheader("1. Dynamic Properties for Across-wind and Torsion")
    col_dyn1, col_dyn2, col_dyn3, col_dyn4 = st.columns(4)
    with col_dyn1:
        n_W = st.number_input("Across-wind Natural Freq. $n_W$ (Hz)", value=44.0/H if H>0 else 1.0, step=0.1)
    with col_dyn2:
        beta_W = st.number_input("Across-wind Damping $\\beta_W$", value=0.015, step=0.005, format="%.3f")
    with col_dyn3:
        n_T = st.number_input("Torsional Natural Freq. $n_T$ (Hz)", value=55.0/H if H>0 else 1.2, step=0.1)
    with col_dyn4:
        beta_T = st.number_input("Torsional Damping $\\beta_T$", value=0.015, step=0.005, format="%.3f")

    # ==========================================
    # Step 2: Applicability Checks (Section 4.1)
    # ==========================================
    st.subheader("Applicability Checks ")
    st.markdown("The standard specifies limits for buildings to be considered for across-wind and torsional effects:")

    def check_section_4_1(H, W, D, V_H, n_W, n_T):
        r_slenderness = H / math.sqrt(W * D)
        r_DW = D / W
        r_vW = V_H / (n_W * math.sqrt(W * D)) if n_W > 0 else float('inf')
        r_vT = V_H / (n_T * math.sqrt(W * D)) if n_T > 0 else float('inf')
        
        is_applicable = True # ตั้งค่าเริ่มต้นให้ผ่าน
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**A. Necessity to Consider**")
            st.success(f"$\\frac{{H}}{{\\sqrt{{WD}}}} = {r_slenderness:.2f} \\ge 3$ \n\n**(✅ Must calculate)**")
                
            st.markdown("**B. Building Shape and Proportions**")
            if r_slenderness <= 6.0:
                st.success(f"$\\frac{{H}}{{\\sqrt{{WD}}}} = {r_slenderness:.2f}$ (✅ $\\le 6$)")
            else:
                st.error(f"$\\frac{{H}}{{\\sqrt{{WD}}}} = {r_slenderness:.2f}$ (❌ Exceeds 6)")
                is_applicable = False
                
            if 0.2 <= r_DW <= 5.0:
                st.success(f"$\\frac{{D}}{{W}} = {r_DW:.2f}$ (✅ Within 0.2 to 5)")
            else:
                st.error(f"$\\frac{{D}}{{W}} = {r_DW:.2f}$ (❌ Out of bounds: 0.2 to 5)")
                is_applicable = False

        with col2:
            st.markdown("**C. Across-wind Applicability Limit**")
            if r_vW <= 10.0:
                st.success(f"$\\frac{{V_H}}{{n_W\\sqrt{{WD}}}} = {r_vW:.2f} \\le 10$ (✅ Within scope)")
            else:
                st.error(f"$\\frac{{V_H}}{{n_W\\sqrt{{WD}}}} = {r_vW:.2f} > 10$ (❌ Building is too flexible)")
                is_applicable = False

            st.markdown("**D. Torsional Moment Applicability Limit**")
            if r_vT <= 10.0:
                st.success(f"$\\frac{{V_H}}{{n_T\\sqrt{{WD}}}} = {r_vT:.2f} \\le 10$ (✅ Within scope)")
            else:
                st.error(f"$\\frac{{V_H}}{{n_T\\sqrt{{WD}}}} = {r_vT:.2f} > 10$ (❌ Building is too flexible)")
                is_applicable = False
        
        if not is_applicable:
            st.error("⚠️ **The building parameters fall outside the limits of this standard. This chapter CANNOT be used for this wind direction.**")
                
        return is_applicable

    tab_chk_x, tab_chk_y = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])
    with tab_chk_x:
        st.markdown("*Wind acting on X-axis (Width $W = W_y$, Depth $D = W_x$)*")
        can_calc_x = check_section_4_1(H, W=Wy, D=Wx, V_H=V_H, n_W=n_W, n_T=n_T)
    with tab_chk_y:
        st.markdown("*Wind acting on Y-axis (Width $W = W_x$, Depth $D = W_y$)*")
        can_calc_y = check_section_4_1(H, W=Wx, D=Wy, V_H=V_H, n_W=n_W, n_T=n_T)

    # ==========================================
    # Step 3 & 4: P_L and M_T Functions
    # ==========================================
    def calculate_across_wind_force(H, W, D, V_H, n_W, beta_W, q_H, I_w, z, Area):
        ratio_DW = D / W
        C_L_prime = 0.0082*(ratio_DW**3) - 0.071*(ratio_DW**2) + 0.22*(ratio_DW) 
        g_L = math.sqrt(2 * math.log(3600 * n_W)) + 0.577 / math.sqrt(2 * math.log(3600 * n_W)) 
        
        beta_1 = ((ratio_DW**4) + 23*(ratio_DW**2)) / (2.8*(ratio_DW**4) - 9.8*(ratio_DW**3) + 18*(ratio_DW**2) + 9.5*(ratio_DW) - 0.15) + (0.12 / ratio_DW) 
        lambda_1 = ((1 + 0.38*(ratio_DW**2))**0.89 / 0.12) * ((n_W * W) / V_H) 
        term_FL1 = (4 * 0.85 * (1 + 0.6 * beta_1) * beta_1) / math.pi 
        term_FL2 = (lambda_1**2) / (((1 - lambda_1**2)**2) + 4 * (beta_1**2) * (lambda_1**2)) 
        
        if ratio_DW < 3.0: 
            F_L = term_FL1 * term_FL2
        else:
            beta_2 = 0.28 / (ratio_DW**0.34) 
            lambda_2 = ((ratio_DW**0.85) / 0.56) * ((n_W * W) / V_H) 
            term_FL1_2 = (4 * 0.02 * (1 + 0.6 * beta_2) * beta_2) / math.pi 
            term_FL2_2 = (lambda_2**2) / (((1 - lambda_2**2)**2) + 4 * (beta_2**2) * (lambda_2**2)) 
            F_L = (term_FL1 * term_FL2) + (term_FL1_2 * term_FL2_2) 
            
        R_L = (math.pi * F_L) / (4 * beta_W) 
        P_L = 3 * I_w * q_H * C_L_prime * Area * (z / H) * g_L * math.sqrt(1 + R_L) 
        a_w = 3 * I_w * q_H * C_L_prime * g_L * (W / (rho_B * W * D)) * (z / H) * math.sqrt(R_L) 
        return P_L, a_w, C_L_prime, F_L

    def calculate_torsion_moment(H, W, D, V_H, n_T, beta_T, q_H, I_w, z, Area):
        ratio_DW = D / W
        C_T_prime = (0.0066 + 0.015 * (ratio_DW**2)) ** 0.78 
        g_T = math.sqrt(2 * math.log(3600 * n_T)) + 0.577 / math.sqrt(2 * math.log(3600 * n_T)) 
        V_T_star = V_H / (n_T * math.sqrt(W * D)) 
        L = max(W, D) 
        
        def get_FT(v_star):
            if v_star <= 4.5: 
                Kt = (-1.1*ratio_DW + 0.97)/(ratio_DW**2 + 0.85*ratio_DW + 3.3) + 0.17 
                lt = (ratio_DW + 3.6)/(ratio_DW**2 - 5.1*ratio_DW + 9.1) + (0.14/ratio_DW) + 0.14 
            else: 
                Kt = (0.077*ratio_DW - 0.16)/(ratio_DW**2 - 0.96*ratio_DW + 0.42) + (0.35/ratio_DW) + 0.095 
                lt = (0.44*(ratio_DW**2) - 0.0064)/((ratio_DW**4) - 0.26*(ratio_DW**2) + 0.1) + 0.2 
            return (0.14 * (Kt**2) * (v_star**(2*lt)) / math.pi) * (D*(W**2 + D**2)**2) / ((L**2)*(W**3)) 

        if V_T_star <= 4.5 or (6 <= V_T_star <= 10): 
            F_T = get_FT(V_T_star)
        elif 4.5 < V_T_star < 6: 
            F_4_5 = get_FT(4.5) 
            F_6 = get_FT(6.0) 
            term_exp = 3.5 * math.log(F_6 / F_4_5) * math.log(V_T_star / 4.5) 
            F_T = F_4_5 * math.exp(term_exp) 
        else:
            F_T = 0 
            
        R_T = (math.pi * F_T) / (4 * beta_T) 
        M_T = 1.8 * I_w * q_H * C_T_prime * Area * W * (z / H) * g_T * math.sqrt(1 + R_T) 
        return M_T, C_T_prime, F_T

    # ==========================================
    # Step 5: Story Forces and Load Combinations
    # ==========================================
    st.subheader(" Across-wind and Torsional Results (Story-by-Story)")

    tab_calc_x, tab_calc_y = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])

    def calculate_story_forces_chapter4(H, W, D, V_H, n_W, beta_W, n_T, beta_T, q_H, I_w, floor_zs, floor_hs):
        results = []
        a_w_top = 0
        for z, h_story in zip(floor_zs, floor_hs):
            Area = W * h_story
            P_L, a_w, CL_p, FL = calculate_across_wind_force(H, W, D, V_H, n_W, beta_W, q_H, I_w, z, Area)
            M_T, CT_p, FT = calculate_torsion_moment(H, W, D, V_H, n_T, beta_T, q_H, I_w, z, Area)

            if abs(z - H) < 0.001: 
                a_w_top = a_w 
            
            results.append({
                "Height (z)": z,
                "Wind Area (m²)": Area,
                "P_across (kN)": P_L / 1000,
                "M_torsion (kN-m)": M_T / 1000,
            })
        return pd.DataFrame(results), a_w_top

    with tab_calc_x:
        st.markdown("**Wind acting on X-axis ($W = Wy, D = Wx$)**")
        if can_calc_x: # ใช้ตัวแปร can_calc_x ควบคุมการคำนวณ
            df_ch4_x, a_w_top_x = calculate_story_forces_chapter4(H, Wy, Wx, V_H, n_W, beta_W, n_T, beta_T, q_H, I_w, Floor_list, heights)
            st.dataframe(df_ch4_x.round(3), hide_index=True, use_container_width=True)
            st.info(f"  **Top Story Acceleration ($a_w$):** `{a_w_top_x:.4f}` m/s²")
            
            st.markdown("##### Load Combinations ")
            st.markdown("""
            * **Case A:** $1.0 P_{along} + 0.4 P_{across} + 0.4 M_T$
            * **Case B:** $(0.4 + 0.6/C_g) P_{along} + 1.0 P_{across} + 1.0 M_T$
            """)
            factor_B = 0.4 + (0.6 / Cg_x)
            with st.expander(" View Factor for Case B Calculation"):
                st.markdown(f"**Factor for $P_{{along}}$ in Case B:** $0.4 + \\frac{{0.6}}{{C_g}} = 0.4 + \\frac{{0.6}}{{{Cg_x:.2f}}} = {factor_B:.3f}$")
        else:
            st.error(" **Calculation is skipped for this axis because it does not meet the applicability requirements.**")

    with tab_calc_y:
        st.markdown("**Wind acting on Y-axis ($W = Wx, D = Wy$)**")
        if can_calc_y: # ใช้ตัวแปร can_calc_y ควบคุมการคำนวณ
            df_ch4_y, a_w_top_y = calculate_story_forces_chapter4(H, Wx, Wy, V_H, n_W, beta_W, n_T, beta_T, q_H, I_w, Floor_list, heights)
            st.dataframe(df_ch4_y.round(3), hide_index=True, use_container_width=True)
            st.info(f"  **Top Story Acceleration ($a_w$):** `{a_w_top_y:.4f}` m/s²")
            
            st.markdown("##### Load Combinations ")
            st.markdown("""
            * **Case A:** $1.0 P_{along} + 0.4 P_{across} + 0.4 M_T$
            * **Case B:** $(0.4 + 0.6/C_g) P_{along} + 1.0 P_{across} + 1.0 M_T$
            """)      
            factor_B = 0.4 + (0.6 / Cg_y)
            with st.expander(" View Factor for Case B Calculation"):
                st.markdown(f"**Factor for $P_{{along}}$ in Case B:** $0.4 + \\frac{{0.6}}{{C_g}} = 0.4 + \\frac{{0.6}}{{{Cg_y:.2f}}} = {factor_B:.3f}$")
        else:
            st.error(" **Calculation is skipped for this axis because it does not meet the applicability requirements.**")

st.write("---")