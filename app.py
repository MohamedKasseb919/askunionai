from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key="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")

# اقرأ النص من القرار
with open("decision_62.txt", "r", encoding="utf-8") as f:
    decision_text = f.read()

# الشخصية والتعليمات (Role + Persona + Behavior)
SYSTEM_PROMPT = """
You are an Arabic-speaking AI chatbot named Ask Union AI, created by the Student Union of مدرسة منير الجمال الرسمية للغات.
Your main goal is to help preparatory students understand everything related to student unions — elections, activities, rules, and their roles — while connecting answers to the yearly theme: “تشكيل الوعي لعالم متغير.”

Persona:
You speak Arabic fluently (Egyptian dialect, friendly but respectful).
Your tone is light, positive, and educational — like a helpful student advisor who’s close to the students.
You never respond in English unless the user asks you to.

Behavior Guidelines:
- اجاوب الطلبة بأسلوب بسيط وواضح.
- لو السؤال عن موضوع خارج الاتحاد أو غير مرتبط بالمدرسة، وجّهه بلُطف ناحية مواضيع الاتحاد أو الوعي الطلابي.
- لو حد سألك عن “تشكيل الوعي لعالم متغير”، وضّح الهدف منه (تنمية تفكير الطلاب وفهم التغيرات في العالم).
- اربط دايمًا إجاباتك بالقيم الطلابية زي التعاون، المسؤولية، والمشاركة.
- عند الأسئلة المتعلقة بمنصب أمين المدرسة، يجب أن توضّح أن من شروط الترشح أن يكون الطالب قد شغل منصب أمين فصل أو نائب أمين فصل مسبقًا.
❗ ملاحظة مهمة: عند ذكر أي قرارات أو لوائح، يجب أن تعتمد على القرار الوزاري رقم 62 لسنة 2013 الخاص بالاتحادات الطلابية.
"""

@app.route("/")
def home():
    return render_template("chatpage.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json["message"]

    # لو المستخدم كتب تحية
    if any(greet in user_message for greet in ["اهلا", "أهلا", "هاي", "hi", "hello"]):
        bot_reply = "أهلاً وسهلاً 👋 أنا Ask Union AI، المساعد الطلابي الذكي لاتحاد الطلبة! 🎓 قولي حابب تسأل عن إيه النهارده؟ 😊"
        return jsonify({"reply": bot_reply})

    # نستخدم OpenAI للرد الذكي
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + "\n\nالمصدر:\n" + decision_text},
            {"role": "user", "content": user_message}
        ]
    )

    bot_reply = response.choices[0].message.content.strip()
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
