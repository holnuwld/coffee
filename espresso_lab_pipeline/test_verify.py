import json
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

sample_records = [
    {
        "item": "Auromar Firestone",
        "field": "price",
        "value": "175",
        "source_url": "https://theespressolab.com/products-details/auromar-firestone-7",
        "quote": "175.00",
        "retrieved_at": "2026-10-06T00:20:00Z",
        "condition": "In stock"
    },
    {
        "item": "Auromar Firestone",
        "field": "tasting_notes",
        "value": "Jasmine",
        "source_url": "https://theespressolab.com/products-details/auromar-firestone-7",
        "quote": "Jasmine, Longan & Yuzu",
        "retrieved_at": "2026-10-06T00:20:00Z",
        "condition": "In stock"
    }
]

with open('espresso_lab_pipeline/test_evidence.json', 'w', encoding='utf-8') as f:
    json.dump(sample_records, f, indent=2, ensure_ascii=False)

print("Saved test_evidence.json. Running verify_quotes.py...")
cmd = [r'.venv\Scripts\python.exe', 'verify_quotes.py', 'espresso_lab_pipeline/test_evidence.json', '-o', 'espresso_lab_pipeline/test_verify_out.json']
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)

with open('espresso_lab_pipeline/test_verify_out.json', 'r', encoding='utf-8') as f:
    out = json.load(f)
print("Result:")
for r in out:
    print(" ", r.get('item'), r.get('field'), "->", r.get('status'), r.get('reason'))
