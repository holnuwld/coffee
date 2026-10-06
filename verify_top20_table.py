from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

rows = soup.select('#top20Table tbody tr')
print(f"Total rows in top20Table: {len(rows)}")

active_rows = soup.select('#top20Table tbody tr.active-pick-row')
overlap_rows = soup.select('#top20Table tbody tr.overlap-pick-row')
print(f"Active pick rows: {len(active_rows)}")
print(f"Overlap pick rows: {len(overlap_rows)}")

print("\n--- Top 10 Active Picks ---")
for i, r in enumerate(active_rows, 1):
    link = r.select_one('.c-title-link')
    roastery = r.select_one('.roastery-tag').text.strip()
    price = r.select_one('.aed-price').text.strip()
    score = r.select_one('.total-score').text.strip()
    print(f"Pick #{i:2d}: [{roastery}] {link.text.strip()} | {price} | 총점: {score} | href: {link['href']}")

print("\n--- 10 Overlap Dimmed Items ---")
for i, r in enumerate(overlap_rows, 1):
    link = r.select_one('.c-title-link')
    roastery = r.select_one('.roastery-tag').text.strip()
    reason = r.select_one('.overlap-reason').text.strip()
    print(f"Dimmed #{i:2d}: [{roastery}] {link.text.strip()} | 사유: {reason}")
