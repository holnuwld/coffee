import json
import os
import subprocess
import re
from bs4 import BeautifulSoup

RAW_FILE = r'c:\cowork\coffee\new_pipeline\raw_collected_coffees.json'
with open(RAW_FILE, 'r', encoding='utf-8') as f:
    coffees = json.load(f)

print(f"Loaded {len(coffees)} coffees.")

# Check first 5 coffees variant structure
for c in coffees[:5]:
    print("\n-------------------------------------------")
    print("Title:", c['title'])
    print("URL:", c['source_url'])
    print("Collection:", c['collection'])
    print("Weight Options in c:", c.get('weight_options'))
    print("Current price_aed:", c.get('price_aed'), "Weight:", c.get('weight'), "Per 100g:", c.get('price_per_100g'))
    print("Roast in c:", c.get('roast'))
