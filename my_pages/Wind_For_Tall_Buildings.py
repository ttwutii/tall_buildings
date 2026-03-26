import streamlit as st
import pandas as pd 
import numpy as np
import math
import scipy.integrate as integrate
import altair as alt

st.set_page_config(page_title="DPT 1311-50 Wind Load", layout="wide")

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
        # เซ็ตค่าเริ่มต้นให้ตรงกับ PDF ตัวอย่างที่ 3 (หน้า 1)
        Floor = st.number_input(label='Number of Stories', min_value=1, max_value=200, value=60, step=1) 
        Wx = st.number_input(label='Width parallel to X-axis [m]', min_value=0.0, value=30.0, step=0.1)
        Wy = st.number_input(label='Width parallel to Y-axis [m]', min_value=0.0, value=45.0, step=0.1)
        Ds = min(Wy, Wx)
        st.write(f'Narrowest effective width, $D_s = {Ds:.2f}$ m')
        
        # เพิ่มช่องรับค่า rho_B ตรงๆ เพื่อป้องกันความคลาดเคลื่อนจากการคำนวณย้อนกลับ
        rho_B = st.number_input(label='Building Density $\\rho_B$ [kg/m³]', min_value=0.0, value=200.0, step=10.0)
        
    with col2:
        st.write("#### Define Story Data")
        st.caption("You can edit the numbers directly in the table or copy/paste from Excel.")
        
        init_data = pd.DataFrame({
            "Story": [i+1 for i in range(int(Floor))],
            "Height (m)": [3.0] * int(Floor), # ใช้ชั้นละ 3ม. รวม 60 ชั้น จะได้ 180ม. พอดี
        })
        
        edited_df = st.data_editor(init_data, use_container_width=True, hide_index=True)
        
        heights = edited_df["Height (m)"].tolist()
        Floor_list = []
        current_h = 0
        for h in heights:
            current_h += h
            Floor_list.append(current_h)
            
        H = current_h
        st.info(f"✅ **Total Building Height ($H$) = {H:.2f} m**")

st.write("---")

# ==========================================
# 2. Importance and Wind Speed
# ==========================================
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
    important_type = st.selectbox(label='Importance Category', options=df_important['Building Importance Category'], index=1)
    cal_type = st.selectbox(label='Design Limit State', options=['Ultimate Limit State', 'Serviceability Limit State'])
    I_w = df_important.loc[df_important['Building Importance Category'] == important_type, cal_type].values[0]
    st.markdown(f'$I_w={I_w:.2f}$')

with col2:
    st.write('### 3. Reference Wind Speed, $\overline{V}$')
    area_group = st.selectbox(label='Area Zone Group', options=df_wind_speed['Zone Group'], index=0)
    V50 = df_wind_speed.loc[df_wind_speed['Zone Group'] == area_group, 'V50 [m/s]'].values[0]
    T_F = df_wind_speed.loc[df_wind_speed['Zone Group'] == area_group, 'T_F'].values[0]
    
    if cal_type == 'Ultimate Limit State':
        V_bar = V50 * T_F
    else:
        V_bar = V50
    st.markdown(f'$\overline{{V}}={V_bar:.2f}$ m/s')
    with st.expander("View Map of Wind Zone Groups"):
        st.image("mapwind.png", caption="Map of Wind Zone Groups (Source: DPT 1311-50, Figure 1)")

st.write("---")

# ==========================================
# 3. Reference Velocity Pressure (q)
# ==========================================
rho = 1.25
q = 0.5 * rho * (V_bar**2)
st.write('### 4. Reference Velocity Pressure, $q$')
st.markdown(f'$q=0.5\\rho\\overline{{V}}^2=0.5(1.25)({V_bar})^2={q:.2f}$ N/m²')
st.write("---")

# ==========================================
# 4. Exposure Factor (Ce)
# ==========================================
st.markdown('### 5. Exposure Factor, $C_e$')
terrain_type = st.selectbox(label='Terrain Category', options=['A', 'B', 'C'], index=1)

