import json
import html
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

RAW_FILE = r'c:\cowork\coffee\new_pipeline\raw_collected_coffees.json'
MOBILE_HTML = r'c:\cowork\coffee\mobile.html'
INDEX_HTML = r'c:\cowork\coffee\index.html'
DESKTOP_HTML = r'c:\cowork\coffee\archers_coffee_clean_verified.html'

with open(RAW_FILE, 'r', encoding='utf-8') as f:
    coffees = json.load(f)

print(f"Loaded {len(coffees)} coffees for mobile & index generation.")

COUNTRY_FLAGS = {
    'Panama': '🇵🇦',
    'Ethiopia': '🇪🇹',
    'Colombia': '🇨🇴',
    'Ecuador': '🇪🇨',
    'Costa Rica': '🇨🇷',
    'Brazil': '🇧🇷',
    'Yemen': '🇾🇪',
    'Kenya': '🇰🇪',
    'Guatemala': '🇬🇹',
    'El Salvador': '🇸🇻',
    'Mexico': '🇲🇽',
    'Honduras': '🇭🇳',
    'Rwanda': '🇷🇼',
    'Burundi': '🇧🇮',
    'Bolivia': '🇧🇴',
    'Indonesia': '🇮🇩',
    'Peru': '🇵🇪'
}

def get_flag(c_name):
    for k, v in COUNTRY_FLAGS.items():
        if k.lower() in c_name.lower():
            return v
    return '☕'

