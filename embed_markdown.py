import os
import json
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# --- Config ---
MARKDOWN_DIR = "tds_content"
EMBEDDING_FILE = "course_embeddings.npz"
CHUNKS_METADATA_FILE = "course_chunks.json"
CHUNK_SIZE = 500

# --- Load model ---
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Helpers ---
def chunk_text(text, max_len=500):
    sentences = text.split(". ")
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_len:
            current += s + ". "
        else:
            chunks.append(current.strip())
            current = s + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks

def clean_markdown(md_text):
    lines = [line for line in md_text.splitlines() if not line.strip().startswith("![]")]
    return "\n".join(lines)

# --- Process all .md files ---
print(f"Scanning markdown files in: {MARKDOWN_DIR}")
all_chunks = []
chunk_meta = []
for filename in tqdm(os.listdir(MARKDOWN_DIR)):
    if filename.endswith(".md"):
        path = os.path.join(MARKDOWN_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        content = clean_markdown(content)
        chunks = chunk_text(content, max_len=CHUNK_SIZE)

        for chunk in chunks:
            all_chunks.append(chunk)
            chunk_meta.append({
                "file": filename,
                "chunk": chunk[:200].strip() + "...",
            })

# --- Embed chunks ---
print(f"Embedding {len(all_chunks)} chunks...")
embeddings = model.encode(all_chunks)

# --- Save to disk ---
np.savez_compressed(EMBEDDING_FILE,
                    embeddings=np.array(embeddings),
                    texts=np.array(all_chunks))

with open(CHUNKS_METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(chunk_meta, f, indent=2)

print(f"✅ Done. Chunks: {len(all_chunks)} → Saved to {EMBEDDING_FILE} + {CHUNKS_METADATA_FILE}") 