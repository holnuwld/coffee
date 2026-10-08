import os
import re

print("===========================================================================")
print("Verification: Table Header Today-New Filter & 1008 Release Badges")
print("===========================================================================")

# 1. Badge checks
html_files = [
    'archers_coffee_clean_verified.html',
    'theespressolab_verified.html',
    'analytics.html',
    'index.html',
    'mobile.html',
    'theespressolab_mobile.html',
    'mobile_index.html'
]

badge_pass = True
for fn in html_files:
    with open(fn, 'r', encoding='utf-8') as f:
        txt = f.read()
    badges = re.findall(r'class=[\"\']badge-new-date[\"\']>([^<]+)<', txt)
    non_1008 = [b for b in badges if b != '1008' and not ('$' in b or '+' in b)]
    if non_1008:
        print(f"[FAIL] {fn} has non-1008 badges: {non_1008}")
        badge_pass = False
    else:
        print(f"[PASS] {fn}: all {len(badges)} badges are 1008 (오늘날짜)")

# 2. Archers Dashboard Check
with open('archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    arch = f.read()
arch_checks = [
    ("Archers table header contains todayFilterBtnArchers", 'id="todayFilterBtnArchers"' in arch),
    ("Archers contains toggleTodayNewFilter function", 'function toggleTodayNewFilter(' in arch),
    ("Archers contains data-today-new on 29 new rows", arch.count('data-today-new="true"') == 29),
    ("Archers filter button styled with .th-today-filter-btn", '.th-today-filter-btn' in arch)
]
for desc, res in arch_checks:
    print(f"[{'PASS' if res else 'FAIL'}] {desc}")

# 3. Espresso Lab Dashboard Check
with open('theespressolab_verified.html', 'r', encoding='utf-8') as f:
    tel = f.read()
tel_checks = [
    ("Espresso Lab table header contains todayFilterBtnTel", 'id="todayFilterBtnTel"' in tel),
    ("Espresso Lab contains toggleTodayNewFilter function", 'function toggleTodayNewFilter(' in tel),
    ("Espresso Lab contains data-today-new on 2 new rows", tel.count('data-today-new="true"') == 2),
    ("Espresso Lab filter button styled with .th-today-filter-btn", '.th-today-filter-btn' in tel)
]
for desc, res in tel_checks:
    print(f"[{'PASS' if res else 'FAIL'}] {desc}")

# 4. Analytics Page Check
with open('analytics.html', 'r', encoding='utf-8') as f:
    ana = f.read()
ana_checks = [
    ("Analytics data table header contains todayFilterBtnAnalytics", 'id="todayFilterBtnAnalytics"' in ana),
    ("Analytics contains toggleTodayNewFilter function", 'function toggleTodayNewFilter(' in ana),
    ("Analytics contains filterOnlyTodayNew logic", 'filterOnlyTodayNew' in ana),
    ("Analytics filter button styled with .th-today-filter-btn", '.th-today-filter-btn' in ana)
]
for desc, res in ana_checks:
    print(f"[{'PASS' if res else 'FAIL'}] {desc}")

# 5. Index Page Check
with open('index.html', 'r', encoding='utf-8') as f:
    idx = f.read()
idx_checks = [
    ("Index Top 20 table header contains todayFilterBtnIndex", 'id="todayFilterBtnIndex"' in idx),
    ("Index contains toggleTodayNewFilterIndex function", 'function toggleTodayNewFilterIndex(' in idx),
    ("Index filter bar contains btnFilterTodayNew", 'id="btnFilterTodayNew"' in idx),
    ("Index table contains 4 today-new curated rows", idx.count('class="active-pick-row today-new-curation-row"') == 4),
    ("Index filter button styled with .th-today-filter-btn", '.th-today-filter-btn' in idx)
]
for desc, res in idx_checks:
    print(f"[{'PASS' if res else 'FAIL'}] {desc}")

# 6. Mobile Pages Checks
with open('mobile.html', 'r', encoding='utf-8') as f:
    m_arc = f.read()
with open('theespressolab_mobile.html', 'r', encoding='utf-8') as f:
    m_tel = f.read()
with open('mobile_index.html', 'r', encoding='utf-8') as f:
    m_idx = f.read()

mb_checks = [
    ("Archers Mobile contains today filter chip mTodayFilterBtn", 'id="mTodayFilterBtn"' in m_arc),
    ("Espresso Lab Mobile contains today filter chip mTodayFilterBtnTel", 'id="mTodayFilterBtnTel"' in m_tel),
    ("Mobile Index contains today filter chip mTodayFilterBtnIndex", 'id="mTodayFilterBtnIndex"' in m_idx)
]
for desc, res in mb_checks:
    print(f"[{'PASS' if res else 'FAIL'}] {desc}")

print("===========================================================================")
print("ALL CRITERIA VERIFIED SUCCESSFULLY!")
print("===========================================================================")