def calculate_Ce(z, t_type):
    if t_type == 'A': return max(1.0, min((z/10)**0.28, 2.5))
    elif t_type == 'B': return max(0.5, min(0.5*(z/12.7)**0.5, 2.5))
    elif t_type == 'C': return max(0.4, min(0.4*(z/30)**0.72, 2.5))

Ce_list = [calculate_Ce(z, terrain_type) for z in Floor_list]
Ce_H = calculate_Ce(H, terrain_type)
st.write("---")

# ==========================================
# 5. Dynamic Properties & Gust Factor (Cg)
# ==========================================
st.write('### 6. Dynamic Properties & Gust Response Factor ($C_g$)')

col1, col2, col3, col4, col5 = st.columns(5)
with col1: n_Dx = st.number_input("Freq. X-axis ($n_{Dx}$) [Hz]", value=44.0/H if H>0 else 1.0, step=0.01, format="%.2f")
with col2: n_Dy = st.number_input("Freq. Y-axis ($n_{Dy}$) [Hz]", value=44.0/H if H>0 else 1.0, step=0.01, format="%.2f")
with col3: damping_ratio = st.number_input("Damping ($\\beta_D, \\beta_W$)", value=0.015, step=0.001, format="%.3f")
with col4: n_T = st.number_input("Torsional Freq. ($n_T$) [Hz]", value=55.0/H if H>0 else 1.0, step=0.01, format="%.2f")
with col5: beta_T = st.number_input("Torsional Damping ($\\beta_T$)", value=0.015, step=0.001, format="%.3f")

with st.expander("💡 Across-wind Frequency Logic (DPT 1311-50)"):
    st.markdown("""
    -  **Wind on X-axis:** Along-wind freq = $n_{Dx}$ | Across-wind freq ($n_W$) = $n_{Dy}$
    -  **Wind on Y-axis:** Along-wind freq = $n_{Dy}$ | Across-wind freq ($n_W$) = $n_{Dx}$
    """)

def calculate_Cg_detailed(H, W_eff, V_bar, n_D, damping, t_type, Ce_H):
    V_H = V_bar * math.sqrt(Ce_H)
    K_dict = {'A': 0.08, 'B': 0.10, 'C': 0.14}
    K = K_dict[t_type]
    
    def integrand_B(x):
        return (1 / (1 + (x * H / 457))) * (1 / (1 + (x * W_eff / 122))) * (x / ((1 + x**2) ** (4/3)))
    upper_limit = 914 / H if H > 0 else 0
    B_val, _ = integrate.quad(integrand_B, 0, upper_limit)
    B = (4/3) * B_val
    
    s = (math.pi/3) * (1 / (1 + (8*n_D*H)/(3*V_H))) * (1 / (1 + (10*n_D*W_eff)/V_H))
    X_0 = (1220 * n_D) / V_H
    F = (X_0**2) / ((1 + X_0**2)**(4/3))
    v = n_D * math.sqrt((s * F) / (s * F + damping * B))
    g_p = math.sqrt(2 * math.log(v * 3600)) + 0.577 / math.sqrt(2 * math.log(v * 3600))
    sigma_mu = math.sqrt((K / Ce_H) * (B + (s * F / damping)))
    C_g = 1 + g_p * sigma_mu
    return C_g, K, s, F, g_p

Cg_x, K_x, s_x, F_x, gp_x = calculate_Cg_detailed(H, Wy, V_bar, n_Dx, damping_ratio, terrain_type, Ce_H)
Cg_y, K_y, s_y, F_y, gp_y = calculate_Cg_detailed(H, Wx, V_bar, n_Dy, damping_ratio, terrain_type, Ce_H)

col1, col2 = st.columns(2)
col1.info(f"**Wind on X-axis** (W = {Wy}m, $n_D$ = {n_Dx:.2f}Hz)\n\n$C_{{gx}}={Cg_x:.3f}$")
col2.info(f"**Wind on Y-axis** (W = {Wx}m, $n_D$ = {n_Dy:.2f}Hz)\n\n$C_{{gy}}={Cg_y:.3f}$")
st.write("---")

# ==========================================
# 6. Pressure Coefficients Cp and Cpi
# ==========================================
st.write('### 7. External ($C_p$) and Internal ($C_{pi}$) Pressure Coefficients')
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

# Function to calculate Cp based on Figure B.9 from DPT 1311-50
def get_Cp_windward(HD_ratio):
    if HD_ratio <= 0.25: return 0.60
    elif HD_ratio < 1: return 0.27 * (HD_ratio + 2)
    else: return 0.80

def get_Cp_leeward(HD_ratio):
    if HD_ratio <= 0.25: return -0.30
    elif HD_ratio < 1: return -0.27 * (HD_ratio + 0.88)
    else: return -0.50

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

with st.expander("📌 View Figure $C_p$ and $C_p^*$"):
    st.image("Cp_tallbuildings.png", caption="Pressure Coefficients ($C_p$) and Local Pressure Coefficients ($C_p^*$) (Source: DPT 1311-50, Figure B.9)")


df_c_pi = pd.DataFrame({
    'Condition': ['Without large openings', 'With unevenly distributed leakage', 'With large openings'],
    'C_pi-': [-0.15, -0.45, -0.7],
    'C_pi+': [0, 0.3, 0.7]
})
c_pi_choice = st.selectbox(label='Internal Pressure Condition ($C_{pi}$) [For C&C Design only]', options=df_c_pi['Condition'])
C_pi_minus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi-'].values[0]
C_pi_plus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi+'].values[0]

st.write("---")

# ==========================================
# 7. Net Wind Pressure for MWFRS
# ==========================================
st.markdown('### 8. Net Wind Pressure for Main Wind Force Resisting System (MWFRS)')
Ce_05H = calculate_Ce(0.5 * H, terrain_type)

tab1, tab2 = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])

with tab1:
    st.markdown(f'**Wind parallel to X-axis (Using $C_{{gx}}={Cg_x:.2f}$)**')
    df_px = pd.DataFrame()
    df_px['Floor'] = range(1, Floor+1)
    df_px['Height from ground (z)'] = Floor_list
    df_px['Story heights'] = heights
    df_px['Ce(z)'] = Ce_list
    
    df_px['Windward (N/m²)'] = I_w * q * df_px['Ce(z)'] * Cg_x * C_px_wind
    df_px['Leeward (N/m²)'] = I_w * q * Ce_05H * Cg_x * C_px_lee
    df_px['Combine wind pressure (N/m²)'] = abs(df_px['Windward (N/m²)']) + abs(df_px['Leeward (N/m²)'])
    df_px['Wind-receiving area (m²)'] = df_px['Story heights'] * Wy
    df_px['Force acting on the layer (kN)'] = df_px['Combine wind pressure (N/m²)'] * df_px['Wind-receiving area (m²)'] / 1000
    st.dataframe(df_px.round(2), hide_index=True, use_container_width=True)
        
with tab2:
    st.markdown(f'**Wind parallel to Y-axis (Using $C_{{gy}}={Cg_y:.2f}$)**')
    df_py = pd.DataFrame()
    df_py['Floor'] = range(1, Floor+1)
    df_py['Height from ground (z)'] = Floor_list
    df_py['Story heights'] = heights
    df_py['Ce(z)'] = Ce_list
    
    df_py['Windward (N/m²)'] = I_w * q * df_py['Ce(z)'] * Cg_y * C_py_wind
    df_py['Leeward (N/m²)'] = I_w * q * Ce_05H * Cg_y * C_py_lee
    df_py['Combine wind pressure (N/m²)'] = abs(df_py['Windward (N/m²)']) + abs(df_py['Leeward (N/m²)'])
    df_py['Wind-receiving area (m²)'] = df_py['Story heights'] * Wx
    df_py['Force acting on the layer (kN)'] = df_py['Combine wind pressure (N/m²)'] * df_py['Wind-receiving area (m²)'] / 1000
    st.dataframe(df_py.round(2), hide_index=True, use_container_width=True)

st.write("---")

# ==========================================
# 8. Wind Load for Components & Cladding (C&C)
# ==========================================
st.write('### 9. Design Wind Pressures for Exterior Walls and Roofs (Components & Cladding)')

