import urllib.request
import json
import os
import time
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

os.makedirs('espresso_lab_pipeline/products', exist_ok=True)

# List of all 55 product handles discovered from the catalog
with open('espresso_lab_pipeline/catalog.html', 'r', encoding='utf-8') as f1:
    h1 = f1.read()
with open('espresso_lab_pipeline/catalog_page2.html', 'r', encoding='utf-8') as f2:
    h2 = f2.read()

urls = set()
for html_text in [h1, h2]:
    soup = BeautifulSoup(html_text, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/products-details/' in href:
            clean = href.split('?')[0]
            urls.add(clean)

print(f"Total product URLs to process: {len(urls)}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

downloaded = 0
for idx, u in enumerate(sorted(urls), 1):
    handle = u.split('/products-details/')[-1]
    save_path = f"espresso_lab_pipeline/products/{handle}.html"
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        continue
    
    print(f"[{idx}/{len(urls)}] Fetching {handle}...")
    req = urllib.request.Request(u, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
        with open(save_path, 'w', encoding='utf-8') as out_f:
            out_f.write(content)
        downloaded += 1
        time.sleep(0.15)
    except Exception as e:
        print(f"  Error fetching {u}: {e}")

print(f"Finished crawling. Downloaded {downloaded} new pages.")
