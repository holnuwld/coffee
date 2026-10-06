import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

espressolab = json.load(open('espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8'))

print("=== The Espresso Lab 100g coffees ===")
for c in espressolab:
    if '100' in str(c.get('weight', '')):
        print(f"[{c['country']}] {c['title']} | {c['variety']} | {c['process']} | {c['price_aed']} AED ({c['price_krw']:,}원)")
