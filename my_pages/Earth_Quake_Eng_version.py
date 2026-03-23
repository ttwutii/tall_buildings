import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate
from PIL import Image
import plotly.graph_objects as go
import sys

# Set Page Config
st.set_page_config(page_title='Seismic Design DPT', layout='wide', page_icon="🏗️")

try:
    import openpyxl  # Ensure this library is installed
except ModuleNotFoundError:
    st.error("The openpyxl library is not installed. Please install it using 'pip install openpyxl'.")
    st.stop()

# --- ฟังก์ชันสำหรับโหลดไฟล์ Excel โดยใช้ Cache (ช่วยให้เว็บเร็วขึ้นมาก) ---
@st.cache_data
def load_excel_data(sheet_name):
    return pd.read_excel('แผ่นดินไหว_table.xlsx', sheet_name=sheet_name)

def img_show(name, caption='', width=True):
    image = Image.open(name) 
    return st.image(image, use_column_width=width, caption=caption)

# Title Translation
st.title('DPT Standard 1301/1302-61: Seismic Design')
st.divider()

st.caption('### Input number of stories and details of the structure')
col1, col2 = st.columns([0.3, 0.7])
with col1:
    Floor = st.number_input(label='Number of Stories', min_value=1, max_value=80, value=4, step=1)

with col2:
    st.write("### Define Story Data")
    st.caption("You can edit the numbers directly in the table or copy/paste from Excel.")
    # สร้าง Dataframe เริ่มต้นสำหรับให้ผู้ใช้กรอก
    init_data = pd.DataFrame({
        "Story": [i+1 for i in range(Floor)],
        "Height (m)": [3.0] * Floor,
        "Weight (tonne)": [125.0] * Floor
    })
    
    # st.data_editor ช่วยให้กรอกข้อมูลเป็นตารางเหมือน Excel ได้เลย
    edited_df = st.data_editor(init_data, use_container_width=True, hide_index=True)
    
    # ดึงค่าจากตารางไปใช้คำนวณ
    Floor_list = edited_df["Height (m)"].cumsum().tolist()
    Weight_list = edited_df["Weight (tonne)"].tolist()
    Witotal_list = edited_df["Weight (tonne)"].cumsum().tolist()
    H = Floor_list[-1] if len(Floor_list) > 0 else 0

st.write('---')

# Section 1: Importance Factor
st.write('### 1. Importance Factor and Occupancy Category')
important_dict = {
    'Low': 1.0,      # น้อย
    'Normal': 1.0,   # ปกติ
    'High': 1.25,    # มาก
    'Essential': 1.5 # สูงมาก
}

important = st.selectbox(label='Importance Category', options=list(important_dict.keys()), key='important')
I = important_dict[important]
st.write(r'Importance factor, $I = %.2f$'%(I))

st.write('---')

# Section 2: Analysis Procedure
st.write('### 2. Structural Analysis Procedure')
cal_list = ['Equivalent Static Procedure', 'Dynamic Analysis Procedure']
cal = st.radio(label='Analysis Method', options=cal_list, index=0, key='cal', horizontal=True)

st.write('### 3. Structural Details')
col1, col2, col3 = st.columns(3)
with col1:
    structure_list = ['Reinforced Concrete', 'Steel Structure']
    structure = st.radio(label='Structure Type', options=structure_list, index=0, key='structure')
with col2:
    if structure == structure_list[0]:
        damping_list = ['5.0%', '2.5%']
    else:
        damping_list = ['2.5%']
    damping = st.radio(label='Damping Ratio', options=damping_list, index=0, key='damping')

st.write('---')

# Section 4: Design Spectral Acceleration
st.write('### 4. Design Spectral Response Acceleration')

bkk = st.checkbox('Design in Bangkok Basin area?', value=False, key='bkk')

if not bkk:
    df_SsS1 = load_excel_data('SsS1')

    col1, col2, col3 = st.columns(3)
    with col1:
        province = st.selectbox(label='Province', options=df_SsS1['จังหวัด'].unique(), index=12, key='province')
    with col2:
        district = st.selectbox(label='District/Amphoe', options=df_SsS1.loc[df_SsS1['จังหวัด']==province, 'อำเภอ'], key='district')

    Ss = df_SsS1.loc[(df_SsS1['จังหวัด']==province) & (df_SsS1['อำเภอ']==district), 'Ss'].iloc[0]
    S1 = df_SsS1.loc[(df_SsS1['จังหวัด']==province) & (df_SsS1['อำเภอ']==district), 'S1'].iloc[0]

    st.write(r'$S_{s} = %.3f \> g$'%(Ss))
    st.write(r'$S_{1} = %.3f \> g$'%(S1))
    
    st.write('---')
    st.write('### Site Class Adjustment (Soil Effect)')

    # เพิ่ม Class F
    soil_type = st.selectbox(label='Site Class (Soil Type)', options=['A','B','C','D','E','F'], index=0, key='soil_type')

    def FaFv(df, S):
        if S <= df['index'].min():
            F = df[soil_type].iloc[0]
        elif S >= df['index'].max():
            F = df[soil_type].iloc[-1]
        else:
            y0 = df.loc[df['index'] <= S, soil_type].iloc[-1]
            y1 = df.loc[df['index'] >= S, soil_type].iloc[0]
            x0 = df.loc[df['index'] <= S, 'index'].iloc[-1]
            x1 = df.loc[df['index'] >= S, 'index'].iloc[0]
            f = interpolate.interp1d([x0, x1], [y0, y1])
            F = f([S])[0]
        return F

    df_Fa = load_excel_data('Fa')
    df_Fa.set_index('ประเภทชั้นดิน', inplace=True)
    df_Fa = df_Fa.T.reset_index().astype('float')

    df_Fv = load_excel_data('Fv')
    df_Fv.set_index('ประเภทชั้นดิน', inplace=True)
    df_Fv = df_Fv.T.reset_index().astype('float')

    # เงื่อนไขรับค่าแบบ Manual สำหรับ Site Class F
    if soil_type == 'F':
        st.warning('⚠️ **Site Class F:** ชั้นดินประเภทนี้ต้องอาศัยการวิเคราะห์การตอบสนองเฉพาะพื้นที่ (Site-Specific Geotechnical Investigation) โปรดระบุค่า Fa และ Fv ที่ได้จากรายงานโดยตรง')
        col_fa, col_fv = st.columns(2)
        with col_fa:
            Fa = st.number_input('Manual Fa', min_value=0.0, value=1.000, step=0.001, format="%.3f")
        with col_fv:
            Fv = st.number_input('Manual Fv', min_value=0.0, value=1.000, step=0.001, format="%.3f")
    else:
        Fa = FaFv(df_Fa, Ss)
        Fv = FaFv(df_Fv, S1)

    st.write(r'$F_a = %.3f$'%(Fa))
    st.write(r'$F_v = %.3f$'%(Fv))

    SMS = Fa * Ss
    SM1 = Fv * S1

    st.write(r'$S_{MS} = F_{a} S_{s} = %.3f \times %.3f = %.3f \> g$'%(Fa, Ss, SMS))
    st.write(r'$S_{M1} = F_{v} S_{1} = %.3f \times %.3f = %.3f \> g$'%(Fv, S1, SM1))

    st.write('---')
    st.write('### Design Earthquake Parameters')

    SDS = (2/3) * SMS
    SD1 = (2/3) * SM1

    st.write(r'$S_{DS} = \frac{2}{3} S_{MS} = \frac{2}{3} \times %.3f = %.3f \> g$'%(SMS, SDS))
    st.write(r'$S_{D1} = \frac{2}{3} S_{M1} = \frac{2}{3} \times %.3f = %.3f \> g$'%(SM1, SD1))
    
