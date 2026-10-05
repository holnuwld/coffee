import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('new_pipeline/raw_collected_coffees.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for c in data:
    for k in ['producer', 'farm', 'location', 'variety', 'process', 'altitude']:
        val = c.get(k, '')
        if len(val) < 3 or val.startswith('E<') or val == 'E':
            print(f"Handle: {c['handle']}, Field: {k}, Value: {val}")
