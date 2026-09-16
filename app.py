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
# 🔐 एडमिन पासवर्ड एवं डेटाबेस कॉन्फ़िगरेशन
# ==========================================
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

# ==========================================
# 💾 2-WAY SYNC: डेटाबेस लोड एवं सेव फंक्शन
# ==========================================
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

initial_data = load_permanent_data()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "subjects_data" not in st.session_state:
    st.session_state.subjects_data = initial_data.get("subjects", DEFAULT_SUBJECTS)
if "all_questions_db" not in st.session_state:
    st.session_state.all_questions_db = initial_data.get("questions", {})
if "attempt_history" not in st.session_state:
    st.session_state.attempt_history = initial_data.get("attempts", {})

# ==========================================
# 👁️ टॉप-राइट कॉर्नर आइकन्स का नियंत्रण
# ==========================================
if not st.session_state.is_admin:
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        div[data-testid="stToolbar"] {visibility: hidden; display: none !important;}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        #MainMenu {visibility: visible;}
        div[data-testid="stToolbar"] {visibility: visible !important;}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🚀 ऑटो-वर्ज़न चेकर
# ==========================================
def get_dynamic_version():
    try:
        total_q = sum(len(v) for v in st.session_state.all_questions_db.values())
        total_c = sum(len(v) for v in st.session_state.subjects_data.values())
        file_time = os.path.getmtime(DB_FILE) if os.path.exists(DB_FILE) else os.path.getmtime(__file__)
        return f"v{datetime.fromtimestamp(file_time).strftime('%y%m%d%H%M')}_{total_c}_{total_q}"
    except Exception:
        return "v1.0"

CURRENT_SYSTEM_VERSION = get_dynamic_version()

if "client_app_version" not in st.session_state:
    st.session_state.client_app_version = CURRENT_SYSTEM_VERSION

if st.session_state.client_app_version != CURRENT_SYSTEM_VERSION:
    with st.container(border=True):
        st.warning("🔔 **नया अपडेट उपलब्ध है!** ऐप/वेबसाइट में नए प्रश्न या बदलाव जोड़े गए हैं।")
        if st.button("🚀 अभी अपडेट करें (Click to Refresh)", type="primary", use_container_width=True):
            fresh_data = load_permanent_data()
            st.session_state.subjects_data = fresh_data.get("subjects", DEFAULT_SUBJECTS)
            st.session_state.all_questions_db = fresh_data.get("questions", {})
            st.session_state.attempt_history = fresh_data.get("attempts", {})
            st.session_state.client_app_version = CURRENT_SYSTEM_VERSION
            st.toast("✅ ऐप सफलतापूर्वक सिंक व अपडेट हो गया!", icon="🎉")
            time.sleep(1)
            st.rerun()

# स्टेट इनिशियलाइजेशन
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
if "is_reattempt_flow" not in st.session_state:
    st.session_state.is_reattempt_flow = False

current_key = f"{st.session_state.selected_subject}_{st.session_state.selected_chapter}"
current_questions = st.session_state.all_questions_db.get(current_key, [])

# ==========================================
# ⚡ सुरक्षित एवं उन्नत ऑटो-कंप्रेसर फंक्शन (500 Error Fix)
# ==========================================
def compress_and_convert_to_bytes(img, max_width=900, quality=75):
    try:
        # EXIF ओरिएंटेशन ठीक करना ताकि फोटो उल्टी न हो
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    # अगर इमेज बहुत बड़ी है तो उसका साइज़ ऑटोमैटिक घटाएं
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int((float(img.height) * float(ratio)))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
    buf = io.BytesIO()
    img.save(buf, format="JPEG", optimize=True, quality=quality)
    return buf.getvalue()

# ==========================================
# 📊 टेस्ट सबमिट एवं रैंक/पर्सेंटाइल गणना
# ==========================================
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
    
    if total_participants > 1:
        below_count = sum(1 for s in all_scores if s < raw_score)
        percentile = (below_count / (total_participants - 1)) * 100
    else:
        percentile = 100.0

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

