import streamlit as st

# 1. กำหนดหน้าต่างๆ โดยชี้ไปที่ Path ของไฟล์ในโฟลเดอร์ views
home_page = st.Page("my_pages/Home.py", title="Home", icon="🏠")
ref_code_page = st.Page("my_pages/Reference_Codes.py", title="Reference Code", icon="📚")
load_combs = st.Page("my_pages/Load_Combs.py", title="Load Combinations", icon="⚖️")

#Eng_version
wind_tall_eng = st.Page("my_pages/Wind_For_Tall_Buildings_Eng_version.py", title="Wind Load - Tall Building ", icon="🏙️")
earthquake_eng = st.Page("my_pages/Earth_Quake_Eng_version.py", title="Earthquake Load", icon="🌍")

# 2. จัดกลุ่มเมนู (แก้ชื่อหมวดหมู่และเพิ่มหน้าได้ตามต้องการ)
pg = st.navigation(
    {
        "Main Menu": [home_page,ref_code_page, load_combs],
        "Loading for Tall Buildings": [wind_tall_eng, earthquake_eng]
        
    }
)

# 3. ตั้งค่าหน้าเว็บ (ส่วนนี้จะถูกใช้กับทุกหน้า)
st.set_page_config(page_title="Loading Design", layout="wide")

# 4. สั่งรันระบบเมนู
pg.run()