else:
    # Bangkok Basin Logic
    with (st.expander('Bangkok Basin Zone Map')):
        img_show('eq_bkk_zone.png')
    
    zone = st.selectbox(label='Zone', options=np.arange(1, 11), key='zone')
    
    if cal == cal_list[0]:
        sheet_name_ = 'bkk_equivalent'
    else:
        sheet_name_ = 'bkk_rsa'
        
    if damping == '5.0%':
        sheet_name = sheet_name_ + '_5.0'
    else:
        sheet_name = sheet_name_ + '_2.5'
    
    df_bkk = load_excel_data(sheet_name)
    col = df_bkk.columns
    df_bkk = pd.melt(df_bkk, id_vars=col[0], value_vars=col[1:], var_name='T', value_name='Sa').astype('float')
    
    SDS = df_bkk.loc[(df_bkk['zone']==zone) & (df_bkk['T']==0.2), 'Sa'].iloc[0]
    SD1 = df_bkk.loc[(df_bkk['zone']==zone) & (df_bkk['T']==1.0), 'Sa'].iloc[0]
    
    st.write(r'$S_{DS} = %.3f \> g$'%(SDS))
    st.write(r'$S_{D1} = %.3f \> g$'%(SD1))

# Section 5: Fundamental Period
st.write('### 5. Approximate Fundamental Period ($T_a$)')
if structure == structure_list[0]:
    T_structure = 0.02 * H
    st.write('Structure:', structure, r'$\qquad T = 0.02H = 0.02 \times %.2f \mathrm{~m} = %.3f \mathrm{~sec}$'%(H, T_structure))
else:
    T_structure = 0.03 * H
    st.write('Structure:', structure, r'$\qquad T = 0.03H = 0.03 \times %.2f \mathrm{~m} = %.3f \mathrm{~sec}$'%(H, T_structure))

st.write('---')
    
# Section 6: Seismic Design Category
st.write('### 6. Seismic Design Category (SDC)')
st.info('The SDC classification based on $S_{DS}$ and $S_{D1}$ is determined considering a 5% damping ratio for all building types.')

type_dict = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}

def type161162TS(SDS, SD1):
    imp_map = {'Low': 'น้อย', 'Normal': 'ปกติ', 'High': 'มาก', 'Essential': 'สูงมาก'}
    thai_imp = imp_map[important]
    
    df = load_excel_data('T1.6-1')
    df = pd.melt(df, id_vars=['min','max'], value_vars=['น้อย','ปกติ','มาก','สูงมาก'], var_name='important', value_name='type')
    type161 = df.loc[(df['min']<=SDS) & (df['max']>SDS) & (df['important']==thai_imp), 'type'].iloc[0]

    df = load_excel_data('T1.6-2')
    df = pd.melt(df, id_vars=['min','max'], value_vars=['น้อย','ปกติ','มาก','สูงมาก'], var_name='important', value_name='type')
    type162 = df.loc[(df['min']<=SD1) & (df['max']>SD1) & (df['important']==thai_imp), 'type'].iloc[0]
    
    TS = SD1/SDS if SD1 <= SDS else 1.0
    return type161, type162, TS

if bkk and damping=='2.5%':
    df_bkkx = load_excel_data(sheet_name_ + '_5.0')
    colx = df_bkkx.columns
    df_bkkx = pd.melt(df_bkkx, id_vars=col[0], value_vars=col[1:], var_name='T', value_name='Sa').astype('float')
    SDSx = df_bkkx.loc[(df_bkkx['zone']==zone) & (df_bkkx['T']==0.2), 'Sa'].iloc[0]
    SD1x = df_bkkx.loc[(df_bkkx['zone']==zone) & (df_bkkx['T']==1.0), 'Sa'].iloc[0]
    st.write('For 5% Damping ratio reference:')
    st.write(r'$S_{DS} = %.3f \> g, \quad S_{D1} = %.3f \> g$'%(SDSx, SD1x))
    type161, type162, TTSS = type161162TS(SDSx, SD1x)
