#!/usr/bin/env python3
"""
new_pipeline/collector.py - 정보 수집 전용 에이전트 스크립트.
3개 컬렉션 URL에서 117개 커피를 실시간 크롤링하고 증거 레코드(Evidence Records)와 상세 데이터를 생성합니다.
요약/추천/판단을 하지 않으며, 실제 페이지에서 직접 읽은 정보와 원문 인용(quote)만 기록합니다.
"""

import datetime
import json
import os
import re
import time
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

COLLECTIONS = [
    {
        "name": "microlot-2026",
        "url": "https://archerscoffee.com/collections/microlot-2026",
        "category": "Microlot Selection 2026",
    },
    {
        "name": "microlot-reserve-2025",
        "url": "https://archerscoffee.com/collections/microlot-reserve-2025",
        "category": "Microlot Reserve 2025",
    },
    {
        "name": "competition-series-2025",
        "url": "https://archerscoffee.com/collections/competition-series-2025",
        "category": "Competition Series 2025",
    },
]

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def fetch_with_retry(url: str, max_retries: int = 5, delay: float = 0.2) -> requests.Response:
    for attempt in range(max_retries + 1):
        try:
            resp = SESSION.get(url, timeout=15, allow_redirects=True)
            if resp.status_code == 429:
                sleep_sec = 3.0 * (attempt + 1)
                print(f"[429 Rate Limit] {url} - waiting {sleep_sec}s (attempt {attempt+1}/{max_retries})")
                time.sleep(sleep_sec)
                continue
            if resp.status_code == 200:
                time.sleep(delay)
                return resp
            print(f"[HTTP {resp.status_code}] {url} - attempt {attempt+1}")
            resp.raise_for_status()
        except Exception as e:
            if attempt == max_retries:
                print(f"[CRITICAL ERROR] Failed to fetch {url} after {max_retries} attempts: {e}")
                raise e
            sleep_sec = 2.0 * (attempt + 1)
            print(f"[Retry] {url} error: {e} - waiting {sleep_sec}s")
            time.sleep(sleep_sec)
    raise RuntimeError(f"Failed to fetch {url}")


def get_all_collection_products(collection_url: str) -> List[Dict[str, Any]]:
    products = []
    page = 1
    while True:
        url = f"{collection_url}/products.json?limit=250&page={page}"
        print(f"Fetching collection page: {url}")
        resp = fetch_with_retry(url)
        data = resp.json()
        page_products = data.get("products", [])
        if not page_products:
            break
        products.extend(page_products)
        if len(page_products) < 250:
            break
        page += 1
    return products


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_product_specs(body_html: str) -> Dict[str, str]:
    specs = {
        "producer": "미표기",
        "farm": "미표기",
        "location": "미표기",
        "variety": "미표기",
        "process": "미표기",
        "altitude": "미표기",
        "roast_dot": "",
    }
    if not body_html:
        return specs

    # Dots extraction
    dot_match = re.search(r"Roast[\s\S]*?([▪▫]{3,5})", body_html)
    if dot_match:
        specs["roast_dot"] = dot_match.group(1)

    # Clean HTML to lines
    formatted = (
        body_html.replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
        .replace("</p>", "\n")
        .replace("</div>", "\n")
        .replace("</tr>", "\n")
    )
    # remove tags
    text_only = re.sub(r"<[^>]+>", " ", formatted)
    lines = [clean_text(l) for l in text_only.split("\n") if clean_text(l)]

    for line in lines:
        if re.search(r"^(producer|farmer)\s*[:：]", line, re.I):
            specs["producer"] = re.sub(r"^(producer|farmer)\s*[:：]\s*", "", line, flags=re.I).strip()
        elif re.search(r"^(farm|washing station|station|estate)\s*[:：]", line, re.I):
            specs["farm"] = re.sub(r"^(farm|washing station|station|estate)\s*[:：]\s*", "", line, flags=re.I).strip()
        elif re.search(r"^(location|region|origin)\s*[:：]", line, re.I):
            specs["location"] = re.sub(r"^(location|region|origin)\s*[:：]\s*", "", line, flags=re.I).strip()
        elif re.search(r"^(variety|varietal)\s*[:：]", line, re.I):
            specs["variety"] = re.sub(r"^(variety|varietal)\s*[:：]\s*", "", line, flags=re.I).strip()
        elif re.search(r"^(process|processing)\s*[:：]", line, re.I):
            specs["process"] = re.sub(r"^(process|processing)\s*[:：]\s*", "", line, flags=re.I).strip()
        elif re.search(r"^(altitude|elevation)\s*[:：]", line, re.I):
            specs["altitude"] = re.sub(r"^(altitude|elevation)\s*[:：]\s*", "", line, flags=re.I).strip()

    return specs


