import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# 1. ARCHERS DASHBOARD: BADGES -> TEXT & MULTI-SCORE SORTING
# ==============================================================================
print("Updating archers_coffee_clean_verified.html...")
with open('c:/cowork/coffee/archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    arc = f.read()

# 1-1. Remove badge styling from spec-tag & badge-pass
# Replace <span class="spec-tag">Collection</span> with plain text or compact span
def clean_spec_tag(m):
    txt = m.group(1).strip()
    # Add gentle break for long collection names
    txt = txt.replace('Competition Series ', 'Competition<br>')
    txt = txt.replace('Competition 2025', 'Competition<br>2025')
    txt = txt.replace('Micro-lot Reserve', 'Reserve<br>Microlot')
    return f'<div style="font-weight:600; font-size:11.5px; color:#8b949e; line-height:1.2; word-break:keep-all;">{txt}</div>'

arc = re.sub(r'<span class="spec-tag">([^<]+)</span>', clean_spec_tag, arc)
arc = re.sub(r'<span class="badge-pass">✓ 통과</span>', '<span style="color:#3fb950; font-weight:700; font-size:11.5px;">✓ 통과</span>', arc)

# 1-2. Update score header in thead with sub-sorts (종합/맛/값/희)
arc_score_th_old = r'<th onclick="sortTable\(2, \'number\'\)" style="width:85px;">⭐ 종합점수<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">\(100점\)</span><span class="sort-icon">▲▼</span></th>'
arc_score_th_new = """<th class="th-score-head" style="width:105px; text-align:center; padding:5px 2px; user-select:none;">
            <div onclick="sortScoreCol('total')" style="cursor:pointer; font-weight:800; font-size:12px; color:var(--accent-gold);" title="종합 점수 기준 정렬">
              ⭐ 종합점수 <span id="sortInd_arch_total" style="font-size:9.5px;">▼</span>
            </div>
            <div style="font-size:10.5px; color:#8b949e; margin-top:2px; display:flex; justify-content:center; align-items:center; gap:2px;">
              <span onclick="sortScoreCol('taste')" id="sortTrigger_arch_taste" style="cursor:pointer; padding:1px 3px; border-radius:3px; font-weight:700;" title="맛 점수(50점 만점) 정렬">맛<span id="sortInd_arch_taste" style="font-size:9px;">↕</span></span>
              <span>/</span>
              <span onclick="sortScoreCol('price')" id="sortTrigger_arch_price" style="cursor:pointer; padding:1px 3px; border-radius:3px; font-weight:700;" title="가격 점수(30점 만점) 정렬">값<span id="sortInd_arch_price" style="font-size:9px;">↕</span></span>
              <span>/</span>
              <span onclick="sortScoreCol('rarity')" id="sortTrigger_arch_rarity" style="cursor:pointer; padding:1px 3px; border-radius:3px; font-weight:700;" title="희소성(20점 만점) 정렬">희<span id="sortInd_arch_rarity" style="font-size:9px;">↕</span></span>
            </div>
          </th>"""

arc = re.sub(arc_score_th_old, arc_score_th_new, arc)

# 1-3. Ensure each td.td-score has data-total, data-taste, data-price, data-rarity
def enrich_td_score(m):
    tot = m.group(1)
    inner = m.group(2)
    # Parse 맛, 값, 희
    t_m = re.search(r'맛\s*([\d.]+)', inner)
    p_m = re.search(r'값\s*([\d.]+)', inner)
    r_m = re.search(r'희\s*([\d.]+)', inner)
    taste = t_m.group(1) if t_m else "38.0"
    price = p_m.group(1) if p_m else "27.0"
    rarity = r_m.group(1) if r_m else "20.0"
    return f'<td class="td-score" data-value="{tot}" data-total="{tot}" data-taste="{taste}" data-price="{price}" data-rarity="{rarity}" style="text-align:center; vertical-align:middle;">{inner}</td>'

arc = re.sub(r'<td class="td-score"[^>]*data-value="([^"]+)"[^>]*>(.*?)</td>', enrich_td_score, arc, flags=re.DOTALL)


# 1-4. Add sortScoreCol JavaScript function
arc_js_func = """
  let currentScoreSortKey = 'total';
  let currentScoreSortDir = 'desc';

  function sortScoreCol(key) {
    if (currentScoreSortKey === key) {
      currentScoreSortDir = (currentScoreSortDir === 'desc') ? 'asc' : 'desc';
    } else {
      currentScoreSortKey = key;
      currentScoreSortDir = 'desc';
    }

    const keys = ['total', 'taste', 'price', 'rarity'];
    keys.forEach(k => {
      const ind = document.getElementById('sortInd_arch_' + k);
      const trig = document.getElementById('sortTrigger_arch_' + k);
      if (k === currentScoreSortKey) {
        if (ind) {
          ind.textContent = (currentScoreSortDir === 'desc') ? '▼' : '▲';
          ind.style.color = 'var(--accent-gold)';
        }
        if (trig) trig.style.color = 'var(--accent-gold)';
      } else {
        if (ind) {
          ind.textContent = '↕';
          ind.style.color = '';
        }
        if (trig) trig.style.color = '';
      }
    });

    const tbody = document.getElementById('tableBody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((rowA, rowB) => {
      const cellA = rowA.querySelector('.td-score');
      const cellB = rowB.querySelector('.td-score');
      if (!cellA || !cellB) return 0;

      const valA = parseFloat(cellA.getAttribute('data-' + key) || 0);
      const valB = parseFloat(cellB.getAttribute('data-' + key) || 0);

      let diff = (currentScoreSortDir === 'desc') ? (valB - valA) : (valA - valB);
      if (diff !== 0) return diff;

      // Secondary: total
      const totA = parseFloat(cellA.getAttribute('data-total') || 0);
      const totB = parseFloat(cellB.getAttribute('data-total') || 0);
      return totB - totA;
    });

    rows.forEach(r => tbody.appendChild(r));
  }
"""

if 'function sortScoreCol(' not in arc:
    arc = arc.replace('function sortTable(columnIndex, type) {', arc_js_func + '\n  function sortTable(columnIndex, type) {', 1)

with open('c:/cowork/coffee/archers_coffee_clean_verified.html', 'w', encoding='utf-8') as f:
    f.write(arc)
print("Archers dashboard updated with plain text tags and multi-score sorting!")


# ==============================================================================
# 2. ESPRESSO LAB DASHBOARD: BADGES -> TEXT & MULTI-SCORE SORTING
# ==============================================================================
print("Updating theespressolab_verified.html...")
with open('c:/cowork/coffee/theespressolab_verified.html', 'r', encoding='utf-8') as f:
    tel = f.read()

# 2-1. Remove badge classes from variety, process, country, roast, verified
# Replace badges with clean text
tel = re.sub(r'<span class="badge badge-country">([^<]+)</span>', r'<div style="font-weight:600; font-size:12px;">\1</div>', tel)
tel = re.sub(r'<span class="badge badge-variety">([^<]+)</span>', r'<div style="font-weight:500; font-size:12px; word-break:keep-all; line-height:1.25;">\1</div>', tel)
tel = re.sub(r'<span class="badge badge-process">([^<]+)</span>', r'<div style="font-weight:500; font-size:12px; word-break:keep-all; line-height:1.25;">\1</div>', tel)
tel = re.sub(r'<span class="badge badge-roast">([^<]+)</span>', r'<div style="font-size:11.5px; color:var(--text-muted);">\1</div>', tel)
tel = re.sub(r'<span class="badge badge-verified">✓ 통과</span>', r'<span style="color:#3fb950; font-weight:700; font-size:11.5px;">✓ 통과</span>', tel)
tel = re.sub(r'<span class="no-import-tag">([^<]+)</span>', r'<div style="font-size:11px; color:#8b949e; word-break:keep-all;">\1</div>', tel)

# 2-2. Update score header in thead with sub-sorts (종합/맛/값/희)
tel_score_th_old = r'<th onclick="sortTable\(2, \'num\'\)" style="width:85px;">⭐ 종합점수<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">\(100점\)</span><span class="sort-arrow"></span></th>'
tel_score_th_new = """<th class="th-score-head text-center" style="width:105px; padding:5px 2px; user-select:none;">
            <div onclick="sortScoreCol('total')" style="cursor:pointer; font-weight:800; font-size:12px; color:var(--accent-gold);" title="종합 점수 기준 정렬">
              ⭐ 종합점수 <span id="sortInd_tel_total" style="font-size:9.5px;">▼</span>
            </div>
            <div style="font-size:10.5px; color:var(--text-muted); margin-top:2px; display:flex; justify-content:center; align-items:center; gap:2px;">
              <span onclick="sortScoreCol('taste')" id="sortTrigger_tel_taste" style="cursor:pointer; padding:1px 3px; border-radius:3px; font-weight:700;" title="맛 점수(50점 만점) 정렬">맛<span id="sortInd_tel_taste" style="font-size:9px;">↕</span></span>
              <span>/</span>
              <span onclick="sortScoreCol('price')" id="sortTrigger_tel_price" style="cursor:pointer; padding:1px 3px; border-radius:3px; font-weight:700;" title="가격 점수(30점 만점) 정렬">값<span id="sortInd_tel_price" style="font-size:9px;">↕</span></span>
              <span>/</span>
              <span onclick="sortScoreCol('rarity')" id="sortTrigger_tel_rarity" style="cursor:pointer; padding:1px 3px; border-radius:3px; font-weight:700;" title="희소성(20점 만점) 정렬">희<span id="sortInd_tel_rarity" style="font-size:9px;">↕</span></span>
            </div>
          </th>"""

tel = re.sub(tel_score_th_old, tel_score_th_new, tel)

# 2-3. Enrich td.td-score with data-total, data-taste, data-price, data-rarity
tel = re.sub(r'<td class="text-center font-mono td-score"[^>]*data-value="([^"]+)"[^>]*>(.*?)</td>', enrich_td_score, tel, flags=re.DOTALL)


# 2-4. Add sortScoreCol JavaScript function
tel_js_func = """
    let currentScoreSortKey = 'total';
    let currentScoreSortDir = 'desc';

    function sortScoreCol(key) {
      if (currentScoreSortKey === key) {
        currentScoreSortDir = (currentScoreSortDir === 'desc') ? 'asc' : 'desc';
      } else {
        currentScoreSortKey = key;
        currentScoreSortDir = 'desc';
      }

      const keys = ['total', 'taste', 'price', 'rarity'];
      keys.forEach(k => {
        const ind = document.getElementById('sortInd_tel_' + k);
        const trig = document.getElementById('sortTrigger_tel_' + k);
        if (k === currentScoreSortKey) {
          if (ind) {
            ind.textContent = (currentScoreSortDir === 'desc') ? '▼' : '▲';
            ind.style.color = 'var(--accent-gold)';
          }
          if (trig) trig.style.color = 'var(--accent-gold)';
        } else {
          if (ind) {
            ind.textContent = '↕';
            ind.style.color = '';
          }
          if (trig) trig.style.color = '';
        }
      });

      const tbody = document.querySelector('#coffeeTable tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));

      rows.sort((rowA, rowB) => {
        const cellA = rowA.querySelector('.td-score');
        const cellB = rowB.querySelector('.td-score');
        if (!cellA || !cellB) return 0;

        const valA = parseFloat(cellA.getAttribute('data-' + key) || 0);
        const valB = parseFloat(cellB.getAttribute('data-' + key) || 0);

        let diff = (currentScoreSortDir === 'desc') ? (valB - valA) : (valA - valB);
        if (diff !== 0) return diff;

        const totA = parseFloat(cellA.getAttribute('data-total') || 0);
        const totB = parseFloat(cellB.getAttribute('data-total') || 0);
        return totB - totA;
      });

      rows.forEach(r => tbody.appendChild(r));
    }
"""

if 'function sortScoreCol(' not in tel:
    tel = tel.replace('function sortTable(colIndex, type) {', tel_js_func + '\n    function sortTable(colIndex, type) {', 1)

with open('c:/cowork/coffee/theespressolab_verified.html', 'w', encoding='utf-8') as f:
    f.write(tel)
print("Espresso Lab dashboard updated with plain text tags and multi-score sorting!")
