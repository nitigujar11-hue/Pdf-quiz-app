import streamlit as st
import google.generativeai as genai
import PyPDF2
import json

st.set_page_config(page_title="PDF to Quiz AI", page_icon="📝", layout="centered")

# आपकी बिल्कुल सही नई AQ. वाली API Key
genai.configure(api_key="AQ.Ab8RN6Lg43p4YdwsAq2wlb-n5HGqKsHwbdMRCvuNWKhnMpnbhw")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_quiz(text):
    prompt = f"""
    तुम एक एक्सपर्ट क्विज़ मास्टर हो। नीचे दिए गए टेक्स्ट को पढ़ो और उसमें से 5 सबसे महत्वपूर्ण बहुविकल्पीय प्रश्न (MCQs) बनाओ।
    तुम्हारा आउटपुट सिर्फ एक JSON एरे (Array) फॉर्मेट में होना चाहिए।
    
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
    
    # नया और फास्ट AI मॉडल
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # AI को बताना कि जवाब सिर्फ JSON (कंप्यूटर भाषा) में देना है
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    return json.loads(response.text)

st.title("📄 PDF से स्मार्ट क्विज़ 🧠")
st.write("अपनी कोई भी PDF यहाँ अपलोड करें और AI तुरंत आपके लिए एक क्लिक करने वाला क्विज़ तैयार कर देगा!")

uploaded_file = st.file_uploader("यहाँ PDF अपलोड करें (Max: 200MB)", type=["pdf"])

if uploaded_file is not None:
    if st.button("क्विज़ जनरेट करें ✨"):
        with st.spinner("AI आपकी PDF पढ़ रहा है और क्विज़ बना रहा है... कृपया कुछ सेकंड रुकें ⏳"):
            try:
                text = extract_text_from_pdf(uploaded_file)[:15000]
                quiz_data = generate_quiz(text)
                st.session_state.quiz_data = quiz_data
                st.success("क्विज़ तैयार है! 🎉 नीचे खेलना शुरू करें:")
            except Exception as e:
                # अगर अब कोई एरर आएगा, तो वह हमें स्क्रीन पर साफ-साफ बता देगा कि क्या दिक्कत है
                st.error(f"क्विज़ बनाने में दिक्कत आई। असली कारण: {e}")

if "quiz_data" in st.session_state:
    st.divider()
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"### प्रश्न {i+1}: {q['question']}")
        user_choice = st.radio("अपना उत्तर चुनें:", q['options'], key=f"q_{i}", index=None)
        
        if user_choice:
            if user_choice == q['answer']:
                st.success(f"✅ **बिल्कुल सही!** \n\n**व्याख्या:** {q['explanation']}")
            else:
                st.error(f"❌ **गलत उत्तर।** सही उत्तर है: **{q['answer']}** \n\n**व्याख्या:** {q['explanation']}")
        st.write("---")
