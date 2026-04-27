import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time, json

# ---- CONFIG ----
seed_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
base_domain = "en.wikipedia.org"
MAX_PAGES = 200

# ---- DATA STRUCTURES ----
queue = [seed_url]
visited = set()
pages = []

# ---- CRAWLER LOOP ----
while queue and len(visited) < MAX_PAGES:
    url = queue.pop(0)

    if url in visited:
        continue

    print(f"Crawling: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=5)

        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            continue

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')

    # ---- EXTRACT CONTENT ----
    title = soup.title.string.strip() if soup.title else ""
    text = soup.get_text(separator=" ", strip=True)

    pages.append({
        "url": url,
        "title": title,
        "text": text
    })

    visited.add(url)

    # ---- EXTRACT LINKS ----
    for link in soup.find_all('a', href=True):
        href = link['href']

        # Convert relative → absolute
        full_url = urljoin(url, href)

        parsed = urlparse(full_url)

        # ---- FILTERING ----
        # Stay inside Wikipedia
        if base_domain not in parsed.netloc:
            continue

        # Only real article pages
        if not full_url.startswith("https://en.wikipedia.org/wiki/"):
            continue

        # Remove special pages (File:, Help:, etc.)
        path = parsed.path

        if not path.startswith("/wiki/"):
            continue

        # Skip special pages
        if any(prefix in path for prefix in ["/wiki/File:", "/wiki/Help:", "/wiki/Category:", "/wiki/Special:"]):
            continue

        # Avoid duplicates
        if full_url not in visited:
            queue.append(full_url)

    time.sleep(1)  # be polite

# ---- SAVE DATA ----
with open("data/pages.json", "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)

print(f"\nDone! Crawled {len(pages)} pages.")