# ==========================================
# 🔑 एडमिन लॉगिन डायलॉग
# ==========================================
@st.dialog("🔐 एडमिन लॉगिन पोर्टल")
def admin_login_dialog():
    st.write("एडमिन कंट्रोल्स एवं 'Editing All' एक्सेस करने के लिए पासवर्ड दर्ज करें:")
    pwd = st.text_input("पासवर्ड (Password):", type="password", key="dlg_pwd")
    if st.button("लॉगिन करें 🚀", type="primary", use_container_width=True):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.success("सफलतापूर्वक एडमिन मोड चालू हो गया!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("गलत पासवर्ड! कृपया दोबारा प्रयास करें।")

# --- साइडबार: एडमिन कंट्रोल हब ---
with st.sidebar:
    st.title("🔐 पोर्टल नियंत्रण")
    st.caption(f"Sync ID: {CURRENT_SYSTEM_VERSION}")
    
    if st.session_state.is_admin:
        st.success("👨‍🏫 आप एडमिन के रूप में लॉगिन हैं")
        if st.button("लॉगआउट (स्टूडेंट मोड)"):
            st.session_state.is_admin = False
            st.rerun()

        st.divider()

        with st.expander("📁 Editing All (मास्टर कंट्रोल हब)", expanded=True):
            tab_subj, tab_chap, tab_q = st.tabs(["📚 विषय", "📑 चैप्टर", "📝 प्रश्न"])

            with tab_subj:
                st.markdown("**नया विषय जोड़ें:**")
                new_s_name = st.text_input("विषय का नाम:", key="hub_new_subj")
                if st.button("नया विषय सेव करें ➕"):
                    if new_s_name.strip() and new_s_name not in st.session_state.subjects_data:
                        st.session_state.subjects_data[new_s_name.strip()] = []
                        save_permanent_data()
                        st.success(f"'{new_s_name}' जुड़ गया व सिंक हो गया!")
                        st.rerun()
                    else:
                        st.warning("मान्य नाम डालें!")

                st.write("---")
                all_s = list(st.session_state.subjects_data.keys())
                if all_s:
                    st.markdown("**विषय एडिट / डिलीट:**")
                    sel_s = st.selectbox("विषय चुनें:", all_s, key="hub_sel_s")
                    rename_s = st.text_input("नया नाम:", value=sel_s, key="hub_rename_s")
                    
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        if st.button("नाम बदलें 🔄", key="hub_btn_ren_s"):
                            if rename_s.strip() and rename_s != sel_s:
                                st.session_state.subjects_data[rename_s.strip()] = st.session_state.subjects_data.pop(sel_s)
                                if st.session_state.selected_subject == sel_s:
                                    st.session_state.selected_subject = rename_s.strip()
                                save_permanent_data()
                                st.success("अपडेट हो गया!")
                                st.rerun()
                    with c_s2:
                        if st.button("विषय हटाएं 🗑️", key="hub_btn_del_s", type="secondary"):
                            del st.session_state.subjects_data[sel_s]
                            if st.session_state.selected_subject == sel_s:
                                st.session_state.selected_subject = None
                                st.session_state.selected_chapter = None
                            save_permanent_data()
                            st.warning("विषय हटा दिया गया!")
                            st.rerun()

            with tab_chap:
                all_s = list(st.session_state.subjects_data.keys())
                if all_s:
                    p_subj = st.selectbox("विषय चुनें:", all_s, key="hub_p_subj")
                    curr_chaps = st.session_state.subjects_data.get(p_subj, [])

                    st.markdown("**नया चैप्टर जोड़ें:**")
                    new_c_name = st.text_input("चैप्टर का नाम:", key="hub_new_c")
                    if st.button("चैप्टर सेव करें ➕"):
                        if new_c_name.strip() and new_c_name not in curr_chaps:
                            st.session_state.subjects_data[p_subj].append(new_c_name.strip())
                            save_permanent_data()
                            st.success("चैप्टर जुड़ गया व सिंक हो गया!")
                            st.rerun()

                    if curr_chaps:
                        st.write("---")
                        st.markdown("**चैप्टर एडिट / डिलीट:**")
                        sel_c = st.selectbox("चैप्टर चुनें:", curr_chaps, key="hub_sel_c")
                        rename_c = st.text_input("नया चैप्टर नाम:", value=sel_c, key="hub_rename_c")

                        c_c1, c_c2 = st.columns(2)
                        with c_c1:
                            if st.button("चैप्टर नाम बदलें 🔄", key="hub_btn_ren_c"):
                                if rename_c.strip() and rename_c != sel_c:
                                    idx = st.session_state.subjects_data[p_subj].index(sel_c)
                                    st.session_state.subjects_data[p_subj][idx] = rename_c.strip()
                                    if st.session_state.selected_chapter == sel_c:
                                        st.session_state.selected_chapter = rename_c.strip()
                                    save_permanent_data()
                                    st.success("चैप्टर अपडेट हो गया!")
                                    st.rerun()
                        with c_c2:
                            if st.button("चैप्टर हटाएं 🗑️", key="hub_btn_del_c", type="secondary"):
                                st.session_state.subjects_data[p_subj].remove(sel_c)
                                if st.session_state.selected_chapter == sel_c:
                                    st.session_state.selected_chapter = None
                                save_permanent_data()
                                st.warning("चैप्टर हटा दिया गया!")
                                st.rerun()

            with tab_q:
                all_s = list(st.session_state.subjects_data.keys())
                if all_s:
                    q_subj = st.selectbox("विषय:", all_s, key="hub_q_s")
                    q_chaps = st.session_state.subjects_data.get(q_subj, [])
                    if q_chaps:
                        q_chap = st.selectbox("चैप्टर:", q_chaps, key="hub_q_c")
                        target_db_key = f"{q_subj}_{q_chap}"
                        target_q_list = st.session_state.all_questions_db.get(target_db_key, [])

                        st.caption(f"कुल उपलब्ध प्रश्न: {len(target_q_list)}")

                        with st.expander("➕ नया सवाल जोड़ें (विकल्प फोटो सहित)", expanded=False):
                            st.markdown("### 1. प्रश्न विवरण:")
                            q_t = st.text_area("प्रश्न टेक्स्ट:")
                            
                            q_i = st.file_uploader("प्रश्न की फोटो:", type=["png", "jpg", "jpeg"], key="h_qi")
                            final_q_img = None
                            if q_i:
                                try:
                                    pil_img_q = Image.open(q_i)
                                    st.caption("✂️ प्रश्न का हिस्सा क्रॉप करें:")
                                    cropped_q = st_cropper(pil_img_q, realtime_update=True, box_color='#00FF00', aspect_ratio=None, key="crop_q")
                                    final_q_img = compress_and_convert_to_bytes(cropped_q)
                                    st.image(final_q_img, caption="प्रश्न फोटो", width=220)
                                except Exception as e:
                                    st.error(f"फोटो प्रोसेस करने में त्रुटि: {e}")

                            st.write("---")
                            st.markdown("### 2. चारों विकल्प (टेक्स्ट या फोटो):")
                            
                            col_a1, col_a2 = st.columns(2)
                            with col_a1: op_a = st.text_input("विकल्प A टेक्स्ट:", key="h_ta")
                            with col_a2: img_a = st.file_uploader("A फोटो:", type=["png", "jpg", "jpeg"], key="h_ia")
                            final_img_a = compress_and_convert_to_bytes(Image.open(img_a)) if img_a else None

                            col_b1, col_b2 = st.columns(2)
                            with col_b1: op_b = st.text_input("विकल्प B टेक्स्ट:", key="h_tb")
                            with col_b2: img_b = st.file_uploader("B फोटो:", type=["png", "jpg", "jpeg"], key="h_ib")
                            final_img_b = compress_and_convert_to_bytes(Image.open(img_b)) if img_b else None

                            col_c1, col_c2 = st.columns(2)
                            with col_c1: op_c = st.text_input("विकल्प C टेक्स्ट:", key="h_tc")
                            with col_c2: img_c = st.file_uploader("C फोटो:", type=["png", "jpg", "jpeg"], key="h_ic")
                            final_img_c = compress_and_convert_to_bytes(Image.open(img_c)) if img_c else None

                            col_d1, col_d2 = st.columns(2)
                            with col_d1: op_d = st.text_input("विकल्प D टेक्स्ट:", key="h_td")
                            with col_d2: img_d = st.file_uploader("D फोटो:", type=["png", "jpg", "jpeg"], key="h_id")
                            final_img_d = compress_and_convert_to_bytes(Image.open(img_d)) if img_d else None

                            corr = st.selectbox("सही उत्तर चुनें:", ["A", "B", "C", "D"], key="h_corr")
                            
                            st.write("---")
                            st.markdown("### 3. सॉल्यूशन फोटो (वैकल्पिक):")
                            sol_i = st.file_uploader("सॉल्यूशन फोटो:", type=["png", "jpg", "jpeg"], key="h_sol")
                            final_sol_img = None
                            if sol_i:
                                try:
                                    pil_img_s = Image.open(sol_i)
                                    st.caption("✂️ सॉल्यूशन का हिस्सा क्रॉप करें:")
                                    cropped_s = st_cropper(pil_img_s, realtime_update=True, box_color='#0000FF', aspect_ratio=None, key="crop_s")
                                    final_sol_img = compress_and_convert_to_bytes(cropped_s)
                                    st.image(final_sol_img, caption="सॉल्यूशन फोटो", width=220)
                                except Exception as e:
                                    st.error(f"सॉल्यूशन फोटो प्रोसेस करने में त्रुटि: {e}")

                            if st.button("सवाल सेव करें 💾", key="h_save_q_btn"):
                                if not q_t and not final_q_img:
                                    st.error("कृपया प्रश्न का टेक्स्ट लिखें या फोटो दें!")
                                else:
                                    new_item = {
                                        "question_text": q_t if q_t else "नीचे दी गई फोटो को देखकर उत्तर दें:",
                                        "question_image": final_q_img,
                                        "options_text": {
                                            "A": op_a if op_a else "विकल्प A (फोटो देखें)",
                                            "B": op_b if op_b else "विकल्प B (फोटो देखें)",
                                            "C": op_c if op_c else "विकल्प C (फोटो देखें)",
                                            "D": op_d if op_d else "विकल्प D (फोटो देखें)"
                                        },
                                        "options_image": {
                                            "A": final_img_a,
                                            "B": final_img_b,
                                            "C": final_img_c,
                                            "D": final_img_d
                                        },
                                        "answer": corr,
                                        "sol_image": final_sol_img
                                    }
                                    if target_db_key not in st.session_state.all_questions_db:
                                        st.session_state.all_questions_db[target_db_key] = []
                                    st.session_state.all_questions_db[target_db_key].append(new_item)
                                    save_permanent_data()
                                    st.success("सफलतापूर्वक नया प्रश्न सेव और सिंक हो गया!")
                                    st.rerun()

                        if target_q_list:
                            st.divider()
                            if st.button("⚠️ Delete All (इस चैप्टर के सभी प्रश्न हटाएं)", key="hub_del_all_btn", type="secondary"):
                                st.session_state.all_questions_db[target_db_key] = []
                                save_permanent_data()
                                st.warning("सभी प्रश्न हटा दिए गए!")
                                st.rerun()
                    else:
                        st.caption("इस विषय में कोई चैप्टर नहीं है।")
    else:
        st.info("एडमिन फीचर्स एक्सेस करने के लिए नीचे दिए गए बटन से लॉगिन करें।")

# ==========================================
# 📲 टॉप हेडर: शेयर बटन
# ==========================================
col_h_left, col_h_right = st.columns([3, 1])
with col_h_right:
    components.html("""
    <div style="text-align: right; margin-bottom: 5px;">
        <button id="shareBtn" style="
            background: linear-gradient(135deg, #25D366, #128C7E);
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 20px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        ">
            📲 शेयर करें
        </button>
    </div>
    <script>
    document.getElementById('shareBtn').addEventListener('click', async () => {
        const shareData = {
            title: 'ALL SUBJECT TEST PORTAL',
            text: 'ऑनलाइन मॉक टेस्ट दें और अपनी तैयारी परखें! यहाँ क्लिक करें:',
            url: window.location.href
        };
        if (navigator.share) {
            try {
                await navigator.share(shareData);
            } catch (err) {}
        } else {
            navigator.clipboard.writeText(window.location.href);
            alert('लिंक कॉपी हो गया है! अब आप इसे WhatsApp पर भेज सकते हैं।');
        }
    });
    </script>
    """, height=45)

# सामान्य सॉल्यूशन कार्ड रेंडरर
def render_solution_card(index_list, answers_dict, empty_msg="इस श्रेणी में कोई प्रश्न नहीं है।"):
    if not index_list:
        st.info(empty_msg)
        return

    for idx in index_list:
        q = current_questions[idx]
        ans = answers_dict.get(idx)
        
        if ans is None:
            badge = "⚪ अनअटेम्प्ट"
        elif ans == q['answer']:
            badge = "✅ सही"
        else:
            badge = "❌ गलत"

        with st.expander(f"प्रश्न {idx+1} [{badge}] : {q['question_text'][:45]}..."):
            st.markdown(f"### प्रश्न {idx+1}: {q['question_text']}")
            if q.get("question_image"):
                st.image(q["question_image"], width=420)

            opt_imgs = q.get("options_image", {})
            if any(opt_imgs.values()):
                cols_sol_opt = st.columns(4)
                for i_k, k in enumerate(["A", "B", "C", "D"]):
                    with cols_sol_opt[i_k]:
                        if opt_imgs.get(k):
                            st.caption(f"विकल्प {k}:")
                            st.image(opt_imgs[k], use_container_width=True)

            st.write(f"**A)** {q['options_text']['A']}")
            st.write(f"**B)** {q['options_text']['B']}")
            st.write(f"**C)** {q['options_text']['C']}")
            st.write(f"**D)** {q['options_text']['D']}")

            st.write("---")
            st.write(f"**आपका चयन:** {ans if ans else 'उत्तर नहीं दिया (Unattempted)'}")
            st.write(f"**सही उत्तर:** :green[**विकल्प {q['answer']}**]")
            
            if q.get('sol_image') is not None:
                st.write("📸 **सॉल्यूशन फोटो:**")
                st.image(q['sol_image'], use_container_width=True)
            else:
                st.caption("इस सवाल के लिए कोई सॉल्यूशन फोटो उपलब्ध नहीं है।")

# ==============================================================================
# 🎯 1. मुख्य स्क्रीन: प्रीमियम एग्जाम डैशबोर्ड
# ==============================================================================
if st.session_state.selected_subject is None:
    st.markdown("""
        <style>
        .hero-banner {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 24px;
            border-radius: 16px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(30, 58, 138, 0.2);
        }
        .hero-title {
            font-size: 26px;
            font-weight: 800;
            margin-bottom: 6px;
        }
        .hero-sub {
            font-size: 14px;
            opacity: 0.9;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">🎯 परीक्षा तैयारी पोर्टल (Exam Prep Hub)</div>
            <div class="hero-sub">अपनी तैयारी को परखें, अध्यायवार टेस्ट दें और रियल-टाइम परफॉर्मेंस ट्रैक करें।</div>
        </div>
    """, unsafe_allow_html=True)

    all_active_subjects = list(st.session_state.subjects_data.keys())
    total_subjects_count = len(all_active_subjects)
    total_chapters_count = sum(len(v) for v in st.session_state.subjects_data.values())
    total_questions_count = sum(len(v) for v in st.session_state.all_questions_db.values())
    total_attempts_count = sum(len(v) for v in st.session_state.attempt_history.values())

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.container(border=True).metric("📚 कुल विषय", f"{total_subjects_count}")
    with s_col2:
        st.container(border=True).metric("📑 कुल चैप्टर्स", f"{total_chapters_count}")
    with s_col3:
        st.container(border=True).metric("📝 उपलब्ध प्रश्न", f"{total_questions_count}")
    with s_col4:
        st.container(border=True).metric("🏆 आपके टेस्ट प्रयास", f"{total_attempts_count}")

    st.write("")
    st.markdown("### 📖 अपने विषय का चयन करें")
    st.caption("नीचे दिए गए किसी भी विषय पर क्लिक करके अभ्यास शुरू करें:")

    if not all_active_subjects:
        st.warning("अभी कोई विषय उपलब्ध नहीं है।")
    else:
        cols = st.columns(3)
        for index, subj in enumerate(all_active_subjects):
            with cols[index % 3]:
                with st.container(border=True):
                    chaps = st.session_state.subjects_data.get(subj, [])
                    st.subheader(subj)
                    st.caption(f"📑 उपलब्ध अध्याय: **{len(chaps)}**")
                    if st.button("अभ्यास शुरू करें ➔", key=f"subj_{index}", use_container_width=True, type="primary"):
                        st.session_state.selected_subject = subj
                        st.rerun()

    st.write("")
    st.write("---")
    col_adm_space, col_adm_btn = st.columns([3, 1])
    with col_adm_btn:
        if not st.session_state.is_admin:
            if st.button("🔑 एडमिन लॉगिन (Owner Access)", use_container_width=True):
                admin_login_dialog()
        else:
            st.success("👨‍🏫 एडमिन मोड सक्रिय है")
            if st.button("🚪 एडमिन लॉगआउट", use_container_width=True):
                st.session_state.is_admin = False
                st.rerun()

# --- 2. मुख्य स्क्रीन: अध्याय चयन ---
elif st.session_state.selected_chapter is None:
    st.button("⬅ वापस डैशबोर्ड पर जाएं", on_click=lambda: st.session_state.update({"selected_subject": None}))
    st.title(f"{st.session_state.selected_subject}")
    st.write("### अपना चैप्टर चुनें (Select Chapter):")
    st.write("---")

    chapters = st.session_state.subjects_data.get(st.session_state.selected_subject, [])
    if not chapters:
        st.warning("इस विषय में अभी कोई चैप्टर मौजूद नहीं है।")
    else:
        cols = st.columns(2)
        for index, chap in enumerate(chapters):
            with cols[index % 2]:
                st.container(border=True).write(f"📑 **{chap}**")
                if st.button("मॉक टेस्ट लगाएं ✍️", key=f"chap_{index}", use_container_width=True):
                    st.session_state.selected_chapter = chap
                    st.rerun()

# --- 3. मुख्य स्क्रीन: मॉक टेस्ट व एडवांस्ड रिजल्ट ---
else:
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅ चैप्टर लिस्ट पर जाएं"):
            st.session_state.selected_chapter = None
            st.session_state.quiz_started = False
            st.session_state.submitted = False
            st.session_state.user_answers = {}
            st.session_state.is_reattempt_flow = False
            st.rerun()
    with col_title:
        st.subheader(f"📌 {st.session_state.selected_subject} ➔ {st.session_state.selected_chapter}")

    st.divider()

    past_attempts = st.session_state.attempt_history.get(current_key, [])

    # स्थिति 1: टेस्ट शुरू होने से पहले
    if not st.session_state.quiz_started and not st.session_state.submitted:
        st.write(f"**उपलब्ध प्रश्न:** {len(current_questions)}")
        
        opt_c1, opt_c2, opt_c3 = st.columns(3)
        with opt_c1:
            marks_per_q = st.selectbox(
                "प्रत्येक सही उत्तर के अंक:",
                [1.0, 2.0, 3.0, 4.0],
                format_func=lambda x: f"+{int(x)} अंक"
            )
            st.session_state.selected_marks = marks_per_q

        with opt_c2:
            neg_val = st.selectbox(
                "नेगेटिव मार्किंग चुनें:",
                [0.0, 0.25, 0.33, 0.50, 1.0],
                format_func=lambda x: f"-{x} अंक" if x > 0 else "कोई नेगेटिव नहीं (0.00)"
            )
            st.session_state.selected_neg = neg_val

        with opt_c3:
            time_choice = st.selectbox(
                "⏱️ टेस्ट का समय चुनें:",
                [0, 5, 10, 15, 20, 30, 45, 60],
                format_func=lambda x: "कोई समय सीमा नहीं (No Limit)" if x == 0 else f"{x} मिनट"
            )
            st.session_state.time_limit_seconds = time_choice * 60

        if len(current_questions) == 0:
            st.warning("⚠️ इस चैप्टर में अभी कोई टेस्ट उपलब्ध नहीं है।")
        else:
            if past_attempts:
                st.write("")
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("📊 View Result (पिछला रिजल्ट देखें)", use_container_width=True):
                        st.session_state.submitted = True
                        st.session_state.quiz_started = False
                        st.rerun()
                with col_act2:
                    if st.button("🔄 Re-attempt Test (दोबारा टेस्ट दें)", type="primary", use_container_width=True):
                        st.session_state.is_reattempt_flow = True
                        st.session_state.quiz_started = True
                        st.session_state.start_time = time.time()
                        st.session_state.user_answers = {}
                        st.rerun()
            else:
                if st.button("🚀 स्टार्ट टेस्ट (Start Test)", type="primary", use_container_width=True):
                    st.session_state.quiz_started = True
                    st.session_state.start_time = time.time()
                    st.rerun()

    # स्थिति 2: टेस्ट चल रहा है (लाइव)
    elif st.session_state.quiz_started and not st.session_state.submitted:
        
        # 📊 री-अटेम्प्ट हिस्ट्री चार्ट एवं पिछले प्रश्नों का समाधान
        if past_attempts:
            next_attempt_num = len(past_attempts) + 1
            with st.container(border=True):
                st.info(f"🎯 **आप प्रयास #{next_attempt_num} दे रहे हैं** (अब तक आपने कुल **{len(past_attempts)}** प्रयास पूरे किए हैं)")
                
                with st.expander("📈 पिछले सभी प्रयासों का चार्ट व विवरण देखें", expanded=True):
                    clean_history = []
                    for h in past_attempts:
                        clean_history.append({
                            "प्रयास": h.get("अटेम्प्ट"),
                            "प्राप्तांक": h.get("raw_score", 0.0),
                            "सही": h.get("सही (Correct)", 0),
                            "गलत": h.get("गलत (Wrong)", 0),
                            "छोड़े गए": h.get("छोड़े (Skipped)", 0),
                            "सटीकता": h.get("सटीकता", "0%"),
                            "तारीख": h.get("तारीख", "")
                        })
                    df_chart = pd.DataFrame(clean_history)
                    st.bar_chart(df_chart.set_index("प्रयास")[["प्राप्तांक", "सही", "गलत"]])
                    st.dataframe(df_chart, use_container_width=True)

                # पिछले प्रयासों के सवाल व सॉल्यूशन
                with st.expander("🔍 पिछले प्रयासों के सवाल व सॉल्यूशन देखें (Right, Wrong, Unattempted)"):
                    att_labels = [f"प्रयास #{i+1} ({att.get('तारीख', '')})" for i, att in enumerate(past_attempts)]
                    chosen_att_idx = st.selectbox("किस प्रयास के सवाल देखना चाहते हैं?", range(len(att_labels)), format_func=lambda x: att_labels[x])
                    
                    target_att = past_attempts[chosen_att_idx]
                    past_user_ans = target_att.get("user_answers", {})
                    
                    p_cor = []
                    p_inc = []
                    p_una = []
                    for idx, q in enumerate(current_questions):
                        a = past_user_ans.get(idx)
                        if a is None:
                            p_una.append(idx)
                        elif a == q['answer']:
                            p_cor.append(idx)
                        else:
                            p_inc.append(idx)

                    p_t_cor, p_t_inc, p_t_una = st.tabs([
                        f"✅ सही प्रश्न ({len(p_cor)})", 
                        f"❌ गलत प्रश्न ({len(p_inc)})", 
                        f"⚪ अनअटेम्प्ट प्रश्न ({len(p_una)})"
                    ])
                    with p_t_cor:
                        render_solution_card(p_cor, past_user_ans, "इस प्रयास में कोई सही उत्तर नहीं था।")
                    with p_t_inc:
                        render_solution_card(p_inc, past_user_ans, "इस प्रयास में कोई गलत उत्तर नहीं था।")
                    with p_t_una:
                        render_solution_card(p_una, past_user_ans, "इस प्रयास में कोई अनअटेम्प्ट प्रश्न नहीं था।")

        if st.session_state.time_limit_seconds > 0:
            elapsed = time.time() - st.session_state.start_time
            remaining = st.session_state.time_limit_seconds - elapsed

            if remaining <= 0:
                st.error("⏰ समय समाप्त हो गया है! आपका टेस्ट स्वतः सबमिट किया जा रहा है...")
                calculate_and_submit_quiz(is_timeout=True)
                st.rerun()
            else:
                rem_mins = int(remaining // 60)
                rem_secs = int(remaining % 60)
                st.warning(f"⏱️ **बचा हुआ समय:** {rem_mins:02d}:{rem_secs:02d} मिनट")
        else:
            st.caption(f"नियम: सही पर +{int(st.session_state.get('selected_marks', 1.0))} अंक | गलत पर -{st.session_state.get('selected_neg', 0.0)} अंक | कोई समय सीमा नहीं")

        for idx, q in enumerate(current_questions):
            st.markdown(f"### प्रश्न {idx+1}: {q['question_text']}")
            
            if q.get("question_image"):
                st.image(q["question_image"], width=480)

            opt_imgs = q.get("options_image", {})
            if any(opt_imgs.values()):
                cols_opt_img = st.columns(4)
                for i_k, k in enumerate(["A", "B", "C", "D"]):
                    with cols_opt_img[i_k]:
                        if opt_imgs.get(k):
                            st.caption(f"विकल्प {k}:")
                            st.image(opt_imgs[k], use_container_width=True)
            
            radio_choices = [
                f"A) {q['options_text']['A']}",
                f"B) {q['options_text']['B']}",
                f"C) {q['options_text']['C']}",
                f"D) {q['options_text']['D']}"
            ]
            ans = st.radio(f"प्रश्न {idx+1} का उत्तर चुनें:", radio_choices, key=f"ans_{current_key}_{idx}", index=None)
            st.session_state.user_answers[idx] = ans[0] if ans else None

            if st.session_state.is_admin:
                col_inline_ed, col_inline_del = st.columns([1, 1])
                with col_inline_ed:
                    with st.expander(f"✏️ प्रश्न {idx+1} को एडिट करें"):
                        with st.form(f"inline_edit_form_{idx}"):
                            q_edit_txt = st.text_area("प्रश्न टेक्स्ट:", value=q.get("question_text", ""), key=f"inline_qtxt_{idx}")
                            q_edit_a = st.text_input("विकल्प A:", value=q['options_text'].get('A', ''), key=f"inline_qa_{idx}")
                            q_edit_b = st.text_input("विकल्प B:", value=q['options_text'].get('B', ''), key=f"inline_qb_{idx}")
                            q_edit_c = st.text_input("विकल्प C:", value=q['options_text'].get('C', ''), key=f"inline_qc_{idx}")
                            q_edit_d = st.text_input("विकल्प D:", value=q['options_text'].get('D', ''), key=f"inline_qd_{idx}")

                            opts = ["A", "B", "C", "D"]
                            curr_ans = q.get("answer", "A")
                            c_idx = opts.index(curr_ans) if curr_ans in opts else 0
                            q_edit_ans = st.selectbox("सही उत्तर:", opts, index=c_idx, key=f"inline_qans_{idx}")

                            if st.form_submit_button("अपडेट करें 🔄"):
                                st.session_state.all_questions_db[current_key][idx]["question_text"] = q_edit_txt
                                st.session_state.all_questions_db[current_key][idx]["options_text"] = {
                                    "A": q_edit_a, "B": q_edit_b, "C": q_edit_c, "D": q_edit_d
                                }
                                st.session_state.all_questions_db[current_key][idx]["answer"] = q_edit_ans
                                save_permanent_data()
                                st.success(f"प्रश्न {idx+1} तुरंत अपडेट व सिंक हो गया!")
                                st.rerun()

                with col_inline_del:
                    if st.button(f"🗑️ प्रश्न {idx+1} हटाएं", key=f"inline_del_btn_{idx}", type="secondary"):
                        st.session_state.all_questions_db[current_key].pop(idx)
                        save_permanent_data()
                        st.success(f"प्रश्न {idx+1} डिलीट व सिंक कर दिया गया!")
                        st.rerun()

            st.write("---")

        if st.button("🏁 टेस्ट सबमिट करें (Submit Test)", type="primary"):
            calculate_and_submit_quiz(is_timeout=False)
            st.rerun()

    # ==============================================================================
    # 🏆 स्थिति 3: रिजल्ट स्क्रीन
    # ==============================================================================
    elif st.session_state.submitted:
        st.header("📊 आपकी संपूर्ण परफॉर्मेंस रिपोर्ट (Performance Report)")
        
        current_attempt = past_attempts[-1] if past_attempts else {}
        cur_answers = current_attempt.get("user_answers", st.session_state.user_answers)

        with st.container(border=True):
            r_c1, r_c2, r_c3, r_c4 = st.columns(4)
            r_c1.metric("🎯 स्कोर (Score)", current_attempt.get("प्राप्तांक", "0"))
            r_c2.metric("🏆 ओवरऑल रैंक", current_attempt.get("रैंक", "1 / 1"))
            r_c3.metric("📈 पर्सेंटाइल", current_attempt.get("पर्सेंटाइल", "100.0%"))
            r_c4.metric("⚡ सटीकता (Accuracy)", current_attempt.get("सटीकता", "0%"))

            st.write("---")
            q_c1, q_c2, q_c3, q_c4 = st.columns(4)
            q_c1.metric("📝 कुल प्रश्न", current_attempt.get("कुल प्रश्न", len(current_questions)))
            q_c2.metric("✅ सही (Correct)", current_attempt.get("सही (Correct)", 0))
            q_c3.metric("❌ गलत (Incorrect)", current_attempt.get("गलत (Wrong)", 0))
            q_c4.metric("⚪ अनअटेम्प्ट (Unattempted)", current_attempt.get("छोड़े (Skipped)", 0))

        correct_indices = []
        incorrect_indices = []
        unattempted_indices = []

        for idx, q in enumerate(current_questions):
            ans = cur_answers.get(idx)
            if ans is None:
                unattempted_indices.append(idx)
            elif ans == q['answer']:
                correct_indices.append(idx)
            else:
                incorrect_indices.append(idx)

        st.divider()
        st.subheader("🔍 प्रश्नों का विस्तृत हल एवं विश्लेषण (Question Analysis)")
        
        tab_all, tab_cor, tab_inc, tab_un = st.tabs([
            f"📑 View All (कुल {len(current_questions)})",
            f"✅ Correct ({len(correct_indices)})",
            f"❌ Incorrect ({len(incorrect_indices)})",
            f"⚪ Unattempted ({len(unattempted_indices)})"
        ])

        with tab_all:
            render_solution_card(list(range(len(current_questions))), cur_answers)
        with tab_cor:
            render_solution_card(correct_indices, cur_answers, "आपने कोई भी सही उत्तर नहीं दिया है।")
        with tab_inc:
            render_solution_card(incorrect_indices, cur_answers, "शानदार! आपका एक भी सवाल गलत नहीं हुआ है।")
        with tab_un:
            render_solution_card(unattempted_indices, cur_answers, "आपने सारे सवाल हल किए हैं, कोई भी सवाल नहीं छोड़ा!")

        st.divider()
        st.write("### 📌 आगे की कार्रवाई चुनें:")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            if st.button("📊 View Result (दोबारा ऊपर जाएं)", use_container_width=True):
                st.rerun()
        with col_res2:
            if st.button("🔄 Re-attempt Test (दोबारा टेस्ट दें)", type="primary", use_container_width=True):
                st.session_state.submitted = False
                st.session_state.quiz_started = True
                st.session_state.start_time = time.time()
                st.session_state.user_answers = {}
                st.rerun()
