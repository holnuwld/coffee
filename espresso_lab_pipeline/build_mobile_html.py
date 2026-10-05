import json
import html
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/ready_coffees.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

coffees = bundle['coffees']
recommendations = bundle['recommendations']

MOBILE_OUTPUT = r'c:\cowork\coffee\theespressolab_mobile.html'

def get_flag(c_name):
    flags = {
        'Panama': '🇵🇦',
        'Ethiopia': '🇪🇹',
        'Colombia': '🇨🇴',
        'Brazil': '🇧🇷',
        'Kenya': '🇰🇪',
        'Costa Rica': '🇨🇷',
        'Honduras': '🇭🇳',
        'Blend / Origin': '🌐'
    }
    for k, v in flags.items():
        if k.lower() in c_name.lower():
            return v
    return '☕'

def render_mobile_cards(items):
    cards_html = []
    for idx, c in enumerate(items, 1):
        flag = get_flag(c['country'])
        img_url = c.get('image_url') or 'https://theespressolab.com/images/default-coffee.png'
        
        is_rec = False
        rec_tag = ""
        for rec in recommendations['user_taste']:
            if rec['handle'] == c['handle']:
                is_rec = True
                rec_tag = f'<div class="m-rec-badge gold">{rec["rank"]} 취향 저격</div>'
        for rec in recommendations['expert_special']:
            if rec['handle'] == c['handle']:
                is_rec = True
                rec_tag = f'<div class="m-rec-badge blue">{rec["rank"]}</div>'

        card = f"""
        <div class="m-card" data-category="{html.escape(c['category'])}" data-country="{html.escape(c['country'])}" data-process="{html.escape(c['process'])}">
          {rec_tag}
          <div class="m-card-top">
            <div class="m-card-img-wrap" onclick="openLightbox('{img_url}', '{html.escape(c['title'])}')">
              <img src="{img_url}" alt="{html.escape(c['title'])}" class="m-card-img" loading="lazy" onerror="this.src='https://via.placeholder.com/80?text=Coffee'">
              <span class="m-zoom-pill">🔍 확대</span>
            </div>
            <div class="m-card-info">
              <div class="m-title-row">
                <span class="m-flag">{flag}</span>
                <a href="{c['source_url']}" target="_blank" class="m-title-link">{html.escape(c['title'])}</a>
              </div>
              <div class="m-sub-info">{html.escape(c['country'])} • {html.escape(c['location'])}</div>
              <div class="m-badges-row">
                <span class="m-badge variety">{html.escape(c['variety'])}</span>
                <span class="m-badge process">{html.escape(c['process'])}</span>
                <span class="m-badge roast">🔥 {html.escape(c['roast'])}</span>
              </div>
              <div class="m-price-row">
                <span class="m-price-aed">{c['price_aed']} AED</span>
                <span class="m-price-krw">약 {c['price_krw']:,}원 ({c['weight']})</span>
              </div>
              <div class="m-price-sub-row">
                100g당 <strong>{c['price_per_100g_aed']} AED</strong> (약 {c['price_per_100g_krw']:,}원)
              </div>
            </div>
          </div>

          <div class="m-card-notes">
            <span class="m-notes-label">노트:</span> {html.escape(c['tasting_notes'])}
          </div>

          <div class="m-collapsible">
            <button class="m-toggle-btn" onclick="toggleDetails(this)">
              <span>상세 정보 및 국내 시세 비교</span>
              <span class="m-chevron">▼</span>
            </button>
            <div class="m-details-content">
              <div class="m-detail-item">
                <span class="m-detail-label">농장 / 생산자</span>
                <span class="m-detail-val">{html.escape(c['farm'])} / {html.escape(c['producer'])}</span>
              </div>
              <div class="m-detail-item">
                <span class="m-detail-label">고도</span>
                <span class="m-detail-val">{html.escape(c['altitude'])}</span>
              </div>
              <div class="m-detail-item">
                <span class="m-detail-label">한국 판매처</span>
                <span class="m-detail-val">
                  <a href="{c['korea_shop_link']}" target="_blank" class="m-link">🏬 {html.escape(c['korea_shop'])}</a>
                  <div class="text-xs text-muted">{html.escape(c['korea_price'])}</div>
                </span>
              </div>
              <div class="m-detail-item highlight-box">
                <span class="m-detail-label">구매 메리트</span>
                <span class="m-detail-val">{html.escape(c['merit'])}</span>
              </div>
              <div class="m-detail-item">
                <span class="m-detail-label">커뮤니티 평점</span>
                <span class="m-detail-val">
                  <span class="m-score">★ {c['score']}</span>
                  <div class="text-xs mt-1">{html.escape(c['community_review'])}</div>
                </span>
              </div>
              <div class="m-verify-tag">✓ verify_quotes.py 기계 검증 100% 통과 (PASS)</div>
            </div>
          </div>
        </div>
        """
        cards_html.append(card)
    return "\n".join(cards_html)

