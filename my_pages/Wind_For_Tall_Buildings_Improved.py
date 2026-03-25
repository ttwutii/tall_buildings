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
        Floor = st.number_input(label='Number of Stories', min_value=1, max_value=200, value=10, step=1)
        Wx = st.number_input(label='Width parallel to X-axis [m]', min_value=0.0, value=30.0, step=0.1)
        Wy = st.number_input(label='Width parallel to Y-axis [m]', min_value=0.0, value=45.0, step=0.1)
        Ds = min(Wy, Wx)
        st.write(f'Narrowest effective width, $D_s = {Ds:.2f}$ m')
        
    with col2:
        st.write("#### Define Story Data")
        st.caption("You can edit the numbers directly in the table or copy/paste from Excel.")
        
        init_data = pd.DataFrame({
            "Story": [i+1 for i in range(int(Floor))],
            "Height (m)": [4.0] * int(Floor),
            "Weight (tonne)": [1080.0] * int(Floor) 
        })
        
        edited_df = st.data_editor(init_data, use_container_width=True, hide_index=True)
        
        heights = edited_df["Height (m)"].tolist()
        Floor_list = []
        current_h = 0
        for h in heights:
            current_h += h
            Floor_list.append(current_h)
            
        H = current_h
        
        total_weight_tonne = edited_df["Weight (tonne)"].sum()
        total_mass_kg = total_weight_tonne * 1000
        volume = Wx * Wy * H
        
        if volume > 0:
            rho_B = total_mass_kg / volume
        else:
            rho_B = 0
        
        col2_1, col2_2, col2_3 = st.columns(3)
        col2_1.info(f"Total Height, $H = {H:.2f}$ m")
        col2_2.info(f"Total Weight = {total_weight_tonne:,.2f} tonnes")
        col2_3.info(f"Building Density, $\\rho_B = {rho_B:,.2f}$ kg/m³")

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
st.write('### 6. Dynamic Properties & Gust Response Factor ($C_g$)')
st.markdown("Specify the building's natural frequencies and damping properties.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    n_Dx = st.number_input("Freq. X-axis ($n_{Dx}$) [Hz]", value=44.0/H if H>0 else 1.0, step=0.01)
with col2:
    n_Dy = st.number_input("Freq. Y-axis ($n_{Dy}$) [Hz]", value=44.0/H if H>0 else 1.0, step=0.01)
with col3:
    damping_ratio = st.number_input("Damping ($\\beta_D, \\beta_W$)", value=0.015, step=0.001, format="%.3f")
with col4:
    n_T = st.number_input("Torsional Freq. ($n_T$) [Hz]", value=55.0/H if H>0 else 1.0, step=0.01)
with col5:
    beta_T = st.number_input("Torsional Damping ($\\beta_T$)", value=0.015, step=0.001, format="%.3f")

with st.expander("💡 Across-wind Frequency Logic (DPT 1311-50)"):
    st.markdown("""
    For rectangular buildings, the natural frequencies are swapped between along-wind and across-wind:
    - 🌬️ **Wind on X-axis:** - Along-wind frequency = $n_{Dx}$
      - Across-wind frequency ($n_W$) = $n_{Dy}$
    - 🌬️ **Wind on Y-axis:** - Along-wind frequency = $n_{Dy}$
      - Across-wind frequency ($n_W$) = $n_{Dx}$
      
    *(Note: The damping ratio for across-wind $\\beta_W$ is assumed to be equal to $\\beta_D$)*
    """)

def calculate_Cg_detailed(H, W_eff, V_bar, n_D, damping, t_type, Ce_H):
    V_H = V_bar * math.sqrt(Ce_H)
    K_dict = {'A': 0.08, 'B': 0.10, 'C': 0.14}
    K = K_dict[t_type]
    
    def integrand_B(x):
        term1 = 1 / (1 + (x * H / 457))
        term2 = 1 / (1 + (x * W_eff / 122))
        term3 = x / ((1 + x**2) ** (4/3))
        return term1 * term2 * term3
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
col1.info(f"**Wind on X-axis** (W = {Wy}m, $n_D$ = {n_Dx}Hz)\n\n$C_{{gx}}={Cg_x:.3f}$")
col2.info(f"**Wind on Y-axis** (W = {Wx}m, $n_D$ = {n_Dy}Hz)\n\n$C_{{gy}}={Cg_y:.3f}$")

c_gi = 2.0 

st.write("---")

# ==========================================
# 6. Wind Pressure Coefficients Cp and Cpi
# ==========================================
st.write('### 7. External ($C_p$) and Internal ($C_{pi}$) Wind Pressure Coefficients')

col_chk1, col_chk2 = st.columns(2)
with col_chk1:
    if H > 23:
        st.success(f"✅ **Height Check:** $H = {H:.2f}$ m > 23 m")
    else:
        st.error(f"❌ **Height Check:** $H \le 23$ m (Not applicable for Figure B.9) ")
with col_chk2:
    HDs = H / Ds if Ds > 0 else 0
    if HDs >= 1:
        st.success(f"✅ **Slenderness Check:** $H/D_s = {HDs:.2f} \ge 1$")
    else:
        st.error(f"❌ **Slenderness Check:** $H/D_s < 1$ (Not applicable for Figure B.9) ")

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

st.markdown("**Average Pressure Coefficients ($C_p$) and Local Pressure Coefficients ($C_p^*$)**")
col_cp1, col_cp2, col_cp3 = st.columns(3)
col_cp1.info(f"**Wind parallel to X-axis ($D = {Wx}$)**\n- Windward ($C_p$): {C_px_wind:.2f}\n- Leeward ($C_p$): {C_px_lee:.2f}")
col_cp2.info(f"**Wind parallel to Y-axis ($D = {Wy}$)**\n- Windward ($C_p$): {C_py_wind:.2f}\n- Leeward ($C_p$): {C_py_lee:.2f}")
col_cp3.warning("**Side Walls and Roof**\n- Side Walls ($C_p$): -0.70 \n- Roof ($C_p$): -1.0 to -0.5 \n- Wall edges ($C_p^*$): -1.20 ")

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
st.markdown('For the Main Wind Force Resisting System (MWFRS), internal pressures cancel out. The net pressure is the vector sum of windward and leeward external pressures.')
#st.latex(r'P_{MWFRS} = I_w q C_{e(z)} C_g C_{p(windward)} - I_w q C_{e(0.5H)} C_g C_{p(leeward)}')

Ce_05H = calculate_Ce(0.5 * H, terrain_type) 

with st.expander("📌 View Reference Height Rules for $C_e$"):
    st.markdown(f"""
    - **Windward walls:** Use height at each level ($z$) -> $C_e$ varies with height 
    - **Leeward walls:** Use $0.5H = {0.5*H:.2f}$ m -> $C_e = {Ce_05H:.3f}$ 
    """)

tab1, tab2 = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])

