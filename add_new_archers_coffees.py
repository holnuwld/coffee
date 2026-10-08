import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
    existing_archers = json.load(f)

existing_handles = {c.get('handle') for c in existing_archers}

with open('archers_new_enriched.json', encoding='utf-8') as f:
    new_items = json.load(f)

added = 0
for idx, item in enumerate(new_items, 1000):
    h = item['handle']
    if h in existing_handles:
        continue
    
    p_100g = float(item['price_aed'])
    p_krw = int(p_100g * 380)

    raw_item = {
        "id": 9000000000000 + idx,
        "collection": item['collection'],
        "title": item['title'],
        "handle": h,
        "source_url": item['source_url'],
        "image_url": item.get('image_url', ''),
        "country": item['country'],
        "location": item.get('location', item['country']),
        "farm": item['farm'],
        "producer": item['producer'],
        "variety": item['variety'],
        "process": item['process'],
        "altitude": str(item['altitude']),
        "roast": "라이트-미디엄 (Filter | Espresso) [▪▫▫]",
        "tasting_notes": item['tasting_notes'],
        "weight": "100g",
        "price_aed": p_100g,
        "price_krw": p_krw,
        "price_per_100g_aed": p_100g,
        "price_per_100g_krw": p_krw,
        "korea_status": item['korea_status'],
        "korea_seller": "국내 미수입 독점 랏",
        "korea_link": item['source_url'],
        "korea_price": f"국내 미수입 (현지 {p_100g} AED)",
        "purchase_merit": item['purchase_merit'],
        "user_review": f"아처스 공식 최신 릴리즈 랏. {item['description']}",
        "user_review_link": item['source_url']
    }
    existing_archers.append(raw_item)
    added += 1
    print(f"Added Archers: {item['title']} ({p_100g} AED)")

with open('new_pipeline/raw_collected_coffees.json', 'w', encoding='utf-8') as f:
    json.dump(existing_archers, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully added {added} new coffees to new_pipeline/raw_collected_coffees.json! (Total: {len(existing_archers)})")
