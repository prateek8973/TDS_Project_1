import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import time

# --- CONFIG ---
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_ID = 34  # TDS Knowledge Base
START_DATE = "2025-01-01"
END_DATE = "2025-04-15"
SAVE_DIR = "tds_forum_data"
COOKIE_STRING = "_t="  # ⚠️ Required

# --- HEADERS ---
HEADERS = {
    "Accept": "application/json",
    "Cookie": COOKIE_STRING,
    "User-Agent": "Mozilla/5.0"
}

# --- Helpers ---
def iso_date(s): return datetime.strptime(s, "%Y-%m-%d")
def within_range(iso, start, end):
    d = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ")
    return start <= d <= end

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# --- Fetch paginated topics in category ---
def get_all_topics():
    topics = []
    page = 0
    while True:
        url = f"{BASE_URL}/latest.json?category={CATEGORY_ID}&page={page}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"Failed to fetch page {page}: {res.status_code}")
            break
        items = res.json().get("topic_list", {}).get("topics", [])
        if not items:
            break
        topics.extend(items)
        print(f"✔️ Page {page}: {len(items)} topics")
        page += 1
        time.sleep(1)  # polite delay
    return topics

# --- Fetch all posts from a topic ---
def fetch_posts(topic_id):
    url = f"{BASE_URL}/t/{topic_id}.json"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else None

# --- Main ---
def scrape_all():
    os.makedirs(SAVE_DIR, exist_ok=True)
    start, end = iso_date(START_DATE), iso_date(END_DATE)

    topics = get_all_topics()
    print(f"🔍 Total topics fetched: {len(topics)}")

    all_data = []
    for topic in tqdm(topics, desc="Scraping all posts"):
        data = fetch_posts(topic["id"])
        if not data:
            continue

        for post in data["post_stream"]["posts"]:
            created_at = post["created_at"]
            if not within_range(created_at, start, end):
                continue

            soup = BeautifulSoup(post["cooked"], "html.parser")
            images = [img["src"] for img in soup.find_all("img") if img.get("src")]

            all_data.append({
                "topic_id": topic["id"],
                "title": data.get("title"),
                "username": post["username"],
                "created_at": created_at,
                "raw": post.get("raw", ""),
                "cooked_html": post["cooked"],
                "image_urls": images
            })

    save_json(all_data, os.path.join(SAVE_DIR, "tds_all_posts.json"))
    print(f"\n✅ Saved {len(all_data)} posts to 'tds_all_posts.json'.")

if __name__ == "__main__":
    scrape_all()
