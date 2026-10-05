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
        print("=== JSON-LD COMPLETE ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("Error:", e)

# Also let's inspect #tel_coffee_info or main product container in DOM
info = soup.find(id='tel_coffee_info')
if info:
    print("=== #tel_coffee_info FOUND ===")
    print(info.prettify()[:2000])

# Also let's check product images
print("\n=== PRODUCT IMAGES ===")
for img in soup.find_all('img'):
    src = img.get('src', img.get('data-src', ''))
    if any(k in src.lower() for k in ['product', 'media', 'coffee', 'upload']):
        print("Img src:", src, "| alt:", img.get('alt'))
