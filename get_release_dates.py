import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

dates_map = {}

for col in ['competition-series', 'specialty-selection-2026']:
    url = f'https://archerscoffee.com/collections/{col}/products.json?limit=250'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
        for p in data.get('products', []):
            h = p['handle']
            pub = p.get('published_at') or p.get('created_at') or ''
            # Format: '2025-02-14T08:31:00+04:00' -> '0214' or '1008'
            if pub:
                # extract month and day
                m_d = pub[5:7] + pub[8:10]
            else:
                m_d = '1008'
            dates_map[h] = m_d
            print(f"{h}: {pub} -> {m_d}")
    except Exception as e:
        print(f"Error fetching {col}: {e}")

# Espresso Lab handles default to 1008
dates_map['samambaia-natural-yellow-catucai'] = '1008'
dates_map['caballero-bomba-de-fruta-1-6'] = '1008'

with open('new_coffee_dates.json', 'w', encoding='utf-8') as f:
    json.dump(dates_map, f, ensure_ascii=False, indent=2)

print("\nSaved new_coffee_dates.json!")
