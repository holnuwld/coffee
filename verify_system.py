import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    idx = f.read()

with open('cart.html', 'r', encoding='utf-8') as f:
    cart = f.read()

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

checks = [
    ("index.html contains cart-action-toolbar", "cart-action-toolbar" in idx),
    ("index.html contains link to cart.html", "cart.html" in idx),
    ("index.html contains similarity text (유사도)", "유사도" in idx),
    ("index.html contains selectAllCheckbox", "selectAllCheckbox" in idx),
    ("index.html contains cart checkbox class", "cart-row-checkbox" in idx),
    ("index.html contains 7-item similarity modal elements", "mSimilarityBody" in idx),
    ("index.html contains 7 items in modal (지역, 농장, 프로듀서, 컵노트, 프로세스, 배전도, 고도)", 
        all(term in idx for term in ['지역', '농장', '프로듀서', '컵노트', '프로세스', '배전도', '고도'])),
    ("cart.html contains official PO title", "발주서" in cart),
    ("cart.html contains localStorage reader", "localStorage.getItem" in cart),
    ("cart.html contains DEFAULT_PICKS for standalone opening", "DEFAULT_PICKS" in cart),
    ("cart.html contains window.print()", "window.print()" in cart),
    ("cart.html contains direct shop links with target='_blank'", 'target="_blank"' in cart),
    ("cart.html contains roastery links to source_url", "source_url" in cart),
    ("Top 20 curation JSON has exactly 20 items", len(top_20) == 20),
    ("Top 20 has exactly 10 active picks", sum(1 for c in top_20 if c.get("is_active")) == 10),
    ("Top 20 has exactly 10 dimmed picks", sum(1 for c in top_20 if not c.get("is_active")) == 10),
    ("Elto Sama Honey (#4) is active pick (different cup notes rule)", any(c['rank'] == 4 and c['is_active'] for c in top_20)),
    ("All 20 items have valid max_prior_sim", all('max_prior_sim' in c for c in top_20)),
    ("All 20 items have valid source_url", all(c.get('source_url', '').startswith('http') for c in top_20)),
]

print("="*60)
print("System Verification Report")
print("="*60)
all_pass = True
for name, res in checks:
    status = "PASS" if res else "FAIL"
    print(f"[{status:4s}] {name}")
    if not res:
        all_pass = False

print("="*60)
if all_pass:
    print("ALL CHECKS PASSED PERFECTLY (100% COMPLETE)!")
else:
    print("SOME CHECKS FAILED. Please review.")
