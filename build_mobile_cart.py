import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

active_10 = [c for c in top_20 if c.get('is_active')]

cart_html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>UAE 스페셜티 커피 현지 구매 발주서 (모바일 PO)</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
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
    --danger: #f85149;
    --safe-bottom: env(safe-area-inset-bottom, 16px);
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
  body {{
    background: var(--bg-main);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.5;
    padding-bottom: calc(var(--safe-bottom) + 30px);
    overflow-x: hidden;
  }}

  /* Top Nav */
  .m-header {{
    background: rgba(10, 14, 23, 0.95);
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
  .m-nav-back {{
    color: var(--blue);
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}
  .m-desktop-link {{
    font-size: 11.5px;
    padding: 5px 10px;
    border-radius: 6px;
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 600;
  }}

  /* Document Banner */
  .m-doc-banner {{
    padding: 20px 16px 16px 16px;
    background: linear-gradient(180deg, #131a26 0%, #0a0e17 100%);
    border-bottom: 1px solid var(--border-color);
  }}
  .m-doc-badge {{
    display: inline-block;
    background: var(--accent-glow);
    border: 1px solid var(--accent);
    color: var(--accent-gold);
    font-size: 10.5px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 999px;
    margin-bottom: 8px;
  }}
  .m-doc-title {{
    font-size: 21px;
    font-weight: 800;
    line-height: 1.35;
    margin-bottom: 6px;
    color: #fff;
  }}
  .m-doc-meta {{
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.4;
  }}

  /* Instructions Card (Clean mobile list) */
  .m-inst-card {{
    margin: 16px;
    background: rgba(19, 26, 38, 0.8);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent-gold);
    border-radius: 12px;
    padding: 14px 16px;
  }}
  .m-inst-head {{
    font-size: 13.5px;
    font-weight: 800;
    color: var(--accent-gold);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .m-inst-list {{
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .m-inst-item {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: rgba(10, 14, 23, 0.6);
    padding: 8px 10px;
    border-radius: 6px;
    border: 1px solid rgba(46, 62, 87, 0.5);
  }}
  .m-inst-num {{
    background: rgba(240, 180, 41, 0.2);
    color: var(--accent-gold);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 800;
    width: 22px;
    height: 22px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    flex-shrink: 0;
  }}
  .m-inst-txt {{
    font-size: 12px;
    color: #c9d1d9;
    line-height: 1.5;
    word-break: keep-all;
  }}
  .m-inst-txt strong {{ color: #fff; }}

  /* KPI Grid (2x2) */
  .m-kpi-grid {{
    margin: 0 16px 16px 16px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }}
  .m-kpi-box {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 12px;
  }}
  .m-kpi-lbl {{
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 600;
    margin-bottom: 4px;
  }}
  .m-kpi-val {{
    font-size: 18px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
  }}
  .val-gold {{ color: var(--accent-gold); }}
  .val-blue {{ color: var(--blue); }}
  .val-green {{ color: var(--success); }}

  /* Action Buttons Bar */
  .m-actions-wrap {{
    margin: 0 16px 16px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .m-act-btn {{
    width: 100%;
    padding: 11px 14px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.15s ease;
    border: 1px solid var(--border-color);
    background: var(--bg-card);
    color: var(--text-primary);
  }}
  .btn-print {{
    background: linear-gradient(135deg, #d29922, #b07d12);
    color: #000;
    border: none;
    font-weight: 800;
  }}
  .btn-secondary {{
    background: var(--bg-inner);
    color: var(--text-secondary);
  }}

  /* Coffee Cards Container */
  .m-po-list {{
    margin: 0 16px 24px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  /* PO Item Card */
  .m-po-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 14px;
    position: relative;
  }}
  .m-po-card-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
  }}
  .m-po-top-left {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .m-po-no {{
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    color: var(--text-secondary);
  }}
  .m-roastery-badge {{
    font-size: 10.5px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
  }}
  .badge-archers {{ background: rgba(56, 139, 253, 0.15); color: var(--blue); border: 1px solid rgba(56, 139, 253, 0.3); }}
  .badge-espressolab {{ background: rgba(240, 180, 41, 0.15); color: var(--accent-gold); border: 1px solid rgba(240, 180, 41, 0.3); }}

  .btn-del-item {{
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid rgba(248, 81, 73, 0.3);
    color: var(--danger);
    width: 26px;
    height: 26px;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
  }}

  /* Coffee Name & Link */
  .m-po-name {{
    font-size: 15.5px;
    font-weight: 800;
    color: #fff;
    line-height: 1.35;
    margin-bottom: 6px;
    word-break: keep-all;
  }}
  .m-po-name a {{
    color: inherit;
    text-decoration: none;
  }}
  .m-po-name a:hover {{ color: var(--blue); }}
  .m-out-link {{
    font-size: 12px;
    color: var(--blue);
  }}

  /* Price & Weight */
  .m-po-price-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
  }}
  .m-po-aed {{
    font-size: 16px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: var(--blue);
  }}
  .m-po-krw {{
    font-size: 12px;
    color: var(--text-secondary);
    margin-left: 6px;
  }}
  .m-po-weight {{
    font-size: 11px;
    color: var(--text-muted);
  }}

  /* Terroir & Notes */
  .m-po-sub {{
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 6px;
  }}
  .m-po-notes {{
    background: rgba(240, 180, 41, 0.08);
    border: 1px solid rgba(240, 180, 41, 0.2);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    color: #fce881;
    font-weight: 600;
    margin-bottom: 10px;
  }}

  /* Accordion Toggle */
  .m-po-toggle {{
    width: 100%;
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    color: var(--text-secondary);
    padding: 6px 10px;
    font-size: 11.5px;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
  }}
  .m-po-content {{
    display: none;
    padding-top: 10px;
    margin-top: 8px;
    border-top: 1px dashed var(--border-color);
    font-size: 12px;
    color: var(--text-secondary);
  }}
  .m-po-content.show {{ display: block; }}

  /* Empty State */
  .m-empty-state {{
    text-align: center;
    padding: 50px 20px;
    color: var(--text-muted);
    font-size: 14px;
    background: var(--bg-card);
    border: 1px dashed var(--border-color);
    border-radius: 12px;
  }}

  /* Toast Notification */
  .m-toast {{
    position: fixed;
    top: 65px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(240, 180, 41, 0.95);
    color: #000;
    font-weight: 700;
    font-size: 12.5px;
    padding: 8px 18px;
    border-radius: 999px;
    z-index: 300;
    display: none;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
  }}

  /* Print Styles */
  @media print {{
    body {{ background: #fff !important; color: #000 !important; padding-bottom: 0 !important; }}
    .m-header, .m-actions-wrap, .btn-del-item, .m-po-toggle {{ display: none !important; }}
    .m-po-content {{ display: block !important; color: #333 !important; }}
    .m-po-card {{ border: 1px solid #ccc !important; background: #fff !important; page-break-inside: avoid; }}
    .m-po-name a {{ color: #000 !important; text-decoration: underline !important; }}
    .m-po-aed {{ color: #000 !important; }}
    .m-inst-card {{ background: #f9f9f9 !important; border: 1px solid #ccc !important; }}
    .m-inst-txt, .m-inst-txt strong {{ color: #000 !important; }}
  }}
</style>
</head>
<body>

<!-- Header -->
<header class="m-header">
  <a href="mobile_index.html" class="m-nav-back">
    ← 모바일 큐레이션으로
  </a>
  <a href="cart.html" class="m-desktop-link">🖥️ 데스크톱 발주서</a>
</header>

<!-- Banner -->
<section class="m-doc-banner">
  <span class="m-doc-badge">구매 담당자 전달용 PO</span>
  <h1 class="m-doc-title">📋 UAE 스페셜티 커피 구매 발주서</h1>
  <div class="m-doc-meta" id="mDocMetaDate">
    발주 문서 번호: UAE-SPEC-PO-2026<br>
    대상: Archers Coffee &amp; The Espresso Lab
  </div>
</section>

<!-- Checklist -->
<div class="m-inst-card">
  <div class="m-inst-head">📌 현지 구매 담당자 필독 가이드</div>
  <div class="m-inst-list">
    <div class="m-inst-item">
      <span class="m-inst-num">01</span>
      <div class="m-inst-txt"><strong>100g 소포장 패키지:</strong> 전 품목 100g 규격인지 꼭 확인하세요.</div>
    </div>
    <div class="m-inst-item">
      <span class="m-inst-num">02</span>
      <div class="m-inst-txt"><strong>필터/브루잉용:</strong> 에스프레소용이 아닌 Filter / Light Roast 원두입니다.</div>
    </div>
    <div class="m-inst-item">
      <span class="m-inst-num">03</span>
      <div class="m-inst-txt"><strong>원두명 클릭:</strong> 커피 이름을 누르면 로스터리 공식 웹스토어로 바로 연결됩니다.</div>
    </div>
    <div class="m-inst-item">
      <span class="m-inst-num">04</span>
      <div class="m-inst-txt"><strong>로스팅 일자:</strong> 최근 2~3주 이내 로스팅된 원두를 우선 수령하세요.</div>
    </div>
    <div class="m-inst-item">
      <span class="m-inst-num">05</span>
      <div class="m-inst-txt"><strong>Tax 영수증:</strong> 공항 부가세(VAT) 환급을 위해 Tax Invoice 영수증을 챙기세요.</div>
    </div>
  </div>
</div>

<!-- KPI Grid -->
<div class="m-kpi-grid">
  <div class="m-kpi-box">
    <div class="m-kpi-lbl">총 발주 품목</div>
    <div class="m-kpi-val val-gold"><span id="kpiCount">0</span>종</div>
  </div>
  <div class="m-kpi-box">
    <div class="m-kpi-lbl">로스터리별 구성</div>
    <div class="m-kpi-val val-blue" style="font-size:15px; line-height:24px;">
      <span id="kpiArchers">0</span> 아처스 / <span id="kpiTel">0</span> 에소랩
    </div>
  </div>
  <div class="m-kpi-box">
    <div class="m-kpi-lbl">현지 결제액 (AED)</div>
    <div class="m-kpi-val val-gold"><span id="kpiAed">0.0</span> AED</div>
  </div>
  <div class="m-kpi-box">
    <div class="m-kpi-lbl">원화 환산 견적 (KRW)</div>
    <div class="m-kpi-val val-green">약 <span id="kpiKrw">0</span>원</div>
  </div>
</div>

<!-- Action Buttons -->
<div class="m-actions-wrap">
  <button type="button" class="m-act-btn btn-print" onclick="window.print()">🖨️ 발주서 인쇄 / PDF 저장</button>
  <button type="button" class="m-act-btn" onclick="copyOrderText()">📋 텍스트 발주서 복사 (카톡/메신저용)</button>
  <button type="button" class="m-act-btn" onclick="copyShareUrl()">🔗 모바일 발주서 공유 링크 복사</button>
  <div style="display:flex; gap:8px;">
    <a href="mobile_index.html" class="m-act-btn btn-secondary" style="flex:1; text-decoration:none;">➕ 원두 더 담기</a>
    <button type="button" class="m-act-btn btn-secondary" style="width:110px; color:var(--danger);" onclick="resetCart()">🗑️ 초기화</button>
  </div>
</div>

<!-- Toast -->
<div class="m-toast" id="mToast">알림 메시지</div>

<!-- Cart Item Cards -->
<main class="m-po-list" id="mPoList">
  <!-- Generated via JS -->
</main>

<script>
  const MASTER_COFFEES = {json.dumps(top_20, ensure_ascii=False)};
  const DEFAULT_PICKS = {json.dumps(active_10, ensure_ascii=False)};

  let cartItems = [];

  function initPo() {{
    const today = new Date();
    document.getElementById('mDocMetaDate').innerHTML = `발주 일자: ${{today.getFullYear()}}-${{String(today.getMonth()+1).padStart(2,'0')}}-${{String(today.getDate()).padStart(2,'0')}}<br>대상: Archers Coffee &amp; The Espresso Lab`;

    // 1. Check URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const itemHandlesParam = urlParams.get('items');

    if (itemHandlesParam) {{
      const handles = itemHandlesParam.split(',');
      cartItems = MASTER_COFFEES.filter(c => handles.includes(c.handle));
    }}

    // 2. If no URL params, check localStorage
    if (!cartItems.length) {{
      try {{
        const stored = localStorage.getItem('coffee_cart');
        if (stored) {{
          cartItems = JSON.parse(stored);
        }}
      }} catch (e) {{}}
    }}

    // 3. Fallback to active 10 picks
    if (!cartItems || !cartItems.length) {{
      cartItems = [...DEFAULT_PICKS];
    }}

    renderPoItems();
  }}

  function renderPoItems() {{
    const container = document.getElementById('mPoList');
    container.innerHTML = '';

    if (!cartItems.length) {{
      container.innerHTML = `
        <div class="m-empty-state">
          발주서에 담긴 커피가 없습니다.<br><br>
          <a href="mobile_index.html" style="color:var(--accent-gold); font-weight:700; text-decoration:none;">[원두 큐레이션 보러 가기 ↗]</a>
        </div>
      `;
      updateKpis(0, 0, 0, 0, 0);
      return;
    }}

    let totalAed = 0;
    let totalKrw = 0;
    let archers = 0;
    let tel = 0;

    cartItems.forEach((c, idx) => {{
      const a = parseFloat(c.price_aed || 0);
      const k = parseInt(c.price_krw || Math.round(a * 380));
      totalAed += a;
      totalKrw += k;

      if (c.roastery.includes('Archers')) archers++;
      else tel++;

      const rBadgeCls = c.roastery.includes('Archers') ? 'badge-archers' : 'badge-espressolab';
      const rev = c.detailed_review || {{}};
      const dt = c.similar_details || {{}};

      const card = document.createElement('article');
      card.className = 'm-po-card';
      card.innerHTML = `
        <div class="m-po-card-top">
          <div class="m-po-top-left">
            <span class="m-po-no">#${{idx + 1}}</span>
            <span class="m-roastery-badge ${{rBadgeCls}}">${{c.roastery_badge}}</span>
            <span style="font-size:11px; color:var(--text-muted); font-family:'JetBrains Mono',monospace;">종합 ${{c.score_total}}점</span>
          </div>
          <button type="button" class="btn-del-item" onclick="deleteItem(${{idx}})" title="품목 삭제">✕</button>
        </div>

        <h2 class="m-po-name">
          <a href="${{c.source_url}}" target="_blank" rel="noopener noreferrer">
            ${{c.title}} <span class="m-out-link">↗</span>
          </a>
        </h2>

        <div class="m-po-price-row">
          <div>
            <span class="m-po-aed">${{a.toFixed(1)}} AED</span>
            <span class="m-po-krw">(약 ${{k.toLocaleString()}}원)</span>
          </div>
          <span class="m-po-weight">${{c.weight || '100g'}} • ${{c.roast || 'Filter'}}</span>
        </div>

        <div class="m-po-sub">
          <strong>${{c.country}}</strong> • ${{c.farm || 'N/A'}} (${{c.variety}}, ${{c.process}})
        </div>

        <div class="m-po-notes">
          ✨ ${{c.notes || 'N/A'}}
        </div>

        <button type="button" class="m-po-toggle" onclick="toggleItemDetail('po_det_${{idx}}', this)">
          <span>스펙 &amp; 큐레이션 분석 상세 보기</span>
          <span>▼</span>
        </button>

        <div class="m-po-content" id="po_det_${{idx}}">
          <div style="margin-bottom:8px;">
            <strong>생산자:</strong> ${{c.producer || 'N/A'}} | <strong>재배고도:</strong> ${{c.altitude || 'N/A'}}
          </div>
          <div style="margin-bottom:8px;">
            <strong>배점 내역:</strong> 맛 ${{c.score_taste}}/50 • 가성비 ${{c.score_price}}/30 • 희소성 ${{c.score_rarity}}/20
          </div>
          <div style="background:rgba(10,14,23,0.7); padding:8px 10px; border-radius:6px; margin-bottom:8px; line-height:1.5;">
            <strong>💡 선발 사유:</strong> ${{rev.taste_analysis || c.overlap_note || '우수 원두'}}
          </div>
          <div style="font-size:11.5px; color:var(--text-muted);">
            ${{c.similar_target_rank ? `🔍 상위 #${{c.similar_target_rank}}위 원두와 유사도 ${{c.max_prior_sim}}%` : '★ 1위 기준 원두'}}
          </div>
        </div>
      `;
      container.appendChild(card);
    }});

    updateKpis(cartItems.length, archers, tel, totalAed, totalKrw);
    saveStorage();
  }}

  function updateKpis(cnt, arch, tel, aed, krw) {{
    document.getElementById('kpiCount').textContent = cnt;
    document.getElementById('kpiArchers').textContent = arch;
    document.getElementById('kpiTel').textContent = tel;
    document.getElementById('kpiAed').textContent = aed.toFixed(1);
    document.getElementById('kpiKrw').textContent = krw.toLocaleString();
  }}

  function toggleItemDetail(id, btn) {{
    const panel = document.getElementById(id);
    if (!panel) return;
    const isShow = panel.classList.contains('show');
    if (isShow) {{
      panel.classList.remove('show');
      btn.querySelector('span:last-child').textContent = '▼';
    }} else {{
      panel.classList.add('show');
      btn.querySelector('span:last-child').textContent = '▲';
    }}
  }}

  function deleteItem(idx) {{
    cartItems.splice(idx, 1);
    renderPoItems();
    showToast('품목이 발주서에서 삭제되었습니다.');
  }}

  function saveStorage() {{
    try {{
      localStorage.setItem('coffee_cart', JSON.stringify(cartItems));
    }} catch (e) {{}}
  }}

  function resetCart() {{
    if (confirm('발주서 목록을 초기화하시겠습니까?')) {{
      cartItems = [];
      saveStorage();
      renderPoItems();
      showToast('발주서가 초기화되었습니다.');
    }}
  }}

  function copyOrderText() {{
    if (!cartItems.length) {{
      alert('발주서에 담긴 커피가 없습니다.');
      return;
    }}
    let totalAed = 0;
    let lines = ['[📋 UAE 스페셜티 커피 현지 구매 발주서 (모바일)]', '규격: 전 품목 100g 필터용(Filter Light Roast) 필수', '----------------------------------------'];
    cartItems.forEach((c, idx) => {{
      const a = parseFloat(c.price_aed || 0);
      totalAed += a;
      lines.push(`${{idx + 1}}. [${{c.roastery}}] ${{c.title}}`);
      lines.push(`   - 가격: ${{a}} AED (약 ${{Math.round(a*380).toLocaleString()}}원)`);
      lines.push(`   - 컵노트: ${{c.notes}}`);
      lines.push(`   - 링크: ${{c.source_url}}`);
    }});
    lines.push('----------------------------------------');
    lines.push(`총 ${{cartItems.length}}종 / 결제 예정액: ${{totalAed.toFixed(1)}} AED (약 ${{Math.round(totalAed*380).toLocaleString()}}원)`);

    navigator.clipboard.writeText(lines.join('\\n')).then(() => {{
      showToast('발주서 텍스트가 클립보드에 복사되었습니다!');
    }}).catch(() => {{
      alert('클립보드 권한 오류');
    }});
  }}

  function copyShareUrl() {{
    if (!cartItems.length) {{
      alert('발주서에 담긴 커피가 없습니다.');
      return;
    }}
    const handles = cartItems.map(c => c.handle).join(',');
    const shareUrl = window.location.origin + window.location.pathname + '?items=' + encodeURIComponent(handles);
    navigator.clipboard.writeText(shareUrl).then(() => {{
      showToast('모바일 발주서 공유 링크가 복사되었습니다!');
    }}).catch(() => {{
      alert('공유 URL 복사 실패');
    }});
  }}

  function showToast(msg) {{
    const t = document.getElementById('mToast');
    t.textContent = msg;
    t.style.display = 'block';
    setTimeout(() => {{ t.style.display = 'none'; }}, 2200);
  }}

  window.addEventListener('DOMContentLoaded', initPo);
</script>

</body>
</html>
"""

with open('mobile_cart.html', 'w', encoding='utf-8') as f:
    f.write(cart_html_template)

print(f"Generated mobile_cart.html successfully ({len(cart_html_template)} bytes)")
