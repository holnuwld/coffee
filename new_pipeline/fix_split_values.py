import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

raw_file = 'new_pipeline/raw_collected_coffees.json'
with open(raw_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed_count = 0
for c in data:
    if c['handle'] == 'colombia-luna-finca-el-paraiso' and c['altitude'] == '1,':
        c['altitude'] = '1,960 masl'
        fixed_count += 1
        print("Fixed colombia-luna altitude to 1,960 masl")
    if 'elto' in c['handle'] and c.get('producer') == 'E':
        c['producer'] = 'Eliyas Dukamo & Atiklit Dejene'
        fixed_count += 1
        print(f"Fixed {c['handle']} producer to Eliyas Dukamo & Atiklit Dejene")

with open(raw_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Updated {fixed_count} records in {raw_file}")
