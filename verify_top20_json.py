import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('top_20_curation.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total items in top_20_curation.json: {len(data)}")
for c in data:
    status = f"★ PICK #{c['active_pick_num']}" if c['is_active'] else "🚫 DIMMED "
    rev = c.get('detailed_review', {})
    has_details = bool(rev.get('taste_analysis') and rev.get('brewing_guide'))
    print(f"[{status}] {c['rank']:2d}위 (총점 {c['score_total']:2d} = 맛{c['score_taste']:2d} + 값{c['score_price']:2d} + 희{c['score_rarity']:2d}) : [{c['roastery_badge']}] {c['title']} | has_modal_data: {has_details}")