else:
    type161, type162, TTSS = type161162TS(SDS, SD1)
    
if not bkk:
    if T_structure < 0.8 * TTSS:
        st.write(r'As $T = %.3f \mathrm{~s} < 0.8 T_s = %.3f \mathrm{~s}$'%(T_structure, 0.8*TTSS))
        st.write('SDC determined by Table 1.6-1 only.')
        type_num = type161
    else:
        st.write(r'As $T = %.3f \mathrm{~s} \ge 0.8 T_s = %.3f \mathrm{~s}$'%(T_structure, 0.8*TTSS))
        st.write('SDC determined by the most stringent of Table 1.6-1 and 1.6-2.')
        type_num = max(type161, type162)
else:
    if T_structure <= 0.5:
        st.write(r'As $T = %.3f \mathrm{~s} \le 0.5 \mathrm{~s}$'%(T_structure))
        st.write('SDC determined by Table 1.6-1 only.')
        type_num = type161
    else:
        st.write(r'As $T = %.3f \mathrm{~s} > 0.5 \mathrm{~s}$'%(T_structure))
        st.write('SDC determined by Table 1.6-2 only.')
        type_num = type162

final_type = type_dict[str(type_num)]
st.write(r'Seismic Design Category: <span style="color:red">**Category %s**</span>'%(final_type), unsafe_allow_html=True)
st.write('---')    

# Section 7: Structural System Factors
st.write('### 7. Structural System Factors')
col1, col2, col3 = st.columns(3)
with col1:
    R = st.number_input(label='Response Modification Factor, $R$', min_value=0.0, value=8.0, key='R')
with col2:
    omega0 = st.number_input(label='System Overstrength Factor, $\Omega_0$', min_value=0.0, value=3.0, key='omega0')
with col3:
    Cd = st.number_input(label='Deflection Amplification Factor, $C_d$', min_value=0.0, value=5.5, key='Cd')


# Create Expander
with st.expander("Table 2.3-1 Response Modification Factors and Additional Requirements", expanded=False):
    
    st.markdown("### Table 2.3-1 Response Modification Factor ($R$), System Overstrength Factor ($\\Omega_0$), and Deflection Amplification Factor ($C_d$)")
    
    # Create Tabs for better readability
    tab1, tab2, tab3 = st.tabs(["Categories 1 - 2", "Category 3", "Categories 4 - 7"])
    
    # Tab 1: Categories 1 and 2
    with tab1:
        st.markdown("""
| Basic Seismic-Force-Resisting System | Lateral Force-Resisting System | $R$ | $\\Omega_0$ | $C_d$ | B | C | D |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. Bearing Wall System** | Ordinary Reinforced Concrete Shear Wall | 4 | 2.5 | 4 | ✔️ | ✔️ | * |
| | Special Reinforced Concrete Shear Wall | 5 | 2.5 | 5 | ✔️ | ✔️ | ✔️ |
| | Ordinary Precast Shear Wall ++ | 3 | 2.5 | 3 | ✔️ | ❌ | ❌ |
| | Intermediate Precast Shear Wall ++ | 4 | 2.5 | 4 | ✔️ | ✔️ | ❌ |
| **2. Building Frame System** | Steel Eccentrically Braced Frame with Moment-Resisting Connections | 8 | 2 | 4 | ✔️ | ✔️ | ✔️ |
| | Steel Eccentrically Braced Frame with Non-Moment-Resisting Connections | 7 | 2 | 4 | ✔️ | ✔️ | ✔️ |
| | Special Steel Concentric Braced Frame | 6 | 2 | 5 | ✔️ | ✔️ | ✔️ |
| | Ordinary Steel Concentric Braced Frame | 3.5 | 2 | 3.5 | ✔️ | ✔️ | ❌ |
| | Special Reinforced Concrete Shear Wall | 6 | 2.5 | 5 | ✔️ | ✔️ | ✔️ |
| | Ordinary Reinforced Concrete Shear Wall | 5 | 2.5 | 4.5 | ✔️ | ✔️ | * |
| | Ordinary Precast Shear Wall ++ | 4 | 2.5 | 4 | ✔️ | ❌ | ❌ |
| | Intermediate Precast Shear Wall ++ | 5 | 2.5 | 4.5 | ✔️ | ✔️ | ❌ |
        """)

    # Tab 2: Category 3
    with tab2:
        st.markdown("""
| Basic Seismic-Force-Resisting System | Lateral Force-Resisting System | $R$ | $\\Omega_0$ | $C_d$ | B | C | D |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **3. Moment Resisting Frame** | Ductile/Special Steel Moment-Resisting Frame | 8 | 3 | 5.5 | ✔️ | ✔️ | ✔️ |
| | Special Truss Moment Frame | 7 | 3 | 5.5 | ✔️ | ✔️ | ✔️ |
| | Intermediate Steel Moment Resisting Frame | 4.5 | 3 | 4 | ✔️ | ✔️ | * |
| | Ordinary Steel Moment Resisting Frame | 3.5 | 3 | 3 | ✔️ | ✔️ | ❌ |
| | Precast or Cast-in-Place Ductile/Special Reinforced Concrete Moment Resisting Frame ++ | 8 | 3 | 5.5 | ✔️ | ✔️ | ✔️ |
| | Ductile RC Moment-Resisting Frame with Limited Ductility/ Intermediate RC Moment-Resisting Frame | 5 | 3 | 4.5 | ✔️ | ✔️ | * |
| | Ordinary Reinforced Concrete Moment Resisting Frame | 3 | 3 | 2.5 | ✔️ | ❌ | ❌ |
        """)

    # Tab 3: Categories 4 to 7
    with tab3:
        st.markdown("""
| Basic Seismic-Force-Resisting System | Lateral Force-Resisting System | $R$ | $\\Omega_0$ | $C_d$ | B | C | D |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **4. Dual System with Ductile/Special Moment Resisting Frame** *(capable of resisting at least 25% of prescribed seismic forces)* | Special Steel Concentrically Braced Frame | 7 | 2.5 | 5.5 | ✔️ | ✔️ | ✔️ |
| | Steel Eccentrically Braced Frame | 8 | 2.5 | 4 | ✔️ | ✔️ | ✔️ |
| | Special Reinforced Concrete Shear Wall | 7 | 2.5 | 5.5 | ✔️ | ✔️ | ✔️ |
| | Ordinary Reinforced Concrete Shear Wall | 6 | 2.5 | 5 | ✔️ | ✔️ | * |
| **5. Dual System with Moment Resisting Frame with Limited Ductility / Dual System with Intermediate Moment Resisting Frame** *(capable of resisting at least 25% of prescribed seismic forces)* | Special Steel Concentrically Braced Frame | 6 | 2.5 | 5 | ✔️ | ✔️ | ❌ |
| | Special Reinforced Concrete Shear Wall | 6.5 | 2.5 | 5 | ✔️ | ✔️ | ✔️ |
| | Ordinary Reinforced Concrete Shear Wall | 5.5 | 2.5 | 4.5 | ✔️ | ✔️ | * |
| **6. Shear Wall Frame Interactive System** | Shear Wall Frame Interactive System with Ordinary Reinforced Concrete Moment Frame and Ordinary Concrete Shear Wall | 4.5 | 2.5 | 4 | ✔️ | ❌ | ❌ |
| **7. Steel Systems Not Specifically Detailed for Seismic Resistance** | Steel Systems Not Specifically Detailed for Seismic Resistance | 3 | 3 | 3 | ✔️ | ✔️ | ❌ |
        """)
        
    # Footnotes
    st.caption("**Note:** ✔️ = Permitted, ❌ = Not Permitted, **\*** = See Section 2.3.1.2, **++** = See Section 2.3.1.3")
    st.caption("*(Note: Columns B, C, D refer to Seismic Design Categories ข, ค, ง respectively)*")

    st.divider() 
    
    # Height Limitations Text
    st.markdown("""
    #### 2.3.1.2 Height Limitations for Seismic Design Category D

    Lateral force-resisting systems comprising Ordinary Reinforced Concrete Shear Walls, Intermediate/Limited Ductility RC Moment Frames, or Intermediate Steel Moment Frames for Seismic Design Category D are permitted for buildings not exceeding the following heights:
    
    1. **40 meters** for Intermediate/Limited Ductility RC Moment Frames and Intermediate Steel Moment Frames.
    2. **60 meters** for Ordinary Reinforced Concrete Shear Walls.
    
    Additionally, when calculating design strength, the seismic forces used for designing the structural members shall be increased by **40%**. For deformation calculation purposes, it is not necessary to increase the calculated seismic forces.
    
    In cases where the building height exceeds the specified limits, a limit state check (e.g., concrete and steel strain, shear, etc.) of structural members must be performed to ensure they are within acceptable criteria for the level of detailing used, under both the design earthquake and the maximum considered earthquake. Such checks must utilize methodologies and values accepted in structural engineering practice or be supported by test results confirming the members' performance.
    """)

