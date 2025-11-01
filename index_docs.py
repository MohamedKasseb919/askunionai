import os, json, time
from dotenv import load_dotenv
from tqdm import tqdm
import openai
try:
    import faiss
except Exception as e:
    faiss = None
import numpy as np

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

DOC_PATH = "decision_62.txt"
EMBED_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
BATCH = 10

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

if not os.path.exists(DOC_PATH):
    print(f"ERROR: Document file not found: {DOC_PATH}. Put your training file into the project folder and try again.")
    raise SystemExit(1)

print("Reading document...")
with open(DOC_PATH, 'r', encoding='utf-8') as f:
    txt = f.read()

print("Splitting into chunks...")
chunks = chunk_text(txt)
print(f"Total chunks: {len(chunks)}")

embeddings = []
for i in tqdm(range(0, len(chunks), BATCH), desc='Embedding batches'):
    batch = chunks[i:i+BATCH]
    resp = openai.Embedding.create(model=EMBED_MODEL, input=batch)
    for r in resp['data']:
        embeddings.append(np.array(r['embedding'], dtype='float32'))
    time.sleep(0.05)

if len(embeddings) != len(chunks):
    print("Warning: embeddings count != chunks count")

d = len(embeddings[0])
if faiss is not None:
    index = faiss.IndexFlatL2(d)
    index.add(np.vstack(embeddings))
    faiss.write_index(index, 'docs_index.faiss')
    print('FAISS index created: docs_index.faiss')
else:
    np.save('embeddings.npy', np.vstack(embeddings))
    print('FAISS not available. embeddings.npy saved as fallback.')

meta = [{'text': chunks[i], 'chunk_id': i} for i in range(len(chunks))]
with open('meta.json', 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print('meta.json written.')
