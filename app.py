import streamlit as st
import pandas as pd
import datetime
import io
import json
import gspread
import altair as alt

# ==========================================
# १. ॲपची सेटिंग आणि ॲडव्हान्स डिझाईन (Premium UI)
# ==========================================
st.set_page_config(page_title="स्मार्ट सेतू हिशोब", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;800&family=Poppins:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Mukta', 'Poppins', sans-serif; }
    
    .main-title { font-size: 38px; font-weight: 800; text-align: center; margin-bottom: 5px; color: #1e3a8a; }
    .sub-title { text-align: center; font-size: 16px; color: #475569; margin-bottom: 25px; font-weight: 600; }
    
    .grand-total-card { 
        background: linear-gradient(135deg, #059669, #047857); 
        color: white; padding: 25px; border-radius: 16px; text-align: center; 
        margin-top: 15px; margin-bottom: 20px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .grand-total-text { font-size: 45px; font-weight: 800; margin: 0; line-height: 1.1;}
    .grand-total-label { font-size: 18px; opacity: 0.95; margin-bottom: 5px; font-weight: 600; }

    /* Report Table Styling */
    .report-table { width: 100%; border-collapse: collapse; margin-top: 5px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .report-table th { background-color: #1e3a8a; color: white; padding: 12px; text-align: left; font-size: 16px; }
    .report-table td { padding: 12px; border-bottom: 1px solid #e2e8f0; color: #334155; font-size: 15px; font-weight: 600;}
    .report-table tr:last-child td { border-bottom: none; }
    .report-total-row { background-color: #f1f5f9; font-weight: 800 !important; color: #0f172a !important; font-size: 18px !important; }
    
    /* 🔥 नवीन: ग्राफ खाली आडवा स्लायडर आणण्यासाठी */
    .scrollable-chart {
        overflow-x: auto;
        white-space: nowrap;
        width: 100%;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# २. गुगल शीट कनेक्शन आणि सुपरफास्ट कॅशिंग
# ==========================================
def connect_to_gsheet():
    try:
        creds_data = json.loads(st.secrets["google_credentials"])
        if isinstance(creds_data, list):
            creds_data = creds_data[0]
            
        gc = gspread.service_account_from_dict(creds_data)
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

@st.cache_data(show_spinner=False, ttl=10)
def fetch_all_records(_ws):
    return _ws.get_all_records()

# ==========================================
# ३. सिक्युरिटी आणि स्टेट मॅनेजमेंट
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

if "form_key" not in st.session_state:
    st.session_state["form_key"] = 0
if "force_clear" not in st.session_state:
    st.session_state["force_clear"] = False
if "last_date" not in st.session_state:
    st.session_state["last_date"] = str(datetime.date.today())

if not st.session_state["logged_in"]:
    col_l1, col_login, col_l3 = st.columns([1, 2, 1])
    with col_login:
        st.markdown('<div class="main-title">🏛️ स्मार्ट सेतू हिशोब</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">🔐 सुरक्षित लॉगिन (Secure Login)</div>', unsafe_allow_html=True)
        AUTHORIZED_USERS = {"setuknk": "2026"}
        login_username = st.text_input("👤 तुमचा युझरनेम किंवा ID टाका:")
        login_password = st.text_input("🔑 तुमचा पासवर्ड किंवा PIN टाका:", type="password")
        if st.button("🚀 लॉगिन करा (Login)", type="primary", use_container_width=True):
            if login_username in AUTHORIZED_USERS and AUTHORIZED_USERS[login_username] == login_password:
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = login_username
                st.rerun()
            else:
                st.error("❌ चुकीचा युझरनेम किंवा पासवर्ड! प्रवेश नाकारला.")
else:
    # ==========================================
    # ४. मुख्य हिशोब ॲप
    # ==========================================
    st.markdown('<div class="main-title">🏛️ स्मार्ट सेतू हिशोब</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">👋 स्वागत आहे! ({st.session_state["current_user"]})</div>', unsafe_allow_html=True)
    
    col_x1, col_x2 = st.columns([6, 1])
    with col_x2:
        if st.button("🚪 लॉग आउट", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["current_user"] = ""
            st.rerun()

    tab1, tab2 = st.tabs(["📝 आजचा हिशोब भरा", "📊 अहवाल आणि रिपोर्ट"])
    
    sh = connect_to_gsheet()
    hishob_ws = init_db(sh)

    rates = {
        "उत्पन्नाचा": 80, "वय/अधिवास": 80, "अल्पभूधारक": 80, "जातीचा": 80, "EWS": 80,
        "वारसा": 80, "नॉन-क्रिमीलेअर": 80, "ज्येष्ठ नागरिक": 80, "डोंगरी": 80, "रहिवासी": 80, "शेतकरी": 80, "संजय गांधी": 80,
        "प्रतिज्ञापत्रे": 80,
        "रेशन नाव कमी": 69, "रेशन नाव दाखल": 69,
        "स्कॅन पेजेस": 2
    }

    with tab1:
        col_t1_space1, col_t1_main, col_t1_space2 = st.columns([1, 3, 1])
        with col_t1_main:
            date_today = st.date_input("📅 तारीख निवडा:", datetime.date.today())
            date_str = str(date_today)
            
            if date_str != st.session_state["last_date"]:
                st.session_state["force_clear"] = False
                st.session_state["form_key"] += 1
                st.session_state["last_date"] = date_str
            
            all_records = fetch_all_records(hishob_ws)
            existing_row = None
            row_index = None
            
            for i, record in enumerate(all_records):
                if str(record.get("तारीख")) == date_str:
                    existing_row = record
                    row_index = i + 2 
                    break
            
            if existing_row:
                st.info(f"💡 {date_str} या तारखेचा हिशोब आधीच सेव्ह आहे. तुम्ही तो खाली बदलू (Edit) शकता.")
                btn_label = "💾 हिशोब अपडेट करा (Update)"
            else:
                btn_label = "💾 हिशोब गुगल शीटमध्ये सेव्ह करा"

            def get_val(col_name):
                if st.session_state["force_clear"]:
                    return 0
                if existing_row:
                    try:
                        return int(existing_row.get(col_name, 0))
                    except:
                        return 0
                return 0

            fk = st.session_state["form_key"]
            
            with st.expander("📁 १. सर्व महसूल व इतर दाखले (दर: ₹८०)", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    v1 = st.number_input("उत्पन्नाचा दाखला", min_value=0, step=1, value=get_val("उत्पन्नाचा"), key=f"v1_{fk}")
                    v2 = st.number_input("वय, राष्ट्रीयत्व, अधिवास", min_value=0, step=1, value=get_val("वय/अधिवास"), key=f"v2_{fk}")
                    v3 = st.number_input("अल्पभूधारक / भूमिहीन", min_value=0, step=1, value=get_val("अल्पभूधारक"), key=f"v3_{fk}")
                    v4 = st.number_input("जातीचा दाखला", min_value=0, step=1, value=get_val("जातीचा"), key=f"v4_{fk}")
                    v5 = st.number_input("EWS प्रमाणपत्र", min_value=0, step=1, value=get_val("EWS"), key=f"v5_{fk}")
                    v6 = st.number_input("वारसा दाखला", min_value=0, step=1, value=get_val("वारसा"), key=f"v6_{fk}")
                with c2:
                    v7 = st.number_input("नॉन-क्रिमीलेअर", min_value=0, step=1, value=get_val("नॉन-क्रिमीलेअर"), key=f"v7_{fk}")
                    v8 = st.number_input("ज्येष्ठ नागरिक प्रमाणपत्र", min_value=0, step=1, value=get_val("ज्येष्ठ नागरिक"), key=f"v8_{fk}")
                    v9 = st.number_input("डोंगरी दाखला", min_value=0, step=1, value=get_val("डोंगरी"), key=f"v9_{fk}")
                    v10 = st.number_input("रहिवासी दाखला", min_value=0, step=1, value=get_val("रहिवासी"), key=f"v10_{fk}")
                    v11 = st.number_input("शेतकरी दाखला", min_value=0, step=1, value=get_val("शेतकरी"), key=f"v11_{fk}")
                    v12 = st.number_input("संजय गांधी पेन्शन", min_value=0, step=1, value=get_val("संजय गांधी"), key=f"v12_{fk}")
                
                mahsul_rs = (v1+v2+v3+v4+v5+v6+v7+v8+v9+v10+v11+v12) * 80

            with st.expander("📁 २. प्रतिज्ञापत्र (Affidavit) [दर: ₹८०]"):
                v13 = st.number_input("एकूण प्रतिज्ञापत्रे", min_value=0, step=1, value=get_val("प्रतिज्ञापत्रे"), key=f"v13_{fk}")
                affidavit_rs = v13 * 80

            with st.expander("📁 ३. रेशन कार्ड कामे [दर: ₹६९]"):
                v14 = st.number_input("नाव कमी करणे", min_value=0, step=1, value=get_val("रेशन नाव कमी"), key=f"v14_{fk}")
                v15 = st.number_input("नाव दाखल करणे", min_value=0, step=1, value=get_val("रेशन नाव दाखल"), key=f"v15_{fk}")
                ration_rs = (v14 + v15) * 69

            with st.expander("📁 ४. स्कॅनिंग [दर: ₹२ / पेज]"):
                v16 = st.number_input("एकूण स्कॅन केलेली पेजेस", min_value=0, step=1, value=get_val("स्कॅन पेजेस"), key=f"v16_{fk}")
                scan_rs = v16 * 2

            with st.expander("📁 ५. इतर किरकोळ कमाई"):
                v17 = st.number_input("थेट एकूण रक्कम टाका (₹)", min_value=0, step=1, value=get_val("इतर कमाई"), key=f"v17_{fk}")

            grand_total = mahsul_rs + affidavit_rs + ration_rs + scan_rs + v17
            
            date_label_text = "आजची" if date_str == str(datetime.date.today()) else f"{datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%d-%m-%Y')} ची"

            st.markdown(f'''
            <div class="grand-total-card">
                <div class="grand-total-label">💰 {date_label_text} एकूण कमाई</div>
                <div class="grand-total-text">₹ {grand_total}</div>
            </div>
            ''', unsafe_allow_html=True)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                save_clicked = st.button(btn_label, use_container_width=True, type="primary")
            with col_btn2:
                clear_clicked = st.button("🧹 सर्व आकडे पुसा (Clear)", use_container_width=True)

            if clear_clicked:
                st.session_state["force_clear"] = True
                st.session_state["form_key"] += 1
                st.rerun()

            if save_clicked:
                row_data = [
                    date_str, st.session_state["current_user"], 
                    v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, 
                    v13, v14, v15, v16, v17, grand_total
                ]
                try:
                    if existing_row and row_index:
                        try:
                            hishob_ws.update(f"A{row_index}:T{row_index}", [row_data])
                        except:
                            hishob_ws.update(values=[row_data], range_name=f"A{row_index}:T{row_index}")
                        st.success("✅ रेकॉर्ड यशस्वीरित्या अपडेट झाला!")
                    else:
                        hishob_ws.append_row(row_data)
                        st.balloons()
                        st.success("✅ रेकॉर्ड गुगल शीटमध्ये यशस्वीरित्या सेव्ह झाला!")
                    
                    fetch_all_records.clear()
                    st.session_state["force_clear"] = False
                    st.session_state["form_key"] += 1
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"⚠️ सेव्ह करताना अडचण आली: {e}")

    with tab2:
        st.markdown('<div class="sub-title" style="margin-bottom:10px;">🔍 ॲडव्हान्स अहवाल (Advanced Reports)</div>', unsafe_allow_html=True)
        
        all_data = fetch_all_records(hishob_ws)
        df = pd.DataFrame(all_data)
        
        if not df.empty:
            df['तारीख'] = pd.to_datetime(df['तारीख'])
            
            filter_type = st.selectbox("📅 रिपोर्टचा कालावधी निवडा:", 
                                       ["विशिष्ट तारीख", "दोन तारखांच्या दरम्यान", "विशिष्ट महिना", "विशिष्ट वर्ष", "सर्व डेटा"])
            
            filtered_df = df.copy()
            col_f1, col_f2 = st.columns(2)
            
            if filter_type == "विशिष्ट तारीख":
                sel_date = st.date_input("तारीख निवडा (रिपोर्टसाठी):", datetime.date.today())
                filtered_df = df[df['तारीख'].dt.date == sel_date]
            elif filter_type == "दोन तारखांच्या दरम्यान":
                with col_f1: start_date = st.date_input("सुरुवातीची तारीख:")
                with col_f2: end_date = st.date_input("शेवटची तारीख:")
                filtered_df = df[(df['तारीख'].dt.date >= start_date) & (df['तारीख'].dt.date <= end_date)]
            elif filter_type == "विशिष्ट महिना":
                months = ["जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून", "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"]
                with col_f1: 
                    sel_month_name = st.selectbox("महिना निवडा:", months)
                    sel_month = months.index(sel_month_name) + 1
                with col_f2: 
                    sel_year = st.selectbox("वर्ष निवडा:", range(2024, 2030))
                filtered_df = df[(df['तारीख'].dt.month == sel_month) & (df['तारीख'].dt.year == sel_year)]
            elif filter_type == "विशिष्ट वर्ष":
                sel_year = st.selectbox("वर्ष निवडा:", range(2024, 2030))
                filtered_df = df[df['तारीख'].dt.year == sel_year]

            report_type = st.radio("📊 रिपोर्टचा प्रकार:", ["संपूर्ण हिशोब (डिटेल)", "फक्त दाखल्यांची संख्या"], horizontal=True)

            if not filtered_df.empty:
                report_list = []
                grand_total_calc = 0
                
                if report_type == "फक्त दाखल्यांची संख्या":
                    cols_to_check = list(rates.keys())
                    cols_to_check.remove("स्कॅन पेजेस") 
                    for col in cols_to_check:
                        if col in filtered_df.columns:
                            count = filtered_df[col].sum()
                            if count > 0:
                                report_list.append({"तपशील (काम)": col, "एकूण संख्या": count})
                else:
                    all_cols = list(rates.keys()) + ["इतर कमाई"]
                    for col in all_cols:
                        if col in filtered_df.columns:
                            count = filtered_df[col].sum()
                            if count > 0:
                                if col == "इतर कमाई":
                                    total_amt = count
                                    report_list.append({"तपशील (काम)": col, "संख्या": "-", "दर": "-", "एकूण रक्कम (₹)": total_amt})
                                    grand_total_calc += total_amt
                                else:
                                    rate = rates[col]
                                    total_amt = count * rate
                                    report_list.append({"तपशील (काम)": col, "संख्या": count, "दर": f"₹ {rate}", "एकूण रक्कम (₹)": total_amt})
                                    grand_total_calc += total_amt

                if report_list:
                    df_report = pd.DataFrame(report_list)
                    
                    if filter_type == "विशिष्ट तारीख":
                        date_str_rep = f"दिनांक: {sel_date.strftime('%d-%m-%Y')}"
                    elif filter_type == "दोन तारखांच्या दरम्यान":
                        date_str_rep = f"कालावधी: {start_date.strftime('%d-%m-%Y')} ते {end_date.strftime('%d-%m-%Y')}"
                    elif filter_type == "विशिष्ट महिना":
                        date_str_rep = f"महिना: {sel_month_name} {sel_year}"
                    elif filter_type == "विशिष्ट वर्ष":
                        date_str_rep = f"वर्ष: {sel_year}"
                    else:
                        date_str_rep = "संपूर्ण डेटा (सर्व रेकॉर्ड्स)"

                    st.markdown("---")
                    
                    col_view1, col_view2 = st.columns([1.2, 1])
                    
                    with col_view1:
                        st.markdown(f"### 📋 रिपोर्ट प्रीव्ह्यू")
                        html_table = "<table class='report-table'><tr>"
                        for col_name in df_report.columns:
                            html_table += f"<th>{col_name}</th>"
                        html_table += "</tr>"
                        
                        for _, row in df_report.iterrows():
                            html_table += "<tr>"
                            for val in row:
                                html_table += f"<td>{val}</td>"
                            html_table += "</tr>"
                            
                        if report_type == "संपूर्ण हिशोब (डिटेल)":
                            html_table += f"<tr class='report-total-row'><td colspan='3' style='text-align:right;'>एकूण कमाई:</td><td>₹ {grand_total_calc}</td></tr>"
                        html_table += "</table>"
                        
                        st.markdown(html_table, unsafe_allow_html=True)
                    
                    with col_view2:
                        st.markdown("### 📊 कामाचा आलेख (Dashboard)")
                        
                        chart_data = []
                        for col in rates.keys(): 
                            if col in filtered_df.columns:
                                count = filtered_df[col].sum()
                                if count > 0:
                                    chart_data.append({
                                        "तपशील (काम)": col,
                                        "एकूण संख्या": int(count),
                                        "एकूण रक्कम (₹)": int(count * rates[col])
                                    })
                        
                        if "इतर कमाई" in filtered_df.columns:
                            itar = filtered_df["इतर कमाई"].sum()
                            if itar > 0:
                                chart_data.append({
                                    "तपशील (काम)": "इतर कमाई",
                                    "एकूण संख्या": 0,
                                    "एकूण रक्कम (₹)": int(itar)
                                })
                        
                        if chart_data:
                            clean_chart_df = pd.DataFrame(chart_data)
                            
                            # 🔥 फिक्स १: बार ग्राफ (दाखल्यांची संख्या) - झूम (interactive) आणि स्लायडर सह!
                            st.markdown("**📈 दाखल्यांची संख्या**")
                            bar_df = clean_chart_df[clean_chart_df["एकूण संख्या"] > 0]
                            
                            bar_chart = alt.Chart(bar_df).mark_bar(
                                size=30, 
                                cornerRadiusTopLeft=4, 
                                cornerRadiusTopRight=4
                            ).encode(
                                x=alt.X('तपशील (काम):N', sort='-y', title="", axis=alt.Axis(labelAngle=-45, labelOverlap=False)),
                                y=alt.Y('एकूण संख्या:Q', title="संख्या"),
                                color=alt.Color('तपशील (काम):N', scale=alt.Scale(scheme='category20'), legend=None),
                                tooltip=[alt.Tooltip("तपशील (काम)", title="काम"), alt.Tooltip("एकूण संख्या", title="संख्या")]
                            ).properties(height=300, width=max(800, len(bar_df)*50)).interactive()
                            
                            # HTML डब्यात टाकल्यामुळे 'आडवा स्लायडर' १००% येणार!
                            st.markdown('<div class="scrollable-chart">', unsafe_allow_html=True)
                            st.altair_chart(bar_chart, use_container_width=False)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 🔥 फिक्स २: डोनट चार्ट (कमाईची रक्कम) - मोठा साईझ आणि स्पष्ट लेजंड!
                            st.markdown("**🍩 कमाईची विभागणी (₹)**")
                            pie_chart = alt.Chart(clean_chart_df).mark_arc(
                                innerRadius=50,         
                                stroke="#ffffff",       
                                strokeWidth=1.5
                            ).encode(
                                theta=alt.Theta(field="एकूण रक्कम (₹)", type="quantitative"),
                                color=alt.Color('तपशील (काम):N', scale=alt.Scale(scheme='category20'), legend=alt.Legend(title="कामाचा प्रकार", orient="right", columns=1)),
                                tooltip=[alt.Tooltip("तपशील (काम)", title="काम"), alt.Tooltip("एकूण रक्कम (₹)", title="रक्कम (₹)")]
                            ).properties(height=400, width=400) # इथे width आणि height मोठी केली आहे!
                            
                            st.altair_chart(pie_chart, use_container_width=True)

                    st.markdown("---")

                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_report.to_excel(writer, index=False, sheet_name='Report', startrow=3)
                            workbook = writer.book
                            worksheet = writer.sheets['Report']
                            worksheet.set_paper(9)
                            worksheet.set_portrait() 
                            
                            title_format = workbook.add_format({'bold': True, 'font_size': 18, 'font_name': 'Mukta', 'align': 'center', 'valign': 'vcenter', 'color': '#1e3a8a'})
                            date_format = workbook.add_format({'bold': True, 'font_size': 13, 'font_name': 'Mukta', 'align': 'center', 'valign': 'vcenter', 'color': '#475569'})
                            header_format = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Mukta', 'bg_color': '#1e3a8a', 'font_color': 'white', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                            cell_format = workbook.add_format({'font_size': 13, 'font_name': 'Mukta', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                            cell_left_format = workbook.add_format({'font_size': 13, 'font_name': 'Mukta', 'border': 1, 'align': 'left', 'valign': 'vcenter'})
                            
                            worksheet.merge_range('A1:D1', "🏛️ स्मार्ट सेतू केंद्र - हिशोब अहवाल", title_format)
                            worksheet.merge_range('A2:D2', date_str_rep, date_format)
                            worksheet.set_row(0, 30)
                            worksheet.set_row(1, 20)
                            worksheet.set_row(2, 10)
                            
                            worksheet.set_column('A:A', 30, cell_left_format)
                            worksheet.set_column('B:D', 18, cell_format)
                            
                            for col_num, value in enumerate(df_report.columns.values):
                                worksheet.write(3, col_num, value, header_format)
                            
                            for row_num in range(len(df_report) + 4):
                                worksheet.set_row(row_num, 22)
                                
                            if report_type == "संपूर्ण हिशोब (डिटेल)":
                                last_row = len(df_report) + 4
                                total_format = workbook.add_format({'bold': True, 'font_size': 15, 'font_name': 'Mukta', 'bg_color': '#f1f5f9', 'border': 1, 'align': 'right', 'valign': 'vcenter'})
                                total_amt_format = workbook.add_format({'bold': True, 'font_size': 15, 'font_name': 'Mukta', 'bg_color': '#e2e8f0', 'font_color': '#059669', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                                
                                worksheet.merge_range(last_row, 0, last_row, 2, "एकूण कमाई:", total_format)
                                worksheet.write(last_row, 3, f"₹ {grand_total_calc}", total_amt_format)
                                worksheet.set_row(last_row, 28)

                        excel_data = output.getvalue()
                        st.download_button(label="📥 A4 उभी Excel डाऊनलोड", data=excel_data, file_name="Smart_Setu_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                    
                    with col_d2:
                        print_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>स्मार्ट सेतू अहवाल</title>
                            <meta charset="utf-8">
                            <style>
                                @import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;800&display=swap');
                                body {{ font-family: 'Mukta', Arial, sans-serif; padding: 40px; color: #333; }}
                                h2 {{ text-align: center; color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; margin-bottom: 5px; }}
                                .date-text {{ text-align: center; font-size: 16px; color: #555; margin-bottom: 20px; font-weight: bold; }}
                                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                                th {{ background-color: #f2f2f2; color: #333; font-weight: bold; padding: 12px; text-align: left; border: 1px solid #ddd; }}
                                td {{ padding: 10px; border: 1px solid #ddd; font-size: 16px; }}
                                .total-row {{ font-weight: bold; background-color: #e2e8f0; font-size: 18px; }}
                                .total-row td {{ padding: 15px; }}
                            </style>
                        </head>
                        <body onload="window.print()">
                            <h2>🏛️ स्मार्ट सेतू केंद्र - हिशोब अहवाल</h2>
                            <div class="date-text">{date_str_rep}</div>
                            <table>
                                <tr>
                        """
                        for col_name in df_report.columns:
                            print_html += f"<th>{col_name}</th>"
                        print_html += "</tr>"
                        
                        for _, row in df_report.iterrows():
                            print_html += "<tr>"
                            for val in row:
                                print_html += f"<td>{val}</td>"
                            print_html += "</tr>"
                            
                        if report_type == "संपूर्ण हिशोब (डिटेल)":
                            print_html += f"""
                            <tr class='total-row'>
                                <td colspan='3' style='text-align: right;'>एकूण कमाई:</td>
                                <td>₹ {grand_total_calc}</td>
                            </tr>
                            """
                        print_html += "</table><br><p style='text-align:center; color:#777; font-size:12px;'>* This is a computer generated report.</p></body></html>"
                        
                        st.download_button(label="🖨️ रिपोर्ट प्रिंट / PDF काढा", data=print_html, file_name="Print_Report.html", mime="text/html", use_container_width=True)

                    st.markdown("---")
                    st.markdown('<div class="sub-title" style="margin-bottom:10px;">📦 सुरक्षित डेटाबेस बॅकअप</div>', unsafe_allow_html=True)
                    st.info("💡 इथून तुम्ही आतापर्यंतचा सर्व मूळ डेटा डाऊनलोड करू शकता. या फाईलमध्ये **'ऑटो-फिल्टर (▼)'** लावलेला आहे, ज्यामुळे तुम्ही तारखेनुसार किंवा दाखल्यानुसार माहिती सहज शोधू शकता.")
                    
                    backup_df = df.copy()
                    backup_df = backup_df.sort_values(by='तारीख', ascending=True) 
                    backup_df['तारीख'] = backup_df['तारीख'].dt.strftime('%d-%m-%Y')
                    
                    output_backup = io.BytesIO()
                    with pd.ExcelWriter(output_backup, engine='xlsxwriter') as writer:
                        backup_df.to_excel(writer, index=False, sheet_name='Raw_Backup')
                        workbook_b = writer.book
                        worksheet_b = writer.sheets['Raw_Backup']
                        
                        header_fmt_b = workbook_b.add_format({'bold': True, 'font_size': 12, 'font_name': 'Mukta', 'bg_color': '#1e3a8a', 'font_color': 'white', 'border': 1})
                        cell_fmt_b = workbook_b.add_format({'font_size': 11, 'font_name': 'Mukta', 'border': 1, 'align': 'center'})
                        
                        worksheet_b.set_column('A:T', 15, cell_fmt_b)
                        
                        for col_num, value in enumerate(backup_df.columns.values):
                            worksheet_b.write(0, col_num, value, header_fmt_b)
                            
                        max_row = len(backup_df)
                        max_col = len(backup_df.columns) - 1
                        worksheet_b.autofilter(0, 0, max_row, max_col)
                        
                    backup_data = output_backup.getvalue()
                    st.download_button(label="📥 संपूर्ण डेटाबेस डाऊनलोड करा (Excel Backup)", data=backup_data, file_name="Smart_Setu_Full_Backup.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

                else:
                    st.info("या कालावधीत कोणतेही दाखले काढलेले नाहीत.")
            else:
                st.warning("या कालावधीसाठी कोणताही डेटा उपलब्ध नाही. 🤷‍♂️")