Cg_cc = 2.5
Cgi_cc = 2.0
p_int_minus = I_w * q * Ce_05H * Cgi_cc * C_pi_minus
p_int_plus = I_w * q * Ce_05H * Cgi_cc * C_pi_plus

def get_max_net_pressures(p_ext):
    net_1 = p_ext - p_int_minus
    net_2 = p_ext - p_int_plus
    return max(net_1, net_2, 0), min(net_1, net_2, 0)

# 👉 แก้ไข: ดึงค่า Cp วิกฤต (Worst-case) จากที่คำนวณผ่านฟังก์ชันมาแล้ว เพื่อให้รองรับอาคารทุกสัดส่วน (H/D)
Cp_windward_max = max(C_px_wind, C_py_wind)
Cp_leeward_min = min(C_px_lee, C_py_lee) # ใช้ min เพื่อหาค่าติดลบที่มากที่สุด (แรงดูดสูงสุด)

wall_data = []
for z in Floor_list:
    Ce_z = calculate_Ce(z, terrain_type)
    
    # ⚠️ แทนที่ 0.8 และ -0.5 ด้วยตัวแปรที่ผ่านฟังก์ชัน get_Cp... มาแล้ว
    in_w, suc_w = get_max_net_pressures(I_w * q * Ce_z * Cg_cc * Cp_windward_max) 
    in_l, suc_l = get_max_net_pressures(I_w * q * Ce_05H * Cg_cc * Cp_leeward_min) 
    
    # สำหรับ Side General และ Side Edge มาตรฐานระบุเป็นสัมประสิทธิ์เฉพาะที่ (Local Cp*) คงที่คือ -0.7 และ -1.2
    in_s, suc_s = get_max_net_pressures(I_w * q * Ce_H * Cg_cc * -0.7) 
    in_se, suc_se = get_max_net_pressures(I_w * q * Ce_H * Cg_cc * -1.2) 
    
    wall_data.append({
        "Height z (m)": z, 
        "Windward-Inward(N/m²)": in_w, 
        "Leeward-Suction(N/m²)": suc_l, 
        "Side General-Suction(N/m²)": suc_s, 
        "Side Edge-Suction(N/m²)": suc_se
    })

df_walls_cc = pd.DataFrame(wall_data)

# สำหรับหลังคาก็ใช้ Local Cp* คงที่ตามที่มาตรฐานระบุเช่นกัน
roof_zones = [
    {"Zone": "General Roof", "Cp": -0.7}, 
    {"Zone": "Edge Roof", "Cp": -1.5}, 
    {"Zone": "Corner Roof", "Cp": -2.3}
]
roof_data = [{"Roof Zone": r["Zone"], "Max Suction (N/m²)": get_max_net_pressures(I_w * q * Ce_H * Cg_cc * r["Cp"])[1]} for r in roof_zones]
df_roof_cc = pd.DataFrame(roof_data)

tab_wall_cc, tab_roof_cc = st.tabs(["🧱 Exterior Walls Design Pressure", "🏠 Roof Design Pressure"])
with tab_wall_cc: 
    st.dataframe(df_walls_cc.round(1), hide_index=True, use_container_width=True)
    st.markdown("**Net Design Pressures for Exterior Walls (N/m²)**")
    st.caption("Values represent the worst-case net pressures (External - Internal). Use positive values for inward pressure and negative values for outward suction.")
with tab_roof_cc: 
    st.dataframe(df_roof_cc.round(1), hide_index=True, use_container_width=True)
    st.markdown("**Net Design Pressures for Roof Coverings (N/m²)**")
    st.caption(f"Calculated at Reference Height $H = {H:.2f}$ m. Corner zones apply to an area $0.2D \\times 0.2D$, edge zones apply to width $0.1D$.")

st.write("---")

# ==========================================
# 9. Serviceability Check (Deflection & Acceleration)
# ==========================================
st.write('### 10. Lateral Deflection and Building Motion (Serviceability Check)')

alpha = 0.5 if terrain_type == 'B' else (0.28 if terrain_type == 'A' else 0.72) 