# # สร้าง Expander
# with st.expander("ตารางที่ 2.3-1 ค่าตัวประกอบปรับผลตอบสนองและข้อกำหนดเพิ่มเติม", expanded=False):
    
#     st.markdown("### ตารางที่ 2.3-1 ค่าตัวประกอบปรับผลตอบสนอง ($R$) ตัวประกอบกำลังส่วนเกิน ($\\Omega_0$) และ ตัวประกอบขยายค่าการโก่งตัว ($C_d$)")
    
#     # สร้าง Tabs เพื่อแบ่งหมวดหมู่ให้อ่านง่ายขึ้น
#     tab1, tab2, tab3 = st.tabs(["หมวด 1 - 2", "หมวด 3", "หมวด 4 - 7"])
    
#     # แท็บที่ 1: หมวด 1 และ 2
#     with tab1:
#         st.markdown("""
# | ระบบโครงสร้างโดยรวม | ระบบต้านแรงด้านข้าง | $R$ | $\\Omega_0$ | $C_d$ | ข | ค | ง |
# |---|---|:---:|:---:|:---:|:---:|:---:|:---:|
# | **1. ระบบกำแพงรับน้ำหนักบรรทุกแนวดิ่ง**<br>*(Bearing Wall System)* | กำแพงรับแรงเฉือนแบบธรรมดา (Ordinary Reinforced Concrete Shear Wall) | 4 | 2.5 | 4 | ✔️ | ✔️ | * |
# | | กำแพงรับแรงเฉือนแบบที่มีการให้รายละเอียดพิเศษ (Special Reinforced Concrete Shear Wall) | 5 | 2.5 | 5 | ✔️ | ✔️ | ✔️ |
# | | กำแพงรับแรงเฉือนหล่อสำเร็จแบบธรรมดา (Ordinary Precast Shear Wall) ++ | 3 | 2.5 | 3 | ✔️ | ❌ | ❌ |
# | | กำแพงรับแรงเฉือนหล่อสำเร็จแบบที่มีการให้รายละเอียดความเหนียวปานกลาง (Intermediate Precast Shear Wall) ++ | 4 | 2.5 | 4 | ✔️ | ✔️ | ❌ |
# | **2. ระบบโครงอาคาร**<br>*(Building Frame System)* | โครงแกงแนงเหล็กแบบเยื้องศูนย์ที่ใช้จุดต่อแบบรับแรงดัดได้ (Steel Eccentrically Braced Frame with Moment-Resisting Connections) | 8 | 2 | 4 | ✔️ | ✔️ | ✔️ |
# | | โครงแกงแนงเหล็กแบบเยื้องศูนย์ที่ใช้จุดต่อแบบรับแรงเฉือน (Steel Eccentrically Braced Frame with Non-Moment-Resisting Connections) | 7 | 2 | 4 | ✔️ | ✔️ | ✔️ |
# | | โครงแกงแนงเหล็กแบบตรงศูนย์แบบให้รายละเอียดพิเศษ (Special Steel Concentric Braced Frame) | 6 | 2 | 5 | ✔️ | ✔️ | ✔️ |
# | | โครงแกงแนงเหล็กแบบตรงศูนย์แบบธรรมดา (Ordinary Steel Concentric Braced Frame) | 3.5 | 2 | 3.5 | ✔️ | ✔️ | ❌ |
# | | กำแพงรับแรงเฉือนแบบที่มีการให้รายละเอียดพิเศษ (Special Reinforced Concrete Shear Wall) | 6 | 2.5 | 5 | ✔️ | ✔️ | ✔️ |
# | | กำแพงรับแรงเฉือนแบบธรรมดา (Ordinary Reinforced Concrete Shear Wall) | 5 | 2.5 | 4.5 | ✔️ | ✔️ | * |
# | | กำแพงรับแรงเฉือนหล่อสำเร็จแบบธรรมดา (Ordinary Precast Shear Wall) ++ | 4 | 2.5 | 4 | ✔️ | ❌ | ❌ |
# | | กำแพงรับแรงเฉือนหล่อสำเร็จแบบที่มีการให้รายละเอียดความเหนียวปานกลาง (Intermediate Precast Shear Wall) ++ | 5 | 2.5 | 4.5 | ✔️ | ✔️ | ❌ |
#         """)

