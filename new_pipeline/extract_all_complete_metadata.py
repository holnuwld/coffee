import subprocess
import json
import re
import os
import sys
import io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COLLECTIONS = [
    {'slug': 'competition-series-2025', 'name': 'Competition Series 2025'},
    {'slug': 'microlot-reserve-2025', 'name': 'Microlot Reserve 2025'},
    {'slug': 'microlot-2026', 'name': 'Microlot Selection 2026'}
]

KOREA_SIMILAR_BEANS = {
    'auromar': {
        'status': '국내 동일 농장 수입 이력 있음 (피베리 랏은 국내 미수입)',
        'korea_roaster': '코에커피스펙트럼 / 엠아이커피 (오로마르 게이샤 워시드)',
        'korea_link': 'https://micoffee.co.kr',
        'korea_price': '약 55,000원 ~ 80,000원 (100g 기준)',
        'merit': '★ 최상: 국내 시세 대비 약 40% 저렴하며, 극소량 피베리(Peaberry) 랏은 아처스 독점 공급'
    },
    'elida': {
        'status': '국내 동일 농장 수입 이력 있음 (Plano 2801 나노랏은 국내 미수입)',
        'korea_roaster': '커피리브레 / 180커피로스터스 (엘리다 에스테이트 워시드 게이샤)',
        'korea_link': 'https://coffeelibre.kr',
        'korea_price': '약 70,000원 ~ 90,000원 (100g 기준)',
        'merit': '★ 최상: 세계 최고가 농장의 정통 워시드 게이샤를 국내 시세 대비 30~40% 저렴하게 구매 가능'
    },
    'cenizos': {
        'status': '국내 정식 유통 없음 (Archers 독점 랏)',
        'korea_roaster': '없음',
        'korea_link': '없음',
        'korea_price': '없음',
        'merit': '★ 최상: 보케테 해발 2,050m 최고봉 에스테이트로 국내에서는 구할 수 없는 독점 테루아'
    },
    'alo-village': {
        'status': '국내 동일 농부(타미루 타데세) 수입 이력 있음 (Archers SFW/DFW 랏은 독점)',
        'korea_roaster': '언스페셜티 / 국내 스페셜티 샵 (2021 COE 1위 랏 기획전)',
        'korea_link': 'https://unspecialty.com',
        'korea_price': '약 35,000원 ~ 45,000원 (100g 기준)',
        'merit': '★ 최상: 해발 2,400m 초고고도 워시드. 아처스 현지가는 100g당 약 23,000원으로 국내 반값 수준'
    },
    'hamasho': {
        'status': '국내 동일 생산지(다예 벤사 하마쇼) 수입 이력 있음 (내추럴 위주)',
        'korea_roaster': '커피리브레 / 나무사이로 (하마쇼 내추럴)',
        'korea_link': 'https://coffeelibre.kr',
        'korea_price': '약 20,000원 ~ 25,000원 (100g 기준)',
        'merit': '★ 최상: 국내 수입 랏 대비 약 50% 저렴한 AED 33(약 12,500원)으로 극강의 데일리 가성비'
    },
    'elto': {
        'status': '국내 정식 유통 없음 (Elto Coffee 직거래 독점)',
        'korea_roaster': '없음',
        'korea_link': '없음',
        'korea_price': '없음',
        'merit': '★ 최상: 2,200m 초고고도 워시드가 100g당 AED 28~33(약 10,600원~12,500원)으로 국내 미수입 & 최강 가성비'
    },
    'putushio': {
        'status': '국내 정식 유통 없음 (에콰도르 로하 희귀 메호라도)',
        'korea_roaster': '없음 (국내 에콰도르 메호라도 취급 로스터리 간헐적 출시)',
        'korea_link': 'https://momos.co.kr',
        'korea_price': '약 45,000원 ~ 60,000원 (100g 기준)',
        'merit': '★ 높음: 워시드 게이샤급 허브티 톤을 가진 희귀 품종으로 현지 가격(약 3.1만원) 메리트 우수'
    },
    'cerro-azul': {
        'status': '국내 상시 유통 (엠아이커피 생두 상시 공급)',
        'korea_roaster': '언스페셜티 / 센터커피 / 국내 다수 로스터리',
        'korea_link': 'https://micoffee.co.kr/product/detail.html?product_no=1862',
        'korea_price': '약 35,000원 ~ 45,000원 (100g 기준)',
        'merit': '△ 보통: 맛은 탁월하나 국내에서도 유사 랏을 쉽게 구할 수 있어 현지 구매 메리트는 상대적으로 낮음'
    },
    'paraiso': {
        'status': '국내 대량 상시 유통 (디에고 베르무데즈 가향/무산소 시리즈)',
        'korea_roaster': '커피리브레 / 모모스커피 / 로우키 등 국내 전역',
        'korea_link': 'https://coffeelibre.kr',
        'korea_price': '약 25,000원 ~ 32,000원 (100g 기준)',
        'merit': '△ 낮음: 국내에서 거의 동일한 원두를 항시 구매할 수 있어 두바이 현지 구매 메리트 없음'
    },
    'fazenda-um': {
        'status': '국내 동일 농장 수입 이력 있음 (모모스커피 보람 움 기획전)',
        'korea_roaster': '모모스커피 (파젠다 움 시리즈)',
        'korea_link': 'https://momos.co.kr',
        'korea_price': '약 18,000원 ~ 25,000원 (100g 기준)',
        'merit': '○ 양호: 100g당 AED 35(약 13,000원)로 국내 대비 약 30~40% 저렴'
    }
}

