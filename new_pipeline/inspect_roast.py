import subprocess
import json
import re
from bs4 import BeautifulSoup

def check_product(handle):
    out = subprocess.check_output(['curl.exe', '-s', f'https://archerscoffee.com/products/{handle}.json'])
    d = json.loads(out)
    p = d['product']
    print(f"=== {p['title']} ===")
    print("Options:", p['options'])
    for v in p['variants'][:3]:
        print(f"  Variant: {v['title']} -> Price: {v['price']}")
    
    # Check body HTML for Roast
    body = p.get('body_html', '')
    soup = BeautifulSoup(body, 'html.parser')
    for p_tag in soup.find_all(['p', 'div', 'li']):
        t = p_tag.get_text().strip()
        if 'roast' in t.lower() or 'filter' in t.lower() or 'espresso' in t.lower():
            print("  Body text:", t)

check_product('panama-finca-auromar-malla-geisha-washed-peaberry')
check_product('panama-elida-geisha-washed-plano')
check_product('ethiopia-alo-village-washed-archers-lot-1')
check_product('colombia-letty-finca-el-paraiso')
check_product('brazil-fazenda-um-supreme-pulp-natural')
