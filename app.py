import os, json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import openai
try:
    import faiss
except Exception:
    faiss = None
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
EMBED_MODEL = 'text-embedding-3-small'
CHAT_MODEL = 'gpt-4o-mini'

use_faiss = False
if os.path.exists('docs_index.faiss') and faiss is not None:
    index = faiss.read_index('docs_index.faiss')
    with open('meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
    use_faiss = True
elif os.path.exists('embeddings.npy') and os.path.exists('meta.json'):
    embeddings = np.load('embeddings.npy')
    with open('meta.json','r',encoding='utf-8') as f:
        meta = json.load(f)
else:
    index = None
    meta = []

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

class ChatRequest(BaseModel):
    question: str
    k: int = 4

SYSTEM_PROMPT = """أنت بوت اسمه Ask Union AI — مساعد اتحاد الطلاب.
بتجاوب على الأسئلة الخاصة بالاتحادات الطلابية في المدارس والجامعات المصرية.
اتكلم باللهجة المصرية المهذبة، ورد بإيجاز ومن غير تكلف.
لو حد سألك مين عملك، قول: أنا من تصميم اتحاد طلاب مدرسة منير الجمال الرسمية للغات.
لو السؤال مش متعلق بالاتحاد، وجّهه بلُطف لموضوع الاتحاد.
"""

def embed_text(text):
    resp = openai.Embedding.create(model=EMBED_MODEL, input=text)
    return np.array(resp['data'][0]['embedding'], dtype='float32')

def retrieve_top_k(query, k=4):
    q_emb = embed_text(query)
    if use_faiss:
        D, I = index.search(np.array([q_emb]), k)
        return [meta[i]['text'] for i in I[0]]
    else:
        sims = embeddings.dot(q_emb)
        topk_idx = np.argsort(-sims)[:k]
        return [meta[int(i)]['text'] for i in topk_idx]

@app.post('/chat')
def chat_endpoint(req: ChatRequest):
    q = req.question
    contexts = retrieve_top_k(q, req.k)
    context_text = '\n\n'.join(contexts)
    user_prompt = f"السؤال: {q}\n\nالمراجع:\n{context_text}\n\nأجب بالعربية باللهجة المصرية."
    response = openai.ChatCompletion.create(
        model=CHAT_MODEL,
        messages=[{'role':'system','content': SYSTEM_PROMPT},
                  {'role':'user','content': user_prompt}],
        max_tokens=600,
        temperature=0.2
    )
    return JSONResponse({'answer': response['choices'][0]['message']['content']})

@app.get('/chatpage.html')
def serve_ui():
    return FileResponse('chatpage.html')

@app.get('/')
def root():
    return {'status':'ok'}
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "✅ السيرفر شغال تمام! جرب تضيف الشات بعدين."

    app.run(debug=True)

