import urllib.request
import json
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

for h in ['bombe-washed-7', 'kamavindi-giakanja-ab-washed-7']:
    url = f"https://theespressolab.com/products-details/{h}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    for s in soup.find_all('script', type='application/ld+json'):
        data = json.loads(s.string)
        desc = data.get('description', '')
        print(f"\n==================== {h} DESCRIPTION ====================")
        print(desc[:1500])
