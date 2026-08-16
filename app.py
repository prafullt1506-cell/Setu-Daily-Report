import streamlit as st
import datetime
import pandas as pd
import io # हे एक्सेल फाईल बनवण्यासाठी लागेल

# १. ॲपची सेटिंग
st.set_page_config(page_title="स्मार्ट सेतू हिशोब", page_icon="🏛️", layout="centered")

# २. प्रीमियम डिझाईन आणि CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;800&family=Poppins:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Mukta', 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, var(--background-color) 0%, rgba(59, 130, 246, 0.05) 100%);
    }
    
    .main-title { font-size: 38px; font-weight: 800; text-align: center; margin-bottom: 5px; color: var(--text-color); }
    .sub-title { text-align: center; font-size: 16px; color: #6B7280; margin-bottom: 25px; font-weight: 600;}
    
    .grand-total-card { 
        background: linear-gradient(135deg, #10B981, #047857); 
        color: white; padding: 25px; border-radius: 15px; 
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3); 
        text-align: center; margin-top: 10px; margin-bottom: 20px;
    }
    .grand-total-text { font-size: 45px; font-weight: 800; margin: 0; line-height: 1.1; font-family: 'Poppins', sans-serif;}
    .grand-total-label { font-size: 18px; opacity: 0.9; margin-bottom: 5px; font-weight: 600; }
    
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# मुख्य टायटल
st.markdown('<div class="main-title">🏛️ स्मार्ट सेतू हिशोब</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">मोबाईल फ्रेंडली डॅशबोर्ड</div>', unsafe_allow_html=True)

# दोन मुख्य टॅब्स
tab1, tab2 = st.tabs(["📝 आजचा हिशोब भरा", "📊 अहवाल आणि रिपोर्ट"])

# =========================================================================
# टॅब १: आजचा हिशोब भरा 
# =========================================================================
with tab1:
    st.caption("माहिती भरण्यासाठी खालील फोल्डर्सवर क्लिक करा 🔽")
    
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
        affidavit_rs = st.number_input("एकूण प्रतिज्ञापत्रे", min_value=0, step=1) * 80

    with st.expander("📁 ३. रेशन कार्ड कामे [दर: ₹६९]"):
        ration_rs = (st.number_input("नाव कमी करणे", min_value=0, step=1) + st.number_input("नाव दाखल करणे", min_value=0, step=1)) * 69

    with st.expander("📁 ४. स्कॅनिंग [दर: ₹२ / पेज]"):
        scan_rs = st.number_input("एकूण स्कॅन केलेली पेजेस", min_value=0, step=1) * 2

    with st.expander("📁 ५. इतर किरकोळ कमाई"):
        itar = st.number_input("थेट एकूण रक्कम टाका (₹)", min_value=0, step=1)

    grand_total = mahsul_rs + affidavit_rs + ration_rs + scan_rs + itar

    st.markdown(f'''
    <div class="grand-total-card">
        <div class="grand-total-label">💰 आजची एकूण कमाई</div>
        <div class="grand-total-text">₹ {grand_total}</div>
    </div>
    ''', unsafe_allow_html=True)

    if st.button("💾 आजचा हिशोब सेव्ह करा", use_container_width=True, type="primary"):
        st.balloons()
        st.success("✅ रेकॉर्ड यशस्वीरित्या सेव्ह झाला!")

# =========================================================================
# टॅब २: अहवाल आणि विश्लेषण 
# =========================================================================
with tab2:
    st.markdown("### 🔍 अहवाल फिल्टर करा")
    
    period = st.radio("१. कालावधी निवडा:", ["एका दिवसाचा", "दोन तारखांमधील", "संपूर्ण महिन्याचा"], horizontal=True)
    
    if period == "एका दिवसाचा":
        st.date_input("तारीख निवडा:", datetime.date.today())
    elif period == "दोन तारखांमधील":
        st.date_input("सुरुवातीची आणि शेवटची तारीख निवडा:", [])
    elif period == "संपूर्ण महिन्याचा":
        col_m, col_y = st.columns(2)
        col_m.selectbox("महिना निवडा:", ["जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून", "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"])
        col_y.selectbox("वर्ष निवडा:", [2026, 2027, 2028])

    st.write("---")

    report_type = st.radio("२. रिपोर्ट प्रकार:", ["फक्त दाखल्यांची संख्या", "संपूर्ण हिशोब (रक्कमेसहित)"], horizontal=True)
    st.write("")
    
    # लॉजिक: फक्त दाखले निवडले तर स्कॅनिंग आणि इतर कमाई दिसणार नाही
    if report_type == "फक्त दाखल्यांची संख्या":
        demo_data = pd.DataFrame({
            "कामाचा प्रकार": ["उत्पन्नाचा दाखला", "जातीचा दाखला", "रेशन कार्ड", "प्रतिज्ञापत्र"], 
            "एकूण संख्या": [25, 15, 8, 10]
        })
    else:
        demo_data = pd.DataFrame({
            "कामाचा प्रकार": ["उत्पन्नाचा दाखला", "जातीचा दाखला", "रेशन कार्ड", "प्रतिज्ञापत्र", "स्कॅनिंग (पेजेस)", "इतर कमाई"], 
            "एकूण संख्या / पेजेस": [25, 15, 8, 10, 120, "-"], 
            "एकूण रक्कम (₹)": [2000, 1200, 552, 800, 240, 500]
        })

    # -------------------------------------------------------------------------
    # A4 Print Ready Excel फाईल बनवण्याची प्रोसेस (xlsxwriter)
    # -------------------------------------------------------------------------
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        demo_data.to_excel(writer, index=False, sheet_name='Report')
        
        workbook  = writer.book
        worksheet = writer.sheets['Report']
        
        # १. पेज A4 सेट करणे आणि मध्यभागी घेणे
        worksheet.set_paper(9) # 9 म्हणजे A4 साईझ
        worksheet.center_horizontally()
        
        # २. फॉन्ट आणि बॉर्डर डिझाईन (Header)
        header_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'font_name': 'Arial',
            'bg_color': '#D3D3D3', 'border': 1,
            'align': 'center', 'valign': 'vcenter'
        })
        
        # ३. सामान्य डेटाचे डिझाईन (Cell Data)
        cell_format = workbook.add_format({
            'font_size': 12, 'font_name': 'Arial',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        
        # कॉलम रुंदी (Width) वाढवणे जेणेकरून मजकूर लपणार नाही
        worksheet.set_column('A:A', 30, cell_format) # 'कामाचा प्रकार' कॉलम मोठा केला
        worksheet.set_column('B:C', 20, cell_format) # इतर कॉलम सेट केले
        
        # हेडरला फॉरमॅट लावणे
        for col_num, value in enumerate(demo_data.columns.values):
            worksheet.write(0, col_num, value, header_format)

    excel_data = output.getvalue()
    # -------------------------------------------------------------------------

    col_view, col_down = st.columns(2)
    
    with col_view:
        if st.button("👁️ रिपोर्ट पहा", type="primary", use_container_width=True):
            st.dataframe(demo_data, use_container_width=True) 
            
            if report_type == "संपूर्ण हिशोब (रक्कमेसहित)":
                st.info("💰 **या कालावधीतील एकूण कमाई: ₹ ५२९२**")

    with col_down:
        # आता थेट .xlsx फाईल डाउनलोड होईल
        st.download_button(
            label="📥 Excel (.xlsx) डाउनलोड",
            data=excel_data,
            file_name="Setu_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )