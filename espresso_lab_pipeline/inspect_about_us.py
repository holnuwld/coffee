import requests
import sys
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://theespressolab.com/about-us', headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

text = soup.get_text()
lines = [l.strip() for l in text.split('\n') if l.strip()]

print("=== Text excerpt from About Us ===")
for l in lines:
    if any(k in l.lower() for k in ['roast', 'profile', 'filter', 'craft', 'philosophy', 'light']):
        print(f"  {l}")