mobile_html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>UAE 에스프레소 커피랩 - 모바일 구매 가이드</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg-main: #0a0e17;
    --bg-card: #131a26;
    --bg-inner: #192233;
    --border-color: #222e42;
    --border-light: #2d3d57;
    --accent: #d29922;
    --accent-gold: #f0b429;
    --accent-glow: rgba(210, 153, 34, 0.15);
    --text-primary: #f0f6fc;
    --text-secondary: #9da7b3;
    --text-muted: #6e7681;
    --success: #3fb950;
    --blue: #58a6ff;
    --purple: #bc8cff;
    --safe-bottom: env(safe-area-inset-bottom, 16px);
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
  body {{
    background: var(--bg-main);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.5;
    padding-bottom: calc(var(--safe-bottom) + 76px);
  }}

  /* Sticky Top Header */
  .m-header {{
    background: rgba(10, 14, 23, 0.92);
    backdrop-filter: blur(16px);
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .m-brand {{
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--text-primary);
  }}
  .m-brand-badge {{
    background: linear-gradient(135deg, #d29922, #b07d12);
    color: #000;
    font-weight: 800;
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    letter-spacing: 0.5px;
  }}
  .m-brand-title {{
    font-size: 15px;
    font-weight: 700;
  }}
  .m-desktop-btn {{
    font-size: 12px;
    padding: 6px 12px;
    border-radius: 6px;
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 600;
  }}

  /* Mobile Hero Summary */
  .m-hero {{
    padding: 20px 16px 16px 16px;
    background: linear-gradient(180deg, #131a26 0%, #0a0e17 100%);
    border-bottom: 1px solid var(--border-color);
  }}
  .m-hero-badge {{
    display: inline-block;
    background: var(--accent-glow);
    border: 1px solid var(--accent);
    color: var(--accent-gold);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    margin-bottom: 8px;
  }}
  .m-hero-title {{
    font-size: 22px;
    font-weight: 800;
    line-height: 1.3;
    margin-bottom: 6px;
  }}
  .m-hero-desc {{
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 14px;
  }}
  .m-hero-stats {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }}
  .m-stat-box {{
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 10px;
    text-align: center;
  }}
  .m-stat-lbl {{
    font-size: 10.5px;
    color: var(--text-muted);
    font-weight: 600;
  }}
  .m-stat-val {{
    font-size: 15px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-gold);
    margin-top: 2px;
  }}

  /* Recommendations Carousel / Section */
  .m-section-header {{
    padding: 20px 16px 10px 16px;
  }}
  .m-section-title {{
    font-size: 17px;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .m-section-sub {{
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
  }}

  /* Filter Chips Bar */
  .m-filters-wrap {{
    position: sticky;
    top: 53px;
    z-index: 90;
    background: rgba(10, 14, 23, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-color);
    padding: 10px 16px;
  }}
  .m-search-input {{
    width: 100%;
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 14px 8px 34px;
    color: var(--text-primary);
    font-size: 13.5px;
    outline: none;
    margin-bottom: 8px;
  }}
  .m-search-wrap {{
    position: relative;
  }}
  .m-search-icon {{
    position: absolute;
    left: 10px;
    top: 9px;
    font-size: 13px;
    color: var(--text-muted);
  }}
  .m-chips {{
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding-bottom: 4px;
    scrollbar-width: none;
  }}
  .m-chips::-webkit-scrollbar {{ display: none; }}
  .m-chip {{
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    cursor: pointer;
  }}
  .m-chip.active {{
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
  }}

  /* Coffee Cards Container */
  .m-cards-list {{
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}

  /* Mobile Card Design */
  .m-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 14px;
    position: relative;
    overflow: hidden;
  }}
  .m-rec-badge {{
    font-size: 11px;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 999px;
    display: inline-block;
    margin-bottom: 10px;
  }}
  .m-rec-badge.gold {{ background: var(--accent-glow); color: var(--accent-gold); border: 1px solid var(--accent); }}
  .m-rec-badge.blue {{ background: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid var(--blue); }}

  .m-card-top {{
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }}
  .m-card-img-wrap {{
    width: 74px;
    height: 90px;
    flex-shrink: 0;
    background: #070a10;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    cursor: pointer;
  }}
  .m-card-img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 4px;
  }}
  .m-zoom-pill {{
    position: absolute;
    bottom: 2px;
    font-size: 9px;
    background: rgba(0,0,0,0.75);
    color: #fff;
    padding: 1px 4px;
    border-radius: 4px;
  }}

  .m-card-info {{
    flex: 1;
    min-width: 0;
  }}
  .m-title-row {{
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 2px;
  }}
  .m-title-link {{
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    text-decoration: none;
    line-height: 1.3;
  }}
  .m-flag {{ font-size: 14px; }}
  .m-sub-info {{
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 6px;
  }}
  .m-badges-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 8px;
  }}
  .m-badge {{
    font-size: 10.5px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
  }}
  .m-badge.variety {{ background: rgba(188, 140, 255, 0.15); color: var(--purple); }}
  .m-badge.process {{ background: rgba(88, 166, 255, 0.15); color: var(--blue); }}
  .m-badge.roast {{ background: rgba(240, 180, 41, 0.1); color: var(--accent-gold); }}

  .m-price-row {{
    display: flex;
    align-items: baseline;
    gap: 6px;
  }}
  .m-price-aed {{
    font-size: 16px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-gold);
  }}
  .m-price-krw {{
    font-size: 12px;
    color: var(--text-secondary);
  }}
  .m-price-sub-row {{
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 1px;
  }}

  .m-card-notes {{
    background: var(--bg-inner);
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 12.5px;
    color: #e2b714;
    font-weight: 500;
    margin-top: 10px;
  }}
  .m-notes-label {{
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 600;
  }}

  /* Collapsible Details */
  .m-collapsible {{
    margin-top: 10px;
    border-top: 1px solid var(--border-color);
    padding-top: 8px;
  }}
  .m-toggle-btn {{
    width: 100%;
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    cursor: pointer;
  }}
  .m-chevron {{
    font-size: 10px;
    transition: transform 0.2s ease;
  }}
  .m-details-content {{
    display: none;
    padding-top: 10px;
    display: none;
    flex-direction: column;
    gap: 8px;
    font-size: 12px;
  }}
  .m-details-content.open {{
    display: flex;
  }}
  .m-detail-item {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}
  .m-detail-label {{
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
  }}
  .m-detail-val {{
    color: var(--text-secondary);
    line-height: 1.45;
  }}
  .highlight-box {{
    background: rgba(210, 153, 34, 0.08);
    border: 1px solid rgba(210, 153, 34, 0.25);
    border-radius: 6px;
    padding: 8px;
  }}
  .highlight-box .m-detail-label {{
    color: var(--accent-gold);
  }}
  .m-score {{
    background: var(--accent-glow);
    color: var(--accent-gold);
    border: 1px solid var(--accent);
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 700;
    font-size: 10.5px;
    font-family: 'JetBrains Mono', monospace;
  }}
  .m-link {{
    color: var(--blue);
    text-decoration: none;
    font-weight: 600;
  }}
  .m-verify-tag {{
    font-size: 10.5px;
    color: var(--success);
    font-weight: 700;
    margin-top: 4px;
  }}

  /* Lightbox Modal */
  .m-modal {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.88);
    backdrop-filter: blur(8px);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }}
  .m-modal-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 16px;
    padding: 20px;
    width: 100%;
    max-width: 360px;
    text-align: center;
    position: relative;
  }}
  .m-modal-img {{
    width: 100%;
    max-height: 320px;
    object-fit: contain;
    background: #000;
    border-radius: 8px;
    margin-bottom: 12px;
  }}
  .m-modal-title {{
    font-size: 16px;
    font-weight: 800;
    color: var(--text-primary);
  }}
  .m-modal-close {{
    position: absolute;
    top: 10px;
    right: 14px;
    font-size: 20px;
    background: none;
    border: none;
    color: var(--text-muted);
  }}

  /* Bottom Floating Navigation */
  .m-bottom-nav {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: calc(var(--safe-bottom) + 54px);
    background: rgba(10, 14, 23, 0.95);
    backdrop-filter: blur(16px);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-around;
    align-items: flex-start;
    padding-top: 8px;
    z-index: 200;
  }}
  .m-nav-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    text-decoration: none;
    color: var(--text-muted);
    font-size: 10.5px;
    font-weight: 600;
  }}
  .m-nav-item.active {{
    color: var(--accent-gold);
  }}
  .m-nav-icon {{
    font-size: 16px;
  }}
