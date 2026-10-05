import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://theespressolab.com/products-details/auromar-firestone-7"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode('utf-8')
    with open('espresso_lab_pipeline/sample_product.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Sample product saved. Length:", len(html))
except Exception as e:
    print("Fetch error:", e)
