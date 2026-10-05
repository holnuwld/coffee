import sys
import io
import json
import subprocess
import re
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Let's inspect 5 diverse products
test_urls = [
    'https://archerscoffee.com/products/brazil-fazenda-um-supreme-pulp-natural',
    'https://archerscoffee.com/products/panama-finca-auromar-malla-geisha-washed-peaberry',
    'https://archerscoffee.com/products/panama-elida-estate-geisha-plano-2801',
    'https://archerscoffee.com/products/ethiopia-alo-village-washed-archers-lot-1',
    'https://archerscoffee.com/products/colombia-letty-finca-el-paraiso'
]

for url in test_urls:
    print(f"\n========================================================")
    print(f"URL: {url}")
    out = subprocess.check_output(['curl.exe', '-s', '-L', url])
    html = out.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')

    # Look for Roast in body text
    body_text = soup.get_text()
    roast_mentions = [line.strip() for line in body_text.splitlines() if 'roast' in line.lower() and len(line.strip()) < 100]
    print("Roast mentions in page:")
    for r in roast_mentions[:5]:
        print("  -", repr(r))

    # Look for options dropdown/buttons in HTML
    # Check for select or radio buttons with name containing Roast
    roast_options = []
    for select in soup.find_all(['select', 'fieldset', 'div']):
        name = select.get('name', '') or select.get('class', '') or select.get('data-select-label', '')
        if 'roast' in str(name).lower():
            roast_options.append((str(name), select.get_text().strip()))
    print("Roast UI elements:", roast_options[:3])

    # Check Shopify product JSON for options
    json_url = url + '.json'
    try:
        j_out = subprocess.check_output(['curl.exe', '-s', '-L', json_url])
        j_data = json.loads(j_out)
        p = j_data['product']
        print("Shopify Options:")
        for opt in p.get('options', []):
            print(f"  Option: {opt.get('name')} -> {opt.get('values')}")
        print("Shopify Variants (first 3):")
        for v in p.get('variants', [])[:3]:
            print(f"  Variant Title: {v.get('title')} | Price: {v.get('price')}")
    except Exception as e:
        print("JSON fetch error:", e)