COMMUNITY_REVIEWS = {
    'auromar': {
        'text': "BOP 챔피언 오로마르 피베리 워시드. '자스민과 화이트 와인, 얼그레이 홍차 뉘앙스가 맑고 투명하며 산미 밸런스가 압도적'이라는 r/pourover 호평.",
        'link': "https://www.reddit.com/r/pourover/comments/1d3f9k3/panama_geisha_recommendations/"
    },
    'elida': {
        'text': "라마스투스 가문의 엘리다 에스테이트 워시드. '라벤더와 레몬그라스, 백포도의 섬세한 백차(White Tea) 같은 질감' 극찬.",
        'link': "https://www.reddit.com/r/pourover/comments/17q5f5m/has_anyone_tried_archers_coffee/"
    },
    'cenizos': {
        'text': "보케테 해발 2,050m 최고봉 게이샤. '복숭아 홍차를 마시는 듯한 티라이크 텍스처와 베르가못 여운' 호평.",
        'link': "https://www.reddit.com/r/pourover/comments/17q5f5m/has_anyone_tried_archers_coffee/"
    },
    'alo-village': {
        'text': "2021 에티오피아 COE 1위 타미루 타데세. '해발 2,400m 초고고도 특유의 얼그레이와 살구, 자스민의 정갈한 클린컵' 평가.",
        'link': "https://www.reddit.com/r/pourover/comments/1hpx3k2/top_50_coffee_roasters_of_2025/"
    },
    'hamasho': {
        'text': "다예 벤사 시다마 최고봉 랏. '블랙티와 서양배, 레몬그라스가 은은하게 감도는 워시드' 평가.",
        'link': "https://www.reddit.com/r/pourover/comments/17q5f5m/has_anyone_tried_archers_coffee/"
    },
    'elto': {
        'text': "엘토 커피 시다마 벤사 랏. '진저에일 같은 청량함과 자스민 꽃향, 복숭아 아이스티 톤' 호평.",
        'link': "https://www.reddit.com/r/pourover/comments/17q5f5m/has_anyone_tried_archers_coffee/"
    },
    'putushio': {
        'text': "에콰도르 로하 티피카 메호라도. '자스민과 스위트 라임의 청량한 허브티 톤' 호평.",
        'link': "https://www.reddit.com/r/pourover/comments/1b8m9k2/finca_soledad_pepe_arguello/"
    },
    'fazenda-um': {
        'text': "2023 WBC 챔피언 패밀리 파젠다 움. '사과, 자두의 편안한 산미와 밀크초콜릿 단맛 밸런스' 호평.",
        'link': "https://europeancoffeetrip.com/cafe/archers-coffee-sharjah/"
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

def parse_full_specs(soup, body_html, title):
    specs = {
        'producer': '미표기',
        'farm': '미표기',
        'location': '미표기',
        'variety': '미표기',
        'process': '미표기',
        'altitude': '미표기',
        'roastDot': ''
    }

    # 1. Parse from Description Accordion
    for acc in soup.find_all(class_='accordion__wrapper'):
        acc_title = acc.find(class_='accordion__title')
        if acc_title and 'description' in acc_title.get_text().lower():
            lines = [s.strip() for s in acc.stripped_strings if s.strip()]
            for i, line in enumerate(lines):
                norm = line.lower().replace(':', '').strip()
                def get_val(idx):
                    if idx >= len(lines): return ""
                    v = lines[idx].lstrip(':').strip()
                    if not v and idx + 1 < len(lines): v = lines[idx+1].lstrip(':').strip()
                    return v
                if norm in ['producer', 'farmer'] and i + 1 < len(lines):
                    v = get_val(i+1)
                    if v and v.lower() not in ['farm', 'variety', 'location', 'process', 'altitude', 'fermentation', 'sweetness', 'acidity', 'roast']:
                        specs['producer'] = v
                elif norm in ['farm', 'washing station', 'estate', 'station'] and i + 1 < len(lines):
                    v = get_val(i+1)
                    if v and v.lower() not in ['producer', 'variety', 'location', 'process', 'altitude', 'fermentation', 'sweetness', 'acidity', 'roast']:
                        specs['farm'] = v
                elif norm in ['location', 'region', 'origin'] and i + 1 < len(lines):
                    v = get_val(i+1)
                    if v and v.lower() not in ['producer', 'farm', 'variety', 'process', 'altitude', 'fermentation', 'sweetness', 'acidity', 'roast']:
                        specs['location'] = v
                elif norm in ['variety', 'varietal'] and i + 1 < len(lines):
                    v = get_val(i+1)
                    if v and v.lower() not in ['producer', 'farm', 'location', 'process', 'altitude', 'fermentation', 'sweetness', 'acidity', 'roast']:
                        specs['variety'] = v
                elif norm in ['process', 'processing'] and i + 1 < len(lines):
                    v = get_val(i+1)
                    if v and v.lower() not in ['producer', 'farm', 'location', 'variety', 'altitude', 'fermentation', 'sweetness', 'acidity', 'roast']:
                        specs['process'] = v
                elif norm in ['altitude', 'elevation'] and i + 1 < len(lines):
                    v = get_val(i+1)
                    if v and v.lower() not in ['producer', 'farm', 'location', 'variety', 'process', 'fermentation', 'sweetness', 'acidity', 'roast']:
                        specs['altitude'] = v

    # 2. Fallback to The Farm and Producer accordion or body text
    for acc in soup.find_all(class_='accordion__wrapper'):
        acc_title = acc.find(class_='accordion__title')
        if acc_title and 'farm and producer' in acc_title.get_text().lower():
            txt = acc.get_text()
            if specs['producer'] == '미표기':
                m = re.search(r'(?:led by|produced by|established by|farm of|producer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', txt)
                if m: specs['producer'] = m.group(1).strip()
            if specs['location'] == '미표기':
                m = re.search(r'(?:in|at)\s+([A-Z][a-z]+(?:,\s+[A-Z][a-z]+){1,2})', txt)
                if m: specs['location'] = m.group(1).strip()

    # 3. Fallback from body HTML regex if still missing
    body_lines = [clean_text(s) for s in BeautifulSoup(body_html, 'html.parser').stripped_strings]
    for line in body_lines:
        if specs['producer'] == '미표기' and re.search(r'^(producer|farmer)\s*[:：]', line, re.I):
            specs['producer'] = re.sub(r'^(producer|farmer)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif specs['farm'] == '미표기' and re.search(r'^(farm|washing station|station|estate)\s*[:：]', line, re.I):
            specs['farm'] = re.sub(r'^(farm|washing station|station|estate)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif specs['location'] == '미표기' and re.search(r'^(location|region|origin)\s*[:：]', line, re.I):
            specs['location'] = re.sub(r'^(location|region|origin)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif specs['variety'] == '미표기' and re.search(r'^(variety|varietal)\s*[:：]', line, re.I):
            specs['variety'] = re.sub(r'^(variety|varietal)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif specs['process'] == '미표기' and re.search(r'^(process|processing)\s*[:：]', line, re.I):
            specs['process'] = re.sub(r'^(process|processing)\s*[:：]\s*', '', line, flags=re.I).strip()
        elif specs['altitude'] == '미표기' and re.search(r'^(altitude|elevation)\s*[:：]', line, re.I):
            specs['altitude'] = re.sub(r'^(altitude|elevation)\s*[:：]\s*', '', line, flags=re.I).strip()

    # 4. Fallback inference from title
    if specs['variety'] == '미표기':
        for v_name in ['Geisha', 'Gesha', 'Bourbon', 'Caturra', 'Castillo', 'Typica', 'Sidra', 'Pacamara', 'SL28', 'SL34', '74158', '74110', '74112']:
            if v_name.lower() in title.lower():
                specs['variety'] = v_name
                break
    if specs['process'] == '미표기':
        for p_name in ['Washed', 'Natural', 'Honey', 'Anaerobic', 'Co-Ferment', 'Cold Ferment']:
            if p_name.lower() in title.lower():
                specs['process'] = p_name
                break

    # Roast dots
    dot_match = re.search(r'Roast[\s\S]*?([▪▫]{3,5})', body_html)
    if dot_match: specs['roastDot'] = dot_match.group(1)

    return specs

def main():
    print("=== [EXTRACTING COMPLETE METADATA ACROSS ALL 117 PRODUCTS] ===")
    all_coffees = []

    for col in COLLECTIONS:
        print(f"\nProcessing collection: {col['name']} ({col['slug']})...")
        json_url = f"https://archerscoffee.com/collections/{col['slug']}/products.json?limit=250"
        data = fetch_json(json_url)
        products = data.get('products', [])
        print(f" -> Found {len(products)} products in {col['name']}.")

        for idx, p in enumerate(products):
            title = p['title']
            handle = p['handle']
            product_url = f"https://archerscoffee.com/products/{handle}"
            body_html = p.get('body_html', '')

            # Fetch product page HTML for accordions & live content
            html = get_product_html(product_url)
            p_soup = BeautifulSoup(html, 'html.parser')

            # Parse full specs from accordion and body
            specs = parse_full_specs(p_soup, body_html, title)

            # Country
            country = '기타'
            countries = ['Panama', 'Ethiopia', 'Colombia', 'Costa Rica', 'Ecuador', 'Guatemala', 'Yemen', 'Kenya', 'El Salvador', 'Honduras', 'Brazil', 'Indonesia', 'India', 'Rwanda', 'Burundi', 'Peru', 'Bolivia']
            for c in countries:
                if c.lower() in title.lower() or c.lower() in specs['location'].lower():
                    country = c
                    break

            # Roast Profile
            roast_profile_str = 'Filter Roast'
            for opt in p.get('options', []):
                if 'roast' in opt.get('name', '').lower():
                    vals = opt.get('values', [])
                    if vals: roast_profile_str = vals[0]
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

            # Parse Variants, Weight & Price (default visible variant on storefront)
            variants = p.get('variants', [])
            v0 = variants[0] if variants else {}
            v0_title = v0.get('title', '')
            price_aed = float(v0.get('price', 0))

            m = re.search(r'(\d+)\s*(g|gram|kg|kilogram)', v0_title, re.I)
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

            price_krw = int(price_aed * 380)
            price_per_100g_aed = round((price_aed / g) * 100, 2)
            price_per_100g_krw = int(price_per_100g_aed * 380)

            # Tasting Notes
            tasting_notes = '미표기'
            meta_tag = p_soup.find('meta', attrs={'name': 'description'}) or p_soup.find('meta', attrs={'property': 'og:description'})
            meta_desc = clean_text(meta_tag['content']) if meta_tag and meta_tag.get('content') else ''
            span_tag = p_soup.find('span', class_='metafield-multi_line_text_field')

            if span_tag:
                tasting_notes = clean_text(span_tag.get_text())
            elif meta_desc:
                m_notes = re.search(r'(?:with (?:the )?tasting notes of|with notes of|tasting notes of|it has notes of|has notes of|showcases (?:luminous )?notes of|tasting notes:)\s*([^\n\r.]+)', meta_desc, re.I)
                if m_notes:
                    tasting_notes = m_notes.group(1).strip()
                    tasting_notes = re.split(r'(?:\.\s*This coffee|\.\s*Best enjoyed|\.\s*Works best|\.\s*Coffee sourced|\.\s*Brewed best|\.\s*A truly)', tasting_notes, flags=re.I)[0].strip()

            if tasting_notes == '미표기':
                for s in p_soup.stripped_strings:
                    if any(k in s.lower() for k in ['peach', 'jasmine', 'grape', 'bergamot', 'lychee', 'yuzu', 'floral', 'tea']):
                        if len(s) < 120 and ',' in s:
                            tasting_notes = s.strip()
                            break

            # Korea Domestic Availability & Merit Assessment
            h_lower = handle.lower()
            korea_info = {
                'status': '국내 정식 유통 없음 (Archers 독점 랏)',
                'korea_roaster': '없음',
                'korea_link': '없음',
                'korea_price': '없음',
                'merit': '★ 최상: 국내 미수입 독점 랏으로 현지 구매 메리트 매우 높음'
            }

            for k in KOREA_SIMILAR_BEANS:
                if k in h_lower:
                    korea_info = KOREA_SIMILAR_BEANS[k]
                    break

            # Community Review
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
                'weight': w_label,
                'price_aed': price_aed,
                'price_krw': price_krw,
                'price_per_100g_aed': price_per_100g_aed,
                'price_per_100g_krw': price_per_100g_krw,
                'korea_status': korea_info['status'],
                'korea_seller': korea_info['korea_roaster'],
                'korea_link': korea_info['korea_link'],
                'korea_price': korea_info['korea_price'],
                'purchase_merit': korea_info['merit'],
                'user_review': review_info['text'],
                'user_review_link': review_info['link']
            }
            all_coffees.append(coffee_record)
            print(f"[{len(all_coffees)}/117] {title[:28]} | {specs['producer'][:18]} | {specs['variety'][:12]} | {specs['altitude'][:12]} | AED {price_aed}")

    out_json = r'c:\cowork\coffee\new_pipeline\raw_collected_coffees.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(all_coffees, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_coffees)} complete coffees to {out_json}")

if __name__ == '__main__':
    main()
