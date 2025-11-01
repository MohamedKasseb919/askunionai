import streamlit as st
import openai

# ========== إعدادات الصفحة ==========
st.set_page_config(page_title="Ask Union AI 🤖", page_icon="🤖", layout="wide")

# ========== شكل الواجهة ==========
st.markdown("""
    <style>
    body {
        background-color: #2b1b3f;
        color: white;
        font-family: "Cairo", sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stTextInput > div > div > input {
        text-align: right;
    }
    .big-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #e6d8ff;
    }
    .chat-bubble {
        background-color: #4b2c6b;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        color: white;
    }
    .user-bubble {
        background-color: #7b4ca0;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# ========== تحميل ملف القرار ==========
with open("decision_62.txt", "r", encoding="utf-8") as f:
    decision_text = f.read()

# ========== إعداد البوت ==========
openai.api_key = st.secrets["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"]

system_prompt = f"""
You are Ask Union AI, an Arabic-speaking educational assistant created by the Student Union of مدرسة منير الجمال الرسمية للغات.
Answer only questions related to student unions, elections, activities, the yearly theme “تشكيل الوعي لعالم متغير”, or the ministerial decision 62 for 2013.
If a question is unrelated, politely redirect to student union topics.
Use Egyptian Arabic that’s friendly and clear.
You have access to the following document for reference:
{decision_text}
"""

# ========== واجهة المستخدم ==========
st.markdown('<p class="big-title">🤖 Ask Union AI - اتحاد الطلبة</p>', unsafe_allow_html=True)
st.write("مرحبـــًا 👋 أنا **Ask Union AI**، المساعد الطلابي الذكي لاتحاد الطلبة! 🎓 جاهز أجاوبك على أي سؤال عن الاتحاد، الترشح، أو موضوع السنة الجميل ✨ *تشكيل الوعي لعالم متغير* 🌍")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

user_input = st.text_input("✏️ اكتب سؤالك هنا:")

if st.button("إرسال"):
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.spinner("جاري التفكير... 🤔"):
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state["messages"]
                ]
            )
            reply = completion.choices[0].message["content"]
            st.session_state["messages"].append({"role": "assistant", "content": reply})

# عرض المحادثة
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

