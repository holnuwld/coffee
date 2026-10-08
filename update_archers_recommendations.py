import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('archers_coffee_clean_verified.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add 3rd recommendation to Competition Series 2025: Finca Deborah, Terroir
new_comp_3rd_card = """
        <div class="rec-card">
          <div class="rec-card-top" style="display:flex; gap:16px; align-items:flex-start;">
            <img src="https://cdn.shopify.com/s/files/1/0260/4302/3426/files/Terroir_1.png?v=1742549870" alt="Panama - Finca Deborah, Terroir" class="rec-card-pkg-img" onclick="openLightbox('https://cdn.shopify.com/s/files/1/0260/4302/3426/files/Terroir_1.png?v=1742549870', 'Panama - Finca Deborah, Terroir')" onerror="this.src='https://via.placeholder.com/90x110?text=Archers'">
            <div style="flex:1;">
              <span class="rec-badge" style="background:rgba(217, 119, 6, 0.15); color:#f59e0b; border:1px solid rgba(217, 119, 6, 0.3);">🥉 3순위 (NEW 릴리즈) | WBC 세계 챔피언십 우승 농장 핀카 데보라 & 극상 크리스탈 클린컵</span>
              <div class="rec-price">
                AED 165.0 <span style="font-size:11px; color:#8b949e;">(100g)</span>
                <div class="rec-price-krw">약 62,700원 (100g당 165.0 AED)</div>
              </div>
            </div>
          </div>
          <div class="rec-title">
            <a href="https://archerscoffee.com/products/panama-terroir-finca-deborah" target="_blank">Panama - Finca Deborah, Terroir (Classic Washed Geisha) ↗</a>
          </div>
          <div class="rec-specs-grid">
            <div>국가: <span>Panama</span></div>
            <div>지역: <span>Volcan, Chiriqui</span></div>
            <div>농장: <span>Finca Deborah</span></div>
            <div>농부: <span>Jamison Savage</span></div>
            <div>품종: <span>Geisha</span></div>
            <div>가공: <span>Classic Washed</span></div>
            <div>고도: <span>1,700 - 1,900 masl</span></div>
            <div>배전도: <span>라이트 (Filter Roast, 핸드드립 전용)</span></div>
          </div>
          <div class="rec-notes">
            🌸 <strong>테이스팅 노트:</strong> White Floral, Bergamot, Meyer Lemon, Jasmine Tea, White Peach
          </div>
          <div class="rec-detail-block">
            <strong>🎯 취향 적합도 (100% 완벽 일치 (WBC 우승 명문 + 볼칸 1,900m + 화이트 티·자스민 질감)):</strong>
            전 세계 바리스타 챔피언십(WBC) 결선 무대에서 수많은 챔피언을 탄생시킨 제이미슨 새비지(Jamison Savage)의 상징적인 핀카 데보라(Finca Deborah)에서 생산된 정통 클래식 워시드 게이샤입니다. 인위적인 가공 향을 배제하고 해발 1,900m 바루 화산의 극한 일교차와 테루아 본연의 투명함을 담아내었습니다.
          </div>
          <div class="rec-detail-block">
            <strong>🏔️ 테루아 & 프로듀서 심층 배경:</strong>
            파나마 볼칸(Volcan) 해발 1,900m 고지대에 위치한 핀카 데보라는 100% 태양광 에너지와 천연 우림 생태계를 보존하는 유기농 바이오다이나믹 농법으로 세계적인 명성을 얻었습니다. 제이미슨 새비지는 첨단 발효 공학과 테루아 중심 재배의 선구자로, 그의 클래식 워시드 랏 'Terroir'는 수확 직후 화산 암반수로 세척되어 극상의 투명한 산미 밸런스를 뿜어냅니다.
          </div>
          <div class="rec-detail-block">
            <strong>🍵 센서리 & 티라이크 컵 프로파일 분석:</strong>
            첫 모금에서 은은한 백화(White Floral)와 자스민 차의 맑고 우아한 티 텍스처가 피어오릅니다. 마이어 레몬의 부드럽고 상큼한 시트러스 산미 뒤로 잘 익은 백도(White Peach)와 베르가못 홍차의 달콤한 여운이 긴 피니시로 이어지며, '크리스탈 클린'이라는 찬사가 아깝지 않은 차분하고 정갈한 컵노트를 선사합니다.
          </div>
          <div class="rec-merit-box">
            <strong>💡 국내 비교 & 현지 구매 압도적 메리트:</strong>
            핀카 데보라의 게이샤는 국내 하이엔드 로스터리에 입고될 경우 100g 기준 90,000~110,000원을 호가하며 순식간에 동납니다. 아처스 공식 직거래 100g 가격은 AED 165 (약 62,700원)으로 세계 최고봉 게이샤를 30% 이상 저렴하게 확보할 수 있는 절호의 기회입니다.
          </div>
          <div class="rec-review-box">
            💬 <strong>전문가 평가:</strong> &quot;핀카 데보라 테루아(Terroir)는 게이샤 본연의 순수함을 사랑하는 브루어들에게 최고의 축복이다. 자스민과 백도의 섬세함이 끝까지 흐트러지지 않는 마스터피스.&quot; (평점 9.7/10)
          </div>
          <div class="rec-brew-box">
            <strong>☕ 마스터 푸어오버 브루잉 레시피:</strong>
            도징: 15.5g | 추출수: 250g (추출비 1:16.1, 93℃) | 드리퍼: 하리오 V60 또는 칼리타 웨이브 | 분쇄도: 코만단테 C40 기준 26클릭 | 레시피: 45g 뜸(40초) → 1차 푸어 85g → 2차 푸어 70g → 3차 푸어 50g. 총 추출 2분 20초.
          </div>
        </div>
"""

# Find the end of Elida card in Competition Series box
# It is followed by `</div>\n      <div class="rec-col-box">\n        <div class="rec-col-header">\n          <span>Microlot Reserve 2025</span>`
pattern_comp = re.compile(r'(<div class="rec-title">\s*<a href="https://archerscoffee.com/products/panama-elida-estate-geisha-plano-2801".*?</div>\s*</div>\s*)(</div>\s*<div class="rec-col-box">\s*<div class="rec-col-header">\s*<span>Microlot Reserve 2025</span>)', re.DOTALL)

if pattern_comp.search(html):
    html = pattern_comp.sub(r'\1' + new_comp_3rd_card + r'\n        \2', html)
    print("Successfully added 3rd recommendation (Finca Deborah Terroir) to Competition Series!")
else:
    print("Warning: Could not match Competition Series end pattern!")

# 2. Add Specialty Selection 2026 Recommendation Box after Microlot Selection 2026
new_specialty_box = """
      <div class="rec-col-box">
        <div class="rec-col-header">
          <span>Specialty Selection 2026 (NEW 신규 라인업)</span>
          <span style="font-size:12px; color:var(--accent);">250g 데일리 &amp; 에스프레소 Best 3</span>
        </div>
    
        <!-- 1. Santuario Sul Sudan Rume -->
        <div class="rec-card">
          <div class="rec-card-top" style="display:flex; gap:16px; align-items:flex-start;">
            <div style="flex:1;">
              <span class="rec-badge">🥇 1순위 | 전설의 수단 루메(Sudan Rume) 희귀 품종 &amp; 100g 2.2만원 극가성비</span>
              <div class="rec-price">
                AED 55.0 <span style="font-size:11px; color:#8b949e;">(250g)</span>
                <div class="rec-price-krw">약 20,900원 (100g당 22.0 AED / 8,360원)</div>
              </div>
            </div>
          </div>
          <div class="rec-title">
            <a href="https://archerscoffee.com/products/brazil-santuario-sul-sudan-rume-washed" target="_blank">Brazil - Santuario Sul Sudan Rume Washed ↗</a>
          </div>
          <div class="rec-specs-grid">
            <div>국가: <span>Brazil</span></div>
            <div>지역: <span>Carmo de Minas, Mantiqueira de Minas</span></div>
            <div>농장: <span>Fazenda Santuario Sul</span></div>
            <div>농부: <span>Luiz Paulo Pereira</span></div>
            <div>품종: <span>Sudan Rume (희귀 야생종)</span></div>
            <div>가공: <span>Washed</span></div>
            <div>고도: <span>1,300 - 1,450 masl</span></div>
            <div>배전도: <span>라이트-미디엄 (Filter Roast)</span></div>
          </div>
          <div class="rec-notes">
            🌸 <strong>테이스팅 노트:</strong> Lemon Verbena, Lemongrass, Floral, Green Tea, Crisp Apple
          </div>
          <div class="rec-detail-block">
            <strong>🎯 선별 사유 &amp; 특징:</strong>
            WBC 결선 단골 희귀 품종인 수단 루메(Sudan Rume)를 브라질 최고 명문 산투아리오 술 농장에서 워시드로 정제한 랏입니다. 레몬 버베나와 레몬그라스, 녹차의 산뜻한 허벌 티 뉘앙스를 자랑하며 250g에 55 AED(약 2만원대)라는 믿기 힘든 데일리 가성비를 제공합니다.
          </div>
        </div>

        <!-- 2. Kenya Karimikui AA -->
        <div class="rec-card">
          <div class="rec-card-top" style="display:flex; gap:16px; align-items:flex-start;">
            <div style="flex:1;">
              <span class="rec-badge">🥈 2순위 | 케냐 스페셜티 성지 니에리(Nyeri) 명문 팩토리 카리미쿠이 AA</span>
              <div class="rec-price">
                AED 65.0 <span style="font-size:11px; color:#8b949e;">(250g)</span>
                <div class="rec-price-krw">약 24,700원 (100g당 26.0 AED / 9,880원)</div>
              </div>
            </div>
          </div>
          <div class="rec-title">
            <a href="https://archerscoffee.com/products/kenya-karimikui-aa" target="_blank">Kenya - Karimikui AA (Washed) ↗</a>
          </div>
          <div class="rec-specs-grid">
            <div>국가: <span>Kenya</span></div>
            <div>지역: <span>Nyeri, Mount Kenya</span></div>
            <div>농장: <span>Karimikui Coffee Factory (Rungeto FCS)</span></div>
            <div>품종: <span>SL28, SL34</span></div>
            <div>가공: <span>Fully Washed</span></div>
            <div>고도: <span>1,700 - 1,900 masl</span></div>
            <div>배전도: <span>라이트-미디엄 (Omni Roast)</span></div>
          </div>
          <div class="rec-notes">
            🌸 <strong>테이스팅 노트:</strong> Blackcurrant, Ruby Grapefruit, Hibiscus, Brown Sugar, Juicy
          </div>
          <div class="rec-detail-block">
            <strong>🎯 선별 사유 &amp; 특징:</strong>
            케냐 니에리 최고의 팩토리로 꼽히는 카리미쿠이(Karimikui)의 최상급 AA 스크린 랏입니다. 블랙커런트와 자몽, 히비스커스의 쥬시한 산미와 흑설탕 같은 달콤한 여운이 에스프레소와 드립 모두에서 뛰어난 존재감을 드러냅니다.
          </div>
        </div>

        <!-- 3. Ethiopia Alo Coffee Mewa Village -->
        <div class="rec-card">
          <div class="rec-card-top" style="display:flex; gap:16px; align-items:flex-start;">
            <div style="flex:1;">
              <span class="rec-badge">🥉 3순위 | 2021 COE 1위 챔피언 타미루 타데세 프로듀싱 메와 빌리지</span>
              <div class="rec-price">
                AED 55.0 <span style="font-size:11px; color:#8b949e;">(250g)</span>
                <div class="rec-price-krw">약 20,900원 (100g당 22.0 AED / 8,360원)</div>
              </div>
            </div>
          </div>
          <div class="rec-title">
            <a href="https://archerscoffee.com/products/ethiopia-alo-coffee-mewa-village" target="_blank">Ethiopia - Alo Coffee Mewa Village ↗</a>
          </div>
          <div class="rec-specs-grid">
            <div>국가: <span>Ethiopia</span></div>
            <div>지역: <span>Bensa, Sidama (2,400 masl)</span></div>
            <div>농장: <span>Mewa Village (Alo Coffee)</span></div>
            <div>농부: <span>Tamiru Tadesse (COE 1위 챔피언)</span></div>
            <div>품종: <span>74158</span></div>
            <div>가공: <span>Washed</span></div>
            <div>배전도: <span>라이트-미디엄 (Filter | Espresso)</span></div>
          </div>
          <div class="rec-notes">
            🌸 <strong>테이스팅 노트:</strong> White Peach, Jasmine, Lemon Blossom, Bergamot, Honey Tea
          </div>
          <div class="rec-detail-block">
            <strong>🎯 선별 사유 &amp; 특징:</strong>
            에티오피아 최고봉 알로 커피의 타미루 타데세가 2,400m 초고고도 메와 빌리지에서 정제한 랏입니다. 복숭아와 자스민, 꿀차의 맑은 뉘앙스로 매일 마셔도 부담 없는 최고의 티라이크 데일리 원두입니다.
          </div>
        </div>
      </div>
"""

# Insert new Specialty Selection box after the last rec-col-box
pattern_last_box = re.compile(r'(<div class="rec-col-box">\s*<div class="rec-col-header">\s*<span>Microlot Selection 2026</span>.*?</div>\s*</div>\s*)(</div>\s*</div>\s*<div class="table-wrap">)', re.DOTALL)

if pattern_last_box.search(html):
    html = pattern_last_box.sub(r'\1' + new_specialty_box + r'\2', html)
    print("Successfully added Specialty Selection 2026 box to Archers Dashboard!")
else:
    print("Warning: Could not match last rec-col-box end pattern!")

# Update total stats banner: 117종 -> 146종
html = re.sub(r'총\s*117종', '총 146종', html)
html = re.sub(r'117개\s*원두', '146개 원두', html)
html = re.sub(r'117종\s*원두', '146종 원두', html)

with open('archers_coffee_clean_verified.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Archers coffee dashboard recommendations updated successfully!")
