from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

all_products = {}

for page_file in ['espresso_lab_pipeline/catalog.html', 'espresso_lab_pipeline/catalog_page2.html']:
    with open(page_file, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Let's find all product cards or links
    # Look for any link containing /products-details/
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/products-details/' in href:
            clean_url = href.split('?')[0]
            # Try to find the parent container or card
            card = a.find_parent(class_=re.compile(r'product|card|item|col', re.I))
            if clean_url not in all_products:
                all_products[clean_url] = {
                    'url': clean_url,
                    'handle': clean_url.split('/products-details/')[-1],
                    'card_html': str(card) if card else ''
                }

print(f"Total unique products found across pages 1 and 2: {len(all_products)}")
for k, v in sorted(all_products.items()):
    print("  ", v['handle'], "->", k)
