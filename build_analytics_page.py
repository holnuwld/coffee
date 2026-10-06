"""
Build interactive coffee analytics page (analytics.html)
Features & Updates:
- Full dataset (171 coffees: Archers 117 + The Espresso Lab 54)
- Statistical summary & insights (Pearson correlation, sweet-spots, pricing tiers)
- Graph 1: Scatter plot (Price per 100g vs Score - Total/Taste/Rarity/Price)
  - Color encoded: Archers Comp (black), Reserve (blue), Selection (yellow), Espresso Lab (red)
  - Smaller point radius (4.5px) for clear separation in dense clusters
  - Tooltip caret padding (20px) away from cursor to avoid covering nearby dots
  - Point shape encoding by Country, Process, Altitude, or Default (*, x, o, triangle, rect)
  - Mouse wheel zoom & pan via chartjs-plugin-zoom with floating "Fit to Size" button
  - Distinct active/inactive styles for lineup filter chips
  - Korean search support (country, process, farm, variety, tasting notes, roastery)
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

    # Common farm names
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

def build_data():
    with open('c:/cowork/coffee/new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
        archers_raw = json.load(f)
    with open('c:/cowork/coffee/espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
        tel_raw = json.load(f)

    all_items = []
    
    # Archers (117)
    for idx, c in enumerate(archers_raw):
        sc = score_coffee_item(c, 'Archers')
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
            'search_kr': kr_keywords
        })

    # Espresso Lab (54)
    for idx, c in enumerate(tel_raw):
        sc = score_coffee_item(c, 'The Espresso Lab')
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
            'search_kr': kr_keywords
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

    # Groups stats
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
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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

    /* CONTROLS SECTION */
    .controls-panel {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px 20px;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .control-row {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .control-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .control-label {{
      font-size: 12.5px;
      font-weight: 700;
      color: var(--text-secondary);
      white-space: nowrap;
    }}
    .btn-toggle-group {{
      display: inline-flex;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 3px;
      gap: 3px;
      flex-wrap: wrap;
    }}
    .btn-toggle {{
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 6px 11px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .btn-toggle.active {{
      background: var(--accent-gold);
      color: #000;
      font-weight: 700;
    }}

    /* LINEUP FILTER CHIPS - SHARP CONTRAST */
    .filter-chips {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 20px;
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

    .search-input {{
      padding: 7px 12px;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 13px;
      min-width: 240px;
      outline: none;
    }}
    .search-input:focus {{
      border-color: var(--accent-gold);
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

    /* CHARTS LAYOUT */
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
    }}
    .chart-box-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
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
    .chart-canvas-wrapper {{
      position: relative;
      flex: 1;
      min-height: 460px;
      width: 100%;
    }}

    /* FLOATING FIT BUTTON */
    .chart-fit-btn {{
      position: absolute;
      left: 14px;
      bottom: 24px;
      z-index: 10;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.2s;
    }}
    .chart-fit-btn:hover {{
      border-color: var(--accent-gold);
      color: var(--accent-gold);
      transform: scale(1.04);
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
      max-height: 480px;
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
  </style>
</head>
<body>

<div class="container">
  <!-- TOP NAV -->
  <div class="header-nav">
    <div class="nav-links">
      <a href="index.html" class="nav-btn">← 메인 허브 (Top 20)</a>
      <a href="cart.html" class="nav-btn">🛒 장바구니</a>
      <a href="archers_coffee_clean_verified.html" class="nav-btn">🏛️ 아처스 대시보드</a>
      <a href="theespressolab_verified.html" class="nav-btn">🔬 에소랩 대시보드</a>
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

  <!-- CONTROLS PANEL -->
  <div class="controls-panel">
    <!-- ROW 1: Y-METRIC & SHAPE ENCODER -->
    <div class="control-row">
      <!-- Y-Axis Metric -->
      <div class="control-group">
        <span class="control-label">📈 Y축 점수:</span>
        <div class="btn-toggle-group">
          <button class="btn-toggle active" onclick="setYMetric('total', this)">⭐ 종합점수 (100점)</button>
          <button class="btn-toggle" onclick="setYMetric('taste', this)">☕ 맛 점수 (50점)</button>
          <button class="btn-toggle" onclick="setYMetric('rarity', this)">💎 희소성 (20점)</button>
          <button class="btn-toggle" onclick="setYMetric('price', this)">💰 가격점수 (30점)</button>
        </div>
      </div>

      <!-- Point Shape Encoder -->
      <div class="control-group">
        <span class="control-label">🔷 점 모양(심볼) 구분:</span>
        <div class="btn-toggle-group">
          <button class="btn-toggle active" onclick="setShapeMode('default', this)">기본 (● 원형)</button>
          <button class="btn-toggle" onclick="setShapeMode('country', this)">원산지별 (에티오피아/파나마 등)</button>
          <button class="btn-toggle" onclick="setShapeMode('process', this)">프로세스별 (워시드/내추럴 등)</button>
          <button class="btn-toggle" onclick="setShapeMode('altitude', this)">고도별 (초고도/고고도)</button>
        </div>
      </div>
    </div>

    <!-- ROW 2: ORIGIN & PROCESS QUICK FILTERS -->
    <div class="control-row">
      <!-- Origin Filter -->
      <div class="control-group">
        <span class="control-label">🌍 원산지 필터:</span>
        <div class="btn-toggle-group" id="originFilterGroup">
          <button class="btn-toggle active" onclick="setOriginFilter('all', this)">전체 원산지</button>
          <button class="btn-toggle" onclick="setOriginFilter('Ethiopia', this)">에티오피아 (43)</button>
          <button class="btn-toggle" onclick="setOriginFilter('Panama', this)">파나마 (76)</button>
          <button class="btn-toggle" onclick="setOriginFilter('Colombia', this)">콜롬비아 (26)</button>
          <button class="btn-toggle" onclick="setOriginFilter('Other', this)">코스타리카/기타 (26)</button>
        </div>
      </div>

      <!-- Process Filter -->
      <div class="control-group">
        <span class="control-label">⚙️ 프로세스 필터:</span>
        <div class="btn-toggle-group" id="processFilterGroup">
          <button class="btn-toggle active" onclick="setProcessFilter('all', this)">전체 프로세스</button>
          <button class="btn-toggle" onclick="setProcessFilter('Washed', this)">워시드 (Washed)</button>
          <button class="btn-toggle" onclick="setProcessFilter('Natural', this)">내추럴 (Natural)</button>
          <button class="btn-toggle" onclick="setProcessFilter('Anaerobic/Fermented', this)">무산소·발효</button>
          <button class="btn-toggle" onclick="setProcessFilter('Honey', this)">허니 (Honey)</button>
        </div>
      </div>
    </div>

    <!-- ROW 3: LINEUP CHIPS & SEARCH INPUT -->
    <div class="control-row">
      <!-- Roastery / Group Filters -->
      <div class="control-group">
        <span class="control-label">🏷️ 라인업 필터:</span>
        <div class="filter-chips">
          <div class="chip active" onclick="toggleGroupFilter('competition', this)" style="border-color:#8b949e; color:#f0f6fc;">
            <span class="chip-dot" style="background:#1f242d; border:1px solid #8b949e;"></span>
            아처스 컴피티션 (85)
          </div>
          <div class="chip active" onclick="toggleGroupFilter('reserve', this)" style="border-color:#2563eb; color:#60a5fa;">
            <span class="chip-dot" style="background:#2563eb;"></span>
            아처스 리저브 (20)
          </div>
          <div class="chip active" onclick="toggleGroupFilter('selection', this)" style="border-color:#d97706; color:#fbbf24;">
            <span class="chip-dot" style="background:#d97706;"></span>
            아처스 셀렉션 (12)
          </div>
          <div class="chip active" onclick="toggleGroupFilter('esolab', this)" style="border-color:#dc2626; color:#f87171;">
            <span class="chip-dot" style="background:#dc2626;"></span>
            에소랩 전체 (54)
          </div>
        </div>
      </div>

      <!-- Search Input with Korean support -->
      <div class="control-group" style="margin-left:auto;">
        <input type="text" id="searchInput" class="search-input" placeholder="🔍 원두명, 생산국(예:에티오피아), 품종, 농장 검색..." oninput="handleSearch(this.value)">
      </div>
    </div>

    <!-- DYNAMIC SHAPE LEGEND BAR -->
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
            마우스 휠 스크롤로 확대/축소, 드래그로 이동 가능하며 점을 클릭하면 상세 정보가 열립니다.
          </div>
        </div>
        <div style="font-size:12px; color:var(--text-muted);">
          현재 표시: <span id="pointCountDisplay" style="font-weight:700; color:var(--accent-gold);">171</span>종
        </div>
      </div>
      <div class="chart-canvas-wrapper">
        <canvas id="scatterChart"></canvas>
        <button class="chart-fit-btn" onclick="resetScatterZoom()" title="확대/축소 리셋 및 전체보기">
          🔍 전체보기 (Fit to Size)
        </button>
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
      <div class="chart-canvas-wrapper">
        <canvas id="notesChart"></canvas>
      </div>
    </div>
  </div>

  <!-- BOTTOM TABLE VIEW -->
  <div class="table-section">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <h3 style="font-size:16px; font-weight:700;">📋 필터링된 원두 리스트 (<span id="tableCountDisplay">171</span>종)</h3>
      <div style="font-size:12px; color:var(--text-muted);">행을 클릭하면 상세 분석 모달이 열립니다.</div>
    </div>
    <div class="table-responsive">
      <table class="data-table" id="dataTable">
        <thead>
          <tr>
            <th onclick="sortTable('roastery')">로스터리 ↕</th>
            <th onclick="sortTable('title')">원두명 ↕</th>
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

<!-- COFFEE DETAIL MODAL -->
<div class="detail-overlay" id="detailOverlay" onclick="closeDetailModal(event)">
  <div class="detail-modal" onclick="event.stopPropagation()">
    <div class="modal-header">
      <div>
        <div class="detail-badges" id="modalBadges"></div>
        <h2 class="detail-title" id="modalTitle" style="margin-top:6px;"></h2>
      </div>
      <button class="modal-close-btn" onclick="closeDetailModal()">&times;</button>
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
  let highlightedNote = null;
  let sortKey = 'score_total';
  let sortAsc = false;

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

      // 5. Note cross-filtering
      if (highlightedNote) {{
        const hasNote = c.notes_list.some(n => n.includes(highlightedNote));
        if (!hasNote) return false;
      }}
      return true;
    }});
  }}

  // Initialize Scatter Chart
  function initScatterChart() {{
    const ctx = document.getElementById('scatterChart').getContext('2d');
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';

    scatterChart = new Chart(ctx, {{
      type: 'scatter',
      data: {{ datasets: buildScatterDatasets() }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        animation: {{ duration: 300 }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            backgroundColor: isDark ? 'rgba(22, 27, 34, 0.96)' : 'rgba(255, 255, 255, 0.98)',
            titleColor: isDark ? '#f0f6fc' : '#1f2328',
            bodyColor: isDark ? '#8b949e' : '#57606a',
            borderColor: isDark ? '#30363d' : '#d0d7de',
            borderWidth: 1,
            padding: 10,
            caretPadding: 20, // Keep tooltip away from cursor and dense points
            caretSize: 8,
            xAlign: 'center',
            yAlign: 'bottom',
            titleFont: {{ size: 12.5, weight: 'bold' }},
            bodyFont: {{ size: 11.5, lineHeight: 1.4 }},
            callbacks: {{
              label: function(ctx) {{
                const raw = ctx.raw;
                const c = raw.coffee;
                return [
                  `☕ [${{c.roastery}}] ${{c.title}}`,
                  `💰 100g: ${{c.price_100g_aed}} AED (~${{c.price_100g_krw.toLocaleString()}}원)`,
                  `⭐ 종합: ${{c.score_total}}점 (맛 ${{c.score_taste}} / 값 ${{c.score_price}} / 희 ${{c.score_rarity}})`,
                  `🌍 원산지: ${{c.country}} | 가공: ${{c.process}}`,
                  `👉 클릭하여 상세 스펙 열기`
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
                speed: 0.1
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
            title: {{
              display: true,
              text: '100g당 가격 (AED) - 마우스 휠 스크롤로 확대/축소 가능',
              color: isDark ? '#8b949e' : '#57606a',
              font: {{ weight: 'bold', size: 11.5 }}
            }},
            grid: {{ color: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }},
            ticks: {{ color: isDark ? '#8b949e' : '#57606a' }}
          }},
          y: {{
            title: {{
              display: true,
              text: getYAxisLabel(),
              color: isDark ? '#8b949e' : '#57606a',
              font: {{ weight: 'bold', size: 11.5 }}
            }},
            grid: {{ color: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }},
            ticks: {{ color: isDark ? '#8b949e' : '#57606a' }}
          }}
        }},
        onClick: (evt, activeEls) => {{
          if (activeEls.length > 0) {{
            const el = activeEls[0];
            const dataset = scatterChart.data.datasets[el.datasetIndex];
            const pointData = dataset.data[el.index];
            if (pointData && pointData.coffee) {{
              openDetailModal(pointData.coffee);
            }}
          }}
        }}
      }}
    }});
  }}

  function resetScatterZoom() {{
    if (scatterChart) {{
      scatterChart.resetZoom();
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

      // Point styles array explicitly defined for Chart.js dataset
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
        animation: {{ duration: 300 }},
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

    // Count occurrences within filtered coffees
    const noteCountMap = {{}};
    TOP_NOTES_VOCAB.forEach(n => {{ noteCountMap[n] = 0; }});

    filtered.forEach(c => {{
      TOP_NOTES_VOCAB.forEach(note => {{
        if (c.notes_list.some(n => n.includes(note))) {{
          noteCountMap[note] = (noteCountMap[note] || 0) + 1;
        }}
      }});
    }});

    // Sort notes by count descending, take top 14
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

    // Update subtitle
    const sub = document.getElementById('notesChartSubtitle');
    if (sub) {{
      let filterDesc = [];
      if (currentOriginFilter !== 'all') filterDesc.push(`원산지:${{currentOriginFilter}}`);
      if (currentProcessFilter !== 'all') filterDesc.push(`가공:${{currentProcessFilter}}`);
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
  function renderTable() {{
    const filtered = getFilteredCoffees();
    const sorted = [...filtered].sort((a, b) => {{
      let valA = a[sortKey];
      let valB = b[sortKey];
      if (typeof valA === 'string') {{
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }}
      return sortAsc ? valA - valB : valB - valA;
    }});

    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = sorted.map(c => `
      <tr onclick="openDetailModalById('${{c.id}}')">
        <td><strong style="color:${{c.color}};">${{c.roastery}}</strong></td>
        <td><strong style="word-break:keep-all;">${{c.title}}</strong></td>
        <td>${{c.country}}</td>
        <td>${{c.process}}</td>
        <td style="font-weight:700; font-family:monospace;">${{c.price_100g_aed}} AED</td>
        <td style="font-family:monospace; color:var(--accent-blue);">${{c.score_taste}}</td>
        <td style="font-family:monospace; color:var(--accent-green);">${{c.score_price}}</td>
        <td style="font-family:monospace; color:#a855f7;">${{c.score_rarity}}</td>
        <td style="font-weight:800; font-family:monospace; color:var(--accent-gold);">${{c.score_total}}</td>
      </tr>
    `).join('');

    document.getElementById('tableCountDisplay').textContent = sorted.length;
    document.getElementById('pointCountDisplay').textContent = sorted.length;
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
      scatterChart.data.datasets = buildScatterDatasets();
      scatterChart.options.scales.y.title.text = getYAxisLabel();
      scatterChart.update();
    }}
    updateNotesChart();
    updateShapeLegend();
    renderTable();
  }}

  // Filter & Toggle handlers
  function setYMetric(metric, btn) {{
    currentYMetric = metric;
    document.querySelectorAll('.control-row:first-child .control-group:first-child .btn-toggle').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateAll();
  }}

  function setShapeMode(mode, btn) {{
    currentShapeMode = mode;
    document.querySelectorAll('.control-row:first-child .control-group:nth-child(2) .btn-toggle').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateAll();
  }}

  function setOriginFilter(origin, btn) {{
    currentOriginFilter = origin;
    document.querySelectorAll('#originFilterGroup .btn-toggle').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateAll();
  }}

  function setProcessFilter(proc, btn) {{
    currentProcessFilter = proc;
    document.querySelectorAll('#processFilterGroup .btn-toggle').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
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

  function handleSearch(val) {{
    searchQuery = val.trim();
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

    document.getElementById('modalBadges').innerHTML = `
      <span class="detail-badge roastery" style="color:${{c.color}}; border-color:${{c.color}};">${{c.roastery}}</span>
      <span class="detail-badge">${{c.group_name}}</span>
      <span class="detail-badge">${{c.country}}</span>
      <span class="detail-badge">${{c.process}}</span>
    `;
    document.getElementById('modalTitle').textContent = c.title;

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

    document.getElementById('detailOverlay').classList.add('active');
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
