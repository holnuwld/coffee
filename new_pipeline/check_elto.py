import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('new_pipeline/raw_collected_coffees.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for c in data:
    if 'elto' in c['handle']:
        print(c['handle'], '| Producer:', c.get('producer'), '| Farm:', c.get('farm'), '| Location:', c.get('location'))
