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

# ==========================================
# 1. Building Dimensions (มิติอาคาร)
# ==========================================

inputs = st.container()
with inputs:
    st.write('### 1. Building Dimensions')
    col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
    with col2:
        Floor = st.number_input(label='Number of Stories', min_value=1, max_value=100, value=10, step=1)
    
    with col3:
        Floor_list = []
        H = 0
        with st.expander("Define Story Heights (Default = 3m each)"):
            for i in range(Floor):
                # แปลป้ายกำกับความสูงแต่ละชั้น
                Heigth = st.number_input(label=f'Story Height {i+1} [m]', min_value=0.0, value=3.0, step=0.1, key=f"floor{i}")
                H += Heigth
                Floor_list.append(H)
        st.info(f"Total Height (H) = {H:.2f} m")

    with col1:
        Wx = st.number_input(label='Width parallel to X-axis [m]', min_value=0.0, value=20.0, step=0.1)
        Wy = st.number_input(label='Width parallel to Y-axis [m]', min_value=0.0, value=20.0, step=0.1)
        Ds = min(Wy, Wx)
        st.write(f'Minimum Building Width, $D_s={Ds:.2f}$ m')

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
    else:
        V_bar = V50
    st.markdown(f'$\overline{{V}}={V_bar:.2f}$ m/s')

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
# 6. Pressure Coefficients Cp and Cpi
# ==========================================
st.write('### 7. Pressure Coefficients, $C_p$ and $C_{pi}$')

def get_Cp_leeward(HD_ratio):
    if HD_ratio <= 0.25: return -0.30
    elif HD_ratio < 1: return -0.27*(HD_ratio + 0.88)
    else: return -0.50

def get_Cp_windward(HD_ratio):
    if HD_ratio <= 0.25: return 0.60
    elif HD_ratio < 1: return 0.27*(HD_ratio + 2)
    else: return 0.80

C_px_wind = get_Cp_windward(H/Wx)
C_px_lee = get_Cp_leeward(H/Wx)
C_py_wind = get_Cp_windward(H/Wy)
C_py_lee = get_Cp_leeward(H/Wy)

df_c_pi = pd.DataFrame({
    'Condition': ['No large openings', 'Unevenly distributed leakage', 'Large openings'],
    'C_pi-': [-0.15, -0.45, -0.7],
    'C_pi+': [0, 0.3, 0.7]
})
c_pi_choice = st.selectbox(label='Internal Pressure Case ($C_{pi}$)', options=df_c_pi['Condition'])
C_pi_minus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi-'].values[0]
C_pi_plus = df_c_pi.loc[df_c_pi['Condition'] == c_pi_choice, 'C_pi+'].values[0]

st.write("---")

# ==========================================
# 7. Net Wind Pressure
# ==========================================
st.markdown('### 8. Net Wind Pressure ($P_{net}$)')
st.markdown('$P_{net}=I_w q C_e C_g C_p - I_w q C_e C_{gi} C_{pi}$')

tab1, tab2 = st.tabs(["Wind on X-axis", "Wind on Y-axis"])

def plot_pressure(df, title):
    chart = alt.Chart(df).mark_bar(size=Floor*3, color='steelblue', opacity=0.8).encode(
        x=alt.X('Combine wind pressure (N/m²)', title='Combined Wind Pressure (N/m²)'),
        y=alt.Y('Height above ground (z)', title='Height (m)', sort='-y'),
        tooltip=['Height above ground (z)', 'Combine wind pressure (N/m²)']
    ).configure_mark(orient='horizontal').properties(height=400, title=title)
    st.altair_chart(chart, use_container_width=True)

with tab1:
    st.markdown(f'**Wind Direction: X-axis (using $C_{{gx}}={Cg_x:.2f}$)**')
    df_px = pd.DataFrame()
    df_px['Story'] = range(1, Floor+1)
    df_px['Height above ground (z)'] = Floor_list
    df_px['Ce'] = Ce_list
    df_px['Windward'] = I_w * q * df_px['Ce'] * (Cg_x * C_px_wind) - (I_w * q * df_px['Ce'] * c_gi * C_pi_minus)
    df_px['Leeward'] = I_w * q * Ce_H * (Cg_x * C_px_lee) - (I_w * q * Ce_H * c_gi * C_pi_minus)
    df_px['Combine wind pressure (N/m²)'] = abs(df_px['Windward']) + abs(df_px['Leeward'])
    
    st.dataframe(df_px.round(2), hide_index=True, use_container_width=True)
    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:
        plot_pressure(df_px, 'Net Pressure X-axis')

