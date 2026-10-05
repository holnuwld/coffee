import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/raw_parsed_coffees.json', 'r', encoding='utf-8') as f:
    coffees = json.load(f)

print(f"Loaded {len(coffees)} coffees.")

needs_refine = []
for idx, c in enumerate(coffees, 1):
    status = []
    if c['country'] in ['Specialty Origin', '']: status.append('country')
    if c['producer'] in ['Specialty Producer', '']: status.append('producer')
    if c['farm'] in [c['title'], '']: status.append('farm')
    if c['location'] in [c['country'], '']: status.append('location')
    
    if status:
        needs_refine.append((idx, c['handle'], c['title'], status, c['desc_text'][:120]))

print(f"\nCoffees needing field refinement: {len(needs_refine)}")
for item in needs_refine:
    print(f"#{item[0]} [{item[1]}] {item[2]} -> missing {item[3]}")
    print(f"   Desc: {item[4]}")
