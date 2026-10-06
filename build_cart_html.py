import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

# The active 10 picks by default
active_10 = [c for c in top_20 if c.get('is_active')]

cart_page_code = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAE 스페셜티 커피 현지 구매 발주서 (Purchase Order & Spec Sheet)</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #090d13;
    --card-bg: #131a26;
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
    --danger: #f85149;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    min-height: 100vh;
    padding: 30px 20px 80px 20px;
  }}

  .container {{
    max-width: 1280px;
    margin: 0 auto;
  }}

  /* Top Navigation Bar */
  .top-nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }}
  .nav-back-link {{
    color: var(--blue);
    text-decoration: none;
    font-size: 13.5px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: color 0.15s ease;
  }}
  .nav-back-link:hover {{
    color: #fff;
    text-decoration: underline;
  }}
  .nav-badges {{
    display: flex;
    gap: 8px;
  }}
  .badge-tag {{
    font-size: 11.5px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
  }}
  .badge-po {{
    background: var(--accent-glow);
    color: var(--accent-gold);
    border: 1px solid var(--accent);
  }}

  /* Document Header */
  .doc-header {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
  }}
  .doc-title-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 12px;
  }}
  .doc-title {{
    font-size: 28px;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.5px;
  }}
  .doc-meta-right {{
    text-align: right;
    font-size: 12.5px;
    color: var(--text-muted);
  }}
  .doc-meta-right strong {{
    color: var(--text-secondary);
  }}
  .doc-desc {{
    font-size: 14.5px;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 950px;
  }}

  /* Purchasing Instructions Callout */
  .instructions-card {{
    background: rgba(19, 26, 38, 0.7);
    border-left: 4px solid var(--accent-gold);
    border-top: 1px solid var(--border);
    border-right: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 24px;
  }}
  .inst-title {{
    font-size: 14.5px;
    font-weight: 700;
    color: var(--accent-gold);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .inst-list {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 8px 20px;
    font-size: 13px;
    color: #c9d1d9;
  }}
  .inst-list li {{
    display: flex;
    align-items: flex-start;
    gap: 6px;
  }}
  .inst-list li span {{
    color: var(--accent-gold);
    font-weight: 700;
  }}

  /* Summary KPI Cards Grid */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }}
  @media (max-width: 860px) {{
    .kpi-grid {{ grid-template-columns: 1fr 1fr; }}
  }}
  @media (max-width: 480px) {{
    .kpi-grid {{ grid-template-columns: 1fr; }}
  }}
  .kpi-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .kpi-label {{
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 600;
    margin-bottom: 6px;
  }}
  .kpi-value {{
    font-size: 24px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
  }}
  .kpi-sub {{
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 4px;
  }}
  .val-gold {{ color: var(--accent-gold); }}
  .val-green {{ color: var(--success); }}
  .val-blue {{ color: var(--blue); }}

  /* Toolbar Actions */
  .action-toolbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
  }}
  .action-group-left {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .action-group-right {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .po-btn {{
    background: #111722;
    border: 1px solid var(--border);
    color: var(--text-primary);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }}
  .po-btn:hover {{
    border-color: var(--border-light);
    background: #1a2333;
  }}
  .btn-print {{
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
    border-color: var(--accent);
  }}
  .btn-print:hover {{
    background: linear-gradient(135deg, #e3b341, #c89617);
    color: #000;
  }}
  .btn-danger {{
    color: var(--danger);
  }}
  .btn-danger:hover {{
    background: rgba(248, 81, 73, 0.15);
    border-color: var(--danger);
  }}

  /* Cart Table */
  .table-box {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow-x: auto;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
    margin-bottom: 24px;
  }}
  .po-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13px;
  }}
  .po-table th {{
    background: #0f1622;
    color: var(--text-secondary);
    font-weight: 700;
    text-align: left;
    padding: 14px 16px;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }}
  .po-table td {{
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }}
  .po-table tr:hover td {{
    background: rgba(24, 35, 51, 0.6);
  }}

  .roastery-badge {{
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
  }}
  .badge-archers {{ background: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid rgba(88, 166, 255, 0.3); }}
  .badge-espressolab {{ background: var(--accent-glow); color: var(--accent-gold); border: 1px solid var(--accent); }}

  .coffee-link {{
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    line-height: 1.4;
    display: inline-block;
    transition: color 0.15s ease;
  }}
  .coffee-link:hover {{
    color: var(--accent-gold);
    text-decoration: underline;
  }}
  .coffee-link .out-icon {{
    font-size: 11px;
    opacity: 0.8;
    margin-left: 3px;
  }}

  .spec-sub {{
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 3px;
  }}

  .price-cell {{
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
  }}
  .price-aed {{
    font-size: 15px;
    font-weight: 800;
    color: var(--accent-gold);
  }}
  .price-krw {{
    font-size: 11.5px;
    color: var(--text-muted);
  }}

  .notes-tag {{
    font-size: 12px;
    color: #e6edf3;
    line-height: 1.45;
  }}

  .reason-text {{
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.45;
    max-width: 320px;
  }}

  .btn-remove-item {{
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 16px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.15s ease;
  }}
  .btn-remove-item:hover {{
    color: var(--danger);
    background: rgba(248, 81, 73, 0.15);
  }}

  /* Footer & Signature Block */
  .footer-sig-block {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-top: 32px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }}
  @media (max-width: 680px) {{
    .footer-sig-block {{ grid-template-columns: 1fr; }}
  }}
  .sig-col h4 {{
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 12px;
  }}
  .sig-line {{
    border-bottom: 1px dashed var(--border-light);
    height: 40px;
    margin-bottom: 6px;
  }}
  .sig-sub {{
    font-size: 11.5px;
    color: var(--text-muted);
  }}

  /* Print Stylesheet */
  @media print {{
    body {{
      background: #fff !important;
      color: #000 !important;
      padding: 0 !important;
    }}
    .top-nav, .action-toolbar, .btn-remove-item {{
      display: none !important;
    }}
    .doc-header, .instructions-card, .kpi-card, .table-box, .footer-sig-block {{
      background: #fff !important;
      border: 1px solid #ccc !important;
      box-shadow: none !important;
      color: #000 !important;
    }}
    .doc-title {{ color: #000 !important; }}
    .kpi-value, .price-aed {{ color: #000 !important; }}
    .po-table th {{
      background: #f0f0f0 !important;
      color: #000 !important;
      border-bottom: 2px solid #000 !important;
    }}
    .po-table td {{
      border-bottom: 1px solid #ddd !important;
      color: #000 !important;
    }}
    .coffee-link {{
      color: #000 !important;
      text-decoration: underline !important;
    }}
  }}
</style>
</head>
<body>

<div class="container">

  <!-- Navigation -->
  <div class="top-nav">
    <a href="index.html" class="nav-back-link">
      ← 통합 허브 대시보드로 돌아가기
    </a>
    <div class="nav-badges">
      <span class="badge-tag badge-po">Official Purchase Order</span>
      <span class="badge-tag" style="background:#111722; color:var(--text-secondary); border:1px solid var(--border);">1 AED ≈ 380 KRW</span>
    </div>
  </div>

  <!-- Document Header -->
  <header class="doc-header">
    <div class="doc-title-row">
      <h1 class="doc-title">📋 UAE 현지 스페셜티 커피 공식 구매 발주서</h1>
      <div class="doc-meta-right">
        <div><strong>발주 문서 번호:</strong> UAE-SPEC-PO-2026</div>
        <div><strong>구매 대상 로스터리:</strong> Archers Coffee & The Espresso Lab</div>
        <div id="printDateStr"></div>
      </div>
    </div>
    <p class="doc-desc">
      본 문서는 아랍에미리트(두바이/샤르자) 현지 매장 방문 구매를 위해 기계 검증(<code>verify_quotes.py</code>)을 통과한 최상급 스페셜티 원두 큐레이션 발주 명세서입니다. 현지 구매 담당자는 하단 목록의 원두명, 로스터리, 가격 및 스펙을 확인한 후 매장에서 구매해 주시기 바랍니다.
    </p>
  </header>

  <!-- Purchasing Instructions for Manager -->
  <div class="instructions-card">
    <div class="inst-title">📌 현지 구매 담당자 필독 가이드 (Purchaser Checklist)</div>
    <ul class="inst-list">
      <li><span>1.</span> <strong>패키지 용량 필수 확인:</strong> 전 품목 <strong>100g 소포장 패키지</strong> 기준입니다.</li>
      <li><span>2.</span> <strong>배전도(Roast) 확인:</strong> 에스프레소용이 아닌 <strong>필터/브루잉용(Filter / Light Roast)</strong>인지 확인하세요.</li>
      <li><span>3.</span> <strong>원두 링크 확인:</strong> 원두명을 클릭하면 로스터리 공식 웹스토어 상품 페이지로 연결됩니다.</li>
      <li><span>4.</span> <strong>신선도 확인:</strong> 매장 진열 품목 중 <strong>로스팅 일자(Roast Date)가 최근 2~3주 이내</strong>인 원두를 우선 수령하세요.</li>
      <li><span>5.</span> <strong>영수증 보관:</strong> 두바이 공항 출국 시 부가세(VAT) 환급을 위해 Tax Invoice 영수증을 챙기세요.</li>
      <li><span>6.</span> <strong>품절 시 대안:</strong> 해당 나노랏이 현장 품절인 경우, 목록 내 다른 동일 로스터리 원두를 수량 대체하세요.</li>
    </ul>
  </div>

  <!-- Summary KPI Cards -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">총 발주 품목 수</div>
      <div class="kpi-value val-gold"><span id="kpiTotalCount">0</span>종</div>
      <div class="kpi-sub">전 품목 100g 개별 패키지</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">로스터리별 구성</div>
      <div class="kpi-value val-blue" style="font-size:18px; line-height:32px;">
        <span id="kpiArchersCount">0</span> 아처스 / <span id="kpiTelCount">0</span> 에소랩
      </div>
      <div class="kpi-sub">샤르자 & 두바이 플래그십</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">현지 결제 예정액 (AED)</div>
      <div class="kpi-value val-gold"><span id="kpiTotalAed">0.0</span> AED</div>
      <div class="kpi-sub">매장 현지 직접 결제 (디르함)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">원화 환산 견적 (KRW)</div>
      <div class="kpi-value val-green">약 <span id="kpiTotalKrw">0</span>원</div>
      <div class="kpi-sub">국내 직구 대비 35~50% 절감</div>
    </div>
  </div>

  <!-- Action Toolbar -->
  <div class="action-toolbar">
    <div class="action-group-left">
      <button type="button" class="po-btn btn-print" onclick="window.print()">🖨️ 발주서 인쇄 / PDF 저장</button>
      <button type="button" class="po-btn" onclick="copyOrderText()">📋 텍스트 발주서 복사 (메신저 전달용)</button>
      <button type="button" class="po-btn" onclick="copyShareableUrl()">🔗 발주서 공유 링크 복사</button>
    </div>
    <div class="action-group-right">
      <a href="index.html#top20Section" class="po-btn">➕ 원두 추가 / 변경하러 가기</a>
      <button type="button" class="po-btn btn-danger" onclick="clearCartAndReset()">🗑️ 발주서 초기화</button>
    </div>
  </div>

  <!-- Fallback Notification Banner -->
  <div id="fallbackNotice" style="display:none; background:rgba(88,166,255,0.1); border:1px solid rgba(88,166,255,0.3); padding:10px 16px; border-radius:8px; font-size:13px; color:var(--blue); margin-bottom:16px;">
    💡 <strong>안내:</strong> 저장된 장바구니 데이터가 없어 시스템 기본 <strong>"엄선 10선 공식 추천 발주 목록"</strong>이 자동으로 로드되었습니다.
  </div>

  <!-- Procurement Table -->
  <div class="table-box">
    <table class="po-table" id="poTable">
      <thead>
        <tr>
          <th style="width:40px; text-align:center;">No.</th>
          <th style="width:130px;">로스터리</th>
          <th>커피 이름 (클릭 시 공식 판매처 ↗) & 스펙</th>
          <th style="text-align:right; width:120px;">현지 가격 (100g)</th>
          <th>테루아 및 가공 방식</th>
          <th>센서리 테이스팅 노트</th>
          <th>핵심 구매 사유 (큐레이션 평)</th>
          <th style="width:50px; text-align:center;">비고</th>
        </tr>
      </thead>
      <tbody id="poTableBody">
        <!-- Rendered via JS -->
      </tbody>
    </table>
  </div>

  <!-- Signature / Approval Block (Print & Delivery) -->
  <div class="footer-sig-block">
    <div class="sig-col">
      <h4>발주자 (Requestor)</h4>
      <div class="sig-line"></div>
      <div class="sig-sub">성명 / 서명 / 일자</div>
    </div>
    <div class="sig-col">
      <h4>현지 구매 담당자 (Procurement Officer)</h4>
      <div class="sig-line"></div>
      <div class="sig-sub">구매 완료 확인 / 영수증 첨부</div>
    </div>
  </div>

</div>

<script>
  // Master Dataset Reference (Top 20)
  const MASTER_COFFEES = {json.dumps(top_20, ensure_ascii=False)};
  const DEFAULT_PICKS = {json.dumps(active_10, ensure_ascii=False)};

  let cartItems = [];

  function initCart() {{
    const today = new Date();
    document.getElementById('printDateStr').textContent = `출력/발주일시: ${{today.getFullYear()}}-${{String(today.getMonth()+1).padStart(2,'0')}}-${{String(today.getDate()).padStart(2,'0')}}`;

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
      }} catch (e) {{
        console.error(e);
      }}
    }}

    // 3. If still empty, fall back to Default 10 Active Picks!
    if (!cartItems || !cartItems.length) {{
      cartItems = [...DEFAULT_PICKS];
      document.getElementById('fallbackNotice').style.display = 'block';
    }}

    renderCartTable();
  }}

  function renderCartTable() {{
    const tbody = document.getElementById('poTableBody');
    tbody.innerHTML = '';

    if (!cartItems.length) {{
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:40px; color:var(--text-muted);">발주서에 담긴 커피가 없습니다. [원두 추가하러 가기]를 눌러 커피를 담아주세요.</td></tr>';
      updateKpis(0, 0, 0, 0, 0);
      return;
    }}

    let totalAed = 0;
    let totalKrw = 0;
    let archersCount = 0;
    let telCount = 0;

    cartItems.forEach((c, idx) => {{
      const pAed = parseFloat(c.price_aed || 0);
      const pKrw = parseInt(c.price_krw || Math.round(pAed * 380));
      totalAed += pAed;
      totalKrw += pKrw;

      if (c.roastery.includes('Archers')) archersCount++;
      else telCount++;

      const rBadgeCls = c.roastery.includes('Archers') ? 'badge-archers' : 'badge-espressolab';
      const rev = c.detailed_review || {{}};
      const reasonText = rev.taste_analysis ? rev.taste_analysis.substring(0, 110) + '...' : (c.overlap_note || '최상위 큐레이션 원두');

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="text-align:center; font-family:'JetBrains Mono',monospace; font-weight:700;">${{idx + 1}}</td>
        <td>
          <span class="roastery-badge ${{rBadgeCls}}">${{c.roastery_badge}}</span>
        </td>
        <td>
          <a href="${{c.source_url}}" target="_blank" rel="noopener noreferrer" class="coffee-link" title="공식 웹스토어로 바로가기">
            ${{c.title}} <span class="out-icon">↗</span>
          </a>
          <div class="spec-sub">${{c.weight || '100g'}} • ${{c.roast || 'Filter Light Roast'}}</div>
        </td>
        <td class="price-cell">
          <div class="price-aed">${{pAed.toFixed(1)}} AED</div>
          <div class="price-krw">약 ${{pKrw.toLocaleString()}}원</div>
        </td>
        <td>
          <div style="font-weight:600; color:#e6edf3;">${{c.country || ''}} • ${{c.farm || ''}}</div>
          <div class="spec-sub">${{c.variety || ''}} (${{c.process || ''}}) • ${{c.altitude || ''}}</div>
        </td>
        <td>
          <div class="notes-tag">✨ ${{c.notes || 'N/A'}}</div>
        </td>
        <td>
          <div class="reason-text">${{reasonText}}</div>
        </td>
        <td style="text-align:center;">
          <button type="button" class="btn-remove-item" onclick="removeItem(${{idx}})" title="발주 목록에서 삭제">✕</button>
        </td>
      `;
      tbody.appendChild(tr);
    }});

    updateKpis(cartItems.length, archersCount, telCount, totalAed, totalKrw);
    saveCartToStorage();
  }}

  function updateKpis(total, archers, tel, aed, krw) {{
    document.getElementById('kpiTotalCount').textContent = total;
    document.getElementById('kpiArchersCount').textContent = archers;
    document.getElementById('kpiTelCount').textContent = tel;
    document.getElementById('kpiTotalAed').textContent = aed.toFixed(1);
    document.getElementById('kpiTotalKrw').textContent = krw.toLocaleString();
  }}

  function removeItem(idx) {{
    cartItems.splice(idx, 1);
    renderCartTable();
  }}

  function saveCartToStorage() {{
    try {{
      localStorage.setItem('coffee_cart', JSON.stringify(cartItems));
    }} catch (e) {{
      console.error(e);
    }}
  }}

  function clearCartAndReset() {{
    if (confirm('발주서 목록을 초기화하시겠습니까?')) {{
      cartItems = [];
      saveCartToStorage();
      renderCartTable();
    }}
  }}

  function copyOrderText() {{
    if (!cartItems.length) {{
      alert('발주서에 담긴 커피가 없습니다.');
      return;
    }}
    let totalAed = 0;
    let lines = ['[📋 UAE 스페셜티 커피 현지 구매 발주서]', '규격: 전 품목 100g 필터용(Filter Light Roast) 필수 확인', '----------------------------------------'];
    cartItems.forEach((c, idx) => {{
      const p = parseFloat(c.price_aed || 0);
      totalAed += p;
      lines.push(`${{idx + 1}}. [${{c.roastery}}] ${{c.title}}`);
      lines.push(`   - 가격: ${{p}} AED (약 ${{Math.round(p*380).toLocaleString()}}원)`);
      lines.push(`   - 컵노트: ${{c.notes}}`);
      lines.push(`   - 구매링크: ${{c.source_url}}`);
    }});
    lines.push('----------------------------------------');
    lines.push(`총 ${{cartItems.length}}종 / 결제 예정액: ${{totalAed.toFixed(1)}} AED (약 ${{Math.round(totalAed*380).toLocaleString()}}원)`);

    navigator.clipboard.writeText(lines.join('\\n')).then(() => {{
      alert('담당자 전달용 발주서 텍스트가 클립보드에 복사되었습니다! 카카오톡이나 이메일에 붙여넣으세요.');
    }}).catch(err => {{
      alert('복사 권한 오류가 발생했습니다.');
    }});
  }}

  function copyShareableUrl() {{
    if (!cartItems.length) {{
      alert('발주서에 담긴 커피가 없습니다.');
      return;
    }}
    const handles = cartItems.map(c => c.handle).join(',');
    const shareUrl = window.location.origin + window.location.pathname + '?items=' + encodeURIComponent(handles);
    navigator.clipboard.writeText(shareUrl).then(() => {{
      alert('발주서 공유 링크가 복사되었습니다! 이 링크를 열면 선택한 품목이 그대로 표시됩니다:\\n' + shareUrl);
    }}).catch(err => {{
      alert('공유 URL 복사 실패');
    }});
  }}

  window.addEventListener('DOMContentLoaded', initCart);
</script>

</body>
</html>
"""

with open('cart.html', 'w', encoding='utf-8') as f:
    f.write(cart_page_code)

print(f"Generated cart.html successfully ({len(cart_page_code)} bytes)")