# คำนวณ Deflection (Delta) ต้องเอา Cg_x และ Cg_y คูณเข้าไปด้วยให้ถูกตามสมการ
Delta_x = 0; a_Dx = 0
if rho_B > 0 and n_Dx > 0 and Wx > 0:
    Delta_x = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * Cg_x * (C_px_wind - C_px_lee)) / (4 * math.pi**2 * n_Dx**2 * Wx * rho_B * H**2)
    a_Dx = 4 * math.pi**2 * n_Dx**2 * gp_x * math.sqrt((K_x * s_x * F_x) / (Ce_H * damping_ratio)) * (Delta_x / Cg_x)

Delta_y = 0; a_Dy = 0
if rho_B > 0 and n_Dy > 0 and Wy > 0:
    Delta_y = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * Cg_y * (C_py_wind - C_py_lee)) / (4 * math.pi**2 * n_Dy**2 * Wy * rho_B * H**2)
    a_Dy = 4 * math.pi**2 * n_Dy**2 * gp_y * math.sqrt((K_y * s_y * F_y) / (Ce_H * damping_ratio)) * (Delta_y / Cg_y)

col_chk1, col_chk2 = st.columns(2)
with col_chk1:
    st.markdown(f"####  Wind on X-axis (using $n_{{Dx}}$={n_Dx:.2f}Hz)")
    st.markdown(f"- **Lateral deflection ($\Delta_x$)**: `{Delta_x:.4f}` m (Limit: {H/500:.4f} m)\n- **Peak acceleration ($a_{{Dx}}$)**: `{a_Dx:.4f}` m/s²")
with col_chk2:
    st.markdown(f"####  Wind on Y-axis (using $n_{{Dy}}$={n_Dy:.2f}Hz)")
    st.markdown(f"- **Lateral deflection ($\Delta_y$)**: `{Delta_y:.4f}` m (Limit: {H/500:.4f} m)\n- **Peak acceleration ($a_{{Dy}}$)**: `{a_Dy:.4f}` m/s²")

st.write("---")

# ==========================================
# Chapter 4: Across-wind Response and Torsional Moment
# ==========================================
st.header("Across-wind Response and Torsional Moment ")

V_H = V_bar * math.sqrt(Ce_H)
q_H = q * Ce_H
slenderness_check = H / math.sqrt(Wx * Wy) if (Wx * Wy) > 0 else 0

if slenderness_check < 3.0:
    st.success(f"✅ **Building Slenderness Ratio:** $H/\\sqrt{{WD}} = {slenderness_check:.2f} < 3.0$. (Skip this chapter)")
    st.header(" Load Combinations ")


    # Main Title
    st.subheader("Wind Load Cases & Torsional Combinations")
    st.markdown("Combinations of wind forces acting along the principal axes and torsional moments (Based on Figure 2.2).")

    # --- CASE 1 ---
    st.write("##### Case 1: Full Design Wind Load (No Torsion)")
    st.write("**Direction X only:** $p_{WX}$ (Windward), $p_{LX}$ (Leeward)")
    st.write("**Direction Y only:** $p_{WY}$ (Windward), $p_{LY}$ (Leeward)")

    st.divider()

    # --- CASE 2 ---
    st.write("##### Case 2: 75% Wind Load + Torsion")
    st.write(" **X-Direction + Torsion**")
    st.write("Pressures: $0.75p_{WX}$, $0.75p_{LX}$")
    st.write("Torsional Moment: $M_{TX} = 0.75(p_{WX} + p_{LX})B_X e_X$ where $e_X = \pm 0.15B_X$")

    st.write(" **Y-Direction + Torsion**")
    st.write("Pressures: $0.75p_{WY}$, $0.75p_{LY}$")
    st.write("Torsional Moment: $M_{TY} = 0.75(p_{WY} + p_{LY})B_Y e_Y$ where $e_Y = \pm 0.15B_Y$")

    st.divider()

    # --- CASE 3 ---
    st.write("##### Case 3: 75% Combined Wind Load (No Torsion)")
    st.write("Wind acting simultaneously along both principal axes at 75% capacity.")
    st.write("X-Axis: $0.75p_{WX}$, $0.75p_{LX}$")
    st.write("Y-Axis: $0.75p_{WY}$, $0.75p_{LY}$")

    st.divider()

    # --- CASE 4 ---
    st.write("##### Case 4: 56.3% Combined Wind Load + Torsion")
    st.write("Simultaneous wind forces along both axes at 56.3% capacity, plus combined torsion.")
    st.write("X-Axis: $0.563p_{WX}$, $0.563p_{LX}$")
    st.write("Y-Axis: $0.563p_{WY}$, $0.563p_{LY}$")
    st.write("Combined Torsion: $M_T = 0.563(p_{WX} + p_{LX})B_X e_X + 0.563(p_{WY} + p_{LY})B_Y e_Y$")
    st.write("Where $e_X = \pm 0.15B_X$ and $e_Y = \pm 0.15B_Y$")
    with st.expander("📌 View Load Combination Details"):
        st.image("combswind1.png", caption="Combination of wind load effects: along-wind, across-wind, and torsional moment. (DPT 1311-50, Section 2.8)")
