#!/usr/bin/env python3
"""
verify_quotes.py - 증거 레코드의 quote와 value를 웹페이지 본문과 기계적으로 검증하는 CLI 도구.
LLM 호출 없이 순수 규칙 기반 및 텍스트 정규화로 동작합니다.
"""

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# Windows 콘솔 cp949 인코딩 문제 방지
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 기본 로깅 설정
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("verify_quotes")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 15  # 초

# Zero-width 문자 정규식
ZERO_WIDTH_PATTERN = re.compile(
    r"[\u200b\u200c\u200d\ufeff\u200e\u200f\u202a-\u202e]"
)

# 따옴표 및 대시 통일 매핑
QUOTE_TRANSLATION = str.maketrans({
    "‘": "'",
    "’": "'",
    "‚": "'",
    "‛": "'",
    "“": '"',
    "”": '"',
    "„": '"',
    "‟": '"',
    "«": '"',
    "»": '"',
    "`": "'",
})

DASH_TRANSLATION = str.maketrans({
    "–": "-",
    "—": "-",
    "−": "-",
    "‐": "-",
    "‑": "-",
    "‒": "-",
    "―": "-",
})


def normalize_text(text: str) -> str:
    """
    공통 텍스트 정규화 규칙:
    1. 유니코드 NFKC
    2. zero-width 문자 제거
    3. 따옴표류 통일 (' 및 ")
    4. 대시류 통일 (-)
    5. 연속 공백/줄바꿈을 공백 1개로 치환
    6. 영문 대소문자 무시 (소문자화)
    """
    if not text:
        return ""

    # 1. 유니코드 NFKC
    t = unicodedata.normalize("NFKC", str(text))

    # 2. zero-width 문자 제거
    t = ZERO_WIDTH_PATTERN.sub("", t)

    # 3. 따옴표 통일
    t = t.translate(QUOTE_TRANSLATION)

    # 4. 대시 종류 통일
    t = t.translate(DASH_TRANSLATION)

    # 5. 연속 공백 및 줄바꿈 -> 공백 1개
    t = re.sub(r"\s+", " ", t).strip()

    # 6. 소문자화
    t = t.lower()

    return t


def strip_number_commas(text: str) -> str:
    """
    숫자 사이의 천 단위 쉼표만 제거 (3,200 -> 3200, 1,000,000 -> 1000000).
    일반 쉼표(단어 사이 쉼표)는 보존합니다.
    """
    return re.sub(r"(?<=\d),(?=\d{3}(?:\D|$))", "", text)


def check_value_in_quote(value: Any, quote: str) -> bool:
    """
    value가 quote 안에 존재하는지 확인합니다.
    - 숫자는 천 단위 쉼표 차이만 허용 (3,200 == 3200)
    - 그 외 퍼지 매칭이나 유사도 비교는 하지 않음
    """
    if value is None or quote is None:
        return False

    norm_val = normalize_text(str(value))
    norm_quote = normalize_text(quote)

    if not norm_val:
        return True

    # 1. 단순 일치
    if norm_val in norm_quote:
        return True

    # 2. 천 단위 쉼표 차이 허용 비교
    val_stripped = strip_number_commas(norm_val)
    quote_stripped = strip_number_commas(norm_quote)

    if val_stripped in quote_stripped:
        return True

    return False


def extract_visible_text(html: str) -> Tuple[str, bool, str]:
    """
    HTML에서 보이는 텍스트를 추출하고 JS 렌더링 의심 여부를 판정합니다.
    Returns:
        (visible_text, is_needs_browser, reason)
    """
    if not html or not html.strip():
        return "", True, "페이지 본문이 완전히 비어있음"

    soup = BeautifulSoup(html, "html.parser")

    # 스크립트 태그 카운트
    script_tags = soup.find_all("script")
    script_count = len(script_tags)

    # noscript 텍스트 확인 (JS 활성화 요구 문구 등)
    noscript_texts = [ns.get_text() for ns in soup.find_all("noscript")]
    noscript_combined = " ".join(noscript_texts).lower()

    # 보이지 않는 태그 제거
    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        tag.decompose()

    # 보이는 텍스트 추출
    visible_text = soup.get_text(separator=" ")
    visible_text_clean = re.sub(r"\s+", " ", visible_text).strip()
    text_len = len(visible_text_clean)

    # JS 렌더링 의심 판정
    js_required_phrases = [
        "enable javascript",
        "javascript is required",
        "you need to enable javascript",
        "requires javascript",
        "turn on javascript",
    ]

    has_js_warning = any(p in noscript_combined for p in js_required_phrases) or any(
        p in visible_text_clean.lower() for p in js_required_phrases
    )

    if has_js_warning and text_len < 200:
        return (
            visible_text_clean,
            True,
            f"JavaScript 활성화 요구 문구 감지 및 텍스트 부족({text_len}자)으로 JS 렌더링 의심",
        )

    if text_len < 50 and script_count >= 2:
        return (
            visible_text_clean,
            True,
            f"본문 텍스트가 극히 적고({text_len}자) script 태그 다수({script_count}개)로 JS 렌더링 의심",
        )

    if text_len < 10 and script_count >= 1:
        return (
            visible_text_clean,
            True,
            f"본문 텍스트 없음({text_len}자) 및 script 태그 존재로 JS 렌더링 의심",
        )

    return visible_text_clean, False, ""


