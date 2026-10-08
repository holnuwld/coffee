import urllib.request
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode('utf-8'))

def fetch_html(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.read().decode('utf-8')

print("=== 1. Checking Archers Coffee Collections & Products ===")
try:
    cols_data = fetch_json('https://archerscoffee.com/collections.json?limit=250')
    collections = cols_data.get('collections', [])
    print(f"Total collections found: {len(collections)}")
    coffee_related_cols = []
    for c in collections:
        h = c.get('handle', '')
        t = c.get('title', '')
        if any(k in h.lower() for k in ['micro', 'comp', 'reserve', 'lot', '2025', '2026', 'coffee', 'espresso', 'filter', 'drip']):
            coffee_related_cols.append((h, t))
            print(f"  - [{h}] {t}")
except Exception as e:
    print(f"Error fetching collections: {e}")
    coffee_related_cols = [
        ('microlot-2026', 'Microlot 2026'),
        ('microlot-reserve-2025', 'Microlot Reserve 2025'),
        ('competition-series-2025', 'Competition Series 2025')
    ]

# Fetch products from the 3 main collections + any new relevant collection
archers_live_products = {}
for h, t in coffee_related_cols:
    if h in ['all', 'frontpage']: continue
    # Only fetch coffee lot collections
    if not any(k in h for k in ['microlot', 'competition', 'reserve', 'series']): continue
    try:
        p_url = f"https://archerscoffee.com/collections/{h}/products.json?limit=250"
        p_data = fetch_json(p_url)
        prods = p_data.get('products', [])
        print(f"Collection [{h}]: {len(prods)} products found online")
        for p in prods:
            handle = p['handle']
            if handle not in archers_live_products:
                archers_live_products[handle] = {
                    'title': p['title'],
                    'handle': handle,
                    'collection': h,
                    'published_at': p.get('published_at'),
                    'updated_at': p.get('updated_at'),
                    'variants': len(p.get('variants', [])),
                    'available': any(v.get('available', True) for v in p.get('variants', [])),
                    'min_price': min([float(v.get('price', 0)) for v in p.get('variants', [])]) if p.get('variants') else 0
                }
    except Exception as e:
        print(f"  Error fetching {h}: {e}")

print(f"\nTotal unique live products found on Archers: {len(archers_live_products)}")

# Compare with local archers data
try:
    with open('new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
        archers_local = json.load(f)
    local_handles = {c.get('handle'): c for c in archers_local if c.get('handle')}
    print(f"Total local Archers coffees: {len(local_handles)}")
    
    new_online = []
    for h, p in archers_live_products.items():
        if h not in local_handles:
            new_online.append(p)
            
    removed_online = []
    for h, c in local_handles.items():
        if h not in archers_live_products:
            removed_online.append(c)
            
    print(f"\n[Archers Comparison Result]")
    print(f"- Newly added on website: {len(new_online)}")
    for p in new_online[:10]:
        print(f"   + [NEW] {p['title']} ({p['collection']}) - {p['min_price']} AED (Available: {p['available']})")
    if len(new_online) > 10:
        print(f"   ... and {len(new_online)-10} more")
        
    print(f"- Delisted or missing from these collections: {len(removed_online)}")
    for c in removed_online[:10]:
        print(f"   - [DELISTED/MOVED] {c.get('title')} ({c.get('collection')})")
    if len(removed_online) > 10:
        print(f"   ... and {len(removed_online)-10} more")
except Exception as e:
    print(f"Local comparison error: {e}")

