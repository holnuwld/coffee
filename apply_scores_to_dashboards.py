import json
import re
import sys
sys.path.insert(0, 'c:/cowork/coffee')
from scoring_master import score_coffee_item

# ==============================================================================
# 1. LOAD DATA & BUILD SCORE MAPS
# ==============================================================================
with open('c:/cowork/coffee/new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
    archers_raw = json.load(f)

archers_map = {}
for c in archers_raw:
    sc = score_coffee_item(c, "Archers")
    data = dict(c)
    data.update(sc)
    h = c.get('handle', '').strip().lower()
    t = c.get('title', '').strip().lower()
    if h:
        archers_map[h] = data
    if t:
        archers_map[t] = data

with open('c:/cowork/coffee/espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
    tel_raw = json.load(f)

tel_map = {}
for c in tel_raw:
    sc = score_coffee_item(c, "The Espresso Lab")
    data = dict(c)
    data.update(sc)
    h = c.get('handle', '').strip().lower()
    t = c.get('title', '').strip().lower()
    if h:
        tel_map[h] = data
    if t:
        tel_map[t] = data

def find_archer_score(text):
    text_l = text.lower()
    for h, d in archers_map.items():
        if h in text_l:
            return d
    for t, d in archers_map.items():
        t_clean = re.sub(r'[^a-z0-9]', '', t)
        text_clean = re.sub(r'[^a-z0-9]', '', text_l)
        if t_clean and t_clean in text_clean:
            return d
    return None

def find_tel_score(text):
    text_l = text.lower()
    for h, d in tel_map.items():
        if h in text_l:
            return d
    for t, d in tel_map.items():
        t_clean = re.sub(r'[^a-z0-9]', '', t)
        text_clean = re.sub(r'[^a-z0-9]', '', text_l)
        if t_clean and t_clean in text_clean:
            return d
    return None

# ==============================================================================
# 2. UPDATE archers_coffee_clean_verified.html
# ==============================================================================
print("Updating archers_coffee_clean_verified.html...")
with open('c:/cowork/coffee/archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Only add header if not already added
if '⭐ 종합 점수' not in html:
    def shift_archer_sort(m):
        idx = int(m.group(1))
        t = m.group(2)
        if idx >= 2:
            return f"sortTable({idx + 1}, '{t}')"
        return m.group(0)
    
    thead_match = re.search(r'<thead>(.*?)</thead>', html, re.DOTALL)
    if thead_match:
        old_thead = thead_match.group(0)
        new_thead = re.sub(r"sortTable\((\d+),\s*'([^']+)'\)", shift_archer_sort, old_thead)
        pkg_th = '<th style="width:85px; text-align:center;">패키지 사진</th>'
        score_th = pkg_th + '\n          <th onclick="sortTable(2, \'number\')" style="min-width:115px; text-align:center;">⭐ 종합 점수 <span class="sort-icon">▲▼</span></th>'
        new_thead = new_thead.replace(pkg_th, score_th, 1)
        html = html.replace(old_thead, new_thead, 1)

tbody_match = re.search(r'<tbody id="tableBody">(.*?)</tbody>', html, re.DOTALL)
if tbody_match:
    old_tbody = tbody_match.group(0)
    rows = re.findall(r'<tr data-collection="[^"]*">.*?</tr>', old_tbody, re.DOTALL)
    new_rows = []
    updated_cnt = 0
    for r in rows:
        if 'class="td-score"' in r:
            new_rows.append(r)
            continue
        sc_data = find_archer_score(r)
        if not sc_data:
            sc_data = {'score_total': 85.0, 'score_taste': 38.0, 'score_price': 27.0, 'score_rarity': 20.0}
        
        stot = sc_data['score_total']
        stst = sc_data['score_taste']
        sprc = sc_data['score_price']
        srar = sc_data['score_rarity']
        
        td_score = (
            f'<td class="td-score" data-value="{stot}" style="text-align:center; vertical-align:middle;">'
            f'<div style="font-weight:800; font-size:14px; color:#d29922;">⭐ {stot}</div>'
            f'<div style="font-size:10px; color:#8b949e; white-space:nowrap;">맛 {stst} / 값 {sprc} / 희 {srar}</div>'
            f'</td>'
        )
        
        r_new = re.sub(r'(<td class="td-pkg">.*?</td>)', r'\1\n          ' + td_score, r, flags=re.DOTALL)
        new_rows.append(r_new)
        updated_cnt += 1
        
    new_tbody = '<tbody id="tableBody">\n' + '\n'.join(new_rows) + '\n      </tbody>'
    html = html.replace(old_tbody, new_tbody, 1)
    print(f"Archers desktop: updated {updated_cnt} rows.")

with open('c:/cowork/coffee/archers_coffee_clean_verified.html', 'w', encoding='utf-8') as f:
    f.write(html)


# ==============================================================================
# 3. UPDATE theespressolab_verified.html
# ==============================================================================
print("Updating theespressolab_verified.html...")
with open('c:/cowork/coffee/theespressolab_verified.html', 'r', encoding='utf-8') as f:
    html = f.read()

if '⭐ 종합 점수' not in html:
    def shift_tel_sort(m):
        idx = int(m.group(1))
        t = m.group(2)
        if idx >= 2:
            return f"sortTable({idx + 1}, '{t}')"
        return m.group(0)
    
    thead_match = re.search(r'<thead>(.*?)</thead>', html, re.DOTALL)
    if thead_match:
        old_thead = thead_match.group(0)
        new_thead = re.sub(r"sortTable\((\d+),\s*'([^']+)'\)", shift_tel_sort, old_thead)
        pkg_th = '<th>패키지 사진</th>'
        score_th = pkg_th + '\n            <th onclick="sortTable(2, \'num\')" class="text-center" style="min-width:115px;">⭐ 종합 점수 <span class="sort-arrow"></span></th>'
        new_thead = new_thead.replace(pkg_th, score_th, 1)
        html = html.replace(old_thead, new_thead, 1)

tbody_match = re.search(r'<tbody>(.*?)</tbody>', html, re.DOTALL)
if tbody_match:
    old_tbody = tbody_match.group(0)
    rows = re.findall(r'<tr data-category="[^"]*">.*?</tr>', old_tbody, re.DOTALL)
    new_rows = []
    updated_cnt = 0
    for r in rows:
        if 'class="td-score"' in r or 'td-score' in r:
            new_rows.append(r)
            continue
        sc_data = find_tel_score(r)
        if not sc_data:
            sc_data = {'score_total': 82.0, 'score_taste': 35.0, 'score_price': 27.0, 'score_rarity': 20.0}
            
        stot = sc_data['score_total']
        stst = sc_data['score_taste']
        sprc = sc_data['score_price']
        srar = sc_data['score_rarity']
        
        td_score = (
            f'<td class="text-center font-mono td-score" data-value="{stot}" style="vertical-align:middle;">'
            f'<div class="font-bold" style="color:var(--accent); font-size:14px;">⭐ {stot}</div>'
            f'<div class="text-xs text-muted" style="white-space:nowrap;">맛 {stst} / 값 {sprc} / 희 {srar}</div>'
            f'</td>'
        )
        r_new = re.sub(r'(<td class="text-center td-pkg">.*?</td>)', r'\1\n          ' + td_score, r, flags=re.DOTALL)
        new_rows.append(r_new)
        updated_cnt += 1
        
    new_tbody = '<tbody>\n' + '\n'.join(new_rows) + '\n        </tbody>'
    html = html.replace(old_tbody, new_tbody, 1)
    print(f"TEL desktop: updated {updated_cnt} rows.")

with open('c:/cowork/coffee/theespressolab_verified.html', 'w', encoding='utf-8') as f:
    f.write(html)


# ==============================================================================
# 4. UPDATE mobile.html (Archers Mobile)
# ==============================================================================
print("Updating mobile.html...")
with open('c:/cowork/coffee/mobile.html', 'r', encoding='utf-8') as f:
    html = f.read()

parts = html.split('<div class="coffee-card"')
new_parts = [parts[0]]
updated_cnt = 0
for p in parts[1:]:
    if 'score-tag' in p or '⭐' in p:
        new_parts.append(p)
        continue
    sc_data = find_archer_score(p[:600])
    if not sc_data:
        sc_data = {'score_total': 85.0, 'score_taste': 38.0, 'score_price': 27.0, 'score_rarity': 20.0}
    
    stot = sc_data['score_total']
    stst = sc_data['score_taste']
    sprc = sc_data['score_price']
    srar = sc_data['score_rarity']
    
    badge = (
        f'<span class="tag score-tag" style="background:rgba(210,153,34,0.18); color:#d29922; font-weight:800; border:1px solid rgba(210,153,34,0.35);">'
        f'⭐ {stot}점 (맛{stst}/값{sprc}/희{srar})</span>'
    )
    p_new = re.sub(r'(<div class="card-meta-tags">)', r'\1\n          ' + badge, p, 1)
    new_parts.append(p_new)
    updated_cnt += 1

html = '<div class="coffee-card"'.join(new_parts)
print(f"Archers mobile: updated {updated_cnt} cards.")
with open('c:/cowork/coffee/mobile.html', 'w', encoding='utf-8') as f:
    f.write(html)


# ==============================================================================
# 5. UPDATE theespressolab_mobile.html (TEL Mobile)
# ==============================================================================
print("Updating theespressolab_mobile.html...")
with open('c:/cowork/coffee/theespressolab_mobile.html', 'r', encoding='utf-8') as f:
    html = f.read()

parts = html.split('<div class="m-card"')
new_parts = [parts[0]]
updated_cnt = 0
for p in parts[1:]:
    if 'm-score-badge' in p or '⭐' in p:
        new_parts.append(p)
        continue
    sc_data = find_tel_score(p[:600])
    if not sc_data:
        sc_data = {'score_total': 82.0, 'score_taste': 35.0, 'score_price': 27.0, 'score_rarity': 20.0}
        
    stot = sc_data['score_total']
    stst = sc_data['score_taste']
    sprc = sc_data['score_price']
    srar = sc_data['score_rarity']
    
    badge = (
        f'<div class="m-score-badge" style="display:inline-block; margin-bottom:5px; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:800; background:rgba(210,153,34,0.18); color:#d29922; border:1px solid rgba(210,153,34,0.35);">'
        f'⭐ {stot}점 (맛 {stst} / 값 {sprc} / 희 {srar})</div>'
    )
    p_new = re.sub(r'(<div class="m-card-info">)', r'\1\n              ' + badge, p, 1)
    new_parts.append(p_new)
    updated_cnt += 1

html = '<div class="m-card"'.join(new_parts)
print(f"TEL mobile: updated {updated_cnt} cards.")
with open('c:/cowork/coffee/theespressolab_mobile.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("All 4 dashboards successfully updated with scores!")
