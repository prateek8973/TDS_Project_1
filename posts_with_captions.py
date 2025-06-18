import os
import json
from bs4 import BeautifulSoup

# --- Config ---
INPUT_FILE = './tds_forum_data/tds_all_posts_with_image_captions.json'
OUTPUT_FILE = './tds_forum_data/tds_all_posts_final.json'

# --- Load posts ---
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    posts = json.load(f)

# --- Process posts ---
for post in posts:
    html = post.get("cooked_html", "")
    captions = post.get("image_captions", [])
    
    if not captions or not html:
        continue  # skip if no images or no HTML

    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")

    for img_tag, caption in zip(img_tags, captions):
        caption_tag = soup.new_tag("em")
        caption_tag.string = caption
        img_tag.replace_with(caption_tag)

    post["cooked_html_with_captions"] = str(soup)

# --- Save result ---
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"✅ Captions embedded in HTML and saved to: {OUTPUT_FILE}")
