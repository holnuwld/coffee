# 📋 UAE 스페셜티 커피 통합 프로젝트 핸드오버 가이드 (AI Model Handover Guide)

> **문서 목적**: 다음 AI 모델 또는 개발자가 프로젝트의 전체 맥락, 아키텍처, 데이터셋, 디자인 시스템, 검증 규칙을 즉시 이해하고 일관성 있게 작업을 이어갈 수 있도록 작성된 완전 인계 문서입니다.  
> **기준 일시**: 2026년 10월 11일 기준  
> **저장소**: `https://github.com/holnuwld/coffee.git` (기본 브랜치: `main`)

---

## ☕ 1. 프로젝트 개요 및 핵심 목표

- **프로젝트명**: UAE 2대 명문 스페셜티 커피(아처스 & 에스프레소랩) 통합 전수 검증 리포트 & 현지 구매 허브
- **대상 로스터리**:
  1. **아처스 커피 (Archers Coffee)**: 샤르자/두바이 소재. 세계 바리스타 챔피언십 랏, 직거래 마이크로랏 중심 (**총 146종 전수**)
  2. **에스프레소 커피랩 (The Espresso Lab / TEL)**: 두바이 D3 소재. 파나마 게이샤, 희귀 품종 중심 (**총 56종 전수**)
  - **합계**: **총 202종** 전수 원두 데이터베이스 및 100g 환산 가격 체계 구축
- **핵심 목표**:
  - 두바이 현지 로스터리 매장 방문 구매(면세) 시 "국내 미수입 독점 랏" 및 "국내 옥션 시세 대비 30~50% 이상 저렴한 랏" 중심의 큐레이션 제공
  - 100g 단위 통합 TOP 20 랭킹 및 엄선 10선 선발
  - 실시간 장바구니, 견적 계산, 불변 스냅샷 공유 링크, A4 인쇄/PDF 및 메신저용 발주서(PO Sheet) 시스템 제공
  - 환율 기준: **1 AED ≈ 380 KRW** (고정 환율 기준)

---

## 🗂️ 2. 핵심 파일 구성 및 아키텍처 맵

### 1) 주요 웹 페이지 (HTML)
| 파일명 | 대상 기기 | 설명 | 주요 기능 |
| :--- | :---: | :--- | :--- |
| [`index.html`](index.html) | 데스크톱 | 통합 포털 메인 허브 | 3대 대시보드 수평 카드 링크, 통합 TOP 20 테이블, 실시간 장바구니 계산기, 기기 환경 감지 자동 리다이렉트 |
| [`mobile_index.html`](mobile_index.html) | 모바일 | 모바일 메인 포털 | 터치 최적화 카드 뷰, 아코디언 상세 스펙, 다크모드 지원 |
| [`archers_coffee_clean_verified.html`](archers_coffee_clean_verified.html) | 데스크톱 | 아처스 146종 대시보드 | 요약보기/전체보기 토글, 146종 실물 패키지 라이트박스, 18개 컬럼 양방향 정렬, Best 3 추천 |
| [`archers_mobile.html`](archers_mobile.html) | 모바일 | 아처스 모바일 뷰 | 터치 카드 뷰, 원터치 필터 칩, 라이트박스 모달 |
| [`theespressolab_verified.html`](theespressolab_verified.html) | 데스크톱 | 에소랩 56종 대시보드 | 아처스와 100% 동일한 에디토리얼 레이아웃, 요약보기/전체보기 토글, Best 3 추천 |
| [`theespressolab_mobile.html`](theespressolab_mobile.html) | 모바일 | 에소랩 모바일 뷰 | 터치 카드 뷰, 실물 패키지 라이트박스 |
| [`analytics.html`](analytics.html) | 데스크톱 | 통합 애널리틱스 대시보드 | 202종 다각도 통계 차트, 가공 프로세스 다중 선택(Multi-select), 컵노트 프리셋 필터, 로스터리 2줄 표기 & 공식몰 링크 |
| [`cart.html`](cart.html) | 데스크톱 | 현지 구매 발주서 (PO Sheet) | 실시간 견적, A4 인쇄/PDF 저장, 메신저 텍스트 복사, 불변 동결 스냅샷 링크(`?snapshot=...`) |
| [`mobile_cart.html`](mobile_cart.html) | 모바일 | 모바일 현지 구매 발주서 | 현지 매장 방문 시 빠른 주문 확인용 모바일 최적화 발주서 |