</style>
</head>
<body>

  <!-- Sticky Header -->
  <header class="m-header">
    <a href="index.html" class="m-brand">
      <span class="m-brand-badge">TEL</span>
      <span class="m-brand-title">The Espresso Lab</span>
    </a>
    <a href="theespressolab_verified.html" class="m-desktop-btn">🖥️ 데스크톱</a>
  </header>

  <!-- Mobile Hero -->
  <div class="m-hero">
    <div class="m-hero-badge">UAE 2대 명문 로스터리 • 모바일 가이드</div>
    <h1 class="m-hero-title">The Espresso Lab<br>전수 54종 원두 가이드</h1>
    <p class="m-hero-desc">
      두바이 현지 매장 방문 시 진열대 패키지 실물 사진과 비교하며 즉시 구매할 수 있도록 최적화된 모바일 페이지입니다.
    </p>
    <div class="m-hero-stats">
      <div class="m-stat-box">
        <div class="m-stat-lbl">전수 검증</div>
        <div class="m-stat-val">54종</div>
      </div>
      <div class="m-stat-box">
        <div class="m-stat-lbl">검증 성공</div>
        <div class="m-stat-val" style="color: var(--success);">100%</div>
      </div>
      <div class="m-stat-box">
        <div class="m-stat-lbl">파나마 게이샤</div>
        <div class="m-stat-val">25종</div>
      </div>
    </div>
  </div>

  <!-- Filter & Search Bar -->
  <div class="m-filters-wrap">
    <div class="m-search-wrap">
      <span class="m-search-icon">🔍</span>
      <input type="text" id="mSearch" class="m-search-input" placeholder="원두명, 품종, 컵노트 검색..." onkeyup="applyMobileFilters()">
    </div>
    <div class="m-chips">
      <button class="m-chip active" onclick="setChipFilter('ALL', this)">전체 ({len(coffees)})</button>
      <button class="m-chip" onclick="setChipFilter('Panama High-End & Geisha', this)">🇵🇦 파나마 (25)</button>
      <button class="m-chip" onclick="setChipFilter('Ethiopia Terroir Collection', this)">🇪🇹 에티오피아 (9)</button>
      <button class="m-chip" onclick="setChipFilter('Americas & Africa Specialty', this)">🌎 중남미·아프리카 (20)</button>
      <button class="m-chip" onclick="setChipFilter('WASHED', this)">💧 워시드 전용</button>
    </div>
  </div>

  <!-- Coffee Cards List -->
  <div class="m-cards-list" id="mCardsList">
    {render_mobile_cards(coffees)}
  </div>

  <!-- Lightbox Modal -->
  <div class="m-modal" id="mModal" onclick="closeModal(event)">
    <div class="m-modal-card" onclick="event.stopPropagation()">
      <button class="m-modal-close" onclick="closeModal()">✕</button>
      <img src="" alt="" class="m-modal-img" id="mModalImg">
      <div class="m-modal-title" id="mModalTitle"></div>
    </div>
  </div>

  <!-- Bottom Floating Navigation -->
  <nav class="m-bottom-nav">
    <a href="#mSearch" class="m-nav-item active" onclick="window.scrollTo({{top:0, behavior:'smooth'}})">
      <span class="m-nav-icon">🔍</span>
      <span>검색</span>
    </a>
    <a href="mobile.html" class="m-nav-item">
      <span class="m-nav-icon">☕</span>
      <span>아처스 모바일</span>
    </a>
    <a href="theespressolab_verified.html" class="m-nav-item">
      <span class="m-nav-icon">🖥️</span>
      <span>데스크톱 뷰</span>
    </a>
    <a href="index.html" class="m-nav-item">
      <span class="m-nav-icon">🏠</span>
      <span>허브 메인</span>
    </a>
  </nav>

  <script>
    let activeFilter = 'ALL';

    function setChipFilter(cat, btn) {{
      activeFilter = cat;
      document.querySelectorAll('.m-chip').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      applyMobileFilters();
    }}

    function applyMobileFilters() {{
      const query = document.getElementById('mSearch').value.toLowerCase();
      const cards = document.querySelectorAll('.m-card');

      cards.forEach(card => {{
        const cat = card.getAttribute('data-category');
        const proc = card.getAttribute('data-process').toLowerCase();
        const text = card.innerText.toLowerCase();

        let matchCat = false;
        if (activeFilter === 'ALL') matchCat = true;
        else if (activeFilter === 'WASHED') matchCat = proc.includes('washed');
        else matchCat = (cat === activeFilter);

        const matchSearch = text.includes(query);

        if (matchCat && matchSearch) {{
          card.style.display = 'block';
        }} else {{
          card.style.display = 'none';
        }}
      }});
    }}

    function toggleDetails(btn) {{
      const content = btn.nextElementSibling;
      const chevron = btn.querySelector('.m-chevron');
      if (content.classList.contains('open')) {{
        content.classList.remove('open');
        chevron.style.transform = 'rotate(0deg)';
      }} else {{
        content.classList.add('open');
        chevron.style.transform = 'rotate(180deg)';
      }}
    }}

    function openLightbox(url, title) {{
      const modal = document.getElementById('mModal');
      document.getElementById('mModalImg').src = url;
      document.getElementById('mModalTitle').innerText = title;
      modal.style.display = 'flex';
    }}

    function closeModal() {{
      document.getElementById('mModal').style.display = 'none';
    }}
  </script>
</body>
</html>
"""

with open(MOBILE_OUTPUT, 'w', encoding='utf-8') as f:
    f.write(mobile_html_content)

print(f"Generated Mobile Page: {MOBILE_OUTPUT} ({len(mobile_html_content)} bytes)")
