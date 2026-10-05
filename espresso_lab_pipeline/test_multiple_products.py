import urllib.request
import json
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

test_handles = [
    'bombe-washed-7',
    'kamavindi-giakanja-ab-washed-7',
    'jasmine-cup'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

for h in test_handles:
    url = f"https://theespressolab.com/products-details/{h}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        print(f"\n==================== {h} ====================")
        # Find JSON-LD
        for s in soup.find_all('script', type='application/ld+json'):
            data = json.loads(s.string)
            print("Name:", data.get('name'))
            print("Price:", data.get('offers', {}).get('price'), data.get('offers', {}).get('priceCurrency'))
            print("Image:", data.get('image'))
            print("Weight:", data.get('weight'))
            print("AdditionalProps:", data.get('additionalProperty'))
    except Exception as e:
        print(f"Error for {h}:", e)