def plot_pressure(df, title):
    chart = alt.Chart(df).mark_bar(size=Floor*3, color='steelblue', opacity=0.8).encode(
        x=alt.X('Combine wind pressure (N/m²)', title='Combine Wind Pressure'),
        y=alt.Y('Height from ground (z)', title='Height (m)', sort='-y'),
        tooltip=['Height from ground (z)', 'Windward (N/m²)', 'Leeward (N/m²)', 'Combine wind pressure (N/m²)']
    ).configure_mark(orient='horizontal').properties(height=400, title=title)
    st.altair_chart(chart, use_container_width=True)

def plot_force(df, title):
    lines = alt.Chart(df).mark_rule(color='#E65100', strokeWidth=2).encode(
        x=alt.X('Force acting on the layer (kN)', title='Total Force (kN)'),
        x2=alt.value(0), 
        y=alt.Y('Floor', title='Number of Floors', sort='-y'),
        tooltip=['Floor', 'Height from ground (z)', 'Wind-receiving area (m²)', 'Force acting on the layer (kN)']
    )
    heads = alt.Chart(df).mark_point(shape='triangle-left', color='#E65100', filled=True, size=100, opacity=1).encode(
        x=alt.value(0), y=alt.Y('Floor', sort='-y'),
    )
    chart = (lines + heads).properties(height=400, title=title)
    st.altair_chart(chart, use_container_width=True)

