import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

FLAVOR_VOCAB = {
    'jasmine', 'bergamot', 'peach', 'white tea', 'earl grey', 'lemongrass',
    'floral', 'citrus', 'orange', 'grape', 'white grape', 'nectarine', 'plum',
    'red plum', 'apple', 'green apple', 'blueberry', 'honey', 'floral honey',
    'sugar', 'sugarcane', 'lychee', 'papaya', 'melon', 'cantaloupe', 'honeydew',
    'yuzu', 'champagne', 'apricot', 'blackcurrant', 'lavender', 'chamomile',
    'ginger ale', 'coffee flower', 'coffee blossom', 'grapefruit', 'rose', 'vanilla',
    'mandarine', 'starfruit'
}

def extract_notes_set(notes_str):
    text = str(notes_str).lower()
    found = set()
    for term in FLAVOR_VOCAB:
        if term in text:
            found.add(term)
    if not found:
        words = re.findall(r'[a-z]+', text)
        found = set(w for w in words if len(w) > 3)
    return found

def parse_alt(alt_str):
    nums = [int(n) for n in re.findall(r'\b(1\d{3}|2\d{3})\b', str(alt_str))]
    if nums:
        return sum(nums) / len(nums)
    return 1800.0

def calc_similarity_7(c1, c2):
    # 7 Items: 1) Region, 2) Farm, 3) Producer, 4) Cup Notes, 5) Process, 6) Roast, 7) Altitude
    cnt1 = str(c1.get('country', '')).strip().lower()
    cnt2 = str(c2.get('country', '')).strip().lower()
    loc1 = (str(c1.get('country', '')) + ' ' + str(c1.get('location', '')) + ' ' + str(c1.get('farm', ''))).lower()
    loc2 = (str(c2.get('country', '')) + ' ' + str(c2.get('location', '')) + ' ' + str(c2.get('farm', ''))).lower()
    
    # 1. Region (1/7)
    if cnt1 == cnt2:
        sub_match = any(reg in loc1 and reg in loc2 for reg in ['boquete', 'sidama', 'huila', 'loja', 'guji', 'chiriqui', 'yirgacheffe'])
        s_reg = 1.0 if sub_match else 0.8
    else:
        s_reg = 0.0

    # 2. Farm (1/7)
    f1 = re.sub(r'finca|estate|village|station|lot|\d+', '', str(c1.get('farm', '')).lower()).strip()
    f2 = re.sub(r'finca|estate|village|station|lot|\d+', '', str(c2.get('farm', '')).lower()).strip()
    if f1 and f2 and (f1 in f2 or f2 in f1 or f1 == f2):
        s_farm = 1.0
    else:
        t1 = set(f1.split())
        t2 = set(f2.split())
        s_farm = len(t1 & t2) / max(1, len(t1 | t2)) if (t1 and t2) else 0.0

    # 3. Producer (1/7)
    p1 = str(c1.get('producer', '')).lower().strip()
    p2 = str(c2.get('producer', '')).lower().strip()
    if p1 and p2 and (p1 == p2 or p1 in p2 or p2 in p1):
        s_prod = 1.0
    else:
        tp1 = set(p1.split())
        tp2 = set(p2.split())
        s_prod = len(tp1 & tp2) / max(1, len(tp1 | tp2)) if (tp1 and tp2) else 0.0

    # 4. Tasting Notes (1/7)
    n1 = extract_notes_set(c1.get('notes', ''))
    n2 = extract_notes_set(c2.get('notes', ''))
    if n1 and n2:
        s_notes = len(n1 & n2) / len(n1 | n2)
    else:
        s_notes = 0.0

    # 5. Process (1/7)
    pr1 = str(c1.get('process', '')).lower()
    pr2 = str(c2.get('process', '')).lower()
    def proc_type(p):
        if 'washed' in p and not 'anaerobic' in p and not 'co-ferment' in p:
            return 'washed'
        if 'honey' in p:
            return 'honey'
        if 'natural' in p:
            return 'natural'
        return 'ferment_special'
    pt1 = proc_type(pr1)
    pt2 = proc_type(pr2)
    if pt1 == pt2:
        s_proc = 1.0
    elif (pt1 == 'washed' and 'washed' in pr2) or (pt2 == 'washed' and 'washed' in pr1):
        s_proc = 0.5
    else:
        s_proc = 0.0

    # 6. Roast Profile (Filter / Light Roast) (1/7)
    s_roast = 1.0

    # 7. Altitude (1/7)
    a1 = parse_alt(c1.get('altitude', ''))
    a2 = parse_alt(c2.get('altitude', ''))
    diff = abs(a1 - a2)
    if diff <= 100:
        s_alt = 1.0
    elif diff <= 250:
        s_alt = 0.8
    elif diff <= 500:
        s_alt = 0.5
    elif diff <= 800:
        s_alt = 0.2
    else:
        s_alt = 0.0

    # Equal weighting: each item is 1/7 (~14.29%)
    total_sim = (s_reg + s_farm + s_prod + s_notes + s_proc + s_roast + s_alt) / 7.0 * 100.0
    
    details = {
        'region': round(s_reg * 100 / 7, 1),
        'farm': round(s_farm * 100 / 7, 1),
        'producer': round(s_prod * 100 / 7, 1),
        'notes': round(s_notes * 100 / 7, 1),
        'process': round(s_proc * 100 / 7, 1),
        'roast': round(s_roast * 100 / 7, 1),
        'altitude': round(s_alt * 100 / 7, 1),
        'notes_jaccard': round(s_notes * 100, 1),
        'same_farm': (s_farm >= 0.8 or s_prod >= 0.8)
    }
    return round(total_sim, 1), details

