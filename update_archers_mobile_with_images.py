import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load image map
with open('archers_images_map.json', 'r', encoding='utf-8') as f:
    img_map = json.load(f)

# 2. Read mobile.html
with open('mobile.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 3. Add CSS for mobile package images and lightbox
mobile_pkg_css = """
  /* Mobile Package Image & Card Flex */
  .m-card-header-flex {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: 8px;
  }
  .m-pkg-thumb-wrap {
    width: 62px;
    height: 78px;
    flex-shrink: 0;
    background: #0d121a;
    border: 1px solid var(--border);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    cursor: pointer;
    overflow: hidden;
  }
  .m-pkg-thumb {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 2px;
  }
  .m-zoom-pill {
    position: absolute;
    bottom: 2px;
    right: 2px;
    font-size: 8px;
    background: rgba(0, 0, 0, 0.75);
    color: #fff;
    padding: 1px 3px;
    border-radius: 3px;
    pointer-events: none;
    font-weight: 600;
  }
  .m-card-header-body {
    flex: 1;
    min-width: 0;
  }

  /* Top 6 Pick Cards Package Image */
  .top-card-header-flex {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }
  .top-card-pkg-wrap {
    width: 72px;
    height: 90px;
    flex-shrink: 0;
    background: #0d121a;
    border: 1px solid rgba(210, 153, 34, 0.4);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    cursor: pointer;
    overflow: hidden;
  }
  .top-card-pkg-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 3px;
  }
  .top-card-header-body {
    flex: 1;
    min-width: 0;
  }

  /* Mobile Lightbox Modal */
  .m-lightbox-backdrop {
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0, 0, 0, 0.88);
    backdrop-filter: blur(8px);
    z-index: 10000;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .m-lightbox-backdrop.active { display: flex; }
  .m-lightbox-box {
    background: #141922;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 16px;
    max-width: 360px;
    width: 100%;
    text-align: center;
    position: relative;
    box-shadow: 0 16px 40px rgba(0,0,0,0.7);
  }
  .m-lightbox-img {
    max-width: 100%;
    max-height: 420px;
    object-fit: contain;
    border-radius: 8px;
    background: #090d13;
  }
  .m-lightbox-title {
    margin-top: 12px;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    line-height: 1.4;
  }
  .m-lightbox-close {
    position: absolute;
    top: 10px; right: 10px;
    background: rgba(255,255,255,0.15);
    border: none;
    color: #fff;
    font-size: 18px;
    width: 30px; height: 30px;
    border-radius: 50%;
    cursor: pointer;
  }
"""

if '.m-card-header-flex' not in html:
    html = html.replace('</style>', f'{mobile_pkg_css}\n</style>')

# 4. Update the 117 cards in mobile.html
def update_card(m):
    card_text = m.group(0)
    if 'm-pkg-thumb-wrap' in card_text:
        return card_text
    
    h_match = re.search(r'https://archerscoffee.com/products/([a-zA-Z0-9_\-]+)', card_text)
    if not h_match:
        return card_text
    handle = h_match.group(1)
    img_url = img_map.get(handle, 'https://via.placeholder.com/62x78?text=Archers')
    
    title_match = re.search(r'<div class="card-title">([^<]+)</div>', card_text)
    raw_title = title_match.group(1).strip() if title_match else handle
    safe_title = raw_title.replace("'", "\\'")
    
    # We want to wrap card-top and card-title inside m-card-header-flex
    # Original:
    # <div class="card-top">
    #   ...
    # </div>
    # <div class="card-title">...</div>
    
    header_pattern = re.compile(r'(<div class="card-top">.*?</div>\s*<div class="card-title">.*?</div>)', re.DOTALL)
    
    def wrap_header(hm):
        orig_header = hm.group(1)
        return f"""<div class="m-card-header-flex">
        <div class="m-pkg-thumb-wrap" onclick="openLightbox('{img_url}', '{safe_title}')">
          <img src="{img_url}" alt="{safe_title}" class="m-pkg-thumb" loading="lazy" onerror="this.src='https://via.placeholder.com/62x78?text=Archers'">
          <span class="m-zoom-pill">🔍 확대</span>
        </div>
        <div class="m-card-header-body">
          {orig_header}
        </div>
      </div>"""
    
    new_card_text = header_pattern.sub(wrap_header, card_text, count=1)
    return new_card_text

card_pattern = re.compile(r'<div class="coffee-card".*?<!-- Expandable Detailed Section -->.*?</div>\s*</div>', re.DOTALL)
updated_html, count = card_pattern.subn(update_card, html)
print(f"Updated {count} coffee cards in mobile.html with package images.")
html = updated_html

# 5. Update Top 6 Cards in top-swipe-container
top_matches = [
    ("panama-finca-auromar-malla-geisha-washed-peaberry", "Panama Auromar Geisha Washed Peaberry"),
    ("ethiopia-hamasho-village-washed-archers-lot-2025", "Ethiopia Hamasho Village Washed Archers Lot"),
    ("panama-elida-estate-geisha-plano-2801", "Panama Elida Geisha Washed Plano 2801"),
    ("panama-finca-los-cenizos-geisha-washed-gw208", "Panama Finca Los Cenizos Geisha Washed GW-208"),
    ("finca-del-putushio-typica-mejorado-rt", "Ecuador Finca Del Putushio Typica Mejorado RT"),
    ("ethiopia-elto-coffee-sama-washed", "Ethiopia Elto Coffee Sama Washed")
]

for handle, title in top_matches:
    img_url = img_map.get(handle, '')
    if img_url:
        safe_title = title.replace("'", "\\'")
        # Find top-card containing this title
        pattern = re.compile(r'(<div class="top-card">.*?<div class="top-card-title">' + re.escape(title) + r'</div>.*?<div class="top-card-price">.*?</div>)', re.DOTALL)
        
        def replace_top(tm):
            orig = tm.group(1)
            if 'top-card-pkg-wrap' in orig:
                return orig
            # Extract badge and title/price
            badge_m = re.search(r'<span class="top-card-badge".*?</span>', orig, re.DOTALL)
            badge_html = badge_m.group(0) if badge_m else ''
            
            title_price_m = re.search(r'(<div class="top-card-title">.*?</div>\s*<div class="top-card-price">.*?</div>)', orig, re.DOTALL)
            tp_html = title_price_m.group(1) if title_price_m else ''
            
            new_hdr = f"""<div class="top-card">
      {badge_html}
      <div class="top-card-header-flex">
        <div class="top-card-pkg-wrap" onclick="openLightbox('{img_url}', '{safe_title}')">
          <img src="{img_url}" alt="{safe_title}" class="top-card-pkg-img" loading="lazy" onerror="this.src='https://via.placeholder.com/72x90?text=Archers'">
          <span class="m-zoom-pill">🔍 확대</span>
        </div>
        <div class="top-card-header-body">
          {tp_html}
        </div>
      </div>"""
            return new_hdr

        html, top_c = pattern.subn(replace_top, html, count=1)
        if top_c > 0:
            print(f"Updated top card: {title}")

# 6. Add Lightbox Modal & JS before </body>
lightbox_modal = """
<!-- Mobile Package Image Lightbox Modal -->
<div class="m-lightbox-backdrop" id="mLightbox" onclick="closeLightbox(event)">
  <div class="m-lightbox-box" onclick="event.stopPropagation()">
    <button class="m-lightbox-close" onclick="closeLightbox()">&times;</button>
    <img id="mLightboxImg" src="" alt="패키지 확대" class="m-lightbox-img">
    <div id="mLightboxTitle" class="m-lightbox-title"></div>
  </div>
</div>

<script>
  function openLightbox(src, title) {
    const box = document.getElementById('mLightbox');
    const img = document.getElementById('mLightboxImg');
    const titleEl = document.getElementById('mLightboxTitle');
    if (box && img) {
      img.src = src;
      if (titleEl) titleEl.textContent = title;
      box.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeLightbox(e) {
    if (e && e.target && e.target.id !== 'mLightbox' && !e.target.classList.contains('m-lightbox-close')) {
      return;
    }
    const box = document.getElementById('mLightbox');
    if (box) {
      box.classList.remove('active');
      document.body.style.overflow = '';
    }
  }
</script>
"""

if 'id="mLightbox"' not in html:
    html = html.replace('</body>', f'{lightbox_modal}\n</body>')

with open('mobile.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved updated mobile.html with package images and lightbox.")
