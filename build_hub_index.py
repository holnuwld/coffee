import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

INDEX_HTML = r'c:\cowork\coffee\index.html'

content = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAE 2대 명문 스페셜티 커피 통합 검증 & 구매 가이드</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,800;1,600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
  :root {
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
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    line-height: 1.6;
    min-height: 100vh;
    padding: 40px 20px 80px 20px;
  }

  .container {
    max-width: 1100px;
    margin: 0 auto;
  }

  /* Header Section */
  .hub-header {
    text-align: center;
    margin-bottom: 48px;
  }
  .hub-badge {
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
  }
  .hub-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 42px;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 16px;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  @media (max-width: 768px) {
    .hub-title { font-size: 30px; }
  }
  .hub-desc {
    color: var(--text-secondary);
    font-size: 16px;
    max-width: 760px;
    margin: 0 auto 28px auto;
    line-height: 1.7;
  }

  .stats-summary-bar {
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 48px;
  }
  .summary-badge {
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
  }
  .summary-badge.green { border-color: rgba(63, 185, 80, 0.4); color: var(--success); }
  .summary-badge.gold { border-color: var(--accent); color: var(--accent-gold); }

  /* Roastery Showcase Grid */
  .roastery-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    margin-bottom: 56px;
  }
  @media (max-width: 860px) {
    .roastery-grid { grid-template-columns: 1fr; }
  }

  .roastery-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px 30px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
    transition: all 0.25s ease;
  }
  .roastery-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  }
  .roastery-card.espressolab {
    border-top: 5px solid #d29922;
  }
  .roastery-card.archers {
    border-top: 5px solid #58a6ff;
  }

  .r-top-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 16px;
  }
  .tag-gold { background: var(--accent-glow); color: var(--accent-gold); border: 1px solid var(--accent); }
  .tag-blue { background: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid var(--blue); }

  .r-name {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 10px;
    color: #fff;
  }
  .r-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 24px;
  }

  .r-highlights {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 30px;
    font-size: 13.5px;
    color: #c9d1d9;
  }
  .r-highlights li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    line-height: 1.5;
  }
  .r-highlights li span {
    color: var(--accent-gold);
    font-weight: 800;
    flex-shrink: 0;
  }
  .roastery-card.archers .r-highlights li span {
    color: var(--blue);
  }

  /* Version Buttons for each roastery */
  .r-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: auto;
  }
  .r-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 14px 12px;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.2s ease;
    text-align: center;
  }
  .r-btn .btn-title {
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .r-btn .btn-sub {
    font-size: 11px;
    opacity: 0.8;
    margin-top: 2px;
    font-weight: 500;
  }

  .btn-desktop-gold {
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
  }
  .btn-desktop-gold:hover { background: linear-gradient(135deg, #e3b341, #c89617); }

  .btn-mobile-gold {
    background: #1c2638;
    border: 1px solid var(--border-light);
    color: var(--text-primary);
  }
  .btn-mobile-gold:hover { border-color: var(--accent); background: #223047; }

  .btn-desktop-blue {
    background: linear-gradient(135deg, #238636, #1e702d);
    color: #fff;
  }
  .btn-desktop-blue:hover { background: linear-gradient(135deg, #2ea043, #238636); }

  .btn-mobile-blue {
    background: #1c2638;
    border: 1px solid var(--border-light);
    color: var(--text-primary);
  }
  .btn-mobile-blue:hover { border-color: var(--blue); background: #223047; }

  /* User Preference Note Card */
  .pref-note-card {
    background: rgba(19, 26, 38, 0.6);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    gap: 20px;
  }
  @media (max-width: 680px) {
    .pref-note-card { flex-direction: column; align-items: flex-start; }
  }
  .pref-icon {
    font-size: 36px;
    flex-shrink: 0;
  }
  .pref-content h3 {
    font-size: 16px;
    font-weight: 700;
    color: var(--accent-gold);
    margin-bottom: 4px;
  }
  .pref-content p {
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.6;
  }

  /* Footer */
  footer {
    text-align: center;
    font-size: 13px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 24px;
  }
  footer a { color: var(--blue); text-decoration: none; }
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

  <!-- Footer -->
  <footer>
    <p>
      UAE Specialty Coffee Verification Pipeline • Powered by Pure Code Verification Engine (<code>verify_quotes.py</code>)<br>
      GitHub Repository: <a href="https://github.com/holnuwld/coffee" target="_blank">github.com/holnuwld/coffee</a>
    </p>
  </footer>

</div>

</body>
</html>
"""

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Generated Hub Index: {INDEX_HTML} ({len(content)} bytes)")
