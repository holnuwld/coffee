from bs4 import BeautifulSoup
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/sample_product.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

for script in soup.find_all('script', type='application/ld+json'):
    try:
        data = json.loads(script.string)
        desc = data.get('description', '')
        print("=== DESCRIPTION IN JSON-LD ===")
        print(desc)
    except Exception as e:
        print("Error:", e)
