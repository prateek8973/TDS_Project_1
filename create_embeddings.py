import json
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# --- Config ---
INPUT_FILE = './tds_forum_data/tds_all_posts_with_image_captions.json'
OUTPUT_NPZ_FILE = './tds_forum_data/tds_embeddings_with_metadata.npz'
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# --- Load Posts ---
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    posts = json.load(f)

# --- Load Model ---
model = SentenceTransformer(EMBEDDING_MODEL)

# --- Prepare Texts and Metadata ---
texts = []
metadata = []

for post in posts:
    html = post.get("cooked_html", "").strip()
    captions = post.get("image_captions", [])

    # Use cooked_html_with_captions if available, else compose manually
    if "cooked_html_with_captions" in post:
        text = post["cooked_html_with_captions"].strip()
    else:
        caption_text = "\n".join(captions).strip()
        text = html
        if caption_text:
            text += "\n" + caption_text

    if text:
        texts.append(text)
        metadata.append({
            "topic_id": post.get("topic_id"),
            "title": post.get("title"),
            "username": post.get("username"),
            "created_at": post.get("created_at"),
            "text": text,
        })

# --- Generate Embeddings ---
print(f"🔍 Generating embeddings for {len(texts)} posts...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# --- Save to .npz ---
np.savez_compressed(
    OUTPUT_NPZ_FILE,
    embeddings=embeddings,
    metadata=np.array(metadata, dtype=object)
)

print(f"✅ Saved embeddings and metadata to: {OUTPUT_NPZ_FILE}") 