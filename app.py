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

st.set_page_config(page_title="ALL SUBJECT TEST", page_icon="📝", layout="wide")

# ==========================================
# 🔐 डेटाबेस कॉन्फ़िगरेशन
# ==========================================
DB_FILE = "app_quiz_database_v2.pkl"

DEFAULT_SUBJECTS = {
    "🔢 Mathematics": [
        "Percentage", "Profit & Loss", "PARTNERSHIP", "Ratio & Proportion",
        "Simple & Compound Interest", "Time & Work", "Speed, Time & Distance", "TRAIN", 
        "Number System", "Average", "Mensuration 2D", "MENSURATION 3D", 
        "LCM & HCF", "SIMPLIFICATION", "AGE", "DISCOUNT", "DATA INTERPRETATION"
    ],
    "🧠 Reasoning": [
        "Coding-Decoding", "Analogy", "Blood Relation", "Classification", 
        "Logical Arrangement", "Inserting Missing Characters", "Clock & Calendar", "Sitting Arrangement", 
        "Rankings Test", "Venn Diagram", "Mathematics Operation", "Statement and Conclusion", 
        "Direction & Distance", "Series", "Syllogism", "Non-Verbal Reasoning"
    ],
    "🌍 Indian Geography": [
        "भारत की नदियाँ एवं झीलें", "पर्वत एवं पठार", "जलवायु एवं मानसून", "कृषि एवं खनिज संसाधन", 
        "राष्ट्रीय उद्यान एवं अभयारण्य", "Other"
    ],
    "🏛️ Indian Polity": [
        "संविधान की प्रस्तावना व स्रोत", "मौलिक अधिकार एवं कर्तव्य", "राष्ट्रपति एवं संसद", 
        "न्यायपालिका (Supreme Court)", "पंचायती राज व संशोधन", "OTHER"
    ],
    "💡 General Science": [
        "Physics", "Chemistry", "Biology", "OTHER"
    ],
    "🏆 Static GK": [
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
# 💾 डेटाबेस लोड एवं सेव फंक्शन (मल्टी-यूजर सपोर्ट)
# ==========================================
def load_permanent_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    # डिफ़ॉल्ट एडमिन क्रेडेंशियल (Mobile: 9999999999, Password: admin)
    return {
        "subjects": DEFAULT_SUBJECTS, 
        "questions": {}, 
        "full_mock_questions": {}, # Full mock database
        "attempts": {}, 
        "users": {"9999999999": {"name": "Admin", "password": "admin", "role": "admin"}}
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
    st.session_state.logged_in_user = None  # None, "admin", or mobile_number
if "user_role" not in st.session_state:
    st.session_state.user_role = None  # "admin" or "user"
if "subjects_data" not in st.session_state:
    st.session_state.subjects_data = initial_data.get("subjects", DEFAULT_SUBJECTS)
if "all_questions_db" not in st.session_state:
    st.session_state.all_questions_db = initial_data.get("questions", {})
if "full_mock_db" not in st.session_state:
    st.session_state.full_mock_db = initial_data.get("full_mock_questions", {})
if "attempt_history" not in st.session_state:
    st.session_state.attempt_history = initial_data.get("attempts", {})

# ==========================================
# 🔐 लॉगिन / साइनअप / फॉरगॉट पासवर्ड स्क्रीन (RWA Style Login)
# ==========================================
if st.session_state.logged_in_user is None:
    st.markdown("""
        <style>
        .login-card {
            background: #f8fafc;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            max-width: 450px;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📚 ALL SUBJECT TEST PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>अपनी तैयारी को परखें और सफलता सुनिश्चित करें</p>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup, tab_forgot = st.tabs(["🔑 लॉगिन", "📝 नया अकाउंट", "🔄 पासवर्ड भूल गए"])

        with tab_login:
            st.write("### अपने खाते में लॉगिन करें")
            login_mobile = st.text_input("मोबाइल नंबर (Mobile Number):", key="log_mob")
            login_pass = st.text_input("पासवर्ड (Password):", type="password", key="log_pass")
            
            if st.button("लॉगिन करें 🚀", type="primary", use_container_width=True):
                login_mobile = login_mobile.strip()
                if login_mobile in st.session_state.users_db:
                    if st.session_state.users_db[login_mobile]["password"] == login_pass:
                        st.session_state.logged_in_user = login_mobile
                        st.session_state.user_role = st.session_state.users_db[login_mobile]["role"]
                        st.success("सफलतापूर्वक लॉगिन हो गया!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("गलत पासवर्ड! कृपया दोबारा जांच करें।")
                else:
                    st.error("यह मोबाइल नंबर पंजीकृत नहीं है। कृपया नया अकाउंट बनाएं।")

        with tab_signup:
            st.write("### नया यूजर रजिस्ट्रेशन")
            new_name = st.text_input("पूरा नाम (Full Name):", key="sign_name")
            new_mob = st.text_input("मोबाइल नंबर (Mobile Number):", key="sign_mob")
            new_pass = st.text_input("नया पासवर्ड बनाएं (Password):", type="password", key="sign_pass")
            
            if st.button("अकाउंट बनाएं ➔", type="primary", use_container_width=True):
                new_mob = new_mob.strip()
                if not new_name or not new_mob or not new_pass:
                    st.warning("कृपया सभी जानकारी भरें!")
                elif new_mob in st.session_state.users_db:
                    st.error("यह मोबाइल नंबर पहले से रजिस्टर्ड है। कृपया लॉगिन करें।")
                else:
                    st.session_state.users_db[new_mob] = {
                        "name": new_name,
                        "password": new_pass,
                        "role": "user"
                    }
                    save_permanent_data()
                    st.success("अकाउंट सफलतापूर्वक बन गया! अब आप लॉगिन टैब से लॉगिन कर सकते हैं।")

        with tab_forgot:
            st.write("### पासवर्ड रीसेट करें")
            f_mob = st.text_input("अपना रजिस्टर्ड मोबाइल नंबर:", key="f_mob")
            f_new_pass = st.text_input("नया पासवर्ड सेट करें:", type="password", key="f_new_pass")
            
            if st.button("पासवर्ड अपडेट करें 🔄", use_container_width=True):
                f_mob = f_mob.strip()
                if f_mob in st.session_state.users_db:
                    st.session_state.users_db[f_mob]["password"] = f_new_pass
                    save_permanent_data()
                    st.success("पासवर्ड सफलतापूर्वक बदल गया है! अब लॉगिन करें।")
                else:
                    st.error("यह मोबाइल नंबर हमारे डेटाबेस में नहीं मिला।")
    
    st.stop()  # लॉगिन होने तक आगे का कोड नहीं चलेगा

# ==========================================
# 👁️ एडमिन / यूजर सेशन सेटअप
# ==========================================
current_user = st.session_state.logged_in_user
is_admin_user = (st.session_state.user_role == "admin")

# ==========================================
# ⚡ ऑटो-कंप्रेसर फंक्शन (500 Error Fix)
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
# 📊 टेस्ट सबमिट एवं व्यक्तिगत यूजर स्कोर गणना
# ==========================================
def calculate_and_submit_quiz(is_timeout=False, is_full_mock=False):
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

    # हर यूजर का डेटा अलग स्टोर होगा ताकि मिक्स न हो
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

# --- साइडबार: यूजर/एडमिन कंट्रोल्स ---
with st.sidebar:
    st.title("👤 यूजर पैनल")
    user_info = st.session_state.users_db.get(current_user, {})
    st.write(f"**नाम:** {user_info.get('name', 'User')}")
    st.write(f"**मोबाइल:** {current_user}")
    st.write(f"**रोल:** {'👨‍🏫 Admin' if is_admin_user else '👨‍🎓 Student'}")
    
    if st.button("🚪 लॉगआउट (Logout)", type="secondary", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.user_role = None
        st.rerun()

    if is_admin_user:
        st.divider()
        st.subheader("🛠️ एडमिन मास्टर पैनल")
        with st.expander("👥 सभी रजिस्टर्ड यूजर्स देखें"):
            for u_mob, u_data in st.session_state.users_db.items():
                st.write(f"**नाम:** {u_data.get('name')} | **मो.:** {u_mob} | **पासवर्ड:** {u_data.get('password')}")

        with st.expander("📊 यूजर का टेस्ट डेटा देखें"):
            sel_u = st.selectbox("यूजर चुनें:", list(st.session_state.users_db.keys()), format_func=lambda x: f"{st.session_state.users_db[x]['name']} ({x})")
            user_attempts_all = {k: v for k, v in st.session_state.attempt_history.items() if k.startswith(sel_u)}
            if user_attempts_all:
                for k, v in user_attempts_all.items():
                    st.write(f"**टेस्ट:** {k.replace(sel_u+'_', '')}")
                    for att in v:
                        st.json(att)
            else:
                st.caption("इस यूजर ने अभी कोई टेस्ट नहीं दिया है।")

# स्टेट इनिशियलाइजेशन
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
# 📲 टॉप हेडर: शेयर बटन व फुल मॉक आइकॉन (Top Middle)
# ==========================================
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    # टॉप-मिडिल में फुल मॉक बटन (RWA स्टाइल आइकॉन)
    if st.button("🏆 Full Mock Test (फुल मॉक)", use_container_width=True, type="primary"):
        st.session_state.is_full_mock_mode = True
        st.session_state.selected_subject = None
        st.session_state.selected_chapter = None
        st.session_state.quiz_started = False
        st.session_state.submitted = False
        st.rerun()

with col_h3:
    components.html("""
    <div style="text-align: right; margin-top: 5px;">
        <button id="shareBtn" style="
            background: linear-gradient(135deg, #25D366, #128C7E);
            color: white; border: none; padding: 6px 12px; font-size: 13px; font-weight: bold; border-radius: 15px; cursor: pointer;
        ">📲 शेयर करें</button>
    </div>
    <script>
    document.getElementById('shareBtn').addEventListener('click', async () => {
        if (navigator.share) {
            try { await navigator.share({title: 'ALL SUBJECT TEST', url: window.location.href}); } catch(e){}
        } else {
            navigator.clipboard.writeText(window.location.href);
            alert('लिंक कॉपी हो गया!');
        }
    });
    </script>
    """, height=40)

# ==========================================
# 🎯 1. फुल मॉक टेस्ट स्क्रीन (Top Middle Icon Clicked)
# ==========================================
if st.session_state.is_full_mock_mode:
    st.button("⬅ वापस डैशबोर्ड पर जाएं", on_click=lambda: st.session_state.update({"is_full_mock_mode": False}))
    st.title("🏆 Full Length Mock Test Portal")
    st.write("---")

    fm_key = "full_mock_main_exam"
    st.session_state.current_test_key = fm_key
    full_mock_questions = st.session_state.full_mock_db.get(fm_key, [])
    st.session_state.active_questions_list = full_mock_questions

    if is_admin_user:
        with st.expander("➕ फुल मॉक में नया प्रश्न जोड़ें (एडमिन)", expanded=False):
            with st.form("fm_add_q_form"):
                fm_qt = st.text_area("प्रश्न टेक्स्ट:")
                fm_i = st.file_uploader("प्रश्न फोटो (वैकल्पिक):", type=["png", "jpg", "jpeg"])
                
                c1, c2 = st.columns(2)
                with c1: 
                    fm_oa = st.text_input("विकल्प A")
                    fm_oc = st.text_input("विकल्प C")
                with c2: 
                    fm_ob = st.text_input("विकल्प B")
                    fm_od = st.text_input("विकल्प D")
                
                fm_ans = st.selectbox("सही उत्तर:", ["A", "B", "C", "D"])
                
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

    if not st.session_state.quiz_session_active and not st.session_state.submitted:
        st.write(f"**उपलब्ध फुल मॉक प्रश्न:** {len(full_mock_questions)}")
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.session_state.selected_marks = st.selectbox("अंक प्रति प्रश्न:", [1.0, 2.0, 4.0], key="fm_marks")
        with c_m2:
            fm_time = st.selectbox("समय सीमा:", [0, 30, 60, 90, 120], format_func=lambda x: "असीमित" if x==0 else f"{x} मिनट", key="fm_time")
            st.session_state.time_limit_seconds = fm_time * 60

        if full_mock_questions:
            if st.button("🚀 फुल मॉक टेस्ट शुरू करें", type="primary", use_container_width=True):
                st.session_state.quiz_session_active = True
                st.session_state.start_time = time.time()
                st.session_state.user_answers = {}
                st.rerun()
        else:
            st.warning("फिलहाल कोई फुल मॉक प्रश्न उपलब्ध नहीं हैं। (एडमिन द्वारा जोड़े जाने बाकी हैं)")

    elif st.session_state.quiz_session_active:
        # लाइव टाइमर लॉजिक
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
            st.session_state.quiz_session_active = False
            st.rerun()

# ==========================================
# 🎯 2. मुख्य विषय एवं चैप्टर स्क्रीन (RWA Style Grid Icons)
# ==========================================
elif st.session_state.selected_subject is None:
    st.markdown("### 📖 विषय सूची (Subjects)")
    st.caption("नीचे दिए गए आइकॉन पर क्लिक करके अपने विषयों के मॉक टेस्ट दें:")

    all_active_subjects = list(st.session_state.subjects_data.keys())
    cols = st.columns(3)
    
    # RWA स्टाइल आइकॉन डिजाइन
    for index, subj in enumerate(all_active_subjects):
        with cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"<h3 style='text-align: center;'>{subj}</h3>", unsafe_allow_html=True)
                chaps = st.session_state.subjects_data.get(subj, [])
                st.caption(f"📑 कुल चैप्टर: {len(chaps)}")
                if st.button(f"ओपन करें ➔", key=f"subj_btn_{index}", use_container_width=True, type="primary"):
                    st.session_state.selected_subject = subj
                    st.rerun()

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
    st.write("### चैप्टर चुनें:")
    st.write("---")

    chapters = st.session_state.subjects_data.get(st.session_state.selected_subject, [])
    cols = st.columns(2)
    for index, chap in enumerate(chapters):
        with cols[index % 2]:
            with st.container(border=True):
                st.write(f"📑 **{chap}**")
                if st.button("टेस्ट लगाएं ✍️", key=f"chap_click_{index}", use_container_width=True):
                    st.session_state.selected_chapter = chap
                    st.rerun()

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

    # एडमिन के लिए उसी सब्जेक्ट/चैप्टर के अंदर प्रश्न जोड़ने का सेक्शन
    if is_admin_user:
        with st.expander("➕ इस चैप्टर में नया प्रश्न जोड़ें (एडमिन)", expanded=False):
            with st.form("chapter_add_q_form"):
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
                    st.success("✅ प्रश्न सफलतापूर्वक सेव हो गया! अब अगला प्रश्न दर्ज कर सकते हैं।")
                    time.sleep(0.8)
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
        # फिक्स किया हुआ लाइव टाइमर
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
