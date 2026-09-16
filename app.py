import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ALL SUBJECT TEST", page_icon="📝", layout="wide")

# एडमिन पासवर्ड
ADMIN_PASSWORD = "NINI@123"

# विषय और उनके सभी चैप्टर्स की लिस्ट (सिंटैक्स ठीक कर दिया गया है)
SUBJECTS_DATA = {
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

# स्टेट मैनेजमेंट
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

# सवाल और अटेम्प्ट हिस्ट्री का डाटाबेस
if "all_questions_db" not in st.session_state:
    st.session_state.all_questions_db = {}
if "attempt_history" not in st.session_state:
    st.session_state.attempt_history = {}

current_key = f"{st.session_state.selected_subject}_{st.session_state.selected_chapter}"
current_questions = st.session_state.all_questions_db.get(current_key, [])


# --- साइडबार: एडमिन लॉगिन एवं अपलोड सेक्शन ---
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

    # एडमिन के लिए सवाल और इमेज अपलोड फॉर्म
    if st.session_state.is_admin and st.session_state.selected_chapter is not None:
        st.divider()
        st.subheader("➕ नया सवाल जोड़ें")
        with st.form("manual_add_q", clear_on_submit=True):
            q_text = st.text_area("प्रश्न दर्ज करें:")
            op_a = st.text_input("विकल्प A:")
            op_b = st.text_input("विकल्प B:")
            op_c = st.text_input("विकल्प C:")
            op_d = st.text_input("विकल्प D:")
            correct = st.selectbox("सही विकल्प चुनें:", ["A", "B", "C", "D"])
            
            sol_img = st.file_uploader("सॉल्यूशन की फोटो अपलोड करें:", type=["png", "jpg", "jpeg"])
            
            save_btn = st.form_submit_button("सवाल सेव करें 💾")
            if save_btn and q_text and op_a and op_b:
                ops = {"A": op_a, "B": op_b, "C": op_c, "D": op_d}
                new_q = {
                    "question": q_text,
                    "options": [op_a, op_b, op_c, op_d],
                    "answer": ops[correct],
                    "sol_image": sol_img.read() if sol_img else None
                }
                if current_key not in st.session_state.all_questions_db:
                    st.session_state.all_questions_db[current_key] = []
                st.session_state.all_questions_db[current_key].append(new_q)
                st.success("सवाल टेस्ट में जुड़ गया!")
                st.rerun()


# --- 1. मुख्य स्क्रीन: विषय चयन ---
if st.session_state.selected_subject is None:
    st.title("📚 - टेस्ट सीरीज पोर्टल")
    st.write("### अपना विषय चुनें (Select Subject):")
    st.write("---")

    cols = st.columns(3)
    for index, subj in enumerate(SUBJECTS_DATA.keys()):
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

    chapters = SUBJECTS_DATA[st.session_state.selected_subject]
    cols = st.columns(2)
    for index, chap in enumerate(chapters):
        with cols[index % 2]:
            st.container(border=True).write(f"📑 **{chap}**")
            if st.button("मॉक टेस्ट लगाएं ✍️", key=f"chap_{index}", use_container_width=True):
                st.session_state.selected_chapter = chap
                st.rerun()


# --- 3. मुख्य स्क्रीन: मॉक टेस्ट व अटेम्प्ट ट्रैकर ---
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

    # टेस्ट शुरू करने से पहले (अंक और नेगेटिव मार्किंग चयन)
    if not st.session_state.quiz_started and not st.session_state.submitted:
        st.write(f"**उपलब्ध प्रश्न:** {len(current_questions)}")
        
        opt_col1, opt_col2 = st.columns(2)
        
        with opt_col1:
            marks_per_q = st.selectbox(
                "प्रत्येक सही उत्तर के लिए अंक चुनें:",
                [1.0, 2.0, 3.0, 4.0],
                format_func=lambda x: f"+{int(x)} अंक प्रति सही उत्तर"
            )
            st.session_state.selected_marks = marks_per_q

        with opt_col2:
            neg_val = st.selectbox(
                "नेगेटिव मार्किंग चुनें:",
                [0.0, 0.25, 0.33, 0.50, 1.0],
                format_func=lambda x: f"-{x} अंक प्रति गलत उत्तर" if x > 0 else "कोई नेगेटिव मार्किंग नहीं (0.00)"
            )
            st.session_state.selected_neg = neg_val

        # पिछले प्रयासों का रिकॉर्ड दिखाना
        past_attempts = st.session_state.attempt_history.get(current_key, [])
        if past_attempts:
            with st.expander(f"📜 आपके पिछले प्रयासों का रिकॉर्ड (कुल {len(past_attempts)} बार टेस्ट दिया)", expanded=True):
                df_history = pd.DataFrame(past_attempts)
                st.dataframe(df_history, use_container_width=True)

        if len(current_questions) == 0:
            st.warning("⚠️ इस चैप्टर में अभी कोई टेस्ट उपलब्ध नहीं है। कृपया एडमिन द्वारा प्रश्न जोड़े जाने की प्रतीक्षा करें।")
        else:
            if st.button("🚀 स्टार्ट टेस्ट (Start Test)", type="primary"):
                st.session_state.quiz_started = True
                st.rerun()

    # लाइव मॉक टेस्ट
    elif st.session_state.quiz_started and not st.session_state.submitted:
        st.caption(f"नियम: सही उत्तर पर +{int(st.session_state.get('selected_marks', 1.0))} अंक | गलत उत्तर पर -{st.session_state.get('selected_neg', 0.0)} अंक")
        
        for idx, q in enumerate(current_questions):
            st.markdown(f"#### Q{idx+1}. {q['question']}")
            ans = st.radio("विकल्प चुनें:", q['options'], key=f"ans_{current_key}_{idx}", index=None)
            st.session_state.user_answers[idx] = ans
            st.write("---")

        if st.button("🏁 टेस्ट सबमिट करें (Submit Test)", type="primary"):
            st.session_state.submitted = True
            st.session_state.quiz_started = False
            
            # स्कोर की गणना और हिस्ट्री सेव करना
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
            st.session_state.attempt_history[current_key].append({
                "अटेम्प्ट (Attempt)": f"प्रयास #{attempt_num}",
                "तारीख व समय": datetime.now().strftime("%d-%m-%Y %H:%M"),
                "कुल प्रश्न": total,
                "अंतिम स्कोर": f"{final_score:.2f} / {max_marks:.0f}",
                "सही उत्तर": correct,
                "गलत उत्तर": wrong,
                "छोड़े गए": unattempted,
                "सटीकता (Accuracy)": f"{accuracy:.1f}%"
            })
            st.rerun()

    # रिजल्ट स्क्रीन
    elif st.session_state.submitted:
        st.header("📊 आपकी परफॉर्मेंस रिपोर्ट")
        
        # इस प्रयास का डेटा
        current_attempt = st.session_state.attempt_history[current_key][-1]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("अंतिम स्कोर (Score)", current_attempt["अंतिम स्कोर"])
        c2.metric("सटीकता (Accuracy)", current_attempt["सटीकता (Accuracy)"])
        c3.metric("सही (Correct)", current_attempt["सही उत्तर"])
        c4.metric("गलत (Wrong)", current_attempt["गलत उत्तर"])
        c5.metric("छोड़े गए (Skipped)", current_attempt["छोड़े गए"])

        st.divider()

        # री-अटेम्प्ट बटन
        col_btn1, col_btn2 = st.columns([1, 2])
        with col_btn1:
            if st.button("🔄 री-अटेम्प्ट टेस्ट (Re-attempt Test)", type="primary"):
                st.session_state.submitted = False
                st.session_state.quiz_started = True
                st.session_state.user_answers = {}
                st.rerun()

        # सभी पिछले प्रयासों की पूरी टेबल
        with st.expander("📜 आपके सभी री-अटेम्प्ट्स का इतिहास देखें (Click to expand)", expanded=True):
            df_history = pd.DataFrame(st.session_state.attempt_history[current_key])
            st.table(df_history)

        st.divider()
        st.subheader("🔍 प्रश्नों का विस्तृत हल (Image Solutions)")
        for idx, q in enumerate(current_questions):
            ans = st.session_state.user_answers.get(idx, "उत्तर नहीं दिया")
            is_correct = (ans == q['answer'])

            with st.expander(f"प्रश्न {idx+1}: {'✅ सही' if is_correct else '❌ गलत/छोड़ा'} - {q['question'][:45]}..."):
                st.write(f"**प्रश्न:** {q['question']}")
                st.write(f"**आपका चयन:** {ans}")
                st.write(f"**सही उत्तर:** :green[{q['answer']}]")
                
                if q.get('sol_image') is not None:
                    st.write("📸 **सॉल्यूशन फोटो:**")
                    st.image(q['sol_image'], use_container_width=True)
                else:
                    st.caption("इस सवाल के लिए कोई सॉल्यूशन फोटो अपलोड नहीं की गई है।")
