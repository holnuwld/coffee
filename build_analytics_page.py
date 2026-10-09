"""
Build interactive coffee analytics page (analytics.html)
Features & Updates:
- Full dataset (171 coffees: Archers 117 + The Espresso Lab 54)
- Statistical summary & insights (Pearson correlation, sweet-spots, pricing tiers)
- Graph 1: Scatter plot (Price per 100g vs Score - Total/Taste/Rarity/Price)
  - Color encoded: Archers Comp (black), Reserve (blue), Selection (yellow), Espresso Lab (red)
  - Small point radius (4.5px) for clear separation in dense clusters
  - Strictly fixed height HUD Bar (44px) & fixed canvas wrapper (460px) to prevent vertical infinite resize loops!
  - HUD update moved safely to onHover hook (isolated from tooltip rendering lifecycle)
  - Tooltip with 35px caretPadding and pointer-events: none
  - Axis-only wheel zoom: Wheel scrolling on the center of the graph allows normal page scroll; only scrolling directly on X/Y axes zooms!
  - Fixed absolute scale limits (X: 0~1150 AED, Y: score range) across filter changes
  - Header-aligned "Fit to Size" button with zero graph overlap
  - Multi-bean cluster dialog: clicking dense spots with multiple dots displays list of all beans at that coordinate
  - Mobile 2-stage interaction: 1st tap shows preview card, 2nd tap/button opens full modal
  - Explicit Enter key or Search button execution (with reset button)
  - Unified 2x2 grid control cards layout: fully standardized button sizes, alignments, and mobile responsiveness
- Graph 2: Tasting notes distribution chart with dynamic recalculation based on active filters
  - Dedicated Origin and Process quick filter buttons
  - Real-time recalculation of flavor frequencies when origin/process/lineup filters change
  - Bidirectional cross-filtering (clicking note filters scatter plot; selecting bean highlights notes)
- Dual theme support (Dark / Light) synchronized with other pages
- Full mobile responsiveness
"""

import json
import sys
import re
import math
import statistics

sys.path.insert(0, 'c:/cowork/coffee')
from scoring_master import score_coffee_item

def normalize_process(proc_str):
    if not proc_str:
        return 'Other'
    p = proc_str.lower()
    if 'washed' in p or 'hybrid' in p:
        return 'Washed'
    elif 'anaerobic' in p or 'ferment' in p or 'yeast' in p or 'koji' in p or 'carbonic' in p:
        return 'Anaerobic/Fermented'
    elif 'honey' in p:
        return 'Honey'
    elif 'natural' in p:
        return 'Natural'
    return 'Other'

def normalize_country(country_str):
    if not country_str:
        return 'Other'
    c = country_str.strip().title()
    if 'Panama' in c:
        return 'Panama'
    elif 'Ethiopia' in c:
        return 'Ethiopia'
    elif 'Colombia' in c:
        return 'Colombia'
    elif 'Costa Rica' in c:
        return 'Costa Rica'
    return 'Other'

def get_altitude_cat(alt_num):
    if not alt_num or alt_num == 0:
        return 'Unknown'
    if alt_num >= 2000:
        return '2000m+ (Ultra-high)'
    elif alt_num >= 1800:
        return '1800-1999m (High)'
    elif alt_num >= 1600:
        return '1600-1799m (Mid-high)'
    else:
        return '<1600m (Standard)'

def extract_notes_list(notes_raw):
    notes = []
    if isinstance(notes_raw, list):
        for n in notes_raw:
            cleaned = n.strip().lower()
            if cleaned and len(cleaned) > 2:
                notes.append(cleaned)
    elif isinstance(notes_raw, str):
        tokens = re.split(r'[,/•·\n&]+', notes_raw)
        for t in tokens:
            cleaned = t.strip().lower()
            if cleaned and len(cleaned) > 2:
                notes.append(cleaned)
    return notes

def generate_korean_keywords(c, roastery, group_key):
    kr = []
    if roastery == 'Archers':
        kr.extend(['아처스', '아쳐스'])
        if group_key == 'competition': kr.extend(['컴피티션', '대회'])
        elif group_key == 'reserve': kr.extend(['리저브', '마이크로랏'])
        elif group_key == 'selection': kr.extend(['셀렉션', '데일리'])
    elif roastery == 'The Espresso Lab':
        kr.extend(['에소랩', '에스프레소랩', '디에스프레소랩', '에스프레소'])
    
    country = str(c.get('country', '')).lower()
    if 'panama' in country: kr.append('파나마')
    if 'ethiopia' in country: kr.append('에티오피아')
    if 'colombia' in country: kr.append('콜롬비아')
    if 'costa rica' in country: kr.append('코스타리카')
    if 'kenya' in country: kr.append('케냐')
    if 'brazil' in country: kr.append('브라질')
    if 'ecuador' in country: kr.append('에콰도르')
    if 'guatemala' in country: kr.append('과테말라')
    
    proc = str(c.get('process', '')).lower()
    if 'washed' in proc: kr.extend(['워시드', '수세식'])
    if 'natural' in proc: kr.extend(['내추럴', '네추럴', '건식'])
    if 'anaerobic' in proc: kr.extend(['무산소', '혐기성'])
    if 'honey' in proc: kr.append('허니')
    if 'ferment' in proc: kr.append('발효')
    if 'yeast' in proc: kr.append('효모')
    if 'carbonic' in proc: kr.append('카보닉')
    if 'hybrid' in proc: kr.append('하이브리드')
    if 'thermal' in proc: kr.append('써멀쇼크')
    
    var = str(c.get('variety', '')).lower()
    title_l = str(c.get('title', '')).lower()
    combined = var + ' ' + title_l
    if 'geisha' in combined or 'gesha' in combined: kr.extend(['게이샤', '게샤'])
    if 'caturra' in combined: kr.append('카투라')
    if 'catuai' in combined: kr.append('카투아이')
    if 'castillo' in combined: kr.append('카스티요')
    if 'typica' in combined: kr.append('티피카')
    if 'bourbon' in combined: kr.append('버번')
    if 'sidra' in combined: kr.append('시드라')
    if 'chiroso' in combined: kr.append('치로소')
    if 'peaberry' in combined: kr.append('피베리')
    if 'pacamara' in combined: kr.append('파카마라')
    if 'eugenioides' in combined: kr.append('에우제니오이데스')

    farm_l = str(c.get('farm', '')).lower() + ' ' + str(c.get('producer', '')).lower() + ' ' + title_l
    if 'auromar' in farm_l: kr.append('오로마')
    if 'elida' in farm_l: kr.append('엘리다')
    if 'chiquita' in farm_l: kr.append('치키타')
    if 'hamasho' in farm_l: kr.append('하마쇼')
    if 'bombe' in farm_l: kr.append('봄베')
    if 'cerro azul' in farm_l: kr.append('세로아줄')
    if 'granja' in farm_l: kr.append('그란하')

    notes = str(c.get('tasting_notes', '')).lower()
    if 'peach' in notes: kr.extend(['복숭아', '피치'])
    if 'jasmine' in notes: kr.extend(['자스민', '재스민'])
    if 'bergamot' in notes: kr.extend(['베르가못', '베르가모트'])
    if 'floral' in notes: kr.extend(['꽃', '플로럴'])
    if 'citrus' in notes: kr.append('시트러스')
    if 'mandarine' in notes: kr.extend(['만다린', '귤'])
    if 'yuzu' in notes: kr.append('유자')
    if 'strawberry' in notes: kr.extend(['딸기', '스트로베리'])
    if 'lychee' in notes: kr.append('리치')
    if 'mango' in notes: kr.append('망고')
    if 'papaya' in notes: kr.append('파파야')
    if 'apricot' in notes: kr.append('살구')
    if 'pear' in notes: kr.append('서양배')
    if 'grape' in notes: kr.append('포도')
    if 'honey' in notes: kr.append('꿀')
    if 'earl grey' in notes: kr.append('얼그레이')
    if 'blueberry' in notes: kr.append('블루베리')
    
    return ' '.join(set(kr))

TODAY_NEW_HANDLES_MAP = {
    'colombia-mandela-vieux': '1008',
    'panama-altieri-coffee-alessa-020425': '1008',
    'panama-altieri-coffee-alessa-190325-cold-dry-ferment': '1008',
    'panama-ale-241223-gw-altieri-coffee': '1008',
    'panama-sakura-geisha-washed-bambito-estate': '1008',
    'panama-enigma-finca-deborah': '1008',
    'panama-interstellar-finca-deborah': '1008',
    'panama-nirvana': '1008',
    'panama-terroir-finca-deborah': '1008',
    'hacienda-la-esmeralda-tomaco-4-anc': '1008',
    'panama-janson-family-geisha-honey-los-alpes-lot-503': '1008',
    'panama-mil-cumbres-lot-omo-0702-geisha-washed': '1008',
    'panama-tierra-blanca-geisha-washed': '1008',
    'brazil-fazenda-ip-natural': '1008',
    'brazil-santa-ines': '1008',
    'brazil-santuario-sul-sudan-rume-washed': '1008',
    'burundi-kivuvuma-natural': '1008',
    'colombia-condor-decaf': '1008',
    'el-salvador-finca-el-cerro-pacas-washed': '1008',
    'el-salvador-finca-majahual': '1008',
    'ethiopia-alo-coffee-mewa-village': '1008',
    'ethiopia-banko-chelchele-chelbesa-natural-1': '1008',
    'guatemala-guatemala-finca-santa-rita': '1008',
    'honduras-finca-cascaritas-lot-19': '1008',
    'honduras-finca-mira-flores-lot-22': '1008',
    'indonesia-central-sumatera-bener-kelipah-natural': '1008',
    'kenya-karimikui-aa': '1008',
    'panama-michella-estate-typica-washed-finca-lerida': '1008',
    'rwanda-muzo-lot-04': '1008',
    'samambaia-natural-yellow-catucai': '1008',
    'caballero-bomba-de-fruta-1-6': '1008'
}