@dataclass
class FetchResult:
    status_code: Optional[int]
    html: Optional[str]
    visible_text: str
    is_needs_browser: bool
    browser_reason: str
    error: Optional[str]


class PageFetcher:
    """
    URL 캐싱 및 도메인별 Rate Limiting, 재시도를 지원하는 페이지 페처.
    """

    def __init__(self, delay_per_domain: float = 0.15, max_retries: int = 2):
        self.delay_per_domain = delay_per_domain
        self.max_retries = max_retries
        self.cache: Dict[str, FetchResult] = {}
        self.domain_last_request: Dict[str, float] = {}
        self.lock = Lock()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch(self, url: str) -> FetchResult:
        with self.lock:
            if url in self.cache:
                return self.cache[url]

        domain = urlparse(url).netloc

        last_resp = None
        for attempt in range(self.max_retries + 1):
            with self.lock:
                last_req = self.domain_last_request.get(domain, 0.0)
                elapsed = time.time() - last_req
                if elapsed < self.delay_per_domain:
                    time.sleep(self.delay_per_domain - elapsed)
                self.domain_last_request[domain] = time.time()

            try:
                resp = self.session.get(
                    url, timeout=REQUEST_TIMEOUT, allow_redirects=True
                )
                last_resp = resp

                # 일시적 429 Too Many Requests 시 잠시 대기 후 재시도 또는 curl 폴백
                if resp.status_code == 429 or resp.status_code == 403:
                    try:
                        import subprocess
                        curl_proc = subprocess.run(
                            ["curl.exe", "-s", "-L", "--max-time", "15", url],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            timeout=15,
                        )
                        if curl_proc.returncode == 0 and len(curl_proc.stdout) > 500:
                            html = curl_proc.stdout.decode("utf-8", errors="ignore")
                            visible_text, is_needs_browser, browser_reason = extract_visible_text(html)
                            result = FetchResult(
                                status_code=200,
                                html=html,
                                visible_text=visible_text,
                                is_needs_browser=is_needs_browser,
                                browser_reason=browser_reason,
                                error=None,
                            )
                            break
                    except Exception:
                        pass

                    if attempt < self.max_retries:
                        retry_after = resp.headers.get("Retry-After")
                        sleep_time = float(retry_after) if retry_after and retry_after.isdigit() else 1.5 * (attempt + 1)
                        time.sleep(sleep_time)
                        continue

                if resp.status_code >= 400:
                    result = FetchResult(
                        status_code=resp.status_code,
                        html=None,
                        visible_text="",
                        is_needs_browser=False,
                        browser_reason="",
                        error=f"HTTP {resp.status_code} {resp.reason}",
                    )
                else:
                    html = resp.text
                    visible_text, is_needs_browser, browser_reason = extract_visible_text(html)
                    result = FetchResult(
                        status_code=resp.status_code,
                        html=html,
                        visible_text=visible_text,
                        is_needs_browser=is_needs_browser,
                        browser_reason=browser_reason,
                        error=None,
                    )
                break

            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(1.0)
                    continue
                result = FetchResult(
                    status_code=None,
                    html=None,
                    visible_text="",
                    is_needs_browser=False,
                    browser_reason="",
                    error=f"요청 시간 초과 ({REQUEST_TIMEOUT}초)",
                )
                break
            except requests.exceptions.RequestException as e:
                result = FetchResult(
                    status_code=None,
                    html=None,
                    visible_text="",
                    is_needs_browser=False,
                    browser_reason="",
                    error=f"네트워크/연결 오류: {type(e).__name__} ({str(e)})",
                )
                break
            except Exception as e:
                result = FetchResult(
                    status_code=None,
                    html=None,
                    visible_text="",
                    is_needs_browser=False,
                    browser_reason="",
                    error=f"알 수 없는 오류: {str(e)}",
                )
                break

        with self.lock:
            self.cache[url] = result

        return result