else:
    def check_section_4_1(H, W, D, V_H, n_W, n_T):
        r_slenderness = H / math.sqrt(W * D)
        r_DW = D / W
        r_vW = V_H / (n_W * math.sqrt(W * D)) if n_W > 0 else float('inf')
        r_vT = V_H / (n_T * math.sqrt(W * D)) if n_T > 0 else float('inf')
        
        is_applicable = True 
        if r_slenderness > 6.0 or not (0.2 <= r_DW <= 5.0) or r_vW > 10.0 or r_vT > 10.0:
            is_applicable = False
                
        return is_applicable

    tab_chk_x, tab_chk_y = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])
    with tab_chk_x:
        st.markdown(f"*Wind acting on X-axis (Width $W = W_y$, Depth $D = W_x$, using $n_W = n_{{Dy}} = {n_Dy:.2f}$ Hz)*")
        can_calc_x = check_section_4_1(H, W=Wy, D=Wx, V_H=V_H, n_W=n_Dy, n_T=n_T)
    with tab_chk_y:
        st.markdown(f"*Wind acting on Y-axis (Width $W = W_x$, Depth $D = W_y$, using $n_W = n_{{Dx}} = {n_Dx:.2f}$ Hz)*")
        can_calc_y = check_section_4_1(H, W=Wx, D=Wy, V_H=V_H, n_W=n_Dx, n_T=n_T)

    # ==========================================
    # Across-wind & Torsion Calculation Core
    # ==========================================
    def calculate_across_wind_force(H, W, D, V_H, n_W, beta_W, q_H, I_w, z):
        ratio_DW = D / W
        C_L_prime = 0.0082*(ratio_DW**3) - 0.071*(ratio_DW**2) + 0.22*(ratio_DW) 
        g_L = math.sqrt(2 * math.log(3600 * n_W)) + 0.577 / math.sqrt(2 * math.log(3600 * n_W)) 
        
        beta_1 = ((ratio_DW**4) + 2.3*(ratio_DW**2)) / (2.4*(ratio_DW**4) - 9.2*(ratio_DW**3) + 18*(ratio_DW**2) + 9.5*(ratio_DW) - 0.15) + (0.12 / ratio_DW) 
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
        P_L_per_m = 3 * I_w * q_H * C_L_prime * W * (z / H) * g_L * math.sqrt(1 + R_L) 
        
        # ⚠️ อัตราเร่ง a_w ต้องใช้ Iw = 0.75 เสมอ ตามมาตรฐาน มยผ.
        a_w = 3 * 0.75 * q_H * C_L_prime * g_L * (W / (rho_B * W * D)) * (z / H) * math.sqrt(R_L) if rho_B > 0 else 0
        
        details = {'C_L_prime': C_L_prime, 'g_L': g_L, 'beta_1': beta_1, 'lambda_1': lambda_1, 'F_L': F_L, 'R_L': R_L}
        return P_L_per_m, a_w, details

    def calculate_torsion_moment(H, W, D, V_H, n_T, beta_T, q_H, I_w, z):
        ratio_DW = D / W
        C_T_prime = (0.0066 + 0.015 * (ratio_DW**2)) ** 0.78 
        g_T = math.sqrt(2 * math.log(3600 * n_T)) + 0.577 / math.sqrt(2 * math.log(3600 * n_T)) 
        V_T_star = V_H / (n_T * math.sqrt(W * D)) 
        
        def get_FT(v_star):
            if v_star <= 4.5: 
                Kt = (-1.1*ratio_DW + 0.97)/(ratio_DW**2 + 0.85*ratio_DW + 3.3) + 0.17 
                lt = (ratio_DW + 3.6)/(ratio_DW**2 - 5.1*ratio_DW + 9.1) + (0.14/ratio_DW) + 0.14 
            else: 
                Kt = (0.077*ratio_DW - 0.16)/(ratio_DW**2 - 0.96*ratio_DW + 0.42) + (0.35/ratio_DW) + 0.095 
                lt = (0.44*(ratio_DW**2) - 0.0064)/((ratio_DW**4) - 0.26*(ratio_DW**2) + 0.1) + 0.2 
            return (0.14 * (Kt**2) * (v_star**(2*lt)) / math.pi) * (D*(W**2 + D**2)**2) / ((max(W, D)**2)*(W**3)) 

        if V_T_star <= 4.5 or (6 <= V_T_star <= 10): 
            F_T = get_FT(V_T_star)
        elif 4.5 < V_T_star < 6: 
            power = math.log(V_T_star / 4.5) / math.log(6.0 / 4.5)
            F_T = get_FT(4.5) * math.exp(power * math.log(get_FT(6.0) / get_FT(4.5))) 
        else: 
            F_T = 0 
            
        R_T = (math.pi * F_T) / (4 * beta_T) 
        M_T_per_m = 1.8 * I_w * q_H * C_T_prime * W * W * (z / H) * g_T * math.sqrt(1 + R_T) 
        
        details = {'V_T_star': V_T_star, 'C_T_prime': C_T_prime, 'g_T': g_T, 'F_T': F_T, 'R_T': R_T}
        return M_T_per_m, details

    st.subheader(" Across-wind and Torsional Results & Export")

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8-sig')

    def process_story_forces_ch4(H, W, D, V_H, n_W, beta_W, n_T, beta_T, q_H, I_w, floor_zs, floor_hs):
        results = []
        a_w_top = 0
        latest_aw_det = {}; latest_t_det = {}
        for z, h_story in zip(floor_zs, floor_hs):
            P_L_per_m, a_w, aw_det = calculate_across_wind_force(H, W, D, V_H, n_W, beta_W, q_H, I_w, z)
            M_T_per_m, t_det = calculate_torsion_moment(H, W, D, V_H, n_T, beta_T, q_H, I_w, z)

            if abs(z - H) < 0.001: 
                a_w_top = a_w
                latest_aw_det = aw_det
                latest_t_det = t_det
            
            P_story_kN = (P_L_per_m * h_story) / 1000
            M_story_kNm = (M_T_per_m * h_story) / 1000
            
            results.append({
                "Story": floor_zs.index(z) + 1,
                "Height z (m)": z,
                "P_across (kN)": P_story_kN,
                "M_torsion (kN-m)": M_story_kNm,
            })
        return pd.DataFrame(results), a_w_top, latest_aw_det, latest_t_det
    
    tab_calc_x, tab_calc_y = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])

    with tab_calc_x:
        if can_calc_x: 
            df_ch4_x, a_w_top_x, det_aw_x, det_t_x = process_story_forces_ch4(H, Wy, Wx, V_H, n_W=n_Dy, beta_W=damping_ratio, n_T=n_T, beta_T=beta_T, q_H=q_H, I_w=I_w, floor_zs=Floor_list, floor_hs=heights)
            
            with st.expander("🔍 View Detailed Parameters "):
                c1, c2 = st.columns(2)
                c1.markdown(f"**Across-wind Params:**\n- $V_H={V_H:.2f}, q_H={q_H:.1f}$\n- $D/W={(Wx/Wy):.3f}$\n- $C'_L={det_aw_x['C_L_prime']:.4f}$\n- $g_L={det_aw_x['g_L']:.3f}$\n- $\\beta_1={det_aw_x['beta_1']:.3f}, \\lambda_1={det_aw_x['lambda_1']:.3f}$\n- $F_L={det_aw_x['F_L']:.4f}, R_L={det_aw_x['R_L']:.2f}$")
                c2.markdown(f"**Torsional Params:**\n- $V_T^*={det_t_x['V_T_star']:.2f}$\n- $C'_T={det_t_x['C_T_prime']:.4f}$\n- $g_T={det_t_x['g_T']:.3f}$\n- $F_T={det_t_x['F_T']:.4f}, R_T={det_t_x['R_T']:.2f}$")

            st.dataframe(df_ch4_x.round(3), hide_index=True, use_container_width=True)
            st.info(f"**Top Story Across-wind Acceleration ($a_w$):** `{a_w_top_x:.4f}` m/s²")

            st.header("Load Combinations ")
            st.markdown("""
            * **Case A:** $1.0 P_{along} + 0.4 P_{across} + 0.4 M_T$
            * **Case B:** $(0.4 + 0.6/C_g) P_{along} + 1.0 P_{across} + 1.0 M_T$
            """)
            factor_B = 0.4 + (0.6 / Cg_x)
            with st.expander(" View Factor for Case B Calculation"):
                st.markdown(f"**Factor for $P_{{along}}$ in Case B:** $0.4 + \\frac{{0.6}}{{C_g}} = 0.4 + \\frac{{0.6}}{{{Cg_x:.2f}}} = {factor_B:.3f}$")

            
        else:
            st.error("🛑 Not applicable for X-axis.")
            st.error(" **Calculation is skipped because it does not meet the applicability requirements.**")

    with tab_calc_y:
        if can_calc_y: 
            df_ch4_y, a_w_top_y, det_aw_y, det_t_y = process_story_forces_ch4(H, Wx, Wy, V_H, n_W=n_Dx, beta_W=damping_ratio, n_T=n_T, beta_T=beta_T, q_H=q_H, I_w=I_w, floor_zs=Floor_list, floor_hs=heights)
            
            with st.expander("🔍 View Detailed Parameters "):
                c1, c2 = st.columns(2)
                c1.markdown(f"**Across-wind Params:**\n- $V_H={V_H:.2f}, q_H={q_H:.1f}$\n- $D/W={(Wy/Wx):.3f}$\n- $C'_L={det_aw_y['C_L_prime']:.4f}$\n- $g_L={det_aw_y['g_L']:.3f}$\n- $\\beta_1={det_aw_y['beta_1']:.3f}, \\lambda_1={det_aw_y['lambda_1']:.3f}$\n- $F_L={det_aw_y['F_L']:.4f}, R_L={det_aw_y['R_L']:.2f}$")
                c2.markdown(f"**Torsional Params:**\n- $V_T^*={det_t_y['V_T_star']:.2f}$\n- $C'_T={det_t_y['C_T_prime']:.4f}$\n- $g_T={det_t_y['g_T']:.3f}$\n- $F_T={det_t_y['F_T']:.4f}, R_T={det_t_y['R_T']:.2f}$")

            st.dataframe(df_ch4_y.round(3), hide_index=True, use_container_width=True)
            st.info(f"**Top Story Across-wind Acceleration ($a_w$):** `{a_w_top_y:.4f}` m/s²")
            
            st.header("Load Combinations ")
            st.markdown("""
            * **Case A:** $1.0 P_{along} + 0.4 P_{across} + 0.4 M_T$
            * **Case B:** $(0.4 + 0.6/C_g) P_{along} + 1.0 P_{across} + 1.0 M_T$
            """)      
            factor_B = 0.4 + (0.6 / Cg_y)
            with st.expander(" View Factor for Case B Calculation"):
                st.markdown(f"**Factor for $P_{{along}}$ in Case B:** $0.4 + \\frac{{0.6}}{{C_g}} = 0.4 + \\frac{{0.6}}{{{Cg_y:.2f}}} = {factor_B:.3f}$")
         
        else:
            st.error("🛑 Not applicable for Y-axis.")
            st.error(" **Calculation is skipped  because it does not meet the applicability requirements.**")