#     # แท็บที่ 2: หมวด 3
#     with tab2:
#         st.markdown("""
# | ระบบโครงสร้างโดยรวม | ระบบต้านแรงด้านข้าง | $R$ | $\\Omega_0$ | $C_d$ | ข | ค | ง |
# |---|---|:---:|:---:|:---:|:---:|:---:|:---:|
# | **3. ระบบโครงต้านแรงดัด**<br>*(Moment Resisting Frame)* | โครงต้านแรงดัดเหล็กที่มีความเหนียวพิเศษ (Ductile/Special Steel Moment-Resisting Frame) | 8 | 3 | 5.5 | ✔️ | ✔️ | ✔️ |
# | | โครงถักต้านแรงดัดที่มีการให้รายละเอียดความเหนียวเป็นพิเศษ (Special Truss Moment Frame) | 7 | 3 | 5.5 | ✔️ | ✔️ | ✔️ |
# | | โครงต้านแรงดัดเหล็กที่มีความเหนียวปานกลาง (Intermediate Steel Moment Resisting Frame) | 4.5 | 3 | 4 | ✔️ | ✔️ | * |
# | | โครงต้านแรงดัดเหล็กธรรมดา (Ordinary Steel Moment Resisting Frame) | 3.5 | 3 | 3 | ✔️ | ✔️ | ❌ |
# | | โครงต้านแรงดัดคอนกรีตเสริมเหล็กที่มีความเหนียวพิเศษ (แบบหล่อในที่ หรือ แบบหล่อสำเร็จ) (Precast or Cast-in-Place Ductile/Special Reinforced Concrete Moment Resisting Frame) ++ | 8 | 3 | 5.5 | ✔️ | ✔️ | ✔️ |
# | | โครงต้านแรงดัดคอนกรีตเสริมเหล็กที่มีความเหนียวปานกลางหรือความเหนียวจำกัด (Ductile RC Moment-Resisting Frame with Limited Ductility/ Intermediate RC Moment-Resisting Frame) | 5 | 3 | 4.5 | ✔️ | ✔️ | * |
# | | โครงต้านแรงดัดคอนกรีตเสริมเหล็กแบบธรรมดา (Ordinary Reinforced Concrete Moment Resisting Frame) | 3 | 3 | 2.5 | ✔️ | ❌ | ❌ |
#         """)

#     # แท็บที่ 3: หมวด 4 ถึง 7
#     with tab3:
#         st.markdown("""
# | ระบบโครงสร้างโดยรวม | ระบบต้านแรงด้านข้าง | $R$ | $\\Omega_0$ | $C_d$ | ข | ค | ง |
# |---|---|:---:|:---:|:---:|:---:|:---:|:---:|
# | **4. ระบบโครงสร้างแบบผสมที่มีโครงต้านแรงดัดที่มีความเหนียวที่สามารถต้านทานแรงด้านข้างไม่น้อยกว่าร้อยละ 25 ของแรงที่กระทำกับอาคารทั้งหมด**<br>*(Dual System with Ductile/Special Moment Resisting Frame)* | ร่วมกับโครงแกงแนงเหล็กแบบตรงศูนย์แบบพิเศษ (Special Steel Concentrically Braced Frame) | 7 | 2.5 | 5.5 | ✔️ | ✔️ | ✔️ |
# | | ร่วมกับโครงแกงแนงเหล็กแบบเยื้องศูนย์ (Steel Eccentrically Braced Frame) | 8 | 2.5 | 4 | ✔️ | ✔️ | ✔️ |
# | | ร่วมกับกำแพงรับแรงเฉือนแบบที่มีการให้รายละเอียดพิเศษ (Special Reinforced Concrete Shear Wall) | 7 | 2.5 | 5.5 | ✔️ | ✔️ | ✔️ |
# | | ร่วมกับกำแพงรับแรงเฉือนแบบธรรมดา (Ordinary Reinforced Concrete Shear Wall) | 6 | 2.5 | 5 | ✔️ | ✔️ | * |
# | **5. ระบบโครงสร้างแบบผสมที่มีโครงต้านแรงดัดที่มีความเหนียวปานกลางหรือความเหนียวจำกัดที่สามารถต้านทานแรงด้านข้างไม่น้อยกว่าร้อยละ 25 ของแรงที่กระทำกับอาคารทั้งหมด**<br>*(Dual System with Moment Resisting Frame with Limited Ductility / Dual System with Intermediate Moment Resisting Frame)* | ร่วมกับโครงแกงแนงเหล็กแบบตรงศูนย์แบบพิเศษ (Special Steel Concentrically Braced Frame) | 6 | 2.5 | 5 | ✔️ | ✔️ | ❌ |
# | | ร่วมกับกำแพงรับแรงเฉือนแบบที่มีการให้รายละเอียดพิเศษ (Special Reinforced Concrete Shear Wall) | 6.5 | 2.5 | 5 | ✔️ | ✔️ | ✔️ |
# | | ร่วมกับกำแพงรับแรงเฉือนแบบธรรมดา (Ordinary Reinforced Concrete Shear Wall) | 5.5 | 2.5 | 4.5 | ✔️ | ✔️ | * |
# | **6. ระบบปฏิสัมพันธ์**<br>*(Shear Wall Frame Interactive System)* | ระบบปฏิสัมพันธ์ระหว่างกำแพงรับแรงเฉือนและโครงต้านแรงดัดแบบธรรมดาที่ไม่มีการให้รายละเอียดความเหนียว (Shear Wall Frame Interactive System with Ordinary Reinforced Concrete Moment Frame and Ordinary Concrete Shear Wall) | 4.5 | 2.5 | 4 | ✔️ | ❌ | ❌ |
# | **7. ระบบโครงสร้างเหล็กที่ไม่มีการให้รายละเอียดสำหรับรับแรงแผ่นดินไหว**<br>*(Steel Systems Not Specifically Detailed for Seismic Resistance)* | ระบบโครงสร้างเหล็กที่ไม่มีการให้รายละเอียดสำหรับรับแรงแผ่นดินไหว | 3 | 3 | 3 | ✔️ | ✔️ | ❌ |
#         """)
        
#     # เชิงอรรถ (อยู่นอก Tabs เพื่อให้แสดงผลตลอดเวลา)
#     st.caption("**หมายเหตุ:** ✔️ = ใช้ได้, ❌ = ห้ามใช้, **\*** = ดูหัวข้อ 2.3.1.2, **++** = ดูหัวข้อ 2.3.1.3")

#     st.divider() # ขีดเส้นคั่น
    
#     # ข้อกำหนดด้านความสูง (อยู่นอก Tabs เพื่อให้แสดงผลตลอดเวลา)
#     st.markdown("""
#     #### 2.3.1.2 ข้อกำหนดด้านความสูงสำหรับประเภทการออกแบบต้านทานการสั่นสะเทือนของแผ่นดินไหว ง

#     ระบบต้านแรงด้านข้างที่ประกอบด้วย กำแพงรับแรงเฉือนแบบธรรมดา โครงต้านแรงดัดคอนกรีตเสริมเหล็กที่มีความเหนียวปานกลางหรือความเหนียวจำกัด หรือ โครงต้านแรงดัดเหล็กที่มีความเหนียวปานกลาง สำหรับประเภทการออกแบบต้านทานการสั่นสะเทือนของแผ่นดินไหว ง สามารถใช้ได้กับอาคารที่มีความสูงไม่เกินค่าต่อไปนี้
    
#     1. **40 เมตร** สำหรับ โครงต้านแรงดัดคอนกรีตเสริมเหล็กที่มีความเหนียวปานกลางหรือความเหนียวจำกัด และ โครงต้านแรงดัดเหล็กที่มีความเหนียวปานกลาง  
#     2. **60 เมตร** สำหรับ กำแพงรับแรงเฉือนแบบธรรมดา  
    
#     ทั้งนี้ในการคำนวณออกแบบด้านกำลัง ให้เพิ่มค่าแรงแผ่นดินไหวที่ใช้ในการออกแบบองค์อาคารอีก **ร้อยละ 40** ในส่วนการคำนวณค่าการเสียรูป ไม่จำเป็นต้องเพิ่มค่าแรงที่ใช้ในการคำนวณ
    
#     ในกรณีที่อาคารมีความสูงมากกว่าที่กำหนด ต้องมีการตรวจสอบ ภาวะขีดสุด (Limit State) ค่าความเครียดของคอนกรีตและเหล็กเสริม แรงเฉือน ฯลฯ ขององค์อาคาร ว่ามีค่าอยู่ในเกณฑ์ที่ยอมรับได้สำหรับระดับการให้รายละเอียดขององค์อาคารที่ใช้ ภายใต้แผ่นดินไหวสำหรับออกแบบ และภายใต้แผ่นดินไหวรุนแรงสูงสุดที่พิจารณา ทั้งนี้การตรวจสอบดังกล่าวต้องใช้วิธีการและค่าต่าง ๆ เป็นไปตามวิธีและค่าที่เป็นที่ยอมรับในทางวิศวกรรม หรือมีผลทดสอบที่ยืนยันถึงสมรรถนะขององค์อาคาร
#     """)
st.write('---')

# Section 8: Design Response Spectrum
st.write('### 8. Design Response Spectrum Acceleration, $S_a$')

# if not bkk:
#     if cal == cal_list[0]: # Equivalent Static
#         if SD1 <= SDS:
#             T0, Ts = 0.0, SD1/SDS
#             T_data = np.append([T0,Ts], np.arange(round(Ts,1), 2.1, 0.1))
#             S_data = np.array([SDS, SDS])
#             for T in T_data:
#                 if T > Ts: S_data = np.append(S_data, [SD1/T])
#             Sa_structure = SDS if T_structure <= Ts else SD1/T_structure
#         else:
#             T0, Ts = 0.2, 1.0
#             T_data = np.append([0,T0,Ts], np.arange(1.1, 2.1, 0.1))
#             S_data = np.array([SDS, SDS, SD1])
#             for T in T_data:
#                 if T > Ts: S_data = np.append(S_data, [SD1/T])
#             if T_structure <= T0: Sa_structure = SDS
#             elif T_structure <= Ts:
#                 f = interpolate.interp1d([T0,Ts], [SDS,SD1]); Sa_structure = f(T_structure)
#             else: Sa_structure = SD1/T_structure

