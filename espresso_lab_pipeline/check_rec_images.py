import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('espresso_lab_pipeline/enriched_coffees.json', encoding='utf-8'))
c_map = {c['handle']: c for c in data}
recs = [
    'auromar-firestone',
    'bombe-washed',
    'sl28-santa-isabel',
    'el-rubi-parainema-anaerobic-washed-lot-a',
    'kamavindi-giakanja-ab-washed',
    'kotowa-las-brujas-ethiopian-natural-lot-4219'
]

print("=== Exact image URLs in enriched_coffees.json ===")
for r in recs:
    c = c_map.get(r)
    if c:
        print(f"{r} -> image: {c.get('image_url')}")
    else:
        print(f"NOT FOUND: {r}")
