import json
import re
import sys
from scoring_master import score_coffee_item

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/cowork/coffee/new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
    archers = json.load(f)

with open('c:/cowork/coffee/espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
    tel = json.load(f)

# Load existing curation for detailed reviews if available
existing_reviews = {}
try:
    with open('top_20_curation.json', encoding='utf-8') as f:
        old_cur = json.load(f)
        for c in old_cur:
            if c.get('handle'):
                existing_reviews[c['handle']] = c.get('detailed_review')
except Exception as e:
    pass

FLAVOR_VOCAB = {
    'jasmine', 'bergamot', 'peach', 'white tea', 'earl grey', 'lemongrass',
    'floral', 'citrus', 'orange', 'grape', 'white grape', 'nectarine', 'plum',
    'red plum', 'apple', 'green apple', 'blueberry', 'honey', 'floral honey',
    'sugar', 'sugarcane', 'lychee', 'papaya', 'melon', 'cantaloupe', 'honeydew',
    'yuzu', 'champagne', 'apricot', 'blackcurrant', 'lavender', 'chamomile',
    'ginger ale', 'coffee flower', 'coffee blossom', 'grapefruit', 'rose', 'vanilla',
    'mandarine', 'starfruit', 'guava', 'violet', 'elderflower', 'pear', 'passion fruit'
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

def calc_similarity_3(c1, c2):
    cnt1 = str(c1.get('country', '')).strip().lower()
    cnt2 = str(c2.get('country', '')).strip().lower()
    loc1 = (str(c1.get('country', '')) + ' ' + str(c1.get('location', '')) + ' ' + str(c1.get('farm', ''))).lower()
    loc2 = (str(c2.get('country', '')) + ' ' + str(c2.get('location', '')) + ' ' + str(c2.get('farm', ''))).lower()
    
    # 1. Terroir (30% total): Region (10) + Farm (10) + Producer (10)
    if cnt1 == cnt2:
        sub_match = any(reg in loc1 and reg in loc2 for reg in ['boquete', 'sidama', 'huila', 'loja', 'guji', 'chiriqui', 'yirgacheffe'])
        s_reg = 1.0 if sub_match else 0.8
    else:
        s_reg = 0.0

    f1 = re.sub(r'finca|estate|village|station|lot|\d+', '', str(c1.get('farm', '')).lower()).strip()
    f2 = re.sub(r'finca|estate|village|station|lot|\d+', '', str(c2.get('farm', '')).lower()).strip()
    if f1 and f2 and (f1 in f2 or f2 in f1 or f1 == f2):
        s_farm = 1.0
    else:
        t1 = set(f1.split())
        t2 = set(f2.split())
        s_farm = len(t1 & t2) / max(1, len(t1 | t2)) if (t1 and t2) else 0.0

    p1 = str(c1.get('producer', '')).lower().strip()
    p2 = str(c2.get('producer', '')).lower().strip()
    if p1 and p2 and (p1 == p2 or p1 in p2 or p2 in p1):
        s_prod = 1.0
    else:
        tp1 = set(p1.split())
        tp2 = set(p2.split())
        s_prod = len(tp1 & tp2) / max(1, len(tp1 | tp2)) if (tp1 and tp2) else 0.0

    # 2. Cup Notes (50%)
    n1 = extract_notes_set(c1.get('notes', ''))
    n2 = extract_notes_set(c2.get('notes', ''))
    s_notes = len(n1 & n2) / len(n1 | n2) if (n1 and n2) else 0.0

    # 3. Process (20%)
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

    s_cup_notes = round(s_notes * 50.0, 1)
    s_terroir = round((s_reg * 10.0) + (s_farm * 10.0) + (s_prod * 10.0), 1)
    s_process = round(s_proc * 20.0, 1)
    total_sim = round(s_cup_notes + s_terroir + s_process, 1)

    details = {
        'notes': s_cup_notes,
        'terroir': s_terroir,
        'region': round(s_reg * 10.0, 1),
        'farm': round(s_farm * 10.0, 1),
        'producer': round(s_prod * 10.0, 1),
        'process': s_process,
        'notes_jaccard': round(s_notes * 100, 1),
        'same_farm': (s_farm >= 0.8 or s_prod >= 0.8)
    }
    return total_sim, details

all_100g = []
for c in archers:
    if '100' in str(c.get('weight', '')).lower() or not c.get('weight') or '100g' in c.get('title', '').lower():
        sc = score_coffee_item(c, "Archers")
        item = {
            'roastery': 'Archers Coffee',
            'roastery_badge': '🏹 Archers',
            'title': c.get('title'),
            'handle': c.get('handle'),
            'country': c.get('country'),
            'location': c.get('location', ''),
            'farm': c.get('farm', ''),
            'producer': c.get('producer', ''),
            'variety': c.get('variety', ''),
            'process': c.get('process', ''),
            'altitude': c.get('altitude', ''),
            'roast': c.get('roast', 'Light Roast'),
            'notes': c.get('tasting_notes', ''),
            'weight': '100g',
            'price_aed': float(c.get('price_per_100g_aed') or c.get('price_aed') or 50.0),
            'price_krw': int(c.get('price_per_100g_krw') or c.get('price_krw') or round(float(c.get('price_aed', 50)) * 380)),
            'source_url': c.get('source_url', f"https://archerscoffee.com/products/{c.get('handle','')}"),
            'korea_shop': c.get('korea_seller', '국내 정식 수입 전무 (현지 독점 직거래 랏)'),
            'korea_status': c.get('korea_status', '국내 정식 유통 없음'),
            'korea_price': c.get('korea_price', '없음'),
            'merit': c.get('purchase_merit', ''),
            'user_review': c.get('user_review', ''),
            'user_review_link': c.get('user_review_link', ''),
            'award_score': sc['award_score'],
            'award_desc': sc['award_desc'],
            'terroir_score': sc['terroir_score'],
            'terroir_desc': sc['terroir_desc'],
            'review_score': sc['review_score'],
            'review_desc': sc['review_desc'],
            'score_taste': sc['score_taste'],
            'score_price': sc['score_price'],
            'score_rarity': sc['score_rarity'],
            'score_total': sc['score_total'],
            'flavor_category': 'Specialty Coffee'
        }
        all_100g.append(item)

for c in tel:
    if '100' in str(c.get('weight', '')).lower():
        sc = score_coffee_item(c, "The Espresso Lab")
        item = {
            'roastery': 'The Espresso Lab',
            'roastery_badge': '🧪 Espresso Lab',
            'title': c.get('title'),
            'handle': c.get('handle'),
            'country': c.get('country'),
            'location': c.get('location', ''),
            'farm': c.get('farm', ''),
            'producer': c.get('producer', ''),
            'variety': c.get('variety', ''),
            'process': c.get('process', ''),
            'altitude': c.get('altitude', ''),
            'roast': c.get('roast', 'Filter (Light Roast)'),
            'notes': c.get('tasting_notes', ''),
            'weight': '100g',
            'price_aed': float(c.get('price_100g_aed') or c.get('price_per_100g_aed') or c.get('price_aed') or 50.0),
            'price_krw': int(c.get('price_per_100g_krw') or c.get('price_krw') or round(float(c.get('price_aed', 50)) * 380)),
            'source_url': c.get('source_url', f"https://theespressolab.com/products-details/{c.get('handle','')}"),
            'korea_shop': c.get('korea_shop', '국내 미수입'),
            'korea_status': '국내 정식 유통 없음',
            'korea_price': c.get('korea_price', '없음'),
            'merit': c.get('merit', ''),
            'user_review': c.get('community_review', ''),
            'user_review_link': c.get('review_link', ''),
            'award_score': sc['award_score'],
            'award_desc': sc['award_desc'],
            'terroir_score': sc['terroir_score'],
            'terroir_desc': sc['terroir_desc'],
            'review_score': sc['review_score'],
            'review_desc': sc['review_desc'],
            'score_taste': sc['score_taste'],
            'score_price': sc['score_price'],
            'score_rarity': sc['score_rarity'],
            'score_total': sc['score_total'],
            'flavor_category': 'Specialty Coffee'
        }
        all_100g.append(item)

# Deduplicate by handle so exact same product listed in multiple collections isn't duplicated
seen_handles = set()
unique_100g = []
for c in all_100g:
    h = c.get('handle')
    if h and h not in seen_handles:
        seen_handles.add(h)
        unique_100g.append(c)
    elif not h:
        unique_100g.append(c)

# Sort all by score_total desc
unique_100g.sort(key=lambda x: x['score_total'], reverse=True)

# Select Top 20 Candidates
top_20 = unique_100g[:20]

# Compute similarity against previously ranked coffees
for i, c in enumerate(top_20):
    c['rank'] = i + 1
    best_sim = 0.0
    best_target = None
    best_dt = None
    for j in range(i):
        prev = top_20[j]
        sim, dt = calc_similarity_3(c, prev)
        if sim > best_sim:
            best_sim = sim
            best_target = prev
            best_dt = dt
            
    c['max_prior_sim'] = best_sim
    c['similar_target_rank'] = best_target['rank'] if best_target else None
    c['similar_target_title'] = best_target['title'] if best_target else None
    c['similar_details'] = best_dt

# Apply Dimming vs Active selection logic:
# RULE 1: 동일 농장이라도 컵노트가 다르면 중복 제외하지 말 것!
# RULE 2: 전체 유사도가 70% 이상이거나, 동일 농장이면서 컵노트 Jaccard가 20% 이상이면 음영 처리
active_picks = []
dimmed_picks = []

for c in top_20:
    rank = c['rank']
    sim = c['max_prior_sim']
    t_rank = c['similar_target_rank']
    t_title = c['similar_target_title']
    dt = c['similar_details']
    
    is_dimmed = False
    
    # First item is always the baseline 1st active pick
    if rank == 1:
        is_dimmed = False
    else:
        # Check rule: If same farm/producer, check cup notes
        if dt and dt['same_farm']:
            if dt['notes_jaccard'] >= 20.0:
                is_dimmed = True
            else:
                # Same farm but different notes -> ALLOWED!
                # Only dim if overall similarity >= 75%
                if sim >= 75.0:
                    is_dimmed = True
                else:
                    is_dimmed = False
        elif sim >= 70.0:
            is_dimmed = True

    # Limit active picks to 10 best distinct picks
    if not is_dimmed and len(active_picks) < 10:
        c['is_active'] = True
        active_picks.append(c)
        c['active_pick_num'] = len(active_picks)
        if t_rank:
            c['overlap_note'] = f"★ 최종 추천 선발 (#{t_rank}위와 유사도 {sim}% - 독자적 향미/테루아 확보)"
        else:
            c['overlap_note'] = f"★ 최종 추천 1위 선발 (기준 원두)"
    else:
        c['is_active'] = False
        c['active_pick_num'] = None
        dimmed_picks.append(c)
        if t_rank:
            c['overlap_note'] = f"🚫 #{t_rank}위와 유사도 {sim}% (향미/테루아 중복 음영 제외)"
        else:
            c['overlap_note'] = f"🚫 상위 랏과 중복 음영 제외"

# Build rich detailed_review for every coffee
for c in top_20:
    h = c.get('handle')
    exist = existing_reviews.get(h)
    
    taste_text = (
        f"COE/BOP 및 명문 성적({c['award_score']}점: {c['award_desc']}), "
        f"테루아({c['terroir_score']}점: {c['terroir_desc']}), "
        f"업계 긍정평가({c['review_score']}점: {c['review_desc']})를 종합 반영한 맛 점수 {c['score_taste']}점(50점 만점). "
        f"주요 컵노트: {c['notes']}."
    )
    
    price_text = (
        f"100g당 {c['price_aed']} AED (약 {c['price_krw']:,}원)로 가격 점수 {c['score_price']}점(30점 만점). "
        f"실제 가격 차이가 0.1점 단위로 정밀하게 반영되었습니다."
    )
    
    rarity_text = (
        f"희소성 점수 {c['score_rarity']}점(20점 만점). {c['korea_shop']}."
    )
    
    sel_reason = (
        f"종합 점수 {c['score_total']}점({c['rank']}위). {c['overlap_note']}"
    )
    
    if exist and exist.get('brewing_guide'):
        brew_guide = exist['brewing_guide']
    else:
        proc = str(c.get('process', '')).lower()
        if 'washed' in proc:
            brew_guide = "드리퍼: Hario V60 | 원두: 15g | 물: 93℃ 240g (1:16 비율) | 분쇄도: 코만단테 24클릭 | 추출 시간: 2분 15초 내 클린컷 추출 권장."
        elif 'honey' in proc or 'peaberry' in str(c.get('title','')).lower():
            brew_guide = "드리퍼: Origami 또는 Kalita Wave | 원두: 16g | 물: 91℃ 240g (1:15 비율) | 분쇄도: 코만단테 25클릭 | 단맛과 바디감 극대화 추출."
        else:
            brew_guide = "드리퍼: Hario V60 | 원두: 15g | 물: 90℃ 225g (1:15 비율) | 분쇄도: 코만단테 26클릭 | 복합적인 향미 뉘앙스를 위한 저온 추출 권장."
            
    c['detailed_review'] = {
        'taste_analysis': taste_text,
        'price_analysis': price_text,
        'rarity_analysis': rarity_text,
        'selection_reason': sel_reason,
        'brewing_guide': brew_guide
    }

# Save updated top_20_curation.json
with open('c:/cowork/coffee/top_20_curation.json', 'w', encoding='utf-8') as f:
    json.dump(top_20, f, ensure_ascii=False, indent=2)

print(f"Successfully generated top_20_curation.json with {len(top_20)} items!")
print(f"Active picks: {len(active_picks)} / 10 | Dimmed picks: {len(dimmed_picks)}")
for c in top_20:
    act = f"Pick #{c['active_pick_num']}" if c['is_active'] else "DIMMED "
    t_info = f"#{c['similar_target_rank']} ({c['max_prior_sim']}%)" if c['similar_target_rank'] else "Base"
    print(f"[{act:8s}] {c['rank']:2d}위: [{c['roastery_badge']}] {c['title'][:26]:26s} | {c['score_total']:4.1f}점 (맛{c['score_taste']:4.1f}/값{c['score_price']:4.1f}/희{c['score_rarity']:4.1f}) | {c['price_aed']:5.1f} AED | Sim vs {t_info}")