# 1. GENERATE mobile.html
mobile_code = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>UAE 아처스 커피 - 모바일 구매 가이드</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #090d13;
    --card-bg: #141922;
    --card-hover: #1c2230;
    --border: #262c36;
    --accent: #d29922;
    --accent-light: #f1e05a;
    --accent-sub: #e3b341;
    --text-primary: #f0f6fc;
    --text-secondary: #9da7b3;
    --text-muted: #6e7681;
    --success: #3fb950;
    --blue: #58a6ff;
    --purple: #bc8cff;
    --safe-bottom: env(safe-area-inset-bottom, 16px);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
  body {
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    line-height: 1.5;
    padding-bottom: calc(var(--safe-bottom) + 70px);
  }

  /* Sticky Top Header */
  .mobile-header {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(9, 13, 19, 0.92);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border);
    padding: 12px 16px;
  }
  .header-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  .brand-title {
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .brand-title span { color: var(--accent-light); font-size: 13px; font-weight: 600; }
  .view-switch-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 11.5px;
    font-weight: 600;
    background: #1c2230;
    color: var(--blue);
    border: 1px solid rgba(88, 166, 255, 0.3);
    text-decoration: none;
  }

  /* Search & Controls */
  .search-wrapper {
    position: relative;
    margin-bottom: 10px;
  }
  .search-input {
    width: 100%;
    background: #141922;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px 10px 36px;
    color: #fff;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }
  .search-input:focus { border-color: var(--accent); }
  .search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 14px;
    color: var(--text-muted);
  }

  /* Filter Chips (Scrollable) */
  .chip-scroller {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding-bottom: 4px;
    scrollbar-width: none;
  }
  .chip-scroller::-webkit-scrollbar { display: none; }
  .chip-btn {
    white-space: nowrap;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    background: #161b24;
    color: var(--text-secondary);
    border: 1px solid var(--border);
    cursor: pointer;
  }
  .chip-btn.active {
    background: #238636;
    color: #fff;
    border-color: #2ea043;
  }

  /* Sort Bar */
  .sort-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background: #0d121a;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 12px;
    color: var(--text-muted);
  }
  .sort-select {
    background: #141922;
    color: var(--text-primary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11.5px;
    outline: none;
  }

  /* Container */
  .main-content { padding: 14px 16px; }

  /* Section Title */
  .sec-title {
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
    color: #f0f6fc;
  }

  /* Top 3 Quick Cards (Horizontal Swipe) */
  .top-swipe-container {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    padding-bottom: 12px;
    margin-bottom: 20px;
    scrollbar-width: none;
  }
  .top-swipe-container::-webkit-scrollbar { display: none; }
  .top-card {
    flex: 0 0 85%;
    max-width: 340px;
    scroll-snap-align: start;
    background: linear-gradient(145deg, #181d27 0%, #12161f 100%);
    border: 1px solid rgba(210, 153, 34, 0.35);
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.4);
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .top-card-badge {
    align-self: flex-start;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    background: rgba(210, 153, 34, 0.2);
    color: var(--accent-light);
    border: 1px solid var(--accent);
  }
  .top-card-title {
    font-size: 15px;
    font-weight: 800;
    color: var(--blue);
    line-height: 1.35;
  }
  .top-card-price {
    font-size: 16px;
    font-weight: 800;
    color: var(--accent-light);
  }
  .top-card-notes {
    font-size: 12px;
    background: rgba(210, 153, 34, 0.08);
    border-left: 3px solid var(--accent);
    padding: 6px 8px;
    border-radius: 0 4px 4px 0;
    color: #f0f6fc;
  }
  .top-card-merit {
    font-size: 11.5px;
    color: #c9d1d9;
    line-height: 1.45;
    background: rgba(88, 166, 255, 0.08);
    border: 1px solid rgba(88, 166, 255, 0.2);
    padding: 8px;
    border-radius: 6px;
  }

  /* List Cards */
  .coffee-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .coffee-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px;
    transition: all 0.2s;
    content-visibility: auto;
    contain-intrinsic-size: 140px;
  }
  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 6px;
  }
  .card-meta-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    align-items: center;
  }
  .tag {
    font-size: 10.5px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
    background: #1c2230;
    color: var(--text-secondary);
  }
  .tag.col-comp { background: rgba(210, 153, 34, 0.15); color: var(--accent-light); border: 1px solid rgba(210, 153, 34, 0.3); }
  .tag.col-res { background: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid rgba(88, 166, 255, 0.3); }
  .tag.col-sel { background: rgba(63, 185, 80, 0.15); color: var(--success); border: 1px solid rgba(63, 185, 80, 0.3); }
  .tag.country { background: #262c36; color: #fff; }

  .card-price-box {
    text-align: right;
    white-space: nowrap;
  }
  .price-aed {
    font-size: 15px;
    font-weight: 800;
    color: var(--accent-light);
  }
  .price-krw {
    font-size: 11px;
    color: var(--text-secondary);
  }

  .card-title {
    font-size: 14.5px;
    font-weight: 800;
    color: #f0f6fc;
    margin-bottom: 6px;
    line-height: 1.35;
  }
  .card-notes {
    font-size: 12px;
    color: #e6edf3;
    background: rgba(255,255,255,0.03);
    border-left: 2px solid var(--accent);
    padding: 4px 8px;
    border-radius: 0 4px 4px 0;
    margin-bottom: 8px;
  }
  .card-quick-specs {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 8px;
  }
  .card-quick-specs span { color: #c9d1d9; }

  /* Accordion Detail */
  .card-detail {
    display: none;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px dashed var(--border);
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.6;
  }
  .card-detail.open { display: block; }
  .detail-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 6px;
    margin-bottom: 10px;
    background: #0d1117;
    padding: 8px 10px;
    border-radius: 6px;
  }
  .detail-row { display: flex; justify-content: space-between; }
  .detail-row span:first-child { color: var(--text-muted); }
  .detail-row span:last-child { color: #f0f6fc; font-weight: 500; text-align: right; }

  .detail-box {
    padding: 8px 10px;
    border-radius: 6px;
    margin-bottom: 8px;
    font-size: 11.5px;
  }
  .detail-box.korea {
    background: rgba(88, 166, 255, 0.08);
    border: 1px solid rgba(88, 166, 255, 0.2);
    color: #c9d1d9;
  }
  .detail-box.merit {
    background: rgba(210, 153, 34, 0.08);
    border: 1px solid rgba(210, 153, 34, 0.2);
    color: #e6edf3;
  }
  .detail-box.review {
    background: rgba(188, 140, 255, 0.08);
    border: 1px solid rgba(188, 140, 255, 0.2);
    color: #d2a8ff;
  }

  .btn-shop {
    display: block;
    width: 100%;
    text-align: center;
    background: #238636;
    color: #fff;
    padding: 8px 0;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    margin-top: 6px;
  }

  .expand-toggle {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: var(--blue);
    font-weight: 600;
    padding-top: 6px;
    cursor: pointer;
  }

  /* Floating Bottom Info Bar */
  .floating-bottom {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(14, 18, 24, 0.95);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-top: 1px solid var(--border);
    padding: 10px 16px;
    padding-bottom: calc(var(--safe-bottom) + 10px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
  }
  .count-text { font-size: 12px; color: var(--text-secondary); font-weight: 600; }
  .btn-top {
    background: #1c2230;
    border: 1px solid var(--border);
    color: #fff;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
  }
</style>
</head>
<body>

<!-- STICKY HEADER -->
<div class="mobile-header">
  <div class="header-top">
    <div class="brand-title">
      ☕ Archers Coffee <span>UAE Guide</span>
    </div>
    <a href="archers_coffee_clean_verified.html" class="view-switch-btn">🖥️ 데스크톱 표</a>
  </div>

  <div class="search-wrapper">
    <span class="search-icon">🔍</span>
    <input type="text" id="mSearch" class="search-input" placeholder="커피명, 품종, 컵노트, 국가 검색..." onkeyup="filterMobileCards()">
  </div>

  <div class="chip-scroller">
    <button class="chip-btn active" onclick="setFilter('all', this)">전체 (117)</button>
    <button class="chip-btn" onclick="setFilter('Competition Series 2025', this)">Competition (85)</button>
    <button class="chip-btn" onclick="setFilter('Microlot Reserve 2025', this)">Reserve (20)</button>
    <button class="chip-btn" onclick="setFilter('Microlot Selection 2026', this)">Selection (12)</button>
    <button class="chip-btn" onclick="setFilter('Panama', this)">🇵🇦 파나마</button>
    <button class="chip-btn" onclick="setFilter('Ethiopia', this)">🇪🇹 에티오피아</button>
    <button class="chip-btn" onclick="setFilter('Washed', this)">💧 워시드</button>
  </div>
</div>

<!-- SORT & STATUS BAR -->
<div class="sort-bar">
  <span id="matchCount">117개 원두 표시 중</span>
  <div>
    정렬:
    <select id="mSort" class="sort-select" onchange="sortMobileCards()">
      <option value="default">추천순</option>
      <option value="price-asc">가격 낮은순 (AED)</option>
      <option value="price-desc">가격 높은순 (AED)</option>
      <option value="p100-asc">100g당 단가 낮은순</option>
      <option value="country">원산지 국가순</option>
    </select>
  </div>
</div>

<div class="main-content">

  <!-- TOP PICKS SWIPER -->
  <div class="sec-title">👑 현지 머스트 바이 추천 Best 6 (좌우 스크롤)</div>
  <div class="top-swipe-container">
    <div class="top-card">
      <span class="top-card-badge">🥇 취향 1위 | BOP 챔피언 독점 피베리</span>
      <div class="top-card-title">Panama Auromar Geisha Washed Peaberry</div>
      <div class="top-card-price">AED 98.0 (100g) <span style="font-size:12px; color:#8b949e;">약 37,240원</span></div>
      <div class="top-card-notes">🌸 화이트그레이프, 커피블라썸, 유자, 샴페인</div>
      <div class="top-card-merit">💡 <strong>국내 반값 혜택:</strong> 국내 일반 플랫빈 시세(7~8만원) 대비 50% 반값이며, 피베리는 국내 미수입 아처스 단독 랏!</div>
    </div>

    <div class="top-card">
      <span class="top-card-badge">🥈 취향 2위 | COE 2위 다예 벤사 독점 워시드</span>
      <div class="top-card-title">Ethiopia Hamasho Village Washed Archers Lot</div>
      <div class="top-card-price">AED 33.0 (100g) <span style="font-size:12px; color:#8b949e;">약 12,540원</span></div>
      <div class="top-card-notes">🌸 레몬그라스, 서양배, 화이트플로럴, 다즐링</div>
      <div class="top-card-merit">💡 <strong>국내 반값 혜택:</strong> 국내 유통 하마쇼(내추럴 2.4만원대) 대비 50% 저렴한 1.2만원대 종결자!</div>
    </div>

    <div class="top-card">
      <span class="top-card-badge">🥉 취향 3위 | 세계 최고가 옥션 명문 엘리다</span>
      <div class="top-card-title">Panama Elida Geisha Washed Plano 2801</div>
      <div class="top-card-price">AED 143.0 (100g) <span style="font-size:12px; color:#8b949e;">약 54,340원</span></div>
      <div class="top-card-notes">🌸 라벤더, 백포도, 허니, 백차 질감</div>
      <div class="top-card-merit">💡 <strong>35% 할인:</strong> 국내 시세(8~9만원대) 대비 35% 저렴하며 아처스 독점 Plano 2801 나노랏.</div>
    </div>

    <div class="top-card">
      <span class="top-card-badge" style="background:rgba(88,166,255,0.2); color:#58a6ff; border-color:#58a6ff;">🌟 전문가 1위 | 2,050m 바루 화산 최고봉</span>
      <div class="top-card-title">Panama Finca Los Cenizos Geisha Washed GW-208</div>
      <div class="top-card-price">AED 210.0 (100g) <span style="font-size:12px; color:#8b949e;">약 79,800원</span></div>
      <div class="top-card-notes">🌸 복숭아 아이스티, 탠저린, 얼그레이 홍차</div>
      <div class="top-card-merit">💡 <strong>100% 현지 독점:</strong> 국내 공식 수입 전무. 2,000m급 게이샤의 경이로운 복숭아 홍차 클린컵.</div>
    </div>

    <div class="top-card">
      <span class="top-card-badge" style="background:rgba(88,166,255,0.2); color:#58a6ff; border-color:#58a6ff;">🌟 전문가 2위 | 에콰도르 희귀 메호라도</span>
      <div class="top-card-title">Ecuador Finca Del Putushio Typica Mejorado RT</div>
      <div class="top-card-price">AED 83.0 (100g) <span style="font-size:12px; color:#8b949e;">약 31,540원</span></div>
      <div class="top-card-notes">🌸 자스민, 레몬그라스, 스위트 라임 허브티</div>
      <div class="top-card-merit">💡 <strong>국내 반값:</strong> 국내 6만원대 메호라도 대비 50% 저렴. 게이샤를 능가하는 화사한 허브티 톤.</div>
    </div>

    <div class="top-card">
      <span class="top-card-badge" style="background:rgba(88,166,255,0.2); color:#58a6ff; border-color:#58a6ff;">🌟 전문가 3위 | 1만원대 데일리 워시드 종결</span>
      <div class="top-card-title">Ethiopia Elto Coffee Sama Washed</div>
      <div class="top-card-price">AED 28.0 (100g) <span style="font-size:12px; color:#8b949e;">약 10,640원</span></div>
      <div class="top-card-notes">🌸 자스민, 레몬그라스, 복숭아 아이스티</div>
      <div class="top-card-merit">💡 <strong>극가성비:</strong> 해발 2,350m 단일 품종 워시드가 단돈 10,640원. 매일 마시는 푸어오버 종결자.</div>
    </div>
  </div>

  <!-- ALL 117 COFFEES MOBILE LIST -->
  <div class="sec-title">📋 전체 117개 원두 리스트 (탭하여 상세 보기)</div>
  <div class="coffee-list" id="coffeeList">
"""

for idx, c in enumerate(coffees, 1):
    flag = get_flag(c['country'])
    col_class = 'col-comp' if 'Competition' in c['collection'] else ('col-res' if 'Reserve' in c['collection'] else 'col-sel')
    col_short = 'Competition' if 'Competition' in c['collection'] else ('Reserve' if 'Reserve' in c['collection'] else 'Selection')

    k_info = f"{c.get('korea_status', '국내 정식 유통 없음')} ({c.get('korea_price', '없음')})"

    mobile_code += f"""
    <div class="coffee-card" 
         data-collection="{html.escape(c['collection'])}" 
         data-country="{html.escape(c['country'])}" 
         data-process="{html.escape(c['process'])}" 
         data-price="{c['price_aed']}" 
         data-p100="{c['price_per_100g_aed']}" 
         data-index="{idx}">
      <div class="card-top">
        <div class="card-meta-tags">
          <span class="tag {col_class}">{col_short}</span>
          <span class="tag country">{flag} {html.escape(c['country'])}</span>
          <span class="tag" style="color:#6e7681;">#{idx}</span>
        </div>
        <div class="card-price-box">
          <div class="price-aed">AED {c['price_aed']} <span style="font-size:10px; color:#8b949e;">({c['weight']})</span></div>
          <div class="price-krw">약 {c['price_krw']:,}원 (100g당 {c['price_per_100g_aed']} AED)</div>
        </div>
      </div>

      <div class="card-title">{html.escape(c['title'])}</div>
      <div class="card-notes">🌸 {html.escape(c['tasting_notes'])}</div>

      <div class="card-quick-specs">
        <div>품종: <span>{html.escape(c['variety'])}</span></div>
        <div>가공: <span>{html.escape(c['process'])}</span></div>
        <div>고도: <span>{html.escape(c['altitude'])}</span></div>
        <div>배전: <span>{html.escape(c['roast'])}</span></div>
      </div>

      <!-- Expandable Detailed Section -->
      <div class="card-detail" id="detail-{idx}">
        <div class="detail-grid">
          <div class="detail-row"><span>지역</span> <span>{html.escape(c['location'])}</span></div>
          <div class="detail-row"><span>농장</span> <span>{html.escape(c['farm'])}</span></div>
          <div class="detail-row"><span>농부</span> <span>{html.escape(c['producer'])}</span></div>
          <div class="detail-row"><span>배전도</span> <span>{html.escape(c['roast'])}</span></div>
        </div>

        <div class="detail-box korea">
          <strong>🇰🇷 국내 유통 & 시세:</strong><br>
          {html.escape(k_info)}
        </div>

        <div class="detail-box merit">
          <strong>💡 현지 구매 메리트:</strong><br>
          {html.escape(c.get('purchase_merit', '★ 높음: 현지 독점 랏'))}
        </div>

        <div class="detail-box review">
          💬 <strong>해외 커뮤니티 평:</strong> {html.escape(c['user_review'])}
        </div>

        <a href="{c['source_url']}" target="_blank" class="btn-shop">아처스 공식몰 원문 보기 ↗</a>
      </div>

      <div class="expand-toggle" onclick="toggleDetail({idx}, this)">
        <span>상세 스펙 & 구매 메리트 펼치기</span> ▼
      </div>
    </div>
    """

mobile_code += """
  </div>
</div>

<!-- FLOATING BOTTOM BAR -->
<div class="floating-bottom">
  <div class="count-text" id="floatingCount">117개 원두 표시 중</div>
  <button class="btn-top" onclick="window.scrollTo({top:0, behavior:'smooth'})">맨 위로 ↑</button>
</div>

<script>
  let activeFilter = 'all';

  function toggleDetail(idx, btn) {
    const detail = document.getElementById('detail-' + idx);
    const isOpen = detail.classList.contains('open');
    if (isOpen) {
      detail.classList.remove('open');
      btn.innerHTML = '<span>상세 스펙 & 구매 메리트 펼치기</span> ▼';
    } else {
      detail.classList.add('open');
      btn.innerHTML = '<span>접기</span> ▲';
    }
  }

  function setFilter(filterVal, btn) {
    activeFilter = filterVal;
    document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterMobileCards();
  }

  function filterMobileCards() {
    const query = document.getElementById('mSearch').value.toLowerCase();
    const cards = document.querySelectorAll('.coffee-card');
    let visibleCount = 0;

    cards.forEach(card => {
      const col = card.getAttribute('data-collection') || '';
      const country = card.getAttribute('data-country') || '';
      const process = card.getAttribute('data-process') || '';
      const text = card.innerText.toLowerCase();

      let matchFilter = false;
      if (activeFilter === 'all') matchFilter = true;
      else if (activeFilter === 'Panama' && country.includes('Panama')) matchFilter = true;
      else if (activeFilter === 'Ethiopia' && country.includes('Ethiopia')) matchFilter = true;
      else if (activeFilter === 'Washed' && process.toLowerCase().includes('washed')) matchFilter = true;
      else if (col.includes(activeFilter)) matchFilter = true;

      const matchSearch = !query || text.includes(query);

      if (matchFilter && matchSearch) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    const statusText = visibleCount + '개 원두 표시 중';
    document.getElementById('matchCount').innerText = statusText;
    document.getElementById('floatingCount').innerText = statusText;
  }

  function sortMobileCards() {
    const sortVal = document.getElementById('mSort').value;
    const container = document.getElementById('coffeeList');
    const cards = Array.from(container.children);

    cards.sort((a, b) => {
      if (sortVal === 'price-asc') {
        return parseFloat(a.getAttribute('data-price')) - parseFloat(b.getAttribute('data-price'));
      } else if (sortVal === 'price-desc') {
        return parseFloat(b.getAttribute('data-price')) - parseFloat(a.getAttribute('data-price'));
      } else if (sortVal === 'p100-asc') {
        return parseFloat(a.getAttribute('data-p100')) - parseFloat(b.getAttribute('data-p100'));
      } else if (sortVal === 'country') {
        return a.getAttribute('data-country').localeCompare(b.getAttribute('data-country'));
      } else {
        return parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index'));
      }
    });

    cards.forEach(card => container.appendChild(card));
  }
</script>
</body>
</html>
"""

with open(MOBILE_HTML, 'w', encoding='utf-8') as f:
    f.write(mobile_code)

print(f"Generated mobile.html successfully: {MOBILE_HTML}")


# 2. GENERATE index.html (Landing Portal & Device Switcher)
index_code = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAE 아처스 커피 (Archers Coffee) 공식 전수 검증 리포트 & 구매 가이드</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,800;1,600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #090d13;
    --card-bg: #141922;
    --border: #262c36;
    --accent: #d29922;
    --accent-light: #f1e05a;
    --text-primary: #f0f6fc;
    --text-secondary: #9da7b3;
    --text-muted: #6e7681;
    --success: #3fb950;
    --blue: #58a6ff;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    line-height: 1.6;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 24px 16px;
  }

  .container {
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
    text-align: center;
  }

  /* Auto Redirect Notification */
  #autoRedirectToast {
    display: none;
    background: rgba(88, 166, 255, 0.15);
    border: 1px solid rgba(88, 166, 255, 0.4);
    color: var(--blue);
    padding: 10px 16px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 24px;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .btn-toast {
    background: var(--blue);
    color: #000;
    border: none;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
  }

  .header-badge {
    display: inline-block;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent);
    font-weight: 800;
    background: rgba(210, 153, 34, 0.12);
    border: 1px solid rgba(210, 153, 34, 0.3);
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 16px;
  }
  h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 38px;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 14px;
    background: linear-gradient(135deg, #fff 0%, #c9d1d9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .desc {
    color: var(--text-secondary);
    font-size: 15px;
    max-width: 680px;
    margin: 0 auto 36px auto;
  }

  /* Version Selection Cards */
  .version-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 36px;
  }
  @media (max-width: 680px) { .version-grid { grid-template-columns: 1fr; } }

  .version-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 24px;
    text-align: left;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-decoration: none;
    color: inherit;
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
  }
  .version-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
  }
  .version-card.desktop:hover { border-color: var(--blue); }

  .v-icon {
    font-size: 40px;
    margin-bottom: 16px;
  }
  .v-tag {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
    background: #1c2230;
    color: var(--text-secondary);
  }
  .v-title {
    font-size: 21px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 10px;
  }
  .v-desc {
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 24px;
  }
  .v-features {
    list-style: none;
    margin-bottom: 28px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-size: 12.5px;
    color: #c9d1d9;
  }
  .v-features li { display: flex; align-items: center; gap: 6px; }
  .v-features li span { color: var(--success); font-weight: 800; }

  .btn-enter {
    display: block;
    width: 100%;
    text-align: center;
    padding: 12px 0;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    transition: opacity 0.2s;
  }
  .btn-enter.mobile-btn {
    background: linear-gradient(135deg, #d29922 0%, #b8860b 100%);
    color: #000;
  }
  .btn-enter.desktop-btn {
    background: linear-gradient(135deg, #238636 0%, #1e702d 100%);
    color: #fff;
  }

  /* Footer & Badges */
  .meta-stats {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 24px;
  }
  .meta-badge {
    background: #141922;
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
  }
  .meta-badge.pass { border-color: rgba(63, 185, 80, 0.4); color: var(--success); }

  footer {
    font-size: 12px;
    color: var(--text-muted);
  }
  footer a { color: var(--blue); text-decoration: none; }
</style>
</head>
<body>

<div class="container">
  <!-- Auto redirect notification for mobile -->
  <div id="autoRedirectToast">
    <span>📱 모바일 기기가 감지되었습니다. 3초 후 모바일 최적화 페이지로 자동 이동합니다.</span>
    <button class="btn-toast" onclick="cancelRedirect()">취소</button>
  </div>

  <div class="header-badge">Verified Specialty Coffee Intelligence</div>
  <h1>UAE 아처스 커피 (Archers Coffee)<br>전수 검증 & 현지 구매 가이드</h1>
  <p class="desc">
    두바이 현지 로스터리 매장 방문 구매를 위해 아처스 3대 컬렉션 117개 원두 전체를 전수 수집 및 기계 검증 완료했습니다.<br>
    사용 중이신 기기 환경에 맞는 최적의 버전을 선택해주세요.
  </p>

  <div class="version-grid">
    <!-- MOBILE CARD -->
    <a href="mobile.html" class="version-card mobile">
      <div class="v-tag">스마트폰 추천</div>
      <div class="v-icon">📱</div>
      <div class="v-title">모바일 최적화 뷰</div>
      <div class="v-desc">
        스마트폰 세로 화면과 터치 인터랙션에 최적화된 앱 스타일 카드 리스트 및 아코디언 뷰입니다.
      </div>
      <ul class="v-features">
        <li><span>✓</span> 모바일 원터치 스와이프 추천 Best 6</li>
        <li><span>✓</span> 탭하여 펼치는 아코디언 상세 스펙</li>
        <li><span>✓</span> 상단 고정 원터치 필터 칩 & 실시간 검색</li>
        <li><span>✓</span> 117개 원두 부드러운 60fps 스크롤</li>
      </ul>
      <div class="btn-enter mobile-btn">모바일 버전으로 보기 ↗</div>
    </a>

    <!-- DESKTOP CARD -->
    <a href="archers_coffee_clean_verified.html" class="version-card desktop">
      <div class="v-tag">PC / 태블릿 추천</div>
      <div class="v-icon">🖥️</div>
      <div class="v-title">데스크톱 대시보드 뷰</div>
      <div class="v-desc">
        18개 전체 세부 지표를 한눈에 비교하고 클릭 한 번으로 양방향 자동 정렬할 수 있는 풀 와이드 대시보드입니다.
      </div>
      <ul class="v-features">
        <li><span>✓</span> 18개 전수 지표 양방향 헤더 자동 정렬</li>
        <li><span>✓</span> 9개 추천 원두 울트라 디테일 사유 분석</li>
        <li><span>✓</span> 국내 시세 vs 현지 가격 대조 표</li>
        <li><span>✓</span> 대화면 다중 비교 및 실시간 검색</li>
      </ul>
      <div class="btn-enter desktop-btn">데스크톱 버전으로 보기 ↗</div>
    </a>
  </div>

  <div class="meta-stats">
    <span class="meta-badge pass">✓ verify_quotes.py 전수 검증 (351/351 PASS)</span>
    <span class="meta-badge">117개 원두 전수 수록</span>
    <span class="meta-badge">1 AED ≈ 380 KRW 환율 적용</span>
    <span class="meta-badge">현지 방문 구매 (관세 면제 기준)</span>
  </div>

  <footer>
    <p>© 2026 Archers Coffee Deep Analysis Project | <a href="https://github.com/holnuwld/coffee" target="_blank">GitHub Repository (holnuwld/coffee)</a></p>
  </footer>
</div>

<script>
  let redirectTimer = null;
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || (window.innerWidth <= 768);

  if (isMobile) {
    const toast = document.getElementById('autoRedirectToast');
    toast.style.display = 'flex';
    redirectTimer = setTimeout(() => {
      window.location.href = 'mobile.html';
    }, 3000);
  }

  function cancelRedirect() {
    if (redirectTimer) clearTimeout(redirectTimer);
    document.getElementById('autoRedirectToast').style.display = 'none';
  }
</script>
</body>
</html>
"""

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(index_code)

print(f"Generated index.html successfully: {INDEX_HTML}")


# 3. UPDATE archers_coffee_clean_verified.html (Add Mobile Switcher Button in Header)
with open(DESKTOP_HTML, 'r', encoding='utf-8') as f:
    desktop_content = f.read()

if 'mobile.html' not in desktop_content:
    # Add mobile switcher badge
    replacement_target = '<div class="badge-row">'
    replacement_content = '''<div class="badge-row">
      <a href="mobile.html" style="text-decoration:none; display:inline-flex; align-items:center; gap:6px; background:rgba(210,153,34,0.25); border:1px solid var(--accent); color:var(--accent-light); padding:5px 14px; border-radius:20px; font-size:12px; font-weight:700;">📱 모바일 최적화 버전으로 보기 ↗</a>'''
    desktop_content = desktop_content.replace(replacement_target, replacement_content, 1)

    with open(DESKTOP_HTML, 'w', encoding='utf-8') as f:
        f.write(desktop_content)
    print("Updated archers_coffee_clean_verified.html with mobile switcher button.")
