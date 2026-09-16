import streamlit as st
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="ALL SUBJECT TEST", page_icon="📝", layout="wide")

# एडमिन पासवर्ड
ADMIN_PASSWORD = "NINI@123"

# डिफ़ॉल्ट विषय और चैप्टर्स का डेटा
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

# स्टेट इनिशियलाइजेशन
if "subjects_data" not in st.session_state:
    st.session_state.subjects_data = DEFAULT_SUBJECTS
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
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "time_limit_seconds" not in st.session_state:
    st.session_state.time_limit_seconds = 0

# डेटाबेस
if "all_questions_db" not in st.session_state:
    st.session_state.all_questions_db = {}
if "attempt_history" not in st.session_state:
    st.session_state.attempt_history = {}

current_key = f"{st.session_state.selected_subject}_{st.session_state.selected_chapter}"
current_questions = st.session_state.all_questions_db.get(current_key, [])


# --- फंक्शन: टेस्ट सबमिट एवं रिजल्ट गणना ---
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
    final_score = (correct * mark_per_q) - (wrong * neg)
    accuracy = (correct / (correct + wrong) * 100) if (correct + wrong) > 0 else 0

    if current_key not in st.session_state.attempt_history:
        st.session_state.attempt_history[current_key] = []

    attempt_num = len(st.session_state.attempt_history[current_key]) + 1
    reason = " (समय समाप्त)" if is_timeout else ""
    st.session_state.attempt_history[current_key].append({
        "अटेम्प्ट (Attempt)": f"प्रयास #{attempt_num}{reason}",
        "तारीख व समय": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "कुल प्रश्न": total,
        "अंतिम स्कोर": f"{final_score:.2f} / {max_marks:.0f}",
        "सही उत्तर": correct,
        "गलत उत्तर": wrong,
        "छोड़े गए": unattempted,
        "सटीकता (Accuracy)": f"{accuracy:.1f}%"
    })


