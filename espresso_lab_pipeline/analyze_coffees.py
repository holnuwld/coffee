import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/enriched_coffees.json', 'r', encoding='utf-8') as f:
    coffees = json.load(f)

print(f"Total Coffees: {len(coffees)}")

countries = {}
for c in coffees:
    cnt = c['country']
    countries[cnt] = countries.get(cnt, 0) + 1

print("\n--- Country Distribution ---")
for cnt, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
    print(f"{cnt}: {count}종")

for t in ['Guji Hambela Rogicha', 'Harusuke', 'La Negrita Mundo Novo', 'Mi Finquita Geisha Lot 153']:
    items = [c for c in coffees if c['title'] == t]
    print(f"\nComparing '{t}':")
    for it in items:
        print(f"  Handle: {it['handle']} | Notes: {it['tasting_notes']} | Alt: {it['altitude']} | Process: {it['process']} | Price: {it['price_aed']} AED")
