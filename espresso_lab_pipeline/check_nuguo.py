import sys
sys.path.append('.')
from verify_quotes import extract_visible_text, normalize_text

with open('espresso_lab_pipeline/products/nuguo-geisha-natural-778.html', 'r', encoding='utf-8') as f:
    html = f.read()

vis, _, _ = extract_visible_text(html)
norm = normalize_text(vis)

idx = norm.find('1110')
if idx == -1:
    idx = norm.find('1,110')
print("Found at:", idx)
if idx != -1:
    print("Snippet:", norm[idx-20:idx+40])
