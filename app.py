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

st.set_page_config(page_title="RWA Style Home Portal", page_icon="📝", layout="wide")

# ==========================================
# 🎨 RWA जैसी होमपेज ग्रिड और कार्ड थीम CSS
# ==========================================
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .hero-banner {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        text-align: center;
    }
    .grid-card {
        background: #ffffff;
        padding: 20px 10px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
        margin-bottom: 15px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .grid-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15);
        border-color: #3b82f6;
    }
    .grid-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }
    .grid-title {
        font-size: 14px;
        font-weight: 600;
        color: #1e293b;
    }
    .test-card {
        background: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 12px;
        border-left: 4px solid #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 डेटाबेस कॉन्फ़िगरेशन
# ==========================================
ADMIN_PASSWORD = "NINI@123"
DB_FILE = "app_quiz_database_rwa_home.pkl"

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
# 🔐 लॉगिन स्क्रीन
# ==========================================
if st.session_state.logged_in_user is None:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📚 RWA Portal Login</h2>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_admin, tab_signup, tab_forgot = st.tabs(["🔑 यूजर लॉगिन", "👨‍🏫 एडमिन", "📝 नया अकाउंट", "🔄 रिकवर"])

        with tab_login:
            log_mob = st.text_input("मोबाइल नंबर:", key="u_log_mob")
            log_pass = st.text_input("पासवर्ड:", type="password", key="u_log_pass")
            if st.button("लॉगिन करें 🚀", type="primary", use_container_width=True):
                log_mob = log_mob.strip()
                if log_mob in st.session_state.users_db and st.session_state.users_db[log_mob]["password"] == log_pass:
                    st.session_state.logged_in_user = log_mob
                    st.session_state.user_role = "user"
                    st.rerun()
                else:
                    st.error("गलत मोबाइल नंबर या पासवर्ड!")

        with tab_admin:
            admin_pwd_input = st.text_input("एडमिन पासवर्ड:", type="password", key="adm_direct_pass")
            if st.button("एडमिन लॉगिन 🔐", type="primary", use_container_width=True):
                if admin_pwd_input == ADMIN_PASSWORD:
                    st.session_state.logged_in_user = "ADMIN"
                    st.session_state.user_role = "admin"
                    st.rerun()
                else:
                    st.error("गलत पासवर्ड!")

        with tab_signup:
            new_name = st.text_input("पूरा नाम:", key="sign_name")
            new_mob = st.text_input("मोबाइल नंबर:", key="sign_mob")
            new_pass = st.text_input("पासवर्ड:", type="password", key="sign_pass")
            if st.button("अकाउंट बनाएं ➔", type="primary", use_container_width=True):
                new_mob = new_mob.strip()
                if new_mob and new_mob not in st.session_state.users_db:
                    st.session_state.users_db[new_mob] = {"name": new_name, "password": new_pass}
                    save_permanent_data()
                    st.success("सफल! अब लॉगिन करें।")
                else:
                    st.error("विवरण जांचें या नंबर पहले से रजिस्टर्ड है।")

        with tab_forgot:
            f_mob = st.text_input("रजिस्टर्ड मोबाइल:", key="f_mob")
            f_new_pass = st.text_input("नया पासवर्ड:", type="password", key="f_new_pass")
            if st.button("अपडेट करें 🔄", use_container_width=True):
                f_mob = f_mob.strip()
                if f_mob in st.session_state.users_db:
                    st.session_state.users_db[f_mob]["password"] = f_new_pass
                    save_permanent_data()
                    st.success("पासवर्ड बदल गया!")
                else:
                    st.error("नंबर नहीं मिला।")
    st.stop()

current_user = st.session_state.logged_in_user
is_admin_user = (st.session_state.user_role == "admin")

# ==========================================
# ⚡ ऑटो-कंप्रेसर
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
        img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", optimize=True, quality=quality)
    return buf.getvalue()

def calculate_and_submit_quiz(is_timeout=False):
    st.session_state.submitted = True
    st.session_state.quiz_started = False
    questions_list = st.session_state.active_questions_list
    total = len(questions_list)
    correct, wrong, unattempted = 0, 0, 0
    mark_per_q = st.session_state.get("selected_marks", 1.0)
    neg = st.session_state.get("selected_neg", 0.0)

    for idx, q in enumerate(questions_list):
        ans = st.session_state.user_answers.get(idx)
        if ans is None: unattempted += 1
        elif ans == q['answer']: correct += 1
        else: wrong += 1

    max_marks = total * mark_per_q
    raw_score = (correct * mark_per_q) - (wrong * neg)
    accuracy = (correct / (correct + wrong) * 100) if (correct + wrong) > 0 else 0

    history_key = f"{current_user}_{st.session_state.current_test_key}"
    if history_key not in st.session_state.attempt_history:
        st.session_state.attempt_history[history_key] = []
    
    past_attempts = st.session_state.attempt_history[history_key]
    st.session_state.attempt_history[history_key].append({
        "अटेम्प्ट": f"प्रयास #{len(past_attempts) + 1}{' (समय समाप्त)' if is_timeout else ''}",
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

# --- साइडबार ---
with st.sidebar:
    st.title("👤 यूजर पैनल")
    if is_admin_user:
        st.success("👨‍🏫 एडमिन मोड")
    else:
        u_inf = st.session_state.users_db.get(current_user, {})
        st.write(f"**नाम:** {u_inf.get('name', 'User')}")
        st.write(f"**मो.:** {current_user}")
    
    if st.button("🚪 लॉगआउट", type="secondary", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()

# स्टेट वेरिएबल्स
if "nav_page" not in st.session_state: st.session_state.nav_page = "home" # "home", "free_weekly_tests", "full_mock"
if "selected_subject" not in st.session_state: st.session_state.selected_subject = None
if "selected_chapter" not in st.session_state: st.session_state.selected_chapter = None
if "quiz_started" not in st.session_state: st.session_state.quiz_started = False
if "submitted" not in st.session_state: st.session_state.submitted = False
if "user_answers" not in st.session_state: st.session_state.user_answers = {}
if "start_time" not in st.session_state: st.session_state.start_time = None
if "time_limit_seconds" not in st.session_state: st.session_state.time_limit_seconds = 0

# ==========================================
# 🏠 होम पेज (9 Grid Cards जैसा स्क्रीनशॉट में है)
# ==========================================
if st.session_state.nav_page == "home":
    st.markdown("""
        <div class="hero-banner">
            <h3 style="color: #1E3A8A; margin:0;">🌟 WELCOME TO TEST PORTAL</h3>
            <p style="color: #64748b; font-size: 13px; margin: 5px 0 0 0;">Free Weekly Test | PDF Notes | Test Series</p>
        </div>
    """, unsafe_allow_html=True)

    # 9 ग्रिड आइकॉन लेआउट (स्क्रीनशॉट के अनुसार)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown('<div class="grid-card"><div class="grid-icon">📚</div><div class="grid-title">Paid Classes</div></div>', unsafe_allow_html=True)
        if st.button("ओपन Paid Classes", key="btn_pc", use_container_width=True): st.info("यह सेक्शन जल्द उपलब्ध होगा!")
    with c2:
        st.markdown('<div class="grid-card"><div class="grid-icon">📖</div><div class="grid-title">Free Courses</div></div>', unsafe_allow_html=True)
        if st.button("ओपन Free Courses", key="btn_fc", use_container_width=True): st.info("यह सेक्शन जल्द उपलब्ध होगा!")
    with c3:
        st.markdown('<div class="grid-card" style="border-color: #3b82f6;"><div class="grid-icon">📝</div><div class="grid-title" style="color:#1E3A8A;">Free Weekly Tests</div></div>', unsafe_allow_html=True)
        if st.button("👉 क्लिक करें (टेस्ट दें)", key="btn_fwt", use_container_width=True, type="primary"):
            st.session_state.nav_page = "free_weekly_tests"
            st.rerun()

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown('<div class="grid-card"><div class="grid-icon">📊</div><div class="grid-title">Test Series</div></div>', unsafe_allow_html=True)
        if st.button("ओपन Test Series", key="btn_ts", use_container_width=True): st.info("जल्द उपलब्ध!")
    with c5:
        st.markdown('<div class="grid-card"><div class="grid-icon">📁</div><div class="grid-title">PDF Class Notes</div></div>', unsafe_allow_html=True)
        if st.button("ओपन PDF Notes", key="btn_pn", use_container_width=True): st.info("जल्द उपलब्ध!")
    with c6:
        st.markdown('<div class="grid-card"><div class="grid-icon">📖</div><div class="grid-title">Books</div></div>', unsafe_allow_html=True)
        if st.button("ओपन Books", key="btn_bk", use_container_width=True): st.info("जल्द उपलब्ध!")

    c7, c8, c9 = st.columns(3)
    with c7:
        st.markdown('<div class="grid-card"><div class="grid-icon">📋</div><div class="grid-title">Syllabus</div></div>', unsafe_allow_html=True)
        if st.button("ओपन Syllabus", key="btn_sy", use_container_width=True): st.info("जल्द उपलब्ध!")
    with c8:
        st.markdown('<div class="grid-card"><div class="grid-icon">⏰</div><div class="grid-title">Timetable</div></div>', unsafe_allow_html=True)
        if st.button("ओपन Timetable", key="btn_tt", use_container_width=True): st.info("जल्द उपलब्ध!")
    with c9:
        st.markdown('<div class="grid-card"><div class="grid-icon">🎯</div><div class="grid-title">Previous Year</div></div>', unsafe_allow_html=True)
        if st.button("ओपन Previous Year", key="btn_py", use_container_width=True): st.info("जल्द उपलब्ध!")

# ==========================================
# 📑 फ्री वीकली टेस्ट के अंदर सब्जेक्ट्स लिस्ट
# ==========================================
elif st.session_state.nav_page == "free_weekly_tests":
    if st.button("⬅ होम पेज पर जाएं"):
        st.session_state.nav_page = "home"
        st.session_state.selected_subject = None
        st.session_state.selected_chapter = None
        st.rerun()

    # --- 1. विषय चयन स्क्रीन ---
    if st.session_state.selected_subject is None:
        st.markdown("### 📄 Free Weekly Tests - विषय सूची")
        all_active_subjects = list(st.session_state.subjects_data.keys())

        for index, subj in enumerate(all_active_subjects):
            chaps = st.session_state.subjects_data.get(subj, [])
            st.markdown(f"""
                <div class="test-card">
                    <b>{subj}</b><br><span style="font-size: 12px; color: #64748b;">कुल चैप्टर्स: {len(chaps)}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"ओपन करें ➔", key=f"subj_btn_{index}", use_container_width=True):
                st.session_state.selected_subject = subj
                st.rerun()
            st.write("")

        if is_admin_user:
            st.write("---")
            with st.expander("➕ नया विषय जोड़ें (एडमिन)"):
                new_s = st.text_input("विषय का नाम:")
                if st.button("विषय सेव करें"):
                    if new_s.strip() and new_s not in st.session_state.subjects_data:
                        st.session_state.subjects_data[new_s.strip()] = []
                        save_permanent_data()
                        st.success("विषय जुड़ गया!")
                        st.rerun()

    # --- 2. चैप्टर चयन स्क्रीन ---
    elif st.session_state.selected_chapter is None:
        st.button("⬅ विषयों की सूची पर जाएं", on_click=lambda: st.session_state.update({"selected_subject": None}))
        st.title(f"📁 {st.session_state.selected_subject}")
        st.write("### चैप्टर चुनें:")
        st.write("---")

        chapters = st.session_state.subjects_data.get(st.session_state.selected_subject, [])
        for index, chap in enumerate(chapters):
            st.markdown(f"""
                <div class="test-card">
                    <b>📑 {chap}</b>
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

    # --- 3. मॉक टेस्ट और प्रश्न स्क्रीन ---
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
                with st.form(key=f"q_form_{len(current_questions)}"):
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
                            "question_text": q_t if q_t else "फोटो देखें:",
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
                        st.success("✅ प्रश्न सेव हो गया! अगला प्रश्न दर्ज करें।")
                        time.sleep(0.4)
                        st.rerun()

        history_key_user = f"{current_user}_{current_test_key}"
        past_attempts = st.session_state.attempt_history.get(history_key_user, [])

        if not st.session_state.quiz_started and not st.session_state.submitted:
            st.write(f"**उपलब्ध प्रश्न:** {len(current_questions)}")
            c1, c2 = st.columns(2)
            with c1: st.session_state.selected_marks = st.selectbox("सही उत्तर के अंक:", [1.0, 2.0, 3.0])
            with c2:
                t_limit = st.selectbox("समय सीमा:", [0, 5, 10, 15, 20], format_func=lambda x: "असीमित" if x==0 else f"{x} मिनट")
                st.session_state.time_limit_seconds = t_limit * 60

            if current_questions:
                if past_attempts and st.button("📊 पिछला रिजल्ट देखें", use_container_width=True):
                    st.session_state.submitted = True
                    st.rerun()
                if st.button("🚀 टेस्ट शुरू करें", type="primary", use_container_width=True):
                    st.session_state.quiz_started = True
                    st.session_state.start_time = time.time()
                    st.session_state.user_answers = {}
                    st.rerun()
            else:
                st.warning("इस चैप्टर में अभी कोई प्रश्न नहीं हैं।")

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
            st.header("📊 परफॉर्मेंस रिपोर्ट")
            last_att = past_attempts[-1] if past_attempts else {}
            with st.container(border=True):
                st.metric("प्राप्तांक", last_att.get("प्राप्तांक", "0"))
                st.metric("सटीकता", last_att.get("सटीकता", "0%"))
            if st.button("🔄 दोबारा टेस्ट दें", type="primary"):
                st.session_state.submitted = False
                st.session_state.quiz_started = False
                st.rerun()
