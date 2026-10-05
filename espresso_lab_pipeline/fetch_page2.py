import urllib.request
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

url_page2 = "https://theespressolab.com/products?sort_by=alphabetical_az&roast_profiles%5B0%5D=1&page=2"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

req = urllib.request.Request(url_page2, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        html2 = resp.read().decode('utf-8')
    with open('espresso_lab_pipeline/catalog_page2.html', 'w', encoding='utf-8') as f:
        f.write(html2)
    print("Page 2 saved. Length:", len(html2))
    
    soup2 = BeautifulSoup(html2, 'html.parser')
    for a in soup2.find_all('a', href=True):
        if 'page=' in a['href']:
            print("Page 2 pagination link:", a['href'], "| text:", a.get_text(strip=True))
except Exception as e:
    print("Error fetching page 2:", e)
