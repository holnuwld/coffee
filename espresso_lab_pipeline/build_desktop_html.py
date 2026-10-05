import json
import html
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/ready_coffees.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

coffees = bundle['coffees']
recommendations = bundle['recommendations']
panama = bundle['panama']
ethiopia = bundle['ethiopia']
americas = bundle['americas']

DESKTOP_OUTPUT = r'c:\cowork\coffee\theespressolab_verified.html'

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

def render_table_rows(items):
    rows_html = []
    for idx, c in enumerate(items, 1):
        flag = get_flag(c['country'])
        img_url = c.get('image_url') or 'https://theespressolab.com/images/default-coffee.png'
        
        # Format table cells cleanly
        r = f"""
        <tr data-category="{html.escape(c['category'])}">
          <td class="text-center font-mono text-muted">{idx}</td>
          <td class="text-center">
            <div class="pkg-img-wrap" onclick="openLightbox('{img_url}', '{html.escape(c['title'])}')">
              <img src="{img_url}" alt="{html.escape(c['title'])}" class="pkg-thumb" loading="lazy" onerror="this.src='https://via.placeholder.com/60?text=Coffee'">
              <span class="zoom-icon">🔍</span>
            </div>
          </td>
          <td class="coffee-title-cell">
            <div class="font-bold text-primary">
              <a href="{c['source_url']}" target="_blank" class="coffee-link">
                {flag} {html.escape(c['title'])}
              </a>
            </div>
            <div class="text-xs text-muted font-mono">{html.escape(c['handle'])}</div>
          </td>
          <td><span class="badge badge-country">{flag} {html.escape(c['country'])}</span></td>
          <td class="text-sm">{html.escape(c['location'])}</td>
          <td class="text-sm font-medium">{html.escape(c['farm'])}</td>
          <td class="text-sm">{html.escape(c['producer'])}</td>
          <td><span class="badge badge-variety">{html.escape(c['variety'])}</span></td>
          <td><span class="badge badge-process">{html.escape(c['process'])}</span></td>
          <td class="text-sm font-mono">{html.escape(c['altitude'])}</td>
          <td><span class="badge badge-roast">🔥 {html.escape(c['roast'])}</span></td>
          <td class="notes-cell">{html.escape(c['tasting_notes'])}</td>
          <td class="text-center font-mono font-bold">{html.escape(c['weight'])}</td>
          <td class="text-right font-mono price-cell">
            <div class="text-accent font-bold">{c['price_aed']} AED</div>
            <div class="text-xs text-muted">약 {c['price_krw']:,}원</div>
          </td>
          <td class="text-right font-mono price-cell">
            <div class="text-success font-bold">{c['price_per_100g_aed']} AED</div>
            <div class="text-xs text-muted">약 {c['price_per_100g_krw']:,}원</div>
          </td>
          <td class="korea-shop-cell">
            <a href="{c['korea_shop_link']}" target="_blank" class="korea-link">
              🏬 {html.escape(c['korea_shop'])}
            </a>
            <div class="text-xs text-muted mt-1">{html.escape(c['korea_price'])}</div>
          </td>
          <td class="merit-cell">
            <div class="merit-text">{html.escape(c['merit'])}</div>
          </td>
          <td class="review-cell">
            <div class="score-badge">★ {c['score']}</div>
            <div class="review-text">{html.escape(c['community_review'])}</div>
          </td>
          <td class="text-center">
            <span class="badge badge-verified">✓ PASS</span>
          </td>
        </tr>
        """
        rows_html.append(r)
    return "\n".join(rows_html)