if not bkk:
    if cal == cal_list[0]: # Equivalent Static
        if SD1 <= SDS:
            T0, Ts = 0.0, SD1/SDS
            T_data = np.append([T0,Ts], np.arange(round(Ts,1), 10.1, 0.1))
            T_data = np.unique(np.sort(T_data)) # จัดการค่าซ้ำ
            
            # สร้าง S_data ให้ขนาดเท่า T_data ทันที ป้องกันขนาดไม่เท่ากัน
            S_data = np.zeros_like(T_data)
            for i, T in enumerate(T_data):
                if T <= Ts: 
                    S_data[i] = SDS
                else: 
                    S_data[i] = SD1/T
                    
            Sa_structure = SDS if T_structure <= Ts else SD1/T_structure
            
        else: # กรณี SD1 > SDS
            T0, Ts = 0.2, 1.0
            T_data = np.append([0,T0,Ts], np.arange(1.1, 10.1, 0.1))
            T_data = np.unique(np.sort(T_data))
            
            S_data = np.zeros_like(T_data)
            for i, T in enumerate(T_data):
                if T <= T0: 
                    S_data[i] = SDS
                elif T <= Ts:
                    f = interpolate.interp1d([T0,Ts], [SDS,SD1])
                    S_data[i] = f(T)
                else: 
                    S_data[i] = SD1/T
                    
            if T_structure <= T0: Sa_structure = SDS
            elif T_structure <= Ts:
                f = interpolate.interp1d([T0,Ts], [SDS,SD1]); Sa_structure = f(T_structure)
            else: Sa_structure = SD1/T_structure
                    
    elif cal == cal_list[1]: # Dynamic
        if SD1 <= SDS:
            T0, Ts = 0.2*SD1/SDS, SD1/SDS
            T_data = np.append([0, T0, Ts], np.arange(round(Ts, 1) + 0.1, 10.1, 0.1))
            T_data = np.unique(np.sort(T_data)) 
            
            S_data = np.zeros_like(T_data)
            for i, T in enumerate(T_data):
                if T <= T0: S_data[i] = 0.4*SDS + (SDS - 0.4*SDS) * (T/T0)
                elif T <= Ts: S_data[i] = SDS
                else: S_data[i] = SD1/T
                
            if T_structure <= T0:
                f = interpolate.interp1d([0.0, T0], [0.4*SDS, SDS]); Sa_structure = f(T_structure)
            elif T_structure <= Ts: Sa_structure = SDS
            else: Sa_structure = SD1/T_structure
        
        else: # SD1 > SDS
            T0, Ts = 0.2, 1.0
            T_data = np.append([0, T0, Ts], np.arange(1.1, 10.1, 0.1))
            T_data = np.unique(np.sort(T_data))
            
            S_data = np.zeros_like(T_data)
            for i, T in enumerate(T_data):
                if T <= T0: S_data[i] = 0.4*SDS + (SDS - 0.4*SDS) * (T/T0)
                elif T <= Ts: 
                    f_interp = interpolate.interp1d([T0, Ts], [SDS, SD1])
                    S_data[i] = f_interp(T)
                else: S_data[i] = SD1/T
                
            if T_structure <= T0:
                f = interpolate.interp1d([0.0, T0], [0.4*SDS, SDS]); Sa_structure = f(T_structure)
            elif T_structure <= Ts:
                f = interpolate.interp1d([T0, Ts], [SDS, SD1]); Sa_structure = f(T_structure)
            else: Sa_structure = SD1/T_structure

if not bkk and damping == '2.5%':
    for i in range(len(T_data)):
        if T_data[i] >= T0: 
            S_data[i] /= 0.85
        else: 
            S_data[i] = SDS * (3.88 * T_data[i] / Ts + 0.4)
    
    Sa_structure = Sa_structure/0.85 if T_structure >= T0 else SDS*(3.88*T_structure/Ts + 0.4)
    
elif bkk:
    T_data = df_bkk.loc[df_bkk['zone']==zone, 'T'].values
    S_data = df_bkk.loc[df_bkk['zone']==zone, 'Sa'].values
    y0 = df_bkk.loc[(df_bkk['zone']==zone) & (df_bkk['T']<=T_structure), :].iloc[-1]['Sa']
    y1 = df_bkk.loc[(df_bkk['zone']==zone) & (df_bkk['T']>=T_structure), :].iloc[0]['Sa']
    x0 = df_bkk.loc[(df_bkk['zone']==zone) & (df_bkk['T']<=T_structure), :].iloc[-1]['T']
    x1 = df_bkk.loc[(df_bkk['zone']==zone) & (df_bkk['T']>=T_structure), :].iloc[0]['T']
    
    # ป้องกัน error หาก T_structure ตรงกับค่าพิกัดพอดี
    if x0 == x1: 
        Sa_structure = y0
    else:
        f = interpolate.interp1d([np.log10(x0), np.log10(x1)], [np.log10(y0), np.log10(y1)])
        Sa_structure = 10**f([np.log10(T_structure)])[0]

