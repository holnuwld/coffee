import sys
sys.path.append('.')
from verify_quotes import extract_visible_text, normalize_text

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/products/auromar-firestone-7.html', 'r', encoding='utf-8') as f:
    html = f.read()

visible_text, is_needs_browser, reason = extract_visible_text(html)
norm_text = normalize_text(visible_text)

idx = norm_text.find('longan')
print("--- CONTEXT OF LONGAN IN NORM_TEXT ---")
print(norm_text[idx-50:idx+80])
