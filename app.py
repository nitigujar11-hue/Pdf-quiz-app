import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
import os
import pickle
import streamlit.components.v1 as components
from PIL import Image, ImageOps
from streamlit_cropper import st_cropper

st.set_page_config(page_title="Free Weekly Test - Portal", page_icon="📝", layout="wide")

# ==========================================
# 🎨 RWA जैसी कस्टम थीम CSS (Video Matching UI)
# ==========================================
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .test-card {
        background: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-left: 4px solid #1E3A8A;
    }
    .test-title {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
        margin-left: 15px;
        flex-grow: 1;
    }
    .icon-box {
        background: #e2e8f0;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 डेटाबेस कॉन्फ़िगरेशन
# ==========================================
ADMIN_PASSWORD = "NINI@123"
DB_FILE = "app_quiz_database_rwa_exact.pkl"

DEFAULT_SUBJECTS = {
    "🔢 Mathematics (गणित)": [
        "Percentage", "Profit & Loss", "PARTNERSHIP", "Ratio & Proportion",
        "Simple & Compound Interest", "Time & Work", "Speed, Time & Distance", "TRAIN", 
        "Number System", "Average", "Mensuration 2D", "MENSURATION 3D", 
        "LCM & HCF", "SIMPLIFICATION", "AGE", "DISCOUNT", "DATA INTERPRETATION"
    ],
    "🧠 Reasoning (तर्कशक्ति)": [
        "Coding-Decoding", "Analogy", "Blood Relation", "Classification", 
        "Logical Arrangement", "Inserting Missing Characters", "Clock & Calendar", "Sitting Arrangement", 
        "Rankings Test", "Venn Diagram", "Mathematics Operation", "Statement and Conclusion", 
        "Direction & Distance", "Series", "Syllogism", "Non-Verbal Reasoning"
    ],
    "🌍 Indian Geography (भूगोल)": [
        "भारत की नदियाँ एवं झीलें", "पर्वत एवं पठार", "जलवायु एवं मानसून", "कृषि एवं खनिज संसाधन", 
        "राष्ट्रीय उद्यान एवं अभयारण्य", "Other"
    ],
    "🏛️ Indian Polity (राजव्यवस्था)": [
        "संविधान की प्रस्तावना व स्रोत", "मौलिक अधिकार एवं कर्तव्य", "राष्ट्रपति एवं संसद", 
        "न्यायपालिका (Supreme Court)", "पंचायती राज व संशोधन", "OTHER"
    ],
    "💡 General Science (सामान्य विज्ञान)": [
        "Physics", "Chemistry", "Biology", "OTHER"
    ],
    "🏆 Static GK (स्टैटिक जीके)": [
        "प्रमुख लोक नृत्य एवं त्यौहार", "महत्वपूर्ण दिवस एवं थीम", "खेलकूद एवं ट्रॉफियां", 
        "भारत के प्रमुख मंदिर व स्मारक", "OTHER"
    ],
    "📖 सामान्य हिंदी": [
        "संधि एवं समास", "विलोम एवं पर्यायवाची शब्द", "मुहावरे एवं लोकोक्तियां", 
        "अनेक शब्दों के लिए एक शब्द", "वर्तनी एवं वाक्य शुद्धि", "OTHER"
    ],
    "📊 Economics": [
        "ALL TOPICS"
    ]
}

# ==========================================
# 💾 डेटाबेस लोड एवं सेव फंक्शन
# ==========================================
def load_permanent_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    return {
        "subjects": DEFAULT_SUBJECTS, 
        "questions": {}, 
        "full_mock_questions": {}, 
        "attempts": {}, 
        "users": {}
    }

def save_permanent_data():
    payload = {
        "subjects": st.session_state.subjects_data,
        "questions": st.session_state.all_questions_db,
        "full_mock_questions": st.session_state.full_mock_db,
        "attempts": st.session_state.attempt_history,
        "users": st.session_state.users_db
    }
    with open(DB_FILE, "wb") as f:
        pickle.dump(payload, f)

initial_data = load_permanent_data()

if "users_db" not in st.session_state:
    st.session_state.users_db = initial_data.get("users", {})
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "subjects_data" not in st.session_state:
    st.session_state.subjects_data = initial_data.get("subjects", DEFAULT_SUBJECTS)
if "all_questions_db" not in st.session_state:
    st.session_state.all_questions_db = initial_data.get("questions", {})
if "full_mock_db" not in st.session_state:
    st.session_state.full_mock_db = initial_data.get("full_mock_questions", {})
if "attempt_history" not in st.session_state:
    st.session_state.attempt_history = initial_data.get("attempts", {})

# ==========================================
# 🔐 लॉगिन / साइनअप / फॉरगॉट पासवर्ड स्क्रीन
# ==========================================
if st.session_state.logged_in_user is None:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📚 Free Weekly Test Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>अपनी तैयारी को परखने के लिए लॉगिन करें</p>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_admin, tab_signup, tab_forgot = st.tabs(["🔑 यूजर लॉगिन", "👨‍🏫 एडमिन लॉगिन", "📝 नया अकाउंट", "🔄 पासवर्ड रिकवर"])

        with tab_login:
            log_mob = st.text_input("मोबाइल नंबर (Mobile Number):", key="u_log_mob")
            log_pass = st.text_input("पासवर्ड (Password):", type="password", key="u_log_pass")
            
            if st.button("लॉगिन करें 🚀", type="primary", use_container_width=True):
                log_mob = log_mob.strip()
                if log_mob in st.session_state.users_db:
                    if st.session_state.users_db[log_mob]["password"] == log_pass:
                        st.session_state.logged_in_user = log_mob
                        st.session_state.user_role = "user"
                        st.success("सफलतापूर्वक लॉगिन हो गया!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error("गलत पासवर्ड!")
                else:
                    st.error("मोबाइल नंबर रजिस्टर्ड नहीं है। कृपया नया अकाउंट बनाएं।")

        with tab_admin:
            admin_pwd_input = st.text_input("एडमिन पासवर्ड दर्ज करें:", type="password", key="adm_direct_pass")
            
            if st.button("एडमिन रूप में प्रवेश करें 🔐", type="primary", use_container_width=True):
                if admin_pwd_input == ADMIN_PASSWORD:
                    st.session_state.logged_in_user = "ADMIN"
                    st.session_state.user_role = "admin"
                    st.success("एडमिन मोड सक्रिय!")
                    time.sleep(0.4)
                    st.rerun()
                else:
                    st.error("गलत एडमिन पासवर्ड!")

        with tab_signup:
            new_name = st.text_input("पूरा नाम:", key="sign_name")
            new_mob = st.text_input("मोबाइल नंबर:", key="sign_mob")
            new_pass = st.text_input("पासवर्ड बनाएं:", type="password", key="sign_pass")
            
            if st.button("रजिस्टर करें ➔", type="primary", use_container_width=True):
                new_mob = new_mob.strip()
                if not new_name or not new_mob or not new_pass:
                    st.warning("सभी विवरण भरना अनिवार्य है!")
                elif new_mob in st.session_state.users_db:
                    st.error("यह मोबाइल नंबर पहले से रजिस्टर्ड है।")
                else:
                    st.session_state.users_db[new_mob] = {"name": new_name, "password": new_pass}
                    save_permanent_data()
                    st.success("सफलतापूर्वक रजिस्ट्रेशन हो गया! अब 'यूजर लॉगिन' टैब से लॉगिन करें।")

        with tab_forgot:
            f_mob = st.text_input("रजिस्टर्ड मोबाइल नंबर:", key="f_mob")
            f_new_pass = st.text_input("नया पासवर्ड:", type="password", key="f_new_pass")
            
            if st.button("पासवर्ड अपडेट करें 🔄", use_container_width=True):
                f_mob = f_mob.strip()
                if f_mob in st.session_state.users_db:
                    st.session_state.users_db[f_mob]["password"] = f_new_pass
                    save_permanent_data()
                    st.success("पासवर्ड बदल गया है!")
                else:
                    st.error("मोबाइल नंबर डेटाबेस में नहीं मिला।")
    
    st.stop()

# ==========================================
# 👁️ सेशन सेटअप
# ==========================================
current_user = st.session_state.logged_in_user
is_admin_user = (st.session_state.user_role == "admin")

# ==========================================
# ⚡ ऑटो-कंप्रेसर फंक्शन
# ==========================================
def compress_and_convert_to_bytes(img, max_width=900, quality=75):
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int((float(img.height) * float(ratio)))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", optimize=True, quality=quality)
    return buf.getvalue()

# ==========================================
# 📊 स्कोर गणना
# ==========================================
def calculate_and_submit_quiz(is_timeout=False):
    st.session_state.submitted = True
    st.session_state.quiz_started = False
    
    questions_list = st.session_state.active_questions_list
    total = len(questions_list)
    correct = 0
    wrong = 0
    unattempted = 0
    
    mark_per_q = st.session_state.get("selected_marks", 1.0)
    neg = st.session_state.get("selected_neg", 0.0)

    for idx, q in enumerate(questions_list):
        ans = st.session_state.user_answers.get(idx)
        if ans is None:
            unattempted += 1
        elif ans == q['answer']:
            correct += 1
        else:
            wrong += 1

    max_marks = total * mark_per_q
    raw_score = (correct * mark_per_q) - (wrong * neg)
    accuracy = (correct / (correct + wrong) * 100) if (correct + wrong) > 0 else 0

    history_key = f"{current_user}_{st.session_state.current_test_key}"
    if history_key not in st.session_state.attempt_history:
        st.session_state.attempt_history[history_key] = []

    past_attempts = st.session_state.attempt_history[history_key]
    attempt_num = len(past_attempts) + 1
    reason = " (समय समाप्त)" if is_timeout else ""
    
    st.session_state.attempt_history[history_key].append({
        "अटेम्प्ट": f"प्रयास #{attempt_num}{reason}",
        "तारीख": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "raw_score": raw_score,
        "प्राप्तांक": f"{raw_score:.2f} / {max_marks:.0f}",
        "सही (Correct)": correct,
        "गलत (Wrong)": wrong,
        "छोड़े (Skipped)": unattempted,
        "सटीकता": f"{accuracy:.1f}%",
        "user_answers": dict(st.session_state.user_answers)
    })
    save_permanent_data()

# --- साइडबार पैनल ---
with st.sidebar:
    st.title("👤 यूजर अकाउंट")
    if is_admin_user:
        st.success("👨‍🏫 एडमिन मोड (Master)")
    else:
        user_info = st.session_state.users_db.get(current_user, {})
        st.write(f"**नाम:** {user_info.get('name', 'User')}")
        st.write(f"**मोबाइल:** {current_user}")
    
    if st.button("🚪 लॉगआउट (Logout)", type="secondary", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()

    if is_admin_user:
        st.divider()
        st.subheader("🛠️ एडमिन कंट्रोल्स")
        with st.expander("👥 सभी रजिस्टर्ड छात्र"):
            if st.session_state.users_db:
                for u_mob, u_data in st.session_state.users_db.items():
                    st.write(f"• {u_data.get('name')} ({u_mob})")
            else:
                st.caption("कोई छात्र नहीं है।")

# स्टेट वेरिएबल्स
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = None
if "selected_chapter" not in st.session_state:
    st.session_state.selected_chapter = None
if "is_full_mock_mode" not in st.session_state:
    st.session_state.is_full_mock_mode = False
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "time_limit_seconds" not in st.session_state:
    st.session_state.time_limit_seconds = 0

# ==========================================
# 📲 टॉप हेडर: 'Free Weekly Test' हेडर + फुल मॉक बटन + शेयर आइकॉन (जैसे वीडियो में है)
# ==========================================
top_c1, top_c2, top_c3 = st.columns([2, 2, 1])
with top_c1:
    st.markdown("<h3 style='color: #1E3A8A; margin: 0;'>⬅ Free Weekly Test</h3>", unsafe_allow_html=True)
with top_c2:
    if st.button("🏆 Full Mock Test", use_container_width=True, type="primary"):
        st.session_state.is_full_mock_mode = True
        st.session_state.selected_subject = None
        st.session_state.selected_chapter = None
        st.session_state.quiz_started = False
        st.session_state.submitted = False
        st.rerun()
with top_c3:
    components.html("""
    <div style="text-align: right; margin-top: 5px;">
        <button id="shareBtn" style="background: transparent; border: none; font-size: 20px; cursor: pointer;" title="Share">🔗</button>
    </div>
    <script>
    document.getElementById('shareBtn').addEventListener('click', async () => {
        if (navigator.share) { try { await navigator.share({title: 'Free Weekly Test', url: window.location.href}); } catch(e){} }
        else { navigator.clipboard.writeText(window.location.href); alert('लिंक कॉपी हो गया!'); }
    });
    </script>
    """, height=40)

st.write("---")

# ==========================================
# 🏆 1. फुल मॉक टेस्ट स्क्रीन
# ==========================================
if st.session_state.is_full_mock_mode:
    if st.button("⬅ वापस जाएं"):
        st.session_state.is_full_mock_mode = False
        st.rerun()
    st.title("🏆 Full Length Mock Test")
    st.write("---")

    fm_key = "full_mock_main_exam"
    st.session_state.current_test_key = fm_key
    full_mock_questions = st.session_state.full_mock_db.get(fm_key, [])
    st.session_state.active_questions_list = full_mock_questions

    if is_admin_user:
        with st.expander("➕ फुल मॉक में नया प्रश्न जोड़ें (एडमिन)", expanded=False):
            with st.form("fm_add_q_form"):
                fm_qt = st.text_area("प्रश्न टेक्स्ट:")
                fm_i = st.file_uploader("प्रश्न फोटो:", type=["png", "jpg", "jpeg"], key="fm_img_up")
                
                c1, c2 = st.columns(2)
                with c1: 
                    fm_oa = st.text_input("विकल्प A", key="fm_a")
                    fm_oc = st.text_input("विकल्प C", key="fm_c")
                with c2: 
                    fm_ob = st.text_input("विकल्प B", key="fm_b")
                    fm_od = st.text_input("विकल्प D", key="fm_d")
                
                fm_ans = st.selectbox("सही उत्तर:", ["A", "B", "C", "D"], key="fm_ans_sel")
                
                if st.form_submit_button("फुल मॉक प्रश्न सेव करें 💾"):
                    final_fm_img = compress_and_convert_to_bytes(Image.open(fm_i)) if fm_i else None
                    if fm_key not in st.session_state.full_mock_db:
                        st.session_state.full_mock_db[fm_key] = []
                    
                    st.session_state.full_mock_db[fm_key].append({
                        "question_text": fm_qt if fm_qt else "फोटो आधारित प्रश्न:",
                        "question_image": final_fm_img,
                        "options_text": {"A": fm_oa, "B": fm_ob, "C": fm_oc, "D": fm_od},
                        "options_image": {},
                        "answer": fm_ans,
                        "sol_image": None
                    })
                    save_permanent_data()
                    st.success("प्रश्न सेव हो गया! अगला प्रश्न जोड़ें।")
                    st.rerun()

    history_key_fm = f"{current_user}_{fm_key}"
    past_fm_attempts = st.session_state.attempt_history.get(history_key_fm, [])

    if not st.session_state.quiz_started and not st.session_state.submitted:
        st.write(f"**कुल उपलब्ध फुल मॉक प्रश्न:** {len(full_mock_questions)}")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.session_state.selected_marks = st.selectbox("अंक प्रति प्रश्न:", [1.0, 2.0, 4.0], key="fm_marks")
        with c_m2:
            fm_time = st.selectbox("समय सीमा:", [0, 30, 60, 90, 120], format_func=lambda x: "असीमित" if x==0 else f"{x} मिनट", key="fm_time")
            st.session_state.time_limit_seconds = fm_time * 60

        if full_mock_questions:
            if st.button("🚀 फुल मॉक टेस्ट शुरू करें", type="primary", use_container_width=True):
                st.session_state.quiz_started = True
                st.session_state.start_time = time.time()
                st.session_state.user_answers = {}
                st.rerun()
        else:
            st.warning("फिलहाल कोई फुल मॉक प्रश्न उपलब्ध नहीं हैं।")

    elif st.session_state.quiz_started and not st.session_state.submitted:
        if st.session_state.time_limit_seconds > 0:
            elapsed = time.time() - st.session_state.start_time
            remaining = st.session_state.time_limit_seconds - elapsed
            if remaining <= 0:
                st.error("⏰ समय समाप्त!")
                calculate_and_submit_quiz(is_timeout=True)
                st.rerun()
            else:
                st.warning(f"⏱️ समय शेष: {int(remaining//60):02d}:{int(remaining%60):02d} मिनट")

        for idx, q in enumerate(full_mock_questions):
            st.markdown(f"### प्रश्न {idx+1}: {q['question_text']}")
            if q.get("question_image"):
                st.image(q["question_image"], width=450)
            
            opts = [f"A) {q['options_text']['A']}", f"B) {q['options_text']['B']}", f"C) {q['options_text']['C']}", f"D) {q['options_text']['D']}"]
            ans = st.radio(f"उत्तर चुनें {idx+1}:", opts, key=f"fm_ans_{idx}", index=None)
            st.session_state.user_answers[idx] = ans[0] if ans else None
            st.write("---")

        if st.button("🏁 फुल मॉक सबमिट करें", type="primary"):
            calculate_and_submit_quiz(is_timeout=False)
            st.rerun()

    elif st.session_state.submitted:
        st.header("📊 फुल मॉक रिपोर्ट")
        last_att = past_fm_attempts[-1] if past_fm_attempts else {}
        st.metric("प्राप्तांक", last_att.get("प्राप्तांक", "0"))
        st.metric("सटीकता", last_att.get("सटीकता", "0%"))
        if st.button("🔄 दोबारा टेस्ट दें"):
            st.session_state.submitted = False
            st.session_state.quiz_started = False
            st.rerun()

# ==========================================
# 🎯 2. RWA जैसी लिस्ट स्टाइल (Video Matching Layout)
# ==========================================
elif st.session_state.selected_subject is None:
    st.markdown("### 📚 विषय एवं वीकली टेस्ट लिस्ट (Subjects)")
    
    all_active_subjects = list(st.session_state.subjects_data.keys())
    
    # वीडियो जैसी कार्ड लिस्ट तैयार करना
    for index, subj in enumerate(all_active_subjects):
        chaps = st.session_state.subjects_data.get(subj, [])
        
        # HTML/Markdown से बिल्कुल वीडियो जैसी लिस्ट रो बनाना
        st.markdown(f"""
            <div class="test-card">
                <div style="display: flex; align-items: center;">
                    <div class="icon-box">📄</div>
                    <div class="test-title">{subj} <br><span style="font-size: 12px; font-weight: normal; color: #64748b;">कुल अध्याय: {len(chaps)}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"ओपन करें ➔", key=f"subj_btn_{index}", use_container_width=True):
            st.session_state.selected_subject = subj
            st.rerun()
        st.write("")

    if is_admin_user:
        st.write("---")
        with st.expander("➕ नया विषय जोड़ें"):
            new_s = st.text_input("विषय का नाम:")
            if st.button("विषय सेव करें"):
                if new_s.strip() and new_s not in st.session_state.subjects_data:
                    st.session_state.subjects_data[new_s.strip()] = []
                    save_permanent_data()
                    st.success("विषय जुड़ गया!")
                    st.rerun()

# --- चैप्टर चयन स्क्रीन ---
elif st.session_state.selected_chapter is None:
    st.button("⬅ विषयों की सूची पर जाएं", on_click=lambda: st.session_state.update({"selected_subject": None}))
    st.title(f"📁 {st.session_state.selected_subject}")
    st.write("### चैप्टर सूची:")
    st.write("---")

    chapters = st.session_state.subjects_data.get(st.session_state.selected_subject, [])
    for index, chap in enumerate(chapters):
        st.markdown(f"""
            <div class="test-card">
                <div style="display: flex; align-items: center;">
                    <div class="icon-box">📑</div>
                    <div class="test-title">{chap}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("टेस्ट लगाएं ✍️", key=f"chap_click_{index}", use_container_width=True):
            st.session_state.selected_chapter = chap
            st.rerun()
        st.write("")

    if is_admin_user:
        st.write("---")
        with st.expander("➕ इस विषय में नया चैप्टर जोड़ें"):
            new_c = st.text_input("चैप्टर का नाम:")
            if st.button("चैप्टर सेव करें"):
                if new_c.strip() and new_c not in chapters:
                    st.session_state.subjects_data[st.session_state.selected_subject].append(new_c.strip())
                    save_permanent_data()
                    st.success("चैप्टर जुड़ गया!")
                    st.rerun()

# --- मॉक टेस्ट और एडमिन क्वेश्चन क्रिएशन स्क्रीन ---
else:
    st.button("⬅ चैप्टर सूची पर जाएं", on_click=lambda: st.session_state.update({"selected_chapter": None, "quiz_started": False, "submitted": False}))
    st.subheader(f"📌 {st.session_state.selected_subject} ➔ {st.session_state.selected_chapter}")
    st.divider()

    current_test_key = f"{st.session_state.selected_subject}_{st.session_state.selected_chapter}"
    st.session_state.current_test_key = current_test_key
    current_questions = st.session_state.all_questions_db.get(current_test_key, [])
    st.session_state.active_questions_list = current_questions

    if is_admin_user:
        with st.expander("➕ इस चैप्टर में नया प्रश्न जोड़ें (एडमिन)", expanded=False):
            with st.form(key=f"chapter_add_q_form_{len(current_questions)}"):
                q_t = st.text_area("प्रश्न लिखें:")
                q_i = st.file_uploader("प्रश्न की फोटो (वैकल्पिक):", type=["png", "jpg", "jpeg"])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    op_a = st.text_input("विकल्प A")
                    op_c = st.text_input("विकल्प C")
                with col_b:
                    op_b = st.text_input("विकल्प B")
                    op_d = st.text_input("विकल्प D")
                
                corr = st.selectbox("सही उत्तर:", ["A", "B", "C", "D"])
                
                if st.form_submit_button("सवाल सेव करें और अगला जोड़ें 💾"):
                    final_q_img = compress_and_convert_to_bytes(Image.open(q_i)) if q_i else None
                    new_item = {
                        "question_text": q_t if q_t else "नीचे दी गई फोटो देखें:",
                        "question_image": final_q_img,
                        "options_text": {"A": op_a, "B": op_b, "C": op_c, "D": op_d},
                        "options_image": {},
                        "answer": corr,
                        "sol_image": None
                    }
                    if current_test_key not in st.session_state.all_questions_db:
                        st.session_state.all_questions_db[current_test_key] = []
                    st.session_state.all_questions_db[current_test_key].append(new_item)
                    save_permanent_data()
                    st.success("✅ प्रश्न सफलतापूर्वक सेव हो गया! अगला प्रश्न दर्ज करें।")
                    time.sleep(0.5)
                    st.rerun()

    history_key_user = f"{current_user}_{current_test_key}"
    past_attempts = st.session_state.attempt_history.get(history_key_user, [])

    if not st.session_state.quiz_started and not st.session_state.submitted:
        st.write(f"**इस चैप्टर में उपलब्ध प्रश्न:** {len(current_questions)}")
        
        opt_c1, opt_c2 = st.columns(2)
        with opt_c1:
            st.session_state.selected_marks = st.selectbox("सही उत्तर के अंक:", [1.0, 2.0, 3.0])
        with opt_c2:
            t_limit = st.selectbox("समय सीमा:", [0, 5, 10, 15, 20], format_func=lambda x: "कोई समय सीमा नहीं" if x==0 else f"{x} मिनट")
            st.session_state.time_limit_seconds = t_limit * 60

        if current_questions:
            if past_attempts:
                if st.button("📊 पिछला रिजल्ट देखें", use_container_width=True):
                    st.session_state.submitted = True
                    st.rerun()
            if st.button("🚀 टेस्ट शुरू करें (Start Test)", type="primary", use_container_width=True):
                st.session_state.quiz_started = True
                st.session_state.start_time = time.time()
                st.session_state.user_answers = {}
                st.rerun()
        else:
            st.warning("इस चैप्टर में अभी कोई प्रश्न नहीं जोड़े गए हैं।")

    elif st.session_state.quiz_started and not st.session_state.submitted:
        if st.session_state.time_limit_seconds > 0:
            elapsed = time.time() - st.session_state.start_time
            remaining = st.session_state.time_limit_seconds - elapsed
            if remaining <= 0:
                st.error("⏰ समय समाप्त!")
                calculate_and_submit_quiz(is_timeout=True)
                st.rerun()
            else:
                st.warning(f"⏱️ शेष समय: {int(remaining//60):02d}:{int(remaining%60):02d} मिनट")

        for idx, q in enumerate(current_questions):
            st.markdown(f"### प्रश्न {idx+1}: {q['question_text']}")
            if q.get("question_image"):
                st.image(q["question_image"], width=450)
            
            opts = [f"A) {q['options_text']['A']}", f"B) {q['options_text']['B']}", f"C) {q['options_text']['C']}", f"D) {q['options_text']['D']}"]
            ans = st.radio(f"उत्तर चुनें {idx+1}:", opts, key=f"q_ans_{idx}", index=None)
            st.session_state.user_answers[idx] = ans[0] if ans else None
            st.write("---")

        if st.button("🏁 टेस्ट सबमिट करें", type="primary"):
            calculate_and_submit_quiz(is_timeout=False)
            st.rerun()

    elif st.session_state.submitted:
        st.header("📊 आपकी परफॉर्मेंस रिपोर्ट")
        last_att = past_attempts[-1] if past_attempts else {}
        
        with st.container(border=True):
            st.metric("प्राप्तांक", last_att.get("प्राप्तांक", "0"))
            st.metric("सटीकता", last_att.get("सटीकता", "0%"))
            st.write(f"**सही प्रश्न:** {last_att.get('सही (Correct)', 0)} | **गलत प्रश्न:** {last_att.get('गलत (Wrong)', 0)}")

        if st.button("🔄 दोबारा टेस्ट दें", type="primary"):
            st.session_state.submitted = False
            st.session_state.quiz_started = False
            st.rerun()
