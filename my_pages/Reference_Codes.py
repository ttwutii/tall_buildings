import streamlit as st

def run():
    st.title("Reference Standards & Codes")
    st.markdown("The calculations in this application are strictly based on the following engineering standards and technical manuals.")
    st.divider()

    # --- Wind Loading Section ---
    st.header("Wind Loading Standards")
    
    with st.container(border=True):
        st.subheader("DPT Standard 1311-50")
        st.write("**Full Name:** Standard for Wind Load Calculations and Response of Structures")
        st.write("**Authority:** Department of Public Works and Town & Country Planning (DPT), Thailand")
        st.info("📌 **Application:** Used for calculating static equivalent wind pressure and gust effect factors for tall buildings.")

    # with st.container(border=True):
    #     st.subheader("ASCE 7-16 / 7-22")
    #     st.write("**Full Name:** Minimum Design Loads and Associated Criteria for Buildings and Other Structures")
    #     st.write("**Authority:** American Society of Civil Engineers (ASCE)")
    #     st.info("📌 **Application:** Referenced for fundamental aerodynamic coefficients ($C_p$) and wind tunnel procedure guidelines.")

    st.divider()

    # --- Earthquake Section ---
    st.header(" Seismic Design Standards")

    with st.container(border=True):
        st.subheader("DPT Standard 1301/1302-61")
        st.write("**Full Name:** Standard for Earthquake Resistant Design of Buildings")
        st.write("**Authority:** Department of Public Works and Town & Country Planning (DPT), Thailand")
        st.info("📌 **Application:** Used for Response Spectrum Analysis, seismic zone mapping, and importance factor definitions.")

        # --- Ministerial Regulation  Section ---
    st.header(" Ministerial Regulations")

    with st.container(border=True):
        st.subheader("Ministerial Regulation B.E. 2566 (2023)")
        st.write("**Full Name:** Ministerial Regulation Prescribing the Weight, Resistance, Durability of Buildings, and the Ground Supporting Buildings for Earthquake Resistance, B.E. 2566.")
        st.write("**Authority:** Ministry of Interior (implemented by the Department of Public Works and Town & Country Planning - DPT)")
        st.info("📌 **Application:** This is the primary law that mandates seismic design across specific provinces in Thailand.")


    # --- Professional Disclaimer ---
    st.divider()
    st.warning("""
    **Professional Disclaimer:** This application is intended to assist structural engineers in preliminary design and verification. 
    Users must cross-check all automated outputs with the original hard-copy standards before finalizing any structural design.
    """)

    # --- Optional: Download Section ---
    st.subheader("Related Documents")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🔗 Visit DPT Official Website", "https://www.dpt.go.th/th/dpt-standard/", use_container_width=True)
        st.link_button("📄 DPT Standard 1301/1302-61 (PDF)", "https://www.dpt.go.th/th/dpt-standard/854#wow-book/3", use_container_width=True)
        st.link_button("📄 DPT Standard 1311-50 (PDF)", "https://www.dpt.go.th/th/dpt-standard/789#wow-book/", use_container_width=True)
        st.link_button("📄 Ministerial Regulation B.E. 2566 (2023) (PDF)", "https://download.asa.or.th/03media/04law/cba/mr/mr66-70h.pdf", use_container_width=True)

if __name__ == "__main__":
    run()





# def run():
#     st.title("📚 Reference Documents & Standards")
#     st.write("เอกสารและมาตรฐานหลักที่ใช้ในการพัฒนาโปรแกรมคำนวณชุดนี้")
#     st.divider()

#     # --- หมวดแรงลม ---
#     st.header("🌪️ Wind Loading Standards")
    
#     with st.container(border=True):
#         st.subheader("มยผ. 1311-50")
#         st.write("**ชื่อเต็ม:** มาตรฐานการคำนวณแรงลมและการตอบสนองของโครงสร้าง")
#         st.write("**หน่วยงาน:** กรมโยธาธิการและผังเมือง (DPT)")
#         st.caption("ใช้สำหรับ: คำนวณ Static Equivalent Wind Pressure สำหรับอาคารสูง")

#     with st.container(border=True):
#         st.subheader("ASCE 7-16")
#         st.write("**ชื่อเต็ม:** Minimum Design Loads and Associated Criteria for Buildings and Other Structures")
#         st.write("**หน่วยงาน:** American Society of Civil Engineers (ASCE)")
#         st.caption("ใช้สำหรับ: อ้างอิงวิธีคำนวณกรณีอาคารที่มีรูปทรงไม่สมมาตร (Non-Symmetrical Shape)")

#     st.divider()

#     # --- หมวดแผ่นดินไหว ---
#     st.header("🫨 Earthquake Engineering Standards")

#     with st.container(border=True):
#         st.subheader("มยผ. 1301/1302-61")
#         st.write("**ชื่อเต็ม:** มาตรฐานการออกแบบอาคารต้านทานการสั่นสะเทือนของแผ่นดินไหว")
#         st.write("**หน่วยงาน:** กรมโยธาธิการและผังเมือง (DPT)")
#         st.caption("ใช้สำหรับ: กำหนดค่าความเร่งตอบสนอง (Response Spectrum) และการจำแนกประเภทอาคาร")

#     # --- ส่วนการแจ้งเตือน ---
#     st.warning("""
#     **หมายเหตุ:** การคำนวณในแอปพลิเคชันนี้เป็นการช่วยคำนวณเบื้องต้น 
#     วิศวกรผู้ใช้งานควรตรวจสอบผลลัพธ์กับเอกสารมาตรฐานฉบับจริงทุกครั้งก่อนนำไปใช้ในการออกแบบ
#     """)

# if __name__ == "__main__":
#     run()