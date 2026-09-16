import streamlit as st
import google.generativeai as genai
import PyPDF2
import json

st.set_page_config(page_title="PDF to Quiz AI", page_icon="📝", layout="centered")

st.title("📄 PDF से स्मार्ट क्विज़ 🧠")

# API Key के लिए साइडबार
with st.sidebar:
    st.header("⚙️ सेटिंग्स")
    raw_api_key = st.text_input("AQ.Ab8RN6LZYNd_oQz5qzHezh6Ak-M9ykMqRMyi--uE96le6k88Vg", type="password")
    st.markdown("*(आपकी API Key सुरक्षित है)*")
    
# चाबी को ऑटोमैटिक साफ करना (अगर गलती से "" आ जाएं तो हट जाएंगे)
user_api_key = raw_api_key.strip().replace('"', '').replace("'", "") if raw_api_key else ""

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_quiz(text, api_key):
    genai.configure(api_key=api_key)
    prompt = f"""
    तुम एक एक्सपर्ट क्विज़ मास्टर हो। नीचे दिए गए टेक्स्ट को पढ़ो और 5 सबसे महत्वपूर्ण बहुविकल्पीय प्रश्न (MCQs) बनाओ।
    आउटपुट सिर्फ JSON फॉर्मेट में होना चाहिए।
    
    [
        {{
            "question": "प्रश्न",
            "options": ["A", "B", "C", "D"],
            "answer": "सही विकल्प",
            "explanation": "व्याख्या"
        }}
    ]
    
    टेक्स्ट: {text}
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# मुख्य वेबसाइट लॉजिक
if not user_api_key:
    st.info("👈 क्विज़ बनाने से पहले बाईं तरफ (Sidebar) में अपनी API Key पेस्ट करें। (अगर बॉक्स नहीं दिख रहा, तो ऊपर बाएँ कोने में `>` बटन दबाएं)")
else:
    uploaded_file = st.file_uploader("यहाँ PDF अपलोड करें (Max: 2TB)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("क्विज़ जनरेट करें ✨"):
            with st.spinner("AI आपके लिए शानदार सवाल तैयार कर रहा है... ⏳"):
                try:
                    text = extract_text_from_pdf(uploaded_file)[:15000]
                    quiz_data = generate_quiz(text, user_api_key)
                    st.session_state.quiz_data = quiz_data
                    st.success("क्विज़ तैयार है! 🎉 अपनी प्रैक्टिस शुरू करें:")
                except Exception as e:
                    st.error(f"माफ़ करें, API Key अभी भी काम नहीं कर रही। असली कारण: {e}")

# क्विज़ खेलने का इंटरफेस
if "quiz_data" in st.session_state:
    st.divider()
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"### प्रश्न {i+1}: {q['question']}")
        user_choice = st.radio("अपना उत्तर चुनें:", q['options'], key=f"q_{i}", index=None)
        
        if user_choice:
            if user_choice == q['answer']:
                st.success(f"✅ **सही जवाब!** {q['explanation']}")
            else:
                st.error(f"❌ **गलत!** सही उत्तर है: **{q['answer']}**. {q['explanation']}")
        st.write("---")
