from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/catalog.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

for a in soup.find_all('a', href=True):
    if 'page=' in a['href']:
        print("Page link:", a['href'], "| text:", a.get_text(strip=True))
