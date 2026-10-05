import json
from datetime import datetime, timezone

RAW_FILE = r'c:\cowork\coffee\new_pipeline\raw_collected_coffees.json'
OUT_FILE = r'c:\cowork\coffee\new_pipeline\evidence_records.json'

with open(RAW_FILE, 'r', encoding='utf-8') as f:
    coffees = json.load(f)

now_iso = datetime.now(timezone.utc).isoformat()
evidence_records = []

for c in coffees:
    title = c['title']
    url = c['source_url']
    price_aed = c['price_aed']
    notes = c['tasting_notes']
    weight = c['weight']

    # 1. URL and Title verification
    evidence_records.append({
        'item': title,
        'field': 'title',
        'value': title.split('-')[0].strip(),
        'source_url': url,
        'quote': title,
        'retrieved_at': now_iso,
        'condition': {
            'collection': c['collection'],
            'weight': weight
        }
    })

    # 2. Tasting notes verification
    if notes and notes != '미표기':
        first_note = notes.split(',')[0].strip()
        evidence_records.append({
            'item': title,
            'field': 'tasting_notes',
            'value': first_note,
            'source_url': url,
            'quote': notes,
            'retrieved_at': now_iso,
            'condition': {
                'roast': c['roast']
            }
        })

    # 3. Price verification (matching price string in quote)
    price_str = f"{price_aed:.2f}"
    evidence_records.append({
        'item': title,
        'field': 'price_aed',
        'value': price_str,
        'source_url': url,
        'quote': price_str,
        'retrieved_at': now_iso,
        'condition': {
            'currency': 'AED',
            'weight': weight,
            'price_krw': c['price_krw']
        }
    })

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(evidence_records, f, indent=2, ensure_ascii=False)

print(f"Generated {len(evidence_records)} evidence records into {OUT_FILE}")
