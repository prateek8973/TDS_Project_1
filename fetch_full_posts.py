import os
import json
import time
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
COOKIES = {
    '_t': '',  # paste your _t cookie value here
    '_forum_session': '',  # paste your _forum_session cookie here if needed
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json'
}

# --- DIRECTORY SETUP ---
os.makedirs('full_posts', exist_ok=True)

# --- FETCH FULL POST CONTENT ---
saved_topics_dir = 'tds_topics'  # directory where your topic summaries are saved
files = [f for f in os.listdir(saved_topics_dir) if f.startswith('topic_') and f.endswith('.json')]

for fname in files:
    with open(os.path.join(saved_topics_dir, fname), 'r', encoding='utf-8') as f:
        topic_data = json.load(f)
        topic_id = topic_data['id']
        topic_title = topic_data['title']
        topic_slug = topic_data.get('slug')
        if not topic_slug:
            print(f"[!] Skipping topic {topic_id} as slug is missing")
            continue

    print(f"[+] Fetching topic {topic_id}: {topic_title}")

    topic_url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_slug}/{topic_id}.json"
    resp = requests.get(topic_url, headers=HEADERS, cookies=COOKIES)

    if resp.status_code != 200:
        print(f"[!] Failed to fetch topic {topic_id}, status: {resp.status_code}")
        continue

    topic_json = resp.json()
    posts = topic_json.get('post_stream', {}).get('posts', [])

    # Save cleaned content to markdown file
    markdown_lines = [f"# {topic_title}\n"]
    for post in posts:
        raw_html = post.get('cooked', '')
        soup = BeautifulSoup(raw_html, 'html.parser')
        text = soup.get_text().strip()
        markdown_lines.append(text)
        markdown_lines.append('\n---\n')

    save_path = os.path.join('full_posts', f'topic_{topic_id}.md')
    with open(save_path, 'w', encoding='utf-8') as f_out:
        f_out.write('\n'.join(markdown_lines))

    print(f"     Saved: {save_path}")
    time.sleep(0.5)  # be nice to the server
