import urllib.request
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.makedirs('espresso_lab_pipeline', exist_ok=True)

url = "https://theespressolab.com/products?sort_by=alphabetical_az&roast_profiles%5B%5D=1&min_price=&max_price="
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        html_content = resp.read().decode('utf-8')
    print("Fetched successfully. Content length:", len(html_content))
    with open('espresso_lab_pipeline/catalog.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Saved to espresso_lab_pipeline/catalog.html")
except Exception as e:
    print("Fetch error:", e)
