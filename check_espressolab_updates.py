import urllib.request
from bs4 import BeautifulSoup
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_html(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.read().decode('utf-8')

print("=== 2. Checking The Espresso Lab Products ===")

# 1. Fetch products pages from theespressolab.com
base_url = "https://theespressolab.com/products"

# Let's inspect multiple pages or sort options if pagination exists
all_live_espressolab = {}

# We check page 1 to 5 to make sure we get everything
for page in range(1, 6):
    page_url = f"https://theespressolab.com/products?page={page}"
    print(f"Fetching {page_url}...")
    try:
        html = fetch_html(page_url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for product cards/links
        found_in_page = 0
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/products-details/' in href:
                clean_url = href.split('?')[0]
                if not clean_url.startswith('http'):
                    clean_url = 'https://theespressolab.com' + clean_url
                handle = clean_url.split('/products-details/')[-1].strip('/')
                
                # Try to extract title, price, sold out status
                card = a.find_parent(class_=re.compile(r'product|card|item|col', re.I))
                card_text = card.get_text(separator=' ', strip=True) if card else ''
                
                is_sold_out = 'sold out' in card_text.lower() or 'out of stock' in card_text.lower()
                
                if handle not in all_live_espressolab:
                    all_live_espressolab[handle] = {
                        'url': clean_url,
                        'handle': handle,
                        'text': card_text,
                        'sold_out': is_sold_out
                    }
                    found_in_page += 1
        print(f"Page {page}: found {found_in_page} new product links (total so far: {len(all_live_espressolab)})")
        if found_in_page == 0 and page > 1:
            break
    except Exception as e:
        print(f"Page {page} error: {e}")
        break

# Also check roastery coffee catalog specifically if filtered
filter_url = "https://theespressolab.com/products?sort_by=alphabetical_az&roast_profiles%5B%5D=1"
try:
    print(f"Checking filtered coffee catalog: {filter_url}...")
    html = fetch_html(filter_url)
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/products-details/' in href:
            clean_url = href.split('?')[0]
            if not clean_url.startswith('http'):
                clean_url = 'https://theespressolab.com' + clean_url
            handle = clean_url.split('/products-details/')[-1].strip('/')
            if handle not in all_live_espressolab:
                all_live_espressolab[handle] = {
                    'url': clean_url,
                    'handle': handle,
                    'text': '',
                    'sold_out': False
                }
except Exception as e:
    print(f"Filter url error: {e}")

print(f"\nTotal live products found on The Espresso Lab: {len(all_live_espressolab)}")

# Compare with local Espresso Lab data
try:
    with open('espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
        tel_local = json.load(f)
    print(f"Total local Espresso Lab coffees: {len(tel_local)}")
    
    local_handles = set()
    for c in tel_local:
        h = c.get('handle') or c.get('source_url', '').split('/products-details/')[-1].strip('/')
        if h: local_handles.add(h)
        
    new_tel = []
    for h, p in all_live_espressolab.items():
        if h not in local_handles:
            new_tel.append(p)
            
    removed_tel = []
    for h in local_handles:
        if h not in all_live_espressolab:
            removed_tel.append(h)
            
    print(f"\n[The Espresso Lab Comparison Result]")
    print(f"- Newly added on website: {len(new_tel)}")
    for p in new_tel:
        print(f"   + [NEW] {p['handle']} -> {p['url']}")
        
    print(f"- Delisted or missing from catalog: {len(removed_tel)}")
    for h in removed_tel:
        print(f"   - [DELISTED/MISSING] {h}")
        
except Exception as e:
    print(f"Comparison error: {e}")
