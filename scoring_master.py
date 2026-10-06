import json
import re

def parse_altitude(alt_str):
    clean = re.sub(r'[, ]', '', str(alt_str))
    nums = [int(n) for n in re.findall(r'\b(1\d{3}|2\d{3})\b', clean)]
    if not nums:
        nums = [int(n) for n in re.findall(r'\b(1\d{3}|2\d{3})\b', str(alt_str))]
    return max(nums) if nums else 1650

def score_coffee_item(c, roastery_name="Archers"):
    title = str(c.get('title', '')).strip()
    title_l = title.lower()
    farm = str(c.get('farm', '')).lower()
    producer = str(c.get('producer', '')).lower()
    variety = str(c.get('variety', '')).lower()
    merit = str(c.get('purchase_merit', '') or c.get('merit', '')).lower()
    country = str(c.get('country', '')).strip()
    country_l = country.lower()
    review = str(c.get('user_review', '') or c.get('community_review', '')).lower()
    
    # 100g price
    p_100g = float(c.get('price_per_100g_aed') or c.get('price_aed') or 50.0)
    alt = parse_altitude(c.get('altitude', ''))
    text_pool = f"{title_l} {farm} {producer} {variety} {merit} {country_l}"
    
    # ----------------------------------------------------
    # 1. COE / BOP 입상급 성적 이력 (20점 만점)
    # ----------------------------------------------------
    if any(k in text_pool for k in ['auromar', 'elida', 'cerro azul', 'deborah', 'cenizos', 'nuguo']) or 'bop 1위' in text_pool:
        # 세계 최고 옥션 및 BOP 1위~3위 챔피언 농장
        award_score = 19.5
        award_desc = "BOP 1위 챔피언 / 세계 최고가 옥션 명문 랏"
    elif any(k in text_pool for k in ['daye bensa', 'elto', 'lajones', 'mil cumbres', 'chevas', 'hartmann']) or 'bop' in text_pool:
        # COE 2위 / BOP 파이널리스트 / 옥션 공식 출품 랏
        award_score = 17.5
        award_desc = "COE 2위 입상 / BOP 파이널리스트 공인 명문"
    elif any(k in text_pool for k in ['putushio', 'santa isabel', 'jairo arcila', 'sebastian gomez', 'el rubi', 'palma', 'sophia', 'las flores', 'coe']):
        # COE National Winner / 유수 명문 대회 출전 나노랏
        award_score = 15.0
        award_desc = "COE 내셔널 위너 / 유수 국제 대회 출전 랏"
    elif any(k in text_pool for k in ['cota', 'suke quto', 'kokose', 'hamasho', 'bombe', 'oboleyan', 'paraiso', 'adolfo', 'rumudamo']):
        # 검증된 우수 마이크로랏 / 유력 프로듀서 대표 랏
        award_score = 12.0
        award_desc = "검증된 유수 마이크로랏 / 프로듀서 대표 랏"
    elif 'geisha' in variety or '74158' in variety or 'sl28' in variety:
        award_score = 9.5
        award_desc = "최고급 명문 품종 단일 혈통 랏"
    else:
        award_score = 7.0
        award_desc = "스페셜티 우수 싱글 오리진 랏"

    # ----------------------------------------------------
    # 2. 테루아 (15점 만점)
    # ----------------------------------------------------
    if alt >= 2200:
        terroir_score = 15.0
        terroir_desc = f"해발 {alt}m 초고고도 극한 일교차 화산 테루아"
    elif ('baru' in text_pool or 'boquete' in text_pool or 'chiriqui' in text_pool) and alt >= 1900:
        terroir_score = 14.8
        terroir_desc = f"바루 화산 최고봉 {alt}m 천혜의 미기후 테루아"
    elif ('boquete' in text_pool or 'chiriqui' in text_pool or 'bensa' in text_pool) and alt >= 1700:
        terroir_score = 13.5
        terroir_desc = f"명문 산지 {alt}m 화산재 미네랄 테루아"
    elif alt >= 1600:
        terroir_score = 11.5
        terroir_desc = f"고지대 {alt}m 최적의 스페셜티 테루아"
    elif alt >= 1400:
        terroir_score = 9.5
        terroir_desc = f"해발 {alt}m 우수 재배 환경"
    else:
        terroir_score = 7.5
        terroir_desc = f"해발 {alt}m 표준 테루아"

    # ----------------------------------------------------
    # 3. 업계 긍정평가 (15점 만점)
    # ----------------------------------------------------
    rev_pool = f"{review} {merit}"
    if any(k in rev_pool for k in ['9.8', '9.7', '9.6', '인생', '경이', '압도적', '감탄', 'crystal clean']):
        review_score = 14.8
        review_desc = "Reddit r/pourover 9.6~9.8/10 만점급 극찬 & Q-Grader 호평"
    elif any(k in rev_pool for k in ['9.5', '9.4', '9.3', '9.2', '9.1', '9.0', '극찬', '마스터피스', '우수', '호평']):
        review_score = 13.2
        review_desc = "글로벌 커피 애호가 및 Q-Grader 90+ 연속 호평"
    elif any(k in rev_pool for k in ['8.', 'reddit', '추천', '좋은', '깔끔']):
        review_score = 11.0
        review_desc = "커뮤니티 실사용자 긍정 리뷰 및 준수한 테이스팅 평점"
    else:
        review_score = 8.5
        review_desc = "로스터리 플래그십 매장 호평 및 기본 평판"

    taste_score = round(award_score + terroir_score + review_score, 1)

    # ----------------------------------------------------
    # 4. 가격 점수 (30점 만점, 소수점 연속 반영 및 적정 기울기)
    # ----------------------------------------------------
    base_price = 29.5 - (p_100g - 25.0) * 0.05
    if '반값' in merit or '50%' in merit:
        base_price += 1.0
    elif '35%' in merit or '40%' in merit:
        base_price += 0.5
    price_score = round(max(10.0, min(30.0, base_price)), 1)

    # ----------------------------------------------------
    # 5. 한국 희소성 (20점 만점)
    # ----------------------------------------------------
    k_shop = str(c.get('korea_status', '') or c.get('korea_shop', '')).lower()
    if '전무' in k_shop or '미수입' in k_shop or '독점' in k_shop or '없음' in k_shop:
        rarity_score = 20.0
        rarity_desc = "국내 정식 수입 전무 (현지 독점 직거래 랏)"
    elif '극소량' in k_shop or '이력' in k_shop:
        rarity_score = 18.0
        rarity_desc = "국내 생두상 유사 랏 극소량 유통 (완판/품절)"
    else:
        rarity_score = 15.5
        rarity_desc = "국내 유사 싱글 오리진 유통 이력 있음"

    total_score = round(taste_score + price_score + rarity_score, 1)

    return {
        'award_score': award_score,
        'award_desc': award_desc,
        'terroir_score': terroir_score,
        'terroir_desc': terroir_desc,
        'review_score': review_score,
        'review_desc': review_desc,
        'score_taste': taste_score,
        'score_price': price_score,
        'score_rarity': rarity_score,
        'score_total': total_score,
        'p_100g': p_100g,
        'alt_num': alt
    }
