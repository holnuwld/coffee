import sys
from bs4 import BeautifulSoup
import re
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/products/auromar-firestone-7.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Check visible text
text = soup.get_text(separator=' ', strip=True)

print("Length of visible text:", len(text))
print("Does 'Jasmine' appear in text?", 'jasmine' in text.lower())
print("Does 'Longan' appear in text?", 'longan' in text.lower())

# Let's find matches for tasting notes or jasmine in raw html vs visible text
for line in text.split('\n'):
    if 'jasmine' in line.lower() or 'longan' in line.lower() or 'yuzu' in line.lower():
        print("MATCH LINE:", line[:150])

matches = [m.start() for m in re.finditer(r'jasmine', html, re.I)]
print("Total occurrences of 'jasmine' in raw HTML:", len(matches))
for m in matches[:5]:
    print("--- RAW CONTEXT ---")
    print(html[m-50:m+150])
