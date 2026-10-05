import urllib.request
import json
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

collections = [
    ('microlot-2026', 'https://archerscoffee.com/collections/microlot-2026'),
    ('microlot-reserve-2025', 'https://archerscoffee.com/collections/microlot-reserve-2025'),
    ('competition-series-2025', 'https://archerscoffee.com/collections/competition-series-2025')
]

for name, url in collections:
    print(f"=== {name} ===")
    json_url = f"{url}/products.json"
    try:
        req = urllib.request.Request(json_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"JSON endpoint worked! Found {len(data.get('products', []))} products.")
            for p in data.get('products', []):
                print(f" - {p.get('title')} (handle: {p.get('handle')})")
    except Exception as e:
        print(f"JSON failed ({e}), trying HTML...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                html = resp.read().decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                # find product links
                links = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '/products/' in href:
                        links.add(href.split('?')[0])
                print(f"HTML worked! Found {len(links)} product links.")
                for l in sorted(links):
                    print(f" - {l}")
        except Exception as e2:
            print(f"HTML also failed: {e2}")
