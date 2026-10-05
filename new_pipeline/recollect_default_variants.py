import json
import subprocess
import re

RAW_FILE = r'c:\cowork\coffee\new_pipeline\raw_collected_coffees.json'
with open(RAW_FILE, 'r', encoding='utf-8') as f:
    coffees = json.load(f)

# Re-check each coffee against its default variant from the collection products JSON
COLLECTIONS = ['competition-series-2025', 'microlot-reserve-2025', 'microlot-2026']
products_by_handle = {}
for col in COLLECTIONS:
    out = subprocess.check_output(['curl.exe', '-s', f'https://archerscoffee.com/collections/{col}/products.json?limit=250'])
    data = json.loads(out)
    for p in data['products']:
        products_by_handle[p['handle']] = p

updated_count = 0
for c in coffees:
    h = c['handle']
    p = products_by_handle.get(h)
    if not p: continue
    
    variants = p.get('variants', [])
    if not variants: continue
    
    v0 = variants[0]
    v0_title = v0.get('title', '')
    v0_price = float(v0.get('price', 0))
    
    # parse weight from v0_title
    m = re.search(r'(\d+)\s*(g|gram|kg|kilogram)', v0_title, re.I)
    g = 100
    w_label = '100g'
    if m:
        num = int(m.group(1))
        unit = m.group(2).lower()
        if unit.startswith('k'):
            g = num * 1000
            w_label = f'{num}kg'
        else:
            g = num
            w_label = f'{num}g'
            
    # Check if v0 is retail (<= 250g)
    if 0 < g <= 250:
        old_price = c['price_aed']
        old_weight = c['weight']
        c['weight'] = w_label
        c['price_aed'] = v0_price
        c['price_krw'] = int(v0_price * 380)
        c['price_per_100g_aed'] = round((v0_price / g) * 100, 2)
        c['price_per_100g_krw'] = int(c['price_per_100g_aed'] * 380)
        if old_price != v0_price:
            updated_count += 1
            print(f"Updated {c['title'][:30]}: {old_weight} AED {old_price} -> {w_label} AED {v0_price}")

with open(RAW_FILE, 'w', encoding='utf-8') as f:
    json.dump(coffees, f, indent=2, ensure_ascii=False)

print(f"Re-collection complete: Updated {updated_count} coffees to default visible retail variant.")
