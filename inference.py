import os
import json
import base64
import numpy as np
from io import BytesIO
from typing import Optional
from PIL import Image
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
FORUM_EMBED_FILE = './tds_forum_data/tds_embeddings_with_metadata.npz'
COURSE_EMBED_FILE = './course_embeddings.npz'
COURSE_CHUNKS_META = './course_chunks.json'
TOP_K = 3

# --- Load Models and Data ---
print("📦 Loading models and data...")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel("gemini-2.0-flash-lite")

forum = np.load(FORUM_EMBED_FILE, allow_pickle=True)
forum_embeddings = forum['embeddings']
forum_metadata = forum['metadata']

course = np.load(COURSE_EMBED_FILE, allow_pickle=True)
course_embeddings = course['embeddings']
course_texts = course['texts']
with open(COURSE_CHUNKS_META, 'r', encoding='utf-8') as f:
    course_metadata = json.load(f)

model = SentenceTransformer('all-MiniLM-L6-v2')

# --- FastAPI App ---
app = FastAPI(title="Virtual Teaching Assistant API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Schema ---
class AskRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64-encoded image

# --- Helpers ---
def decode_image(image_b64: str) -> Image.Image:
    try:
        image_data = base64.b64decode(image_b64)
        return Image.open(BytesIO(image_data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ Failed to decode image: {str(e)}")

def search_top_k(query_embedding, db_embeddings, k=TOP_K):
    sims = cosine_similarity([query_embedding], db_embeddings)[0]
    return np.argsort(sims)[::-1][:k]

def get_forum_links(indices):
    links = []
    for idx in indices:
        post = forum_metadata[idx]
        url = f"https://discourse.onlinedegree.iitm.ac.in/t/{post['topic_id']}"
        links.append({
            "url": url,
            "text": post.get("title", "Forum Post")
        })
    return links

def describe_image(image: Image.Image) -> str:
    try:
        response = gemini.generate_content([
            image,
            "Describe this image for an academic Q&A forum assistant."
        ])
        return response.text.strip()
    except Exception as e:
        return f"(❌ Failed to describe image: {str(e)})"

def build_context(question: str, image_caption: Optional[str] = None):
    query_embedding = model.encode(question)

    forum_idx = search_top_k(query_embedding, forum_embeddings)
    forum_context = "\n\n".join([forum_metadata[i]['text'] for i in forum_idx])
    forum_links = get_forum_links(forum_idx)

    course_idx = search_top_k(query_embedding, course_embeddings)
    course_context = "\n\n".join([course_texts[i] for i in course_idx])

    full_context = f"""You are a virtual assistant for a data science course. Use the forum discussions, course materials, and image (if any) to answer the question.

---

### Course Material:
{course_context}

---

### Forum Discussions:
{forum_context}
"""

    if image_caption:
        full_context += f"\n\n### Image Context:\n{image_caption}"

    full_context += f"\n\nNow answer the question:\n{question}"

    return full_context, forum_links

# --- Endpoint ---
@app.post("/ask")
def ask_virtual_ta(request: AskRequest):
    try:
        image_caption = None

        if request.image:
            image = decode_image(request.image)
            image_caption = describe_image(image)

        context, links = build_context(request.question, image_caption)

        response = gemini.generate_content(context)
        answer = response.text.strip()

        return {
            "answer": answer,
            "links": links
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")
