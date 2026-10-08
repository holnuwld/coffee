import json
import re
import sys
from scoring_master import score_coffee_item

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load data
with open('new_coffee_dates.json', encoding='utf-8') as f:
    dates_map = json.load(f)

with open('new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
    archers_raw = json.load(f)

with open('espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
    tel_raw = json.load(f)

# The exactly 29 newly added coffees today
new_archers = archers_raw[-29:]
# The exactly 2 newly added coffees today
new_tel = tel_raw[-2:]

print(f"Loaded {len(new_archers)} new Archers coffees and {len(new_tel)} new Espresso Lab coffees.")

BADGE_CSS = """
  /* TODAY NEW COFFEES HIGHLIGHT */
  .today-new-coffee-title {
    color: #388bfd !important;
    font-weight: 700;
  }
  [data-theme="light"] .today-new-coffee-title {
    color: #2563eb !important;
  }
  .badge-new-date {
    display: inline-block;
    font-size: 10px;
    font-weight: 800;
    background: rgba(56, 139, 253, 0.15);
    color: #388bfd;
    border: 1px solid rgba(56, 139, 253, 0.35);
    border-radius: 4px;
    padding: 1px 5px;
    margin-left: 6px;
    vertical-align: middle;
    letter-spacing: 0.5px;
    line-height: 1.2;
  }
  [data-theme="light"] .badge-new-date {
    background: rgba(37, 99, 235, 0.1);
    color: #2563eb;
    border-color: rgba(37, 99, 235, 0.3);
  }
"""

# ==============================================================================
# A. UPDATE archers_coffee_clean_verified.html
# ==============================================================================
with open('archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    arch_html = f.read()

# 1. Add CSS
if '.today-new-coffee-title' not in arch_html:
    arch_html = arch_html.replace('</style>', BADGE_CSS + '\n</style>', 1)

# 2. Update existing recommendation cards in archers desktop
recs_to_update = {
    'panama-terroir-finca-deborah': ('Panama - Finca Deborah, Terroir (Classic Washed Geisha)', '1025'),
    'brazil-santuario-sul-sudan-rume-washed': ('Brazil - Santuario Sul Sudan Rume Washed', '1214'),
    'kenya-karimikui-aa': ('Kenya - Karimikui AA (Washed)', '1130'),
    'ethiopia-alo-coffee-mewa-village': ('Ethiopia - Alo Coffee Mewa Village', '0920')
}

for h, (t, d) in recs_to_update.items():
    old_link = f'>{t} ↗<'
    new_link = f' class="today-new-coffee-title">{t} <span class="badge-new-date">{d}</span> ↗<'
    if old_link in arch_html:
        arch_html = arch_html.replace(old_link, new_link)
        print(f"Updated Archers desktop rec: {t}")

# 3. Add table rows for all 29 new Archers coffees
rows_to_add = []
start_idx = 118
for c in new_archers:
    h = c['handle']
    sc = score_coffee_item(c, 'Archers')
    d = dates_map.get(h, '1008')
    img = c.get('image_url') or 'https://via.placeholder.com/68x86?text=Archers'
    col = c.get('collection', 'Specialty Selection 2026')
    col_short = 'Specialty<br>2026' if 'Specialty' in col else ('Comp<br>2025' if 'Comp' in col else 'Reserve<br>2025')
    p_aed = c.get('price_aed', 0)
    p_krw = c.get('price_krw', 0)
    p100_aed = c.get('price_per_100g_aed', p_aed)
    p100_krw = c.get('price_per_100g_krw', p_krw)

    row_html = f"""<tr data-collection="{col}">
          <td style="color:#6e7681; font-weight:600;" data-value="{start_idx}">{start_idx}</td>
          <td class="td-pkg">
            <div class="pkg-img-wrap" onclick="openLightbox('{img}', '{h}')">
              <img src="{img}" alt="{h}" class="pkg-thumb" loading="lazy" onerror="this.src='https://via.placeholder.com/68x86?text=Archers'">
              <span class="zoom-icon">🔍</span>
            </div>
          </td>
          <td class="td-score" data-value="{sc['score_total']}" data-total="{sc['score_total']}" data-taste="{sc['score_taste']}" data-price="{sc['score_price']}" data-rarity="{sc['score_rarity']}" style="text-align:center; vertical-align:middle;">
            <div style="font-weight:800; font-size:14px; color:#d29922;">⭐ {sc['score_total']}</div>
            <div style="font-size:10px; color:#8b949e; white-space:nowrap;">맛 {sc['score_taste']} / 값 {sc['score_price']} / 희 {sc['score_rarity']}</div>
          </td>
          <td><div style="font-weight:600; font-size:11.5px; color:#8b949e; line-height:1.2; word-break:keep-all;">{col_short}</div></td>
          <td class="cell-title">
            <a href="{c['source_url']}" target="_blank" class="today-new-coffee-title">{c['title']} <span class="badge-new-date">{d}</span> ↗</a>
          </td>
          <td><strong>{c['country']}</strong></td>
          <td>{c.get('location', c['country'])}</td>
          <td>{c.get('farm', '-')}</td>
          <td>{c.get('producer', '-')}</td>
          <td><div style="font-weight:600; font-size:11.5px; color:#8b949e; line-height:1.2; word-break:keep-all;">{c['variety']}</div></td>
          <td>{c['process']}</td>
          <td>{c.get('altitude', '-')}</td>
          <td>{c.get('roast', '-')}</td>
          <td class="cell-notes">{c['tasting_notes']}</td>
          <td style="white-space:nowrap;">{c.get('weight', '100g')}</td>
          <td class="cell-price" data-value="{p_aed}">
            AED {p_aed}
            <div class="cell-price-krw">약 {p_krw:,}원</div>
          </td>
          <td class="cell-price" data-value="{p100_aed}">
            AED {p100_aed}
            <div class="cell-price-krw">약 {p100_krw:,}원</div>
          </td>
          <td class="cell-korea">{c.get('korea_seller', '국내 미수입 독점 랏')}</td>
          <td style="color:#8b949e; word-break:keep-all; line-height:1.25;">{c.get('korea_price', '-')}</td>
          <td class="cell-merit">{c.get('purchase_merit', '-')}</td>
          <td class="cell-review">
            {c.get('user_review', '아처스 공식 최신 릴리즈 랏.')} <br>
            <a href="{c['source_url']}" target="_blank" style="font-size:11px; color:#58a6ff;">[공식 링크 ↗]</a>
          </td>
          <td><span class="badge-pass">VERIFIED</span></td>
        </tr>"""
    rows_to_add.append(row_html)
    start_idx += 1

if rows_to_add:
    arch_html = arch_html.replace('</tbody>', '\n' + '\n'.join(rows_to_add) + '\n      </tbody>', 1)
    print(f"Added {len(rows_to_add)} table rows to Archers desktop dashboard!")

# Update tab button count
arch_html = arch_html.replace('전체 보기 (117)', f'전체 보기 ({start_idx - 1})')
if 'Specialty Selection 2026' not in arch_html[arch_html.find('class="tabs"'):arch_html.find('class="search-box"')]:
    arch_html = arch_html.replace(
        '<button class="tab-btn" onclick="switchTab(\'Microlot Selection 2026\')">Microlot Selection 2026 (12)</button>',
        '<button class="tab-btn" onclick="switchTab(\'Microlot Selection 2026\')">Microlot Selection 2026 (12)</button>\n      <button class="tab-btn" onclick="switchTab(\'Specialty Selection 2026\')">Specialty Selection 2026 (29)</button>'
    )

with open('archers_coffee_clean_verified.html', 'w', encoding='utf-8') as f:
    f.write(arch_html)
print("Updated archers_coffee_clean_verified.html successfully!")


# ==============================================================================
# B. UPDATE theespressolab_verified.html
# ==============================================================================
with open('theespressolab_verified.html', 'r', encoding='utf-8') as f:
    tel_html = f.read()

# 1. Add CSS
if '.today-new-coffee-title' not in tel_html:
    tel_html = tel_html.replace('</style>', BADGE_CSS + '\n</style>', 1)

# 2. Update recommendation cards: Caballero & Add Samambaia
caballero_old = '>Caballero Bomba de Fruta #1 (Batch #6) ↗<'
caballero_new = ' class="today-new-coffee-title">Caballero Bomba de Fruta #1 (Batch #6) <span class="badge-new-date">1008</span> ↗<'
if caballero_old in tel_html:
    tel_html = tel_html.replace(caballero_old, caballero_new)
    print("Updated Caballero recommendation card with badge!")

samambaia_card = """
      <!-- Expert 5 (NEW Release) -->
      <div class="rec-card expert" style="border-left: 4px solid var(--accent-gold);">
        <div class="rec-card-header">
          <img src="https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png" alt="Samambaia Natural Yellow Catucai" class="rec-pkg-img" onclick="openLightbox(this.src, 'Samambaia Natural Yellow Catucai')" onerror="this.src='https://via.placeholder.com/105x130?text=Package'">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-gold" style="background:rgba(217, 119, 6, 0.15); color:#f59e0b; border:1px solid rgba(217, 119, 6, 0.3);">🌟 NEW 신규 입고 | 120년 전통 브라질 명문 농장 옐로우 카투카이</span>
            <h3>
              <a href="https://theespressolab.com/products-details/samambaia-natural-yellow-catucai" target="_blank" class="rec-title-link today-new-coffee-title">
                Samambaia Natural Yellow Catucai <span class="badge-new-date">1008</span> ↗
              </a>
            </h3>
            <div class="rec-origin">🇧🇷 Brazil | Sul de Minas (1200 masl)</div>
            <div class="rec-pricing">
              <span class="rec-price-main">76.19 AED (약 28,950원)</span>
              <span class="rec-price-sub">(100g당 76.19 AED (약 28,950원))</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title blue">💎 큐레이터 선별 사유</div>
            <div class="rec-box-text"><strong>120년 역사의 브라질 최고 명문 Fazenda Samambaia의 희귀 옐로우 카투카이 내추럴</strong><br>밀크초콜릿과 헤이즐넛의 고소한 단맛, 황자두의 부드러운 산미와 카라멜의 달콤한 여운이 에스프레소와 브루잉 전반에서 탁월한 밸런스를 뿜어냅니다.</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">💬 평가 & 토론 원문</div>
            <div class="rec-box-text">
              The Espresso Lab 공식 커핑: "밀크초콜릿, 헤이즐넛, 황자두, 카라멜 단맛의 정교한 밸런스."<br>
              <a href="https://theespressolab.com/products-details/samambaia-natural-yellow-catucai" target="_blank" class="review-origin-link mt-1">🔗 The Espresso Lab 공식 원문 보기 ↗</a>
            </div>
          </div>
        </div>
      </div>
"""

if 'samambaia-natural-yellow-catucai' not in tel_html:
    cab_end = 'Caballero Bomba de Fruta #1 (Batch #6)'
    idx_cab = tel_html.find(cab_end)
    if idx_cab != -1:
        idx_card_end = tel_html.find('</div>\n      </div>\n    </div>', idx_cab)
        if idx_card_end != -1:
            tel_html = tel_html[:idx_card_end + 18] + '\n' + samambaia_card + tel_html[idx_card_end + 18:]
            print("Added Samambaia expert recommendation card!")

# 3. Add table rows for the 2 new Espresso Lab coffees
tel_rows_to_add = []
tel_start_idx = 55
for c in new_tel:
    h = c['handle']
    sc = score_coffee_item(c, 'The Espresso Lab')
    flag = '🇧🇷' if c['country'] == 'Brazil' else '🇭🇳'
    img = c.get('image_url') or 'https://via.placeholder.com/60?text=Coffee'
    p_aed = c.get('price_aed', 76.19)
    p_krw = c.get('price_krw', 28950)

    tel_row = f"""        <tr data-category="{c.get('category', 'Latin America Special Lots')}" data-country="{c['country']}" data-process="{c['process']}" data-taste="{sc['score_taste']}" data-price="{sc['score_price']}" data-rarity="{sc['score_rarity']}">
          <td class="text-muted text-xs font-mono">{tel_start_idx}</td>
          <td>
            <div class="pkg-img-wrap" onclick="openLightbox('{img}', '{c['title']}')">
              <img src="{img}" alt="{c['title']}" class="pkg-thumb" loading="lazy" onerror="this.src='https://via.placeholder.com/60?text=Coffee'">
              <span class="zoom-icon">🔍</span>
            </div>
          </td>
          <td class="td-score" data-value="{sc['score_total']}" data-total="{sc['score_total']}" data-taste="{sc['score_taste']}" data-price="{sc['score_price']}" data-rarity="{sc['score_rarity']}" style="text-align:center; vertical-align:middle;">
            <div style="font-weight:800; font-size:14px; color:#d29922;">⭐ {sc['score_total']}</div>
            <div style="font-size:10px; color:#8b949e; white-space:nowrap;">맛 {sc['score_taste']} / 값 {sc['score_price']} / 희 {sc['score_rarity']}</div>
          </td>
          <td>
            <div class="coffee-title-cell">
              <a href="{c['source_url']}" target="_blank" class="coffee-link today-new-coffee-title" title="공식 스토어로 이동">
                {flag} {c['title']} <span class="badge-new-date">1008</span> ↗
              </a>
            </div>
            <div class="text-xs text-muted font-mono">{h}</div>
          </td>
          <td class="text-sm font-medium">{c['farm']}</td>
          <td class="text-xs">{c['producer']}</td>
          <td class="text-xs font-mono">{c['country']}</td>
          <td class="text-xs">{c.get('location', '-')}</td>
          <td class="text-xs font-mono">{c.get('altitude', '-')}</td>
          <td><span class="process-tag">{c['process']}</span></td>
          <td class="text-xs">{c['variety']}</td>
          <td class="text-xs font-medium" style="color:var(--accent);">{c.get('roast', 'Filter (Light)')}</td>
          <td class="notes-cell">{c['tasting_notes']}</td>
          <td class="text-xs font-mono">{c.get('weight', '100g')}</td>
          <td class="price-cell">
            <span class="price-aed">{p_aed} AED</span>
            <span class="price-krw">약 {p_krw:,}원</span>
          </td>
          <td class="price-cell">
            <span class="price-aed">{p_aed} AED</span>
            <span class="price-krw">약 {p_krw:,}원</span>
          </td>
          <td><span class="status-badge na">미수입</span></td>
          <td>
            <div class="merit-text">{c.get('merit', '-')}</div>
          </td>
          <td>
            <div class="review-text">{c.get('community_review', '-')}</div>
          </td>
          <td class="text-center"><span class="badge-pass">PASS</span></td>
        </tr>"""
    tel_rows_to_add.append(tel_row)
    tel_start_idx += 1

if tel_rows_to_add:
    tel_html = tel_html.replace('</tbody>', '\n' + '\n'.join(tel_rows_to_add) + '\n      </tbody>', 1)
    print(f"Added {len(tel_rows_to_add)} table rows to Espresso Lab desktop dashboard!")

# Update stats banner: 54종 -> 56종
tel_html = re.sub(r'전수\s*54종', f'전수 {tel_start_idx - 1}종', tel_html)
tel_html = re.sub(r'총\s*54개', f'총 {tel_start_idx - 1}개', tel_html)

with open('theespressolab_verified.html', 'w', encoding='utf-8') as f:
    f.write(tel_html)
print("Updated theespressolab_verified.html successfully!")


# ==============================================================================
# C. UPDATE mobile.html (Archers Mobile)
# ==============================================================================
with open('mobile.html', 'r', encoding='utf-8') as f:
    arc_mb = f.read()

if '.today-new-coffee-title' not in arc_mb:
    arc_mb = arc_mb.replace('</style>', BADGE_CSS + '\n</style>', 1)

# Add new top pick card in top swiper: Finca Deborah Terroir
top_card_new = """
    <div class="top-card">
      <span class="top-card-badge" style="background:rgba(56,139,253,0.2); color:#58a6ff; border-color:#58a6ff;">🌟 NEW 릴리즈 | WBC 우승 명문 핀카 데보라</span>
      <div class="top-card-header-flex">
        <div class="top-card-pkg-wrap" onclick="openLightbox('https://cdn.shopify.com/s/files/1/0260/4302/3426/files/Terroir_1.png?v=1742549870', 'Panama - Finca Deborah, Terroir')">
          <img src="https://cdn.shopify.com/s/files/1/0260/4302/3426/files/Terroir_1.png?v=1742549870" alt="Panama - Finca Deborah, Terroir" class="top-card-pkg-img" loading="lazy" onerror="this.src='https://via.placeholder.com/72x90?text=Archers'">
          <span class="m-zoom-pill">🔍 확대</span>
        </div>
        <div class="top-card-header-body">
          <div class="top-card-title today-new-coffee-title">Panama - Finca Deborah, Terroir <span class="badge-new-date">1025</span></div>
          <div class="top-card-price">AED 165.0 (100g) <span style="font-size:12px; color:#8b949e;">약 62,700원</span></div>
        </div>
      </div>
      <div class="top-card-notes">🌸 화이트플로럴, 베르가못, 레몬, 자스민티, 백도</div>
      <div class="top-card-merit">💡 <strong>크리스탈 클린:</strong> 해발 1,900m 바루 화산의 극한 일교차와 테루아 본연의 투명함을 담아낸 정통 클래식 워시드 게이샤.</div>
    </div>
"""

if 'Panama - Finca Deborah, Terroir' not in arc_mb:
    target_pos = arc_mb.find('<div class="top-card">')
    if target_pos != -1:
        arc_mb = arc_mb[:target_pos] + top_card_new + arc_mb[target_pos:]
        print("Added Finca Deborah Terroir to mobile.html top swiper!")

# Add mobile cards for all 29 new Archers coffees
mb_cards_to_add = []
mb_idx = 118
for c in new_archers:
    h = c['handle']
    sc = score_coffee_item(c, 'Archers')
    d = dates_map.get(h, '1008')
    col = c.get('collection', 'Specialty Selection 2026')
    p_aed = c.get('price_aed', 0)
    p_krw = c.get('price_krw', 0)
    p100_aed = c.get('price_per_100g_aed', p_aed)

    card_html = f"""    <div class="coffee-card" 
         data-collection="{col}" 
         data-country="{c['country']}" 
         data-process="{c['process']}" 
         data-price="{p_aed}" 
         data-p100="{p100_aed}" 
         data-index="{mb_idx}">
      <div class="card-top">
        <div class="card-meta-tags">
          <span class="tag score-tag" style="background:rgba(210,153,34,0.18); color:#d29922; font-weight:800; border:1px solid rgba(210,153,34,0.35);">⭐ {sc['score_total']}점 (맛{sc['score_taste']}/값{sc['score_price']}/희{sc['score_rarity']})</span>
          <span class="tag col-micro">NEW 릴리즈</span>
          <span class="tag country">{c['country']}</span>
          <span class="tag" style="color:#6e7681;">#{mb_idx}</span>
        </div>
        <div class="card-price-box">
          <div class="price-aed">AED {p_aed} <span style="font-size:10px; color:#8b949e;">({c.get('weight', '100g')})</span></div>
          <div class="price-krw">약 {p_krw:,}원 (100g당 {p100_aed} AED)</div>
        </div>
      </div>

      <div class="card-title today-new-coffee-title">{c['title']} <span class="badge-new-date">{d}</span></div>
      <div class="card-notes">🌸 {c['tasting_notes']}</div>

      <div class="card-quick-specs">
        <div>품종: <span>{c['variety']}</span></div>
        <div>가공: <span>{c['process']}</span></div>
        <div>고도: <span>{c.get('altitude', '-')}</span></div>
        <div>배전: <span>{c.get('roast', '라이트-미디엄')}</span></div>
      </div>
    </div>"""
    mb_cards_to_add.append(card_html)
    mb_idx += 1

if mb_cards_to_add:
    target_bar = '<!-- FLOATING BOTTOM BAR -->'
    if target_bar in arc_mb:
        # Find closing of coffeeList right before target_bar
        idx_bar = arc_mb.find(target_bar)
        idx_close = arc_mb.rfind('</div>', 0, idx_bar)
        idx_close2 = arc_mb.rfind('</div>', 0, idx_close)
        arc_mb = arc_mb[:idx_close2] + '\n' + '\n'.join(mb_cards_to_add) + '\n    ' + arc_mb[idx_close2:]
        print(f"Added {len(mb_cards_to_add)} mobile cards to mobile.html!")

# Update counts
arc_mb = re.sub(r'전체\s*117개', f'전체 {mb_idx - 1}개', arc_mb)
arc_mb = re.sub(r'117개\s*원두', f'{mb_idx - 1}개 원두', arc_mb)

with open('mobile.html', 'w', encoding='utf-8') as f:
    f.write(arc_mb)
print("Updated mobile.html successfully!")


# ==============================================================================
# D. UPDATE theespressolab_mobile.html
# ==============================================================================
with open('theespressolab_mobile.html', 'r', encoding='utf-8') as f:
    tel_mb = f.read()

if '.today-new-coffee-title' not in tel_mb:
    tel_mb = tel_mb.replace('</style>', BADGE_CSS + '\n</style>', 1)

new_tel_mb_cards = """
        <div class="m-card" data-category="Latin America Special Lots" data-country="Honduras" data-process="Anaerobic Natural">
          <div class="m-card-top">
            <div class="m-card-img-wrap" onclick="openLightbox('https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png', 'Caballero Bomba de Fruta #1')">
              <img src="https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png" alt="Caballero Bomba de Fruta #1" class="m-card-img" loading="lazy" onerror="this.src='https://via.placeholder.com/80?text=Coffee'">
              <span class="m-zoom-pill">🔍 확대</span>
            </div>
            <div class="m-card-info">
              <div class="m-score-badge" style="display:inline-block; margin-bottom:5px; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:800; background:rgba(210,153,34,0.18); color:#d29922; border:1px solid rgba(210,153,34,0.35);">⭐ 74.5점 (맛 34.0 / 값 20.5 / 희 20.0)</div>
              <div class="m-title-row">
                <span class="m-flag">🇭🇳</span>
                <a href="https://theespressolab.com/products-details/caballero-bomba-de-fruta-1-6" target="_blank" class="m-title-link today-new-coffee-title">Caballero Bomba de Fruta #1 <span class="badge-new-date">1008</span> ↗</a>
              </div>
              <div class="m-sub-info">Honduras • Marcala, La Paz (1600m)</div>
              <div class="m-badges-row">
                <span class="m-badge variety">Catuai / Java</span>
                <span class="m-badge process">Anaerobic Natural</span>
                <span class="m-badge roast" title="푸어오버 전용 정밀 라이트 로스트">🔥 Filter (Light)</span>
              </div>
              <div class="m-price-row">
                <span class="m-price-aed">76.19 AED</span>
                <span class="m-price-krw">약 28,950원 (100g)</span>
              </div>
            </div>
          </div>
          <div class="m-card-notes">🌸 Passionfruit, Mango, Dark Cherry, Brown Sugar, Rum</div>
          <div class="m-card-merit">💡 <strong>과일 폭탄 랏:</strong> 온두라스 COE 1위 카바예로 부부의 정밀 무산소 내추럴 최신 릴리즈.</div>
        </div>

        <div class="m-card" data-category="Latin America Special Lots" data-country="Brazil" data-process="Natural">
          <div class="m-card-top">
            <div class="m-card-img-wrap" onclick="openLightbox('https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png', 'Samambaia Natural Yellow Catucai')">
              <img src="https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png" alt="Samambaia Natural Yellow Catucai" class="m-card-img" loading="lazy" onerror="this.src='https://via.placeholder.com/80?text=Coffee'">
              <span class="m-zoom-pill">🔍 확대</span>
            </div>
            <div class="m-card-info">
              <div class="m-score-badge" style="display:inline-block; margin-bottom:5px; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:800; background:rgba(210,153,34,0.18); color:#d29922; border:1px solid rgba(210,153,34,0.35);">⭐ 73.8점 (맛 33.3 / 값 20.5 / 희 20.0)</div>
              <div class="m-title-row">
                <span class="m-flag">🇧🇷</span>
                <a href="https://theespressolab.com/products-details/samambaia-natural-yellow-catucai" target="_blank" class="m-title-link today-new-coffee-title">Samambaia Natural Yellow Catucai <span class="badge-new-date">1008</span> ↗</a>
              </div>
              <div class="m-sub-info">Brazil • Sul de Minas (1200m)</div>
              <div class="m-badges-row">
                <span class="m-badge variety">Yellow Catucai</span>
                <span class="m-badge process">Natural</span>
                <span class="m-badge roast" title="드립 & 에스프레소 옴니 로스트">🔥 Omni (Light-Med)</span>
              </div>
              <div class="m-price-row">
                <span class="m-price-aed">76.19 AED</span>
                <span class="m-price-krw">약 28,950원 (100g)</span>
              </div>
            </div>
          </div>
          <div class="m-card-notes">🌸 Milk Chocolate, Hazelnut, Yellow Plum, Caramel Sweetness</div>
          <div class="m-card-merit">💡 <strong>명문 농장 밸런스:</strong> 120년 전통 Samambaia 농장의 희귀 옐로우 카투카이 내추럴.</div>
        </div>
"""

if 'caballero-bomba-de-fruta-1-6' not in tel_mb:
    pos_list = tel_mb.find('<div class="m-cards-list" id="mCardsList">')
    if pos_list != -1:
        insert_pt = pos_list + len('<div class="m-cards-list" id="mCardsList">\n')
        tel_mb = tel_mb[:insert_pt] + new_tel_mb_cards + tel_mb[insert_pt:]
        print("Added Caballero & Samambaia cards to theespressolab_mobile.html!")

with open('theespressolab_mobile.html', 'w', encoding='utf-8') as f:
    f.write(tel_mb)
print("Updated theespressolab_mobile.html successfully!")


# ==============================================================================
# E. UPDATE index.html & mobile_index.html
# ==============================================================================
with open('index.html', 'r', encoding='utf-8') as f:
    idx_html = f.read()

if '.today-new-coffee-title' not in idx_html:
    idx_html = idx_html.replace('</style>', BADGE_CSS + '\n</style>', 1)

# Update roastery highlights with today-new-coffee-title & badge-new-date
if 'Caballero Bomba de Fruta #1' not in idx_html:
    idx_html = idx_html.replace(
        '<li><span>📷</span> <strong>패키지 실물 사진 전수 탑재:</strong> 매장 진열대 실물과 즉시 비교 가능</li>',
        '<li><span>🌟</span> <strong class="today-new-coffee-title">Caballero Bomba de Fruta #1</strong> <span class="badge-new-date">1008</span>: 온두라스 챔피언 과일폭탄 무산소 랏</li>\n          <li><span>🌟</span> <strong class="today-new-coffee-title">Samambaia Yellow Catucai</strong> <span class="badge-new-date">1008</span>: 120년 명문 브라질 내추럴 랏</li>\n          <li><span>📷</span> <strong>패키지 실물 사진 전수 탑재:</strong> 매장 진열대 실물과 즉시 비교 가능</li>'
    )

if 'Finca Deborah, Terroir' not in idx_html:
    idx_html = idx_html.replace(
        '<li><span>📷</span> <strong>패키지 실물 사진 전수 탑재:</strong> 117종 전수 실물 사진 & 라이트박스 확대 지원</li>',
        '<li><span>🌟</span> <strong class="today-new-coffee-title">Panama - Finca Deborah, Terroir</strong> <span class="badge-new-date">1025</span>: WBC 챔피언 명문 크리스탈 클린컵 게이샤</li>\n          <li><span>🌟</span> <strong class="today-new-coffee-title">Brazil - Santuario Sul Sudan Rume</strong> <span class="badge-new-date">1214</span>: 희귀 야생종 수단 루메 극가성비 랏</li>\n          <li><span>📷</span> <strong>패키지 실물 사진 전수 탑재:</strong> 146종 전수 실물 사진 & 라이트박스 확대 지원</li>'
    )

# Add New Releases Showcase banner right above Top 20 section
NEW_RELEASES_SHOWCASE = """
  <!-- TODAY NEW RELEASES SHOWCASE (1008) -->
  <section class="new-releases-section" style="margin: 28px 0 36px 0; padding: 22px 24px; background: linear-gradient(135deg, rgba(19,26,38,0.95) 0%, rgba(13,18,27,0.95) 100%); border: 1px solid rgba(56,139,253,0.35); border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
      <div>
        <span style="font-size:11px; font-weight:800; background:rgba(56,139,253,0.18); color:#58a6ff; border:1px solid rgba(56,139,253,0.4); border-radius:6px; padding:2px 8px; letter-spacing:0.5px;">NEW RELEASES (10/08 업데이트)</span>
        <h3 style="font-size:18px; font-weight:800; margin:6px 0 0 0; color:var(--text-primary);">
          ✨ 오늘 추가된 신규 원두 라인업 (아처스 29종 + 에소랩 2종)
        </h3>
      </div>
      <a href="analytics.html" style="font-size:13px; font-weight:700; color:#58a6ff; text-decoration:none; display:inline-flex; align-items:center; gap:4px; padding:6px 14px; background:rgba(56,139,253,0.12); border:1px solid rgba(56,139,253,0.3); border-radius:8px;">
        전체 202종 인터랙티브 분석 표 보기 ➔
      </a>
    </div>
    <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:12px;">
      <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:11px; color:#8b949e; font-weight:700;">🏹 Archers • Competition Series</div>
          <div style="font-weight:700; font-size:13.5px; margin-top:2px;">
            <a href="https://archerscoffee.com/products/panama-terroir-finca-deborah" target="_blank" class="today-new-coffee-title" style="text-decoration:none;">Panama - Finca Deborah, Terroir <span class="badge-new-date">1025</span> ↗</a>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">White Floral, Bergamot, Meyer Lemon, Jasmine Tea</div>
        </div>
        <div style="text-align:right; white-space:nowrap; font-family:monospace; font-size:12px; color:var(--accent-gold); font-weight:700;">
          165 AED
        </div>
      </div>
      <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:11px; color:#8b949e; font-weight:700;">☕ Espresso Lab • Special Lot</div>
          <div style="font-weight:700; font-size:13.5px; margin-top:2px;">
            <a href="https://theespressolab.com/products-details/caballero-bomba-de-fruta-1-6" target="_blank" class="today-new-coffee-title" style="text-decoration:none;">Caballero Bomba de Fruta #1 <span class="badge-new-date">1008</span> ↗</a>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Passionfruit, Mango, Dark Cherry, Brown Sugar, Rum</div>
        </div>
        <div style="text-align:right; white-space:nowrap; font-family:monospace; font-size:12px; color:var(--accent-gold); font-weight:700;">
          76.19 AED
        </div>
      </div>
      <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:11px; color:#8b949e; font-weight:700;">🏹 Archers • Specialty Selection</div>
          <div style="font-weight:700; font-size:13.5px; margin-top:2px;">
            <a href="https://archerscoffee.com/products/brazil-santuario-sul-sudan-rume-washed" target="_blank" class="today-new-coffee-title" style="text-decoration:none;">Brazil - Santuario Sul Sudan Rume <span class="badge-new-date">1214</span> ↗</a>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Lemon Verbena, Lemongrass, Floral, Green Tea</div>
        </div>
        <div style="text-align:right; white-space:nowrap; font-family:monospace; font-size:12px; color:var(--accent-gold); font-weight:700;">
          22 AED/100g
        </div>
      </div>
      <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:11px; color:#8b949e; font-weight:700;">☕ Espresso Lab • Special Lot</div>
          <div style="font-weight:700; font-size:13.5px; margin-top:2px;">
            <a href="https://theespressolab.com/products-details/samambaia-natural-yellow-catucai" target="_blank" class="today-new-coffee-title" style="text-decoration:none;">Samambaia Yellow Catucai <span class="badge-new-date">1008</span> ↗</a>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Milk Chocolate, Hazelnut, Yellow Plum, Caramel</div>
        </div>
        <div style="text-align:right; white-space:nowrap; font-family:monospace; font-size:12px; color:var(--accent-gold); font-weight:700;">
          76.19 AED
        </div>
      </div>
    </div>
  </section>
"""

if '<!-- TODAY NEW RELEASES SHOWCASE (1008) -->' not in idx_html:
    target_promo = '<!-- ========================================================\n       SECTION 2: TOP 20 COMPREHENSIVE CURATION TABLE'
    if target_promo in idx_html:
        idx_html = idx_html.replace(target_promo, NEW_RELEASES_SHOWCASE + '\n  ' + target_promo)
        print("Added New Releases Showcase to index.html!")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx_html)
print("Updated index.html successfully!")


# Update mobile_index.html
with open('mobile_index.html', 'r', encoding='utf-8') as f:
    m_idx_html = f.read()

if '.today-new-coffee-title' not in m_idx_html:
    m_idx_html = m_idx_html.replace('</style>', BADGE_CSS + '\n</style>', 1)

NEW_RELEASES_MOBILE = """
  <!-- TODAY NEW RELEASES SHOWCASE (MOBILE) -->
  <div style="margin: 16px 12px; padding: 14px; background: var(--m-card-bg); border: 1px solid rgba(56,139,253,0.35); border-radius: 12px;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
      <span style="font-size:10px; font-weight:800; background:rgba(56,139,253,0.18); color:#58a6ff; border:1px solid rgba(56,139,253,0.4); border-radius:4px; padding:1px 6px;">NEW RELEASES (10/08)</span>
      <a href="analytics.html" style="font-size:11px; font-weight:700; color:#58a6ff; text-decoration:none;">전체 202종 보기 ➔</a>
    </div>
    <div style="font-size:12px; font-weight:700; margin-bottom:6px; color:var(--m-text-primary);">오늘 추가된 신규 랏 추천:</div>
    <div style="display:flex; flex-direction:column; gap:6px;">
      <div style="font-size:12px; display:flex; justify-content:space-between; align-items:center;">
        <span class="today-new-coffee-title">Panama - Finca Deborah, Terroir <span class="badge-new-date">1025</span></span>
        <span style="font-family:monospace; font-size:11px; color:var(--m-accent-gold); font-weight:700;">165 AED</span>
      </div>
      <div style="font-size:12px; display:flex; justify-content:space-between; align-items:center;">
        <span class="today-new-coffee-title">Caballero Bomba de Fruta #1 <span class="badge-new-date">1008</span></span>
        <span style="font-family:monospace; font-size:11px; color:var(--m-accent-gold); font-weight:700;">76.19 AED</span>
      </div>
      <div style="font-size:12px; display:flex; justify-content:space-between; align-items:center;">
        <span class="today-new-coffee-title">Brazil - Santuario Sul Sudan Rume <span class="badge-new-date">1214</span></span>
        <span style="font-family:monospace; font-size:11px; color:var(--m-accent-gold); font-weight:700;">22 AED/100g</span>
      </div>
      <div style="font-size:12px; display:flex; justify-content:space-between; align-items:center;">
        <span class="today-new-coffee-title">Samambaia Yellow Catucai <span class="badge-new-date">1008</span></span>
        <span style="font-family:monospace; font-size:11px; color:var(--m-accent-gold); font-weight:700;">76.19 AED</span>
      </div>
    </div>
  </div>
"""

if '<!-- TODAY NEW RELEASES SHOWCASE (MOBILE) -->' not in m_idx_html:
    target_mb = '<!-- Search & Filter Controls -->'
    if target_mb in m_idx_html:
        m_idx_html = m_idx_html.replace(target_mb, NEW_RELEASES_MOBILE + '\n' + target_mb)
        print("Added New Releases Showcase to mobile_index.html!")

with open('mobile_index.html', 'w', encoding='utf-8') as f:
    f.write(m_idx_html)
print("Updated mobile_index.html successfully!")

print("\nALL HTML FILES SUCCESSFULLY UPDATED WITH BLUE TITLE & DATE BADGE!")