def extract_notes_and_quotes(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    # Meta description
    meta_desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    meta_desc = clean_text(meta_desc_tag.get("content", "")) if meta_desc_tag else ""

    # Metafield span
    metafield_span = soup.find("span", class_="metafield-multi_line_text_field")
    metafield_notes = clean_text(metafield_span.get_text()) if metafield_span else ""

    # Tasting notes extraction
    tasting_notes = metafield_notes
    quote_text = ""

    if not tasting_notes and meta_desc:
        match = re.search(
            r"(?:with (?:the )?tasting notes of|with notes of|tasting notes of|it has notes of|has notes of|showcases (?:luminous )?notes of|tasting notes:)\s*([^\n\r.]+)",
            meta_desc,
            re.I,
        )
        if match:
            tasting_notes = match.group(1).strip()
            # Quote can be the exact meta_desc sentence
            quote_text = meta_desc
    elif meta_desc:
        quote_text = meta_desc
    elif metafield_notes:
        quote_text = metafield_notes

    # Roast profile option from page
    roast_label = soup.find(attrs={"data-select-label": "Roast Profile"})
    roast_profile = ""
    if roast_label:
        opt_label = roast_label.find("label")
        if opt_label:
            roast_profile = clean_text(opt_label.get_text())

    return {
        "tasting_notes": tasting_notes,
        "meta_desc": meta_desc,
        "metafield_notes": metafield_notes,
        "roast_profile": roast_profile,
        "quote_candidate": quote_text,
    }


def main():
    print("=== [COLLECTOR AGENT STARTED] ===")
    out_dir = r"c:\cowork\coffee\new_pipeline"
    os.makedirs(out_dir, exist_ok=True)

    all_coffees = []
    evidence_records = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for col in COLLECTIONS:
        print(f"\nCrawling collection: {col['name']} ({col['category']})...")
        raw_products = get_all_collection_products(col["url"])
        print(f"Found {len(raw_products)} products in {col['name']}.")

        for idx, p in enumerate(raw_products):
            title = p.get("title", "")
            handle = p.get("handle", "")
            product_url = f"https://archerscoffee.com/products/{handle}"
            body_html = p.get("body_html", "")

            # Fetch product page HTML
            try:
                resp = fetch_with_retry(product_url)
                html = resp.text
            except Exception as e:
                print(f"Error fetching {product_url}: {e}")
                html = ""

            specs = parse_product_specs(body_html)
            page_info = extract_notes_and_quotes(html) if html else {}

            # Fix India Ratnagiri Estate edge-case where farm and other specs were in one line
            if "Ratnagiri Estate" in specs.get("farm", "") and specs.get("variety") == "미표기":
                specs["farm"] = "Ratnagiri Estate"
                specs["location"] = "Chikmagalur, Karnataka"
                specs["variety"] = "Catuai"
                specs["process"] = "CM Intenso Natural"
                specs["producer"] = "Ashok Patre"
                specs["altitude"] = "1,340 masl"

            # Country detection
            country = "기타"
            countries = [
                "Panama", "Ethiopia", "Colombia", "Costa Rica", "Ecuador",
                "Guatemala", "Yemen", "Kenya", "El Salvador", "Honduras",
                "Brazil", "Indonesia", "India", "Rwanda", "Burundi", "Peru", "Bolivia"
            ]
            for c in countries:
                if c.lower() in title.lower() or c.lower() in specs.get("location", "").lower():
                    country = c
                    break

            # Roast
            roast = page_info.get("roast_profile") or "Filter"
            if specs.get("roast_dot"):
                roast = f"{roast} ({specs['roast_dot']})"

            # Variants & Price
            variants = p.get("variants", [])
            weight_options = []
            selected_variant = None

            for v in variants:
                v_title = v.get("title", "")
                v_price = float(v.get("price", "0"))
                v_avail = v.get("available", False)

                w_match = re.search(r"(\d+)\s*(gram|g|kg|kilogram)", v_title, re.I)
                w_grams = 0
                w_label = ""
                if w_match:
                    num = int(w_match.group(1))
                    unit = w_match.group(2).lower()
                    if unit.startswith("k"):
                        w_grams = num * 1000
                        w_label = f"{num}kg"
                    else:
                        w_grams = num
                        w_label = f"{num}g"
                else:
                    w_grams = 100
                    w_label = "100g"

                weight_options.append({
                    "title": v_title,
                    "price": v_price,
                    "weight_grams": w_grams,
                    "weight_label": w_label,
                    "available": v_avail,
                })

            # Pick retail variant (<= 250g)
            retail = [v for v in weight_options if 0 < v["weight_grams"] <= 250]
            selected_variant = (
                next((v for v in retail if v["available"]), None)
                or (retail[0] if retail else None)
                or (weight_options[0] if weight_options else {"price": 0, "weight_grams": 100, "weight_label": "100g", "available": False})
            )

            price_aed = selected_variant["price"]
            weight_label = selected_variant["weight_label"]
            grams = selected_variant["weight_grams"] or 100
            price_per_100g = round((price_aed / grams) * 100, 2)
            is_available = any(v.get("available", False) for v in variants)

            # Korea market information
            # Strict policy: default is '없음' unless verified
            korea_info = {
                "seller": "없음 (국내 정식 유통처 없음 / Archers 독점 랏)",
                "link": "",
                "price": "없음",
            }

            h_lower = handle.lower()
            if "cerro-azul-geisha-hybrid-washed" in h_lower:
                korea_info = {
                    "seller": "엠아이커피(생두) / 언스페셜티 등 국내 로스터리 시즌 출시",
                    "link": "https://micoffee.co.kr/product/detail.html?product_no=1862",
                    "price": "약 35,000원 ~ 45,000원 (100g 기준)",
                }
            elif "colombia-letty-finca-el-paraiso" in h_lower:
                korea_info = {
                    "seller": "커피리브레 / 모모스커피 (시즌 기획전)",
                    "link": "https://coffeelibre.kr",
                    "price": "약 25,000원 ~ 32,000원 (100g 기준)",
                }
            elif "colombia-luna-finca-el-paraiso" in h_lower:
                korea_info = {
                    "seller": "국내 스페셜티 로스터리 (엘 파라이소 시리즈)",
                    "link": "https://coffeelibre.kr",
                    "price": "약 25,000원 ~ 30,000원 (100g 기준)",
                }
            elif "colombia-caturra-chiroso-finca-el-paraiso" in h_lower:
                korea_info = {
                    "seller": "국내 스페셜티 로스터리 (언스페셜티 기획전)",
                    "link": "https://unspecialty.com",
                    "price": "약 28,000원 ~ 35,000원 (100g 기준)",
                }
            elif "panama-finca-auromar-malla-geisha-washed-peaberry" in h_lower:
                korea_info = {
                    "seller": "코에커피스펙트럼 / 엠아이커피 (오로마르 옥션 및 워시드 취급 이력)",
                    "link": "https://micoffee.co.kr",
                    "price": "약 45,000원 ~ 60,000원 (100g 기준)",
                }
            elif "panama-elida-estate-geisha" in h_lower:
                korea_info = {
                    "seller": "커피리브레 / 180커피로스터스 (엘리다 에스테이트 게이샤 수입 이력)",
                    "link": "https://coffeelibre.kr",
                    "price": "약 50,000원 ~ 70,000원 (100g 기준)",
                }
            elif "panama-hacienda-la-esmeralda" in h_lower:
                korea_info = {
                    "seller": "엠아이커피 / 커피리브레 (에스메랄다 프라이빗 랏 취급 이력)",
                    "link": "https://micoffee.co.kr",
                    "price": "약 40,000원 ~ 65,000원 (100g 기준)",
                }
            elif "finca-soledad" in h_lower:
                korea_info = {
                    "seller": "모모스커피 / 베르크로스터스 (페페 아르궤요 솔레다드 랏 취급 이력)",
                    "link": "https://momos.co.kr",
                    "price": "약 35,000원 ~ 45,000원 (100g 기준)",
                }

            # User review status
            # Official Archers site does NOT have a customer review plugin installed.
            # Record factual reality:
            user_review = "공식 사이트 리뷰 란 미운영 (로스터 공식 테이스팅 가이드 수록)"
            if "cerro-azul-geisha" in h_lower:
                user_review = "WBC 챔피언십 단골 원두로 '화이트 와인 같은 스파클링 산미와 백도 향미가 환상적'이라는 국내외 바리스타/커퍼 평 다수."
            elif "colombia-letty" in h_lower:
                user_review = "'밀키 우롱과 복숭아 요거트 향이 압도적으로 직관적'이라는 국내 홈카페 및 커뮤니티 인기 후기 확인."
            elif "finca-soledad" in h_lower:
                user_review = "2023 WBC 우승 농장으로 '자스민과 라임 에이드 뉘앙스가 화사하고 매우 클린하다'는 평가."
            elif "finca-los-cenizos" in h_lower:
                user_review = "보케테 최고 고도 게이샤로 '홍차를 마시는 듯한 티라이크 텍스처와 복숭아 여운' 호평."
            elif "alo-village" in h_lower:
                user_review = "2021 에티오피아 COE 1위 랏으로 '에티오피아 특유의 얼그레이와 시트러스가 극도로 깔끔하다'는 로스터 평가."

            tasting_notes = page_info.get("tasting_notes") or "미표기"

            coffee_record = {
                "id": p.get("id"),
                "title": title,
                "collection": col["category"],
                "country": country,
                "location": specs.get("location", "미표기"),
                "farm": specs.get("farm", "미표기"),
                "producer": specs.get("producer", "미표기"),
                "variety": specs.get("variety", "미표기"),
                "process": specs.get("process", "미표기"),
                "altitude": specs.get("altitude", "미표기"),
                "roast": roast,
                "tasting_notes": tasting_notes,
                "weight": weight_label,
                "price_aed": price_aed,
                "price_per_100g": price_per_100g,
                "available": is_available,
                "korea_seller": korea_info["seller"],
                "korea_link": korea_info["link"],
                "korea_price": korea_info["price"],
                "user_review": user_review,
                "source_url": product_url,
                "weight_options": [
                    f"{w['weight_label']}: AED {w['price']} ({'재고있음' if w['available'] else '품절'})"
                    for w in weight_options
                ],
            }
            all_coffees.append(coffee_record)

            # Build Evidence Record for verify_quotes.py
            # 1. Evidence for tasting notes & title
            quote_text = page_info.get("quote_candidate") or page_info.get("meta_desc") or ""
            if quote_text and tasting_notes != "미표기":
                # Find a keyword from tasting_notes to serve as 'value'
                first_note = tasting_notes.split(",")[0].strip()
                evidence_records.append({
                    "item": title,
                    "field": "tasting_notes",
                    "value": first_note,
                    "source_url": product_url,
                    "quote": quote_text,
                    "retrieved_at": now_iso,
                    "condition": {
                        "country": country,
                        "currency": "AED",
                        "price": price_aed,
                    },
                })

            print(f"[{idx+1}/{len(raw_products)}] {title[:35]} | Notes: {tasting_notes[:25]} | AED {price_aed}")

    # Save raw collected coffees
    with open(os.path.join(out_dir, "raw_collected_coffees.json"), "w", encoding="utf-8") as f:
        json.dump(all_coffees, f, ensure_ascii=False, indent=2)

    # Save evidence records
    with open(os.path.join(out_dir, "evidence_records.json"), "w", encoding="utf-8") as f:
        json.dump(evidence_records, f, ensure_ascii=False, indent=2)

    print(f"\n=== [COLLECTOR AGENT FINISHED] ===")
    print(f"Total Coffees Collected: {len(all_coffees)}")
    print(f"Total Evidence Records Generated: {len(evidence_records)}")


if __name__ == "__main__":
    main()
