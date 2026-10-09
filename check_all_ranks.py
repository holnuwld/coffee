import json
from scoring_master import score_coffee_item

with open('new_pipeline/raw_collected_coffees.json', encoding='utf-8') as f:
    arc = json.load(f)
with open('espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
    tel = json.load(f)

new_arc_handles = set(c['handle'] for c in arc[-29:])
new_tel_handles = set(c['handle'] for c in tel[-2:])

all_scored = []
for c in arc:
    sc = score_coffee_item(c, 'Archers')
    all_scored.append({
        'title': c['title'],
        'roastery': 'Archers',
        'score': sc['score_total'],
        'handle': c['handle'],
        'is_new': c['handle'] in new_arc_handles
    })
for c in tel:
    sc = score_coffee_item(c, 'The Espresso Lab')
    all_scored.append({
        'title': c['title'],
        'roastery': 'The Espresso Lab',
        'score': sc['score_total'],
        'handle': c['handle'],
        'is_new': c['handle'] in new_tel_handles
    })

all_scored.sort(key=lambda x: x['score'], reverse=True)
print(f"Total coffees scored: {len(all_scored)}")

print("\n--- TOP 25 AMONG ALL 202 COFFEES ---")
for i in range(25):
    item = all_scored[i]
    star = "🌟 [NEW 1008]" if item['is_new'] else "   "
    print(f"#{i+1:2d} {star} [{item['roastery']}] {item['title'][:45]} | {item['score']} pts")

print("\n--- NEW COFFEES RANKINGS ---")
for i, item in enumerate(all_scored):
    if item['is_new']:
        print(f"Overall #{i+1:3d}: [{item['roastery']}] {item['title'][:45]} | {item['score']} pts")
