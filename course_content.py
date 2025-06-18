import os
import requests
import re

BASE_URL = "https://tds.s-anand.net/#/2025-01/"
SIDEBAR_URL = BASE_URL + "_sidebar.md"
SAVE_DIR = "tds_content"

os.makedirs(SAVE_DIR, exist_ok=True)

# Step 1: Download sidebar.md
print("[+] Downloading sidebar.md...")
resp = requests.get(SIDEBAR_URL)
sidebar_content = resp.text

# Step 2: Extract all .md links
md_links = re.findall(r'\(([^)]+\.md)\)', sidebar_content)
md_links = list(set(md_links))  # Remove duplicates

print(f"[+] Found {len(md_links)} .md files to download.")

# Step 3: Download each .md file
for link in md_links:
    full_url = BASE_URL + link
    print(f"    ↳ Downloading: {link}")
    try:
        r = requests.get(full_url)
        if r.status_code == 200:
            save_path = os.path.join(SAVE_DIR, os.path.basename(link))
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(r.text)
        else:
            print(f"      [!] Failed ({r.status_code})")
    except Exception as e:
        print(f"      [!] Error: {e}")

print("\n✅ Done downloading all Markdown files.")
import os
import requests
import re

BASE_URL = "https://tds.s-anand.net/"
SIDEBAR_URL = BASE_URL + "_sidebar.md"
SAVE_DIR = "tds_content"

os.makedirs(SAVE_DIR, exist_ok=True)

# Step 1: Download sidebar.md
print("[+] Downloading sidebar.md...")
resp = requests.get(SIDEBAR_URL)
sidebar_content = resp.text

# Step 2: Extract all .md links
md_links = re.findall(r'\(([^)]+\.md)\)', sidebar_content)
md_links = list(set(md_links))  # Remove duplicates

print(f"[+] Found {len(md_links)} .md files to download.")

# Step 3: Download each .md file
for link in md_links:
    full_url = BASE_URL + link
    print(f"Downloading: {link}")
    try:
        r = requests.get(full_url)
        if r.status_code == 200:
            save_path = os.path.join(SAVE_DIR, os.path.basename(link))
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(r.text)
        else:
            print(f"Failed ({r.status_code})")
    except Exception as e:
        print(f"Error: {e}")

print("\n Done downloading all Markdown files.")