def verify_record(record: Dict[str, Any], fetcher: PageFetcher) -> Dict[str, Any]:
    """
    단일 증거 레코드에 대한 검증을 수행하고 status와 reason을 추가한 레코드를 반환합니다.
    """
    out_record = dict(record)

    source_url = record.get("source_url")
    quote = record.get("quote", "")
    value = record.get("value")

    if not source_url:
        out_record["status"] = "UNREACHABLE"
        out_record["reason"] = "source_url 필드가 비어있음"
        return out_record

    # 1. URL 가져오기
    fetch_res = fetcher.fetch(source_url)

    # 1-1. 접근 실패
    if fetch_res.error:
        out_record["status"] = "UNREACHABLE"
        out_record["reason"] = fetch_res.error
        return out_record

    # 2. JS 렌더링 의심 페이지 판정
    if fetch_res.is_needs_browser:
        out_record["status"] = "NEEDS_BROWSER"
        out_record["reason"] = fetch_res.browser_reason
        return out_record

    # 3. quote 존재 여부 확인
    norm_page = normalize_text(fetch_res.visible_text)
    norm_quote = normalize_text(quote)

    if not norm_quote:
        out_record["status"] = "FAIL_QUOTE_NOT_FOUND"
        out_record["reason"] = "인용문(quote)이 비어있음"
        return out_record

    if norm_quote not in norm_page:
        out_record["status"] = "FAIL_QUOTE_NOT_FOUND"
        out_record["reason"] = "정규화된 인용문이 페이지 본문 텍스트에 존재하지 않음"
        return out_record

    # 4. value가 quote에 존재하는지 확인
    if not check_value_in_quote(value, quote):
        out_record["status"] = "FAIL_VALUE_NOT_IN_QUOTE"
        out_record["reason"] = f"값('{value}')이 인용문 안에 존재하지 않음 (천 단위 쉼표 차이 제외)"
        return out_record

    # 5. 모든 조건 충족 -> PASS
    out_record["status"] = "PASS"
    out_record["reason"] = "페이지 본문에서 인용문 및 값을 성공적으로 검증함"
    return out_record


def verify_records(
    records: List[Dict[str, Any]], max_workers: int = 5, delay: float = 0.15
) -> List[Dict[str, Any]]:
    """
    레코드 목록을 병렬로 검증하고 입력 순서를 유지하여 반환합니다.
    """
    fetcher = PageFetcher(delay_per_domain=delay)
    verified_records: List[Optional[Dict[str, Any]]] = [None] * len(records)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(verify_record, rec, fetcher): idx
            for idx, rec in enumerate(records)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                verified_records[idx] = future.result()
            except Exception as e:
                orig = dict(records[idx])
                orig["status"] = "UNREACHABLE"
                orig["reason"] = f"검증 프로세스 실행 예외: {str(e)}"
                verified_records[idx] = orig

    return [r for r in verified_records if r is not None]


def print_summary(results: List[Dict[str, Any]]) -> None:
    """
    상태별 카운트 요약을 콘솔에 출력합니다 (인코딩 안전 처리).
    """
    counts = {
        "PASS": 0,
        "FAIL_QUOTE_NOT_FOUND": 0,
        "FAIL_VALUE_NOT_IN_QUOTE": 0,
        "UNREACHABLE": 0,
        "NEEDS_BROWSER": 0,
    }

    for r in results:
        status = r.get("status", "OTHER")
        counts[status] = counts.get(status, 0) + 1

    total = len(results)
    print("\n" + "=" * 55)
    print("                 [검증 결과 요약]")
    print("=" * 55)
    print(f" 총 검증 레코드 수       : {total}건")
    print(f"  [PASS]                 : {counts.get('PASS', 0)}건")
    print(f"  [FAIL_QUOTE_NOT_FOUND] : {counts.get('FAIL_QUOTE_NOT_FOUND', 0)}건")
    print(f"  [FAIL_VALUE_NOT_IN_QUOTE]: {counts.get('FAIL_VALUE_NOT_IN_QUOTE', 0)}건")
    print(f"  [UNREACHABLE]          : {counts.get('UNREACHABLE', 0)}건")
    print(f"  [NEEDS_BROWSER]        : {counts.get('NEEDS_BROWSER', 0)}건")
    print("=" * 55 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="증거 레코드의 quote와 value를 웹페이지 본문과 기계적으로 검증합니다."
    )
    parser.add_argument("input", help="입력 JSON 파일 경로 (레코드 배열)")
    parser.add_argument(
        "-o",
        "--output",
        default="output.json",
        help="검증 결과가 저장될 출력 JSON 파일 경로 (기본값: output.json)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="병렬 작업 스레드 수 (기본값: 5, 최대 권장: 5)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.15,
        help="동일 도메인 요청 간 최소 대기 시간(초) (기본값: 0.15)",
    )

    args = parser.parse_args()

    # 입력 파일 읽기
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        logger.error(f"입력 파일을 찾을 수 없습니다: {args.input}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"입력 파일이 유효한 JSON 형식이 아닙니다: {e}")
        sys.exit(1)

    if not isinstance(records, list):
        logger.error("입력 JSON의 최상위는 레코드 배열이어야 합니다.")
        sys.exit(1)

    logger.info(f"총 {len(records)}건의 레코드 검증을 시작합니다 (workers={args.workers})...")
    start_time = time.time()

    results = verify_records(records, max_workers=args.workers, delay=args.delay)

    # 출력 파일 저장
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"검증 결과가 성공적으로 저장되었습니다: {args.output}")
    except Exception as e:
        logger.error(f"출력 파일 저장 실패: {e}")
        sys.exit(1)

    elapsed = time.time() - start_time
    logger.info(f"검증 완료 (소요 시간: {elapsed:.2f}초)")

    # 요약 출력
    print_summary(results)


if __name__ == "__main__":
    main()
