import json
import html
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

INDEX_HTML = r'c:\cowork\coffee\index.html'

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

print(f"Loaded {len(top_20)} ranked coffees for index.html integration.")

def render_top20_rows():
    rows = []
    active_count = 0
    for c in top_20:
        is_act = c['is_active']
        row_cls = "active-pick-row" if is_act else "overlap-pick-row"
        
        if is_act:
            active_count += 1
            rank_badge = f'<span class="rank-badge active-rank">Pick #{active_count} <span class="rank-num">({c["rank"]}위)</span></span>'
            status_badge = '<span class="status-badge active-badge">★ 최종 추천 10선</span>'
        else:
            rank_badge = f'<span class="rank-badge dimmed-rank">{c["rank"]}위</span>'
            status_badge = f'<span class="status-badge dimmed-badge">🚫 중복 제외</span>'

        roastery_cls = "archers-badge" if "Archers" in c['roastery'] else "espressolab-badge"

        r = f"""
        <tr class="{row_cls}" data-status="{'active' if is_act else 'overlap'}">
          <td class="text-center font-mono">
            {rank_badge}
          </td>
          <td>
            <span class="roastery-tag {roastery_cls}">{c['roastery_badge']}</span>
          </td>
          <td class="coffee-name-cell">
            <a href="{c['source_url']}" target="_blank" class="c-title-link" title="공식 사이트 상품 페이지 열기">
              {html.escape(c['title'])} ↗
            </a>
            <div class="c-spec-sub">
              {html.escape(c['country'])} • {html.escape(c['farm'])} • {html.escape(c['variety'])} ({html.escape(c['process'])})
            </div>
          </td>
          <td class="text-right font-mono price-col">
            <div class="aed-price">{c['price_aed']} AED</div>
            <div class="krw-price">약 {c['price_krw']:,}원</div>
          </td>
          <td class="text-center font-mono score-col">
            <div class="score-breakdown">
              <span title="맛 점수 (40점 만점)">맛 {c['score_taste']}</span> / 
              <span title="가성비 점수 (30점 만점)">가격 {c['score_value']}</span> / 
              <span title="한국 희소성 (30점 만점)">희소 {c['score_rarity']}</span>
            </div>
            <div class="total-score-box">
              <span class="total-score">{c['score_total']}</span><span class="total-max">/100</span>
            </div>
          </td>
          <td class="analysis-cell">
            <div class="review-desc">{html.escape(c['review_comment'])}</div>
            <div class="overlap-reason {'act-reason' if is_act else 'dim-reason'} mt-1">
              <strong>판정:</strong> {html.escape(c['overlap_note'])}
            </div>
          </td>
        </tr>
        """
        rows.append(r)
    return "\n".join(rows)

