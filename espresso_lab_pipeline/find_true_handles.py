import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('espresso_lab_pipeline/enriched_coffees.json', encoding='utf-8'))

print("Searching handles in enriched_coffees.json:")
for c in data:
    for kw in ['auromar', 'bombe', 'santa-isabel', 'giakanja', 'rubi', 'kotowa']:
        if kw in c['handle'] or kw in c['title'].lower():
            print(f"Matched '{kw}': handle={c['handle']}, title={c['title']}, img={c.get('image_url')}")
