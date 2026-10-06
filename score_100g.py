import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

archers = json.load(open('new_pipeline/raw_collected_coffees.json', encoding='utf-8'))
espressolab = json.load(open('espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8'))

all_100g = []

# 1. Process Archers
for c in archers:
    w = str(c.get('weight', '')).lower()
    # Check 100g
    if '100' in w or not w or '100g' in c.get('title', '').lower():
        p_aed = float(c.get('price_aed', 0) or 0)
        p_krw = int(c.get('price_krw', 0) or round(p_aed * 380))
        all_100g.append({
            'roastery': 'Archers Coffee',
            'roastery_badge': '🏹 Archers',
            'handle': c.get('handle', ''),
            'title': c.get('title', ''),
            'country': c.get('country', ''),
            'farm': c.get('farm', ''),
            'producer': c.get('producer', ''),
            'variety': c.get('variety', ''),
            'process': c.get('process', ''),
            'altitude': c.get('altitude', ''),
            'roast': c.get('roast', 'Light Roast'),
            'notes': c.get('tasting_notes', ''),
            'weight': '100g',
            'price_aed': p_aed,
            'price_krw': p_krw,
            'source_url': c.get('source_url', f"https://archerscoffee.com/products/{c.get('handle','')}"),
            'collection': c.get('collection', 'Competition / Microlot'),
            'korea_shop': c.get('korea_shop', '국내 미수입 / 아처스 독점'),
            'merit': c.get('merit', '')
        })

# 2. Process The Espresso Lab
for c in espressolab:
    w = str(c.get('weight', '')).lower()
    if '100' in w:
        p_aed = float(c.get('price_aed', 0) or 0)
        p_krw = int(c.get('price_krw', 0) or round(p_aed * 380))
        all_100g.append({
            'roastery': 'The Espresso Lab',
            'roastery_badge': '☕ The Espresso Lab',
            'handle': c.get('handle', ''),
            'title': c.get('title', ''),
            'country': c.get('country', ''),
            'farm': c.get('farm', ''),
            'producer': c.get('producer', ''),
            'variety': c.get('variety', ''),
            'process': c.get('process', ''),
            'altitude': c.get('altitude', ''),
            'roast': c.get('roast', 'Filter (Light Roast)'),
            'notes': c.get('tasting_notes', ''),
            'weight': '100g',
            'price_aed': p_aed,
            'price_krw': p_krw,
            'source_url': c.get('source_url', f"https://theespressolab.com/products-details/{c.get('handle','')}"),
            'collection': c.get('category', 'Filter Collection'),
            'korea_shop': c.get('korea_shop', '국내 미수입'),
            'merit': c.get('merit', '')
        })

print(f"Total 100g candidates from both roasteries: {len(all_100g)}")

# Scoring function based on user criteria:
# 1. Taste (40): Washed (+8), Tea-like notes (+12), Panama/Ethiopia (+10), Clean cup / High pedigree (+10)
# 2. Value (30): 100g price reasonableness & discount vs Korea market
# 3. Rarity (30): Unobtainable in Korea / Exclusive lot / Nanolot

def score_coffee(c):
    taste_score = 0
    value_score = 0
    rarity_score = 0
    
    cnt = c['country'].lower()
    proc = c['process'].lower()
    var = c['variety'].lower()
    notes = c['notes'].lower()
    title = c['title'].lower()
    farm = c['farm'].lower()
    p_aed = c['price_aed']
    
    # 1. Taste Score (Max 40)
    # A. Washed (+8)
    if 'washed' in proc:
        taste_score += 8
    elif 'honey' in proc or 'anaerobic washed' in proc or 'waterfall' in proc:
        taste_score += 6
    else: # Natural
        taste_score += 4
        
    # B. Tea-like & Floral sensory (+12)
    tea_keywords = ['tea', 'jasmine', 'white tea', 'earl grey', 'bergamot', 'peach', 'lemongrass', 'floral', 'citrus', 'clean', 'chamomile', 'blossom']
    matched_tea = sum(1 for kw in tea_keywords if kw in notes or kw in title)
    taste_score += min(12, matched_tea * 3 + 2)
    
    # C. Country preference: Panama or Ethiopia (+10)
    if 'panama' in cnt:
        taste_score += 10
    elif 'ethiopia' in cnt:
        taste_score += 10
    elif 'colombia' in cnt or 'ecuador' in cnt or 'kenya' in cnt:
        taste_score += 7
    else:
        taste_score += 5
        
    # D. Pedigree / Variety / BOP / COE (+10)
    if 'geisha' in var or 'geisha' in title:
        taste_score += 5
    elif 'sl28' in var or 'mejorado' in var or '74158' in var or 'parainema' in var:
        taste_score += 5
    else:
        taste_score += 3
        
    if any(k in (farm + title + c['merit'].lower()) for k in ['auromar', 'elida', 'bop', 'coe', 'bensa', 'lamastus', 'nuguo', 'cenizos', 'longboard']):
        taste_score += 5
    else:
        taste_score += 3
        
    taste_score = min(40, taste_score)
    
    # 2. Value Score (Max 30) - based on 100g price in AED
    if p_aed <= 40: # ~1.5만원 이하 (초극가성비)
        value_score = 30
    elif p_aed <= 70: # ~2.6만원
        value_score = 28
    elif p_aed <= 100: # ~3.8만원
        value_score = 25
    elif p_aed <= 150: # ~5.7만원
        value_score = 21
    elif p_aed <= 200: # ~7.6만원
        value_score = 17
    elif p_aed <= 300: # ~11.4만원
        value_score = 14
    elif p_aed <= 500: # ~19만원
        value_score = 10
    else: # 초고가 옥션 랏 (700~1100 AED)
        value_score = 7
        
    # Bonus value if known big discount vs Korea
    if '반값' in c['merit'] or '50%' in c['merit'] or '35%' in c['merit']:
        value_score = min(30, value_score + 2)
        
    # 3. Rarity in Korea (Max 30)
    if '미수입' in c['korea_shop'] or '전무' in c['korea_shop'] or '독점' in c['korea_shop']:
        rarity_score = 29
    elif '취급 이력' in c['korea_shop'] or '극소량' in c['korea_shop'] or '품절' in c['merit']:
        rarity_score = 26
    else:
        rarity_score = 20
        
    total_score = taste_score + value_score + rarity_score
    return taste_score, value_score, rarity_score, total_score

for c in all_100g:
    t, v, r, tot = score_coffee(c)
    c['score_taste'] = t
    c['score_value'] = v
    c['score_rarity'] = r
    c['score_total'] = tot

all_100g.sort(key=lambda x: x['score_total'], reverse=True)

print("\n--- Top 30 100g Coffees Ranked by Total Score ---")
for i, c in enumerate(all_100g[:30]):
    print(f"{i+1:2d}. [{c['roastery_badge']}] {c['title']} ({c['country']}) | {c['variety']} {c['process']} | {c['price_aed']} AED ({c['price_krw']:,}원) | 총점: {c['score_total']} (맛:{c['score_taste']}, 가성비:{c['score_value']}, 희소성:{c['score_rarity']})")
