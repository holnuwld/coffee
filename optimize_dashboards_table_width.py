import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# 1. OPTIMIZE archers_coffee_clean_verified.html
# ==============================================================================
print("Optimizing archers_coffee_clean_verified.html table widths & headers...")
with open('c:/cowork/coffee/archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    arc_html = f.read()

# 1-1. Update CSS: Slim paddings and remove white-space: nowrap on th
arc_css_old = """  th {
    background: #1f242c;
    color: #c9d1d9;
    font-weight: 600;
    padding: 12px 14px;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
    position: sticky;
    top: 0;
    z-index: 10;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s;
  }"""

arc_css_new = """  th {
    background: #1f242c;
    color: #c9d1d9;
    font-weight: 700;
    padding: 9px 5px;
    border-bottom: 2px solid var(--border);
    white-space: normal;
    line-height: 1.25;
    position: sticky;
    top: 0;
    z-index: 10;
    cursor: pointer;
    user-select: none;
    text-align: center;
    vertical-align: middle;
    word-break: keep-all;
    transition: background 0.15s;
  }"""

if arc_css_old in arc_html:
    arc_html = arc_html.replace(arc_css_old, arc_css_new)
    print("Archers CSS: th updated successfully.")
else:
    # Try regex replacement
    arc_html = re.sub(
        r'th\s*\{\s*background:\s*#1f242c;.*?white-space:\s*nowrap;.*?transition:\s*background\s*0\.15s;\s*\}',
        arc_css_new.strip(),
        arc_html,
        flags=re.DOTALL
    )
    print("Archers CSS: th updated via regex.")

# Slim td padding
arc_html = re.sub(
    r'td\s*\{\s*padding:\s*12px\s*14px;',
    'td {\n    padding: 8px 6px; word-break: keep-all;',
    arc_html
)

# 1-2. Update Table Header with Compact Labels and <br>
arc_thead_pattern = r'<thead>\s*<tr>\s*<th onclick="sortTable\(0, \'number\'\)".*?</tr>\s*</thead>'
arc_new_thead = """<thead>
        <tr>
          <th onclick="sortTable(0, 'number')" style="width:36px;">#<span class="sort-icon">▲▼</span></th>
          <th style="width:65px;">사진</th>
          <th onclick="sortTable(2, 'number')" style="width:85px;">⭐ 종합점수<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(100점)</span><span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(3, 'string')" style="width:75px;">컬렉션<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(4, 'string')" style="min-width:140px; text-align:left;">커피 이름<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(공식몰 링크 ↗)</span><span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(5, 'string')" style="width:60px;">국가<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(6, 'string')" style="width:75px;">지역<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(7, 'string')" style="width:80px;">농장/<br>스테이션<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(8, 'string')" style="width:80px;">농부/<br>프로듀서<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(9, 'string')" style="width:70px;">품종<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(10, 'string')" style="width:75px;">가공방식<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(프로세스)</span><span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(11, 'string')" style="width:60px;">고도<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(12, 'string')" style="width:58px;">배전도<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(13, 'string')" style="min-width:120px; text-align:left;">컵노트<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(14, 'string')" style="width:45px;">중량<span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(15, 'number')" style="width:78px;">현지 가격<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(AED/원화)</span><span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(16, 'number')" style="width:78px;">100g 가격<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(기준가)</span><span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(17, 'string')" style="min-width:110px; text-align:left;">국내 유통처<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(유사 랏)</span><span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(18, 'string')" style="width:80px;">국내 시세<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(100g)</span><span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(19, 'string')" style="min-width:110px; text-align:left;">구매 메리트<br>분석<span class="sort-icon">▲▼</span></th>
          <th style="min-width:110px; text-align:left;">해외 후기<br><span style="font-size:10px; color:#6e7681;">(Reddit)</span></th>
          <th style="width:45px;">검증</th>
        </tr>
      </thead>"""

arc_html = re.sub(arc_thead_pattern, arc_new_thead, arc_html, flags=re.DOTALL)

# 1-3. Relax nowrap on Korean price cells
arc_html = re.sub(
    r'<td style="color:#8b949e; white-space:nowrap;">',
    '<td style="color:#8b949e; word-break:keep-all; line-height:1.25;">',
    arc_html
)

with open('c:/cowork/coffee/archers_coffee_clean_verified.html', 'w', encoding='utf-8') as f:
    f.write(arc_html)
print("Archers dashboard table optimization complete!")


# ==============================================================================
# 2. OPTIMIZE theespressolab_verified.html
# ==============================================================================
print("Optimizing theespressolab_verified.html table widths & headers...")
with open('c:/cowork/coffee/theespressolab_verified.html', 'r', encoding='utf-8') as f:
    tel_html = f.read()

# 2-1. Update CSS: Slim paddings and remove white-space: nowrap on th
tel_css_old = """  .data-table th {
    background: #0f1621;
    color: var(--text-secondary);
    font-weight: 700;
    text-align: left;
    padding: 16px 16px;
    border-bottom: 2px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 20;
    cursor: pointer;
    user-select: none;
    transition: color 0.15s ease;
    white-space: nowrap;
  }"""

tel_css_new = """  .data-table th {
    background: #0f1621;
    color: var(--text-secondary);
    font-weight: 700;
    text-align: center;
    padding: 9px 5px;
    border-bottom: 2px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 20;
    cursor: pointer;
    user-select: none;
    transition: color 0.15s ease;
    white-space: normal;
    line-height: 1.25;
    word-break: keep-all;
    vertical-align: middle;
  }"""

if tel_css_old in tel_html:
    tel_html = tel_html.replace(tel_css_old, tel_css_new)
    print("TEL CSS: th updated successfully.")
else:
    tel_html = re.sub(
        r'\.data-table th\s*\{\s*background:\s*#0f1621;.*?white-space:\s*nowrap;\s*\}',
        tel_css_new.strip(),
        tel_html,
        flags=re.DOTALL
    )
    print("TEL CSS: th updated via regex.")

# Slim td padding
tel_html = re.sub(
    r'\.data-table td\s*\{\s*padding:\s*14px\s*16px;',
    '.data-table td {\n    padding: 8px 6px; word-break: keep-all;',
    tel_html
)

# 2-2. Update Table Header with Compact Labels and <br>
tel_thead_pattern = r'<thead>\s*<tr>\s*<th onclick="sortTable\(0, \'num\'\)".*?</tr>\s*</thead>'
tel_new_thead = """<thead>
          <tr>
            <th onclick="sortTable(0, 'num')" style="width:36px;">#<span class="sort-arrow"></span></th>
            <th style="width:65px;">사진</th>
            <th onclick="sortTable(2, 'num')" style="width:85px;">⭐ 종합점수<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(100점)</span><span class="sort-arrow"></span></th>
            <th onclick="sortTable(3, 'str')" style="min-width:140px; text-align:left;">커피 이름<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(원문 링크 ↗)</span><span class="sort-arrow"></span></th>
            <th onclick="sortTable(4, 'str')" style="width:60px;">국가<span class="sort-arrow"></span></th>
            <th onclick="sortTable(5, 'str')" style="width:75px;">지역<span class="sort-arrow"></span></th>
            <th onclick="sortTable(6, 'str')" style="width:80px;">농장<span class="sort-arrow"></span></th>
            <th onclick="sortTable(7, 'str')" style="width:80px;">농부/<br>프로듀서<span class="sort-arrow"></span></th>
            <th onclick="sortTable(8, 'str')" style="width:70px;">품종<span class="sort-arrow"></span></th>
            <th onclick="sortTable(9, 'str')" style="width:75px;">가공 방식<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(프로세스)</span><span class="sort-arrow"></span></th>
            <th onclick="sortTable(10, 'str')" style="width:60px;">재배 고도<span class="sort-arrow"></span></th>
            <th onclick="sortTable(11, 'str')" style="width:58px;">배전도<span class="sort-arrow"></span></th>
            <th onclick="sortTable(12, 'str')" style="min-width:120px; text-align:left;">컵노트<span class="sort-arrow"></span></th>
            <th onclick="sortTable(13, 'str')" class="text-center" style="width:45px;">중량<span class="sort-arrow"></span></th>
            <th onclick="sortTable(14, 'num')" style="width:78px;">현지 가격<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(AED/원화)</span><span class="sort-arrow"></span></th>
            <th onclick="sortTable(15, 'num')" style="width:78px;">100g 가격<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(기준가)</span><span class="sort-arrow"></span></th>
            <th style="min-width:110px; text-align:left;">한국 판매처<br><span style="font-size:10px; font-weight:normal; opacity:0.8;">(링크 ↗)</span></th>
            <th style="min-width:120px; text-align:left;">한국 시세 &<br>구매 메리트</th>
            <th onclick="sortTable(18, 'str')" style="min-width:120px; text-align:left;">커뮤니티 평점<br>& 후기<span class="sort-arrow"></span></th>
            <th class="text-center" style="width:45px;">검증</th>
          </tr>
        </thead>"""

tel_html = re.sub(tel_thead_pattern, tel_new_thead, tel_html, flags=re.DOTALL)

with open('c:/cowork/coffee/theespressolab_verified.html', 'w', encoding='utf-8') as f:
    f.write(tel_html)
print("Espresso Lab dashboard table optimization complete!")
