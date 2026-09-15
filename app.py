import streamlit as st
import requests
import PyPDF2
import json
import re

st.set_page_config(page_title="PDF to Quiz AI", page_icon="📝", layout="centered")

st.title("📄 PDF से स्मार्ट क्विज़ 🧠")

# API Key के लिए साइडबार
with st.sidebar:
    st.header("⚙️ सेटिंग्स")
    raw_api_key = st.text_input("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", type="password")
    st.markdown("*(API Key सुरक्षित है)*")
    
user_api_key = raw_api_key.strip().replace('"', '').replace("'", "") if raw_api_key else ""

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_quiz(text, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    तुम एक एक्सपर्ट क्विज़ मास्टर हो। नीचे दिए गए टेक्स्ट को पढ़ो और महत्वपूर्ण बहुविकल्पीय प्रश्न (MCQs) बनाओ।
    आउटपुट सिर्फ JSON एरे (Array) फॉर्मेट में होना चाहिए। कोई अतिरिक्त बात मत लिखना।
    [
        {{
            "question": "प्रश्न",
            "options": ["A", "B", "C", "D"],
            "answer": "सही विकल्प",
            "explanation": "व्याख्या"
        }}
    ]
    टेक्स्ट: {text[:15000]}
    """
    
    data = {
        # OpenRouter का 100% फ्री मॉडल (Llama 3.1)
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        raise Exception(f"OpenRouter Error: {response.text}")
        
    result = response.json()
    clean_text = result['choices'][0]['message']['content'].strip()
    
    # JSON को साफ करने का स्मार्ट तरीका
    match = re.search(r'\[.*\]', clean_text, re.DOTALL)
    if match:
        clean_text = match.group(0)
        
    return json.loads(clean_text)

# मुख्य वेबसाइट लॉजिक
if not user_api_key:
    st.info("👈 क्विज़ बनाने से पहले बाईं तरफ (Sidebar) में अपनी OpenRouter API Key पेस्ट करें।")
else:
    uploaded_file = st.file_uploader("यहाँ PDF अपलोड करें (Max: 200MB)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("क्विज़ जनरेट करें ✨"):
            with st.spinner("AI आपकी प्रैक्टिस के लिए शानदार सवाल तैयार कर रहा है... ⏳"):
                try:
                    text = extract_text_from_pdf(uploaded_file)
                    quiz_data = generate_quiz(text, user_api_key)
                    st.session_state.quiz_data = quiz_data
                    st.success("क्विज़ तैयार है! 🎉 अपनी 10-मिनट की टाइमर वाली प्रैक्टिस शुरू करें:")
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
                st.success(f"✅ **बिल्कुल सही जवाब!** {q['explanation']}")
            else:
                st.error(f"❌ **गलत!** सही उत्तर है: **{q['answer']}**. {q['explanation']}")
        st.write("---")
