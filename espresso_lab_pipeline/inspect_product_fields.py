from bs4 import BeautifulSoup
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/sample_product.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("Title:", soup.title.string if soup.title else "No title")

# Check OpenGraph meta tags
for meta in soup.find_all('meta'):
    prop = meta.get('property', meta.get('name', ''))
    content = meta.get('content', '')
    if any(k in prop for k in ['title', 'price', 'image', 'description']):
        print(f"Meta [{prop}]: {content[:100]}")

# Check JSON-LD
for script in soup.find_all('script', type='application/ld+json'):
    try:
        data = json.loads(script.string)
        print("JSON-LD found:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        print("JSON-LD parse error:", e)

# Check specifications or details tables/lists
print("\n--- SPECIFICATIONS OR ACCORDIONS ---")
for el in soup.find_all(['table', 'dl', 'ul', 'div'], class_=re.compile(r'spec|detail|attr|info|meta', re.I)):
    txt = el.get_text(separator=' | ', strip=True)
    if any(k in txt.lower() for k in ['variety', 'altitude', 'producer', 'process', 'farm', 'notes']):
        print(f"Found specs container [{el.name} class={el.get('class')}]:")
        print(txt[:400])
        print("="*40)