with tab1:
    st.markdown(f'**Wind parallel to X-axis (Using $C_{{gx}}={Cg_x:.2f}$)**')
    df_px = pd.DataFrame()
    df_px['Floor'] = range(1, Floor+1)
    df_px['Height from ground (z)'] = Floor_list
    df_px['Story heights'] = heights
    df_px['Ce(z)'] = Ce_list
    
    # Calculate Net Pressure for MWFRS (No Internal Pressure)
    df_px['Windward (N/m²)'] = I_w * q * df_px['Ce(z)'] * Cg_x * C_px_wind
    df_px['Leeward (N/m²)'] = I_w * q * Ce_05H * Cg_x * C_px_lee
    df_px['Combine wind pressure (N/m²)'] = df_px['Windward (N/m²)'] - df_px['Leeward (N/m²)']

    df_px['Wind-receiving area (m²)'] = df_px['Story heights'] * Wy
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
    
    df_py['Windward (N/m²)'] = I_w * q * df_py['Ce(z)'] * Cg_y * C_py_wind
    df_py['Leeward (N/m²)'] = I_w * q * Ce_05H * Cg_y * C_py_lee
    df_py['Combine wind pressure (N/m²)'] = df_py['Windward (N/m²)'] - df_py['Leeward (N/m²)']

    df_py['Wind-receiving area (m²)'] = df_py['Story heights'] * Wx
    df_py['Force acting on the layer (kN)'] = df_py['Combine wind pressure (N/m²)'] * df_py['Wind-receiving area (m²)'] / 1000
    
    st.dataframe(df_py.round(2), hide_index=True, use_container_width=True)
    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:
        plot_pressure(df_py, 'Net Pressure Y-axis')
        plot_force(df_py, 'Wind Force Y-axis')

st.write("---")

# ==========================================
# 8. Wind Load for Components & Cladding (C&C)
# ==========================================
st.write('### 9. Design Wind Pressures for Exterior Walls and Roofs (Components & Cladding)')
st.markdown("""
For designing exterior cladding, windows, and roof coverings, the standard requires considering the combined effect of external and internal pressures ($C_{pi}+$ and $C_{pi}-$). 
A specific gust effect factor ($C_g = 2.5$) and internal gust factor ($C_{gi} = 2.0$) are used. Local pressure coefficients ($C_p^*$) are applied for edge and corner zones which experience high suction.
""")
st.latex(r'P_{C\&C} = I_w q C_e C_g C_p - I_w q C_{e(0.5H)} C_{gi} C_{pi}')

Cg_cc = 2.5
Cgi_cc = 2.0
p_int_minus = I_w * q * Ce_05H * Cgi_cc * C_pi_minus
p_int_plus = I_w * q * Ce_05H * Cgi_cc * C_pi_plus

def get_max_net_pressures(p_ext):
    net_1 = p_ext - p_int_minus
    net_2 = p_ext - p_int_plus
    max_inward = max(net_1, net_2, 0)
    max_suction = min(net_1, net_2, 0)
    return max_inward, max_suction

wall_data = []
for z in Floor_list:
    Ce_z = calculate_Ce(z, terrain_type)
    p_ext_windward = I_w * q * Ce_z * Cg_cc * (0.8) 
    in_w, suc_w = get_max_net_pressures(p_ext_windward)
    
    p_ext_leeward = I_w * q * Ce_05H * Cg_cc * (-0.5)
    in_l, suc_l = get_max_net_pressures(p_ext_leeward)
    
    p_ext_side = I_w * q * Ce_H * Cg_cc * (-0.7)
    in_s, suc_s = get_max_net_pressures(p_ext_side)
    
    p_ext_side_edge = I_w * q * Ce_H * Cg_cc * (-1.2)
    in_se, suc_se = get_max_net_pressures(p_ext_side_edge)
    
    wall_data.append({
        "Height z (m)": z,
        "Windward (Inward)": in_w,
        "Leeward (Suction)": suc_l,
        "Side General (Suction)": suc_s,
        "Side Edge Zone (Suction)": suc_se
    })

df_walls_cc = pd.DataFrame(wall_data)

