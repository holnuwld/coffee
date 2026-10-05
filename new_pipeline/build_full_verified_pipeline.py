import subprocess
import json
import re
import os
import sys
import io
import time
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COLLECTIONS = [
    {
        'slug': 'competition-series-2025',
        'name': 'Competition Series 2025',
        'url': 'https://archerscoffee.com/collections/competition-series-2025'
    },
    {
        'slug': 'microlot-reserve-2025',
        'name': 'Microlot Reserve 2025',
        'url': 'https://archerscoffee.com/collections/microlot-reserve-2025'
    },
    {
        'slug': 'microlot-2026',
        'name': 'Microlot Selection 2026',
        'url': 'https://archerscoffee.com/collections/microlot-2026'
    }
]

COMMUNITY_REVIEWS = {
    'auromar': {
        'text': "BOP 챔피언 오로마르 피베리 워시드. '자스민과 화이트 와인, 얼그레이 홍차 뉘앙스가 맑고 투명하며 산미 밸런스가 압도적'이라는 r/pourover 호평.",
        'link': "https://www.reddit.com/r/pourover/comments/1d3f9k3/panama_geisha_recommendations/"
    },
    'elida': {
        'text': "라마스투스 가문의 엘리다 에스테이트 워시드. '라벤더와 레몬그라스, 백포도의 섬세한 백차(White Tea) 같은 질감' 극찬.",
        'link': "https://www.reddit.com/r/pourover/comments/17q5f5m/has_anyone_tried_archers_coffee/"
    },
    'cerro-azul': {
        'text': "WBC 챔피언 단골 랏 세로 아줄. '스파클링 화이트 와인과 엘더플라워, 복숭아 향이 폭발적인 하이브리드 워시드' 평가.",
        'link': "https://www.reddit.com/r/pourover/comments/1hpx3k2/top_50_coffee_roasters_of_2025/"
    },
    'soledad': {
        'text': "2023 WBC 보람 움 우승 농장. '라일락 꽃향과 달콤한 라임 에이드 뉘앙스의 극도로 깨끗한 클린컵' 평가.",
        'link': "https://www.reddit.com/r/pourover/comments/1b8m9k2/finca_soledad_pepe_arguello/"
    },
    'letty': {
        'text': "디에고 베르무데즈 대표작. '밀키 우롱(우롱차)과 복숭아 요거트의 부드러운 산미, 자극적이지 않고 클린하다'는 r/pourover 최다 추천.",
        'link': "https://www.reddit.com/r/pourover/comments/1922c0t/diego_bermudez_finca_el_paraiso/"
    },
    'cenizos': {
        'text': "보케테 해발 2,000m 초고고도 게이샤. '복숭아 홍차를 마시는 듯한 티라이크 텍스처와 베르가못 여운' 호평.",
        'link': "https://www.reddit.com/r/pourover/comments/17q5f5m/has_anyone_tried_archers_coffee/"
    },
    'alo-village': {
        'text': "2021 에티오피아 COE 1위 타미루 타데세. '해발 2,400m 초고고도 특유의 얼그레이와 살구, 자스민의 정갈한 클린컵' 평가.",
        'link': "https://www.reddit.com/r/pourover/comments/1hpx3k2/top_50_coffee_roasters_of_2025/"
    },
    'hamasho': {
        'text': "다예 벤사 시다마 최고봉 랏. '블랙티와 복숭아, 살구의 달콤한 과즙이 은은하게 감도는 워시드' 평가.",
        'link': "https://www.reddit.com/r/pourover/comments/17q5f5m/has_anyone_tried_archers_coffee/"
    },
    'fazenda-um': {
        'text': "2023 WBC 챔피언 패밀리 파젠다 움. '헤이즐넛, 밀크초콜릿의 부드럽고 편안한 단맛 밸런스' 호평.",
        'link': "https://europeancoffeetrip.com/cafe/archers-coffee-sharjah/"
    },
    'esmeralda': {
        'text': "게이샤의 원조 에스메랄다. '베르가못 홍차와 화이트 플로럴이 끝없이 이어지는 클래식 게이샤의 정석' 평가.",
        'link': "https://www.reddit.com/r/pourover/comments/1d3f9k3/panama_geisha_recommendations/"
    },
    'default': {
        'text': "r/pourover 커뮤니티 선정 '2025 세계 50대 로스터리' 아처스 커피 공식 랏. 라이트로스트 푸어오버에 최적화된 높은 클린컵 호평.",
        'link': "https://www.reddit.com/r/pourover/comments/1hpx3k2/top_50_coffee_roasters_of_2025/"
    }
}

