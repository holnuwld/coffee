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
  <button type="button" class="m-act-btn btn-print" onclick="generateImmutableSnapshotUrl()" style="background:linear-gradient(135deg, #d29922, #b07d12); color:#000; font-weight:800;" title="현재 시점의 내용으로 영구 동결되는 불변 링크를 생성합니다">
    🔒 발주서 불변 링크 확정 복사 (스냅샷)
  </button>
  <button type="button" class="m-act-btn" onclick="generateSharedCartUrl()" style="color:var(--blue); border-color:rgba(88,166,255,0.4);" title="다른 사람과 장바구니를 함께 수정할 수 있는 링크를 복사합니다">
    👥 장바구니 공동 편집 링크 복사
  </button>
  <button type="button" class="m-act-btn" onclick="window.print()">🖨️ 발주서 인쇄 / PDF 저장</button>
  <button type="button" class="m-act-btn" onclick="copyOrderText()">📋 텍스트 발주서 복사 (메신저용)</button>
  <div style="display:flex; gap:8px;" id="mEditActionRow">
    <a href="mobile_index.html" class="m-act-btn btn-secondary" style="flex:1; text-decoration:none;">➕ 원두 더 담기</a>
    <button type="button" class="m-act-btn btn-secondary" style="width:110px; color:var(--danger);" onclick="resetCart()">🗑️ 초기화</button>
  </div>
</div>

<!-- Snapshot Locked Mode Banner -->
<div id="mSnapshotBanner" style="display:none; margin:0 16px 16px 16px; background:rgba(210,153,34,0.12); border:1.5px solid var(--accent-gold); padding:12px 14px; border-radius:10px;">
  <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
    <span style="font-size:18px;">🔒</span>
    <strong style="color:var(--accent-gold); font-size:13.5px;">발주 확정 불변 스냅샷 (Frozen)</strong>
  </div>
  <div style="font-size:12px; color:#c9d1d9; line-height:1.45;" id="mSnapshotMetaTxt">
    발행 시점의 데이터로 영구 동결되었습니다. 이후 장바구니 변경과 무관하게 당시 내용이 보존됩니다.
  </div>
</div>

