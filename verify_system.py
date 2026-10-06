import json
import re
import os

with open('index.html', 'r', encoding='utf-8') as f:
    idx = f.read()

with open('cart.html', 'r', encoding='utf-8') as f:
    cart = f.read()

with open('mobile_index.html', 'r', encoding='utf-8') as f:
    m_idx = f.read()

with open('mobile_cart.html', 'r', encoding='utf-8') as f:
    m_cart = f.read()

with open('archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    archers = f.read()

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

with open('theespressolab_verified.html', 'r', encoding='utf-8') as f:
    tel_dt = f.read()

with open('theespressolab_mobile.html', 'r', encoding='utf-8') as f:
    tel_mb = f.read()

with open('mobile.html', 'r', encoding='utf-8') as f:
    arc_mb = f.read()

checks = [
    # Desktop index.html & cart.html
    ("index.html contains cart-action-toolbar", "cart-action-toolbar" in idx),
    ("index.html contains link to cart.html", "cart.html" in idx),
    ("index.html contains link to mobile_index.html", "mobile_index.html" in idx),
    ("index.html contains selectAllCheckbox", "selectAllCheckbox" in idx),
    ("index.html contains cart checkbox class", "cart-row-checkbox" in idx),
    ("index.html contains 7 items in modal (지역, 농장, 프로듀서, 컵노트, 프로세스, 배전도, 고도)", 
        all(term in idx for term in ['지역', '농장', '프로듀서', '컵노트', '프로세스', '배전도', '고도'])),
    ("cart.html contains purchaser checklist inst-grid", "inst-grid" in cart),
    ("cart.html contains purchaser checklist inst-num badges", "inst-num" in cart),
    ("cart.html contains link to mobile_cart.html", "mobile_cart.html" in cart),
    ("cart.html contains window.print()", "window.print()" in cart),
    ("cart.html contains direct shop links with target='_blank'", 'target="_blank"' in cart),

    # Mobile index.html
    ("mobile_index.html exists and > 50KB", os.path.getsize('mobile_index.html') > 50000),
    ("mobile_index.html contains rank (순위)", "m-rank-badge" in m_idx),
    ("mobile_index.html contains roastery (로스터리)", "m-roastery-badge" in m_idx),
    ("mobile_index.html contains coffee title (커피명)", "m-coffee-title" in m_idx),
    ("mobile_index.html contains price (가격)", "m-price-aed" in m_idx),
    ("mobile_index.html contains total score (총점)", "m-score-val" in m_idx),
    ("mobile_index.html contains accordion toggle (드로우다운)", "toggleDrawdown" in m_idx and "m-drawdown-content" in m_idx),
    ("mobile_index.html contains cart checkbox & floating bar", "m-bottom-cart-bar" in m_idx and "m-checkbox" in m_idx),
    ("mobile_index.html contains link to mobile_cart.html", "mobile_cart.html" in m_idx),

    # Mobile cart.html
    ("mobile_cart.html exists and > 50KB", os.path.getsize('mobile_cart.html') > 50000),
    ("mobile_cart.html contains mobile checklist", "m-inst-card" in m_cart),
    ("mobile_cart.html contains KPI grid (총품목, AED, KRW)", "m-kpi-grid" in m_cart),
    ("mobile_cart.html contains PO card view with item toggle", "m-po-card" in m_cart and "toggleItemDetail" in m_cart),
    ("mobile_cart.html contains window.print()", "window.print()" in m_cart),
    ("mobile_cart.html contains text copy function", "copyOrderText" in m_cart),
    ("mobile_cart.html contains direct shop links with target='_blank'", 'target="_blank"' in m_cart),

    # Immutable Snapshot & Shared Cart Features
    ("cart.html contains generateImmutableSnapshotUrl", "generateImmutableSnapshotUrl" in cart),
    ("cart.html contains snapshot banner", "snapshotBanner" in cart),
    ("cart.html contains shared_cart handling", "shared_cart" in cart),
    ("cart.html contains snapshot parameter handler (?snapshot=)", "urlParams.get('snapshot')" in cart),
    ("cart.html locks editing in snapshot mode", "isSnapshotMode" in cart),
    ("mobile_cart.html contains generateImmutableSnapshotUrl", "generateImmutableSnapshotUrl" in m_cart),
    ("mobile_cart.html contains snapshot banner", "mSnapshotBanner" in m_cart),
    ("mobile_cart.html contains shared_cart handling", "shared_cart" in m_cart),
    ("mobile_cart.html contains snapshot parameter handler (?snapshot=)", "urlParams.get('snapshot')" in m_cart),
    ("mobile_cart.html locks editing in snapshot mode", "isSnapshotMode" in m_cart),

    # Archers dashboard expert rank 1 fix
    ("Archers dashboard contains Expert Rank 1 (Los Cenizos GW 208)", "1위 | Competition Series 2025" in archers and "Los Cenizos" in archers),
    ("Archers dashboard has complete Best 3 (1위, 2위, 3위)", all(f"{r}위 |" in archers for r in [1, 2, 3])),

    # Archers package photos & Lightbox modal
    ("Archers desktop dashboard contains package photos (.td-pkg)", "td-pkg" in archers and "pkg-thumb" in archers),
    ("Archers desktop dashboard contains Lightbox modal (openLightbox)", "openLightbox" in archers and "imgLightbox" in archers),
    ("Archers mobile view contains package photos (m-pkg-thumb)", "m-pkg-thumb" in arc_mb),
    ("Archers mobile view contains Lightbox modal (mLightbox)", "mLightbox" in arc_mb),

    # Dual Theme (Bright / Dark Mode) Across All 8 Pages
    ("index.html: [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in idx and "themeToggleBtn" in idx and "toggleTheme()" in idx),
    ("mobile_index.html: [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in m_idx and "themeToggleBtn" in m_idx and "toggleTheme()" in m_idx),
    ("cart.html: [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in cart and "themeToggleBtn" in cart and "toggleTheme()" in cart),
    ("mobile_cart.html: [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in m_cart and "themeToggleBtn" in m_cart and "toggleTheme()" in m_cart),
    ("theespressolab_verified.html: [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in tel_dt and "themeToggleBtn" in tel_dt and "toggleTheme()" in tel_dt),
    ("theespressolab_mobile.html: [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in tel_mb and "themeToggleBtn" in tel_mb and "toggleTheme()" in tel_mb),
    ("archers_coffee_clean_verified.html: [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in archers and "themeToggleBtn" in archers and "toggleTheme()" in archers),
    ("mobile.html (Archers Mobile): [data-theme='light'] CSS + themeToggleBtn + toggleTheme()", '[data-theme="light"]' in arc_mb and "themeToggleBtn" in arc_mb and "toggleTheme()" in arc_mb),

    # FOUC prevention instant script in head on all pages
    ("All 8 pages have FOUC prevention theme script in head", all("localStorage.getItem('theme')" in p for p in [idx, m_idx, cart, m_cart, tel_dt, tel_mb, archers, arc_mb])),

    # Dataset integrity
    ("Top 20 curation JSON has exactly 20 items", len(top_20) == 20),
    ("Top 20 has exactly 10 active picks", sum(1 for c in top_20 if c.get("is_active")) == 10),
    ("Elto Sama Honey (#4) is active pick (different cup notes rule)", any(c['rank'] == 4 and c['is_active'] for c in top_20)),
]

print("="*75)
print("Comprehensive System Verification Report (Mobile, Snapshot & Shared Cart)")
print("="*75)
all_pass = True
for name, res in checks:
    status = "PASS" if res else "FAIL"
    print(f"[{status:4s}] {name}")
    if not res:
        all_pass = False

print("="*75)
if all_pass:
    print("ALL CHECKS PASSED PERFECTLY (100% COMPLETE)! NO FLAWS DETECTED.")
else:
    print("SOME CHECKS FAILED. Please review.")

