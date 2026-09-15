import streamlit as st
import google.generativeai as genai
import PyPDF2
import json

st.set_page_config(page_title="PDF to Quiz AI", page_icon="📝", layout="centered")

st.title("📄 PDF से स्मार्ट क्विज़ 🧠")

# API Key के लिए साइडबार (Sidebar)
with st.sidebar:
    st.header("⚙️ सेटिंग्स")
    user_api_key = st.text_input("अपनी API Key यहाँ पेस्ट करें:", type="password")
    st.markdown("*(API Key सुरक्षित है और कहीं सेव नहीं होगी)*")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_quiz(text, api_key):
    # यूज़र की डाली हुई API Key इस्तेमाल करना
    genai.configure(api_key=api_key)
    
    prompt = f"""
    तुम एक एक्सपर्ट क्विज़ मास्टर हो। नीचे दिए गए टेक्स्ट को पढ़ो और 5 सबसे महत्वपूर्ण बहुविकल्पीय प्रश्न (MCQs) बनाओ।
    आउटपुट सिर्फ JSON फॉर्मेट में होना चाहिए।
    
    [
        {{
            "question": "प्रश्न यहाँ लिखें",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "सही विकल्प का पूरा टेक्स्ट",
            "explanation": "व्याख्या"
        }}
    ]
    
    टेक्स्ट:
    {text}
    """
    
    # सबसे स्टेबल (Stable) AI मॉडल
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# मुख्य वेबसाइट
if not user_api_key:
    st.info("👈 कृपया क्विज़ बनाने से पहले बाईं तरफ (Sidebar) में अपनी API Key पेस्ट करें।")
else:
    uploaded_file = st.file_uploader("यहाँ PDF अपलोड करें (Max: 200MB)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("क्विज़ जनरेट करें ✨"):
            with st.spinner("AI क्विज़ बना रहा है... ⏳"):
                try:
                    text = extract_text_from_pdf(uploaded_file)[:15000]
                    quiz_data = generate_quiz(text, user_api_key)
                    st.session_state.quiz_data = quiz_data
                    st.success("क्विज़ तैयार है! 🎉")
                except Exception as e:
                    st.error(f"एरर आ गया: {e}")

# क्विज़ खेलने का इंटरफेस
if "quiz_data" in st.session_state:
    st.divider()
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"### प्रश्न {i+1}: {q['question']}")
        user_choice = st.radio("अपना उत्तर चुनें:", q['options'], key=f"q_{i}", index=None)
        
        if user_choice:
            if user_choice == q['answer']:
                st.success(f"✅ **सही!** {q['explanation']}")
            else:
                st.error(f"❌ **गलत!** सही उत्तर है: **{q['answer']}**. {q['explanation']}")
        st.write("---")
