import glob
import re
from bs4 import BeautifulSoup

print("Searching roasting / filter profile descriptions in crawled pages...")

# Check catalog.html and several product htmls
files = glob.glob('espresso_lab_pipeline/products/*.html')[:10] + ['espresso_lab_pipeline/catalog.html']

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        text = soup.get_text()
        matches = re.findall(r'.{0,100}(?:Filter Roast|roast profile|roasting|roast level|Omni|Light roast).{0,100}', text, re.IGNORECASE)
        if matches:
            print(f"\n--- {fpath} ---")
            for m in matches[:3]:
                clean_m = ' '.join(m.split())
                print(f"  [Found]: {clean_m}")
