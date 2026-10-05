import subprocess
import json
import re
from bs4 import BeautifulSoup

def inspect(url):
    print(f"\n=================== INSPECTING: {url} ===================")
    out = subprocess.check_output(['curl.exe', '-s', '-L', url])
    html = out.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')

    print("Title:", soup.title.string.strip() if soup.title else "N/A")

    # Meta tags for price
    meta_price = soup.find('meta', property='og:price:amount')
    meta_curr = soup.find('meta', property='og:price:currency')
    print("Meta Price:", meta_price['content'] if meta_price else "None", meta_curr['content'] if meta_curr else "None")

    # Check for ld+json
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get('@type') == 'Product':
                print("JSON-LD Product Name:", data.get('name'))
                offers = data.get('offers')
                if isinstance(offers, list):
                    for o in offers:
                        print("  Offer:", o.get('name'), o.get('price'), o.get('priceCurrency'))
                elif isinstance(offers, dict):
                    print("  Offer:", offers.get('price'), offers.get('priceCurrency'))
        except Exception:
            pass

    # Visible text with price or AED
    price_strings = [s for s in soup.stripped_strings if re.search(r'AED\s*\d+|\d+\s*AED', s, re.I)]
    print("Visible AED strings:", price_strings[:5])

    # Visible text with roast
    roast_strings = [s for s in soup.stripped_strings if 'roast' in s.lower()]
    print("Visible Roast strings:", roast_strings[:10])

    # Check variant selectors
    labels = [l.get_text().strip() for l in soup.find_all('label')]
    print("Labels:", [l for l in labels if any(k in l.lower() for k in ['roast', 'size', 'weight', 'g', 'filter'])][:10])

inspect('https://archerscoffee.com/products/panama-finca-auromar-malla-geisha-washed-peaberry')
inspect('https://archerscoffee.com/products/panama-elida-geisha-washed-plano')
inspect('https://archerscoffee.com/products/ethiopia-alo-village-washed-archers-lot-1')
inspect('https://archerscoffee.com/products/colombia-letty-finca-el-paraiso')
