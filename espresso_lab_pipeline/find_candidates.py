import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/enriched_coffees.json', 'r', encoding='utf-8') as f:
    coffees = json.load(f)

print("=== PANAMA COFFEES ===")
for c in coffees:
    if c['country'] == 'Panama':
        print(f"[{c['handle']}] {c['title']} | Price: {c['price_aed']} AED ({c['weight']}) | 100g: {c['price_per_100g_aed']} AED (약 {c['price_per_100g_krw']:,}원)")
        print(f"  Farm: {c['farm']} | Producer: {c['producer']}")
        print(f"  Variety: {c['variety']} | Process: {c['process']} | Elevation: {c['altitude']}")
        print(f"  Notes: {c['tasting_notes']}")
        print()

print("\n=== ETHIOPIA COFFEES ===")
for c in coffees:
    if c['country'] == 'Ethiopia':
        print(f"[{c['handle']}] {c['title']} | Price: {c['price_aed']} AED ({c['weight']}) | 100g: {c['price_per_100g_aed']} AED (약 {c['price_per_100g_krw']:,}원)")
        print(f"  Farm: {c['farm']} | Producer: {c['producer']}")
        print(f"  Variety: {c['variety']} | Process: {c['process']} | Elevation: {c['altitude']}")
        print(f"  Notes: {c['tasting_notes']}")
        print()