# --- साइडबार: एडमिन लॉगिन और "Editing All" मास्टर कंट्रोल ---
with st.sidebar:
    st.title("🔐 पोर्टल नियंत्रण")
    
    if not st.session_state.is_admin:
        with st.expander("🔑 एडमिन लॉगिन (केवल ओनर के लिए)"):
            admin_pwd = st.text_input("पासवर्ड डालें:", type="password")
            if st.button("लॉगिन"):
                if admin_pwd == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.success("एडमिन मोड चालू हो गया!")
                    st.rerun()
                else:
                    st.error("गलत पासवर्ड!")
    else:
        st.success("👨‍🏫 आप एडमिन के रूप में लॉगिन हैं")
        if st.button("लॉगआउट (स्टूडेंट मोड)"):
            st.session_state.is_admin = False
            st.rerun()

        st.divider()

        # ==========================================
        # 📁 मुख्य फोल्डर: Editing All
        # ==========================================
        with st.expander("📁 Editing All (मास्टर कंट्रोल हब)", expanded=True):
            st.info("यहाँ से आप विषय, चैप्टर और प्रश्न जोड़, बदल या हटा सकते हैं।")
            
            tab_subj, tab_chap, tab_q = st.tabs(["📚 विषय", "📑 चैप्टर", "📝 प्रश्न"])

            # 1. विषय टैब
            with tab_subj:
                st.markdown("**नया विषय जोड़ें:**")
                new_s_name = st.text_input("विषय का नाम:", key="hub_new_subj")
                if st.button("नया विषय सेव करें ➕"):
                    if new_s_name.strip() and new_s_name not in st.session_state.subjects_data:
                        st.session_state.subjects_data[new_s_name.strip()] = []
                        st.success(f"'{new_s_name}' जुड़ गया!")
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
                                st.success("अपडेट हो गया!")
                                st.rerun()
                    with c_s2:
                        if st.button("विषय हटाएं 🗑️", key="hub_btn_del_s", type="secondary"):
                            del st.session_state.subjects_data[sel_s]
                            if st.session_state.selected_subject == sel_s:
                                st.session_state.selected_subject = None
                                st.session_state.selected_chapter = None
                            st.warning("विषय हटा दिया गया!")
                            st.rerun()

            # 2. चैप्टर टैब
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
                            st.success("चैप्टर जुड़ गया!")
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
                                    st.success("चैप्टर अपडेट हो गया!")
                                    st.rerun()
                        with c_c2:
                            if st.button("चैप्टर हटाएं 🗑️", key="hub_btn_del_c", type="secondary"):
                                st.session_state.subjects_data[p_subj].remove(sel_c)
                                if st.session_state.selected_chapter == sel_c:
                                    st.session_state.selected_chapter = None
                                st.warning("चैप्टर हटा दिया गया!")
                                st.rerun()

            # 3. प्रश्न टैब
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

                        with st.expander("➕ नया सवाल जोड़ें", expanded=False):
                            with st.form("hub_add_q_form", clear_on_submit=True):
                                q_t = st.text_area("प्रश्न टेक्स्ट:")
                                q_i = st.file_uploader("प्रश्न फोटो:", type=["png", "jpg", "jpeg"], key="h_qi")
                                
                                c_a1, c_a2 = st.columns(2)
                                with c_a1: op_a = st.text_input("A टेक्स्ट:")
                                with c_a2: img_a = st.file_uploader("A फोटो:", type=["png", "jpg", "jpeg"], key="h_ia")
                                
                                c_b1, c_b2 = st.columns(2)
                                with c_b1: op_b = st.text_input("B टेक्स्ट:")
                                with c_b2: img_b = st.file_uploader("B फोटो:", type=["png", "jpg", "jpeg"], key="h_ib")
                                
                                c_c1, c_c2 = st.columns(2)
                                with c_c1: op_c = st.text_input("C टेक्स्ट:")
                                with c_c2: img_c = st.file_uploader("C फोटो:", type=["png", "jpg", "jpeg"], key="h_ic")
                                
                                c_d1, c_d2 = st.columns(2)
                                with c_d1: op_d = st.text_input("D टेक्स्ट:")
                                with c_d2: img_d = st.file_uploader("D फोटो:", type=["png", "jpg", "jpeg"], key="h_id")

                                corr = st.selectbox("सही उत्तर:", ["A", "B", "C", "D"], key="h_corr")
                                sol_i = st.file_uploader("सॉल्यूशन फोटो:", type=["png", "jpg", "jpeg"], key="h_sol")
                                
                                if st.form_submit_button("सवाल सेव करें 💾"):
                                    if not q_t and not q_i:
                                        st.error("प्रश्न का टेक्स्ट या फोटो दें!")
                                    else:
                                        new_item = {
                                            "question_text": q_t if q_t else "नीचे दी गई फोटो को देखकर उत्तर दें:",
                                            "question_image": q_i.read() if q_i else None,
                                            "options_text": {
                                                "A": op_a if op_a else "विकल्प A (फोटो देखें)",
                                                "B": op_b if op_b else "विकल्प B (फोटो देखें)",
                                                "C": op_c if op_c else "विकल्प C (फोटो देखें)",
                                                "D": op_d if op_d else "विकल्प D (फोटो देखें)"
                                            },
                                            "options_image": {
                                                "A": img_a.read() if img_a else None,
                                                "B": img_b.read() if img_b else None,
                                                "C": img_c.read() if img_c else None,
                                                "D": img_d.read() if img_d else None
                                            },
                                            "answer": corr,
                                            "sol_image": sol_i.read() if sol_i else None
                                        }
                                        if target_db_key not in st.session_state.all_questions_db:
                                            st.session_state.all_questions_db[target_db_key] = []
                                        st.session_state.all_questions_db[target_db_key].append(new_item)
                                        st.success("सवाल जुड़ गया!")
                                        st.rerun()

                        if target_q_list:
                            st.divider()
                            if st.button("⚠️ Delete All (इस चैप्टर के सभी प्रश्न हटाएं)", key="hub_del_all_btn", type="secondary"):
                                st.session_state.all_questions_db[target_db_key] = []
                                st.warning("सभी प्रश्न हटा दिए गए!")
                                st.rerun()
                    else:
                        st.caption("इस विषय में कोई चैप्टर नहीं है।")


