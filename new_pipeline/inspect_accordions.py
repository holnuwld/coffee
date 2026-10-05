import io
import sys
import subprocess
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

html = subprocess.check_output(['curl.exe', '-s', 'https://archerscoffee.com/products/panama-finca-auromar-malla-geisha-washed-peaberry']).decode('utf-8', errors='ignore')
soup = BeautifulSoup(html, 'html.parser')

accordions = soup.find_all(class_='accordion__wrapper')
print(f"Total accordion wrappers: {len(accordions)}")

for idx, acc in enumerate(accordions):
    title = acc.find(class_='accordion__title')
    title_text = title.get_text().strip() if title else "No Title"
    print(f"\n[{idx}] Accordion Title: {title_text}")
    print("Content:")
    # print clean lines
    for line in acc.stripped_strings:
        print("  |", line)
