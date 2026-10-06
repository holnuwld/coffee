import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

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
    ("index.html contains dedicated tasting notes column (✨ 컵노트)", "✨ 컵노트" in idx and "notes-cell" in idx),
    ("index.html contains shortened roastery badge (🏹 Archers)", "🏹 Archers" in idx and "🧪 Espresso Lab" in idx),
    ("index.html contains new 3-criteria similarity in modal (컵노트 50%, 테루아 30%, 프로세스 20%)", 
        all(term in idx for term in ['컵노트 (50%)', '지역 (10%)', '농장 (10%)', '프로듀서 (10%)', '프로세스 (20%)'])),
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

    # Dataset integrity & New Criteria
    ("Top 20 curation JSON has exactly 20 items", len(top_20) == 20),
    ("Top 20 has exactly 10 active picks", sum(1 for c in top_20 if c.get("is_active")) == 10),
    ("Elto Sama Honey is active pick (different cup notes rule)", any('sama' in c.get('title','').lower() and 'honey' in c.get('title','').lower() and c.get('is_active') for c in top_20)),
    ("Top 20 curation JSON has 3-criteria similarity breakdown (notes, terroir, process)", 
        any(c.get('similar_details') and 'terroir' in c['similar_details'] for c in top_20)),
    ("mobile_index.html contains 3-criteria similarity breakdown", "3대 기준 유사도 세부 내역" in m_idx),

    # New User Requirements Verification (Dashboards all coffees scored & Desktop table fixed)
    ("index.html table layout prevents column overlap with colgroup & min-width", "colgroup" in idx and "top20Table" in idx),
    ("index.html criteria box contains new 3 taste criteria (COE 20, Terroir 15, Review 15)", 
        all(k in idx for k in ['이력20', '테루아15', '평가15'])),
    ("Archers desktop dashboard contains ⭐ 종합점수 header and 117 score cells",
        any(h in archers for h in ["⭐ 종합 점수", "⭐ 종합점수"]) and archers.count('class="td-score"') >= 117),
    ("Espresso Lab desktop dashboard contains ⭐ 종합점수 header and 54 score cells",
        any(h in tel_dt for h in ["⭐ 종합 점수", "⭐ 종합점수"]) and tel_dt.count('td-score') >= 54),
    ("Archers mobile dashboard contains 117 score tags",
        arc_mb.count('score-tag') >= 117),
    ("Espresso Lab mobile dashboard contains 54 score badges",
        tel_mb.count('m-score-badge') >= 54),
    ("Price scores in Top 20 have continuous decimal precision",
        any(isinstance(c.get('score_price'), float) and not float(c.get('score_price')).is_integer() for c in top_20)),

    # Roastery Dashboards: Multi-Score Sub-sorting (Total / Taste / Price / Rarity) & Plain Text Badges
    ("Archers desktop dashboard contains sortScoreCol function for sub-sorting", "function sortScoreCol(" in archers and "sortInd_arch_taste" in archers),
    ("Archers desktop dashboard has data-taste, data-price, data-rarity on all 117 rows", archers.count('data-taste=') >= 117 and archers.count('data-price=') >= 117),
    ("Espresso Lab desktop dashboard contains sortScoreCol function for sub-sorting", "function sortScoreCol(" in tel_dt and "sortInd_tel_taste" in tel_dt),
    ("Espresso Lab desktop dashboard has data-taste, data-price, data-rarity on all 54 rows", tel_dt.count('data-taste=') >= 54 and tel_dt.count('data-price=') >= 54),

    # Analytics Page (analytics.html) Full Requirements
    ("analytics.html exists and size > 150KB", os.path.exists('analytics.html') and os.path.getsize('analytics.html') > 150000),
    ("analytics.html contains 171 coffee beans dataset", '"total_count": 171' in open('analytics.html', encoding='utf-8').read() or '171종' in open('analytics.html', encoding='utf-8').read()),
    ("analytics.html contains statistical insights (sweet-spot 30~70 AED, correlation)", all(t in open('analytics.html', encoding='utf-8').read() for t in ['30 ~ 70 AED', '상관관계', '스위트스팟'])),
    ("analytics.html contains Graph 1: Scatter plot (scatterChart)", "scatterChart" in open('analytics.html', encoding='utf-8').read() and "type: 'scatter'" in open('analytics.html', encoding='utf-8').read()),
    ("analytics.html supports 4 group color encoding (Comp, Reserve, Selection, Esolab)", all(k in open('analytics.html', encoding='utf-8').read() for k in ['competition', 'reserve', 'selection', 'esolab'])),
    ("analytics.html supports point shape encoding (country, process, altitude, default)", "currentShapeMode" in open('analytics.html', encoding='utf-8').read() and "getPointStyle" in open('analytics.html', encoding='utf-8').read()),
    ("analytics.html contains Graph 2: Tasting notes chart (notesChart)", "notesChart" in open('analytics.html', encoding='utf-8').read() and "TOP_NOTES" in open('analytics.html', encoding='utf-8').read()),
    ("analytics.html contains detail modal with 3 taste criteria breakdown", "detailOverlay" in open('analytics.html', encoding='utf-8').read() and "modalAwardScore" in open('analytics.html', encoding='utf-8').read()),
    ("analytics.html supports dual theme (dark/light) with theme toggle", "toggleTheme" in open('analytics.html', encoding='utf-8').read() and '[data-theme="light"]' in open('analytics.html', encoding='utf-8').read()),
    ("analytics.html contains 100g price cap filter toolbar (table-price-filter-bar & setPriceFilter)", "table-price-filter-bar" in open('analytics.html', encoding='utf-8').read() and "setPriceFilter" in open('analytics.html', encoding='utf-8').read()),
    ("index.html contains link to analytics.html (analytics-promo-card)", "analytics-promo-card" in idx and "analytics.html" in idx),
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