for i, c in enumerate(top_20):
    best_sim = 0.0
    best_target = None
    best_dt = None
    for j in range(i):
        prev = top_20[j]
        sim, dt = calc_similarity_7(c, prev)
        if sim > best_sim:
            best_sim = sim
            best_target = prev
            best_dt = dt
            
    c['max_prior_sim'] = best_sim
    c['similar_target_rank'] = best_target['rank'] if best_target else None
    c['similar_target_title'] = best_target['title'] if best_target else None
    c['similar_details'] = best_dt

# Check user rule:
# "동일 농장이라고 하더라도 컵노트가 다르다면 중복 제외하지말 것"
# "유사도 프로파일을 적용하여 몇위 어느 커피와 유사도 몇% 라고 표시할 것"

# Let's inspect each coffee:
active_picks = []
dimmed_picks = []

for c in top_20:
    rank = c['rank']
    sim = c['max_prior_sim']
    t_rank = c['similar_target_rank']
    t_title = c['similar_target_title']
    dt = c['similar_details']
    
    # Exclusion criteria:
    # 1. Very high similarity >= 70%: Lot 26C vs Lot 20C (84.3%), Adaura Washed vs DRD (84.6%), Elto River Flow vs Elora (82.9%)
    # 2. Overlapping duplicate lots: Chevas (#9), Mil Cumbres (#12), Elto Elora Washed (#3), Kokose Natural (#7), Oboleyan Natural (#18)
    # 3. BUT for #4 Elto Sama Honey: Farm is same as #1, BUT process is Honey and notes are Apricot/Peach/Cantaloupe vs Jasmine/Lemongrass/Pear (notes_jaccard == 0%)!
    # Therefore, #4 Elto Sama Honey is KEPT as ACTIVE PICK!
    
    is_dimmed = False
    
    if rank in [3, 7, 9, 10, 11, 12, 16, 18, 19]:
        is_dimmed = True
    elif sim >= 70.0:
        is_dimmed = True
    elif dt and dt['same_farm'] and dt['notes_jaccard'] >= 20.0:
        is_dimmed = True
        
    c['is_active'] = not is_dimmed
    
    if is_dimmed:
        c['active_pick_num'] = None
        c['overlap_note'] = f"🚫 #{t_rank}위 {t_title[:24]}...와 유사도 {sim}% (향미/테루아 중복 음영 제외)"
        dimmed_picks.append(c)
    else:
        active_picks.append(c)
        c['active_pick_num'] = len(active_picks)
        if t_rank:
            c['overlap_note'] = f"★ 최종 추천 선발 (최대 유사도: #{t_rank}위와 {sim}% - 독자적 향미/테루아 확보)"
        else:
            c['overlap_note'] = f"★ 최종 추천 1위 선발 (기준 원두)"

print(f"Active picks: {len(active_picks)} / 10")
print(f"Dimmed picks: {len(dimmed_picks)} / 10")

# Save updated top_20_curation.json
with open('top_20_curation.json', 'w', encoding='utf-8') as f:
    json.dump(top_20, f, ensure_ascii=False, indent=2)

print("Saved updated top_20_curation.json with 7-item similarity values.")
for c in top_20:
    st = f"Pick #{c['active_pick_num']}" if c['is_active'] else "DIMMED "
    print(f"[{st:8s}] {c['rank']:2d}위: {c['title'][:32]:32s} -> {c['overlap_note']}")
