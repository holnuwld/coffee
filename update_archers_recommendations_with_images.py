import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('archers_images_map.json', 'r', encoding='utf-8') as f:
    img_map = json.load(f)

with open('archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update hl-item (Top 3 boxes)
def hl_replace(m):
    item_html = m.group(0)
    h_match = re.search(r'https://archerscoffee.com/products/([a-zA-Z0-9_\-]+)', item_html)
    if not h_match:
        return item_html
    handle = h_match.group(1)
    img_url = img_map.get(handle, 'https://via.placeholder.com/54x68?text=Archers')
    title_match = re.search(r'products/[^"]+">([^<]+)</a>', item_html)
    raw_title = title_match.group(1).replace(' ↗', '').strip() if title_match else handle
    safe_title = raw_title.replace("'", "\\'")

    if 'class="hl-item-pkg-img"' in item_html:
        return item_html

    img_tag = f"""<img src="{img_url}" alt="{safe_title}" class="hl-item-pkg-img" onclick="openLightbox('{img_url}', '{safe_title}')" onerror="this.src='https://via.placeholder.com/54x68?text=Archers'">"""
    return item_html.replace('<div class="hl-item">', f'<div class="hl-item" style="display:flex; align-items:center; gap:14px;">\n          {img_tag}')

hl_pattern = re.compile(r'<div class="hl-item">.*?</div>\s*</div>\s*</div>', re.DOTALL)
html = re.sub(r'<div class="hl-item">(?:(?!<div class="hl-item">).)*?</div>\s*</div>\s*</div>', hl_replace, html, flags=re.DOTALL)

# 2. Update rec-card (Collection Top 3 cards)
def rec_replace(m):
    card_html = m.group(0)
    h_match = re.search(r'https://archerscoffee.com/products/([a-zA-Z0-9_\-]+)', card_html)
    if not h_match:
        return card_html
    handle = h_match.group(1)
    img_url = img_map.get(handle, 'https://via.placeholder.com/90x110?text=Archers')
    title_match = re.search(r'products/[^"]+">([^<]+)</a>', card_html)
    raw_title = title_match.group(1).replace(' ↗', '').strip() if title_match else handle
    safe_title = raw_title.replace("'", "\\'")

    if 'class="rec-card-pkg-img"' in card_html:
        return card_html

    img_tag = f"""<img src="{img_url}" alt="{safe_title}" class="rec-card-pkg-img" onclick="openLightbox('{img_url}', '{safe_title}')" onerror="this.src='https://via.placeholder.com/90x110?text=Archers'">"""
    
    # We want to insert img_tag into rec-card-top
    # Pattern: <div class="rec-card-top">\s*(<span class="rec-badge">.*?</span>)\s*</div>
    top_pattern = re.compile(r'<div class="rec-card-top">(.*?)</div>', re.DOTALL)
    def top_sub(tm):
        inner = tm.group(1)
        return f'<div class="rec-card-top" style="display:flex; gap:16px; align-items:flex-start;">\n            {img_tag}\n            <div style="flex:1;">{inner}</div>\n          </div>'

    new_card = top_pattern.sub(top_sub, card_html, count=1)
    return new_card

rec_pattern = re.compile(r'<div class="rec-card">(?:(?!<div class="rec-card">).)*?</div>\s*</div>', re.DOTALL)
html = rec_pattern.sub(rec_replace, html)

with open('archers_coffee_clean_verified.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated archers_coffee_clean_verified.html with recommendation card images!")