# --- 1. मुख्य स्क्रीन: विषय चयन ---
if st.session_state.selected_subject is None:
    st.title("📚 - टेस्ट सीरीज पोर्टल")
    st.write("### अपना विषय चुनें (Select Subject):")
    st.write("---")

    all_active_subjects = list(st.session_state.subjects_data.keys())
    if not all_active_subjects:
        st.warning("अभी कोई विषय उपलब्ध नहीं है। कृपया एडमिन साइडबार से नए विषय जोड़ें।")
    else:
        cols = st.columns(3)
        for index, subj in enumerate(all_active_subjects):
            with cols[index % 3]:
                st.container(border=True).subheader(subj)
                if st.button("ओपन करें ➔", key=f"subj_{index}", use_container_width=True):
                    st.session_state.selected_subject = subj
                    st.rerun()


# --- 2. मुख्य स्क्रीन: अध्याय चयन ---
elif st.session_state.selected_chapter is None:
    st.button("⬅ वापस सभी विषय पर जाएं", on_click=lambda: st.session_state.update({"selected_subject": None}))
    st.title(f"{st.session_state.selected_subject}")
    st.write("### अपना चैप्टर चुनें (Select Chapter):")
    st.write("---")

    chapters = st.session_state.subjects_data.get(st.session_state.selected_subject, [])
    if not chapters:
        st.warning("इस विषय में अभी कोई चैप्टर मौजूद नहीं है। कृपया साइडबार से चैप्टर जोड़ें।")
    else:
        cols = st.columns(2)
        for index, chap in enumerate(chapters):
            with cols[index % 2]:
                st.container(border=True).write(f"📑 **{chap}**")
                if st.button("मॉक टेस्ट लगाएं ✍️", key=f"chap_{index}", use_container_width=True):
                    st.session_state.selected_chapter = chap
                    st.rerun()