def build_data():
    with open('c:/cowork/coffee/new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
        archers_raw = json.load(f)
    with open('c:/cowork/coffee/espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
        tel_raw = json.load(f)

    all_items = []
    
    # Archers (117)
    for idx, c in enumerate(archers_raw):
        sc = score_coffee_item(c, 'Archers')
        h = c.get('handle', '')
        is_new = h in TODAY_NEW_HANDLES_MAP
        rel_date = TODAY_NEW_HANDLES_MAP.get(h, '1008') if is_new else ''
        col = c.get('collection', '')
        if 'Competition' in col:
            group_key = 'competition'
            group_name = '아처스 컴피티션 (Competition)'
            color = '#1f242d' # deep black
        elif 'Reserve' in col:
            group_key = 'reserve'
            group_name = '아처스 리저브 (Reserve)'
            color = '#2563eb' # royal blue
        else:
            group_key = 'selection'
            group_name = '아처스 셀렉션 (Selection)'
            color = '#d97706' # warm yellow / amber

        alt_num = sc.get('alt_num', 0)
        proc_cat = normalize_process(c.get('process', ''))
        country_cat = normalize_country(c.get('country', ''))
        alt_cat = get_altitude_cat(alt_num)
        notes = extract_notes_list(c.get('tasting_notes', ''))
        kr_keywords = generate_korean_keywords(c, 'Archers', group_key)

        k_price = c.get('korea_price', '-')
        if isinstance(k_price, (int, float)):
            k_price_str = f"{int(k_price):,}원"
        else:
            k_price_str = str(k_price)

        all_items.append({
            'id': f'arc_{idx}',
            'roastery': 'Archers',
            'group_key': group_key,
            'group_name': group_name,
            'color': color,
            'title': c.get('title', 'Unknown Title'),
            'country': c.get('country', '-'),
            'country_cat': country_cat,
            'location': c.get('location', '-'),
            'farm': c.get('farm', '-'),
            'producer': c.get('producer', '-'),
            'variety': c.get('variety', '-'),
            'process': c.get('process', '-'),
            'process_cat': proc_cat,
            'altitude': c.get('altitude', '-'),
            'alt_num': alt_num,
            'alt_cat': alt_cat,
            'roast': c.get('roast', '-'),
            'tasting_notes': c.get('tasting_notes', '-'),
            'notes_list': notes,
            'weight': c.get('weight', '200g'),
            'price_aed': c.get('price_aed', 0),
            'price_krw': c.get('price_krw', 0),
            'price_100g_aed': sc.get('p_100g', 0),
            'price_100g_krw': c.get('price_per_100g_krw', 0),
            'score_total': sc.get('score_total', 0),
            'score_taste': sc.get('score_taste', 0),
            'score_price': sc.get('score_price', 0),
            'score_rarity': sc.get('score_rarity', 0),
            'award_score': sc.get('award_score', 0),
            'award_desc': sc.get('award_desc', '-'),
            'terroir_score': sc.get('terroir_score', 0),
            'terroir_desc': sc.get('terroir_desc', '-'),
            'review_score': sc.get('review_score', 0),
            'review_desc': sc.get('review_desc', '-'),
            'source_url': c.get('source_url', '#'),
            'korea_status': c.get('korea_status', '-'),
            'korea_seller': c.get('korea_seller', '-'),
            'korea_price': k_price_str,
            'merit': c.get('purchase_merit', '-'),
            'search_kr': kr_keywords,
            'handle': h,
            'is_today_new': is_new,
            'release_date': rel_date
        })

    # Espresso Lab (54)
    for idx, c in enumerate(tel_raw):
        sc = score_coffee_item(c, 'The Espresso Lab')
        h = c.get('handle', '')
        is_new = h in TODAY_NEW_HANDLES_MAP
        rel_date = TODAY_NEW_HANDLES_MAP.get(h, '1008') if is_new else ''
        group_key = 'esolab'
        group_name = '더 에스프레소 랩 (The Espresso Lab)'
        color = '#dc2626' # vibrant red

        alt_num = sc.get('alt_num', 0)
        proc_cat = normalize_process(c.get('process', ''))
        country_cat = normalize_country(c.get('country', ''))
        alt_cat = get_altitude_cat(alt_num)
        notes = extract_notes_list(c.get('tasting_notes', ''))
        kr_keywords = generate_korean_keywords(c, 'The Espresso Lab', group_key)

        k_price = c.get('korea_price', '-')
        if isinstance(k_price, (int, float)):
            k_price_str = f"{int(k_price):,}원"
        else:
            k_price_str = str(k_price)

        all_items.append({
            'id': f'tel_{idx}',
            'roastery': 'The Espresso Lab',
            'group_key': group_key,
            'group_name': group_name,
            'color': color,
            'title': c.get('title', 'Unknown Title'),
            'country': c.get('country', '-'),
            'country_cat': country_cat,
            'location': c.get('location', '-'),
            'farm': c.get('farm', '-'),
            'producer': c.get('producer', '-'),
            'variety': c.get('variety', '-'),
            'process': c.get('process', '-'),
            'process_cat': proc_cat,
            'altitude': c.get('altitude', '-'),
            'alt_num': alt_num,
            'alt_cat': alt_cat,
            'roast': c.get('roast', '-'),
            'tasting_notes': c.get('tasting_notes', '-'),
            'notes_list': notes,
            'weight': c.get('weight', '200g'),
            'price_aed': c.get('price_aed', 0),
            'price_krw': c.get('price_krw', 0),
            'price_100g_aed': sc.get('p_100g', 0),
            'price_100g_krw': c.get('price_per_100g_krw', 0),
            'score_total': sc.get('score_total', 0),
            'score_taste': sc.get('score_taste', 0),
            'score_price': sc.get('score_price', 0),
            'score_rarity': sc.get('score_rarity', 0),
            'award_score': sc.get('award_score', 0),
            'award_desc': sc.get('award_desc', '-'),
            'terroir_score': sc.get('terroir_score', 0),
            'terroir_desc': sc.get('terroir_desc', '-'),
            'review_score': sc.get('review_score', 0),
            'review_desc': sc.get('review_desc', '-'),
            'source_url': c.get('source_url', '#'),
            'korea_status': '미수입' if c.get('korea_shop') == '-' else '수입확인',
            'korea_seller': c.get('korea_shop', '-'),
            'korea_price': k_price_str,
            'merit': c.get('merit', '-'),
            'search_kr': kr_keywords,
            'handle': h,
            'is_today_new': is_new,
            'release_date': rel_date
        })

    return all_items

def calculate_statistics(items):
    prices = [it['price_100g_aed'] for it in items]
    totals = [it['score_total'] for it in items]
    tastes = [it['score_taste'] for it in items]
    rarities = [it['score_rarity'] for it in items]

    def pearson(x, y):
        mx = statistics.mean(x)
        my = statistics.mean(y)
        num = sum((a - mx) * (b - my) for a, b in zip(x, y))
        den = math.sqrt(sum((a - mx)**2 for a in x) * sum((b - my)**2 for b in y))
        return num / den if den != 0 else 0

    stats = {
        'total_count': len(items),
        'archers_count': sum(1 for it in items if it['roastery'] == 'Archers'),
        'tel_count': sum(1 for it in items if it['roastery'] == 'The Espresso Lab'),
        'price_min': min(prices),
        'price_max': max(prices),
        'price_median': round(statistics.median(prices), 1),
        'price_mean': round(statistics.mean(prices), 1),
        'total_min': min(totals),
        'total_max': max(totals),
        'total_median': round(statistics.median(totals), 1),
        'total_mean': round(statistics.mean(totals), 1),
        'taste_min': min(tastes),
        'taste_max': max(tastes),
        'taste_median': round(statistics.median(tastes), 1),
        'taste_mean': round(statistics.mean(tastes), 1),
        'corr_price_total': round(pearson(prices, totals), 3),
        'corr_price_taste': round(pearson(prices, tastes), 3),
        'corr_price_rarity': round(pearson(prices, rarities), 3),
    }

    group_stats = {}
    for g_key in ['competition', 'reserve', 'selection', 'esolab']:
        sub = [it for it in items if it['group_key'] == g_key]
        if sub:
            sub_p = [it['price_100g_aed'] for it in sub]
            sub_tot = [it['score_total'] for it in sub]
            sub_taste = [it['score_taste'] for it in sub]
            group_stats[g_key] = {
                'count': len(sub),
                'price_mean': round(statistics.mean(sub_p), 1),
                'price_median': round(statistics.median(sub_p), 1),
                'score_mean': round(statistics.mean(sub_tot), 1),
                'taste_mean': round(statistics.mean(sub_taste), 1),
            }
    stats['groups'] = group_stats
    return stats

def generate_html(items, stats):
    items_json = json.dumps(items, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>전체 원두 인터랙티브 데이터 분석 (171종) | 두바이 스페셜티 허브</title>
  <!-- Pretendard & JetBrains Mono Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
  <!-- Chart.js 4.4.1 & Zoom Plugin -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
  <style>
    :root {{
      --bg-primary: #0d1117;
      --bg-secondary: #161b22;
      --bg-card: #21262d;
      --border-color: #30363d;
      --text-primary: #f0f6fc;
      --text-secondary: #8b949e;
      --text-muted: #6e7681;
      --accent-gold: #e3b341;
      --accent-gold-bg: rgba(227, 179, 65, 0.15);
      --accent-blue: #388bfd;
      --accent-blue-bg: rgba(56, 139, 253, 0.15);
      --accent-red: #f85149;
      --accent-green: #3fb950;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
      --chart-grid: rgba(255, 255, 255, 0.08);
      --chart-tick: #8b949e;
    }}

    [data-theme="light"] {{
      --bg-primary: #f6f8fa;
      --bg-secondary: #ffffff;
      --bg-card: #ffffff;
      --border-color: #d0d7de;
      --text-primary: #1f2328;
      --text-secondary: #57606a;
      --text-muted: #8c959f;
      --accent-gold: #b08800;
      --accent-gold-bg: rgba(176, 136, 0, 0.12);
      --accent-blue: #0969da;
      --accent-blue-bg: rgba(9, 105, 218, 0.12);
      --accent-red: #cf222e;
      --accent-green: #1a7f37;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
      --chart-grid: rgba(0, 0, 0, 0.06);
      --chart-tick: #57606a;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.5;
      padding-bottom: 60px;
      transition: background-color 0.2s, color 0.2s;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px 16px;
    }}

    /* HEADER */
    .header-nav {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border-color);
    }}
    .nav-links {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .nav-btn {{
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--border-color);
      background: var(--bg-secondary);
      color: var(--text-primary);
      cursor: pointer;
      transition: all 0.2s;
    }}
    .nav-btn:hover {{
      border-color: var(--accent-gold);
      color: var(--accent-gold);
    }}
    .nav-btn.active {{
      background: var(--bg-card);
      border-color: var(--accent-gold);
      color: var(--accent-gold);
      box-shadow: 0 0 10px rgba(227, 179, 65, 0.25);
    }}
    .theme-toggle-btn {{
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-primary);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .page-title-box {{
      margin-bottom: 24px;
    }}
    .page-badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 12px;
      background: var(--accent-gold-bg);
      color: var(--accent-gold);
      border: 1px solid var(--accent-gold);
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .page-title {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .page-desc {{
      font-size: 14px;
      color: var(--text-secondary);
    }}

    /* STATS SUMMARY CARDS */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .stat-card-title {{
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .stat-card-val {{
      font-size: 26px;
      font-weight: 800;
      color: var(--text-primary);
      margin-bottom: 4px;
      letter-spacing: -0.5px;
    }}
    .stat-card-sub {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    /* INSIGHT REPORT BOX */
    .insight-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-left: 4px solid var(--accent-gold);
      border-radius: 12px;
      padding: 18px 20px;
      margin-bottom: 24px;
      box-shadow: var(--shadow-sm);
    }}
    .insight-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }}
    .insight-header h3 {{
      font-size: 16px;
      font-weight: 700;
      color: var(--accent-gold);
    }}
    .insight-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 14px;
    }}
    .insight-item {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 12px 14px;
      font-size: 13px;
    }}
    .insight-item-title {{
      font-weight: 700;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .insight-item-desc {{
      color: var(--text-secondary);
      line-height: 1.45;
    }}

    /* ========================================================
       UNIFIED 2x2 CONTROLS CARD GRID SYSTEM (PERFECT ALIGNMENT)
       ======================================================== */
    .controls-card-wrapper {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 22px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: var(--shadow-sm);
    }}

    .controls-grid-2x2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}
    @media (max-width: 900px) {{
      .controls-grid-2x2 {{
        grid-template-columns: 1fr;
      }}
    }}

    .ctrl-subcard {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .ctrl-subcard-header {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .ctrl-icon {{
      font-size: 14px;
    }}
    .ctrl-title {{
      font-size: 12px;
      font-weight: 700;
      color: var(--text-secondary);
      letter-spacing: 0.3px;
    }}

    .btn-group-grid {{
      display: grid;
      gap: 5px;
      width: 100%;
    }}
    .btn-group-grid.grid-4 {{
      grid-template-columns: repeat(4, 1fr);
    }}
    .btn-group-grid.grid-5 {{
      grid-template-columns: repeat(5, 1fr);
    }}
    @media (max-width: 600px) {{
      .btn-group-grid.grid-4 {{
        grid-template-columns: repeat(2, 1fr);
      }}
      .btn-group-grid.grid-5 {{
        grid-template-columns: repeat(3, 1fr);
      }}
    }}

    .ctrl-btn {{
      height: 34px;
      padding: 0 8px;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      transition: all 0.15s ease;
      user-select: none;
    }}
    .ctrl-btn:hover {{
      color: var(--text-primary);
      border-color: var(--accent-gold);
    }}
    .ctrl-btn.active {{
      background: var(--accent-gold);
      color: #000;
      border-color: var(--accent-gold);
      font-weight: 800;
      box-shadow: 0 1px 4px rgba(0,0,0,0.2);
    }}

    /* BOTTOM ROW: LINEUPS & UNIFIED SEARCH */
    .controls-bottom-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
      padding-top: 12px;
      border-top: 1px solid var(--border-color);
    }}
    .lineup-bar-left {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .ctrl-bottom-label {{
      font-size: 12px;
      font-weight: 700;
      color: var(--text-secondary);
      white-space: nowrap;
    }}

    .filter-chips {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .chip {{
      height: 34px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 0 12px;
      border-radius: 18px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .chip.active {{
      opacity: 1 !important;
      border: 2px solid currentColor !important;
      background: var(--bg-card) !important;
      color: var(--text-primary) !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }}
    .chip:not(.active) {{
      opacity: 0.35 !important;
      border: 1px dashed var(--border-color) !important;
      background: transparent !important;
      color: var(--text-muted) !important;
      text-decoration: line-through;
    }}
    .chip-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
      transition: all 0.2s;
    }}
    .chip:not(.active) .chip-dot {{
      filter: grayscale(100%);
      opacity: 0.4;
    }}

    /* SEARCH INPUT GROUP WITH EXACT 34px HEIGHT */
    .lineup-bar-right {{
      display: flex;
      align-items: center;
    }}
    @media (max-width: 900px) {{
      .lineup-bar-right {{
        width: 100%;
      }}
      .search-input-group {{
        width: 100%;
      }}
      .search-input {{
        flex: 1;
      }}
    }}
    .search-input-group {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}
    .search-input {{
      height: 34px;
      padding: 0 12px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      color: var(--text-primary);
      font-size: 12.5px;
      min-width: 260px;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--accent-gold);
    }}
    .search-btn {{
      height: 34px;
      padding: 0 14px;
      background: var(--accent-gold);
      color: #000;
      border: 1px solid var(--accent-gold);
      border-radius: 6px;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      white-space: nowrap;
      transition: opacity 0.2s;
    }}
    .search-btn:hover {{
      opacity: 0.9;
    }}
    .search-clear-btn {{
      height: 34px;
      padding: 0 10px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
    }}
    .search-clear-btn:hover {{
      color: var(--text-primary);
      border-color: var(--accent-red);
    }}

    /* SHAPE LEGEND BANNER */
    .shape-legend-bar {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      padding: 8px 14px;
      background: var(--bg-card);
      border: 1px dashed var(--border-color);
      border-radius: 8px;
      font-size: 12px;
      color: var(--text-secondary);
    }}
    .shape-item {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-weight: 600;
      color: var(--text-primary);
    }}

    /* STRICT FIXED HEIGHT HUD BAR - PREVENTS RESIZE LOOP */
    .chart-hud-bar {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 0 14px;
      margin-bottom: 12px;
      height: 44px;
      min-height: 44px;
      max-height: 44px;
      overflow: hidden;
      display: flex;
      align-items: center;
      box-sizing: border-box;
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }}
    .chart-hud-idle {{
      color: var(--text-muted);
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .chart-hud-active {{
      color: var(--text-primary);
      font-size: 12.5px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      width: 100%;
    }}

    /* CHARTS LAYOUT & STRICT FIXED HEIGHT CANVAS */
    .charts-main-grid {{
      display: grid;
      grid-template-columns: 2fr 1.1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}
    @media (max-width: 1024px) {{
      .charts-main-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .chart-box {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
    }}
    .chart-box-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .chart-title {{
      font-size: 16px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .chart-subtitle {{
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 2px;
    }}

    /* STRICT 460px FIXED HEIGHT CANVAS WRAPPER - PREVENTS VERTICAL RESIZE LOOPS */
    .chart-canvas-wrapper {{
      position: relative;
      height: 460px;
      min-height: 460px;
      max-height: 460px;
      width: 100%;
      overflow: hidden;
    }}

    /* MOBILE PREVIEW CARD */
    .mobile-preview-card {{
      position: fixed;
      bottom: 16px;
      left: 16px;
      right: 16px;
      background: var(--bg-secondary);
      border: 2px solid var(--accent-gold);
      border-radius: 14px;
      padding: 14px 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.7);
      z-index: 999;
      animation: slideUpPreview 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    @keyframes slideUpPreview {{
      from {{ transform: translateY(100%); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}

    /* DETAIL MODAL / PANEL */
    .detail-overlay {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.65);
      backdrop-filter: blur(4px);
      z-index: 1000;
      justify-content: center;
      align-items: center;
      padding: 16px;
    }}
    .detail-overlay.active {{
      display: flex;
    }}
    .detail-modal {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      max-width: 650px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 10px 40px rgba(0,0,0,0.6);
      animation: modalFadeIn 0.2s ease-out;
    }}
    @keyframes modalFadeIn {{
      from {{ transform: scale(0.96); opacity: 0; }}
      to {{ transform: scale(1); opacity: 1; }}
    }}
    .modal-header {{
      padding: 18px 22px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      position: sticky;
      top: 0;
      background: var(--bg-secondary);
      z-index: 2;
    }}
    .modal-star-btn {{
      border-color: var(--accent-gold) !important;
      color: var(--accent-gold) !important;
      font-weight: 700 !important;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .modal-star-btn:hover {{
      background: rgba(210, 153, 34, 0.2) !important;
      transform: translateY(-1px);
    }}
    .modal-star-btn.active-in-cart {{
      background: var(--accent-gold) !important;
      color: #0d1117 !important;
      box-shadow: 0 0 10px rgba(210, 153, 34, 0.5) !important;
    }}
    .modal-star-btn-sm {{
      padding: 4px 10px !important;
      font-size: 12px !important;
      border-color: var(--accent-gold) !important;
      color: var(--accent-gold) !important;
      font-weight: 700 !important;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .modal-star-btn-sm:hover {{
      background: rgba(210, 153, 34, 0.2) !important;
    }}
    .modal-star-btn-sm.active-in-cart {{
      background: var(--accent-gold) !important;
      color: #0d1117 !important;
    }}
  .modal-close-btn {{
      background: transparent;
      border: none;
      font-size: 22px;
      color: var(--text-muted);
      cursor: pointer;
      line-height: 1;
      padding: 4px 8px;
      border-radius: 6px;
    }}
    .modal-close-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-card);
    }}
    .modal-body {{
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    /* CLUSTER MULTI-ITEM CARD */
    .cluster-item-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 14px;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }}
    .cluster-item-card:hover {{
      border-color: var(--accent-gold);
      background: var(--bg-primary);
      transform: translateX(3px);
    }}

    /* NEW COFFEE HIGHLIGHTS */
    .today-new-coffee-title {{
      color: #388bfd !important;
      font-weight: 700;
    }}
    [data-theme="light"] .today-new-coffee-title {{
      color: #2563eb !important;
    }}
    .badge-new-date {{
      display: inline-block;
      font-size: 10px;
      font-weight: 800;
      background: rgba(56, 139, 253, 0.15);
      color: #388bfd;
      border: 1px solid rgba(56, 139, 253, 0.35);
      border-radius: 4px;
      padding: 1px 5px;
      margin-left: 6px;
      vertical-align: middle;
      letter-spacing: 0.5px;
      line-height: 1.2;
    }}
    [data-theme="light"] .badge-new-date {{
      background: rgba(37, 99, 235, 0.1);
      color: #2563eb;
      border-color: rgba(37, 99, 235, 0.3);
    }}

    /* DETAIL ELEMENTS */
    .detail-badges {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .detail-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
    }}
    .detail-badge.roastery {{
      color: var(--accent-gold);
      border-color: var(--accent-gold);
    }}
    .detail-title {{
      font-size: 20px;
      font-weight: 800;
      line-height: 1.3;
      color: var(--text-primary);
    }}
    .detail-score-box {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 16px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      text-align: center;
    }}
    .score-unit-num {{
      font-size: 22px;
      font-weight: 800;
      color: var(--accent-gold);
    }}
    .score-unit-label {{
      font-size: 11px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-top: 2px;
    }}
    .detail-section-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}
    .detail-specs-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      font-size: 13px;
    }}
    .spec-row {{
      display: flex;
      flex-direction: column;
      background: var(--bg-card);
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }}
    .spec-lbl {{
      font-size: 11px;
      color: var(--text-muted);
      margin-bottom: 2px;
    }}
    .spec-val {{
      font-weight: 600;
      color: var(--text-primary);
      word-break: break-word;
    }}
    .notes-tag-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .note-tag {{
      background: var(--accent-gold-bg);
      color: var(--accent-gold);
      border: 1px solid var(--accent-gold);
      padding: 4px 10px;
      border-radius: 16px;
      font-size: 12px;
      font-weight: 600;
    }}
    .modal-footer {{
      padding: 16px 22px;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      background: var(--bg-secondary);
    }}

    /* BOTTOM TABLE VIEW */
    .table-section {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px 20px;
      box-shadow: var(--shadow-sm);
    }}
    .table-responsive {{
      overflow-x: auto;
      max-height: 960px;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      margin-top: 12px;
    }}
    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      text-align: left;
    }}
    table.data-table th {{
      background: var(--bg-card);
      padding: 10px 12px;
      font-weight: 700;
      color: var(--text-secondary);
      position: sticky;
      top: 0;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
      cursor: pointer;
      user-select: none;
    }}
    table.data-table th:hover {{
      color: var(--accent-gold);
    }}
    table.data-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-primary);
    }}
    table.data-table tbody tr:hover {{
      background: var(--bg-card);
      cursor: pointer;
    }}

    /* MULTI-METRIC RANGE FILTER PANEL */
    .table-filter-panel {{
      margin-top: 14px;
      margin-bottom: 10px;
      padding: 16px 18px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: var(--shadow-sm);
    }}
    .tfp-top-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--border-color);
    }}
    .tfp-title {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .tfp-top-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .tfp-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 12px;
    }}
    .tfp-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .tfp-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-secondary);
    }}
    .tfp-range-row {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .tfp-input-box {{
      flex: 1;
      display: inline-flex;
      align-items: center;
      height: 30px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 0 6px;
      gap: 4px;
      transition: border-color 0.2s;
    }}
    .tfp-input-box:focus-within {{
      border-color: var(--accent-gold);
    }}
    .tfp-num-input {{
      width: 100%;
      height: 24px;
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-size: 12px;
      font-weight: 700;
      outline: none;
      padding: 0;
    }}
    .tfp-num-input::placeholder {{
      color: var(--text-muted);
      font-weight: normal;
      font-size: 11px;
    }}
    .tfp-text-input {{
      width: 100%;
      height: 24px;
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-size: 12px;
      font-weight: 600;
      outline: none;
      padding: 0 4px;
    }}
    .tfp-text-input::placeholder {{
      color: var(--text-muted);
      font-weight: normal;
      font-size: 11px;
    }}
    .tfp-unit-tag {{
      font-size: 10.5px;
      color: var(--text-muted);
      font-weight: 600;
      white-space: nowrap;
    }}
    .tfp-range-sep {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 700;
    }}
    .tfp-preset-row {{
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }}
    .tfp-preset-btn {{
      height: 24px;
      padding: 0 7px;
      border-radius: 4px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-secondary);
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      white-space: nowrap;
    }}
    .tfp-preset-btn:hover {{
      border-color: var(--accent-gold);
      color: var(--text-primary);
    }}
    .tfp-preset-btn.active {{
      background: var(--accent-gold);
      color: #000;
      border-color: var(--accent-gold);
      font-weight: 800;
    }}
    .tfp-bottom-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      padding-top: 8px;
      border-top: 1px dashed var(--border-color);
    }}
    .tfp-active-tags {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .tfp-tag {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--accent-gold);
      background: var(--accent-gold-bg);
      border: 1px solid var(--accent-gold);
      padding: 3px 8px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tfp-tag:hover {{
      background: rgba(227, 179, 65, 0.25);
    }}
    .tfp-tag-del {{
      font-weight: 800;
      color: var(--text-muted);
      margin-left: 2px;
    }}
    .tfp-tag-del:hover {{
      color: var(--accent-red);
    }}
    .tfp-btn-apply {{
      height: 32px;
      padding: 0 14px;
      background: var(--accent-gold);
      color: #000;
      border: none;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      transition: opacity 0.2s;
    }}
    .tfp-btn-apply:hover {{
      opacity: 0.9;
    }}
    .tfp-btn-reset {{
      height: 30px;
      padding: 0 10px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tfp-btn-reset:hover {{
      border-color: var(--accent-red);
      color: var(--accent-red);
    }}
    .tpf-sync-label {{
      font-size: 12px;
      color: var(--text-secondary);
      display: inline-flex;
      align-items: center;
      gap: 5px;
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}
    .tpf-sync-label input[type="checkbox"] {{
      cursor: pointer;
      accent-color: var(--accent-gold);
    }}
    .table-count-badge {{
      display: inline-block;
      font-size: 12px;
      font-weight: 800;
      color: var(--accent-gold);
      background: var(--accent-gold-bg);
      border: 1px solid var(--accent-gold);
      padding: 2px 8px;
      border-radius: 12px;
    }}
    .table-filter-tag {{
      font-size: 11.5px;
      font-weight: 700;
      color: var(--accent-blue);
      background: rgba(37, 99, 235, 0.12);
      border: 1px solid var(--accent-blue);
      padding: 2px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    @media (max-width: 768px) {{
      .tfp-top-header {{
        flex-direction: column;
        align-items: flex-start;
      }}
      .tfp-grid {{
        grid-template-columns: 1fr;
      }}
      .tfp-bottom-bar {{
        flex-direction: column;
        align-items: flex-start;
      }}
    }}
  
  /* TABLE HEADER TODAY NEW FILTER BUTTON */
  .th-today-filter-btn {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(56, 139, 253, 0.15);
    color: #58a6ff;
    border: 1px solid rgba(56, 139, 253, 0.4);
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    user-select: none;
    vertical-align: middle;
    line-height: 1.2;
    text-transform: none;
  }}
  .th-today-filter-btn:hover {{
    background: rgba(56, 139, 253, 0.3);
    border-color: #58a6ff;
    color: #fff;
    transform: translateY(-1px);
  }}
  .th-today-filter-btn.active {{
    background: #238636 !important;
    color: #ffffff !important;
    border-color: #2ea043 !important;
    box-shadow: 0 0 10px rgba(46, 160, 67, 0.4);
  }}
  [data-theme="light"] .th-today-filter-btn {{
    background: rgba(37, 99, 235, 0.1);
    color: #2563eb;
    border-color: rgba(37, 99, 235, 0.35);
  }}
  [data-theme="light"] .th-today-filter-btn:hover {{
    background: rgba(37, 99, 235, 0.2);
    color: #1d4ed8;
    border-color: #2563eb;
  }}
  [data-theme="light"] .th-today-filter-btn.active {{
    background: #16a34a !important;
    color: #ffffff !important;
    border-color: #15803d !important;
    box-shadow: 0 0 10px rgba(22, 163, 74, 0.35);
  }}

</style>
</head>
<body>

<div class="container">
  <!-- TOP NAV -->
  <div class="header-nav">
    <div class="nav-links">
      <a href="index.html" class="nav-btn">🏆 Top 20 큐레이션</a>
      <a href="analytics.html" class="nav-btn active">📊 애널리틱스</a>
      <a href="archers_coffee_clean_verified.html" class="nav-btn">🏹 아처스 대시보드</a>
      <a href="theespressolab_verified.html" class="nav-btn">☕ 에소랩 대시보드</a>
      <a href="cart.html" class="nav-btn">🛒 장바구니 (<span class="cart-badge-count">0</span>개)</a>
    </div>
    <button class="theme-toggle-btn" id="themeToggleBtn" onclick="toggleTheme()">
      <span id="themeIcon">☀️</span> <span id="themeText">라이트 모드</span>
    </button>
  </div>

  <!-- PAGE TITLE -->
  <div class="page-title-box">
    <span class="page-badge">Interactive Full Dataset Analytics</span>
    <h1 class="page-title">
      <span>📊 두바이 2대 로스터리 전체 원두 통계 분석 (171종)</span>
    </h1>
    <p class="page-desc">
      아처스(Archers 117종)와 더 에스프레소 랩(The Espresso Lab 54종) 전수 조사 데이터를 바탕으로 가격 대비 점수 분포, 컵노트 군집, 가성비 스위트스팟을 정밀 분석합니다.
    </p>
  </div>

  <!-- STATS SUMMARY CARDS -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-card-title">
        <span>총 분석 원두 (데이터셋 규모)</span>
        <span>☕</span>
      </div>
      <div class="stat-card-val">171종</div>
      <div class="stat-card-sub">아처스 117종 (68.4%) + 에소랩 54종 (31.6%)</div>
    </div>

    <div class="stat-card">
      <div class="stat-card-title">
        <span>100g당 가격 (중앙값 / 평균)</span>
        <span>💰</span>
      </div>
      <div class="stat-card-val">110.0 AED</div>
      <div class="stat-card-sub">평균 141.8 AED (~53,880원) | 범위: 28 ~ 1,110 AED</div>
    </div>

    <div class="stat-card">
      <div class="stat-card-title">
        <span>종합 점수 (100점 만점)</span>
        <span>⭐</span>
      </div>
      <div class="stat-card-val">79.4점</div>
      <div class="stat-card-sub">맛 35.6 / 가격 23.8 / 희소 20.0 (중앙값 78.2점)</div>
    </div>

    <div class="stat-card">
      <div class="stat-card-title">
        <span>가성비 스위트스팟 (Sweet Spot)</span>
        <span>🎯</span>
      </div>
      <div class="stat-card-val" style="color:var(--accent-green);">30 ~ 70 AED</div>
      <div class="stat-card-sub">Reserve/Selection 라인업 집중, 평균 종합 85.6점</div>
    </div>
  </div>

  <!-- STATISTICAL INSIGHTS ACCORDION -->
  <div class="insight-card">
    <div class="insight-header">
      <span>💡</span>
      <h3>통계적 유효 분포 및 핵심 인사이트 분석</h3>
    </div>
    <div class="insight-list">
      <div class="insight-item">
        <div class="insight-item-title">
          <span>🎯</span> <strong>가성비 극대화 구간: 30 ~ 70 AED</strong>
        </div>
        <div class="insight-item-desc">
          아처스 리저브(평균 51.6 AED) 및 셀렉션(평균 35.2 AED)이 평균 종합점수 85.6점과 82.9점을 기록하여 만족도/가격 밸런스가 가장 높습니다.
        </div>
      </div>

      <div class="insight-item">
        <div class="insight-item-title">
          <span>📉</span> <strong>가격과 종합점수의 음의 상관관계 (r = -0.602)</strong>
        </div>
        <div class="insight-item-desc">
          초고가 라인업(100g당 300~1,110 AED)은 가격 점수(30점) 감점으로 종합점수가 낮아지는 반면, 40~90 AED 대 고품질 원두들이 최상위권을 형성합니다.
        </div>
      </div>

      <div class="insight-item">
        <div class="insight-item-title">
          <span>📈</span> <strong>맛 점수와 가격의 한계효용 체감 (r = +0.083)</strong>
        </div>
        <div class="insight-item-desc">
          가격이 3~5배 비싸다고 맛 점수가 비례하지 않습니다. 100g당 50~100 AED 대에서도 Q-Grader 90+급 테루아를 갖춘 원두가 다수 존재합니다.
        </div>
      </div>

      <div class="insight-item">
        <div class="insight-item-title">
          <span>🏛️</span> <strong>로스터리별 뚜렷한 포지셔닝 차이</strong>
        </div>
        <div class="insight-item-desc">
          아처스는 광범위한 발효 프로세스 및 가성비 리저브(평균 51.6 AED) 중심인 반면, 에소랩은 파나마 게이샤 등 희귀 고가 라인(평균 209.3 AED)에 집중합니다.
        </div>
      </div>
    </div>
  </div>

  <!-- STANDARDIZED CONTROLS CARD WRAPPER (2x2 GRID + CLEAN BOTTOM BAR) -->
  <div class="controls-card-wrapper">
    <!-- TOP GRID: 2x2 STANDARDIZED CARDS -->
    <div class="controls-grid-2x2">
      <!-- 1. Y-Axis Metric -->
      <div class="ctrl-subcard">
        <div class="ctrl-subcard-header">
          <span class="ctrl-icon">📈</span>
          <span class="ctrl-title">Y축 점수 지표 선택</span>
        </div>
        <div class="btn-group-grid grid-4">
          <button class="ctrl-btn active" onclick="setYMetric('total', this)">⭐ 종합점수</button>
          <button class="ctrl-btn" onclick="setYMetric('taste', this)">☕ 맛 (50)</button>
          <button class="ctrl-btn" onclick="setYMetric('rarity', this)">💎 희소 (20)</button>
          <button class="ctrl-btn" onclick="setYMetric('price', this)">💰 가격 (30)</button>
        </div>
      </div>

      <!-- 2. Point Shape Mode -->
      <div class="ctrl-subcard">
        <div class="ctrl-subcard-header">
          <span class="ctrl-icon">🔷</span>
          <span class="ctrl-title">점 모양(심볼) 구분</span>
        </div>
        <div class="btn-group-grid grid-4">
          <button class="ctrl-btn active" onclick="setShapeMode('default', this)">● 기본(원형)</button>
          <button class="ctrl-btn" onclick="setShapeMode('country', this)">🌍 원산지별</button>
          <button class="ctrl-btn" onclick="setShapeMode('process', this)">⚙️ 프로세스별</button>
          <button class="ctrl-btn" onclick="setShapeMode('altitude', this)">⛰️ 고도별</button>
        </div>
      </div>

      <!-- 3. Origin Quick Filter -->
      <div class="ctrl-subcard">
        <div class="ctrl-subcard-header">
          <span class="ctrl-icon">🌍</span>
          <span class="ctrl-title">원산지 빠른 필터 (Origin)</span>
        </div>
        <div class="btn-group-grid grid-5" id="originFilterGroup">
          <button class="ctrl-btn active" onclick="setOriginFilter('all', this)">전체</button>
          <button class="ctrl-btn" onclick="setOriginFilter('Ethiopia', this)">에티오피아</button>
          <button class="ctrl-btn" onclick="setOriginFilter('Panama', this)">파나마</button>
          <button class="ctrl-btn" onclick="setOriginFilter('Colombia', this)">콜롬비아</button>
          <button class="ctrl-btn" onclick="setOriginFilter('Other', this)">기타</button>
        </div>
      </div>

      <!-- 4. Process Quick Filter -->
      <div class="ctrl-subcard">
        <div class="ctrl-subcard-header">
          <span class="ctrl-icon">⚙️</span>
          <span class="ctrl-title">가공 방식 필터 (Process)</span>
        </div>
        <div class="btn-group-grid grid-5" id="processFilterGroup">
          <button class="ctrl-btn active" onclick="setProcessFilter('all', this)">전체</button>
          <button class="ctrl-btn" onclick="setProcessFilter('Washed', this)">워시드</button>
          <button class="ctrl-btn" onclick="setProcessFilter('Natural', this)">내추럴</button>
          <button class="ctrl-btn" onclick="setProcessFilter('Anaerobic/Fermented', this)">무산소</button>
          <button class="ctrl-btn" onclick="setProcessFilter('Honey', this)">허니</button>
        </div>
      </div>
    </div>

    <!-- BOTTOM ROW: LINEUPS & UNIFIED SEARCH -->
    <div class="controls-bottom-bar">
      <!-- Left: Lineup chips -->
      <div class="lineup-bar-left">
        <span class="ctrl-bottom-label">🏷️ 라인업 필터:</span>
        <div class="filter-chips">
          <div class="chip active" onclick="toggleGroupFilter('competition', this)" style="border-color:#8b949e; color:#f0f6fc;">
            <span class="chip-dot" style="background:#1f242d; border:1px solid #8b949e;"></span>
            <span>아처스 컴피티션 (85)</span>
          </div>
          <div class="chip active" onclick="toggleGroupFilter('reserve', this)" style="border-color:#2563eb; color:#60a5fa;">
            <span class="chip-dot" style="background:#2563eb;"></span>
            <span>아처스 리저브 (20)</span>
          </div>
          <div class="chip active" onclick="toggleGroupFilter('selection', this)" style="border-color:#d97706; color:#fbbf24;">
            <span class="chip-dot" style="background:#d97706;"></span>
            <span>아처스 셀렉션 (12)</span>
          </div>
          <div class="chip active" onclick="toggleGroupFilter('esolab', this)" style="border-color:#dc2626; color:#f87171;">
            <span class="chip-dot" style="background:#dc2626;"></span>
            <span>에소랩 전체 (54)</span>
          </div>
        </div>
      </div>

      <!-- Right: Search box with Enter/Button -->
      <div class="lineup-bar-right">
        <div class="search-input-group">
          <input type="text" id="searchInput" class="search-input" placeholder="🔍 원두명, 생산국(예:에티오피아), 농장..." onkeydown="if(event.key==='Enter') executeSearch()">
          <button class="search-btn" onclick="executeSearch()">검색</button>
          <button class="search-clear-btn" id="searchResetBtn" onclick="clearSearch()" style="display:none;" title="검색어 초기화">✕</button>
        </div>
      </div>
    </div>

    <!-- SHAPE LEGEND -->
    <div class="shape-legend-bar" id="shapeLegendBar">
      <span style="font-weight:700; color:var(--accent-gold);">심볼 안내:</span>
      <span class="shape-item">● 전체 원두 (원형)</span>
    </div>
  </div>

  <!-- MAIN CHARTS LAYOUT -->
  <div class="charts-main-grid">
    <!-- GRAPH 1: SCATTER PLOT -->
    <div class="chart-box">
      <div class="chart-box-header">
        <div>
          <div class="chart-title">
            <span>🎯 100g당 가격 vs 점수 산점도 (Scatter Plot)</span>
          </div>
          <div class="chart-subtitle" id="scatterSubtitle">
            X/Y축 위에서 휠 스크롤 시 축 확대/축소 가능 (가운데는 일반 스크롤 유지). 점 클릭 시 상세 확인.
          </div>
        </div>
        <!-- FIT TO SIZE BUTTON PROPERLY ALIGNED IN HEADER -->
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:12px; color:var(--text-muted);">표시: <strong id="pointCountDisplay" style="color:var(--accent-gold);">171</strong>종</span>
          <button class="nav-btn" onclick="resetScatterZoom()" style="height:32px; padding:0 12px; font-size:12px; font-weight:700; border-color:var(--accent-gold); color:var(--accent-gold);">
            🔍 전체보기 (Fit)
          </button>
        </div>
      </div>

      <!-- STRICT FIXED 44px HEIGHT HUD BAR - NO VERTICAL EXPANSION -->
      <div class="chart-hud-bar" id="chartHudBar">
        <div class="chart-hud-idle" id="hudIdleText">
          <span>💡</span> <span>점 위에 마우스를 올리면 원두 요약이 여기에 실시간 표시됩니다. (밀집 구간 클릭 시 선택 목록 팝업)</span>
        </div>
        <div class="chart-hud-active" id="hudActiveText" style="display:none;"></div>
      </div>

      <!-- STRICT FIXED 460px HEIGHT CANVAS WRAPPER -->
      <div class="chart-canvas-wrapper">
        <canvas id="scatterChart"></canvas>
      </div>
    </div>

    <!-- GRAPH 2: TASTING NOTES DISTRIBUTION -->
    <div class="chart-box">
      <div class="chart-box-header">
        <div>
          <div class="chart-title">
            <span>🍑 컵노트 출현 빈도 및 분포도</span>
          </div>
          <div class="chart-subtitle" id="notesChartSubtitle">
            현재 필터링된 원두 171종 기준 컵노트 출현 빈도 (바 클릭 시 크로스 필터링)
          </div>
        </div>
      </div>
      <!-- STRICT FIXED 460px HEIGHT CANVAS WRAPPER -->
      <div class="chart-canvas-wrapper" style="margin-top:56px;">
        <canvas id="notesChart"></canvas>
      </div>
    </div>
  </div>

  <!-- BOTTOM TABLE VIEW -->
  <div class="table-section">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <h3 style="font-size:16px; font-weight:700; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
        <span>📋 필터링된 원두 리스트</span>
        <span class="table-count-badge"><span id="tableCountDisplay">171</span>종</span>
        <span id="priceFilterActiveBadge" class="table-filter-tag" style="display:none;"></span>
      </h3>
      <div style="font-size:12px; color:var(--text-muted);">행을 클릭하면 상세 분석 모달이 열립니다.</div>
    </div>

    <!-- MULTI-METRIC RANGE FILTER PANEL -->
    <div class="table-filter-panel">
      <!-- Panel Top Header -->
      <div class="tfp-top-header">
        <div class="tfp-title">
          <span>🎛️ 원두 리스트 다차원 정밀 필터 (수치 범위 · 컵노트 · 프로세스)</span>
          <span style="font-size:11.5px; font-weight:normal; color:var(--text-muted); margin-left:6px;">지표별 범위 및 컵노트(주관식), 프로세스(객관식) 조건을 복합 적용할 수 있습니다.</span>
        </div>
        <div class="tfp-top-actions">
          <label class="tpf-sync-label" title="체크 시 상단 산점도 및 컵노트 차트에도 해당 범위 필터가 함께 적용됩니다.">
            <input type="checkbox" id="syncPriceWithChartsCheckbox" checked onchange="toggleSyncPriceWithCharts(this)">
            <span>📊 상단 차트 동시 연동</span>
          </label>
          <button class="tfp-btn-reset" onclick="resetAllRangeFilters()" title="모든 범위 필터 초기화">✕ 필터 전체 초기화</button>
        </div>
      </div>

      <!-- 5 Metric Filter Cards Grid -->
      <div class="tfp-grid">
        <!-- 1. Price 100g -->
        <div class="tfp-card">
          <div class="tfp-card-header">
            <span>💰 100g당 가격 (AED)</span>
            <span style="font-size:10.5px; color:var(--text-muted);">28 ~ 1,110 AED</span>
          </div>
          <div class="tfp-range-row">
            <div class="tfp-input-box">
              <input type="number" id="filter_price_min" class="tfp-num-input" placeholder="최소" min="0" max="1500" step="5" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이상</span>
            </div>
            <span class="tfp-range-sep">~</span>
            <div class="tfp-input-box">
              <input type="number" id="filter_price_max" class="tfp-num-input" placeholder="최대" min="0" max="1500" step="5" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이하</span>
            </div>
          </div>
          <div class="tfp-preset-row">
            <button class="tfp-preset-btn" onclick="setPreset('price_100g_aed', null, 40, this)">≤40</button>
            <button class="tfp-preset-btn" onclick="setPreset('price_100g_aed', null, 70, this)">≤70 (스위트)</button>
            <button class="tfp-preset-btn" onclick="setPreset('price_100g_aed', 30, 70, this)">30~70</button>
            <button class="tfp-preset-btn" onclick="setPreset('price_100g_aed', null, 100, this)">≤100</button>
            <button class="tfp-preset-btn" onclick="setPreset('price_100g_aed', null, 150, this)">≤150</button>
          </div>
        </div>

        <!-- 2. Total Score -->
        <div class="tfp-card">
          <div class="tfp-card-header">
            <span>⭐ 종합점수 (100점)</span>
            <span style="font-size:10.5px; color:var(--text-muted);">평균 79.4점</span>
          </div>
          <div class="tfp-range-row">
            <div class="tfp-input-box">
              <input type="number" id="filter_total_min" class="tfp-num-input" placeholder="최소" min="0" max="100" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이상</span>
            </div>
            <span class="tfp-range-sep">~</span>
            <div class="tfp-input-box">
              <input type="number" id="filter_total_max" class="tfp-num-input" placeholder="최대" min="0" max="100" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이하</span>
            </div>
          </div>
          <div class="tfp-preset-row">
            <button class="tfp-preset-btn" onclick="setPreset('score_total', 85, null, this)">≥85 (최상위)</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_total', 80, null, this)">≥80</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_total', 75, null, this)">≥75</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_total', 80, 90, this)">80~90</button>
          </div>
        </div>

        <!-- 3. Taste Score -->
        <div class="tfp-card">
          <div class="tfp-card-header">
            <span>☕ 맛 점수 (50점)</span>
            <span style="font-size:10.5px; color:var(--accent-blue);">COE20+테루아15+평가15</span>
          </div>
          <div class="tfp-range-row">
            <div class="tfp-input-box">
              <input type="number" id="filter_taste_min" class="tfp-num-input" placeholder="최소" min="0" max="50" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이상</span>
            </div>
            <span class="tfp-range-sep">~</span>
            <div class="tfp-input-box">
              <input type="number" id="filter_taste_max" class="tfp-num-input" placeholder="최대" min="0" max="50" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이하</span>
            </div>
          </div>
          <div class="tfp-preset-row">
            <button class="tfp-preset-btn" onclick="setPreset('score_taste', 42, null, this)">≥42 (명품)</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_taste', 38, null, this)">≥38</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_taste', 35, null, this)">≥35</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_taste', 35, 45, this)">35~45</button>
          </div>
        </div>

        <!-- 4. Price Score (Value) -->
        <div class="tfp-card">
          <div class="tfp-card-header">
            <span>💰 가격/가성비 (30점)</span>
            <span style="font-size:10.5px; color:var(--accent-green);">저렴할수록 고득점</span>
          </div>
          <div class="tfp-range-row">
            <div class="tfp-input-box">
              <input type="number" id="filter_price_score_min" class="tfp-num-input" placeholder="최소" min="0" max="30" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이상</span>
            </div>
            <span class="tfp-range-sep">~</span>
            <div class="tfp-input-box">
              <input type="number" id="filter_price_score_max" class="tfp-num-input" placeholder="최대" min="0" max="30" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이하</span>
            </div>
          </div>
          <div class="tfp-preset-row">
            <button class="tfp-preset-btn" onclick="setPreset('score_price', 28, null, this)">≥28 (극가성비)</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_price', 25, null, this)">≥25</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_price', 20, null, this)">≥20</button>
          </div>
        </div>

        <!-- 5. Rarity Score -->
        <div class="tfp-card">
          <div class="tfp-card-header">
            <span>💎 희소성 (20점)</span>
            <span style="font-size:10.5px; color:#a855f7;">마이크로랏/게이샤</span>
          </div>
          <div class="tfp-range-row">
            <div class="tfp-input-box">
              <input type="number" id="filter_rarity_min" class="tfp-num-input" placeholder="최소" min="0" max="20" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이상</span>
            </div>
            <span class="tfp-range-sep">~</span>
            <div class="tfp-input-box">
              <input type="number" id="filter_rarity_max" class="tfp-num-input" placeholder="최대" min="0" max="20" step="1" oninput="applyRangeFilters()" onkeydown="if(event.key==='Enter') applyRangeFilters()">
              <span class="tfp-unit-tag">이하</span>
            </div>
          </div>
          <div class="tfp-preset-row">
            <button class="tfp-preset-btn" onclick="setPreset('score_rarity', 18, null, this)">≥18 (극희귀)</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_rarity', 15, null, this)">≥15</button>
            <button class="tfp-preset-btn" onclick="setPreset('score_rarity', 10, null, this)">≥10</button>
          </div>
        </div>

        <!-- 6. Cup Notes (Objective Multi-Select Presets & Subjective Free-Text Search) -->
        <div class="tfp-card" style="border-left: 3px solid var(--accent-gold);">
          <div class="tfp-card-header" style="display:flex; justify-content:space-between; align-items:center;">
            <span>🍒 컵노트 (객관식 다중선택 / 검색)</span>
            <div style="display:flex; align-items:center; gap:5px;">
              <button type="button" id="noteMatchModeBtn" onclick="toggleNoteMatchMode()" style="font-size:11px; font-weight:700; padding:2px 8px; height:22px; border-radius:12px; background:var(--card-bg); border:1px solid var(--accent-gold); color:var(--accent-gold); cursor:pointer;" title="다중 선택 시 매칭 모드 전환: OR(하나라도 포함) / AND(모두 포함)">
                조건: OR (하나라도) ↕
              </button>
            </div>
          </div>
          <div class="tfp-range-row">
            <div class="tfp-input-box" style="position:relative; width:100%;">
              <input type="text" id="filter_note_input" class="tfp-text-input" placeholder="직접 검색 (예: 복숭아, peach, 자스민, 딸기...)" oninput="applyNoteFilterInput()" onkeydown="if(event.key==='Enter') applyNoteFilterInput()">
              <button type="button" id="noteClearBtn" onclick="clearNoteInput()" style="display:none; position:absolute; right:6px; background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:13px; padding:0 4px;" title="지우기">✕</button>
            </div>
          </div>
          <div class="tfp-preset-row" id="notePresetRow" style="gap:5px; flex-wrap:wrap;">
            <button class="tfp-preset-btn" data-note="복숭아" onclick="toggleNotePreset('복숭아', this)">복숭아</button>
            <button class="tfp-preset-btn" data-note="자스민" onclick="toggleNotePreset('자스민', this)">자스민</button>
            <button class="tfp-preset-btn" data-note="베르가못" onclick="toggleNotePreset('베르가못', this)">베르가못</button>
            <button class="tfp-preset-btn" data-note="만다린" onclick="toggleNotePreset('만다린', this)">만다린</button>
            <button class="tfp-preset-btn" data-note="오렌지" onclick="toggleNotePreset('오렌지', this)">오렌지</button>
            <button class="tfp-preset-btn" data-note="파파야" onclick="toggleNotePreset('파파야', this)">파파야</button>
            <button class="tfp-preset-btn" data-note="망고" onclick="toggleNotePreset('망고', this)">망고</button>
            <button class="tfp-preset-btn" data-note="유자" onclick="toggleNotePreset('유자', this)">유자</button>
            <button class="tfp-preset-btn" data-note="플로럴" onclick="toggleNotePreset('플로럴', this)">플로럴</button>
            <button class="tfp-preset-btn" data-note="서양배" onclick="toggleNotePreset('서양배', this)">서양배</button>
            <button class="tfp-preset-btn" data-note="살구" onclick="toggleNotePreset('살구', this)">살구</button>
            <button class="tfp-preset-btn" data-note="초콜릿" onclick="toggleNotePreset('초콜릿', this)">초콜릿</button>
          </div>
        </div>

        <!-- 7. Processing Method (Objective Multiple-Choice Filter) -->
        <div class="tfp-card" style="border-left: 3px solid var(--accent-blue);">
          <div class="tfp-card-header">
            <span>⚙️ 가공 프로세스 (객관식)</span>
            <span style="font-size:10.5px; color:var(--accent-blue);">가공 방식 선택</span>
          </div>
          <div class="tfp-preset-row" id="tfpProcessBtnGroup" style="gap:5px; margin-top:2px;">
            <button class="tfp-preset-btn active" data-proc="all" onclick="setTfpProcessFilter('all', this)">전체</button>
            <button class="tfp-preset-btn" data-proc="Washed" onclick="setTfpProcessFilter('Washed', this)">워시드 (Washed)</button>
            <button class="tfp-preset-btn" data-proc="Natural" onclick="setTfpProcessFilter('Natural', this)">내추럴 (Natural)</button>
            <button class="tfp-preset-btn" data-proc="Anaerobic/Fermented" onclick="setTfpProcessFilter('Anaerobic/Fermented', this)">무산소/발효 (Anaerobic)</button>
            <button class="tfp-preset-btn" data-proc="Honey" onclick="setTfpProcessFilter('Honey', this)">허니 (Honey)</button>
            <button class="tfp-preset-btn" data-proc="Other" onclick="setTfpProcessFilter('Other', this)">기타 (Other)</button>
          </div>
        </div>
      </div>

      <!-- Panel Bottom Actions & Active Filter Badges -->
      <div class="tfp-bottom-bar">
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <span style="font-size:12px; font-weight:700; color:var(--text-secondary);">적용 조건:</span>
          <div class="tfp-active-tags" id="activeFilterTags">
            <span style="font-size:11.5px; color:var(--text-muted);">(조건 없음 - 전체 원두 표시 중)</span>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <button class="tfp-btn-apply" onclick="applyRangeFilters()">🔍 조건 필터 적용</button>
        </div>
      </div>
    </div>

    <div class="table-responsive">
      <table class="data-table" id="dataTable">
        <thead>
          <tr>
            <th onclick="sortTable('roastery')">로스터리 ↕</th>
            <th style="min-width:190px;">
              <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
                <span onclick="sortTable('title')" style="cursor:pointer;" title="원두명 정렬">원두명 ↕</span>
                <button type="button" id="todayFilterBtnAnalytics" class="th-today-filter-btn" onclick="toggleTodayNewFilter(event)" title="오늘(1008) 출시된 신규 원두(31종)만 보기 필터 토글">
                  ✨ 1008 신규만
                </button>
              </div>
            </th>
            <th onclick="sortTable('country')">원산지 ↕</th>
            <th onclick="sortTable('process')">프로세스 ↕</th>
            <th onclick="sortTable('price_100g_aed')">100g 가격 (AED) ↕</th>
            <th onclick="sortTable('score_taste')">맛(50) ↕</th>
            <th onclick="sortTable('score_price')">값(30) ↕</th>
            <th onclick="sortTable('score_rarity')">희(20) ↕</th>
            <th onclick="sortTable('score_total')">종합점수 ↕</th>
          </tr>
        </thead>
        <tbody id="tableBody">
          <!-- Populated by JS -->
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- CLUSTER MULTI-BEAN SELECTION MODAL -->
<div class="detail-overlay" id="clusterOverlay" onclick="closeClusterModal(event)">
  <div class="detail-modal" style="max-width: 520px;" onclick="event.stopPropagation()">
    <div class="modal-header">
      <div>
        <div class="detail-badge" style="color:var(--accent-gold); border-color:var(--accent-gold);">밀집 구간 원두 선택</div>
        <h2 class="detail-title" style="font-size:18px; margin-top:4px;" id="clusterTitle">선택 지점 원두 목록</h2>
      </div>
      <button class="modal-close-btn" onclick="closeClusterModal()">&times;</button>
    </div>
    <div class="modal-body" style="padding:16px;">
      <p style="font-size:12.5px; color:var(--text-secondary); margin-bottom:12px;">
        선택하신 지점에 여러 원두가 겹쳐 있습니다. 확인하실 원두를 선택해주세요:
      </p>
      <div id="clusterList" style="display:flex; flex-direction:column; gap:8px; max-height:380px; overflow-y:auto;">
        <!-- Populated by JS -->
      </div>
    </div>
  </div>
</div>

<!-- MOBILE 1-TAP PREVIEW CARD -->
<div id="mobilePreviewCard" class="mobile-preview-card" style="display:none;">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
    <div id="mpBadges" style="display:flex; gap:4px; flex-wrap:wrap;"></div>
    <button onclick="closeMobilePreview()" style="background:transparent; border:none; color:var(--text-muted); font-size:20px; line-height:1; cursor:pointer;">&times;</button>
  </div>
  <div id="mpTitle" style="font-size:15px; font-weight:800; color:var(--text-primary); margin-bottom:6px; line-height:1.3;"></div>
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; font-size:13px;">
    <span id="mpPrice" style="font-weight:700; color:var(--accent-gold); font-family:monospace;"></span>
    <span id="mpScore" style="font-weight:800; color:var(--text-primary);"></span>
  </div>
  <button id="mpDetailBtn" class="nav-btn" style="width:100%; justify-content:center; background:linear-gradient(135deg, #e3b341, #d97706); color:#000; font-weight:800; font-size:13px; border:none;">
    👉 터치하여 상세 스펙 전체보기
  </button>
</div>

<!-- COFFEE DETAIL MODAL -->
<div class="detail-overlay" id="detailOverlay" onclick="closeDetailModal(event)">
  <div class="detail-modal" onclick="event.stopPropagation()">
    <div class="modal-header">
      <div>
        <div class="detail-badges" id="modalBadges"></div>
        <h2 class="detail-title" id="modalTitle" style="margin-top:6px;"></h2>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <button id="modalStarBtnAnalyticsHeader" class="nav-btn modal-star-btn-sm" onclick="toggleCartFromModalAnalytics()" title="장바구니 담기 토글">⭐ 담기</button>
        <button class="modal-close-btn" onclick="closeDetailModal()">&times;</button>
      </div>
    </div>
    <div class="modal-body">
      <!-- SCORES -->
      <div class="detail-score-box">
        <div>
          <div class="score-unit-num" id="modalScoreTotal">0</div>
          <div class="score-unit-label">⭐ 종합점수</div>
        </div>
        <div>
          <div class="score-unit-num" id="modalScoreTaste" style="color:var(--accent-blue);">0</div>
          <div class="score-unit-label">☕ 맛 (50)</div>
        </div>
        <div>
          <div class="score-unit-num" id="modalScorePrice" style="color:var(--accent-green);">0</div>
          <div class="score-unit-label">💰 값 (30)</div>
        </div>
        <div>
          <div class="score-unit-num" id="modalScoreRarity" style="color:#a855f7;">0</div>
          <div class="score-unit-label">💎 희 (20)</div>
        </div>
      </div>

      <!-- TASTE BREAKDOWN (NEW 3 CRITERIA) -->
      <div>
        <div class="detail-section-title">맛 점수 3대 평가 상세 내역 (50점 만점)</div>
        <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:8px; padding:12px; font-size:12.5px; display:flex; flex-direction:column; gap:8px;">
          <div>
            <strong style="color:var(--accent-gold);">🏆 COE/BOP 입상급 성적 (20점):</strong> 
            <span id="modalAwardScore" style="font-weight:700;"></span>점 - <span id="modalAwardDesc" style="color:var(--text-secondary);"></span>
          </div>
          <div>
            <strong style="color:var(--accent-blue);">⛰️ 테루아 & 재배환경 (15점):</strong> 
            <span id="modalTerroirScore" style="font-weight:700;"></span>점 - <span id="modalTerroirDesc" style="color:var(--text-secondary);"></span>
          </div>
          <div>
            <strong style="color:var(--accent-green);">🌐 업계 & 리뷰어 긍정평가 (15점):</strong> 
            <span id="modalReviewScore" style="font-weight:700;"></span>점 - <span id="modalReviewDesc" style="color:var(--text-secondary);"></span>
          </div>
        </div>
      </div>

      <!-- SPECS GRID -->
      <div>
        <div class="detail-section-title">원두 스펙 및 테크니컬 데이터</div>
        <div class="detail-specs-grid">
          <div class="spec-row">
            <span class="spec-lbl">원산지 / 생산국</span>
            <span class="spec-val" id="modalCountry">-</span>
          </div>
          <div class="spec-row">
            <span class="spec-lbl">지역 / 농장 / 생산자</span>
            <span class="spec-val" id="modalFarm">-</span>
          </div>
          <div class="spec-row">
            <span class="spec-lbl">품종 (Variety)</span>
            <span class="spec-val" id="modalVariety">-</span>
          </div>
          <div class="spec-row">
            <span class="spec-lbl">프로세싱 (Process)</span>
            <span class="spec-val" id="modalProcess">-</span>
          </div>
          <div class="spec-row">
            <span class="spec-lbl">고도 (Altitude)</span>
            <span class="spec-val" id="modalAltitude">-</span>
          </div>
          <div class="spec-row">
            <span class="spec-lbl">100g당 가격 (AED / KRW)</span>
            <span class="spec-val" id="modalPrice100g">-</span>
          </div>
        </div>
      </div>

      <!-- TASTING NOTES -->
      <div>
        <div class="detail-section-title">컵노트 (Flavor Notes)</div>
        <div class="notes-tag-list" id="modalNotesList"></div>
      </div>

      <!-- MERIT & KOREA STATUS -->
      <div>
        <div class="detail-section-title">현지 구매 가치 및 국내 유통 현황</div>
        <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:8px; padding:12px; font-size:12.5px; line-height:1.5;">
          <div style="margin-bottom:6px;"><strong>국내 수입 상태:</strong> <span id="modalKoreaStatus"></span> (<span id="modalKoreaSeller"></span>, <span id="modalKoreaPrice"></span>)</div>
          <div><strong>구매 메리트:</strong> <span id="modalMerit" style="color:var(--text-secondary);"></span></div>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button id="modalStarBtnAnalytics" class="nav-btn modal-star-btn" onclick="toggleCartFromModalAnalytics()">⭐ 장바구니 담기</button>
      <a id="modalSourceBtn" href="#" target="_blank" class="nav-btn" style="border-color:var(--accent-gold); color:var(--accent-gold);">공식 사이트 원문 보기 ↗</a>
      <button class="nav-btn" onclick="closeDetailModal()">닫기</button>
    </div>
  </div>
</div>

<script>
  // 1. DATASETS
  const ALL_COFFEES = {items_json};
  const STATS = {stats_json};

  // State
  let currentYMetric = 'total'; // 'total', 'taste', 'rarity', 'price'
  let currentShapeMode = 'default'; // 'default', 'country', 'process', 'altitude'
  let currentOriginFilter = 'all'; // 'all', 'Ethiopia', 'Panama', 'Colombia', 'Other'
  let currentProcessFilter = 'all'; // 'all', 'Washed', 'Natural', 'Anaerobic/Fermented', 'Honey'
  let activeGroups = new Set(['competition', 'reserve', 'selection', 'esolab']);
  let searchQuery = '';
  let selectedCoffeeId = null;
  let mobilePreviewCoffeeId = null;
  let highlightedNote = null;
  let noteFilterQuery = ''; // Subjective free-text cup note filter
  let selectedPresetNotes = new Set(); // Multi-select objective cup note presets
  let noteMatchMode = 'or'; // 'or' (at least one) | 'and' (must match all)
  let syncPriceWithCharts = true; // whether to sync range filters with charts
  let sortKey = 'score_total';
  let sortAsc = false;

  // Korean to English cup note synonym mapping
  const KR_NOTE_MAP = {{
    '복숭아': ['peach'], '피치': ['peach'], '백도': ['white peach', 'peach'], '황도': ['yellow peach', 'peach'],
    '자스민': ['jasmine'], '재스민': ['jasmine'],
    '베르가못': ['bergamot'], '베르가모트': ['bergamot'],
    '만다린': ['mandarin', 'mandarine'], '오렌지': ['orange'], '감귤': ['mandarin', 'citrus'], '귤': ['mandarin', 'citrus'],
    '유자': ['yuzu'], '레몬': ['lemon'], '라임': ['lime'], '시트러스': ['citrus'],
    '플로럴': ['floral', 'flower', 'blossom'], '꽃': ['floral', 'flower', 'blossom'], '블라썸': ['blossom'],
    '파파야': ['papaya'], '망고': ['mango'], '패션후르츠': ['passion fruit', 'passionfruit'], '리치': ['lychee'],
    '딸기': ['strawberry'], '스트로베리': ['strawberry'], '블루베리': ['blueberry'], '라즈베리': ['raspberry'], '베리': ['berry'],
    '포도': ['grape', 'grapes'], '청포도': ['white grape', 'white grapes'], '와인': ['wine'],
    '서양배': ['pear'], '배': ['pear'], '사과': ['apple'], '살구': ['apricot'], '자두': ['plum'], '체리': ['cherry'],
    '꿀': ['honey'], '허니': ['honey'], '사탕수수': ['sugarcane', 'sugar cane'],
    '초콜릿': ['chocolate', 'cacao', 'cocoa'], '초콜렛': ['chocolate', 'cacao', 'cocoa'], '카카오': ['cacao', 'chocolate'],
    '카라멜': ['caramel', 'toffee'], '캐러멜': ['caramel', 'toffee'], '바닐라': ['vanilla'],
    '아몬드': ['almond', 'nut'], '견과류': ['nut', 'almond', 'hazelnut'],
    '얼그레이': ['earl grey', 'tea'], '홍차': ['black tea', 'tea'], '녹차': ['green tea', 'tea'],
    '열대과일': ['tropical', 'mango', 'papaya', 'passion fruit', 'guava']
  }};

  function checkCoffeeMatchesNote(c, query) {{
    if (!query) return true;
    const q = query.toLowerCase().trim();
    if (!q) return true;
    const directText = (c.tasting_notes + ' ' + c.notes_list.join(' ') + ' ' + (c.search_kr || '')).toLowerCase();
    if (directText.includes(q)) return true;
    for (const [krWord, enEquivs] of Object.entries(KR_NOTE_MAP)) {{
      if (q.includes(krWord) || krWord.includes(q)) {{
        if (enEquivs.some(en => directText.includes(en))) return true;
      }}
    }}
    return false;
  }}

  // Multi-cup-note matcher combining objective presets (OR / AND) and subjective text input
  function checkCoffeeMatchesActiveNotes(c) {{
    // 1. Objective multi-selected presets
    if (selectedPresetNotes.size > 0) {{
      const presets = Array.from(selectedPresetNotes);
      if (noteMatchMode === 'and') {{
        const allMatch = presets.every(n => checkCoffeeMatchesNote(c, n));
        if (!allMatch) return false;
      }} else {{
        const anyMatch = presets.some(n => checkCoffeeMatchesNote(c, n));
        if (!anyMatch) return false;
      }}
    }}
    // 2. Subjective direct text search input
    if (noteFilterQuery) {{
      if (!checkCoffeeMatchesNote(c, noteFilterQuery)) return false;
    }}
    return true;
  }}

  function formatNotesHighlight(notesStr) {{
    if (!notesStr) return '-';
    try {{
      const activeQueries = [];
      if (noteFilterQuery) activeQueries.push(noteFilterQuery.trim().toLowerCase());
      selectedPresetNotes.forEach(n => activeQueries.push(n.trim().toLowerCase()));
      if (activeQueries.length === 0) return notesStr;

      let words = [];
      activeQueries.forEach(q => {{
        if (!q) return;
        words.push(q);
        for (const [krWord, enList] of Object.entries(KR_NOTE_MAP)) {{
          if (q.includes(krWord) || krWord.includes(q)) {{
            words.push(...enList);
          }}
        }}
      }});

      words = Array.from(new Set(words)).filter(w => w && w.length >= 2).sort((a, b) => b.length - a.length);
      if (words.length === 0) return notesStr;

      const escaped = words.map(w => w.split('').map(ch => ('-/^$*+?.()|[]{{}}'.includes(ch) ? '\\\\' + ch : ch)).join('')).join('|');
      const regex = new RegExp('(' + escaped + ')', 'gi');
      return notesStr.replace(regex, '<mark style="background:var(--accent-gold-bg); color:var(--accent-gold); padding:0 3px; border-radius:3px; font-weight:700;">$1</mark>');
    }} catch(e) {{
      return notesStr;
    }}
  }}

  // Multi-Metric Range Filters State (min / max)
  let rangeFilters = {{
    price_100g_aed: {{ min: null, max: null }},
    score_total:    {{ min: null, max: null }},
    score_taste:    {{ min: null, max: null }},
    score_price:    {{ min: null, max: null }},
    score_rarity:   {{ min: null, max: null }}
  }};

  // Helper: check if a coffee item matches all active range filters
  function matchesRangeFilters(c) {{
    for (const [key, range] of Object.entries(rangeFilters)) {{
      const val = c[key];
      if (val === undefined || val === null) continue;
      if (range.min !== null && val < range.min) return false;
      if (range.max !== null && val > range.max) return false;
    }}
    return true;
  }}

  // Chart references
  let scatterChart = null;
  let notesChart = null;

  // Base Top notes vocabulary
  const TOP_NOTES_VOCAB = [
    'peach', 'lychee', 'mandarine', 'white grapes', 'pear', 'papaya',
    'jasmine', 'apricot', 'mango', 'yuzu', 'honey', 'nectarine',
    'cantaloupe', 'strawberry', 'bergamot', 'earl grey', 'blueberry', 'sugarcane'
  ];

  // Point Style Mappers
  function getPointStyle(c, mode) {{
    if (mode === 'country') {{
      if (c.country_cat === 'Ethiopia') return 'circle';
      if (c.country_cat === 'Panama') return 'triangle';
      if (c.country_cat === 'Colombia') return 'rect';
      return 'star';
    }}
    if (mode === 'process') {{
      if (c.process_cat === 'Washed') return 'circle';
      if (c.process_cat === 'Natural') return 'triangle';
      if (c.process_cat === 'Anaerobic/Fermented') return 'rectRot';
      if (c.process_cat === 'Honey') return 'rect';
      return 'star';
    }}
    if (mode === 'altitude') {{
      if (c.alt_num >= 2000) return 'star';
      if (c.alt_num >= 1800) return 'triangle';
      if (c.alt_num >= 1600) return 'circle';
      return 'rect';
    }}
    return 'circle';
  }}

  // Filtered dataset
  function getFilteredCoffees() {{
    return ALL_COFFEES.filter(c => {{
      // 1. Group filter
      if (!activeGroups.has(c.group_key)) return false;

      // 2. Origin quick filter
      if (currentOriginFilter !== 'all') {{
        if (c.country_cat !== currentOriginFilter) return false;
      }}

      // 3. Process quick filter
      if (currentProcessFilter !== 'all') {{
        if (c.process_cat !== currentProcessFilter) return false;
      }}

      // 4. Search query (supports Korean & English)
      if (searchQuery) {{
        const q = searchQuery.toLowerCase();
        const text = (c.title + ' ' + c.country + ' ' + c.farm + ' ' + c.producer + ' ' + c.process + ' ' + c.variety + ' ' + c.tasting_notes + ' ' + (c.search_kr || '')).toLowerCase();
        if (!text.includes(q)) return false;
      }}

      // 5. Today new filter
      if (filterOnlyTodayNew) {{
        if (!c.is_today_new) return false;
      }}

      // 5. Note cross-filtering
      if (highlightedNote) {{
        const hasNote = c.notes_list.some(n => n.includes(highlightedNote));
        if (!hasNote) return false;
      }}

      // 6. Multi-Metric Range Filters (applied to dataset when chart sync is active)
      if (syncPriceWithCharts && !matchesRangeFilters(c)) {{
        return false;
      }}

      // 7. Cup note multi-presets & search filter (applied to dataset when chart sync is active)
      if (syncPriceWithCharts && !checkCoffeeMatchesActiveNotes(c)) {{
        return false;
      }}

      return true;
    }});
  }}

  // Scale bounds: FIXED globally to represent all 171 beans consistently
  function getYScaleLimits() {{
    if (currentYMetric === 'taste') return {{ min: 20, max: 50 }};
    if (currentYMetric === 'price') return {{ min: 0, max: 30 }};
    if (currentYMetric === 'rarity') return {{ min: 0, max: 20 }};
    return {{ min: 50, max: 100 }}; // total score
  }}

  // Initialize Scatter Chart
  function initScatterChart() {{
    const ctx = document.getElementById('scatterChart').getContext('2d');
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const yLimits = getYScaleLimits();

    scatterChart = new Chart(ctx, {{
      type: 'scatter',
      data: {{ datasets: buildScatterDatasets() }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        animation: {{ duration: 250 }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            enabled: true,
            backgroundColor: isDark ? 'rgba(22, 27, 34, 0.96)' : 'rgba(255, 255, 255, 0.98)',
            titleColor: isDark ? '#f0f6fc' : '#1f2328',
            bodyColor: isDark ? '#8b949e' : '#57606a',
            borderColor: isDark ? '#30363d' : '#d0d7de',
            borderWidth: 1,
            padding: 10,
            caretPadding: 35, // Generous offset away from pointer to avoid covering dots
            caretSize: 8,
            xAlign: 'center',
            yAlign: 'bottom',
            titleFont: {{ size: 12.5, weight: 'bold' }},
            bodyFont: {{ size: 11.5, lineHeight: 1.4 }},
            callbacks: {{
              // Pure text output only - NO DOM MANIPULATION HERE TO PREVENT RESIZE LOOPS
              label: function(ctx) {{
                const raw = ctx.raw;
                const c = raw.coffee;
                return [
                  `☕ [${{c.roastery}}] ${{c.title}}${{c.is_today_new ? ' [NEW ' + (c.release_date || '1008') + ']' : ''}}`,
                  `💰 100g: ${{c.price_100g_aed}} AED (~${{c.price_100g_krw.toLocaleString()}}원)`,
                  `⭐ 종합: ${{c.score_total}}점 (맛 ${{c.score_taste}} / 값 ${{c.score_price}} / 희 ${{c.score_rarity}})`,
                  `🌍 ${{c.country}} | 가공: ${{c.process}}`,
                  `👉 클릭 시 상세/목록 확인`
                ];
              }}
            }}
          }},
          zoom: {{
            pan: {{
              enabled: true,
              mode: 'xy',
              modifierKey: null
            }},
            zoom: {{
              wheel: {{
                enabled: true,
                speed: 0.08
              }},
              pinch: {{
                enabled: true
              }},
              mode: 'xy'
            }}
          }}
        }},
        scales: {{
          x: {{
            min: 0,
            max: 1150, // Fixed baseline representation for 171 beans
            title: {{
              display: true,
              text: '100g당 가격 (AED) - [X축 위에서 휠 스크롤 시 가격 확대/축소]',
              color: isDark ? '#8b949e' : '#57606a',
              font: {{ weight: 'bold', size: 11.5 }}
            }},
            grid: {{ color: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }},
            ticks: {{ color: isDark ? '#8b949e' : '#57606a' }}
          }},
          y: {{
            min: yLimits.min,
            max: yLimits.max,
            title: {{
              display: true,
              text: getYAxisLabel() + ' - [Y축 위에서 휠 스크롤 시 점수 확대/축소]',
              color: isDark ? '#8b949e' : '#57606a',
              font: {{ weight: 'bold', size: 11.5 }}
            }},
            grid: {{ color: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }},
            ticks: {{ color: isDark ? '#8b949e' : '#57606a' }}
          }}
        }},
        onHover: (evt, activeEls) => {{
          // Safely update HUD outside of the tooltip rendering cycle
          if (activeEls.length > 0) {{
            const el = activeEls[0];
            const pt = scatterChart.data.datasets[el.datasetIndex]?.data[el.index];
            if (pt && pt.coffee) {{
              updateHudBar(pt.coffee);
            }}
          }} else {{
            resetHudBar();
          }}
        }},
        onClick: (evt, activeEls) => {{
          handleScatterClick(evt);
        }}
      }}
    }});

    // AXIS-ONLY WHEEL ZOOM INTERCEPTOR:
    // Prevents zooming when scrolling on the center plot area so normal page scrolling works smoothly!
    const canvasEl = document.getElementById('scatterChart');
    canvasEl.addEventListener('wheel', function(e) {{
      if (!scatterChart) return;
      const rect = canvasEl.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      const area = scatterChart.chartArea;
      if (!area) return;

      // Check if mouse is inside the center data plotting area
      const isInsidePlotArea = (mouseX >= area.left && mouseX <= area.right && mouseY >= area.top && mouseY <= area.bottom);

      if (isInsidePlotArea) {{
        // Stop zoom plugin from intercepting wheel events in the center of the graph
        // This lets the browser perform normal page vertical scrolling!
        e.stopImmediatePropagation();
        return;
      }}
      // If mouse is on X-axis (below area.bottom) or Y-axis (left of area.left), zoom proceeds normally!
    }}, {{ capture: true, passive: false }});
  }}

  // HUD Bar Real-time update
  function updateHudBar(c) {{
    const idle = document.getElementById('hudIdleText');
    const active = document.getElementById('hudActiveText');
    if (!idle || !active) return;
    idle.style.display = 'none';
    active.style.display = 'flex';
    active.innerHTML = `
      <span style="color:${{c.color}}; font-weight:800; white-space:nowrap;">[${{c.roastery}}]</span>
      <span style="font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:260px;" class="${{c.is_today_new ? 'today-new-coffee-title' : ''}}">${{c.title}}${{c.is_today_new ? '<span class=\"badge-new-date\">' + (c.release_date || '1008') + '</span>' : ''}}</span>
      <span style="color:var(--text-muted);">|</span>
      <span style="font-family:monospace; color:var(--accent-gold); font-weight:700; white-space:nowrap;">${{c.price_100g_aed}} AED (~${{c.price_100g_krw.toLocaleString()}}원)</span>
      <span style="color:var(--text-muted);">|</span>
      <span style="font-weight:800; color:var(--accent-gold); white-space:nowrap;">⭐ ${{c.score_total}}점</span>
      <span style="font-size:11.5px; color:var(--text-secondary); white-space:nowrap;">(맛${{c.score_taste}}/값${{c.score_price}}/희${{c.score_rarity}})</span>
      <span style="color:var(--text-muted);">|</span>
      <span style="font-size:12px; color:var(--text-secondary); white-space:nowrap;">${{c.country}} (${{c.process}})</span>
    `;
  }}

  function resetHudBar() {{
    const idle = document.getElementById('hudIdleText');
    const active = document.getElementById('hudActiveText');
    if (!idle || !active) return;
    idle.style.display = 'flex';
    active.style.display = 'none';
  }}

  // Handle Scatter Click: Handles multi-dot clusters and mobile 2-stage interaction
  function handleScatterClick(evt) {{
    const rect = scatterChart.canvas.getBoundingClientRect();
    const clickX = evt.x !== undefined ? evt.x : (evt.native ? evt.native.clientX - rect.left : 0);
    const clickY = evt.y !== undefined ? evt.y : (evt.native ? evt.native.clientY - rect.top : 0);

    // Find all beans within 18px radius on canvas
    const nearby = [];
    scatterChart.data.datasets.forEach((ds, dsIdx) => {{
      const meta = scatterChart.getDatasetMeta(dsIdx);
      if (!meta.hidden) {{
        meta.data.forEach((element, idx) => {{
          const dist = Math.hypot(element.x - clickX, element.y - clickY);
          if (dist <= 18) {{
            nearby.push(ds.data[idx].coffee);
          }}
        }});
      }}
    }});

    if (nearby.length === 0) return;

    if (nearby.length > 1) {{
      // Multiple beans in dense cluster: open multi-select cluster modal
      openClusterModal(nearby);
      return;
    }}

    // Exactly 1 bean clicked
    const singleCoffee = nearby[0];
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {{
      // Mobile 2-stage tap flow:
      if (mobilePreviewCoffeeId === singleCoffee.id) {{
        // Second tap on the same bean: open full modal!
        closeMobilePreview();
        openDetailModal(singleCoffee);
      }} else {{
        // First tap: show preview card
        showMobilePreview(singleCoffee);
      }}
    }} else {{
      // Desktop: directly open detail modal
      openDetailModal(singleCoffee);
    }}
  }}

  // Multi-item cluster modal
  function openClusterModal(coffeeList) {{
    document.getElementById('clusterTitle').textContent = `선택 지점 원두 (${{coffeeList.length}}종)`;
    const listEl = document.getElementById('clusterList');
    listEl.innerHTML = coffeeList.map(c => `
      <div class="cluster-item-card" onclick="openDetailFromCluster('${{c.id}}')">
        <div style="flex:1;">
          <div style="display:flex; gap:6px; align-items:center; margin-bottom:4px;">
            <span class="detail-badge" style="color:${{c.color}}; border-color:${{c.color}}; font-weight:800;">${{c.roastery}}</span>
            <span class="detail-badge">${{c.country}}</span>
            <span class="detail-badge">${{c.process}}</span>
          </div>
          <div style="font-weight:700; font-size:13.5px; line-height:1.3;" class="${{c.is_today_new ? 'today-new-coffee-title' : ''}}">${{c.title}}${{c.is_today_new ? '<span class="badge-new-date">' + (c.release_date || '1008') + '</span>' : ''}}</div>
        </div>
        <div style="text-align:right; white-space:nowrap;">
          <div style="font-weight:800; font-size:15px; color:var(--accent-gold); font-family:monospace;">⭐ ${{c.score_total}}점</div>
          <div style="font-size:12px; color:var(--text-muted); font-family:monospace;">${{c.price_100g_aed}} AED</div>
          <div style="font-size:11px; color:var(--accent-blue); font-weight:700; margin-top:2px;">상세보기 ➔</div>
        </div>
      </div>
    `).join('');

    document.getElementById('clusterOverlay').classList.add('active');
  }}

  function closeClusterModal() {{
    document.getElementById('clusterOverlay').classList.remove('active');
  }}

  function openDetailFromCluster(coffeeId) {{
    closeClusterModal();
    const c = ALL_COFFEES.find(x => x.id === coffeeId);
    if (c) openDetailModal(c);
  }}

  // Mobile 1-Tap Preview Sheet
  function showMobilePreview(c) {{
    mobilePreviewCoffeeId = c.id;
    selectedCoffeeId = c.id;
    updateNotesChart();

    const card = document.getElementById('mobilePreviewCard');
    document.getElementById('mpBadges').innerHTML = `
      <span class="detail-badge" style="color:${{c.color}}; border-color:${{c.color}}; font-weight:800;">${{c.roastery}}</span>
      <span class="detail-badge">${{c.country}}</span>
      <span class="detail-badge">${{c.process}}</span>
    `;
    if (c.is_today_new) {{
      document.getElementById('mpTitle').innerHTML = `<span class="today-new-coffee-title">${{c.title}}</span><span class="badge-new-date">${{c.release_date || '1008'}}</span>`;
    }} else {{
      document.getElementById('mpTitle').textContent = c.title;
    }}
    document.getElementById('mpPrice').textContent = `💰 100g: ${{c.price_100g_aed}} AED (~${{c.price_100g_krw.toLocaleString()}}원)`;
    document.getElementById('mpScore').textContent = `⭐ ${{c.score_total}}점 (맛${{c.score_taste}}/값${{c.score_price}}/희${{c.score_rarity}})`;

    const btn = document.getElementById('mpDetailBtn');
    btn.onclick = () => {{
      closeMobilePreview();
      openDetailModal(c);
    }};

    card.style.display = 'block';
  }}

  function closeMobilePreview() {{
    const card = document.getElementById('mobilePreviewCard');
    if (card) card.style.display = 'none';
    mobilePreviewCoffeeId = null;
  }}

  // Reset Zoom & Fit to size
  function resetScatterZoom() {{
    if (scatterChart) {{
      scatterChart.resetZoom();
      const yLimits = getYScaleLimits();
      scatterChart.options.scales.x.min = 0;
      scatterChart.options.scales.x.max = 1150;
      scatterChart.options.scales.y.min = yLimits.min;
      scatterChart.options.scales.y.max = yLimits.max;
      scatterChart.update();
    }}
  }}

  function getYAxisLabel() {{
    if (currentYMetric === 'taste') return '맛 점수 (50점 만점: COE 20 + 테루아 15 + 업계평가 15)';
    if (currentYMetric === 'price') return '가격 점수 (30점 만점)';
    if (currentYMetric === 'rarity') return '희소성 점수 (20점 만점)';
    return '종합 점수 (100점 만점)';
  }}

  function buildScatterDatasets() {{
    const filtered = getFilteredCoffees();
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';

    const groups = [
      {{ key: 'competition', name: '아처스 컴피티션', color: isDark ? '#f3f4f6' : '#111827', border: '#111827' }},
      {{ key: 'reserve', name: '아처스 리저브', color: '#2563eb', border: '#1d4ed8' }},
      {{ key: 'selection', name: '아처스 셀렉션', color: '#d97706', border: '#b45309' }},
      {{ key: 'esolab', name: '더 에스프레소 랩', color: '#dc2626', border: '#b91c1c' }}
    ];

    return groups.map(g => {{
      const items = filtered.filter(c => c.group_key === g.key);
      const data = items.map(c => {{
        let yVal = c.score_total;
        if (currentYMetric === 'taste') yVal = c.score_taste;
        if (currentYMetric === 'price') yVal = c.score_price;
        if (currentYMetric === 'rarity') yVal = c.score_rarity;

        return {{
          x: c.price_100g_aed,
          y: yVal,
          coffee: c
        }};
      }});

      const pointStyles = items.map(c => getPointStyle(c, currentShapeMode));
      const pointRadii = items.map(c => (selectedCoffeeId === c.id ? 8.5 : 4.5));

      return {{
        label: g.name,
        data: data,
        pointStyle: pointStyles,
        pointRadius: pointRadii,
        pointHoverRadius: 7.5,
        backgroundColor: g.key === 'competition' ? (isDark ? '#e2e8f0' : '#1f242d') : g.color,
        borderColor: g.key === 'competition' ? (isDark ? '#388bfd' : '#000000') : g.border,
        borderWidth: 1.2
      }};
    }});
  }}

  // Initialize & Update Notes Chart
  function initNotesChart() {{
    const ctx = document.getElementById('notesChart').getContext('2d');
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const notesData = getDynamicNotesData();

    notesChart = new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels: notesData.labels,
        datasets: [{{
          label: '출현 빈도',
          data: notesData.counts,
          backgroundColor: notesData.colors,
          borderColor: isDark ? '#388bfd' : '#0969da',
          borderWidth: 1,
          borderRadius: 4
        }}]
      }},
      options: {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        animation: {{ duration: 250 }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: ctx => `${{ctx.raw}}개 원두에서 식별됨 (클릭 시 크로스 필터)`
            }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }},
            ticks: {{ color: isDark ? '#8b949e' : '#57606a', stepSize: 1 }}
          }},
          y: {{
            grid: {{ display: false }},
            ticks: {{ color: isDark ? '#f0f6fc' : '#1f2328', font: {{ weight: '600', size: 11 }} }}
          }}
        }},
        onClick: (evt, activeEls) => {{
          if (activeEls.length > 0) {{
            const idx = activeEls[0].index;
            const clickedNote = notesChart.data.labels[idx].toLowerCase();
            toggleNoteFilter(clickedNote);
          }}
        }}
      }}
    }});
  }}

  // Calculate dynamic notes frequency based on currently filtered coffees
  function getDynamicNotesData() {{
    const filtered = getFilteredCoffees();
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const selCoffee = ALL_COFFEES.find(c => c.id === selectedCoffeeId);

    const noteCountMap = {{}};
    TOP_NOTES_VOCAB.forEach(n => {{ noteCountMap[n] = 0; }});

    filtered.forEach(c => {{
      TOP_NOTES_VOCAB.forEach(note => {{
        if (c.notes_list.some(n => n.includes(note))) {{
          noteCountMap[note] = (noteCountMap[note] || 0) + 1;
        }}
      }});
    }});

    const sorted = Object.entries(noteCountMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 14);

    const labels = sorted.map(([k]) => k.charAt(0).toUpperCase() + k.slice(1));
    const counts = sorted.map(([, v]) => v);
    const colors = sorted.map(([k]) => {{
      if (highlightedNote === k) return '#f59e0b'; // Gold selected
      if (selCoffee && selCoffee.notes_list.some(n => n.includes(k))) return 'rgba(227, 179, 65, 0.95)';
      return isDark ? 'rgba(56, 139, 253, 0.45)' : 'rgba(9, 105, 218, 0.45)';
    }});

    return {{ labels, counts, colors, totalFiltered: filtered.length }};
  }}

  function updateNotesChart() {{
    if (!notesChart) return;
    const data = getDynamicNotesData();
    notesChart.data.labels = data.labels;
    notesChart.data.datasets[0].data = data.counts;
    notesChart.data.datasets[0].backgroundColor = data.colors;
    notesChart.update();

    const sub = document.getElementById('notesChartSubtitle');
    if (sub) {{
      let filterDesc = [];
      if (currentOriginFilter !== 'all') filterDesc.push(`원산지:${{currentOriginFilter}}`);
      if (currentProcessFilter !== 'all') filterDesc.push(`가공:${{currentProcessFilter}}`);
      if (selectedPresetNotes.size > 0) {{
        filterDesc.push(`선택노트:${{Array.from(selectedPresetNotes).join(',')}}(${{noteMatchMode.toUpperCase()}})`);
      }}
      if (noteFilterQuery) filterDesc.push(`노트검색:'${{noteFilterQuery}}'`);
      if (syncPriceWithCharts) {{
        const activeCount = Object.values(rangeFilters).filter(r => r.min !== null || r.max !== null).length;
        if (activeCount > 0) filterDesc.push(`수치필터 ${{activeCount}}개 적용`);
      }}
      if (searchQuery) filterDesc.push(`검색:'${{searchQuery}}'`);
      const extra = filterDesc.length > 0 ? ` (${{filterDesc.join(', ')}} 적용)` : '';
      sub.textContent = `현재 필터링된 원두 ${{data.totalFiltered}}종 기준 컵노트 출현 빈도${{extra}} (바 클릭 시 크로스 필터링)`;
    }}
  }}

  function toggleNoteFilter(note) {{
    if (highlightedNote === note) {{
      highlightedNote = null;
    }} else {{
      highlightedNote = note;
    }}
    updateAll();
  }}

  // Update Dynamic Shape Legend
  function updateShapeLegend() {{
    const bar = document.getElementById('shapeLegendBar');
    if (currentShapeMode === 'country') {{
      bar.innerHTML = `
        <span style="font-weight:700; color:var(--accent-gold);">원산지별 심볼:</span>
        <span class="shape-item">● 에티오피아 (원형)</span>
        <span class="shape-item">▲ 파나마 (삼각형)</span>
        <span class="shape-item">■ 콜롬비아 (사각형)</span>
        <span class="shape-item">★ 코스타리카 / 기타 (별형)</span>
      `;
    }} else if (currentShapeMode === 'process') {{
      bar.innerHTML = `
        <span style="font-weight:700; color:var(--accent-gold);">프로세스별 심볼:</span>
        <span class="shape-item">● Washed (원형)</span>
        <span class="shape-item">▲ Natural (삼각형)</span>
        <span class="shape-item">◆ Anaerobic/Fermented (다이아몬드)</span>
        <span class="shape-item">■ Honey (사각형)</span>
        <span class="shape-item">★ 기타 실험가공 (별형)</span>
      `;
    }} else if (currentShapeMode === 'altitude') {{
      bar.innerHTML = `
        <span style="font-weight:700; color:var(--accent-gold);">고도별 심볼:</span>
        <span class="shape-item">★ 2,000m 이상 (초고도)</span>
        <span class="shape-item">▲ 1,800 ~ 1,999m (고고도)</span>
        <span class="shape-item">● 1,600 ~ 1,799m (중고도)</span>
        <span class="shape-item">■ 1,600m 미만</span>
      `;
    }} else {{
      bar.innerHTML = `
        <span style="font-weight:700; color:var(--accent-gold);">심볼 안내:</span>
        <span class="shape-item">● 전체 원두 (원형)</span>
        <span style="color:var(--text-muted); font-size:11.5px; margin-left:8px;">* 상단 버튼으로 원산지/프로세스/고도별 심볼 구분을 활성화할 수 있습니다.</span>
      `;
    }}
  }}

  // Render Data Table
  let filterOnlyTodayNew = false;

  function toggleTodayNewFilter(e) {{
    if (e) e.stopPropagation();
    filterOnlyTodayNew = !filterOnlyTodayNew;
    const btn = document.getElementById('todayFilterBtnAnalytics');
    if (btn) {{
      if (filterOnlyTodayNew) {{
        btn.classList.add('active');
        btn.innerHTML = '✨ 1008 신규 (31종 ON)';
      }} else {{
        btn.classList.remove('active');
        btn.innerHTML = '✨ 1008 신규만';
      }}
    }}
    renderTable();
    if (typeof updateCharts === 'function') {{
      updateCharts();
    }}
  }}

  function renderTable() {{
    let filtered = getFilteredCoffees();

    // If charts sync is OFF but range filters or note filter are active, filter table only
    if (!syncPriceWithCharts) {{
      filtered = filtered.filter(c => matchesRangeFilters(c));
      filtered = filtered.filter(c => checkCoffeeMatchesActiveNotes(c));
    }}

    const sorted = [...filtered].sort((a, b) => {{
      let valA = a[sortKey];
      let valB = b[sortKey];
      if (typeof valA === 'string') {{
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }}
      return sortAsc ? valA - valB : valB - valA;
    }});

    const hasPriceF = rangeFilters.price_100g_aed.min !== null || rangeFilters.price_100g_aed.max !== null;
    const hasTasteF = rangeFilters.score_taste.min !== null || rangeFilters.score_taste.max !== null;
    const hasPriceScoreF = rangeFilters.score_price.min !== null || rangeFilters.score_price.max !== null;
    const hasRarityF = rangeFilters.score_rarity.min !== null || rangeFilters.score_rarity.max !== null;
    const hasTotalF = rangeFilters.score_total.min !== null || rangeFilters.score_total.max !== null;

    const tbody = document.getElementById('tableBody');
    if (sorted.length === 0) {{
      tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:36px 16px; color:var(--text-muted); font-size:13.5px;">🔍 지정한 조건에 일치하는 원두가 없습니다. 필터 범위를 조정해 보세요.</td></tr>`;
    }} else {{
      tbody.innerHTML = sorted.map(c => `
        <tr onclick="openDetailModalById('${{c.id}}')">
          <td><strong style="color:${{c.color}};">${{c.roastery}}</strong></td>
          <td>
            <strong style="word-break:keep-all;" class="${{c.is_today_new ? 'today-new-coffee-title' : ''}}">${{c.title}}</strong>${{c.is_today_new ? '<span class=\"badge-new-date\">' + (c.release_date || '1008') + '</span>' : ''}}
            <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">✨ ${{formatNotesHighlight(c.tasting_notes)}}</div>
          </td>
          <td>${{c.country}}</td>
          <td><span style="font-size:11.5px; font-weight:600; ${{currentProcessFilter !== 'all' ? 'color:var(--accent-blue); font-weight:800;' : ''}}">${{c.process}}</span></td>
          <td style="font-family:monospace; ${{hasPriceF ? 'color:var(--accent-gold); font-weight:800;' : 'font-weight:700;'}}">${{c.price_100g_aed}} AED</td>
          <td style="font-family:monospace; color:var(--accent-blue); ${{hasTasteF ? 'font-weight:800; text-decoration:underline;' : ''}}">${{c.score_taste}}</td>
          <td style="font-family:monospace; color:var(--accent-green); ${{hasPriceScoreF ? 'font-weight:800; text-decoration:underline;' : ''}}">${{c.score_price}}</td>
          <td style="font-family:monospace; color:#a855f7; ${{hasRarityF ? 'font-weight:800; text-decoration:underline;' : ''}}">${{c.score_rarity}}</td>
          <td style="font-family:monospace; color:var(--accent-gold); ${{hasTotalF ? 'font-size:14px; font-weight:900;' : 'font-weight:800;'}}">${{c.score_total}}</td>
        </tr>
      `).join('');
    }}

    document.getElementById('tableCountDisplay').textContent = sorted.length;
    document.getElementById('pointCountDisplay').textContent = getFilteredCoffees().length;

    updateActiveFilterBadges(sorted.length);
  }}

  // Update Active Filter Tags & Table Header Badge
  function updateActiveFilterBadges(matchCount) {{
    const container = document.getElementById('activeFilterTags');
    const headerBadge = document.getElementById('priceFilterActiveBadge');
    if (!container) return;

    const tags = [];
    const rf = rangeFilters;

    if (rf.price_100g_aed.min !== null && rf.price_100g_aed.max !== null) {{
      tags.push({{ key: 'price_100g_aed', text: `💰 가격: ${{rf.price_100g_aed.min}}~${{rf.price_100g_aed.max}} AED` }});
    }} else if (rf.price_100g_aed.min !== null) {{
      tags.push({{ key: 'price_100g_aed', text: `💰 가격: ≥${{rf.price_100g_aed.min}} AED` }});
    }} else if (rf.price_100g_aed.max !== null) {{
      tags.push({{ key: 'price_100g_aed', text: `💰 가격: ≤${{rf.price_100g_aed.max}} AED` }});
    }}

    if (rf.score_total.min !== null && rf.score_total.max !== null) {{
      tags.push({{ key: 'score_total', text: `⭐ 종합: ${{rf.score_total.min}}~${{rf.score_total.max}}점` }});
    }} else if (rf.score_total.min !== null) {{
      tags.push({{ key: 'score_total', text: `⭐ 종합: ≥${{rf.score_total.min}}점` }});
    }} else if (rf.score_total.max !== null) {{
      tags.push({{ key: 'score_total', text: `⭐ 종합: ≤${{rf.score_total.max}}점` }});
    }}

    if (rf.score_taste.min !== null && rf.score_taste.max !== null) {{
      tags.push({{ key: 'score_taste', text: `☕ 맛: ${{rf.score_taste.min}}~${{rf.score_taste.max}}점` }});
    }} else if (rf.score_taste.min !== null) {{
      tags.push({{ key: 'score_taste', text: `☕ 맛: ≥${{rf.score_taste.min}}점` }});
    }} else if (rf.score_taste.max !== null) {{
      tags.push({{ key: 'score_taste', text: `☕ 맛: ≤${{rf.score_taste.max}}점` }});
    }}

    if (rf.score_price.min !== null && rf.score_price.max !== null) {{
      tags.push({{ key: 'score_price', text: `🏷️ 값: ${{rf.score_price.min}}~${{rf.score_price.max}}점` }});
    }} else if (rf.score_price.min !== null) {{
      tags.push({{ key: 'score_price', text: `🏷️ 값: ≥${{rf.score_price.min}}점` }});
    }} else if (rf.score_price.max !== null) {{
      tags.push({{ key: 'score_price', text: `🏷️ 값: ≤${{rf.score_price.max}}점` }});
    }}

    if (rf.score_rarity.min !== null && rf.score_rarity.max !== null) {{
      tags.push({{ key: 'score_rarity', text: `💎 희: ${{rf.score_rarity.min}}~${{rf.score_rarity.max}}점` }});
    }} else if (rf.score_rarity.min !== null) {{
      tags.push({{ key: 'score_rarity', text: `💎 희: ≥${{rf.score_rarity.min}}점` }});
    }} else if (rf.score_rarity.max !== null) {{
      tags.push({{ key: 'score_rarity', text: `💎 희: ≤${{rf.score_rarity.max}}점` }});
    }}

    // Note Presets Multi-Selection Tags
    if (selectedPresetNotes.size > 0) {{
      const modeText = noteMatchMode.toUpperCase();
      selectedPresetNotes.forEach(note => {{
        tags.push({{ key: 'preset_note_' + note, text: `🍒 컵노트(${{modeText}}): ${{note}}` }});
      }});
    }}

    // Note Search Tag
    if (noteFilterQuery) {{
      tags.push({{ key: 'note', text: `🔍 컵노트검색: "${{noteFilterQuery}}"` }});
    }}

    // Process Filter Tag
    if (currentProcessFilter !== 'all') {{
      const procKoNames = {{
        'Washed': '워시드',
        'Natural': '내추럴',
        'Anaerobic/Fermented': '무산소/발효',
        'Honey': '허니',
        'Other': '기타'
      }};
      const pKo = procKoNames[currentProcessFilter] || currentProcessFilter;
      tags.push({{ key: 'process', text: `⚙️ 가공: ${{pKo}}` }});
    }}

    if (tags.length === 0) {{
      container.innerHTML = '<span style="font-size:11.5px; color:var(--text-muted);">(조건 없음 - 전체 원두 표시 중)</span>';
      if (headerBadge) headerBadge.style.display = 'none';
    }} else {{
      container.innerHTML = tags.map(t => `
        <span class="tfp-tag" onclick="clearSingleRangeFilter('${{t.key}}')" title="클릭 시 이 조건 해제">
          <span>${{t.text}}</span>
          <span class="tfp-tag-del">✕</span>
        </span>
      `).join('');
      if (headerBadge) {{
        headerBadge.style.display = 'inline-flex';
        headerBadge.textContent = `🏷️ 조건 ${{tags.length}}개 적용 (${{matchCount}}종)`;
      }}
    }}
  }}

  // Read Inputs and Apply Range Filters
  function applyRangeFilters() {{
    const pMin = parseFloat(document.getElementById('filter_price_min').value);
    const pMax = parseFloat(document.getElementById('filter_price_max').value);
    const tMin = parseFloat(document.getElementById('filter_total_min').value);
    const tMax = parseFloat(document.getElementById('filter_total_max').value);
    const sMin = parseFloat(document.getElementById('filter_taste_min').value);
    const sMax = parseFloat(document.getElementById('filter_taste_max').value);
    const psMin = parseFloat(document.getElementById('filter_price_score_min').value);
    const psMax = parseFloat(document.getElementById('filter_price_score_max').value);
    const rMin = parseFloat(document.getElementById('filter_rarity_min').value);
    const rMax = parseFloat(document.getElementById('filter_rarity_max').value);

    rangeFilters.price_100g_aed = {{ min: isNaN(pMin) ? null : pMin, max: isNaN(pMax) ? null : pMax }};
    rangeFilters.score_total    = {{ min: isNaN(tMin) ? null : tMin, max: isNaN(tMax) ? null : tMax }};
    rangeFilters.score_taste    = {{ min: isNaN(sMin) ? null : sMin, max: isNaN(sMax) ? null : sMax }};
    rangeFilters.score_price    = {{ min: isNaN(psMin) ? null : psMin, max: isNaN(psMax) ? null : psMax }};
    rangeFilters.score_rarity   = {{ min: isNaN(rMin) ? null : rMin, max: isNaN(rMax) ? null : rMax }};

    const nInput = document.getElementById('filter_note_input');
    if (nInput) {{
      noteFilterQuery = nInput.value.trim();
    }}

    updateAll();
  }}

  // 컵노트 주관식 입력 처리
  function applyNoteFilterInput() {{
    const val = (document.getElementById('filter_note_input')?.value || '').trim();
    noteFilterQuery = val;
    const btn = document.getElementById('noteClearBtn');
    if (btn) btn.style.display = val ? 'inline-block' : 'none';
    updateAll();
  }}

  // 컵노트 객관식 프리셋 다중 선택 토글
  function toggleNotePreset(noteName, btn) {{
    if (selectedPresetNotes.has(noteName)) {{
      selectedPresetNotes.delete(noteName);
      if (btn) btn.classList.remove('active');
    }} else {{
      selectedPresetNotes.add(noteName);
      if (btn) btn.classList.add('active');
    }}
    updateAll();
  }}

  // 하단 태그에서 특정 프리셋 컵노트 1개 해제
  function removeSinglePresetNote(noteName) {{
    selectedPresetNotes.delete(noteName);
    document.querySelectorAll('#notePresetRow .tfp-preset-btn').forEach(b => {{
      if (b.getAttribute('data-note') === noteName || b.textContent.trim() === noteName) {{
        b.classList.remove('active');
      }}
    }});
    updateAll();
  }}

  // 다중 컵노트 매칭 조건 (OR / AND) 토글
  function toggleNoteMatchMode() {{
    noteMatchMode = (noteMatchMode === 'or') ? 'and' : 'or';
    const btn = document.getElementById('noteMatchModeBtn');
    if (btn) {{
      if (noteMatchMode === 'and') {{
        btn.textContent = '조건: AND (모두) ↕';
        btn.style.borderColor = 'var(--accent-blue)';
        btn.style.color = 'var(--accent-blue)';
      }} else {{
        btn.textContent = '조건: OR (하나라도) ↕';
        btn.style.borderColor = 'var(--accent-gold)';
        btn.style.color = 'var(--accent-gold)';
      }}
    }}
    updateAll();
  }}

  function clearNoteInput() {{
    const input = document.getElementById('filter_note_input');
    if (input) input.value = '';
    noteFilterQuery = '';
    const btn = document.getElementById('noteClearBtn');
    if (btn) btn.style.display = 'none';
    updateAll();
  }}

  function setTfpProcessFilter(proc, btn) {{
    setProcessFilter(proc, btn);
  }}

  // Preset Button Handler
  function setPreset(key, min, max, btn) {{
    const card = btn.closest('.tfp-card');
    const isAlreadyActive = btn.classList.contains('active');

    if (isAlreadyActive) {{
      // Toggle off
      btn.classList.remove('active');
      clearSingleRangeFilter(key);
      return;
    }}

    card.querySelectorAll('.tfp-preset-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Sync input values
    if (key === 'price_100g_aed') {{
      document.getElementById('filter_price_min').value = min !== null ? min : '';
      document.getElementById('filter_price_max').value = max !== null ? max : '';
    }} else if (key === 'score_total') {{
      document.getElementById('filter_total_min').value = min !== null ? min : '';
      document.getElementById('filter_total_max').value = max !== null ? max : '';
    }} else if (key === 'score_taste') {{
      document.getElementById('filter_taste_min').value = min !== null ? min : '';
      document.getElementById('filter_taste_max').value = max !== null ? max : '';
    }} else if (key === 'score_price') {{
      document.getElementById('filter_price_score_min').value = min !== null ? min : '';
      document.getElementById('filter_price_score_max').value = max !== null ? max : '';
    }} else if (key === 'score_rarity') {{
      document.getElementById('filter_rarity_min').value = min !== null ? min : '';
      document.getElementById('filter_rarity_max').value = max !== null ? max : '';
    }}

    rangeFilters[key] = {{ min, max }};
    updateAll();
  }}

  // Clear Single Range Filter
  function clearSingleRangeFilter(key) {{
    if (key.startsWith('preset_note_')) {{
      const n = key.replace('preset_note_', '');
      removeSinglePresetNote(n);
      return;
    }}
    if (key === 'note') {{
      clearNoteInput();
      return;
    }}
    if (key === 'process') {{
      setProcessFilter('all');
      return;
    }}
    rangeFilters[key] = {{ min: null, max: null }};

    if (key === 'price_100g_aed') {{
      document.getElementById('filter_price_min').value = '';
      document.getElementById('filter_price_max').value = '';
      const card = document.querySelectorAll('.tfp-card')[0];
      if (card) card.querySelectorAll('.tfp-preset-btn').forEach(b => b.classList.remove('active'));
    }} else if (key === 'score_total') {{
      document.getElementById('filter_total_min').value = '';
      document.getElementById('filter_total_max').value = '';
      const card = document.querySelectorAll('.tfp-card')[1];
      if (card) card.querySelectorAll('.tfp-preset-btn').forEach(b => b.classList.remove('active'));
    }} else if (key === 'score_taste') {{
      document.getElementById('filter_taste_min').value = '';
      document.getElementById('filter_taste_max').value = '';
      const card = document.querySelectorAll('.tfp-card')[2];
      if (card) card.querySelectorAll('.tfp-preset-btn').forEach(b => b.classList.remove('active'));
    }} else if (key === 'score_price') {{
      document.getElementById('filter_price_score_min').value = '';
      document.getElementById('filter_price_score_max').value = '';
      const card = document.querySelectorAll('.tfp-card')[3];
      if (card) card.querySelectorAll('.tfp-preset-btn').forEach(b => b.classList.remove('active'));
    }} else if (key === 'score_rarity') {{
      document.getElementById('filter_rarity_min').value = '';
      document.getElementById('filter_rarity_max').value = '';
      const card = document.querySelectorAll('.tfp-card')[4];
      if (card) card.querySelectorAll('.tfp-preset-btn').forEach(b => b.classList.remove('active'));
    }}

    updateAll();
  }}

  // Reset All Range Filters
  function resetAllRangeFilters() {{
    rangeFilters = {{
      price_100g_aed: {{ min: null, max: null }},
      score_total:    {{ min: null, max: null }},
      score_taste:    {{ min: null, max: null }},
      score_price:    {{ min: null, max: null }},
      score_rarity:   {{ min: null, max: null }}
    }};

    ['filter_price_min', 'filter_price_max', 'filter_total_min', 'filter_total_max', 
     'filter_taste_min', 'filter_taste_max', 'filter_price_score_min', 'filter_price_score_max',
     'filter_rarity_min', 'filter_rarity_max'].forEach(id => {{
      const el = document.getElementById(id);
      if (el) el.value = '';
    }});

    // Reset note multi-presets & search
    selectedPresetNotes.clear();
    noteMatchMode = 'or';
    const modeBtn = document.getElementById('noteMatchModeBtn');
    if (modeBtn) {{
      modeBtn.textContent = '조건: OR (하나라도) ↕';
      modeBtn.style.borderColor = 'var(--accent-gold)';
      modeBtn.style.color = 'var(--accent-gold)';
    }}
    document.querySelectorAll('#notePresetRow .tfp-preset-btn').forEach(b => b.classList.remove('active'));

    const nInput = document.getElementById('filter_note_input');
    if (nInput) nInput.value = '';
    noteFilterQuery = '';
    const nClearBtn = document.getElementById('noteClearBtn');
    if (nClearBtn) nClearBtn.style.display = 'none';

    // Reset process filter to 'all'
    currentProcessFilter = 'all';
    document.querySelectorAll('#tfpProcessBtnGroup .tfp-preset-btn').forEach(b => {{
      b.classList.toggle('active', b.getAttribute('data-proc') === 'all');
    }});
    document.querySelectorAll('#processFilterGroup .ctrl-btn').forEach(b => {{
      b.classList.toggle('active', (b.getAttribute('onclick') || '').includes("'all'"));
    }});

    document.querySelectorAll('.tfp-preset-btn:not(#tfpProcessBtnGroup .tfp-preset-btn):not(#notePresetRow .tfp-preset-btn)').forEach(b => b.classList.remove('active'));
    updateAll();
  }}

  function toggleSyncPriceWithCharts(cb) {{
    syncPriceWithCharts = cb.checked;
    updateAll();
  }}

  // Backward compatibility stubs
  function setPriceFilter(maxVal, btn) {{
    setPreset('price_100g_aed', null, maxVal, btn || document.createElement('button'));
  }}
  function resetPriceFilter() {{
    clearSingleRangeFilter('price_100g_aed');
  }}

  function sortTable(key) {{
    if (sortKey === key) {{
      sortAsc = !sortAsc;
    }} else {{
      sortKey = key;
      sortAsc = false;
    }}
    renderTable();
  }}

  function updateAll() {{
    if (scatterChart) {{
      const yLimits = getYScaleLimits();
      scatterChart.data.datasets = buildScatterDatasets();
      scatterChart.options.scales.y.title.text = getYAxisLabel() + ' - [Y축 위에서 휠 스크롤 시 점수 확대/축소]';
      // Keep baseline bounds fixed across filter selections unless zoomed
      scatterChart.options.scales.x.min = 0;
      scatterChart.options.scales.x.max = 1150;
      scatterChart.options.scales.y.min = yLimits.min;
      scatterChart.options.scales.y.max = yLimits.max;
      scatterChart.update();
    }}
    updateNotesChart();
    updateShapeLegend();
    renderTable();
  }}

  // Filter & Toggle handlers
  function setYMetric(metric, btn) {{
    currentYMetric = metric;
    btn.parentElement.querySelectorAll('.ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateAll();
  }}

  function setShapeMode(mode, btn) {{
    currentShapeMode = mode;
    btn.parentElement.querySelectorAll('.ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateAll();
  }}

  function setOriginFilter(origin, btn) {{
    currentOriginFilter = origin;
    document.querySelectorAll('#originFilterGroup .ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateAll();
  }}

  function setProcessFilter(proc, btn) {{
    currentProcessFilter = proc;
    document.querySelectorAll('#processFilterGroup .ctrl-btn').forEach(b => {{
      const onclickAttr = b.getAttribute('onclick') || '';
      b.classList.toggle('active', onclickAttr.includes(`'${{proc}}'`));
    }});
    document.querySelectorAll('#tfpProcessBtnGroup .tfp-preset-btn').forEach(b => {{
      b.classList.toggle('active', b.getAttribute('data-proc') === proc);
    }});
    updateAll();
  }}

  function toggleGroupFilter(groupKey, chip) {{
    if (activeGroups.has(groupKey)) {{
      if (activeGroups.size === 1) return; // Keep at least one group
      activeGroups.delete(groupKey);
      chip.classList.remove('active');
    }} else {{
      activeGroups.add(groupKey);
      chip.classList.add('active');
    }}
    updateAll();
  }}

  // Search by Enter or Click
  function executeSearch() {{
    const val = document.getElementById('searchInput').value.trim();
    searchQuery = val;
    const rBtn = document.getElementById('searchResetBtn');
    if (rBtn) rBtn.style.display = val ? 'inline-flex' : 'none';
    updateAll();
  }}

  function clearSearch() {{
    document.getElementById('searchInput').value = '';
    searchQuery = '';
    const rBtn = document.getElementById('searchResetBtn');
    if (rBtn) rBtn.style.display = 'none';
    updateAll();
  }}

  // MODAL LOGIC
  function openDetailModalById(id) {{
    const c = ALL_COFFEES.find(x => x.id === id);
    if (c) openDetailModal(c);
  }}

  function openDetailModal(c) {{
    selectedCoffeeId = c.id;
    updateNotesChart();
    updateHudBar(c);

    document.getElementById('modalBadges').innerHTML = `
      <span class="detail-badge roastery" style="color:${{c.color}}; border-color:${{c.color}};">${{c.roastery}}</span>
      <span class="detail-badge">${{c.group_name}}</span>
      <span class="detail-badge">${{c.country}}</span>
      <span class="detail-badge">${{c.process}}</span>
    `;
    if (c.is_today_new) {{
      document.getElementById('modalTitle').innerHTML = `<span class="today-new-coffee-title">${{c.title}}</span><span class="badge-new-date">${{c.release_date || '1008'}}</span>`;
    }} else {{
      document.getElementById('modalTitle').textContent = c.title;
    }}

    document.getElementById('modalScoreTotal').textContent = c.score_total;
    document.getElementById('modalScoreTaste').textContent = c.score_taste;
    document.getElementById('modalScorePrice').textContent = c.score_price;
    document.getElementById('modalScoreRarity').textContent = c.score_rarity;

    document.getElementById('modalAwardScore').textContent = c.award_score;
    document.getElementById('modalAwardDesc').textContent = c.award_desc;
    document.getElementById('modalTerroirScore').textContent = c.terroir_score;
    document.getElementById('modalTerroirDesc').textContent = c.terroir_desc;
    document.getElementById('modalReviewScore').textContent = c.review_score;
    document.getElementById('modalReviewDesc').textContent = c.review_desc;

    document.getElementById('modalCountry').textContent = c.country;
    document.getElementById('modalFarm').textContent = `${{c.farm}} / ${{c.producer}} (${{c.location}})`;
    document.getElementById('modalVariety').textContent = c.variety;
    document.getElementById('modalProcess').textContent = c.process;
    document.getElementById('modalAltitude').textContent = c.altitude;
    document.getElementById('modalPrice100g').textContent = `${{c.price_100g_aed}} AED (~${{c.price_100g_krw.toLocaleString()}}원)`;

    const notesHtml = c.notes_list.length > 0 
      ? c.notes_list.map(n => `<span class="note-tag">${{n}}</span>`).join('')
      : `<span style="color:var(--text-muted); font-size:12px;">${{c.tasting_notes}}</span>`;
    document.getElementById('modalNotesList').innerHTML = notesHtml;

    document.getElementById('modalKoreaStatus').textContent = c.korea_status;
    document.getElementById('modalKoreaSeller').textContent = c.korea_seller;
    document.getElementById('modalKoreaPrice').textContent = c.korea_price;
    document.getElementById('modalMerit').textContent = c.merit;

    const srcBtn = document.getElementById('modalSourceBtn');
    srcBtn.href = c.source_url;

    currentAnalyticsModalCoffee = c;
    updateModalStarBtnAnalytics(c);

    document.getElementById('detailOverlay').classList.add('active');
  }}

  let currentAnalyticsModalCoffee = null;

  function updateModalStarBtnAnalytics(c) {{
    const btn = document.getElementById('modalStarBtnAnalytics');
    const btnH = document.getElementById('modalStarBtnAnalyticsHeader');
    if (!c) return;
    let inCart = false;
    try {{
      const stored = localStorage.getItem('coffee_cart');
      if (stored) {{
        const cart = JSON.parse(stored);
        inCart = cart.some(x => (x.handle && x.handle === c.handle) || x.title === c.title);
      }}
    }} catch(e) {{}}

    if (btn) {{
      if (inCart) {{
        btn.innerHTML = '★ 장바구니 담김';
        btn.classList.add('active-in-cart');
      }} else {{
        btn.innerHTML = '⭐ 장바구니 담기';
        btn.classList.remove('active-in-cart');
      }}
    }}
    if (btnH) {{
      if (inCart) {{
        btnH.innerHTML = '★ 담김';
        btnH.classList.add('active-in-cart');
      }} else {{
        btnH.innerHTML = '⭐ 담기';
        btnH.classList.remove('active-in-cart');
      }}
    }}
  }}

  function toggleCartFromModalAnalytics() {{
    if (!currentAnalyticsModalCoffee) return;
    const c = currentAnalyticsModalCoffee;
    let cart = [];
    try {{
      const stored = localStorage.getItem('coffee_cart');
      if (stored) cart = JSON.parse(stored);
    }} catch(e) {{}}

    const existingIdx = cart.findIndex(x => (x.handle && x.handle === c.handle) || x.title === c.title);
    if (existingIdx >= 0) {{
      cart.splice(existingIdx, 1);
      localStorage.setItem('coffee_cart', JSON.stringify(cart));
      updateModalStarBtnAnalytics(c);
      updateCartCountBadge();
      showAnalyticsToast(`🗑️ '${{c.title}}' 원두가 장바구니에서 삭제되었습니다.`);
    }} else {{
      const pAed = parseFloat(c.price_aed) || (c.price_100g_aed ? parseFloat(c.price_100g_aed) : 0);
      const pKrw = parseInt(c.price_krw) || (c.price_100g_krw ? parseInt(c.price_100g_krw) : Math.round(pAed * 380));
      const itemToAdd = {{
        title: c.title,
        handle: c.handle,
        roastery: c.roastery.includes('Archers') ? 'Archers Coffee' : 'The Espresso Lab',
        roastery_badge: c.roastery.includes('Archers') ? '🏹 Archers' : '☕ Esolab',
        source_url: c.source_url,
        price_aed: pAed,
        price_krw: pKrw,
        weight: c.weight || '100g',
        roast: c.roast || 'Filter Light Roast',
        country: c.country,
        farm: c.farm,
        producer: c.producer,
        variety: c.variety,
        process: c.process,
        altitude: c.altitude,
        notes: c.tasting_notes || (c.notes_list ? c.notes_list.join(', ') : ''),
        overlap_note: c.merit || '애널리틱스 분석 추천 랏',
        detailed_review: {{
          taste_analysis: `${{c.roastery}} - ${{c.country}} ${{c.variety}} (${{c.process}}). 종합점수 ${{c.score_total}}점 (맛 ${{c.score_taste}}/50). ${{c.merit || ''}}`
        }},
        added_at: Date.now()
      }};
      cart.push(itemToAdd);
      localStorage.setItem('coffee_cart', JSON.stringify(cart));
      updateModalStarBtnAnalytics(c);
      updateCartCountBadge();
      showAnalyticsToast(`🛒 '${{c.title}}' 원두가 장바구니에 담겼습니다!`);
    }}
  }}

  function updateCartCountBadge() {{
    let count = 0;
    try {{
      const stored = localStorage.getItem('coffee_cart');
      if (stored) {{
        const arr = JSON.parse(stored);
        count = arr.length;
      }}
    }} catch (e) {{}}
    document.querySelectorAll('.cart-badge-count').forEach(el => {{
      el.textContent = count;
    }});
  }}

  function showAnalyticsToast(msg) {{
    let toast = document.getElementById('analyticsToast');
    if (!toast) {{
      toast = document.createElement('div');
      toast.id = 'analyticsToast';
      toast.style.cssText = 'position:fixed; bottom:30px; left:50%; transform:translateX(-50%); background:rgba(22,27,34,0.95); border:1px solid #d29922; color:#f0f6fc; padding:12px 24px; border-radius:10px; font-size:14px; font-weight:600; box-shadow:0 8px 24px rgba(0,0,0,0.5); z-index:99999; display:none; align-items:center; gap:8px;';
      document.body.appendChild(toast);
    }}
    toast.textContent = msg;
    toast.style.display = 'flex';
    setTimeout(() => {{
      toast.style.display = 'none';
    }}, 3500);
  }}

  function closeDetailModal(e) {{
    document.getElementById('detailOverlay').classList.remove('active');
    selectedCoffeeId = null;
    updateNotesChart();
  }}

  // THEME TOGGLE
  function initTheme() {{
    const saved = localStorage.getItem('coffee_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    applyThemeUI(saved);
  }}

  function toggleTheme() {{
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('coffee_theme', next);
    applyThemeUI(next);

    // Refresh charts
    if (scatterChart) {{
      scatterChart.destroy();
      initScatterChart();
    }}
    if (notesChart) {{
      notesChart.destroy();
      initNotesChart();
    }}
  }}

  function applyThemeUI(theme) {{
    const icon = document.getElementById('themeIcon');
    const txt = document.getElementById('themeText');
    if (theme === 'light') {{
      icon.textContent = '🌙';
      txt.textContent = '다크 모드';
    }} else {{
      icon.textContent = '☀️';
      txt.textContent = '라이트 모드';
    }}
  }}

  // ON LOAD
  window.addEventListener('DOMContentLoaded', () => {{
    initTheme();
    initScatterChart();
    initNotesChart();
    updateShapeLegend();
    renderTable();
    updateCartCountBadge();
  }});
</script>

</body>
</html>
"""
    with open('c:/cowork/coffee/analytics.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("analytics.html generated successfully with all requested enhancements!")

def main():
    items = build_data()
    stats = calculate_statistics(items)
    print(f"Generated data for {len(items)} coffee beans.")
    generate_html(items, stats)

if __name__ == '__main__':
    main()
