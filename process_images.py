import os
import json
import requests
from tqdm import tqdm

# --- Config ---
INPUT_JSON = './tds_forum_data/tds_all_posts.json'
OUTPUT_JSON = './tds_forum_data/tds_all_posts_with_local_images.json'
IMAGE_DIR = './tds_forum_data/images'

# Create image directory
os.makedirs(IMAGE_DIR, exist_ok=True)

# Load posts
with open(INPUT_JSON, 'r', encoding='utf-8') as f:
    posts = json.load(f)

# Function to download image and return local path
def download_image(url, post_idx, img_idx):
    ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
    filename = f'post{post_idx}_img{img_idx}{ext}'
    filepath = os.path.join(IMAGE_DIR, filename)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        else:
            print(f"❌ Failed: {url} — Status code {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error downloading {url}: {e}")
    return None

# Process each post
for i, post in tqdm(enumerate(posts), total=len(posts), desc="📥 Downloading images"):
    local_paths = []
    for j, url in enumerate(post.get('image_urls', [])):
        local_path = download_image(url, i, j)
        if local_path:
            local_paths.append(local_path)
    post['local_image_paths'] = local_paths

# Save updated posts
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print("✅ All images downloaded and paths saved.")