### 2) 데이터 및 설정 파일
- `espresso_lab_pipeline/coffees_full_dataset.json`: 에스프레소랩 56종 정규 데이터셋
- `standardized_comp2025.json`, `standardized_microReserve2025.json`, `standardized_micro2026.json`: 아처스 컬렉션별 정규 데이터셋
- `top_20_curation.json`: 2대 로스터리 통합 100g TOP 20 및 엄선 10선 큐레이션 데이터
- `scratch/live_archers_products.json`: 아처스 공식 몰 실시간 크롤링 원본 (365개 품목)
- `scratch/live_espressolab_products.json`: 에소랩 공식 몰 실시간 크롤링 원본 (74개 품목)

### 3) 검증 스크립트 (Verification Suites)
- `scratch/verify_latest_requests.py`: 최신 요구사항 기계적 검증기 (29/29 항목)
- `scratch/verify_font_sync.py`: 폰트 및 타이포그래피 일치성 검증기 (19/19 항목)
- `verify_quotes.py`: 원두 스펙 팩트 인용문 전수 검증기 (513건 100% PASS)
- `verify_system.py`: 유사도 알고리즘 및 큐레이션 무결성 검증기

---

## 🎨 3. 디자인 시스템 및 타이포그래피 표준 (Design System)

모든 페이지는 **에디토리얼 웜 미니멀리즘(Editorial Warm Minimalist)** 원칙에 따라 정밀하게 일치되어 있습니다.

### 1) 컬러 팔레트 (CSS Custom Properties)
```css
/* 라이트 모드 (기본) */
:root, [data-theme="light"] {
  --color-bg: #F7F5F0;             /* 따뜻한 아이보리 배경 */
  --color-surface: #FFFFFF;        /* 카드 및 테이블 배경 */
  --color-surface-muted: #EFEEE8;  /* 연한 그레이/베이지 서피스 */
  --color-surface-hover: #F2F0EA;  /* 호버 배경 */
  --color-text-primary: #252923;   /* 다크 에스프레소 텍스트 */
  --color-text-secondary: #73766E; /* 서브 텍스트 */
  --color-text-muted: #92948C;     /* 비활성/캡션 텍스트 */
  --color-border: #E3E1D9;         /* 기본 테두리 */
  --color-border-strong: #CCC9BF;  /* 강조 테두리 */
  --color-accent: #79583E;         /* 시그니처 커피 브라운 액센트 */
  --color-accent-hover: #5F422E;
  --color-accent-subtle: #F0E7DE;  /* 액센트 틴트 배경 */
  --color-success: #47765A;        /* 검증 완료/선발 그린 */
  --color-info: #496C91;           /* 링크/인포 블루 */
}

/* 다크 모드 */
[data-theme="dark"] {
  --color-bg: #171613;             /* 딥 웜 차콜 배경 */
  --color-surface: #201E1A;        /* 다크 카드 배경 */
  --color-surface-muted: #29261F;  
  --color-surface-hover: #322E26;
  --color-text-primary: #EAE5DC;   /* 웜 크림 텍스트 */
  --color-text-secondary: #B6AEA1;
  --color-text-muted: #898174;
  --color-border: #39352D;
  --color-accent: #C49A70;         /* 웜 앰버/골드 액센트 */
  --color-accent-subtle: #382D23;
}
```