roof_zones = [
    {"Zone": "General Roof (Cp = -0.7)", "Cp": -0.7},
    {"Zone": "Edge Roof (Cp* = -1.5)", "Cp": -1.5},
    {"Zone": "Corner Roof (Cp* = -2.3)", "Cp": -2.3}
]
roof_data = []
for r in roof_zones:
    p_ext_roof = I_w * q * Ce_H * Cg_cc * r["Cp"]
    in_r, suc_r = get_max_net_pressures(p_ext_roof)
    roof_data.append({
        "Roof Zone": r["Zone"],
        "External Pressure (N/m²)": p_ext_roof,
        "Max Suction for Design (N/m²)": suc_r
    })
df_roof_cc = pd.DataFrame(roof_data)

tab_wall_cc, tab_roof_cc = st.tabs(["🧱 Exterior Walls Design Pressure", "🏠 Roof Design Pressure"])
with tab_wall_cc:
    st.markdown("**Net Design Pressures for Exterior Walls (N/m²)**")
    st.caption("Values represent the worst-case net pressures (External - Internal). Use positive values for inward pressure and negative values for outward suction.")
    wall_col_config = {
        "Height z (m)": st.column_config.NumberColumn("Height z (m)", format="%.1f"),
        "Windward (Inward)": st.column_config.NumberColumn("Windward (Inward)", format="%.1f"),
        "Leeward (Suction)": st.column_config.NumberColumn("Leeward (Suction)", format="%.1f"),
        "Side General (Suction)": st.column_config.NumberColumn("Side General (Suction)", format="%.1f"),
        "Side Edge Zone (Suction)": st.column_config.NumberColumn("Side Edge Zone (Suction)", format="%.1f"),
    }
    st.dataframe(df_walls_cc, column_config=wall_col_config, hide_index=True, use_container_width=True)

with tab_roof_cc:
    st.markdown("**Net Design Pressures for Roof Coverings (N/m²)**")
    st.caption(f"Calculated at Reference Height $H = {H:.2f}$ m. Corner zones apply to an area $0.2D \\times 0.2D$, edge zones apply to width $0.1D$.")
    roof_col_config = {
        "External Pressure (N/m²)": st.column_config.NumberColumn("External Pressure (N/m²)", format="%.1f"),
        "Max Suction for Design (N/m²)": st.column_config.NumberColumn("Max Suction for Design (N/m²)", format="%.1f"),
    }
    st.dataframe(df_roof_cc, column_config=roof_col_config, hide_index=True, use_container_width=True)

st.write("---")

# ==========================================
# 9. Serviceability Check (Deflection & Acceleration)
# ==========================================
st.write('### 10. Lateral Deflection and Building Motion (Serviceability Check)')

st.info(f"💡 **Average building density ($\\rho_B$)** used for this calculation is **{rho_B:.2f} kg/m³**")

alpha = 0.5 if terrain_type == 'B' else (0.28 if terrain_type == 'A' else 0.72) 

Delta_x = 0; a_Dx = 0
if rho_B > 0 and n_Dx > 0 and Wx > 0:
    Delta_x = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * (C_px_wind - C_px_lee)) / (4 * math.pi**2 * n_Dx**2 * Wx * rho_B * H**2)
    a_Dx = 4 * math.pi**2 * n_Dx**2 * gp_x * math.sqrt((K_x * s_x * F_x) / (Ce_H * damping_ratio)) * (Delta_x / Cg_x)

Delta_y = 0; a_Dy = 0
if rho_B > 0 and n_Dy > 0 and Wy > 0:
    Delta_y = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * (C_py_wind - C_py_lee)) / (4 * math.pi**2 * n_Dy**2 * Wy * rho_B * H**2)
    a_Dy = 4 * math.pi**2 * n_Dy**2 * gp_y * math.sqrt((K_y * s_y * F_y) / (Ce_H * damping_ratio)) * (Delta_y / Cg_y)

col_chk1, col_chk2 = st.columns(2)
with col_chk1:
    st.markdown(f"#### 🌬️ Wind on X-axis (using $n_{{Dx}}$={n_Dx}Hz)")
    st.markdown(f'''
    - **Lateral deflection ($\\Delta_x$)**: `{Delta_x:.4f}` m
      - *Limit ($H/500$)* = {H/500:.4f} m ➡️ {"✅ **Pass**" if Delta_x <= H/500 else "❌ **Fail**"}
    - **Peak acceleration ($a_{{Dx}}$)**: `{a_Dx:.4f}` m/s² 
      - *Limit (Res/Com)* = 0.15 / 0.25 m/s²
    ''')

