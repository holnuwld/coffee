import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

raw_file = 'new_pipeline/raw_collected_coffees.json'
with open(raw_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

for c in data:
    if 'elora' in c['handle'] and c.get('producer') == 'E':
        c['producer'] = 'Eliyas Dukamo & Atiklit Dejene'
        print(f"Fixed {c['handle']} producer to Eliyas Dukamo & Atiklit Dejene")

with open(raw_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
