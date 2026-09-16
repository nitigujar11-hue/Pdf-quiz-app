import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
import os
import pickle
from urllib.parse import quote
from PIL import Image
from streamlit_cropper import st_cropper

st.set_page_config(page_title="ALL SUBJECT TEST", page_icon="📝", layout="wide")

ADMIN_PASSWORD = "NINI@123"
DB_FILE = "app_quiz_database.pkl"

DEFAULT_SUBJECTS = {
    "🔢 Mathematics (गणित)": [
        "Percentage (प्रतिशत)", "Profit & Loss (लाभ और हानि)", "PARTNERSHIP", "Ratio & Proportion (अनुपात)",
        "Simple & Compound Interest", "Time & Work (कार्य और समय)", "Speed, Time & Distance", "TRAIN", 
        "Number System (संख्या पद्धति)", "Average (औसत)", "Mensuration 2D (क्षेत्रमिति 2D)", "MENSURATION 3D", 
        "LCM & HCF", "SIMPLIFICATION", "AGE", "DISCOUNT", "DATA INTERPRETATION"
    ],
    "🧠 Reasoning (तर्कशक्ति)": [
        "Coding-Decoding", "Analogy (सादृश्यता)", "Blood Relation (रक्त संबंध)", "Classification", 
        "Logical Arrangement", "Inserting Missing Characters", "Clock & Calendar", "Sitting Arrangement", 
        "Rankings Test", "Venn Diagram", "Mathematics Operation", "Statement and Conclusion", 
        "Direction & Distance", "Series (श्रृंखला)", "Syllogism (कथन व निष्कर्ष)", "Non-Verbal Reasoning"
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
        "Physics (भौतिक विज्ञान)", "Chemistry (रसायन विज्ञान)", "Biology (जीव विज्ञान)", "OTHER"
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

# 🚀 सुपरफास्ट इन-मेमोरी कैशिंग (बिना लैग के लोड होगा)
@st.cache_data(show_spinner=False)
def load_permanent_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    return {"subjects": DEFAULT_SUBJECTS, "questions": {}, "attempts": {}}

def save_permanent_data():
    payload = {
        "subjects": st.session_state.subjects_data,
        "questions": st.session_state.all_questions_db,
        "attempts": st.session_state.attempt_history
    }
    with open(DB_FILE, "wb") as f:
        pickle.dump(payload, f)
    load_permanent_data.clear()

initial_data = load_permanent_data()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "subjects_data" not in st.session_state:
    st.session_state.subjects_data = initial_data.get("subjects", DEFAULT_SUBJECTS)
if "all_questions_db" not in st.session_state:
    st.session_state.all_questions_db = initial_data.get("questions", {})
if "attempt_history" not in st.session_state:
    st.session_state.attempt_history = initial_data.get("attempts", {})

# क्लीन इंटरफेस
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    div.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    button {transition: transform 0.1s ease-in-out;}
    button:active {transform: scale(0.97);}
    </style>
""", unsafe_allow_html=True)

if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = None
if "selected_chapter" not in st.session_state:
    st.session_state.selected_chapter = None
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

current_key = f"{st.session_state.selected_subject}_{st.session_state.selected_chapter}"
current_questions = st.session_state.all_questions_db.get(current_key, [])

def compress_and_convert_to_bytes(img, max_width=650, quality=65):
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int((float(img.height) * float(ratio)))
        img = img.resize((max_width, new_height), Image.Resampling.BILINEAR)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", optimize=True, quality=quality)
    return buf.getvalue()

def calculate_and_submit_quiz(is_timeout=False):
    st.session_state.submitted = True
    st.session_state.quiz_started = False
    
    total = len(current_questions)
    correct = 0
    wrong = 0
    unattempted = 0
    
    mark_per_q = st.session_state.get("selected_marks", 1.0)
    neg = st.session_state.get("selected_neg", 0.0)

    for idx, q in enumerate(current_questions):
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

    if current_key not in st.session_state.attempt_history:
        st.session_state.attempt_history[current_key] = []

    past_attempts = st.session_state.attempt_history[current_key]
    past_scores = [att.get("raw_score", 0.0) for att in past_attempts]
    all_scores = past_scores + [raw_score]
    all_scores.sort(reverse=True)
    
    current_rank = all_scores.index(raw_score) + 1
    total_participants = len(all_scores)
    
    percentile = (sum(1 for s in all_scores if s < raw_score) / (total_participants - 1) * 100) if total_participants > 1 else 100.0

    attempt_num = len(past_attempts) + 1
    reason = " (समय समाप्त)" if is_timeout else ""
    st.session_state.attempt_history[current_key].append({
        "अटेम्प्ट": f"प्रयास #{attempt_num}{reason}",
        "तारीख": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "raw_score": raw_score,
        "प्राप्तांक": f"{raw_score:.2f} / {max_marks:.0f}",
        "सही (Correct)": correct,
        "गलत (Wrong)": wrong,
        "छोड़े (Skipped)": unattempted,
        "सटीकता": f"{accuracy:.1f}%",
        "रैंक": f"{current_rank} / {total_participants}",
        "पर्सेंटाइल": f"{percentile:.1f}%",
        "user_answers": dict(st.session_state.user_answers)
    })
    save_permanent_data()

@st.dialog("🔐 एडमिन लॉगिन पोर्टल")
def admin_login_dialog():
    st.write("एडमिन कंट्रोल्स के लिए पासवर्ड दर्ज करें:")
    pwd = st.text_input("पासवर्ड:", type="password", key="dlg_pwd")
    if st.button("लॉगिन करें 🚀", type="primary", use_container_width=True):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.rerun()
        else:
            st.error("गलत पासवर्ड!")

# साइडबार
with st.sidebar:
    st.title("🔐 पोर्टल नियंत्रण")
    if st.session_state.is_admin:
        st.success("👨‍🏫 एडमिन मोड")
        if st.button("लॉगआउट"):
            st.session_state.is_admin = False
            st.rerun()

        with st.container(border=True):
            st.markdown("### ⚡ डायरेक्ट लिंक्स")
            st.link_button("📂 GitHub Repo", "https://github.com", use_container_width=True)
            st.link_button("☁️ Streamlit Cloud", "https://share.streamlit.io", use_container_width=True)

        st.divider()
        with st.expander("📁 Editing All", expanded=False):
            tab_subj, tab_chap, tab_q = st.tabs(["📚 विषय", "📑 चैप्टर", "📝 प्रश्न"])
            with tab_subj:
                new_s = st.text_input("विषय:", key="hub_new_subj")
                if st.button("सेव विषय ➕") and new_s.strip():
                    st.session_state.subjects_data[new_s.strip()] = []
                    save_permanent_data()
                    st.rerun()

            with tab_chap:
                all_s = list(st.session_state.subjects_data.keys())
                if all_s:
                    p_s = st.selectbox("विषय:", all_s, key="hub_p_subj")
                    new_c = st.text_input("चैप्टर:", key="hub_new_c")
                    if st.button("सेव चैप्टर ➕") and new_c.strip():
                        st.session_state.subjects_data[p_s].append(new_c.strip())
                        save_permanent_data()
                        st.rerun()

            with tab_q:
                all_s = list(st.session_state.subjects_data.keys())
                if all_s:
                    q_s = st.selectbox("विषय:", all_s, key="hub_q_s")
                    q_c_list = st.session_state.subjects_data.get(q_s, [])
                    if q_c_list:
                        q_c = st.selectbox("चैप्टर:", q_c_list, key="hub_q_c")
                        target_key = f"{q_s}_{q_c}"
                        
                        with st.expander("➕ नया सवाल", expanded=False):
                            q_t = st.text_area("प्रश्न:")
                            q_i = st.file_uploader("फोटो:", type=["png", "jpg", "jpeg"], key="h_qi")
                            final_qi = None
                            if q_i:
                                final_qi = compress_and_convert_to_bytes(Image.open(q_i))

                            oa = st.text_input("A:", key="h_ta")
                            ob = st.text_input("B:", key="h_tb")
                            oc = st.text_input("C:", key="h_tc")
                            od = st.text_input("D:", key="h_td")
                            ans_c = st.selectbox("उत्तर:", ["A", "B", "C", "D"], key="h_corr")
                            sol_i = st.file_uploader("सॉल्यूशन:", type=["png", "jpg", "jpeg"], key="h_sol")
                            final_sol = None
                            if sol_i:
                                final_sol = compress_and_convert_to_bytes(Image.open(sol_i))

                            if st.button("सेव सवाल 💾"):
                                if target_key not in st.session_state.all_questions_db:
                                    st.session_state.all_questions_db[target_key] = []
                                st.session_state.all_questions_db[target_key].append({
                                    "question_text": q_t if q_t else "फोटो देखें:",
                                    "question_image": final_qi,
                                    "options_text": {"A": oa, "B": ob, "C": oc, "D": od},
                                    "options_image": {},
                                    "answer": ans_c,
                                    "sol_image": final_sol
                                })
                                save_permanent_data()
                                st.success("सेव हो गया!")
                                st.rerun()

# 📲 सुपरफास्ट WhatsApp शेयर बटन (डायरेक्ट लिंक)
h_col1, h_col2 = st.columns([3, 1.2])
with h_col2:
    msg = quote("🚀 ऑनलाइन मॉक टेस्ट पोर्टल: यहाँ सभी विषयों के अध्यायवार टेस्ट उपलब्ध हैं। अभी अभ्यास शुरू करें!")
    st.markdown(f"""
        <div style="text-align: right; margin-bottom: 8px;">
            <a href="https://api.whatsapp.com/send?text={msg}" target="_blank" style="
                background-color: #25D366;
                color: white;
                text-decoration: none;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 20px;
                display: inline-block;
            ">📲 शेयर करें</a>
        </div>
    """, unsafe_allow_html=True)

def render_solution_card(index_list, answers_dict, empty_msg="कोई प्रश्न उपलब्ध नहीं।"):
    if not index_list:
        st.info(empty_msg)
        return

    for idx in index_list:
        q = current_questions[idx]
        ans = answers_dict.get(idx)
        badge = "⚪ अनअटेम्प्ट" if ans is None else ("✅ सही" if ans == q['answer'] else "❌ गलत")

        with st.expander(f"प्रश्न {idx+1} [{badge}] : {q['question_text'][:35]}..."):
            st.markdown(f"**प्रश्न {idx+1}:** {q['question_text']}")
            if q.get("question_image"):
                st.image(q["question_image"], width=360)

            st.write(f"**A)** {q['options_text']['A']}")
            st.write(f"**B)** {q['options_text']['B']}")
            st.write(f"**C)** {q['options_text']['C']}")
            st.write(f"**D)** {q['options_text']['D']}")
            st.write("---")
            st.write(f"**आपका चयन:** {ans if ans else 'छोड़ दिया'}")
            st.write(f"**सही उत्तर:** :green[**विकल्प {q['answer']}**]")
            if q.get('sol_image'):
                st.image(q['sol_image'], width=380)

# ==========================================
# 🎯 1. मुख्य स्क्रीन: डैशबोर्ड
# ==========================================
if st.session_state.selected_subject is None:
    st.title("🎯 परीक्षा तैयारी पोर्टल")
    st.caption("अध्यायवार टेस्ट दें और रियल-टाइम परफॉर्मेंस ट्रैक करें।")

    all_s = list(st.session_state.subjects_data.keys())
    m1, m2, m3 = st.columns(3)
    m1.metric("📚 कुल विषय", f"{len(all_s)}")
    m2.metric("📝 कुल प्रश्न", f"{sum(len(v) for v in st.session_state.all_questions_db.values())}")
    m3.metric("🏆 टेस्ट प्रयास", f"{sum(len(v) for v in st.session_state.attempt_history.values())}")

    st.write("---")
    cols = st.columns(3)
    for index, subj in enumerate(all_s):
        with cols[index % 3]:
            with st.container(border=True):
                st.write(f"**{subj}**")
                st.caption(f"चैप्टर: {len(st.session_state.subjects_data.get(subj, []))}")
                if st.button("अभ्यास शुरू करें ➔", key=f"subj_{index}", use_container_width=True):
                    st.session_state.selected_subject = subj
                    st.rerun()

    st.write("---")
    if not st.session_state.is_admin and st.button("🔑 एडमिन लॉगिन"):
        admin_login_dialog()

# --- 2. मुख्य स्क्रीन: अध्याय चयन ---
elif st.session_state.selected_chapter is None:
    if st.button("⬅ वापस"):
        st.session_state.selected_subject = None
        st.rerun()
    st.title(f"{st.session_state.selected_subject}")
    
    chaps = st.session_state.subjects_data.get(st.session_state.selected_subject, [])
    cols = st.columns(2)
    for index, chap in enumerate(chaps):
        with cols[index % 2]:
            st.container(border=True).write(f"📑 **{chap}**")
            if st.button("मॉक टेस्ट लगाएं ✍️", key=f"chap_{index}", use_container_width=True):
                st.session_state.selected_chapter = chap
                st.rerun()

# --- 3. मुख्य स्क्रीन: टेस्ट व रिजल्ट ---
else:
    if st.button("⬅ वापस जाएं"):
        st.session_state.selected_chapter = None
        st.session_state.quiz_started = False
        st.session_state.submitted = False
        st.session_state.user_answers = {}
        st.rerun()

    st.subheader(f"📌 {st.session_state.selected_chapter}")
    past_attempts = st.session_state.attempt_history.get(current_key, [])

    if not st.session_state.quiz_started and not st.session_state.submitted:
        st.write(f"**उपलब्ध प्रश्न:** {len(current_questions)}")
        o1, o2, o3 = st.columns(3)
        with o1: st.session_state.selected_marks = st.selectbox("सही अंक:", [1.0, 2.0, 3.0])
        with o2: st.session_state.selected_neg = st.selectbox("नेगेटिव:", [0.0, 0.25, 0.50])
        with o3:
            tc = st.selectbox("समय:", [0, 5, 10, 15, 20], format_func=lambda x: "No Limit" if x==0 else f"{x} min")
            st.session_state.time_limit_seconds = tc * 60

        if len(current_questions) > 0:
            if past_attempts:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📊 पिछला रिजल्ट देखें", use_container_width=True):
                        st.session_state.submitted = True
                        st.rerun()
                with c2:
                    if st.button("🔄 दोबारा टेस्ट दें", type="primary", use_container_width=True):
                        st.session_state.quiz_started = True
                        st.session_state.start_time = time.time()
                        st.session_state.user_answers = {}
                        st.rerun()
            else:
                if st.button("🚀 स्टार्ट टेस्ट", type="primary", use_container_width=True):
                    st.session_state.quiz_started = True
                    st.session_state.start_time = time.time()
                    st.rerun()
        else:
            st.warning("कोई प्रश्न नहीं हैं।")

    elif st.session_state.quiz_started and not st.session_state.submitted:
        if st.session_state.time_limit_seconds > 0:
            rem = st.session_state.time_limit_seconds - (time.time() - st.session_state.start_time)
            if rem <= 0:
                calculate_and_submit_quiz(is_timeout=True)
                st.rerun()
            st.warning(f"⏱️ शेष समय: {int(rem//60):02d}:{int(rem%60):02d}")

        for idx, q in enumerate(current_questions):
            st.markdown(f"**प्रश्न {idx+1}:** {q['question_text']}")
            if q.get("question_image"):
                st.image(q["question_image"], width=400)

            opts = [f"A) {q['options_text']['A']}", f"B) {q['options_text']['B']}", f"C) {q['options_text']['C']}", f"D) {q['options_text']['D']}"]
            ans = st.radio(f"उत्तर {idx+1}:", opts, key=f"q_{idx}", index=None)
            st.session_state.user_answers[idx] = ans[0] if ans else None
            st.write("---")

        if st.button("🏁 टेस्ट सबमिट करें", type="primary"):
            calculate_and_submit_quiz()
            st.rerun()

    elif st.session_state.submitted:
        st.header("📊 रिजल्ट")
        last_att = past_attempts[-1] if past_attempts else {}
        ans_map = last_att.get("user_answers", st.session_state.user_answers)

        c1, c2, c3 = st.columns(3)
        c1.metric("🎯 स्कोर", last_att.get("प्राप्तांक", "0"))
        c2.metric("✅ सही", last_att.get("सही (Correct)", 0))
        c3.metric("❌ गलत", last_att.get("गलत (Wrong)", 0))

        cor_idx = [i for i, q in enumerate(current_questions) if ans_map.get(i) == q['answer']]
        inc_idx = [i for i, q in enumerate(current_questions) if ans_map.get(i) is not None and ans_map.get(i) != q['answer']]
        una_idx = [i for i, q in enumerate(current_questions) if ans_map.get(i) is None]

        t_all, t_c, t_i, t_u = st.tabs(["📑 सभी", f"✅ सही ({len(cor_idx)})", f"❌ गलत ({len(inc_idx)})", f"⚪ अनअटेम्प्ट ({len(una_idx)})"])
        with t_all: render_solution_card(list(range(len(current_questions))), ans_map)
        with t_c: render_solution_card(cor_idx, ans_map)
        with t_i: render_solution_card(inc_idx, ans_map)
        with t_u: render_solution_card(una_idx, ans_map)

        st.write("---")
        if st.button("🔄 Re-attempt Test (दोबारा टेस्ट दें)", type="primary", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.quiz_started = True
            st.session_state.start_time = time.time()
            st.session_state.user_answers = {}
            st.rerun()
