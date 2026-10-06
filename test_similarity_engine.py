import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

# Extract flavor tokens
FLAVOR_VOCAB = {
    'jasmine', 'bergamot', 'peach', 'white tea', 'earl grey', 'lemongrass',
    'floral', 'citrus', 'orange', 'grape', 'white grape', 'nectarine', 'plum',
    'red plum', 'apple', 'green apple', 'blueberry', 'honey', 'floral honey',
    'sugar', 'sugarcane', 'lychee', 'papaya', 'melon', 'cantaloupe', 'honeydew',
    'yuzu', 'champagne', 'apricot', 'blackcurrant', 'lavender', 'chamomile',
    'ginger ale', 'coffee flower', 'coffee blossom', 'grapefruit', 'rose', 'vanilla'
}

def extract_notes_set(notes_str):
    text = notes_str.lower()
    found = set()
    for term in FLAVOR_VOCAB:
        if term in text:
            found.add(term)
    # fallback to single words
    if not found:
        words = re.findall(r'[a-z]+', text)
        found = set(w for w in words if len(w) > 3)
    return found

def parse_alt(alt_str):
    nums = [int(n) for n in re.findall(r'\b(1\d{3}|2\d{3})\b', str(alt_str))]
    if nums:
        return sum(nums) / len(nums)
    return 1800.0 # default fallback

def calc_similarity_7(c1, c2):
    # 1. Region (1/7 = ~14.28%)
    cnt1 = c1.get('country', '').strip().lower()
    cnt2 = c2.get('country', '').strip().lower()
    loc1 = (c1.get('country', '') + ' ' + c1.get('location', '') + ' ' + c1.get('farm', '')).lower()
    loc2 = (c2.get('country', '') + ' ' + c2.get('location', '') + ' ' + c2.get('farm', '')).lower()
    
    if cnt1 == cnt2:
        # Check sub-region
        sub_match = any(reg in loc1 and reg in loc2 for reg in ['boquete', 'sidama', 'huila', 'loja', 'guji', 'chiriqui', 'yirgacheffe'])
        s_reg = 1.0 if sub_match else 0.8
    else:
        s_reg = 0.0

    # 2. Farm (1/7)
    f1 = re.sub(r'finca|estate|village|station|lot|\d+', '', c1.get('farm', '').lower()).strip()
    f2 = re.sub(r'finca|estate|village|station|lot|\d+', '', c2.get('farm', '').lower()).strip()
    if f1 and f2 and (f1 in f2 or f2 in f1 or f1 == f2):
        s_farm = 1.0
    else:
        # check token overlap
        t1 = set(f1.split())
        t2 = set(f2.split())
        s_farm = len(t1 & t2) / max(1, len(t1 | t2)) if (t1 and t2) else 0.0

    # 3. Producer (1/7)
    p1 = c1.get('producer', '').lower().strip()
    p2 = c2.get('producer', '').lower().strip()
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
    pr1 = c1.get('process', '').lower()
    pr2 = c2.get('process', '').lower()
    
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

    # 6. Roast (1/7)
    # Both are filter / light roast
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

    # 7 Items Equally Weighted (100% / 7 = 14.2857% each)
    total_sim = (s_reg + s_farm + s_prod + s_notes + s_proc + s_roast + s_alt) / 7.0 * 100.0
    
    breakdown = {
        'region': round(s_reg * 100 / 7, 1),
        'farm': round(s_farm * 100 / 7, 1),
        'producer': round(s_prod * 100 / 7, 1),
        'notes': round(s_notes * 100 / 7, 1),
        'process': round(s_proc * 100 / 7, 1),
        'roast': round(s_roast * 100 / 7, 1),
        'altitude': round(s_alt * 100 / 7, 1),
        'raw_notes_jaccard': round(s_notes * 100, 1),
        'same_farm': (s_farm >= 0.8 or s_prod >= 0.8)
    }
    return round(total_sim, 1), breakdown

print("Calculating pairwise similarities for all 20 coffees...")
for i, c in enumerate(top_20):
    best_sim = 0.0
    best_target = None
    best_bd = None
    for j in range(i):
        prev = top_20[j]
        sim, bd = calc_similarity_7(c, prev)
        if sim > best_sim:
            best_sim = sim
            best_target = prev
            best_bd = bd
    c['max_prior_sim'] = best_sim
    c['most_similar_prev'] = best_target['title'] if best_target else None
    c['most_similar_prev_rank'] = best_target['rank'] if best_target else None
    c['sim_breakdown'] = best_bd
    print(f"Rank {c['rank']:2d} [{c['title'][:32]:32s}] -> Max prior sim: {best_sim:4.1f}% with #{c['most_similar_prev_rank']} ({str(c['most_similar_prev'])[:25]}) | Same farm: {best_bd.get('same_farm') if best_bd else False} | Notes Jaccard: {best_bd.get('raw_notes_jaccard', 0) if best_bd else 0}%")
