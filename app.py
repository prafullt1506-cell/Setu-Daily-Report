import streamlit as st
import pandas as pd
import datetime
import io
import json
import gspread

# ==========================================
# १. ॲपची सेटिंग आणि डिझाईन
# ==========================================
st.set_page_config(page_title="स्मार्ट सेतू हिशोब", page_icon="🏛️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;800&family=Poppins:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Mukta', 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(180deg, var(--background-color) 0%, rgba(59, 130, 246, 0.05) 100%); }
    .main-title { font-size: 38px; font-weight: 800; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .sub-title { text-align: center; font-size: 16px; color: #6B7280; margin-bottom: 25px; font-weight: 600;}
    .grand-total-card { background: linear-gradient(135deg, #10B981, #047857); color: white; padding: 25px; border-radius: 15px; text-align: center; margin-top: 10px; margin-bottom: 20px;}
    .grand-total-text { font-size: 45px; font-weight: 800; margin: 0; line-height: 1.1;}
    .grand-total-label { font-size: 18px; opacity: 0.9; margin-bottom: 5px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# २. गुगल शीट कनेक्शन (Database Setup)
# ==========================================
def connect_to_gsheet():
    try:
        creds_data = json.loads(st.secrets["google_credentials"])
        if isinstance(creds_data, list):
            creds_data = creds_data[0]
            
        gc = gspread.service_account_from_dict(creds_data)
        
        # ⚠️ तुमची गुगल शीटची लिंक
        sheet_url = "https://docs.google.com/spreadsheets/d/1CV9oR3fEs1zEtAjvN2jZ_z3wONW2ghKJ4pzsne9MK_0/edit?gid=0#gid=0" 
        
        sh = gc.open_by_url(sheet_url)
        return sh
        
    except Exception as e:
        st.error(f"⚠️ गुगल शीट कनेक्ट करताना एरर आला. Secrets तपासा. Error: {e}")
        st.stop()

def init_db(sh):
    try:
        hishob_ws = sh.worksheet("Hishob")
    except gspread.WorksheetNotFound:
        hishob_ws = sh.add_worksheet(title="Hishob", rows="1000", cols="20")
        headers = ["तारीख", "युजर", "उत्पन्नाचा", "वय/अधिवास", "अल्पभूधारक", "जातीचा", "EWS", 
                   "वारसा", "नॉन-क्रिमीलेअर", "ज्येष्ठ नागरिक", "डोंगरी", "रहिवासी", "शेतकरी", 
                   "संजय गांधी", "प्रतिज्ञापत्रे", "रेशन नाव कमी", "रेशन नाव दाखल", "स्कॅन पेजेस", "इतर कमाई", "एकूण रक्कम"]
        hishob_ws.append_row(headers)
    
    return hishob_ws

# ==========================================
# ३. सिक्युरिटी सिस्टीम (Username & Password Login)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

st.markdown('<div class="main-title">🏛️ स्मार्ट सेतू हिशोब</div>', unsafe_allow_html=True)

# 🔒 इथे तुम्ही ग्राहकांचे Username (ID) आणि त्यांचे Password (PIN) सेट करून ठेवू शकता!
AUTHORIZED_USERS = {
    "setuknk": "1122",
    
}

# --- लॉगिन स्क्रीन ---
if not st.session_state["logged_in"]:
    st.markdown('<div class="sub-title">सुरक्षित लॉगिन (Secure Login)</div>', unsafe_allow_html=True)
    
    with st.container():
        # आता ईमेल ऐवजी युझरनेम (Username) विचारेल
        login_username = st.text_input("तुमचा युझरनेम किंवा ID टाका:")
        login_password = st.text_input("तुमचा पासवर्ड किंवा PIN टाका:", type="password")
        
        if st.button("लॉगिन करा (Login)", type="primary", use_container_width=True):
            # Username डिक्शनरीमध्ये आहे का आणि Password मॅच होतोय का हे चेक करणे
            if login_username in AUTHORIZED_USERS and AUTHORIZED_USERS[login_username] == login_password:
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = login_username
                st.rerun()
            else:
                st.error("❌ चुकीचा युझरनेम किंवा पासवर्ड! प्रवेश नाकारला.")

# ==========================================
# ४. मुख्य हिशोब ॲप (लॉगिन झाल्यानंतर)
# ==========================================
if st.session_state["logged_in"]:
    st.markdown(f'<div class="sub-title">स्वागत आहे! ({st.session_state["current_user"]})</div>', unsafe_allow_html=True)
    
    if st.button("🚪 लॉग आउट करा (Logout)"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.rerun()

    tab1, tab2 = st.tabs(["📝 आजचा हिशोब भरा", "📊 अहवाल आणि रिपोर्ट"])
    
    sh = connect_to_gsheet()
    hishob_ws = init_db(sh)

    # --- टॅब १: हिशोब भरणे ---
    with tab1:
        date_today = st.date_input("तारीख निवडा:", datetime.date.today())
        
        with st.expander("📁 १. सर्व महसूल व इतर दाखले (दर: ₹८०)", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                v1 = st.number_input("उत्पन्नाचा दाखला", min_value=0, step=1)
                v2 = st.number_input("वय, राष्ट्रीयत्व, अधिवास", min_value=0, step=1)
                v3 = st.number_input("अल्पभूधारक / भूमिहीन", min_value=0, step=1)
                v4 = st.number_input("जातीचा दाखला", min_value=0, step=1)
                v5 = st.number_input("EWS प्रमाणपत्र", min_value=0, step=1)
                v6 = st.number_input("वारसा दाखला", min_value=0, step=1)
            with c2:
                v7 = st.number_input("नॉन-क्रिमीलेअर", min_value=0, step=1)
                v8 = st.number_input("ज्येष्ठ नागरिक प्रमाणपत्र", min_value=0, step=1)
                v9 = st.number_input("डोंगरी दाखला", min_value=0, step=1)
                v10 = st.number_input("रहिवासी दाखला", min_value=0, step=1)
                v11 = st.number_input("शेतकरी दाखला", min_value=0, step=1)
                v12 = st.number_input("संजय गांधी पेन्शन", min_value=0, step=1)
            
            mahsul_rs = (v1+v2+v3+v4+v5+v6+v7+v8+v9+v10+v11+v12) * 80

        with st.expander("📁 २. प्रतिज्ञापत्र (Affidavit) [दर: ₹८०]"):
            v13 = st.number_input("एकूण प्रतिज्ञापत्रे", min_value=0, step=1)
            affidavit_rs = v13 * 80

        with st.expander("📁 ३. रेशन कार्ड कामे [दर: ₹६९]"):
            v14 = st.number_input("नाव कमी करणे", min_value=0, step=1)
            v15 = st.number_input("नाव दाखल करणे", min_value=0, step=1)
            ration_rs = (v14 + v15) * 69

        with st.expander("📁 ४. स्कॅनिंग [दर: ₹२ / पेज]"):
            v16 = st.number_input("एकूण स्कॅन केलेली पेजेस", min_value=0, step=1)
            scan_rs = v16 * 2

        with st.expander("📁 ५. इतर किरकोळ कमाई"):
            v17 = st.number_input("थेट एकूण रक्कम टाका (₹)", min_value=0, step=1)

        grand_total = mahsul_rs + affidavit_rs + ration_rs + scan_rs + v17

        st.markdown(f'''
        <div class="grand-total-card">
            <div class="grand-total-label">💰 आजची एकूण कमाई</div>
            <div class="grand-total-text">₹ {grand_total}</div>
        </div>
        ''', unsafe_allow_html=True)

        if st.button("💾 हिशोब गुगल शीटमध्ये सेव्ह करा", use_container_width=True, type="primary"):
            row_data = [
                str(date_today), st.session_state["current_user"], 
                v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, 
                v13, v14, v15, v16, v17, grand_total
            ]
            hishob_ws.append_row(row_data)
            st.balloons()
            st.success("✅ रेकॉर्ड गुगल शीटमध्ये यशस्वीरित्या सेव्ह झाला!")

    # --- टॅब २: रिपोर्टिंग आणि एक्सेल डाउनलोड ---
    with tab2:
        st.markdown("### 🔍 अहवाल फिल्टर करा")
        
        all_data = hishob_ws.get_all_records()
        df = pd.DataFrame(all_data)
        
        if not df.empty:
            df['तारीख'] = pd.to_datetime(df['तारीख'])
            
            period = st.radio("१. कालावधी निवडा:", ["सर्व डेटा", "विशिष्ट तारीख"], horizontal=True)
            if period == "विशिष्ट तारीख":
                sel_date = st.date_input("तारीख निवडा:")
                df = df[df['तारीख'].dt.date == sel_date]
            
            df['तारीख'] = df['तारीख'].dt.strftime('%Y-%m-%d')
            
            report_type = st.radio("२. रिपोर्ट प्रकार:", ["फक्त दाखल्यांची संख्या", "संपूर्ण हिशोब (रक्कमेसहित)"], horizontal=True)
            
            if report_type == "फक्त दाखल्यांची संख्या":
                cols_to_drop = ["स्कॅन पेजेस", "इतर कमाई", "एकूण रक्कम", "युजर"]
                df_report = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
            else:
                df_report = df.copy()

            total_kamai = df['एकूण रक्कम'].sum() if 'एकूण रक्कम' in df.columns else 0

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_report.to_excel(writer, index=False, sheet_name='Report')
                workbook = writer.book
                worksheet = writer.sheets['Report']
                worksheet.set_paper(9)
                worksheet.center_horizontally()
                
                header_format = workbook.add_format({'bold': True, 'font_size': 12, 'font_name': 'Arial', 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
                cell_format = workbook.add_format({'font_size': 11, 'font_name': 'Arial', 'border': 1, 'align': 'center'})
                
                worksheet.set_column('A:Z', 15, cell_format)
                for col_num, value in enumerate(df_report.columns.values):
                    worksheet.write(0, col_num, value, header_format)

            excel_data = output.getvalue()

            col_v, col_d = st.columns(2)
            with col_v:
                if st.button("👁️ रिपोर्ट पहा", type="primary", use_container_width=True):
                    st.dataframe(df_report, use_container_width=True)
                    if report_type == "संपूर्ण हिशोब (रक्कमेसहित)":
                        st.info(f"💰 **या कालावधीतील एकूण कमाई: ₹ {total_kamai}**")
            with col_d:
                st.download_button(label="📥 Excel (.xlsx) डाउनलोड", data=excel_data, file_name="Smart_Setu_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.warning("कोणताही डेटा उपलब्ध नाही. आधी हिशोब भरा!")