### 2) 웹폰트 로딩 규칙 (Web Fonts Standard)
모든 HTML 파일의 `<head>`는 반드시 아래 3개 링크를 정확히 포함해야 합니다.
```html
<!-- 1. 본문용 공식 Pretendard CDN (OS/기기 불문 완전 동일 렌더링) -->
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />

<!-- 2. Google Fonts 프리커넥트 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- 3. 헤드라인 세리프(Playfair Display) + 코드/숫자(JetBrains Mono) -->
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### 3) 폰트 변수 및 주의사항 (CRITICAL)
```css
--font-sans: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Noto Sans KR', sans-serif;
--font-serif: 'Playfair Display', Georgia, serif;
--font-mono: 'JetBrains Mono', monospace;
```
⚠️ **주의**: 과거 에소랩 다크모드에 윈도우 시스템 폰트인 `'Segoe UI'`가 포함되어 윈도우에서 폰트가 틀어지는 버그가 있었습니다. **`--font-sans`에 절대로 `'Segoe UI'`를 추가하지 마십시오.**

### 4) 주요 컴포넌트 타이포그래피 규격
- **`h1` 제목**: `font-family: var(--font-serif); font-size: 32px; font-weight: 700;`
- **상단 메뉴 링크 (`.nav-text-link`)**: `font-size: 13px !important; font-weight: 500 !important;` (활성 상태: `font-weight: 700 !important;`)
- **기본 배지 (`.badge`)**: `font-size: 11.5px; font-weight: 500;`
- **신규 날짜 배지 (`.badge-new-date`)**: `font-size: 10px; font-weight: 700;`
- **하이라이트 랭킹 (`.hl-item-rank`)**: `font-size: 11px; font-weight: 700;`
- **모달 담기 버튼 (`.roastery-modal-star-btn`)**: `font-size: 13px; font-weight: 600;`
- **카트 토스트 (`.roastery-cart-toast`)**: `font-size: 13.5px; font-weight: 600;`
- **테이블 본문 텍스트**: `font-size: 11.5px !important;`

---

## ⚙️ 4. 주요 기능별 구현 메커니즘 (Key Mechanisms)

### 1) 테이블 요약보기 / 전체보기 모드 (Table View Mode Toggle)
- **위치**: `archers_coffee_clean_verified.html`, `theespressolab_verified.html` 테이블 우상단 버튼 (`#viewToggleSummary`, `#viewToggleFull`)
- **동작 원리**:
  - `setTableViewMode('summary')`: 테이블 및 컨테이너에 `.view-summary` 클래스 추가
  - CSS `.table-container.view-summary .col-hide-summary { display: none !important; }`를 통해 아래 9개 열 숨김:
    - `지역`, `농장`, `품종`, `고도`, `중량`, `현지가격`, `국내유통처`, `국내시세`, `구매메리트분석`
  - 요약보기 시 핵심 컬럼(`커피 이름`, `생산자`, `농장`, `가공방식`, `컵노트`, `100g 환산가`)의 너비를 가독성 높게 균형 재분배.
  - `해외후기` 및 `검증` 열은 테이블에서 완전히 영구 제거됨.

