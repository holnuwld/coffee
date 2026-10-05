import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/catalog.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("Page title:", soup.title.string if soup.title else "No title")

# Check pagination
pagination = soup.find_all(class_=re.compile(r'pagination|paginate', re.I))
print("Pagination elements found:", len(pagination))
for p in pagination:
    print("Pagination html:", p.get_text(strip=True))

# Check product links
product_links = set()
for a in soup.find_all('a', href=True):
    href = a['href']
    if '/products/' in href:
        clean_href = href.split('?')[0]
        product_links.add(clean_href)

print(f"Total unique product links found: {len(product_links)}")
for l in sorted(product_links):
    print("  ", l)

# Let's inspect product cards in the catalog
product_cards = soup.find_all(class_=re.compile(r'product-card|product-item|grid-item|card', re.I))
print(f"Product card elements found: {len(product_cards)}")
