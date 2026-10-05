import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://archerscoffee.com/products/ethiopia-elto-coffee-elora-station-classic-washed"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
    matches = [m.start() for m in re.finditer(r'Producer', html, re.IGNORECASE)]
    for m in matches:
        print("--- MATCH ---")
        print(html[max(0, m-50):min(len(html), m+300)])
except Exception as e:
    print("Error:", e)
