import sys
sys.path.append('.')
from verify_quotes import extract_visible_text, normalize_text

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/products/auromar-firestone-7.html', 'r', encoding='utf-8') as f:
    html = f.read()

visible_text, is_needs_browser, reason = extract_visible_text(html)
norm_text = normalize_text(visible_text)

print("Visible text length:", len(visible_text))
print("Normalized text length:", len(norm_text))

# Search for key terms
for term in ['auromar', 'firestone', '175', 'geisha', 'roberto brenes', 'jasmine', 'longan', 'yuzu']:
    norm_term = normalize_text(term)
    print(f"Term '{norm_term}': in norm_text = {norm_term in norm_text}")

# Find any tasting notes or words in norm_text
idx = norm_text.find('auromar')
while idx != -1:
    print("Auromar snippet:", norm_text[idx:idx+80])
    idx = norm_text.find('auromar', idx+1)
    if idx > 1000: break
