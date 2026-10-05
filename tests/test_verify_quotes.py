import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Generator

import pytest

from verify_quotes import (
    PageFetcher,
    check_value_in_quote,
    extract_visible_text,
    normalize_text,
    verify_record,
    verify_records,
)

# 로컬 Mock HTTP 서버 핸들러
class MockServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 테스트 실행 중 콘솔 출력 억제

    def do_GET(self):
        if self.path == "/pass":
            content = """
            <!DOCTYPE html>
            <html>
            <head><title>Test Page</title><style>.hidden { display: none; }</style></head>
            <body>
                <h1>Archers Coffee</h1>
                <p>Panama Finca Los Cenizos Geisha Washed GW 208 by Estela Pitti.</p>
                <div class="price">Retail Price: 210 AED per 100g</div>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        elif self.path == "/whitespace":
            # 다양한 공백, zero-width, 줄바꿈, 대시, 스마트 따옴표가 포함된 페이지
            content = (
                "<html><body>\n"
                "<h1>Specialty\n\n\tCoffee  —   Filter Roast:\u200b</h1>\n"
                "<p>‘Single Origin’ from Ethiopia.</p>\n"
                "<div>Price is 125 AED.</div>\n"
                "</body></html>"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        elif self.path == "/number_comma":
            # 페이지에는 3200 (쉼표 없음), quote에는 3,200 (쉼표 있음)
            content = """
            <html><body>
                <h2>Competition Lot</h2>
                <p>Limited Reserve Coffee: 3200 AED for full box set.</p>
            </body></html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        elif self.path == "/quote_diff":
            content = """
            <html><body>
                <p>This page only talks about Colombia Castillo Natural coffee.</p>
            </body></html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        elif self.path == "/value_missing":
            content = """
            <html><body>
                <p>Panama Geisha Washed from Boquete region produced by Peterson family.</p>
            </body></html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        elif self.path == "/js_rendering":
            # 스크립트만 많고 본문 텍스트가 거의 없는 SPA 페이지
            content = """
            <!doctype html>
            <html>
            <head>
                <script src="/static/app.bundle.js"></script>
                <script src="/static/vendor.js"></script>
                <script>window.__INITIAL_STATE__ = {};</script>
            </head>
            <body>
                <div id="root"></div>
                <noscript>You need to enable JavaScript to run this app.</noscript>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        elif self.path == "/404":
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

        else:
            self.send_response(500)
            self.end_headers()


@pytest.fixture(scope="session")
def mock_server() -> Generator[str, None, None]:
    """로컬 HTTP 서버를 백그라운드 스레드로 실행하는 픽스처"""
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockServerHandler)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield base_url

    server.shutdown()
    server.server_close()


# ==========================================
# 1. 텍스트 정규화 단위 테스트
# ==========================================

def test_normalize_text():
    # 유니코드 NFKC
    assert normalize_text("Ｆｕｌｌｗｉｄｔｈ") == "fullwidth"

    # Zero-width 문자 제거
    assert normalize_text("Coffee\u200bRoast\ufeff") == "coffeeroast"

    # 따옴표 통일
    assert normalize_text("‘hello’ “world” `test`") == "'hello' \"world\" 'test'"

    # 대시 통일
    assert normalize_text("2025–2026—lot") == "2025-2026-lot"

    # 연속 공백/줄바꿈 축소 및 소문자화
    assert normalize_text("  Archers \n\t  Coffee   ") == "archers coffee"


def test_check_value_in_quote():
    # 쉼표 있는 숫자와 없는 숫자 비교
    assert check_value_in_quote("3,200", "Price: 3200 AED") is True
    assert check_value_in_quote("3200", "Price: 3,200 AED") is True
    assert check_value_in_quote("1,000,000", "Total: 1000000 KRW") is True

    # 일반 단어 쉼표는 보존되므로 정확히 일치해야 함
    assert check_value_in_quote("apple, banana", "fruits: apple, banana, cherry") is True
    assert check_value_in_quote("apple banana", "fruits: apple, banana") is False

    # value 불일치
    assert check_value_in_quote("5000", "Price: 3,200 AED") is False
    assert check_value_in_quote("Geisha Natural", "Panama Geisha Washed") is False


def test_extract_visible_text():
    html = """
    <html>
      <head><script>alert('secret');</script><style>body { color: red; }</style></head>
      <body><h1>Title</h1><p>Visible Content for testing purpose here.</p></body>
    </html>
    """
    text, needs_browser, _ = extract_visible_text(html)
    assert "alert" not in text
    assert "color: red" not in text
    assert "Title" in text
    assert "Visible Content" in text
    assert needs_browser is False


# ==========================================
# 2. 7가지 핵심 검증 케이스 엔드투엔드 테스트
# ==========================================

def test_case_pass(mock_server):
    """Case 1: PASS - URL 정상 + quote 존재 + value 존재"""
    fetcher = PageFetcher()
    rec = {
        "item": "Los Cenizos",
        "field": "price",
        "value": "210 AED",
        "source_url": f"{mock_server}/pass",
        "quote": "Retail Price: 210 AED per 100g",
        "retrieved_at": "2026-10-05T00:00:00Z",
        "condition": {"currency": "AED"},
    }
    res = verify_record(rec, fetcher)
    assert res["status"] == "PASS"
    assert "성공적으로 검증" in res["reason"]


def test_case_quote_not_found(mock_server):
    """Case 2: FAIL_QUOTE_NOT_FOUND - 페이지는 열렸으나 quote가 없음"""
    fetcher = PageFetcher()
    rec = {
        "item": "Geisha",
        "field": "variety",
        "value": "Geisha",
        "source_url": f"{mock_server}/quote_diff",
        "quote": "Panama Geisha Washed Boquete",
        "retrieved_at": "2026-10-05T00:00:00Z",
        "condition": {},
    }
    res = verify_record(rec, fetcher)
    assert res["status"] == "FAIL_QUOTE_NOT_FOUND"
    assert "존재하지 않음" in res["reason"]


def test_case_value_not_in_quote(mock_server):
    """Case 3: FAIL_VALUE_NOT_IN_QUOTE - quote는 페이지에 있으나 value가 quote에 없음"""
    fetcher = PageFetcher()
    rec = {
        "item": "Peterson Geisha",
        "field": "altitude",
        "value": "2,000m",  # quote에는 고도 정보가 없음
        "source_url": f"{mock_server}/value_missing",
        "quote": "Panama Geisha Washed from Boquete region produced by Peterson family",
        "retrieved_at": "2026-10-05T00:00:00Z",
        "condition": {},
    }
    res = verify_record(rec, fetcher)
    assert res["status"] == "FAIL_VALUE_NOT_IN_QUOTE"
    assert "인용문 안에 존재하지 않음" in res["reason"]


def test_case_whitespace_and_symbols(mock_server):
    """Case 4: PASS (공백/줄바꿈/대시/따옴표 차이 정규화 통과)"""
    fetcher = PageFetcher()
    rec = {
        "item": "Ethiopia Coffee",
        "field": "price",
        "value": "125 AED",
        "source_url": f"{mock_server}/whitespace",
        # 페이지 원문: "Specialty\n\n\tCoffee  —   Filter Roast:\u200b</h1>\n<p>‘Single Origin’ from Ethiopia.</p>"
        "quote": "Specialty Coffee - Filter Roast: 'Single Origin' from Ethiopia. Price is 125 AED.",
        "retrieved_at": "2026-10-05T00:00:00Z",
        "condition": {},
    }
    res = verify_record(rec, fetcher)
    assert res["status"] == "PASS"


def test_case_number_comma(mock_server):
    """Case 5: PASS (숫자 천 단위 쉼표 차이 허용: 3,200 == 3200)"""
    fetcher = PageFetcher()
    rec = {
        "item": "Competition Box",
        "field": "price",
        "value": "3,200",  # value에는 쉼표 있음
        "source_url": f"{mock_server}/number_comma",
        # 페이지 원문에는 "3200 AED for full box set"
        "quote": "Limited Reserve Coffee: 3200 AED for full box set",
        "retrieved_at": "2026-10-05T00:00:00Z",
        "condition": {"currency": "AED"},
    }
    res = verify_record(rec, fetcher)
    assert res["status"] == "PASS"


def test_case_unreachable_404(mock_server):
    """Case 6: UNREACHABLE (404 Not Found)"""
    fetcher = PageFetcher()
    rec = {
        "item": "Non-existent item",
        "field": "status",
        "value": "available",
        "source_url": f"{mock_server}/404",
        "quote": "Some quote",
        "retrieved_at": "2026-10-05T00:00:00Z",
        "condition": {},
    }
    res = verify_record(rec, fetcher)
    assert res["status"] == "UNREACHABLE"
    assert "404" in res["reason"]


def test_case_needs_browser(mock_server):
    """Case 7: NEEDS_BROWSER (본문 텍스트 부족 및 JS 렌더링 의심 페이지)"""
    fetcher = PageFetcher()
    rec = {
        "item": "SPA App Item",
        "field": "info",
        "value": "Dynamic Content",
        "source_url": f"{mock_server}/js_rendering",
        "quote": "Dynamic Content rendered by React",
        "retrieved_at": "2026-10-05T00:00:00Z",
        "condition": {},
    }
    res = verify_record(rec, fetcher)
    assert res["status"] == "NEEDS_BROWSER"
    assert "JS 렌더링 의심" in res["reason"]


# ==========================================
# 3. URL 캐시 동작 검증
# ==========================================

def test_url_caching(mock_server):
    fetcher = PageFetcher()
    url = f"{mock_server}/pass"

    # 첫 번째 fetch
    res1 = fetcher.fetch(url)
    assert url in fetcher.cache

    # 두 번째 fetch는 캐시 반환 확인
    res2 = fetcher.fetch(url)
    assert res1 is res2


# ==========================================
# 4. CLI 실행 전체 테스트
# ==========================================

def test_cli_execution(tmp_path: Path, mock_server: str):
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "output.json"

    records = [
        {
            "item": "Item 1",
            "field": "price",
            "value": "210 AED",
            "source_url": f"{mock_server}/pass",
            "quote": "Retail Price: 210 AED per 100g",
            "retrieved_at": "2026-10-05T00:00:00Z",
            "condition": {},
        },
        {
            "item": "Item 2",
            "field": "title",
            "value": "Castillo",
            "source_url": f"{mock_server}/quote_diff",
            "quote": "Non-existent quote text",
            "retrieved_at": "2026-10-05T00:00:00Z",
            "condition": {},
        },
    ]

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(records, f)

    # CLI 서브프로세스 실행 (명시적 utf-8 인코딩)
    cmd = [
        sys.executable,
        "verify_quotes.py",
        str(input_file),
        "-o",
        str(output_file),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    assert "검증 결과 요약" in result.stdout

    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        out_data = json.load(f)

    assert len(out_data) == 2
    assert out_data[0]["status"] == "PASS"
    assert out_data[1]["status"] == "FAIL_QUOTE_NOT_FOUND"