content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAE 2대 명문 스페셜티 커피 통합 검증 & 구매 가이드</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,800;1,600&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #090d13;
    --card-bg: #131a26;
    --card-hover: #182333;
    --border: #222f42;
    --border-light: #2e3e57;
    --accent: #d29922;
    --accent-gold: #f0b429;
    --accent-glow: rgba(210, 153, 34, 0.15);
    --text-primary: #f0f6fc;
    --text-secondary: #9da7b3;
    --text-muted: #6e7681;
    --success: #3fb950;
    --blue: #58a6ff;
    --purple: #bc8cff;
    --danger: #f85149;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    line-height: 1.6;
    min-height: 100vh;
    padding: 40px 20px 80px 20px;
  }}

  .container {{
    max-width: 1200px;
    margin: 0 auto;
  }}

  /* Header Section */
  .hub-header {{
    text-align: center;
    margin-bottom: 40px;
  }}
  .hub-badge {{
    display: inline-block;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-gold);
    font-weight: 800;
    background: var(--accent-glow);
    border: 1px solid var(--accent);
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 18px;
  }}
  .hub-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 42px;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 16px;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  @media (max-width: 768px) {{
    .hub-title {{ font-size: 30px; }}
  }}
  .hub-desc {{
    color: var(--text-secondary);
    font-size: 16px;
    max-width: 800px;
    margin: 0 auto 24px auto;
    line-height: 1.7;
  }}

  .stats-summary-bar {{
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 40px;
  }}
  .summary-badge {{
    background: #111722;
    border: 1px solid var(--border);
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .summary-badge.green {{ border-color: rgba(63, 185, 80, 0.4); color: var(--success); }}
  .summary-badge.gold {{ border-color: var(--accent); color: var(--accent-gold); }}

  /* User Preference Note Card */
  .pref-note-card {{
    background: rgba(19, 26, 38, 0.7);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    gap: 20px;
  }}
  @media (max-width: 680px) {{
    .pref-note-card {{ flex-direction: column; align-items: flex-start; }}
  }}
  .pref-icon {{
    font-size: 36px;
    flex-shrink: 0;
  }}
  .pref-content h3 {{
    font-size: 16px;
    font-weight: 700;
    color: var(--accent-gold);
    margin-bottom: 4px;
  }}
  .pref-content p {{
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.6;
  }}

  /* Roastery Showcase Grid */
  .roastery-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
    margin-bottom: 56px;
  }}
  @media (max-width: 860px) {{
    .roastery-grid {{ grid-template-columns: 1fr; }}
  }}

  .roastery-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 32px 28px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
    transition: all 0.25s ease;
  }}
  .roastery-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  }}
  .roastery-card.espressolab {{
    border-top: 5px solid #d29922;
  }}
  .roastery-card.archers {{
    border-top: 5px solid #58a6ff;
  }}

  .r-top-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 14px;
  }}
  .tag-gold {{ background: var(--accent-glow); color: var(--accent-gold); border: 1px solid var(--accent); }}
  .tag-blue {{ background: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid var(--blue); }}

  .r-name {{
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
    color: #fff;
  }}
  .r-subtitle {{
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 20px;
  }}

  .r-highlights {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 24px;
    font-size: 13px;
    color: #c9d1d9;
  }}
  .r-highlights li {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    line-height: 1.5;
  }}
  .r-highlights li span {{
    color: var(--accent-gold);
    font-weight: 800;
    flex-shrink: 0;
  }}
  .roastery-card.archers .r-highlights li span {{
    color: var(--blue);
  }}

  .r-actions {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: auto;
  }}
  .r-btn {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px 10px;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.2s ease;
    text-align: center;
  }}
  .r-btn .btn-title {{
    font-size: 13.5px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .r-btn .btn-sub {{
    font-size: 10.5px;
    opacity: 0.8;
    margin-top: 2px;
    font-weight: 500;
  }}

  .btn-desktop-gold {{
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
  }}
  .btn-desktop-gold:hover {{ background: linear-gradient(135deg, #e3b341, #c89617); }}

  .btn-mobile-gold {{
    background: #1c2638;
    border: 1px solid var(--border-light);
    color: var(--text-primary);
  }}
  .btn-mobile-gold:hover {{ border-color: var(--accent); background: #223047; }}

  .btn-desktop-blue {{
    background: linear-gradient(135deg, #238636, #1e702d);
    color: #fff;
  }}
  .btn-desktop-blue:hover {{ background: linear-gradient(135deg, #2ea043, #238636); }}

  .btn-mobile-blue {{
    background: #1c2638;
    border: 1px solid var(--border-light);
    color: var(--text-primary);
  }}
  .btn-mobile-blue:hover {{ border-color: var(--blue); background: #223047; }}

  /* ========================================================
     TOP 20 RANKED 100g CURATION SECTION (NEW)
     ======================================================== */
  .top20-section {{
    margin-top: 60px;
    border-top: 2px solid var(--border);
    padding-top: 48px;
  }}
  .top20-header {{
    text-align: center;
    margin-bottom: 32px;
  }}
  .top20-badge {{
    display: inline-block;
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
    font-size: 12px;
    font-weight: 800;
    padding: 5px 14px;
    border-radius: 999px;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .top20-title {{
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.8px;
    margin-bottom: 12px;
  }}
  .top20-desc {{
    font-size: 15px;
    color: var(--text-secondary);
    max-width: 860px;
    margin: 0 auto 24px auto;
    line-height: 1.65;
  }}

  /* Score Criteria Legend Box */
  .criteria-box {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 24px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }}
  @media (max-width: 768px) {{
    .criteria-box {{ grid-template-columns: 1fr; gap: 12px; }}
  }}
  .criterion-item {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .crit-name {{
    font-size: 13px;
    font-weight: 700;
    color: var(--accent-gold);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .crit-desc {{
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.5;
  }}

  /* Filter Controls */
  .top20-filters {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 18px;
  }}
  .filter-btns {{
    display: flex;
    gap: 8px;
  }}
  .f-btn {{
    background: #111722;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }}
  .f-btn:hover {{
    color: var(--text-primary);
    border-color: var(--border-light);
  }}
  .f-btn.active {{
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
  }}
  .legend-note {{
    font-size: 12.5px;
    color: var(--text-muted);
  }}

  /* Table Design */
  .table-box {{
    overflow-x: auto;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
  }}
  .top20-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13px;
    white-space: normal;
  }}
  .top20-table th {{
    background: #0f1622;
    color: var(--text-secondary);
    font-weight: 700;
    text-align: left;
    padding: 14px 16px;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }}
  .top20-table td {{
    padding: 16px 16px;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }}

  /* Active vs Overlap Styling */
  .active-pick-row {{
    background: rgba(19, 26, 38, 0.7);
    transition: background 0.15s ease;
  }}
  .active-pick-row:hover {{
    background: rgba(24, 35, 51, 0.95);
  }}
  .overlap-pick-row {{
    background: rgba(10, 14, 20, 0.6);
    opacity: 0.55;
    transition: all 0.2s ease;
  }}
  .overlap-pick-row:hover {{
    opacity: 0.95;
    background: rgba(16, 22, 32, 0.9);
  }}

  /* Cell Details */
  .rank-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 800;
    font-size: 12px;
    white-space: nowrap;
  }}
  .active-rank {{
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
  }}
  .active-rank .rank-num {{
    font-size: 10.5px;
    opacity: 0.85;
    font-weight: 600;
  }}
  .dimmed-rank {{
    background: #1c2430;
    color: var(--text-muted);
    border: 1px solid var(--border);
  }}

  .roastery-tag {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
  }}
  .archers-badge {{ background: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid rgba(88, 166, 255, 0.3); }}
  .espressolab-badge {{ background: var(--accent-glow); color: var(--accent-gold); border: 1px solid var(--accent); }}

  .coffee-name-cell {{
    min-width: 240px;
  }}
  .c-title-link {{
    font-size: 14.5px;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    transition: color 0.15s ease;
  }}
  .c-title-link:hover {{
    color: var(--accent-gold);
    text-decoration: underline;
  }}
  .c-spec-sub {{
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 3px;
    line-height: 1.4;
  }}

  .price-col {{
    min-width: 105px;
  }}
  .aed-price {{
    font-size: 15px;
    font-weight: 800;
    color: var(--accent-gold);
  }}
  .krw-price {{
    font-size: 11.5px;
    color: var(--text-muted);
  }}

  .score-col {{
    min-width: 130px;
  }}
  .score-breakdown {{
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 2px;
  }}
  .total-score-box {{
    display: inline-block;
    background: #0d131c;
    border: 1px solid var(--border);
    padding: 2px 8px;
    border-radius: 6px;
  }}
  .total-score {{
    font-size: 16px;
    font-weight: 800;
    color: var(--success);
  }}
  .total-max {{
    font-size: 10px;
    color: var(--text-muted);
  }}

  .analysis-cell {{
    min-width: 280px;
  }}
  .review-desc {{
    font-size: 12.5px;
    color: var(--text-secondary);
    line-height: 1.5;
  }}
  .overlap-reason {{
    font-size: 11px;
    padding: 3px 6px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 4px;
  }}
  .act-reason {{
    background: rgba(63, 185, 80, 0.1);
    color: var(--success);
    border: 1px solid rgba(63, 185, 80, 0.25);
  }}
  .dim-reason {{
    background: rgba(248, 81, 73, 0.1);
    color: #ff7b72;
    border: 1px solid rgba(248, 81, 73, 0.25);
  }}

  /* Footer */
  footer {{
    text-align: center;
    font-size: 13px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 24px;
    margin-top: 60px;
  }}
  footer a {{ color: var(--blue); text-decoration: none; }}
</style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <header class="hub-header">
    <div class="hub-badge">UAE Specialty Coffee Intelligence Portal</div>
    <h1 class="hub-title">UAE 2대 명문 스페셜티 로스터리<br>전수 검증 & 현지 구매 허브</h1>
    <p class="hub-desc">
      두바이 현지 방문 구매를 위해 아랍에미리트 최고의 로스터리 <strong>The Espresso Lab</strong>과 <strong>Archers Coffee</strong>의 전수 원두(총 171종)를 수집하고, <code>verify_quotes.py</code> 순수 코드로 기계 검증(100% PASS)을 완료한 공식 인덱스 포털입니다.
    </p>

    <!-- Stats Summary -->
    <div class="stats-summary-bar">
      <div class="summary-badge green">
        <span>✓</span> 총 171종 원두 100% 기계 검증 완료
      </div>
      <div class="summary-badge gold">
        <span>📷</span> 에스프레소 커피랩 실물 패키지 사진 전수 탑재
      </div>
      <div class="summary-badge">
        <span>🇦🇪</span> UAE 현지 매장 무관세 구매 가이드
      </div>
    </div>
  </header>

  <!-- User Taste Matching Notice -->
  <div class="pref-note-card">
    <div class="pref-icon">☕</div>
    <div class="pref-content">
      <h3>선호 취향 맞춤형 필터링 안내</h3>
      <p>
        사용자님의 선호 취향인 <strong>"파나마/에티오피아 원산지 + 워시드 가공 + 백차/자스민 티라이크(Tea-like) 텍스처 + 라이트로스트 푸어오버"</strong>에 맞추어 각 로스터리별 1순위 추천 및 전문가 추천 원두를 상단에 독립 배치했습니다.
      </p>
    </div>
  </div>

  <!-- 2 Major Roasteries Grid -->
  <div class="roastery-grid">

    <!-- ROASTERY 1: The Espresso Lab -->
    <div class="roastery-card espressolab">
      <div>
        <div class="r-top-tag tag-gold">Featured Roastery • 전수 54종</div>
        <h2 class="r-name">The Espresso Lab (UAE)</h2>
        <p class="r-subtitle">
          두바이 D3(디자인 디스트릭트) 및 알 사르칼 에비뉴에 플래그십을 둔 하이엔드 로스터리. 2022 Best of Panama 1위 Auromar Firestone 및 2021 에티오피아 COE 1위 Bombe Washed 보유.
        </p>
        <ul class="r-highlights">
          <li><span>📷</span> <strong>패키지 실물 사진 전수 탑재:</strong> 매장 진열대 실물과 즉시 비교 가능</li>
          <li><span>🥇</span> <strong>BOP 챔피언 Auromar Firestone:</strong> 국내 시세 대비 35% 할인</li>
          <li><span>💰</span> <strong>에티오피아 Bombe Washed:</strong> 200g 80 AED (100g당 1.5만원) 반값 종결</li>
          <li><span>🔍</span> <strong>파나마 게이샤 & 하이엔드 25종:</strong> 전수 100% 기계 검증 PASS</li>
        </ul>
      </div>

      <div class="r-actions">
        <a href="theespressolab_verified.html" class="r-btn btn-desktop-gold">
          <span class="btn-title">🖥️ 데스크톱 대시보드</span>
          <span class="btn-sub">18개 컬럼 양방향 정렬 표</span>
        </a>
        <a href="theespressolab_mobile.html" class="r-btn btn-mobile-gold">
          <span class="btn-title">📱 모바일 퀵 가이드</span>
          <span class="btn-sub">패키지 카드 & 원터치 필터</span>
        </a>
      </div>
    </div>

    <!-- ROASTERY 2: Archers Coffee -->
    <div class="roastery-card archers">
      <div>
        <div class="r-top-tag tag-blue">Global Specialty Champion • 전수 117종</div>
        <h2 class="r-name">Archers Coffee (UAE)</h2>
        <p class="r-subtitle">
          샤르자 및 두바이를 거점으로 전 세계 유명 바리스타들과 직거래하는 UAE 최대 스페셜티 로스터리. 컴피티션, 마이크로랏 리저브, 셀렉션 3대 컬렉션 완비.
        </p>
        <ul class="r-highlights">
          <li><span>🥇</span> <strong>Auromar Geisha Washed Peaberry:</strong> 아처스 독점 피베리 나노랏</li>
          <li><span>🥈</span> <strong>Hamasho Village Washed:</strong> 다예 벤사 독점 랏 (100g 1.2만원대)</li>
          <li><span>🏆</span> <strong>Elida Estate Geisha Washed Plano:</strong> 라마스투스 옥션 명문</li>
          <li><span>📋</span> <strong>3대 컬렉션 117종 전수 완비:</strong> 국내 시세 및 커뮤니티 리뷰 대조</li>
        </ul>
      </div>

      <div class="r-actions">
        <a href="archers_coffee_clean_verified.html" class="r-btn btn-desktop-blue">
          <span class="btn-title">🖥️ 데스크톱 대시보드</span>
          <span class="btn-sub">전 컬렉션 정밀 비교 분석</span>
        </a>
        <a href="mobile.html" class="r-btn btn-mobile-blue">
          <span class="btn-title">📱 모바일 퀵 가이드</span>
          <span class="btn-sub">현지 쇼핑 최적화 모바일 뷰</span>
        </a>
      </div>
    </div>

  </div>

  <!-- ========================================================
       TOP 20 RANKED 100g CURATION SECTION
       ======================================================== -->
  <section class="top20-section" id="top20Section">
    <div class="top20-header">
      <div class="top20-badge">Integrated 100g Master Curation</div>
      <h2 class="top20-title">🏆 2대 로스터리 통합 100g 원두 랭킹 TOP 20<br>& 최종 엄선 10선 (Active Picks)</h2>
      <p class="top20-desc">
        두 로스터리의 100g 패키지 원두 131종 전체를 3대 기준(맛 40점 + 가격 합리성 30점 + 한국 희소성 30점 = 총 100점 만점)으로 정밀 평가했습니다.<br>
        상위 20개 중 <strong>순위권 내 다른 원두와 농장 또는 컵노트가 중복되는 하위 10종은 음영(톤다운) 처리</strong>하여, 현지에서 겹치지 않고 다채롭게 구매할 수 있는 <strong>최종 10개(Active Pick)</strong>를 완성했습니다.
      </p>
    </div>

    <!-- Criteria Breakdown Box -->
    <div class="criteria-box">
      <div class="criterion-item">
        <div class="crit-name">☕ 1. 맛이 좋은가 (40점 만점)</div>
        <div class="crit-desc">워시드 가공, 자스민·백차·복숭아 티라이크 텍스처, 파나마/에티오피아 테루아, 푸어오버 라이트로스트 클린컵 및 BOP/COE 챔피언급 위상 평가.</div>
      </div>
      <div class="criterion-item">
        <div class="crit-name">💰 2. 가격이 합리적인가 (30점 만점)</div>
        <div class="crit-desc">100g당 절대 가격(AED/원화) 및 국내 유통 시세(7~10만원) 대비 할인율(30~50% 반값 혜택)을 정량 산정하여 가성비 반영.</div>
      </div>
      <div class="criterion-item">
        <div class="crit-name">🇰🇷 3. 한국에서 구하기 어려운가 (30점 만점)</div>
        <div class="crit-desc">국내 공식 수입 전무 여부, 현지 로스터리 단독 직거래 랏, 나노랏 및 국내 대체 불가성을 평가하여 현지 방문 구매 가치 극대화.</div>
      </div>
    </div>

    <!-- Filter Buttons & Legend -->
    <div class="top20-filters">
      <div class="filter-btns">
        <button class="f-btn active" onclick="filterRanked('all', this)">전체 20개 보기 (중복 음영 포함)</button>
        <button class="f-btn" onclick="filterRanked('active', this)">🎯 최종 추천 10선만 모아보기</button>
        <button class="f-btn" onclick="filterRanked('overlap', this)">🚫 중복 제외 10종 보기</button>
      </div>
      <div class="legend-note">
        💡 <strong>팁:</strong> 음영 처리된 행은 상위 추천 원두와 농장/맛 프로필이 겹쳐 제외된 품목입니다.
      </div>
    </div>

    <!-- Table Responsive Box -->
    <div class="table-box">
      <table class="top20-table" id="top20Table">
        <thead>
          <tr>
            <th class="text-center">선정 / 순위</th>
            <th>로스터리</th>
            <th>커피 이름 (클릭 시 공식 링크) & 스펙</th>
            <th class="text-right">100g 가격</th>
            <th class="text-center">종합 점수 (100점)</th>
            <th>검토 내용 & 선발 / 중복 사유</th>
          </tr>
        </thead>
        <tbody>
          {render_top20_rows()}
        </tbody>
      </table>
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <p>
      UAE Specialty Coffee Verification Pipeline • Powered by Pure Code Verification Engine (<code>verify_quotes.py</code>)<br>
      GitHub Repository: <a href="https://github.com/holnuwld/coffee" target="_blank">github.com/holnuwld/coffee</a>
    </p>
  </footer>

</div>

<script>
  function filterRanked(type, btn) {{
    document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const rows = document.querySelectorAll('#top20Table tbody tr');
    rows.forEach(row => {{
      const st = row.getAttribute('data-status');
      if (type === 'all') {{
        row.style.display = '';
      }} else if (type === 'active') {{
        row.style.display = (st === 'active') ? '' : 'none';
      }} else if (type === 'overlap') {{
        row.style.display = (st === 'overlap') ? '' : 'none';
      }}
    }});
  }}
</script>

</body>
</html>
"""

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Generated Updated index.html: {INDEX_HTML} ({len(content)} bytes)")