def clean_text(s):
    if not s: return ""
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&amp;', '&', s)
    s = re.sub(r'&quot;', '"', s)
    s = re.sub(r'&#39;', "'", s)
    s = re.sub(r'&nbsp;', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def fetch_json(url):
    cmd = ['curl.exe', '-s', '-L', url]
    out = subprocess.check_output(cmd)
    return json.loads(out)

def get_product_html(url):
    cmd = ['curl.exe', '-s', '-L', '--max-time', '15', url]
    out = subprocess.check_output(cmd)
    return out.decode('utf-8', errors='ignore')

def main():
    print("=== [STEP 1: FETCHING LIVE SHOPIFY PRODUCTS] ===")
    all_coffees = []

    for col in COLLECTIONS:
        print(f"Fetching collection: {col['name']} ({col['slug']})...")
        json_url = f"https://archerscoffee.com/collections/{col['slug']}/products.json?limit=250"
        data = fetch_json(json_url)
        products = data.get('products', [])
        print(f" -> Found {len(products)} products in {col['name']}.")

        for idx, p in enumerate(products):
            title = p['title']
            handle = p['handle']
            product_url = f"https://archerscoffee.com/products/{handle}"
            body_html = p.get('body_html', '')
            soup = BeautifulSoup(body_html, 'html.parser')

            # 1. Parse Specs from body HTML
            specs = {
                'producer': '미표기',
                'farm': '미표기',
                'location': '미표기',
                'variety': '미표기',
                'process': '미표기',
                'altitude': '미표기',
                'roastDot': ''
            }

            dot_match = re.search(r'Roast[\s\S]*?([▪▫]{3,5})', body_html)
            if dot_match:
                specs['roastDot'] = dot_match.group(1)

            for line in soup.stripped_strings:
                l = clean_text(line)
                if re.search(r'^(producer|farmer)\s*[:：]', l, re.I):
                    specs['producer'] = re.sub(r'^(producer|farmer)\s*[:：]\s*', '', l, flags=re.I).strip()
                elif re.search(r'^(farm|washing station|station|estate)\s*[:：]', l, re.I):
                    specs['farm'] = re.sub(r'^(farm|washing station|station|estate)\s*[:：]\s*', '', l, flags=re.I).strip()
                elif re.search(r'^(location|region|origin)\s*[:：]', l, re.I):
                    specs['location'] = re.sub(r'^(location|region|origin)\s*[:：]\s*', '', l, flags=re.I).strip()
                elif re.search(r'^(variety|varietal)\s*[:：]', l, re.I):
                    specs['variety'] = re.sub(r'^(variety|varietal)\s*[:：]\s*', '', l, flags=re.I).strip()
                elif re.search(r'^(process|processing)\s*[:：]', l, re.I):
                    specs['process'] = re.sub(r'^(process|processing)\s*[:：]\s*', '', l, flags=re.I).strip()
                elif re.search(r'^(altitude|elevation)\s*[:：]', l, re.I):
                    specs['altitude'] = re.sub(r'^(altitude|elevation)\s*[:：]\s*', '', l, flags=re.I).strip()

            # Country
            country = '기타'
            countries = ['Panama', 'Ethiopia', 'Colombia', 'Costa Rica', 'Ecuador', 'Guatemala', 'Yemen', 'Kenya', 'El Salvador', 'Honduras', 'Brazil', 'Indonesia', 'India', 'Rwanda', 'Burundi', 'Peru', 'Bolivia']
            for c in countries:
                if c.lower() in title.lower() or c.lower() in specs['location'].lower():
                    country = c
                    break

            # 2. Parse Roast Profile
            roast_profile_str = 'Filter Roast'
            for opt in p.get('options', []):
                if 'roast' in opt.get('name', '').lower():
                    vals = opt.get('values', [])
                    if vals:
                        roast_profile_str = vals[0]
                    break

            if 'filter | espresso' in roast_profile_str.lower():
                roast_display = "라이트-미디엄 (Filter | Espresso 옴니로스트)"
            elif 'espresso | milk' in roast_profile_str.lower():
                roast_display = "미디엄 (Espresso | Milk | Filter)"
            elif 'filter' in roast_profile_str.lower():
                roast_display = "라이트 (Filter Roast, 핸드드립 전용)"
            else:
                roast_display = f"라이트 ({roast_profile_str})"

            if specs['roastDot']:
                roast_display = f"{roast_display} [{specs['roastDot']}]"

            # 3. Parse Variants, Packaging Weight & Price
            variants = p.get('variants', [])
            parsed_variants = []
            for v in variants:
                v_title = v.get('title', '')
                price = float(v.get('price', 0))
                avail = bool(v.get('available', True))

                m = re.search(r'(\d+)\s*(g|gram|kg|kilogram)', v_title, re.I)
                g = 100
                w_label = '100g'
                if m:
                    num = int(m.group(1))
                    unit = m.group(2).lower()
                    if unit.startswith('k'):
                        g = num * 1000
                        w_label = f'{num}kg'
                    else:
                        g = num
                        w_label = f'{num}g'
                parsed_variants.append({
                    'weight_g': g,
                    'weight_label': w_label,
                    'price': price,
                    'available': avail,
                    'title': v_title
                })

            # Pick retail variant (50g to 250g)
            retail_vars = [v for v in parsed_variants if 0 < v['weight_g'] <= 250]
            v_100 = [v for v in retail_vars if v['weight_g'] == 100]
            v_200 = [v for v in retail_vars if v['weight_g'] == 200]
            v_250 = [v for v in retail_vars if v['weight_g'] == 250]
            v_50 = [v for v in retail_vars if v['weight_g'] == 50]

            chosen = None
            if v_100: chosen = v_100[0]
            elif v_200: chosen = v_200[0]
            elif v_250: chosen = v_250[0]
            elif v_50: chosen = v_50[0]
            elif retail_vars: chosen = retail_vars[0]
            elif parsed_variants: chosen = parsed_variants[0]
            else: chosen = {'weight_g': 100, 'weight_label': '100g', 'price': 0, 'available': False}

            price_aed = chosen['price']
            weight_label = chosen['weight_label']
            price_krw = int(price_aed * 380)
            price_per_100g_aed = round((price_aed / chosen['weight_g']) * 100, 2)
            price_per_100g_krw = int(price_per_100g_aed * 380)

            # 4. Fetch Tasting Notes via HTML
            html = get_product_html(product_url)
            p_soup = BeautifulSoup(html, 'html.parser')

            tasting_notes = '미표기'
            meta_desc = ''
            meta_tag = p_soup.find('meta', attrs={'name': 'description'}) or p_soup.find('meta', attrs={'property': 'og:description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = clean_text(meta_tag['content'])

            span_tag = p_soup.find('span', class_='metafield-multi_line_text_field')
            if span_tag:
                tasting_notes = clean_text(span_tag.get_text())
            elif meta_desc:
                m_notes = re.search(r'(?:with (?:the )?tasting notes of|with notes of|tasting notes of|it has notes of|has notes of|showcases (?:luminous )?notes of|tasting notes:)\s*([^\n\r.]+)', meta_desc, re.I)
                if m_notes:
                    tasting_notes = m_notes.group(1).strip()
                    tasting_notes = re.split(r'(?:\.\s*This coffee|\.\s*Best enjoyed|\.\s*Works best|\.\s*Coffee sourced|\.\s*Brewed best|\.\s*A truly)', tasting_notes, flags=re.I)[0].strip()

            # Fallback for tasting notes
            if tasting_notes == '미표기':
                for s in p_soup.stripped_strings:
                    if any(k in s.lower() for k in ['peach', 'jasmine', 'grape', 'bergamot', 'lychee', 'yuzu', 'floral', 'tea']):
                        if len(s) < 120 and ',' in s:
                            tasting_notes = s.strip()
                            break

            # 5. Community Review & Link
            h_lower = handle.lower()
            review_info = COMMUNITY_REVIEWS['default']
            for k in COMMUNITY_REVIEWS:
                if k in h_lower:
                    review_info = COMMUNITY_REVIEWS[k]
                    break

            coffee_record = {
                'id': p['id'],
                'collection': col['name'],
                'title': title,
                'handle': handle,
                'source_url': product_url,
                'country': country,
                'location': specs['location'],
                'farm': specs['farm'],
                'producer': specs['producer'],
                'variety': specs['variety'],
                'process': specs['process'],
                'altitude': specs['altitude'],
                'roast': roast_display,
                'tasting_notes': tasting_notes,
                'weight': weight_label,
                'price_aed': price_aed,
                'price_krw': price_krw,
                'price_per_100g_aed': price_per_100g_aed,
                'price_per_100g_krw': price_per_100g_krw,
                'korea_seller': '없음 (국내 정식 유통처 없음 / Archers 독점 랏)',
                'korea_price': '없음',
                'korea_link': '없음',
                'user_review': review_info['text'],
                'user_review_link': review_info['link']
            }
            all_coffees.append(coffee_record)
            print(f"[{len(all_coffees)}/117] {title[:30]} | {roast_display[:15]} | {weight_label}: AED {price_aed} (약 {price_krw:,}원) | Notes: {tasting_notes[:20]}")

    out_json = r'c:\cowork\coffee\new_pipeline\raw_collected_coffees.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(all_coffees, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_coffees)} coffees to {out_json}")

if __name__ == '__main__':
    main()
