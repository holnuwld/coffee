import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('new_pipeline/raw_collected_coffees.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

handles = [
    'panama-finca-auromar-malla-geisha-washed-peaberry',
    'panama-elida-estate-geisha-plano-2801',
    'panama-finca-los-cenizos-geisha-washed-gw-208',
    'ethiopia-hamasho-village-washed-archers-lot-2025',
    'ethiopia-elto-coffee-elora-station-classic-washed',
    'finca-del-putushio-typica-mejorado-rt',
    'ethiopia-elto-coffee-sama-washed',
    'ethiopia-benti-nenka-guji-hambela',
    'costa-rica-cafe-rivense-black-honey'
]

for h in handles:
    matched = [c for c in data if c['handle'] == h]
    if matched:
        c = matched[0]
        print("="*60)
        print(f"Title: {c['title']}")
        print(f"Collection: {c['collection']}")
        print(f"Handle: {c['handle']}")
        print(f"Country: {c['country']}, Location: {c['location']}")
        print(f"Farm: {c['farm']}, Producer: {c['producer']}")
        print(f"Variety: {c['variety']}, Process: {c['process']}, Altitude: {c['altitude']}, Roast: {c['roast']}")
        print(f"Price: AED {c['price_aed']} ({c['weight']}) -> KRW {c['price_krw']:,}원")
        print(f"100g Price: AED {c['price_per_100g_aed']} -> KRW {c['price_per_100g_krw']:,}원")
        print(f"Notes: {c['tasting_notes']}")
        print(f"Korea Status: {c.get('korea_status')}")
        print(f"Korea Seller: {c.get('korea_seller')}")
        print(f"Korea Price: {c.get('korea_price')}")
        print(f"Korea Link: {c.get('korea_link')}")
        print(f"Review: {c.get('user_review')}")
        print(f"Review Link: {c.get('user_review_link')}")
        print(f"Merit: {c.get('purchase_merit')}")