# --- 3. मुख्य स्क्रीन: मॉक टेस्ट व रिजल्ट ---
else:
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅ चैप्टर लिस्ट पर जाएं"):
            st.session_state.selected_chapter = None
            st.session_state.quiz_started = False
            st.session_state.submitted = False
            st.session_state.user_answers = {}
            st.rerun()
    with col_title:
        st.subheader(f"📌 {st.session_state.selected_subject} ➔ {st.session_state.selected_chapter}")

    st.divider()

    # टेस्ट शुरू करने से पहले की सेटिंग्स
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

        # पिछले प्रयासों का रिकॉर्ड
        past_attempts = st.session_state.attempt_history.get(current_key, [])
        if past_attempts:
            with st.expander(f"📜 आपके पिछले प्रयासों का रिकॉर्ड (कुल {len(past_attempts)} बार टेस्ट दिया)", expanded=True):
                df_history = pd.DataFrame(past_attempts)
                st.dataframe(df_history, use_container_width=True)

        if len(current_questions) == 0:
            st.warning("⚠️ इस चैप्टर में अभी कोई टेस्ट उपलब्ध नहीं है। एडमिन 'Editing All' फोल्डर से नए प्रश्न जोड़ सकते हैं।")
        else:
            if st.button("🚀 स्टार्ट टेस्ट (Start Test)", type="primary"):
                st.session_state.quiz_started = True
                st.session_state.start_time = time.time()
                st.rerun()

    # लाइव मॉक टेस्ट (काउंटडाउन टाइमर, प्रश्न क्रमांक और डायरेक्ट एडमिन एडिट/डिलीट)
    elif st.session_state.quiz_started and not st.session_state.submitted:
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

        # प्रत्येक सवाल का प्रदर्शन
        for idx, q in enumerate(current_questions):
            st.markdown(f"### प्रश्न {idx+1}: {q['question_text']}")
            
            if q.get("question_image"):
                st.image(q["question_image"], width=480)
            
            for opt_key in ["A", "B", "C", "D"]:
                if q["options_image"].get(opt_key):
                    st.caption(f"विकल्प {opt_key} की फोटो:")
                    st.image(q["options_image"][opt_key], width=260)
            
            radio_choices = [
                f"A) {q['options_text']['A']}",
                f"B) {q['options_text']['B']}",
                f"C) {q['options_text']['C']}",
                f"D) {q['options_text']['D']}"
            ]
            ans = st.radio(f"प्रश्न {idx+1} का उत्तर चुनें:", radio_choices, key=f"ans_{current_key}_{idx}", index=None)
            st.session_state.user_answers[idx] = ans[0] if ans else None

            # ==========================================
            # 🛠️ सीधे सवाल पर एडमिन एडिट और डिलीट कंट्रोल्स
            # ==========================================
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
                                st.success(f"प्रश्न {idx+1} तुरंत अपडेट कर दिया गया!")
                                st.rerun()

                with col_inline_del:
                    if st.button(f"🗑️ प्रश्न {idx+1} हटाएं", key=f"inline_del_btn_{idx}", type="secondary"):
                        st.session_state.all_questions_db[current_key].pop(idx)
                        st.success(f"प्रश्न {idx+1} डिलीट कर दिया गया!")
                        st.rerun()

            st.write("---")

        if st.button("🏁 टेस्ट सबमिट करें (Submit Test)", type="primary"):
            calculate_and_submit_quiz(is_timeout=False)
            st.rerun()

    # रिजल्ट और सॉल्यूशन स्क्रीन
    elif st.session_state.submitted:
        st.header("📊 आपकी परफॉर्मेंस रिपोर्ट")
        
        current_attempt = st.session_state.attempt_history[current_key][-1]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("अंतिम स्कोर (Score)", current_attempt["अंतिम स्कोर"])
        c2.metric("सटीकता (Accuracy)", current_attempt["सटीकता (Accuracy)"])
        c3.metric("सही (Correct)", current_attempt["सही उत्तर"])
        c4.metric("गलत (Wrong)", current_attempt["गलत उत्तर"])
        c5.metric("छोड़े गए (Skipped)", current_attempt["छोड़े गए"])

        st.divider()

        col_btn1, col_btn2 = st.columns([1, 2])
        with col_btn1:
            if st.button("🔄 री-अटेम्प्ट टेस्ट (Re-attempt Test)", type="primary"):
                st.session_state.submitted = False
                st.session_state.quiz_started = True
                st.session_state.start_time = time.time()
                st.session_state.user_answers = {}
                st.rerun()

        with st.expander("📜 आपके सभी री-अटेम्प्ट्स का इतिहास देखें", expanded=True):
            df_history = pd.DataFrame(st.session_state.attempt_history[current_key])
            st.table(df_history)

        st.divider()
        st.subheader("🔍 प्रश्नों का विस्तृत हल (Solutions)")
        for idx, q in enumerate(current_questions):
            ans = st.session_state.user_answers.get(idx)
            is_correct = (ans == q['answer'])

            with st.expander(f"प्रश्न {idx+1}: {'✅ सही' if is_correct else '❌ गलत/छोड़ा'} - {q['question_text'][:40]}..."):
                st.write(f"**प्रश्न {idx+1}:** {q['question_text']}")
                if q.get("question_image"):
                    st.image(q["question_image"], width=420)

                st.write(f"**आपका चयन:** {ans if ans else 'उत्तर नहीं दिया'}")
                st.write(f"**सही विकल्प:** :green[{q['answer']}]")
                
                if q.get('sol_image') is not None:
                    st.write("📸 **सॉल्यूशन फोटो:**")
                    st.image(q['sol_image'], use_container_width=True)
                else:
                    st.caption("इस सवाल के लिए कोई सॉल्यूशन फोटो अपलोड नहीं की गई है।")
