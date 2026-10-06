import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load image map
with open('archers_images_map.json', 'r', encoding='utf-8') as f:
    img_map = json.load(f)

# 2. Read archers html
with open('archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 3. Add CSS for package image and lightbox if not already present
pkg_css = """
  /* Package Image Styling */
  .td-pkg { width: 85px; min-width: 85px; padding: 6px 8px !important; text-align: center; }
  .pkg-img-wrap {
    width: 68px;
    height: 86px;
    margin: 0 auto;
    background: #090d13;
    border: 1px solid var(--border);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    cursor: pointer;
    overflow: hidden;
    transition: transform 0.15s ease, border-color 0.15s ease;
  }
  .pkg-img-wrap:hover {
    transform: scale(1.06);
    border-color: var(--accent);
    box-shadow: 0 4px 14px rgba(0,0,0,0.5);
  }
  .pkg-thumb {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 3px;
  }
  .zoom-icon {
    position: absolute;
    bottom: 2px;
    right: 2px;
    font-size: 10px;
    background: rgba(0,0,0,0.7);
    color: #fff;
    padding: 1px 3px;
    border-radius: 3px;
    pointer-events: none;
  }

  /* Recommendation Card Package Images */
  .rec-card-pkg-img {
    width: 90px;
    height: 110px;
    object-fit: contain;
    background: #090d13;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 4px;
    cursor: pointer;
    flex-shrink: 0;
    transition: transform 0.15s ease, border-color 0.15s ease;
  }
  .rec-card-pkg-img:hover {
    transform: scale(1.05);
    border-color: var(--accent);
  }
  .hl-item-pkg-img {
    width: 54px;
    height: 68px;
    object-fit: contain;
    background: #090d13;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 2px;
    cursor: pointer;
    flex-shrink: 0;
  }

  /* Lightbox Modal */
  .lightbox-backdrop {
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.85);
    backdrop-filter: blur(8px);
    z-index: 10000;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .lightbox-backdrop.active { display: flex; }
  .lightbox-content {
    background: #111722;
    border: 1px solid var(--border-light);
    border-radius: 16px;
    padding: 20px;
    max-width: 480px;
    width: 100%;
    text-align: center;
    position: relative;
    box-shadow: 0 20px 50px rgba(0,0,0,0.7);
  }
  .lightbox-content img {
    max-width: 100%;
    max-height: 520px;
    object-fit: contain;
    border-radius: 8px;
    background: #090d13;
  }
  .lightbox-caption {
    margin-top: 14px;
    font-size: 15px;
    font-weight: 700;
    color: #fff;
  }
  .lightbox-close {
    position: absolute;
    top: 10px; right: 12px;
    background: rgba(255,255,255,0.1);
    border: none;
    color: #fff;
    font-size: 18px;
    width: 32px; height: 32px;
    border-radius: 50%;
    cursor: pointer;
  }
"""

if '.td-pkg' not in html:
    html = html.replace('</style>', f'{pkg_css}\n</style>')

# 4. Update Table Header with "패키지 사진" and shift sortTable indices
old_thead = """        <tr>
          <th onclick="sortTable(0, 'number')">번호 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(1, 'string')">컬렉션 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(2, 'string')">커피 이름 (클릭 시 공식몰) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(3, 'string')">원산지 국가 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(4, 'string')">지역 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(5, 'string')">농장 / 스테이션 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(6, 'string')">농부 / 프로듀서 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(7, 'string')">품종 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(8, 'string')">프로세스 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(9, 'string')">고도 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(10, 'string')">배전도 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(11, 'string')">컵노트 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(12, 'string')">중량 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(13, 'number')">가격 (AED / 원화) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(14, 'number')">100g당 가격 (AED / 원화) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(15, 'string')">국내 동일 프로듀서 유사 원두 유통처 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(16, 'string')">국내 판매 가격 (유사 랏 시세) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(17, 'string')">현지 구매 메리트 분석 <span class="sort-icon">▲▼</span></th>
          <th>해외 커뮤니티 실사용자 후기 <span style="font-size:10px; color:#6e7681;">(Reddit)</span></th>
          <th>검증 상태</th>
        </tr>"""

new_thead = """        <tr>
          <th onclick="sortTable(0, 'number')">번호 <span class="sort-icon">▲▼</span></th>
          <th style="width:85px; text-align:center;">패키지 사진</th>
          <th onclick="sortTable(2, 'string')">컬렉션 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(3, 'string')">커피 이름 (클릭 시 공식몰) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(4, 'string')">원산지 국가 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(5, 'string')">지역 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(6, 'string')">농장 / 스테이션 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(7, 'string')">농부 / 프로듀서 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(8, 'string')">품종 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(9, 'string')">프로세스 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(10, 'string')">고도 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(11, 'string')">배전도 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(12, 'string')">컵노트 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(13, 'string')">중량 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(14, 'number')">가격 (AED / 원화) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(15, 'number')">100g당 가격 (AED / 원화) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(16, 'string')">국내 동일 프로듀서 유사 원두 유통처 <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(17, 'string')">국내 판매 가격 (유사 랏 시세) <span class="sort-icon">▲▼</span></th>
          <th onclick="sortTable(18, 'string')">현지 구매 메리트 분석 <span class="sort-icon">▲▼</span></th>
          <th>해외 커뮤니티 실사용자 후기 <span style="font-size:10px; color:#6e7681;">(Reddit)</span></th>
          <th>검증 상태</th>
        </tr>"""

if old_thead in html:
    html = html.replace(old_thead, new_thead)
    print("Replaced table header with Package Image column.")

# 5. Insert Package Image cell into every table row in tbody
# Pattern: <td style="color:#6e7681; font-weight:600;" data-value="(\d+)">\1</td>
def row_replace(m):
    row_html = m.group(0)
    # find handle
    h_match = re.search(r'https://archerscoffee.com/products/([a-zA-Z0-9_\-]+)', row_html)
    if not h_match:
        return row_html
    handle = h_match.group(1)
    img_url = img_map.get(handle, 'https://via.placeholder.com/68x86?text=Archers')
    title_match = re.search(r'products/[^"]+">([^<]+)</a>', row_html)
    raw_title = title_match.group(1).replace(' ↗', '').strip() if title_match else handle
    safe_title = raw_title.replace("'", "\\'")

    pkg_cell = f"""          <td class="td-pkg">
            <div class="pkg-img-wrap" onclick="openLightbox('{img_url}', '{safe_title}')">
              <img src="{img_url}" alt="{safe_title}" class="pkg-thumb" loading="lazy" onerror="this.src='https://via.placeholder.com/68x86?text=Archers'">
              <span class="zoom-icon">🔍</span>
            </div>
          </td>"""

    # Insert after first td
    first_td_pattern = r'(<td style="color:#6e7681; font-weight:600;" data-value="\d+">\d+</td>)'
    if not '<td class="td-pkg">' in row_html:
        new_row = re.sub(first_td_pattern, r'\1\n' + pkg_cell, row_html, count=1)
        return new_row
    return row_html

# Update tbody rows
tbody_pattern = re.compile(r'<tr data-collection="[^"]+">.*?</tr>', re.DOTALL)
updated_html, count = tbody_pattern.subn(row_replace, html)
print(f"Updated {count} table rows with package image cells.")
html = updated_html

# 6. Add Lightbox Modal and JS functions before </body>
lightbox_html = """
<!-- Image Lightbox Modal -->
<div class="lightbox-backdrop" id="imgLightbox" onclick="closeLightbox()">
  <div class="lightbox-content" onclick="event.stopPropagation()">
    <img src="" id="lightboxImg" alt="Package Zoom">
    <div id="lightboxCaption" class="lightbox-caption"></div>
    <button class="lightbox-close" onclick="closeLightbox()">✕</button>
  </div>
</div>

<script>
  function openLightbox(src, caption) {
    const box = document.getElementById('imgLightbox');
    const img = document.getElementById('lightboxImg');
    const cap = document.getElementById('lightboxCaption');
    if (box && img) {
      img.src = src;
      cap.textContent = caption || 'Archers Coffee Package';
      box.classList.add('active');
    }
  }

  function closeLightbox() {
    const box = document.getElementById('imgLightbox');
    if (box) box.classList.remove('active');
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeLightbox();
  });
</script>
"""

if 'id="imgLightbox"' not in html:
    html = html.replace('</body>', f'{lightbox_html}\n</body>')

with open('archers_coffee_clean_verified.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Successfully updated archers_coffee_clean_verified.html ({len(html)} bytes)")
