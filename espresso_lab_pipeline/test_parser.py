import os
import json
import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

product_dir = 'espresso_lab_pipeline/products'
files = [f for f in os.listdir(product_dir) if f.endswith('.html')]

print(f"Analyzing {len(files)} downloaded product files...")

parsed_coffees = []
non_coffee_items = []

for fname in files:
    handle = fname.replace('.html', '')
    path = os.path.join(product_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract JSON-LD
    json_ld = None
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if data.get('@type') == 'Product':
                json_ld = data
                break
        except Exception:
            pass
    
    if not json_ld:
        continue
    
    name = json_ld.get('name', '')
    add_props = json_ld.get('additionalProperty') or []
    
    # If no additionalProperty and name indicates gear/cup
    if not add_props:
        non_coffee_items.append((name, handle))
        continue
    
    prop_dict = {p.get('name'): p.get('value') for p in add_props if isinstance(p, dict)}
    
    # Check if coffee
    if not any(k in prop_dict for k in ['Variety', 'Process', 'Elevation', 'Tasting notes', 'Available roast profiles']):
        non_coffee_items.append((name, handle))
        continue
    
    price_val = float(json_ld.get('offers', {}).get('price', 0))
    currency = json_ld.get('offers', {}).get('priceCurrency', 'AED')
    image_list = json_ld.get('image', [])
    image_url = image_list[0] if image_list else ''
    weight_val = json_ld.get('weight', {}).get('value', 200)
    
    # Extract description text and particulars
    desc_html = json_ld.get('description', '')
    desc_soup = BeautifulSoup(desc_html, 'html.parser')
    
    # Particulars table in description
    producer = prop_dict.get('Producer', '')
    farm = ''
    location = ''
    country = ''
    
    # Look for particulars table
    table = desc_soup.find('table')
    if table:
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 2:
                k = tds[0].get_text(strip=True).rstrip(':')
                v = tds[1].get_text(strip=True)
                if 'Producer' in k and not producer:
                    producer = v
                elif 'Farm' in k:
                    farm = v
                elif 'Location' in k or 'Origin' in k:
                    location = v
                elif 'Country' in k:
                    country = v
                elif 'Variety' in k and not prop_dict.get('Variety'):
                    prop_dict['Variety'] = v
                elif 'Elevation' in k and not prop_dict.get('Elevation'):
                    prop_dict['Elevation'] = v
    
    # In the description text, extract country/farm/producer if missing
    desc_text = desc_soup.get_text(separator=' ', strip=True)
    
    parsed_coffees.append({
        'handle': handle,
        'title': name,
        'price_aed': price_val,
        'weight': f"{int(weight_val)}g" if weight_val else "200g",
        'weight_num': int(weight_val) if weight_val else 200,
        'image_url': image_url,
        'variety': prop_dict.get('Variety', 'Arabica'),
        'process': prop_dict.get('Process', ''),
        'altitude': prop_dict.get('Elevation', ''),
        'roast': prop_dict.get('Available roast profiles', 'Filter'),
        'tasting_notes': prop_dict.get('Tasting notes', ''),
        'producer': producer,
        'farm': farm,
        'location': location,
        'country': country,
        'desc_snippet': desc_text[:200]
    })

print(f"Total coffee beans parsed: {len(parsed_coffees)}")
print(f"Non-coffee items filtered: {len(non_coffee_items)}")
for c in parsed_coffees[:5]:
    print(f"  {c['title']} | {c['price_aed']} AED ({c['weight']}) | Variety: {c['variety']} | Notes: {c['tasting_notes']}")
