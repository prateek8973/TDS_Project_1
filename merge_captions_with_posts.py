import os
import json

# --- Config ---
POSTS_FILE = './tds_forum_data/tds_all_posts_with_local_images.json'
CAPTION_CACHE_FILE = './caption_cache.json'
OUTPUT_FILE = './tds_forum_data/tds_all_posts_with_image_captions.json'

# --- Load ---
with open(POSTS_FILE, 'r', encoding='utf-8') as f:
    posts = json.load(f)

with open(CAPTION_CACHE_FILE, 'r', encoding='utf-8') as f:
    caption_cache = json.load(f)

# --- Attach captions to each post ---
for post in posts:
    local_paths = post.get("local_image_paths", [])
    captions = [caption_cache.get(path, "") for path in local_paths]
    post["image_captions"] = captions

# --- Save updated posts ---
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"✅ Captions added to posts and saved to: {OUTPUT_FILE}")
