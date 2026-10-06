import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

archers = json.load(open('new_pipeline/raw_collected_coffees.json', encoding='utf-8'))
espressolab = json.load(open('espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8'))

print(f"Archers total: {len(archers)}")
archers_weights = set(str(c.get('weight', '')).lower() for c in archers)
print(f"Archers weights: {archers_weights}")

print(f"\nEspresso Lab total: {len(espressolab)}")
es_weights = set(str(c.get('weight', '')).lower() for c in espressolab)
print(f"Espresso Lab weights: {es_weights}")

# Count 100g in both
a_100g = [c for c in archers if '100' in str(c.get('weight', '')) or not c.get('weight') or '100g' in str(c.get('title', '')).lower()]
es_100g = [c for c in espressolab if '100' in str(c.get('weight', ''))]

print(f"Archers 100g candidate count: {len(a_100g)}")
print(f"Espresso Lab 100g candidate count: {len(es_100g)}")
