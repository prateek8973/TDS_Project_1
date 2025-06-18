import os
import json
import time
import random
from tqdm import tqdm
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# --- Config ---
POSTS_JSON = './tds_forum_data/tds_all_posts_with_local_images.json'
CAPTION_CACHE = './caption_cache.json'
GEMINI_RATE_LIMIT = 30
GEMINI_WAIT_TIME = 60.0 / GEMINI_RATE_LIMIT
MAX_ATTEMPTS = 5

# --- Configure Gemini ---
print("🔑 Configuring Gemini...")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
caption_model = genai.GenerativeModel("gemini-2.0-flash-lite")

# --- Load posts ---
print("📂 Loading posts...")
with open(POSTS_JSON, 'r', encoding='utf-8') as f:
    posts = json.load(f)

# --- Initialize or load caption cache ---
if os.path.exists(CAPTION_CACHE):
    with open(CAPTION_CACHE, 'r', encoding='utf-8') as f:
        try:
            caption_cache = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Warning: Cache file was empty or corrupted, starting fresh.")
            caption_cache = {}
else:
    caption_cache = {}

# --- Caption generation function ---
def generate_caption_with_gemini(local_path):
    if local_path in caption_cache:
        return caption_cache[local_path]

    try:
        image = Image.open(local_path).convert("RGB")
    except Exception as e:
        print(f"❌ Could not open image {local_path}: {e}")
        return None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = caption_model.generate_content([
                "Describe this image in detail:",
                image
            ])
            caption = response.text.strip()

            # Save to cache
            caption_cache[local_path] = caption
            with open(CAPTION_CACHE, 'w', encoding='utf-8') as f:
                json.dump(caption_cache, f, indent=2)

            time.sleep(GEMINI_WAIT_TIME)
            return caption

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait_time = 2 ** attempt + random.uniform(0, 1)
                print(f"⚠️ Rate limit hit, retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Caption generation failed for {local_path}: {e}")
                break

    return None

# --- Process all posts ---
print("🖼️ Starting caption generation for image posts...")

for i, post in tqdm(enumerate(posts), total=len(posts)):
    image_paths = post.get("local_image_paths", [])
    post_captions = []

    for img_path in image_paths:
        print(f"➡️  Captioning {img_path}")
        caption = generate_caption_with_gemini(img_path)
        if caption:
            post_captions.append(caption)
            print(f"✅ {caption}")
        else:
            print(f"⚠️ Failed to caption {img_path}")

    # Optional: store captions in post object for downstream use
    post['image_captions'] = post_captions

# (Optional) Save posts with image_captions if needed
# with open('./tds_forum_data/tds_all_posts_with_captions.json', 'w', encoding='utf-8') as f:
#     json.dump(posts, f, ensure_ascii=False, indent=2)

print("✅ All images processed and captioned.")