with col_chk2:
    st.markdown(f"#### 🌬️ Wind on Y-axis (using $n_{{Dy}}$={n_Dy}Hz)")
    st.markdown(f'''
    - **Lateral deflection ($\\Delta_y$)**: `{Delta_y:.4f}` m
      - *Limit ($H/500$)* = {H/500:.4f} m ➡️ {"✅ **Pass**" if Delta_y <= H/500 else "❌ **Fail**"}
    - **Peak acceleration ($a_{{Dy}}$)**: `{a_Dy:.4f}` m/s² 
      - *Limit (Res/Com)* = 0.15 / 0.25 m/s²
    ''')

with st.expander("📖 View Equation Details from DPT 1311-50"):
    st.markdown("**Lateral Deflection ($\Delta$):**")
    st.latex(r"\Delta = \frac{3 \left( \frac{H^2}{2+\alpha} \right) I_w q C_{eH} C_p}{4 \pi^2 n_D^2 D \rho_B H^2}")
    st.markdown("**Along-wind Peak Acceleration ($a_D$):**")
    st.latex(r"a_D = 4 \pi^2 n_D^2 g_p \sqrt{\frac{K s F}{C_{eH} \beta_D}} \cdot \frac{\Delta}{C_g}")

st.write("---")

# ==========================================
# Chapter 4: Across-wind Response and Torsional Moment
# ==========================================
st.header("Across-wind Response and Torsional Moment (Chapter 4)")
st.caption("This chapter evaluates the across-wind response and torsional effects on the building, which are critical for slender buildings under wind loads. The calculations follow the procedures outlined in DPT Standard 1311-50, Section 4.")

V_H = V_bar * math.sqrt(Ce_H)
q_H = q * Ce_H

# ==========================================
# Pre-Check: Is the building slender enough?
# ==========================================
slenderness_check = H / math.sqrt(Wx * Wy) if (Wx * Wy) > 0 else 0

if slenderness_check < 3.0:
    st.info(f"💡 **Building Slenderness Ratio:** $H/\\sqrt{{WD}} = {slenderness_check:.2f}$")
    st.success("✅ **Building is not slender enough ($< 3.0$). Across-wind and torsional effects are not significant.** \n\n**➡️ You can safely skip this chapter.**")
else:
    st.subheader("Applicability Checks ")
    st.markdown("The standard specifies limits for buildings to be considered for across-wind and torsional effects:")

    def check_section_4_1(H, W, D, V_H, n_W, n_T):
        r_slenderness = H / math.sqrt(W * D)
        r_DW = D / W
        r_vW = V_H / (n_W * math.sqrt(W * D)) if n_W > 0 else float('inf')
        r_vT = V_H / (n_T * math.sqrt(W * D)) if n_T > 0 else float('inf')
        
        is_applicable = True 
        
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
        st.markdown(f"*Wind acting on X-axis (Width $W = W_y$, Depth $D = W_x$, using $n_W = n_{{Dy}} = {n_Dy}$ Hz)*")
        can_calc_x = check_section_4_1(H, W=Wy, D=Wx, V_H=V_H, n_W=n_Dy, n_T=n_T)
    with tab_chk_y:
        st.markdown(f"*Wind acting on Y-axis (Width $W = W_x$, Depth $D = W_y$, using $n_W = n_{{Dx}} = {n_Dx}$ Hz)*")
        can_calc_y = check_section_4_1(H, W=Wx, D=Wy, V_H=V_H, n_W=n_Dx, n_T=n_T)

