import streamlit as st
import google.generativeai as genai
import PyPDF2
import json

# पेज की डिज़ाइन और टाइटल सेट करना
st.set_page_config(page_title="PDF to Quiz AI", page_icon="📝", layout="centered")

# आपकी दी गई API Key यहाँ जोड़ दी गई है
genai.configure(api_key="AQ.Ab8RN6IOjzXqIb8OOq8QgrGZ4sexZgaCZsXzHi3hBmI1nih32Q")

# 1. PDF से टेक्स्ट निकालने का फंक्शन
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# 2. AI से क्विज़ जनरेट करने का फंक्शन
def generate_quiz(text):
    # AI को निर्देश (Prompt) देना
    prompt = f"""
    तुम एक एक्सपर्ट क्विज़ मास्टर हो। नीचे दिए गए टेक्स्ट को पढ़ो और उसमें से 5 सबसे महत्वपूर्ण बहुविकल्पीय प्रश्न (MCQs) बनाओ।
    तुम्हारा आउटपुट सिर्फ एक JSON फॉर्मेट में होना चाहिए। कोई और फालतू बात मत लिखना।
    
    JSON का फॉर्मेट बिल्कुल ऐसा होना चाहिए:
    [
        {{
            "question": "प्रश्न यहाँ लिखें",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "सही विकल्प का पूरा टेक्स्ट यहाँ लिखें",
            "explanation": "यह उत्तर सही क्यों है, 1-2 लाइन में समझाएं"
        }}
    ]
    
    यहाँ पीडीएफ का टेक्स्ट है:
    {text}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash') # फास्ट और फ्री AI मॉडल
    response = model.generate_content(prompt)
    
    # AI के जवाब को साफ करके JSON में बदलना
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)


# --- वेबसाइट का डिज़ाइन (UI) ---

st.title("📄 PDF से स्मार्ट क्विज़ 🧠")
st.write("अपनी कोई भी PDF यहाँ अपलोड करें और AI तुरंत आपके लिए एक क्लिक करने वाला क्विज़ तैयार कर देगा!")

# PDF अपलोड करने का बटन
uploaded_file = st.file_uploader("यहाँ PDF अपलोड करें (Max: 200MB)", type=["pdf"])

# जब कोई PDF अपलोड करे
if uploaded_file is not None:
    if st.button("क्विज़ जनरेट करें ✨"):
        with st.spinner("AI आपकी PDF पढ़ रहा है और क्विज़ बना रहा है... कृपया कुछ सेकंड रुकें ⏳"):
            try:
                # PDF से टेक्स्ट निकालें (शुरू के 15,000 अक्षर ताकि स्पीड तेज़ रहे)
                text = extract_text_from_pdf(uploaded_file)[:15000]
                
                # AI से क्विज़ बनवाएं
                quiz_data = generate_quiz(text)
                
                # क्विज़ को मेमोरी (Session State) में सेव करें
                st.session_state.quiz_data = quiz_data
                st.success("क्विज़ तैयार है! 🎉 नीचे खेलना शुरू करें:")
            except Exception as e:
                st.error("क्विज़ बनाने में कोई तकनीकी दिक्कत आई। कृपया दोबारा कोशिश करें।")

# --- क्विज़ खेलने का इंटरफेस ---

if "quiz_data" in st.session_state:
    st.divider() # एक लाइन खींचने के लिए
    
    # हर सवाल को स्क्रीन पर दिखाना
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"### प्रश्न {i+1}: {q['question']}")
        
        # 4 क्लिक करने वाले ऑप्शंस (Radio Buttons)
        user_choice = st.radio("अपना उत्तर चुनें:", q['options'], key=f"q_{i}", index=None)
        
        # जैसे ही यूजर किसी ऑप्शन पर क्लिक करेगा:
        if user_choice:
            if user_choice == q['answer']:
                st.success(f"✅ **बिल्कुल सही!** \n\n**व्याख्या:** {q['explanation']}")
            else:
                st.error(f"❌ **गलत उत्तर।** सही उत्तर है: **{q['answer']}** \n\n**व्याख्या:** {q['explanation']}")
        
        st.write("---") # सवालों के बीच गैप