with tab2:
    st.markdown(f'**Wind Direction: Y-axis (using $C_{{gy}}={Cg_y:.2f}$)**')
    df_py = pd.DataFrame()
    df_py['Story'] = range(1, Floor+1)
    df_py['Height above ground (z)'] = Floor_list
    df_py['Ce'] = Ce_list
    df_py['Windward'] = I_w * q * df_py['Ce'] * (Cg_y * C_py_wind) - (I_w * q * df_py['Ce'] * c_gi * C_pi_minus)
    df_py['Leeward'] = I_w * q * Ce_H * (Cg_y * C_py_lee) - (I_w * q * Ce_H * c_gi * C_pi_minus)
    df_py['Combine wind pressure (N/m²)'] = abs(df_py['Windward']) + abs(df_py['Leeward'])
    
    st.dataframe(df_py.round(2), hide_index=True, use_container_width=True)
    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:
        plot_pressure(df_py, 'Net Pressure Y-axis')

st.write("---")


# ==========================================
# 8. Serviceability Check (Deflection & Acceleration)
# ==========================================
st.write('### 9. Lateral Deflection and Building Motion (Serviceability Check)')

col1, col2 = st.columns([1, 3])
with col1:
    rho_B = st.number_input("Average density of the building, $\\rho_B$ (kg/m³)", value=200.0, step=10.0)
with col2:
    st.info("💡 **Reference: DPT Standard 1311-50 (Section 3.7):**\n\n"
            "**$\\rho_B$ (Average density of the building)** is the total mass of the building divided by the enclosed volume ($Volume = W \\times D \\times H$). "
            "Generally, it ranges between **150 - 300 kg/m³**.")

# Calculate deflection and acceleration (checking X-axis as an example)
alpha = 0.5 if terrain_type == 'B' else (0.28 if terrain_type == 'A' else 0.72) # Power law exponent for Ce
Delta_x = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * (C_px_wind - C_px_lee)) / (4 * math.pi**2 * n_D**2 * Wx * rho_B * H**2)
a_Dx = 4 * math.pi**2 * n_D**2 * gp_x * math.sqrt((K_x * s_x * F_x) / (Ce_H * damping_ratio)) * (Delta_x / Cg_x)

st.markdown(f'''
- **Maximum lateral deflection at the top, X-axis ($\\Delta_x$)**: `{Delta_x:.4f}` m (Allowable limit = $H/500$ = {H/500:.4f} m) 
  - {"✅ **Pass**" if Delta_x <= H/500 else "❌ **Fail**"}
- **Maximum peak acceleration, X-axis ($a_D$)**: `{a_Dx:.4f}` m/s² 
  - *(Allowable limit = 0.15 m/s² for residential buildings, 0.25 m/s² for commercial buildings)* 
''')

st.write("---")

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
# st.write('### 9. Serviceability Check')
# col1, col2 = st.columns([1, 1.5]) # ปรับขนาดคอลัมน์ให้กล่องคำอธิบายกว้างขึ้นเล็กน้อย
# with col1:
#     rho_B = st.number_input("ความหนาแน่นเฉลี่ยมวลอาคาร $\\rho_B$ (kg/m³)", value=200.0, step=10.0)
# with col2:
#     # เพิ่มที่มาและอ้างอิงตาม มยผ.1311-50 หัวข้อ 3.7
#     st.info("💡 **อ้างอิง มยผ.1311-50 (หัวข้อ 3.7):**\n\n"
#             "**$\\rho_B$ (Average density of the building)** คือ ค่ามวลทั้งหมดของอาคาร หารด้วยปริมาตรของอาคารที่ถูกห่อหุ้มด้วยพื้นผิวภายนอกอาคาร ($Volume = W \\times D \\times H$) "
#             "โดยทั่วไปอาคารจะมีค่าความหนาแน่นมวลอยู่ระหว่าง **150 - 300 kg/m³**")
# # Check X-axis
# alpha = 0.5 if terrain_type == 'B' else (0.28 if terrain_type == 'A' else 0.72)
# Delta_x = (3 * (H**2 / (2 + alpha)) * 0.75 * q * Ce_H * (C_px_wind - C_px_lee)) / (4 * math.pi**2 * n_D**2 * Wx * rho_B * H**2)
# a_Dx = 4 * math.pi**2 * n_D**2 * gp_x * math.sqrt((K_x * s_x * F_x) / (Ce_H * damping_ratio)) * (Delta_x / Cg_x)