# --- แก้ไขฟังก์ชันพล็อตให้รับค่า Parameter เข้าไปโดยตรง ---
def response_spectrum_plot(T_data, S_data, t_struct, sa_struct, is_bkk):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=T_data, y=S_data, mode='lines', line=dict(color='blue', width=2), showlegend=False, hoverinfo='skip'))
    #fig.add_trace(go.Scatter(x=T_data, y=S_data, mode='lines+markers', line=dict(color='blue', width=2), showlegend=False, hoverinfo='skip'))
    
    fig.add_trace(go.Scatter(x=[min(T_data), t_struct], y=[sa_struct, sa_struct], mode='lines', line=dict(dash='dash', width=3, color='red'), hoverinfo='skip', showlegend=False))
    
    ann_x = np.log10(min(T_data)) if is_bkk else min(T_data)
    fig.add_annotation(x=ann_x, y=sa_struct, text=r'%.3f'%(sa_struct), xanchor="left", yanchor="bottom", font=dict(color="red", size=16), showarrow=False)
    
    fig.add_trace(go.Scatter(x=[t_struct, t_struct], y=[0.0, sa_struct], mode='lines', line=dict(dash='dash', width=3, color='red'), hoverinfo='skip', showlegend=False))
    
    ann_tx = np.log10(t_struct) if is_bkk else t_struct
    ann_ty = np.log10(0.01) if is_bkk else 0.0
    fig.add_annotation(x=ann_tx, y=ann_ty, text=r'%.3f'%(t_struct), xanchor="left", yanchor="bottom", font=dict(color="red", size=16), showarrow=False)
    
    fig.add_trace(go.Scatter(x=[t_struct], y=[sa_struct], mode='markers', marker=dict(color='red', size=8), showlegend=False, hoverinfo='skip'))
    
    fig.update_layout(
        xaxis=dict(title='T (second)', fixedrange=True, range=[0.0, 10.0], rangemode="nonnegative"),
        yaxis=dict(title='Sa (g)', fixedrange=True, range=[0.0, max(S_data)+0.05], rangemode="nonnegative"),
        margin=dict(t=20, b=40), height=300
    )
    if is_bkk:
        fig.update_xaxes(range=[np.log10(0.01), np.log10(10)], type="log")
        fig.update_yaxes(range=[np.log10(0.01), np.log10(1)], type="log")
    return fig

col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.plotly_chart(response_spectrum_plot(T_data, S_data, T_structure, Sa_structure, bkk), theme=None, use_container_width=True)
    st.write(r'Period of structure, $T = %.3f \mathrm{~sec}$'%(T_structure))
    st.write(r'Acceleration of structure, $S_a = %.3f \mathrm{~g}$'%(Sa_structure))

st.write('---')

with st.expander("Show Seismic Design Calculations"):
# Section 9: Base Shear
    st.write('### 9. Base Shear, $V$')
    W = Witotal_list[-1] if len(Witotal_list) > 0 else 0
    st.markdown(rf'$Effective \text{{ Seismic }} \text{{ Weight, }} W = {W:.2f} \text{{ tonne}}$')

    st.write('**Seismic Response Coefficient, $C_s$**')
    Cs_ = Sa_structure * I / R
    Cs = max(Cs_, 0.01)

    st.markdown(r'$C_s = S_a \left( \frac{I}{R} \right) \qquad\qquad \ge \qquad 0.01$')
    st.markdown(r'$\quad\>\> = %.3f \left( \frac{%.2f}{%.2f} \right) \qquad\>\> \ge \qquad 0.01$'%(Sa_structure, I, R))
    st.markdown(r'$\quad\>\> = %.3f \qquad\qquad\quad \ge \qquad 0.01$'%(Cs_))
    st.markdown(r'$\quad\>\> = %.3f$'%(Cs))

    st.write('**Total Design Base Shear**')
    V = Cs * W
    st.markdown(r'$V = C_s W$')
    st.markdown(r'$\quad = %.3f \mathrm{~g} \times %.2f \mathrm{~tonne}$'%(Cs, W))
    st.markdown(r'$\quad = %.2f \mathrm{~tonne}$'%(V))

    st.write('---')

    # Section 10: Vertical Distribution
    st.write('### 10. Vertical Distribution of Seismic Forces')

    st.write('**Vertical Distribution Exponent ($k$)**')
    if T_structure <= 0.5:
        k = 1.0
        st.write(r'For $\qquad T \le 0.5 \mathrm{~sec}, \qquad k = 1.0$')
    elif T_structure >= 2.5:
        k = 2.0
        st.write(r'For $\qquad T \ge 2.5 \mathrm{~sec}, \qquad k = 2.0$')
    else:
        k = 1 + (T_structure-0.5)/2
        st.write(r'For $\qquad 0.5 \mathrm{~sec} < T < 2.5 \mathrm{~sec}, \qquad k = 1 + \frac{T-0.5}{2} = %.2f $'%(k))

    st.write('**Vertical Distribution Factor ($C_{vx}$)**')
    st.write(r'$C_{v x} = \frac{w_x h_x^k}{\sum_{i=1}^{n} w_i h_i^k}$')

    st.write('**Lateral Force at Each Level**')
    st.write(r'$F_x = C_{v x} V$')

    st.write('---')
    st.write(r'### $Lateral ~ Force ~ and ~ Shear ~ Table$')

    # Table Calculation
    floors = pd.DataFrame({'Story': []})
    for i in range(Floor): floors.loc[i] = i+1

    eq = pd.DataFrame(floors)
    eq['Wx [tonne]'] = Weight_list
    eq['hx [m]'] = Floor_list 
    wihxk = eq['Wx [tonne]'] * (eq['hx [m]']**k)
    eq['Wxhx^k'] = wihxk
    eq['Cvx'] = wihxk / wihxk.sum()
    eq['Fx [tonne]'] = eq['Cvx'] * V
    eq['Fx [tonne]'] = eq['Fx [tonne]'].round(2)
    eq = eq.sort_index(ascending=False)
    eq['Vx [tonne]'] = eq['Fx [tonne]'].cumsum()

    # Final Dataframe Display
    st.dataframe(eq, hide_index=True, use_container_width=True)