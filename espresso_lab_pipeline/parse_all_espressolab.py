import os
import json
import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

product_dir = 'espresso_lab_pipeline/products'
files = sorted([f for f in os.listdir(product_dir) if f.endswith('.html')])

print(f"Parsing {len(files)} files...")

coffees = []
non_coffees = []

# Country keywords
KNOWN_COUNTRIES = [
    'Panama', 'Ethiopia', 'Colombia', 'Kenya', 'Ecuador', 'Costa Rica',
    'Brazil', 'Guatemala', 'Yemen', 'Honduras', 'El Salvador', 'Bolivia',
    'Peru', 'Rwanda', 'Burundi', 'Indonesia', 'Mexico', 'Nicaragua'
]

for fname in files:
    handle = fname.replace('.html', '')
    path = os.path.join(product_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # JSON-LD
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
    
    name = json_ld.get('name', '').strip()
    add_props = json_ld.get('additionalProperty') or []
    
    # If no additionalProperty and name indicates gear
    if not add_props:
        non_coffees.append((name, handle, "No additionalProperty"))
        continue
    
    prop_dict = {}
    for p in add_props:
        if isinstance(p, dict) and p.get('name'):
            prop_dict[p.get('name')] = p.get('value')
    
    # Check if coffee
    if not any(k in prop_dict for k in ['Variety', 'Process', 'Elevation', 'Tasting notes', 'Available roast profiles']):
        non_coffees.append((name, handle, "Missing coffee properties"))
        continue
    
    price_val = float(json_ld.get('offers', {}).get('price', 0))
    currency = json_ld.get('offers', {}).get('priceCurrency', 'AED')
    image_list = json_ld.get('image', [])
    image_url = image_list[0] if image_list else ''
    weight_obj = json_ld.get('weight') or {}
    weight_val = weight_obj.get('value', 200) if isinstance(weight_obj, dict) else 200
    if not weight_val or weight_val <= 0:
        weight_val = 200
    
    # Description parsing
    desc_html = json_ld.get('description', '')
    desc_soup = BeautifulSoup(desc_html, 'html.parser')
    
    producer = prop_dict.get('Producer', '').strip()
    farm = ''
    location = ''
    country = ''
    
    # 1. Particulars Table
    table = desc_soup.find('table')
    if table:
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 2:
                k = tds[0].get_text(strip=True).rstrip(':').strip()
                v = tds[1].get_text(strip=True).strip()
                if ('Producer' in k or 'Farmer' in k) and not producer:
                    producer = v
                elif 'Farm' in k and not farm:
                    farm = v
                elif ('Location' in k or 'Region' in k or 'Origin' in k) and not location:
                    location = v
                elif 'Country' in k and not country:
                    country = v
                elif 'Variety' in k and not prop_dict.get('Variety'):
                    prop_dict['Variety'] = v
                elif 'Elevation' in k and not prop_dict.get('Elevation'):
                    prop_dict['Elevation'] = v
    
    # 2. Inspect description text for Farm, Producer, Region, Country
    desc_text = desc_soup.get_text(separator=' ', strip=True)
    
    # Find country in description or name
    if not country:
        for c_candidate in KNOWN_COUNTRIES:
            if re.search(r'\b' + re.escape(c_candidate) + r'\b', desc_text, re.I) or re.search(r'\b' + re.escape(c_candidate) + r'\b', name, re.I):
                country = c_candidate
                break
    
    # If still no country, infer from region/handle/producer
    if not country:
        if any(w in handle for w in ['auromar', 'geisha', 'lamastus', 'kotowa', 'lerida', 'chevas', 'nuguo', 'salto']):
            country = 'Panama'
        elif any(w in handle for w in ['guji', 'hambela', 'bombe', 'yirgacheffe', 'sidama', 'haru', 'testi']):
            country = 'Ethiopia'
        elif any(w in handle for w in ['kamavindi', 'cianda', 'giakanja']):
            country = 'Kenya'
        elif any(w in handle for w in ['daterra', 'carmo', 'samambaia']):
            country = 'Brazil'
        elif any(w in handle for w in ['la-negrita', 'milan', 'rubi']):
            country = 'Colombia'
    
    # Extract Farm if not found
    if not farm:
        # Search for Finca ... or Estate or Farm
        farm_match = re.search(r'(Finca\s+[\w\s]+|[\w\s]+Estate|[\w\s]+Farm|Hacienda\s+[\w\s]+)', desc_text)
        if farm_match:
            farm_candidate = farm_match.group(1).strip()
            # Clean up
            farm_candidate = farm_candidate.split('.')[0].split(',')[0].strip()
            if len(farm_candidate) < 40 and not any(bad in farm_candidate.lower() for bad in ['specialty', 'coffee', 'processing', 'about']):
                farm = farm_candidate
    
    # Extract Producer if not found
    if not producer:
        prod_match = re.search(r'produced by\s+([^,.]+)|by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', desc_text)
        if prod_match:
            producer = (prod_match.group(1) or prod_match.group(2) or '').strip()
    
    # Clean altitude
    altitude = prop_dict.get('Elevation', '')
    if altitude and not altitude.endswith('m') and not altitude.endswith('masl'):
        altitude = f"{altitude} masl"
    elif altitude and altitude.endswith('m'):
        altitude = f"{altitude}asl"
    
    # Process
    process = prop_dict.get('Process', '').strip()
    
    # Variety
    variety = prop_dict.get('Variety', '').strip()
    
    # Roast
    roast = prop_dict.get('Available roast profiles', 'Filter').strip()
    
    # Tasting notes
    notes = prop_dict.get('Tasting notes', '').strip()
    
    # 100g price calculation
    krw_price = int(round(price_val * 380))
    p100_aed = round((price_val / weight_val) * 100, 1)
    p100_krw = int(round(p100_aed * 380))
    
    coffees.append({
        'handle': handle,
        'title': name,
        'country': country or 'Specialty Origin',
        'location': location or country,
        'farm': farm or name,
        'producer': producer or 'Specialty Producer',
        'variety': variety or 'Arabica',
        'process': process or 'Specialty Process',
        'altitude': altitude or 'High Altitude',
        'roast': roast or 'Filter',
        'tasting_notes': notes or 'Specialty Floral & Fruity',
        'weight': f"{int(weight_val)}g",
        'weight_num': int(weight_val),
        'price_aed': price_val,
        'price_krw': krw_price,
        'price_per_100g_aed': p100_aed,
        'price_per_100g_krw': p100_krw,
        'image_url': image_url,
        'source_url': f"https://theespressolab.com/products-details/{handle}",
        'desc_text': desc_text
    })

print(f"Total Valid Coffee Products: {len(coffees)}")
print(f"Filtered out Non-Coffee Items: {len(non_coffees)}")
for nc in non_coffees:
    print(f"  Non-coffee: {nc[0]} ({nc[1]}) - {nc[2]}")

with open('espresso_lab_pipeline/raw_parsed_coffees.json', 'w', encoding='utf-8') as out_f:
    json.dump(coffees, out_f, ensure_ascii=False, indent=2)

print("Saved raw_parsed_coffees.json")