# st.markdown(f'''
# - **Top Drift X-axis ($\Delta_x$)**: `{Delta_x:.4f}` m (Limit = {H/500:.4f} m)
#   - {"✅ **Passed**" if Delta_x <= H/500 else "❌ **Failed**"}
# - **Peak Acceleration X-axis 
# ($a_D$)**: `{a_Dx:.4f}` m/s² (Limit = 0.15 m/s² for Residential, 0.25 m/s² for Commercial)
# ''')
# st.markdown("#### 📚 รายละเอียดสมการอ้างอิงตามมาตรฐาน มยผ.1311-50")

# with st.expander("📖 ดูรายละเอียดสมการการโก่งตัวด้านข้าง (Lateral Deflection)"):
#     st.markdown("""
#     **การโก่งตัวด้านข้างสูงสุดในทิศทางแนวราบ ณ ยอดอาคาร ($\Delta$)** ภายใต้แรงลมสถิตเทียบเท่า สามารถคำนวณโดยประมาณได้จากสมการ (3-12):
#     """)
#     st.latex(r"\Delta = \frac{3 \left( \frac{H^2}{2+\alpha} \right) I_w q C_{eH} C_p}{4 \pi^2 n_D^2 D \rho_B H^2}")
#     st.markdown("""
#     **โดยที่ตัวแปรคือ:**
#     * $I_w$ = ค่าประกอบความสำคัญของแรงลมในสภาวะจำกัดด้านการใช้งาน (กำหนดให้ใช้ 0.75 สำหรับตรวจสอบระยะโก่ง)
#     * $q$ = หน่วยแรงลมอ้างอิงเนื่องจากความเร็วลม ($q_H$)
#     * $C_{eH}$ = ค่าประกอบเนื่องจากสภาพภูมิประเทศที่ระดับยอดอาคาร
#     * $C_p$ = ค่าสัมประสิทธิ์ของหน่วยแรงลมด้านต้นลมและท้ายลมรวมกัน (ตัวอย่างเช่น $0.8 - (-0.5) = 1.3$)
#     * $\\alpha$ = ตัวยกกำลังของค่าประกอบเนื่องจากสภาพภูมิประเทศ
#     * $D$ = ความลึกของอาคารในทิศทางขนานกับทิศทางลม
#     * $\\rho_B$ = ความหนาแน่นเฉลี่ยของมวลอาคาร
#     * $n_D$ = ความถี่ธรรมชาติของอาคาร
#     * $H$ = ความสูงของอาคาร
    
#     *หมายเหตุ: ระยะโก่งตัวทั้งหมดที่เกิดขึ้น ณ ยอดอาคาร จะต้องไม่เกิน $1/500$ ของความสูงของอาคาร*
#     """)

# with st.expander("📖 ดูรายละเอียดสมการการสั่นไหวของอาคาร (Building Motion)"):
#     st.markdown("""
#     **อัตราเร่งสูงสุดในแนวราบที่ยอดอาคารในทิศทางลม ($a_D$)** มีหน่วยเป็น เมตร/วินาที² สามารถคำนวณโดยประมาณได้จากสมการ (3-13):
#     """)
#     st.latex(r"a_D = 4 \pi^2 n_D^2 g_p \sqrt{\frac{K s F}{C_{eH} \beta_D}} \cdot \frac{\Delta}{C_g}")
#     st.markdown("""
#     **โดยที่ตัวแปรเพิ่มเติมคือ:**
#     * $g_p$ = ค่าประกอบเชิงสถิติเพื่อปรับค่ารากกำลังสองเฉลี่ยให้เป็นค่าสูงสุด
#     * $K$ = ค่าสัมประสิทธิ์ที่มีค่าแปรเปลี่ยนไปตามความขรุขระของสภาพภูมิประเทศ
#     * $s$ = ตัวคูณลดเนื่องจากขนาดของอาคาร (Size reduction factor)
#     * $F$ = อัตราส่วนพลังงานของการแปรปรวนของลม ณ ความถี่ธรรมชาติของอาคาร
#     * $\\beta_D$ = อัตราส่วนความหน่วง (Damping ratio) ของการสั่นไหวในทิศทางลม
#     * $\Delta$ = การโก่งตัวด้านข้าง ณ ยอดอาคารที่คำนวณได้
#     * $C_g$ = ค่าประกอบเนื่องจากการกระโชกของลม (Gust effect factor)
    
#     *หมายเหตุ: เพื่อไม่ให้ผู้ใช้อาคารรู้สึกไม่สบาย อัตราเร่งสูงสุดจะต้องมีค่าไม่เกิน 0.15 m/s² สำหรับอาคารที่พักอาศัย หรือ 0.25 m/s² สำหรับอาคารพาณิชย์*
#     """)