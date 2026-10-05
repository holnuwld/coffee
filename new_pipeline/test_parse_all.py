import subprocess
import json
import re
from bs4 import BeautifulSoup

COLLECTIONS = [
    ('microlot-2026', 'Microlot Selection 2026'),
    ('microlot-reserve-2025', 'Microlot Reserve 2025'),
    ('competition-series-2025', 'Competition Series 2025')
]

all_products = []
for slug, cat in COLLECTIONS:
    out = subprocess.check_output(['curl.exe', '-s', f'https://archerscoffee.com/collections/{slug}/products.json?limit=250'])
    data = json.loads(out)
    for p in data['products']:
        p['_category'] = cat
        all_products.append(p)

print(f"Total products fetched: {len(all_products)}")

# Check options across all products
option_names = set()
roast_values = set()
weight_values = set()

for p in all_products:
    for opt in p.get('options', []):
        option_names.add(opt.get('name'))
        if 'roast' in opt.get('name', '').lower():
            roast_values.update(opt.get('values', []))
        if 'weight' in opt.get('name', '').lower() or 'size' in opt.get('name', '').lower():
            weight_values.update(opt.get('values', []))

print("Option names:", option_names)
print("Roast values:", roast_values)
print("Weight values:", weight_values)
