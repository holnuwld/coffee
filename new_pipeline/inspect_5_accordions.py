import io
import sys
import subprocess
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

test_urls = [
    'https://archerscoffee.com/products/panama-elida-estate-geisha-plano-2801',
    'https://archerscoffee.com/products/ethiopia-alo-village-archers-lot-1-sfw',
    'https://archerscoffee.com/products/colombia-letty-finca-el-paraiso',
    'https://archerscoffee.com/products/ethiopia-hamasho-village-washed-archers-lot-2025',
    'https://archerscoffee.com/products/brazil-fazenda-um-supreme-pulp-natural'
]

for url in test_urls:
    print(f"\n========================================================")
    print(f"URL: {url}")
    html = subprocess.check_output(['curl.exe', '-s', url]).decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    
    accordions = soup.find_all(class_='accordion__wrapper')
    for idx, acc in enumerate(accordions):
        title = acc.find(class_='accordion__title')
        title_text = title.get_text().strip() if title else "No Title"
        print(f"  Accordion [{idx}]: {title_text}")
        lines = [line.strip() for line in acc.stripped_strings if line.strip()]
        for l in lines[:15]:
            print("    -", repr(l))
