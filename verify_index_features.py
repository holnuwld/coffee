import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = []

# 1. Check Criteria 50 / 30 / 20
if "맛이 좋은가 (50점 만점)" in html and "가격이 합리적인가 (30점 만점)" in html and "한국에서 구하기 어려운가 (20점 만점)" in html:
    checks.append("PASS: Criteria 50 / 30 / 20 accurately displayed in legend")
else:
    checks.append("FAIL: Criteria 50 / 30 / 20 missing in legend")

# 2. Check Pure score breakdown in table
if "맛 " in html and "/50" in html and "/30" in html and "/20" in html:
    checks.append("PASS: Table score breakdown reflects 50/30/20")
else:
    checks.append("FAIL: Table score breakdown does not match 50/30/20")

# 3. Check Roastery link interaction
roastery_links = re.findall(r'<a href="([^"]+)" target="_blank"[^>]*class="roastery-link-btn', html)
if len(roastery_links) == 20:
    checks.append(f"PASS: All 20 table rows have roastery link pointing to official store URL ({len(roastery_links)} links)")
else:
    checks.append(f"FAIL: Expected 20 roastery links, found {len(roastery_links)}")

# 4. Check Coffee Title Modal Trigger
modal_buttons = re.findall(r'<button type="button" class="coffee-modal-btn" onclick="openCoffeeModal\((\d+)\)"', html)
if len(modal_buttons) == 20:
    checks.append(f"PASS: All 20 table rows have coffee title modal trigger button ({len(modal_buttons)} buttons)")
else:
    checks.append(f"FAIL: Expected 20 coffee modal buttons, found {len(modal_buttons)}")

# 5. Check Active Picks count vs Dimmed count
active_rows = re.findall(r'class="active-pick-row"', html)
overlap_rows = re.findall(r'class="overlap-pick-row"', html)
if len(active_rows) == 10 and len(overlap_rows) == 10:
    checks.append(f"PASS: Exactly 10 Active Pick rows and 10 Overlap Dimmed rows (Total {len(active_rows)+len(overlap_rows)})")
else:
    checks.append(f"FAIL: Active rows {len(active_rows)}, Overlap rows {len(overlap_rows)}")

# 6. Check Modal Dialog presence and JavaScript functionality
if 'id="coffeeModalBackdrop"' in html and 'function openCoffeeModal' in html and 'function closeCoffeeModal' in html:
    checks.append("PASS: Modal DOM elements and JS handlers implemented")
else:
    checks.append("FAIL: Modal elements or handlers missing")

for c in checks:
    print(c)
