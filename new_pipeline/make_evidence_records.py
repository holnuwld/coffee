import json
import os
from datetime import datetime

RAW_FILE = r'c:\cowork\coffee\new_pipeline\raw_collected_coffees.json'
EVIDENCE_FILE = r'c:\cowork\coffee\new_pipeline\evidence_records.json'

with open(RAW_FILE, 'r', encoding='utf-8') as f:
    coffees = json.load(f)

now_iso = datetime.utcnow().isoformat() + "Z"
records = []

for c in coffees:
    title = c.get('title', '')
    url = c.get('source_url', '')
    country = c.get('country', '')
    notes = c.get('tasting_notes', '')
    price = c.get('price_aed', 0)
    producer = c.get('producer', '미표기')

    # Record 1: Tasting Notes
    # The quote is the tasting notes string as visible on the site
    if notes and notes != '미표기':
        first_note = notes.split(',')[0].strip()
        records.append({
            "item": title,
            "field": "tasting_notes",
            "value": first_note,
            "source_url": url,
            "quote": notes,
            "retrieved_at": now_iso,
            "condition": {
                "country": country,
                "currency": "AED",
                "price": price
            }
        })

    # Record 2: Country / Origin
    # The quote is the title which contains the country
    if country and country != '기타':
        records.append({
            "item": title,
            "field": "country",
            "value": country,
            "source_url": url,
            "quote": title,
            "retrieved_at": now_iso,
            "condition": {
                "producer": producer
            }
        })

with open(EVIDENCE_FILE, 'w', encoding='utf-8') as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"Generated {len(records)} evidence records into {EVIDENCE_FILE}")