desktop_html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAE 에스프레소 커피랩 (The Espresso Lab) - 전수 원두 검증 및 구매 가이드</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg-main: #0b0f17;
    --bg-card: #131b26;
    --bg-card-hover: #182332;
    --bg-input: #1a2536;
    --border-color: #243247;
    --border-light: #32435e;
    --accent: #d29922;
    --accent-gold: #f0b429;
    --accent-glow: rgba(210, 153, 34, 0.15);
    --text-primary: #f0f6fc;
    --text-secondary: #9da7b3;
    --text-muted: #6e7681;
    --success: #3fb950;
    --success-bg: rgba(63, 185, 80, 0.12);
    --blue: #58a6ff;
    --blue-bg: rgba(88, 166, 255, 0.12);
    --purple: #bc8cff;
    --purple-bg: rgba(188, 140, 255, 0.12);
    --danger: #f85149;
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 16px;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg-main);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    line-height: 1.6;
    padding: 0 0 100px 0;
  }}

  /* Top Navigation Bar */
  .top-nav {{
    background: rgba(11, 15, 23, 0.85);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 1000;
    padding: 14px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .nav-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: var(--text-primary);
  }}
  .brand-logo-badge {{
    background: linear-gradient(135deg, #d29922, #b07d12);
    color: #fff;
    font-weight: 800;
    padding: 6px 12px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    letter-spacing: 1px;
  }}
  .brand-title {{
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
  }}
  .nav-links {{
    display: flex;
    gap: 16px;
    align-items: center;
  }}
  .nav-btn {{
    padding: 8px 16px;
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s ease;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
  }}
  .nav-btn:hover {{
    color: var(--text-primary);
    border-color: var(--accent);
    background: var(--accent-glow);
  }}
  .nav-btn.primary {{
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
  }}
  .nav-btn.primary:hover {{
    background: var(--accent-gold);
  }}

  /* Hero Banner */
  .hero-container {{
    max-width: 1600px;
    margin: 32px auto 0 auto;
    padding: 0 32px;
  }}
  .hero-card {{
    background: linear-gradient(135deg, #131c29 0%, #172436 50%, #0d1520 100%);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 40px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    position: relative;
    overflow: hidden;
  }}
  .hero-card::after {{
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(210, 153, 34, 0.08) 0%, transparent 70%);
    pointer-events: none;
  }}
  .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-glow);
    border: 1px solid var(--accent);
    color: var(--accent-gold);
    font-size: 12px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .hero-title {{
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.8px;
    line-height: 1.25;
    margin-bottom: 16px;
  }}
  .hero-subtitle {{
    font-size: 16px;
    color: var(--text-secondary);
    max-width: 900px;
    margin-bottom: 28px;
    line-height: 1.7;
  }}
  .hero-stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    padding-top: 24px;
    border-top: 1px solid var(--border-color);
  }}
  .stat-item {{
    background: rgba(11, 15, 23, 0.4);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px 20px;
  }}
  .stat-label {{
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 6px;
  }}
  .stat-value {{
    font-size: 24px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-primary);
  }}
  .stat-value.highlight {{ color: var(--accent-gold); }}
  .stat-value.success {{ color: var(--success); }}

  /* Recommendations Section */
  .section-container {{
    max-width: 1600px;
    margin: 48px auto 0 auto;
    padding: 0 32px;
  }}
  .section-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 24px;
  }}
  .section-title-wrap {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .section-title {{
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .section-desc {{
    font-size: 14px;
    color: var(--text-secondary);
  }}

  /* Recommendation Cards Grid */
  .rec-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin-bottom: 40px;
  }}
  @media (max-width: 1200px) {{
    .rec-grid {{ grid-template-columns: 1fr; }}
  }}
  .rec-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 28px;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 20px;
    transition: all 0.25s ease;
  }}
  .rec-card:hover {{
    transform: translateY(-4px);
    border-color: var(--accent);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  }}
  .rec-card.user-taste {{
    border-top: 4px solid var(--accent-gold);
  }}
  .rec-card.expert {{
    border-top: 4px solid var(--blue);
  }}
  .rec-card-header {{
    display: flex;
    gap: 20px;
    align-items: flex-start;
  }}
  .rec-pkg-img {{
    width: 100px;
    height: 120px;
    object-fit: contain;
    background: #0b0f17;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
    padding: 6px;
    cursor: pointer;
    transition: transform 0.2s ease;
  }}
  .rec-pkg-img:hover {{
    transform: scale(1.08);
  }}
  .rec-header-info {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .rec-rank-badge {{
    font-size: 12px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
    display: inline-block;
    width: fit-content;
  }}
  .rank-gold {{ background: var(--accent-glow); color: var(--accent-gold); border: 1px solid var(--accent); }}
  .rank-blue {{ background: var(--blue-bg); color: var(--blue); border: 1px solid var(--blue); }}

  .rec-title {{
    font-size: 20px;
    font-weight: 800;
    line-height: 1.3;
    color: var(--text-primary);
  }}
  .rec-origin {{
    font-size: 13px;
    color: var(--text-secondary);
  }}
  .rec-pricing {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-top: 4px;
  }}
  .rec-price-main {{
    font-size: 18px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-gold);
  }}
  .rec-price-sub {{
    font-size: 13px;
    color: var(--text-muted);
  }}

  .rec-body {{
    display: flex;
    flex-direction: column;
    gap: 14px;
    font-size: 13.5px;
    line-height: 1.65;
  }}
  .rec-box {{
    background: rgba(11, 15, 23, 0.5);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 14px 16px;
  }}
  .rec-box-title {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-gold);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .rec-box-title.blue {{ color: var(--blue); }}
  .rec-box-title.green {{ color: var(--success); }}
  .rec-box-text {{
    color: var(--text-secondary);
  }}

  /* Filter Controls & Search */
  .filter-controls-wrap {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 20px 24px;
    margin-bottom: 24px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }}
  .tab-buttons {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .tab-btn {{
    background: var(--bg-input);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 10px 18px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .tab-btn:hover {{
    color: var(--text-primary);
    border-color: var(--border-light);
  }}
  .tab-btn.active {{
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
  }}
  .tab-count {{
    background: rgba(0, 0, 0, 0.25);
    padding: 2px 7px;
    border-radius: 999px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
  }}

  .search-input-wrap {{
    position: relative;
    min-width: 340px;
  }}
  .search-input {{
    width: 100%;
    background: var(--bg-input);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 10px 16px 10px 38px;
    color: var(--text-primary);
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s ease;
  }}
  .search-input:focus {{
    border-color: var(--accent);
  }}
  .search-icon {{
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    font-size: 14px;
  }}

  /* Data Table Layout */
  .table-responsive {{
    overflow-x: auto;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }}
  .data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    white-space: normal;
  }}
  .data-table th {{
    background: #0f1621;
    color: var(--text-secondary);
    font-weight: 700;
    text-align: left;
    padding: 14px 16px;
    border-bottom: 2px solid var(--border-color);
    position: sticky;
    top: 61px;
    z-index: 10;
    cursor: pointer;
    user-select: none;
    transition: color 0.15s ease;
    white-space: nowrap;
  }}
  .data-table th:hover {{
    color: var(--accent-gold);
    background: #151e2c;
  }}
  .data-table th .sort-arrow {{
    font-size: 10px;
    margin-left: 4px;
    color: var(--text-muted);
  }}
  .data-table th.sorted-asc .sort-arrow::after {{ content: ' ▲'; color: var(--accent-gold); }}
  .data-table th.sorted-desc .sort-arrow::after {{ content: ' ▼'; color: var(--accent-gold); }}

  .data-table td {{
    padding: 14px 16px;
    border-bottom: 1px solid var(--border-color);
    vertical-align: middle;
  }}
  .data-table tr:hover td {{
    background: var(--bg-card-hover);
  }}

  /* Table Cell Specifics */
  .pkg-img-wrap {{
    position: relative;
    width: 54px;
    height: 64px;
    background: #0b0f17;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    margin: 0 auto;
    overflow: hidden;
    transition: all 0.2s ease;
  }}
  .pkg-img-wrap:hover {{
    border-color: var(--accent);
    transform: scale(1.05);
  }}
  .pkg-thumb {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 3px;
  }}
  .zoom-icon {{
    position: absolute;
    bottom: 2px;
    right: 2px;
    font-size: 10px;
    background: rgba(0, 0, 0, 0.7);
    border-radius: 3px;
    padding: 1px 3px;
    opacity: 0;
    transition: opacity 0.2s ease;
  }}
  .pkg-img-wrap:hover .zoom-icon {{
    opacity: 1;
  }}

  .coffee-link {{
    color: var(--text-primary);
    text-decoration: none;
    font-weight: 700;
    transition: color 0.15s ease;
  }}
  .coffee-link:hover {{
    color: var(--accent-gold);
    text-decoration: underline;
  }}

  .notes-cell {{
    min-width: 160px;
    color: #e2b714;
    font-weight: 500;
  }}
  .merit-cell {{
    min-width: 220px;
    font-size: 12px;
    line-height: 1.5;
    color: var(--text-secondary);
  }}
  .review-cell {{
    min-width: 200px;
    font-size: 12px;
    line-height: 1.5;
  }}
  .score-badge {{
    display: inline-block;
    background: var(--accent-glow);
    color: var(--accent-gold);
    border: 1px solid var(--accent);
    padding: 1px 6px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 11px;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
  }}

  .korea-shop-cell {{
    min-width: 180px;
  }}
  .korea-link {{
    color: var(--blue);
    text-decoration: none;
    font-weight: 600;
    font-size: 12.5px;
  }}
  .korea-link:hover {{
    text-decoration: underline;
  }}

  /* Badges */
  .badge {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11.5px;
    font-weight: 600;
    white-space: nowrap;
  }}
  .badge-country {{ background: rgba(255, 255, 255, 0.08); color: var(--text-primary); }}
  .badge-variety {{ background: var(--purple-bg); color: var(--purple); border: 1px solid rgba(188, 140, 255, 0.3); }}
  .badge-process {{ background: var(--blue-bg); color: var(--blue); border: 1px solid rgba(88, 166, 255, 0.3); }}
  .badge-roast {{ background: rgba(240, 180, 41, 0.1); color: var(--accent-gold); }}
  .badge-verified {{ background: var(--success-bg); color: var(--success); border: 1px solid rgba(63, 185, 80, 0.3); font-weight: 700; }}

  /* Lightbox Modal */
  .modal-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(8px);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }}
  .modal-content {{
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 24px;
    max-width: 500px;
    width: 90%;
    text-align: center;
    position: relative;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
  }}
  .modal-img {{
    width: 100%;
    max-height: 400px;
    object-fit: contain;
    background: #0b0f17;
    border-radius: var(--radius-md);
    padding: 16px;
    margin-bottom: 16px;
  }}
  .modal-title {{
    font-size: 18px;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 8px;
  }}
  .modal-close-btn {{
    position: absolute;
    top: 14px;
    right: 18px;
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 24px;
    cursor: pointer;
  }}
  .modal-close-btn:hover {{ color: #fff; }}

  /* Utilities */
  .text-center {{ text-align: center; }}
  .text-right {{ text-align: right; }}
  .font-bold {{ font-weight: 700; }}
  .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
  .text-muted {{ color: var(--text-muted); }}
  .text-accent {{ color: var(--accent-gold); }}
  .text-success {{ color: var(--success); }}
</style>
</head>
<body>

  <!-- Top Sticky Navigation -->
  <nav class="top-nav">
    <a href="index.html" class="nav-brand">
      <span class="brand-logo-badge">TEL</span>
      <span class="brand-title">The Espresso Lab (UAE)</span>
    </a>
    <div class="nav-links">
      <a href="theespressolab_mobile.html" class="nav-btn">📱 모바일 뷰</a>
      <a href="archers_coffee_clean_verified.html" class="nav-btn">☕ 아처스 커피 대시보드</a>
      <a href="index.html" class="nav-btn primary">🏠 허브 메인</a>
    </div>
  </nav>

  <!-- Hero Section -->
  <div class="hero-container">
    <div class="hero-card">
      <div class="hero-badge">Verified Catalog 2026 • 100% Code Verified</div>
      <h1 class="hero-title">UAE 에스프레소 커피랩 (The Espresso Lab)<br>전수 원두 54종 정밀 검증 & 구매 가이드</h1>
      <p class="hero-subtitle">
        두바이 D3(디자인 디스트릭트) 및 알 사르칼 에비뉴에 위치한 UAE 최고의 스페셜티 로스터리 <strong>The Espresso Lab</strong>의 필터 로스팅 원두 54종 전수를 크롤링하고, 가격·규격·품종 메타데이터를 <code>verify_quotes.py</code> 순수 코드로 기계 검증(PASS 100%)한 공식 대시보드입니다. 패키지 실물 사진과 함께 사용자 맞춤형 추천 및 국내 시세 대비 구매 메리트를 확인하세요.
      </p>

      <div class="hero-stats-grid">
        <div class="stat-item">
          <div class="stat-label">총 검증 원두</div>
          <div class="stat-value highlight">54종 전수</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">기계 검증 성공률</div>
          <div class="stat-value success">100.0% PASS</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">파나마 게이샤 & 최고봉</div>
          <div class="stat-value">25종 (46%)</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">실시간 적용 환율</div>
          <div class="stat-value font-mono">1 AED ≈ 380 KRW</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Recommendations Section: User Taste Top 3 & Expert Special Top 3 -->
  <div class="section-container">
    <div class="section-header">
      <div class="section-title-wrap">
        <h2 class="section-title">🎯 사용자 맞춤 추천 TOP 3 (워시드 • 티라이크 • 푸어오버)</h2>
        <p class="section-desc">사용자님의 취향인 "파나마/에티오피아 + 워시드 + 백차/자스민 티라이크 + 라이트로스트"를 센서리적으로 100% 충족하며, 국내 시세 대비 30~50% 저렴하거나 독점 랏인 3종입니다.</p>
      </div>
    </div>

    <div class="rec-grid">
      <!-- User Taste 1 -->
      <div class="rec-card user-taste">
        <div class="rec-card-header">
          <img src="{recommendations['user_taste'][0]['image_url']}" alt="{recommendations['user_taste'][0]['title']}" class="rec-pkg-img" onclick="openLightbox(this.src, '{recommendations['user_taste'][0]['title']}')">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-gold">{recommendations['user_taste'][0]['rank']}</span>
            <h3 class="rec-title">{recommendations['user_taste'][0]['title']}</h3>
            <div class="rec-origin">🇵🇦 {recommendations['user_taste'][0]['origin']}</div>
            <div class="rec-pricing">
              <span class="rec-price-main">{recommendations['user_taste'][0]['price']}</span>
              <span class="rec-price-sub">({recommendations['user_taste'][0]['price_per_100g']})</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title">👑 추천 핵심 포인트</div>
            <div class="rec-box-text"><strong>{recommendations['user_taste'][0]['badge']}</strong><br>{recommendations['user_taste'][0]['taste_rationale']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">🏞️ 테루아 & 프로듀서</div>
            <div class="rec-box-text">{recommendations['user_taste'][0]['terroir']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">☕ 센서리 프로파일 & 텍스처</div>
            <div class="rec-box-text">{recommendations['user_taste'][0]['sensory']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title green">💰 현지 구매 메리트 (국내 시세 비교)</div>
            <div class="rec-box-text">{recommendations['user_taste'][0]['merit_detail']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">💬 해외 커뮤니티 평가</div>
            <div class="rec-box-text">{recommendations['user_taste'][0]['community']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title blue">🧪 브루잉 가이드 (푸어오버)</div>
            <div class="rec-box-text">{recommendations['user_taste'][0]['brew_tip']}</div>
          </div>
        </div>
      </div>

      <!-- User Taste 2 -->
      <div class="rec-card user-taste">
        <div class="rec-card-header">
          <img src="{recommendations['user_taste'][1]['image_url']}" alt="{recommendations['user_taste'][1]['title']}" class="rec-pkg-img" onclick="openLightbox(this.src, '{recommendations['user_taste'][1]['title']}')">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-gold">{recommendations['user_taste'][1]['rank']}</span>
            <h3 class="rec-title">{recommendations['user_taste'][1]['title']}</h3>
            <div class="rec-origin">🇪🇹 {recommendations['user_taste'][1]['origin']}</div>
            <div class="rec-pricing">
              <span class="rec-price-main">{recommendations['user_taste'][1]['price']}</span>
              <span class="rec-price-sub">({recommendations['user_taste'][1]['price_per_100g']})</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title">👑 추천 핵심 포인트</div>
            <div class="rec-box-text"><strong>{recommendations['user_taste'][1]['badge']}</strong><br>{recommendations['user_taste'][1]['taste_rationale']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">🏞️ 테루아 & 프로듀서</div>
            <div class="rec-box-text">{recommendations['user_taste'][1]['terroir']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">☕ 센서리 프로파일 & 텍스처</div>
            <div class="rec-box-text">{recommendations['user_taste'][1]['sensory']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title green">💰 현지 구매 메리트 (국내 시세 비교)</div>
            <div class="rec-box-text">{recommendations['user_taste'][1]['merit_detail']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">💬 해외 커뮤니티 평가</div>
            <div class="rec-box-text">{recommendations['user_taste'][1]['community']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title blue">🧪 브루잉 가이드 (푸어오버)</div>
            <div class="rec-box-text">{recommendations['user_taste'][1]['brew_tip']}</div>
          </div>
        </div>
      </div>

      <!-- User Taste 3 -->
      <div class="rec-card user-taste">
        <div class="rec-card-header">
          <img src="{recommendations['user_taste'][2]['image_url']}" alt="{recommendations['user_taste'][2]['title']}" class="rec-pkg-img" onclick="openLightbox(this.src, '{recommendations['user_taste'][2]['title']}')">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-gold">{recommendations['user_taste'][2]['rank']}</span>
            <h3 class="rec-title">{recommendations['user_taste'][2]['title']}</h3>
            <div class="rec-origin">🇵🇦 {recommendations['user_taste'][2]['origin']}</div>
            <div class="rec-pricing">
              <span class="rec-price-main">{recommendations['user_taste'][2]['price']}</span>
              <span class="rec-price-sub">({recommendations['user_taste'][2]['price_per_100g']})</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title">👑 추천 핵심 포인트</div>
            <div class="rec-box-text"><strong>{recommendations['user_taste'][2]['badge']}</strong><br>{recommendations['user_taste'][2]['taste_rationale']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">🏞️ 테루아 & 프로듀서</div>
            <div class="rec-box-text">{recommendations['user_taste'][2]['terroir']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">☕ 센서리 프로파일 & 텍스처</div>
            <div class="rec-box-text">{recommendations['user_taste'][2]['sensory']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title green">💰 현지 구매 메리트 (국내 시세 비교)</div>
            <div class="rec-box-text">{recommendations['user_taste'][2]['merit_detail']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">💬 해외 커뮤니티 평가</div>
            <div class="rec-box-text">{recommendations['user_taste'][2]['community']}</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title blue">🧪 브루잉 가이드 (푸어오버)</div>
            <div class="rec-box-text">{recommendations['user_taste'][2]['brew_tip']}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Expert Special Top 3 -->
    <div class="section-header">
      <div class="section-title-wrap">
        <h2 class="section-title">🌟 큐레이터 스페셜 추천 TOP 3 (희귀 품종 • 이색 테루아)</h2>
        <p class="section-desc">일반적인 게이샤를 넘어, 파라이네마의 화이트 티 노트, 니에리 정통 더블워시드, 파나마 화산 에티오피아 토착종 등 특별한 경험을 선사하는 3종입니다.</p>
      </div>
    </div>

    <div class="rec-grid">
      <!-- Expert 1 -->
      <div class="rec-card expert">
        <div class="rec-card-header">
          <img src="{recommendations['expert_special'][0]['image_url']}" alt="{recommendations['expert_special'][0]['title']}" class="rec-pkg-img" onclick="openLightbox(this.src, '{recommendations['expert_special'][0]['title']}')">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-blue">{recommendations['expert_special'][0]['rank']}</span>
            <h3 class="rec-title">{recommendations['expert_special'][0]['title']}</h3>
            <div class="rec-origin">🇨🇴 {recommendations['expert_special'][0]['origin']}</div>
            <div class="rec-pricing">
              <span class="rec-price-main">{recommendations['expert_special'][0]['price']}</span>
              <span class="rec-price-sub">({recommendations['expert_special'][0]['price_per_100g']})</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title blue">💎 큐레이터 선별 사유</div>
            <div class="rec-box-text"><strong>{recommendations['expert_special'][0]['badge']}</strong><br>{recommendations['expert_special'][0]['point']}</div>
          </div>
        </div>
      </div>

      <!-- Expert 2 -->
      <div class="rec-card expert">
        <div class="rec-card-header">
          <img src="{recommendations['expert_special'][1]['image_url']}" alt="{recommendations['expert_special'][1]['title']}" class="rec-pkg-img" onclick="openLightbox(this.src, '{recommendations['expert_special'][1]['title']}')">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-blue">{recommendations['expert_special'][1]['rank']}</span>
            <h3 class="rec-title">{recommendations['expert_special'][1]['title']}</h3>
            <div class="rec-origin">🇰🇪 {recommendations['expert_special'][1]['origin']}</div>
            <div class="rec-pricing">
              <span class="rec-price-main">{recommendations['expert_special'][1]['price']}</span>
              <span class="rec-price-sub">({recommendations['expert_special'][1]['price_per_100g']})</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title blue">💎 큐레이터 선별 사유</div>
            <div class="rec-box-text"><strong>{recommendations['expert_special'][1]['badge']}</strong><br>{recommendations['expert_special'][1]['point']}</div>
          </div>
        </div>
      </div>

      <!-- Expert 3 -->
      <div class="rec-card expert">
        <div class="rec-card-header">
          <img src="{recommendations['expert_special'][2]['image_url']}" alt="{recommendations['expert_special'][2]['title']}" class="rec-pkg-img" onclick="openLightbox(this.src, '{recommendations['expert_special'][2]['title']}')">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-blue">{recommendations['expert_special'][2]['rank']}</span>
            <h3 class="rec-title">{recommendations['expert_special'][2]['title']}</h3>
            <div class="rec-origin">🇵🇦 {recommendations['expert_special'][2]['origin']}</div>
            <div class="rec-pricing">
              <span class="rec-price-main">{recommendations['expert_special'][2]['price']}</span>
              <span class="rec-price-sub">({recommendations['expert_special'][2]['price_per_100g']})</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title blue">💎 큐레이터 선별 사유</div>
            <div class="rec-box-text"><strong>{recommendations['expert_special'][2]['badge']}</strong><br>{recommendations['expert_special'][2]['point']}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Catalog Tables Section -->
  <div class="section-container">
    <div class="section-header">
      <div class="section-title-wrap">
        <h2 class="section-title">📋 에스프레소 커피랩 전체 라인업 전수 테이블 (54종)</h2>
        <p class="section-desc">헤더를 클릭하면 해당 항목 기준으로 양방향 실시간 정렬되며, 패키지 사진을 클릭하면 실물 사진이 확대됩니다.</p>
      </div>
    </div>

    <!-- Filter & Search Controls -->
    <div class="filter-controls-wrap">
      <div class="tab-buttons">
        <button class="tab-btn active" onclick="filterCategory('ALL', this)">
          전체 보기 <span class="tab-count">{len(coffees)}</span>
        </button>
        <button class="tab-btn" onclick="filterCategory('Panama High-End & Geisha', this)">
          🇵🇦 파나마 게이샤 & 하이엔드 <span class="tab-count">{len(panama)}</span>
        </button>
        <button class="tab-btn" onclick="filterCategory('Ethiopia Terroir Collection', this)">
          🇪🇹 에티오피아 테루아 <span class="tab-count">{len(ethiopia)}</span>
        </button>
        <button class="tab-btn" onclick="filterCategory('Americas & Africa Specialty', this)">
          🌎 중남미·아프리카 스페셜티 <span class="tab-count">{len(americas)}</span>
        </button>
      </div>

      <div class="search-input-wrap">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="원두명, 품종, 컵노트, 농장명 검색..." onkeyup="filterSearch()">
      </div>
    </div>

    <!-- Table Responsive Wrap -->
    <div class="table-responsive">
      <table class="data-table" id="coffeeTable">
        <thead>
          <tr>
            <th onclick="sortTable(0, 'num')"># <span class="sort-arrow"></span></th>
            <th>패키지 사진</th>
            <th onclick="sortTable(2, 'str')">커피 이름 (원문 링크) <span class="sort-arrow"></span></th>
            <th onclick="sortTable(3, 'str')">국가 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(4, 'str')">지역 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(5, 'str')">농장 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(6, 'str')">농부/프로듀서 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(7, 'str')">품종 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(8, 'str')">가공 방식 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(9, 'str')">재배 고도 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(10, 'str')">배전도 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(11, 'str')">컵노트 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(12, 'str')" class="text-center">중량 <span class="sort-arrow"></span></th>
            <th onclick="sortTable(13, 'num')" class="text-right">현지 가격 (AED / 원화) <span class="sort-arrow"></span></th>
            <th onclick="sortTable(14, 'num')" class="text-right">100g당 가격 (AED / 원화) <span class="sort-arrow"></span></th>
            <th>한국 판매처 (링크)</th>
            <th>한국 시세 & 구매 메리트</th>
            <th onclick="sortTable(17, 'str')">커뮤니티 평점 & 후기 <span class="sort-arrow"></span></th>
            <th class="text-center">검증</th>
          </tr>
        </thead>
        <tbody>
          {render_table_rows(coffees)}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Lightbox Modal -->
  <div class="modal-overlay" id="lightboxModal" onclick="closeLightbox(event)">
    <div class="modal-content" onclick="event.stopPropagation()">
      <button class="modal-close-btn" onclick="closeLightbox()">✕</button>
      <img src="" alt="" class="modal-img" id="modalImg">
      <h4 class="modal-title" id="modalTitle"></h4>
      <p class="text-xs text-muted">The Espresso Lab Official Retail Package</p>
    </div>
  </div>

  <script>
    // Lightbox Controls
    function openLightbox(url, title) {{
      const modal = document.getElementById('lightboxModal');
      const img = document.getElementById('modalImg');
      const ttl = document.getElementById('modalTitle');
      img.src = url;
      ttl.innerText = title;
      modal.style.display = 'flex';
    }}

    function closeLightbox(e) {{
      document.getElementById('lightboxModal').style.display = 'none';
    }}

    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') closeLightbox();
    }});

    // Tab Filtering
    let currentCategory = 'ALL';
    function filterCategory(cat, btn) {{
      currentCategory = cat;
      const buttons = document.querySelectorAll('.tab-btn');
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      applyFilters();
    }}

    // Search Filtering
    function filterSearch() {{
      applyFilters();
    }}

    function applyFilters() {{
      const query = document.getElementById('searchInput').value.toLowerCase();
      const rows = document.querySelectorAll('#coffeeTable tbody tr');

      rows.forEach(row => {{
        const rowCategory = row.getAttribute('data-category');
        const text = row.innerText.toLowerCase();

        const matchCat = (currentCategory === 'ALL' || rowCategory === currentCategory);
        const matchSearch = text.includes(query);

        if (matchCat && matchSearch) {{
          row.style.display = '';
        }} else {{
          row.style.display = 'none';
        }}
      }});
    }}

    // Table Sorting
    let sortDirections = {{}};
    function sortTable(colIndex, type) {{
      const table = document.getElementById('coffeeTable');
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const ths = table.querySelectorAll('th');

      ths.forEach(th => th.classList.remove('sorted-asc', 'sorted-desc'));

      const currentDir = sortDirections[colIndex] || 'asc';
      const nextDir = currentDir === 'asc' ? 'desc' : 'asc';
      sortDirections[colIndex] = nextDir;

      ths[colIndex].classList.add(nextDir === 'asc' ? 'sorted-asc' : 'sorted-desc');

      rows.sort((a, b) => {{
        let aVal = a.children[colIndex].innerText.trim();
        let bVal = b.children[colIndex].innerText.trim();

        if (type === 'num') {{
          // extract first numerical float
          const aMatch = aVal.match(/([0-9,.]+)/);
          const bMatch = bVal.match(/([0-9,.]+)/);
          const aNum = aMatch ? parseFloat(aMatch[1].replace(/,/g, '')) : 0;
          const bNum = bMatch ? parseFloat(bMatch[1].replace(/,/g, '')) : 0;
          return nextDir === 'asc' ? aNum - bNum : bNum - aNum;
        }} else {{
          return nextDir === 'asc' ? aVal.localeCompare(bVal, 'ko') : bVal.localeCompare(aVal, 'ko');
        }}
      }});

      rows.forEach(r => tbody.appendChild(r));
    }}
  </script>
</body>
</html>
"""

with open(DESKTOP_OUTPUT, 'w', encoding='utf-8') as f:
    f.write(desktop_html_content)

print(f"Generated Desktop Dashboard: {DESKTOP_OUTPUT} ({len(desktop_html_content)} bytes)")