# ==========================================
    # Step 2 & 3: P_L and M_T Functions
    # ==========================================
    # เอาพารามิเตอร์ Area ออกจากวงเล็บ เพื่อให้คำนวณเป็นแบบ "ต่อความสูง 1 เมตร"
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
        
        # คำนวณแรงต่อความสูง 1 เมตร (N/m) ใช้คูณด้วย W
        P_L_per_m = 3 * I_w * q_H * C_L_prime * W * (z / H) * g_L * math.sqrt(1 + R_L) 
        
        # อัตราเร่งสูงสุด (m/s^2)
        a_w = 3 * I_w * q_H * C_L_prime * g_L * (W / (rho_B * W * D)) * (z / H) * math.sqrt(R_L) if rho_B > 0 else 0
        
        # ส่งค่า F_L, g_L, R_L กลับไปด้วยเพื่อนำไปแสดงในตาราง
        return P_L_per_m, a_w, C_L_prime, F_L, g_L, R_L

    # เอาพารามิเตอร์ Area ออกเช่นกัน
    def calculate_torsion_moment(H, W, D, V_H, n_T, beta_T, q_H, I_w, z):
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
            power = math.log(V_T_star / 4.5) / math.log(6.0 / 4.5)
            F_T = F_4_5 * math.exp(power * math.log(F_6 / F_4_5)) 
        else:
            F_T = 0 
            
        R_T = (math.pi * F_T) / (4 * beta_T) 
        
        # โมเมนต์บิดต่อความสูง 1 เมตร (N-m/m) ต้องคูณด้วย W * D
        M_T_per_m = 1.8 * I_w * q_H * C_T_prime * W * D * (z / H) * g_T * math.sqrt(1 + R_T) 
        return M_T_per_m, C_T_prime, F_T

    # ==========================================
    # Step 4: Story Forces and Load Combinations
    # ==========================================
    st.subheader(" Across-wind and Torsional Results (Story-by-Story) & Export")

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8-sig')

    tab_calc_x, tab_calc_y = st.tabs(["Wind Direction: X-axis", "Wind Direction: Y-axis"])

    def calculate_story_forces_chapter4(H, W, D, V_H, n_W, beta_W, n_T, beta_T, q_H, I_w, floor_zs, floor_hs):
        results = []
        a_w_top = 0
        for z, h_story in zip(floor_zs, floor_hs):
            
            # รับค่า g_L และ R_L เพิ่มเข้ามา
            P_L_per_m, a_w, CL_p, FL, g_L, R_L = calculate_across_wind_force(H, W, D, V_H, n_W, beta_W, q_H, I_w, z)
            M_T_per_m, CT_p, FT = calculate_torsion_moment(H, W, D, V_H, n_T, beta_T, q_H, I_w, z)

            if abs(z - H) < 0.001: 
                a_w_top = a_w 
            
            # นำแรงต่อ 1 เมตร มาคูณความสูงของชั้น (h_story) เพื่อให้ได้แรงรวมต่อชั้น
            P_story_kN = (P_L_per_m * h_story) / 1000
            M_story_kNm = (M_T_per_m * h_story) / 1000
            
            results.append({
                "Story": floor_zs.index(z) + 1,
                "Height z (m)": z,
                "F_L": FL,
                "g_L": g_L,
                "R_L": R_L,
                "P_across (kN)": P_story_kN,
                "M_torsion (kN-m)": M_story_kNm,
            })
        return pd.DataFrame(results), a_w_top
   
    with tab_calc_x:
        st.markdown("**Wind acting on X-axis ($W = Wy, D = Wx$)**")
        if can_calc_x: 
            df_ch4_x, a_w_top_x = calculate_story_forces_chapter4(H, Wy, Wx, V_H, n_W=n_Dy, beta_W=damping_ratio, n_T=n_T, beta_T=beta_T, q_H=q_H, I_w=I_w, floor_zs=Floor_list, floor_hs=heights)
            st.dataframe(df_ch4_x.round(3), hide_index=True, use_container_width=True)
            st.info(f"  **Top Story Acceleration ($a_w$):** `{a_w_top_x:.4f}` m/s²")
           
            st.header("Load Combinations ")
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
        if can_calc_y: 
            df_ch4_y, a_w_top_y = calculate_story_forces_chapter4(H, Wx, Wy, V_H, n_W=n_Dx, beta_W=damping_ratio, n_T=n_T, beta_T=beta_T, q_H=q_H, I_w=I_w, floor_zs=Floor_list, floor_hs=heights)
            st.dataframe(df_ch4_y.round(3), hide_index=True, use_container_width=True)
            st.info(f"  **Top Story Acceleration ($a_w$):** `{a_w_top_y:.4f}` m/s²")
           
            st.header("Load Combinations ")
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