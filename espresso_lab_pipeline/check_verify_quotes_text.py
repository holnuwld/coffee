import sys
sys.path.append('.')
from verify_quotes import extract_text_from_html, normalize_text

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/products/auromar-firestone-7.html', 'r', encoding='utf-8') as f:
    html = f.read()

page_text = extract_text_from_html(html)
norm_page = normalize_text(page_text)

print("Normalized page text length:", len(norm_page))

# Check for keywords
for term in ['jasmine', 'longan', 'yuzu', 'auromar', '175', 'geisha', 'roberto']:
    norm_term = normalize_text(term)
    print(f"Is '{norm_term}' in norm_page?", norm_term in norm_page)

# Find surrounding context of 'longan'
idx = norm_page.find('longan')
if idx != -1:
    print("\n--- CONTEXT OF LONGAN ---")
    print(norm_page[max(0, idx-60):min(len(norm_page), idx+100)])
else:
    print("Longan not found in extracted text!")
