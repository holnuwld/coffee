import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/enriched_coffees.json', 'r', encoding='utf-8') as f:
    coffees = json.load(f)

print(f"Total coffees: {len(coffees)}")
all_keys = ['title', 'country', 'location', 'farm', 'producer', 'variety', 'process', 'altitude', 'roast', 'tasting_notes', 'weight', 'price_aed', 'price_per_100g_aed', 'image_url', 'source_url']

missing = 0
for idx, c in enumerate(coffees, 1):
    for k in all_keys:
        if not c.get(k):
            print(f"#{idx} [{c['handle']}] Missing {k}")
            missing += 1

print(f"Total missing key occurrences: {missing}")

# Check country distribution
countries = {}
for c in coffees:
    countries[c['country']] = countries.get(c['country'], 0) + 1
print("\nCountry distribution:")
for k, v in sorted(countries.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Check image URLs
img_missing = sum(1 for c in coffees if not c.get('image_url'))
print(f"\nMissing images: {img_missing}")
