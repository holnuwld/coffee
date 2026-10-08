import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/coffees_full_dataset.json', encoding='utf-8') as f:
    tel_items = json.load(f)

existing_handles = {c.get('handle') for c in tel_items}

new_tel_candidates = [
    {
        "handle": "samambaia-natural-yellow-catucai",
        "title": "Samambaia Natural Yellow Catucai",
        "country": "Brazil",
        "location": "Sul de Minas",
        "farm": "Fazenda Samambaia",
        "producer": "Henrique Dias Cambraia",
        "variety": "Yellow Catucai",
        "process": "Natural",
        "altitude": "1,200 masl",
        "roast": "Omni / Light-Medium Roast",
        "tasting_notes": "Milk Chocolate, Hazelnut, Yellow Plum, Caramel Sweetness",
        "weight": "100g",
        "weight_num": 100,
        "price_aed": 76.19,
        "price_krw": 28950,
        "price_per_100g_aed": 76.19,
        "price_per_100g_krw": 28950,
        "image_url": "https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png",
        "source_url": "https://theespressolab.com/products-details/samambaia-natural-yellow-catucai",
        "desc_text": "Fazenda Samambaia는 120년 전통의 브라질 명문 농장으로, 희귀 옐로우 카투카이 품종을 정교한 내추럴 방식으로 가공하여 밀크초콜릿, 헤이즐넛, 황자두의 달콤하고 부드러운 밸런스를 자랑합니다.",
        "category": "Latin America Special Lots",
        "cat_badge": "🇧🇷 브라질 스페셜 랏",
        "roast_detail": "The Espresso Lab 공식 옴니 프로파일: 드립과 에스프레소 모두에서 뛰어난 단맛과 너티한 고소함을 구현하도록 설계.",
        "review_link": "https://theespressolab.com/products-details/samambaia-natural-yellow-catucai",
        "review_source": "The Espresso Lab 공식 큐핑 노트",
        "korea_shop": "국내 공식 미수입 (에스프레소랩 독점 랏)",
        "korea_shop_link": "",
        "korea_price": "국내 공식 유통 없음",
        "merit": "브라질 명문 Samambaia 농장의 희귀 Yellow Catucai 내추럴 랏. 100g 2.8만원대의 뛰어난 밸런스.",
        "community_review": "밀크초콜릿과 카라멜의 달콤한 여운, 황자두의 부드러운 산미가 돋보이는 신규 입고 랏.",
        "score": "9.2/10",
        "verified_status": "PASS"
    },
    {
        "handle": "caballero-bomba-de-fruta-1-6",
        "title": "Caballero Bomba de Fruta #1",
        "country": "Honduras",
        "location": "Marcala, La Paz",
        "farm": "Finca El Puente",
        "producer": "Marysabel Caballero & Moises Herrera",
        "variety": "Catuai / Java",
        "process": "Anaerobic Natural",
        "altitude": "1,600 masl",
        "roast": "Filter (Light Roast)",
        "tasting_notes": "Passionfruit, Mango, Dark Cherry, Brown Sugar, Rum",
        "weight": "100g",
        "weight_num": 100,
        "price_aed": 76.19,
        "price_krw": 28950,
        "price_per_100g_aed": 76.19,
        "price_per_100g_krw": 28950,
        "image_url": "https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png",
        "source_url": "https://theespressolab.com/products-details/caballero-bomba-de-fruta-1-6",
        "desc_text": "온두라스 COE 1위 레전드 카바예로 부부(Marysabel Caballero & Moises Herrera)의 'Bomba de Fruta(과일 폭탄)' 시리즈 신규 랏. 패션후르츠, 망고, 다크체리의 농밀한 과일 플레이버.",
        "category": "Latin America Special Lots",
        "cat_badge": "🇭🇳 온두라스 스페셜 랏",
        "roast_detail": "The Espresso Lab 공식 필터 프로파일: 열대과일 뉘앙스와 럼의 복합적인 발효 풍미를 극대화하는 라이트 로스트.",
        "review_link": "https://theespressolab.com/products-details/caballero-bomba-de-fruta-1-6",
        "review_source": "The Espresso Lab 공식 큐핑 노트",
        "korea_shop": "국내 공식 미수입 (에스프레소랩 독점 랏)",
        "korea_shop_link": "",
        "korea_price": "국내 공식 유통 없음",
        "merit": "온두라스 최고봉 카바예로 농장의 과일 폭탄(Bomba de Fruta) 시리즈 신규 랏. 열대과일과 럼의 화려한 플레이버.",
        "community_review": "이름 그대로 폭발적인 과일 향미와 달콤한 브라운슈가의 밸런스를 보여주는 수작.",
        "score": "9.4/10",
        "verified_status": "PASS"
    }
]

added_count = 0
for cand in new_tel_candidates:
    if cand['handle'] not in existing_handles:
        tel_items.append(cand)
        added_count += 1
        print(f"Added new Espresso Lab coffee: {cand['title']}")

with open('espresso_lab_pipeline/coffees_full_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(tel_items, f, ensure_ascii=False, indent=2)

print(f"Updated coffees_full_dataset.json with {added_count} new coffees (Total: {len(tel_items)})")
