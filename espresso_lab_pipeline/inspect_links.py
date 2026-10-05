from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/catalog.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Let's inspect all <a> tags inside product list / cards
for a in soup.find_all('a', href=True):
    href = a['href']
    # If href looks like a coffee product
    text = a.get_text(strip=True)
    if any(keyword in href for keyword in ['coffee', 'bean', 'roast', 'product', 'shop']) and len(text) > 2:
        print(f"HREF: {href} | TEXT: {text[:60]}")