### 2) 애널리틱스 가공 프로세스 복수 선택 (Multi-select Process Filter)
- **파일**: [`analytics.html`](file:///c:/cowork/coffee/analytics.html)
- **상태 관리**: `selectedProcessFilters = new Set()`
- **동작**:
  - 사용자가 '워시드', '내추럴', '무산소' 등 복수 버튼 클릭 시 Set에 추가/제거 (OR 조건 적용)
  - `syncProcessButtonsUI()`: '전체' 버튼과 개별 버튼의 활성 클래스(`.active`)를 자동 상호 동기화
  - 상단 필터 칩 영역에 개별 태그(예: `⚙️ 가공: 워시드 (✕)`) 생성 및 원클릭 취소 지원

### 3) 컵노트 툴팁 순수 한국어 번역 시스템
- 모든 컵노트 뱃지 및 셀의 `title` 속성에는 `"한국어 번역: "` 접두사를 일절 붙이지 않고, **순수 한국어 번역 내용만 노출** (예: `title="복숭아, 청포도, 재스민"`).
- `analytics.html`, `archers_coffee_clean_verified.html`, `theespressolab_verified.html`, `cart.html`, 모바일 5개 파일 전수 적용.

### 4) 실시간 장바구니 및 상단바 동기화 (Cart Engine)
- **저장소**: `localStorage.getItem('archers_cart')` (JSON 배열)
- **상단바 장바구니 메뉴 카운트**:
  - 장바구니에 아이템이 추가/삭제될 때마다 모든 페이지의 상단 메뉴 `🛒 장바구니 (N)` 숫자가 실시간 업데이트.
- **상세보기 모달 카트 버튼**:
  - 텍스트 없이 순수 카트 아이콘(🛒) 버튼 형태.
  - 담겨 있을 경우 액센트 컬러(`.active-in-cart`), 없을 경우 흑백/뮤트 상태로 즉시 토글.

### 5) 불변 동결 발주서 스냅샷 (Frozen Snapshot URL)
- [`cart.html`](file:///c:/cowork/coffee/cart.html)에서 `[🔒 발주서 불변 링크 확정 복사]` 클릭 시:
  - 현재 시점의 발주 번호, 확정 일시, 원두 리스트, 금액을 JSON으로 묶어 Base64 암호화 파라미터(`?snapshot=...`) 생성.
  - 이후 장바구니가 변경되더라도 전달받은 링크는 생성 시점의 내용으로 영구 박제(수정/삭제 버튼 자동 잠금).

---

## 🔍 5. 최신 실시간 사이트 크롤링 결과 및 신규 원두 후보군

2026년 10월 11일 실시간 크롤링을 통해 파악된 양사 공식 사이트의 최신 상태입니다. (추후 사용자가 신규 원두 추가를 요청할 때 즉시 활용 가능)

### 1) 아처스 커피 (`https://archerscoffee.com`)
- **신규 출시 랏**:
  - **`Milk-Based` (핸들: `milk-based`) — 2026.10.08 신규 출시**
    - 파나마 & 엘살바도르 워시드 센트럴 아메리카 블렌드
    - 밀크 베이스 에스프레소 전용 (브라우니, 마카다미아, 흑당)
    - 250g AED 42.00 (약 15,960원) / 1kg AED 135.00 (약 51,300원)
  - **파나마 얀센(Janson) 옥션/스페셜 나노랏 4종 — 9월 17일 출시**
    - `Panama - Janson X GW 26 - 191`, `Panama - Janson Family Hacienda Lot 26 - 127`, `Los Alpes Lot 26 - 68`, `Lot 26 - 20`
- *(현황)*: 10월 4일 재발행된 `Ethiopia Banko Chelchele Chelbesa Natural` 및 9월 25일 다예 벤사 랏 3종은 이미 대시보드 146종 테이블에 반영 완료되어 있음.

### 2) 에스프레소 커피랩 (`https://theespressolab.com`)
- **신규 출시 랏**:
  - **`Nati Lot #742` (핸들: `nati-lot-742-9`, 홀빈 / `nati-lot-742-12`, 캡슐)**
    - 인도네시아 망가라이 (Andre Hamboer 생산자)
    - 품종: 카르티카 (Kartika), 가공: 내추럴
    - 컵노트: 사과(Apple), 베리류(Berries), 오렌지(Orange) / 가격: 90.00 AED (약 34,200원)
  - **`Kotowa Duncan Lot #3135` (핸들: `kotowa-duncan-lot-3135-24`)**
    - 파나마 보케테 코토와 농장 (Pacamara 내추럴, 200g)
    - 컵노트: 흑당(Brown Sugar), 사과(Apple), 서양자두(Prune) / 현재 샘플 요청 상태
  - **드립백 및 캡슐 신규 라인업**:
    - `Caballero Bomba de Fruta #1 (Drip)`, `Gura AA (Drip)`, `Santa Rita Washed Capsule`, `Bombe Washed Capsule`
- *(현황)*: 10월 8일 입고된 100g 홀빈 2종(`Samambaia Yellow Catucai`, `Caballero Bomba #1`)은 이미 56종 데이터셋에 반영 완료되어 있음.

---

## 🛠️ 6. 차기 AI 모델/개발자를 위한 필수 작업 지침 (Instructions for Incoming Models)

1. **Python 실행 환경**:
   - 윈도우 환경이므로 시스템 파이썬 대신 반드시 **`uv run python <스크립트>`** 명령어를 사용하여 실행하십시오.
   - 파이썬 스크립트 작성 시 윈도우 인코딩 오류(cp949)를 방지하기 위해 상단에 반드시 `sys.stdout.reconfigure(encoding='utf-8')`를 포함하십시오.
2. **기계적 검증기(Verification Suite) 실행 의무**:
   - 코드를 수정하거나 새로운 기능을 추가한 후에는 반드시 아래 검증 스크립트를 실행하여 100% 통과(0 Failed)를 확인해야 합니다.
     ```bash
     uv run python scratch/verify_latest_requests.py
     uv run python scratch/verify_font_sync.py
     ```
3. **디자인 일관성 준수**:
   - 에소랩 페이지의 레이아웃, 여백, 컴포넌트 구조는 아처스 대시보드와 항상 일치해야 합니다.
   - 폰트 추가나 스타일 변경 시 임의로 폰트를 변경하지 말고, 디자인 시스템에 정의된 `--font-sans`, `--font-serif`, `--font-mono`를 재사용하십시오.
4. **Git 형상 관리**:
   - 작업 완료 후 `git status`로 변경 사항을 점검하고, 명확한 커밋 메시지 작성 후 `git push origin main`으로 원격 저장소와 항상 동기화하십시오.

---

*작성자: Antigravity AI Assistant*  
*최종 갱신 커밋: `97020d5` (origin/main)*
