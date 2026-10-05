import subprocess
import json
import re
from bs4 import BeautifulSoup

def clean_text(s):
    if not s: return ""
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&amp;', '&', s)
    s = re.sub(r'&quot;', '"', s)
    s = re.sub(r'&#39;', "'", s)
    s = re.sub(r'&nbsp;', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_info(p):
    title = p['title']
    body = p.get('body_html', '')
    soup = BeautifulSoup(body, 'html.parser')
    
    # Specs from body_html
    specs = {
        'producer': '미표기',
        'farm': '미표기',
        'location': '미표기',
        'variety': '미표기',
        'process': '미표기',
        'altitude': '미표기'
    }
    
    lines = [clean_text(s) for s in soup.stripped_strings]
    for line in lines:
        if re.search(r'^(producer|farmer)\s*[:：]', line, re.I):
            specs['producer'] = re.sub(r'^(producer|farmer)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif re.search(r'^(farm|washing station|station|estate)\s*[:：]', line, re.I):
            specs['farm'] = re.sub(r'^(farm|washing station|station|estate)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif re.search(r'^(location|region|origin)\s*[:：]', line, re.I):
            specs['location'] = re.sub(r'^(location|region|origin)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif re.search(r'^(variety|varietal)\s*[:：]', line, re.I):
            specs['variety'] = re.sub(r'^(variety|varietal)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif re.search(r'^(process|processing)\s*[:：]', line, re.I):
            specs['process'] = re.sub(r'^(process|processing)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif re.search(r'^(altitude|elevation)\s*[:：]', line, re.I):
            specs['altitude'] = re.sub(r'^(altitude|elevation)\s*[:：]\s*', '', line, flags=re.I).strip()
            
    # Country detection
    country = '기타'
    countries = ['Panama', 'Ethiopia', 'Colombia', 'Costa Rica', 'Ecuador', 'Guatemala', 'Yemen', 'Kenya', 'El Salvador', 'Honduras', 'Brazil', 'Indonesia', 'India', 'Rwanda', 'Burundi', 'Peru', 'Bolivia']
    for c in countries:
        if c.lower() in title.lower() or c.lower() in specs['location'].lower():
            country = c
            break
            
    # Roast from options
    roast = '라이트 (Filter Roast)'
    for opt in p.get('options', []):
        if 'roast' in opt.get('name', '').lower():
            val = opt.get('values', [''])[0]
            if 'filter | espresso' in val.lower():
                roast = '라이트-미디엄 (Filter | Espresso 옴니로스트)'
            elif 'espresso | milk' in val.lower():
                roast = '미디엄 (Espresso | Milk | Filter)'
            elif 'filter' in val.lower():
                roast = '라이트 (Filter Roast, 핸드드립 권장)'
            break

    # Variants and pricing
    variants = p.get('variants', [])
    parsed_variants = []
    for v in variants:
        v_title = v.get('title', '')
        price = float(v.get('price', 0))
        avail = bool(v.get('available', True))
        
        # parse weight
        m = re.search(r'(\d+)\s*(g|gram|kg|kilogram)', v_title, re.I)
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
        parsed_variants.append({
            'weight_g': g,
            'weight_label': w_label,
            'price': price,
            'available': avail,
            'title': v_title
        })

    # Pick smallest retail variant (<= 250g)
    retail_vars = [v for v in parsed_variants if 0 < v['weight_g'] <= 250]
    # prefer 100g if available, else smallest
    v_100 = [v for v in retail_vars if v['weight_g'] == 100]
    v_200 = [v for v in retail_vars if v['weight_g'] == 200]
    v_250 = [v for v in retail_vars if v['weight_g'] == 250]
    v_50 = [v for v in retail_vars if v['weight_g'] == 50]

    chosen = None
    if v_100: chosen = v_100[0]
    elif v_200: chosen = v_200[0]
    elif v_250: chosen = v_250[0]
    elif v_50: chosen = v_50[0]
    elif retail_vars: chosen = retail_vars[0]
    elif parsed_variants: chosen = parsed_variants[0]
    else: chosen = {'weight_g': 100, 'weight_label': '100g', 'price': 0, 'available': False}

    price_aed = chosen['price']
    weight_label = chosen['weight_label']
    price_per_100g = round((price_aed / chosen['weight_g']) * 100, 2)
    
    return {
        'id': p['id'],
        'title': title,
        'country': country,
        'specs': specs,
        'roast': roast,
        'weight': weight_label,
        'price_aed': price_aed,
        'price_per_100g': price_per_100g,
        'handle': p['handle']
    }

print("Extractor defined successfully.")