<!-- Shared Cart Notice -->
<div id="mSharedCartNotice" style="display:none; margin:0 16px 16px 16px; background:rgba(88,166,255,0.12); border:1px solid rgba(88,166,255,0.4); padding:10px 14px; border-radius:8px; font-size:12.5px; color:var(--blue);">
  👥 <strong>공동 편집 모드:</strong> 동료가 공유한 장바구니 목록이 로드되었습니다.
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
  let isSnapshotMode = false;
  let snapshotMeta = null;

  // Safe UTF-8 Base64 Encoding & Decoding
  function encodeBase64Utf8(str) {{
    return encodeURIComponent(btoa(encodeURIComponent(str).replace(/%([0-9A-F]{{2}})/g, function(match, p1) {{
      return String.fromCharCode('0x' + p1);
    }})));
  }}

  function decodeBase64Utf8(str) {{
    try {{
      const raw = atob(decodeURIComponent(str));
      return decodeURIComponent(Array.prototype.map.call(raw, function(c) {{
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }}).join(''));
    }} catch(e) {{
      console.error('Base64 decode error', e);
      return null;
    }}
  }}

  function initPo() {{
    const today = new Date();
    document.getElementById('mDocMetaDate').innerHTML = `발주 일자: ${{today.getFullYear()}}-${{String(today.getMonth()+1).padStart(2,'0')}}-${{String(today.getDate()).padStart(2,'0')}}<br>대상: Archers Coffee &amp; The Espresso Lab`;

    const urlParams = new URLSearchParams(window.location.search);

    // 1. Check for Immutable Snapshot (Highest Priority)
    const snapParam = urlParams.get('snapshot');
    if (snapParam) {{
      try {{
        const jsonStr = decodeBase64Utf8(snapParam);
        if (jsonStr) {{
          const snapData = JSON.parse(jsonStr);
          if (snapData && snapData.items && snapData.items.length) {{
            isSnapshotMode = true;
            snapshotMeta = snapData;
            cartItems = snapData.items;

            document.getElementById('mSnapshotBanner').style.display = 'block';
            document.getElementById('mSnapshotMetaTxt').innerHTML = `
              <strong>문서 번호:</strong> ${{snapData.po_number || 'PO-LOCKED'}}<br>
              <strong>확정 일시:</strong> ${{snapData.created_at || '기록일시'}}<br>
              이후 장바구니 변경과 완전히 독립된 영구 동결 문서입니다.
            `;
            document.getElementById('mDocMetaDate').innerHTML = `발주 확정일시: ${{snapData.created_at || '확정일자'}}<br>문서 번호: ${{snapData.po_number || 'PO-LOCKED'}}`;

            const editRow = document.getElementById('mEditActionRow');
            if (editRow) editRow.style.display = 'none';

            renderPoItems();
            return;
          }}
        }}
      }} catch(err) {{
        console.error('Snapshot load failed', err);
      }}
    }}

    // 2. Check for Shared Collaborative Cart
    const sharedParam = urlParams.get('shared_cart');
    if (sharedParam) {{
      try {{
        const jsonStr = decodeBase64Utf8(sharedParam);
        if (jsonStr) {{
          const sharedData = JSON.parse(jsonStr);
          if (sharedData && sharedData.handles) {{
            cartItems = MASTER_COFFEES.filter(c => sharedData.handles.includes(c.handle));
            document.getElementById('mSharedCartNotice').style.display = 'block';
            saveStorage();
            renderPoItems();
            return;
          }}
        }}
      }} catch(err) {{
        console.error('Shared cart load failed', err);
      }}
    }}

    // 3. Standard item handles URL param
    const itemHandlesParam = urlParams.get('items');
    if (itemHandlesParam) {{
      const handles = itemHandlesParam.split(',');
      cartItems = MASTER_COFFEES.filter(c => handles.includes(c.handle));
    }}

    // 4. LocalStorage
    if (!cartItems.length) {{
      try {{
        const stored = localStorage.getItem('coffee_cart');
        if (stored) {{
          cartItems = JSON.parse(stored);
        }}
      }} catch (e) {{}}
    }}

    // 5. Fallback to active 10 picks
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
          ${{isSnapshotMode 
            ? '<span style="font-size:11px; color:var(--accent-gold); font-weight:800; padding:2px 6px;">🔒 확정</span>' 
            : `<button type="button" class="btn-del-item" onclick="deleteItem(${{idx}})" title="품목 삭제">✕</button>`}}
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
    if (!isSnapshotMode) {{
      saveStorage();
    }}
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
    if (isSnapshotMode) return;
    cartItems.splice(idx, 1);
    renderPoItems();
    showToast('품목이 발주서에서 삭제되었습니다.');
  }}

  function saveStorage() {{
    if (isSnapshotMode) return;
    try {{
      localStorage.setItem('coffee_cart', JSON.stringify(cartItems));
    }} catch (e) {{}}
  }}

  function resetCart() {{
    if (isSnapshotMode) return;
    if (confirm('발주서 목록을 초기화하시겠습니까?')) {{
      cartItems = [];
      saveStorage();
      renderPoItems();
      showToast('발주서가 초기화되었습니다.');
    }}
  }}

  // 1. Generate Immutable Snapshot URL (FROZEN)
  function generateImmutableSnapshotUrl() {{
    if (!cartItems.length) {{
      alert('발주서에 담긴 커피가 없습니다.');
      return;
    }}
    const now = new Date();
    const dateStr = `${{now.getFullYear()}}-${{String(now.getMonth()+1).padStart(2,'0')}}-${{String(now.getDate()).padStart(2,'0')}} ${{String(now.getHours()).padStart(2,'0')}}:${{String(now.getMinutes()).padStart(2,'0')}}`;
    const poCode = 'PO-' + now.getFullYear() + String(now.getMonth()+1).padStart(2,'0') + String(now.getDate()).padStart(2,'0') + '-' + Math.random().toString(36).substring(2,6).toUpperCase();

    const snapshotPayload = {{
      po_number: poCode,
      created_at: dateStr,
      items: cartItems.map(c => ({{
        handle: c.handle,
        title: c.title,
        roastery: c.roastery,
        roastery_badge: c.roastery_badge,
        price_aed: parseFloat(c.price_aed || 0),
        price_krw: parseInt(c.price_krw || Math.round((c.price_aed || 0) * 380)),
        notes: c.notes,
        country: c.country,
        farm: c.farm,
        producer: c.producer,
        variety: c.variety,
        process: c.process,
        altitude: c.altitude,
        roast: c.roast,
        weight: c.weight,
        source_url: c.source_url,
        overlap_note: c.overlap_note,
        score_total: c.score_total,
        score_taste: c.score_taste,
        score_price: c.score_price,
        score_rarity: c.score_rarity,
        max_prior_sim: c.max_prior_sim,
        similar_target_rank: c.similar_target_rank,
        detailed_review: c.detailed_review
      }}))
    }};

    const encoded = encodeBase64Utf8(JSON.stringify(snapshotPayload));
    const snapUrl = window.location.origin + window.location.pathname + '?snapshot=' + encoded;

    navigator.clipboard.writeText(snapUrl).then(() => {{
      alert(`🔒 [불변 발주서 링크 복사 완료]\\n\\n발주 번호: ${{poCode}}\\n확정 일시: ${{dateStr}}\\n\\n✅ 본 링크는 생성 시점의 내용으로 영구 동결(Frozen)되었습니다.\\n이후 장바구니를 다른 사람이 어떻게 수정하더라도, 이 링크를 열면 당시 발주서 내용이 절대 변경되지 않습니다!\\n\\n구매 담당자에게 이 링크를 전달하세요.`);
    }}).catch(() => {{
      prompt('불변 발주서 링크입니다:', snapUrl);
    }});
  }}

  // 2. Generate Collaborative Cart URL (MUTABLE)
  function generateSharedCartUrl() {{
    if (!cartItems.length) {{
      alert('장바구니에 담긴 커피가 없습니다.');
      return;
    }}
    const sharedPayload = {{
      updated_at: new Date().toISOString(),
      handles: cartItems.map(c => c.handle)
    }};
    const encoded = encodeBase64Utf8(JSON.stringify(sharedPayload));
    const shareUrl = window.location.origin + window.location.pathname + '?shared_cart=' + encoded;

    navigator.clipboard.writeText(shareUrl).then(() => {{
      alert(`👥 [장바구니 공동 편집 링크 복사 완료]\\n\\n이 링크를 동료에게 전달하면 동료가 열어서 원두를 추가/수정할 수 있습니다.`);
    }}).catch(() => {{
      prompt('공동 편집 링크입니다:', shareUrl);
    }});
  }}

  function copyOrderText() {{
    if (!cartItems.length) {{
      alert('발주서에 담긴 커피가 없습니다.');
      return;
    }}
    let totalAed = 0;
    const poNum = snapshotMeta ? snapshotMeta.po_number : 'PO-DRAFT';
    const dateInfo = snapshotMeta ? ` (확정일시: ${{snapshotMeta.created_at}})` : '';
    let lines = [`[📋 UAE 스페셜티 커피 현지 구매 발주서 - ${{poNum}}${{dateInfo}}]`, '규격: 전 품목 100g 필터용(Filter Light Roast) 필수', '----------------------------------------'];
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
    generateImmutableSnapshotUrl();
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
