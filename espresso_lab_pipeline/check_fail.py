import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/verified_output.json', 'r', encoding='utf-8') as f:
    out = json.load(f)

for r in out:
    if r.get('status') != 'PASS':
        print(f"Failed record: {r.get('item')} [{r.get('field')}]")
        print(f"  URL: {r.get('source_url')}")
        print(f"  Quote: {r.get('quote')}")
        print(f"  Reason: {r.get('reason')}")
