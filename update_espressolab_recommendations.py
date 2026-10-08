import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('theespressolab_verified.html', 'r', encoding='utf-8') as f:
    html = f.read()

# New Expert Recommendation Card: Caballero Bomba de Fruta #1
new_expert_card = """
      <!-- Expert 4 (NEW Release) -->
      <div class="rec-card expert" style="border-left: 4px solid var(--accent-gold);">
        <div class="rec-card-header">
          <img src="https://theespressolab.com/storage/products/gallery/images/LCP2RJikX6y4mYR7GQuAwzWb764oGDOIGek3lBeD.png" alt="Caballero Bomba de Fruta #1" class="rec-pkg-img" onclick="openLightbox(this.src, 'Caballero Bomba de Fruta #1')" onerror="this.src='https://via.placeholder.com/105x130?text=Package'">
          <div class="rec-header-info">
            <span class="rec-rank-badge rank-gold" style="background:rgba(217, 119, 6, 0.15); color:#f59e0b; border:1px solid rgba(217, 119, 6, 0.3);">🌟 NEW 신규 입고 | 온두라스 카바예로 챔피언 부부의 과일 폭탄 랏</span>
            <h3>
              <a href="https://theespressolab.com/products-details/caballero-bomba-de-fruta-1-6" target="_blank" class="rec-title-link">
                Caballero Bomba de Fruta #1 (Batch #6) ↗
              </a>
            </h3>
            <div class="rec-origin">🇭🇳 Honduras | Marcala, La Paz (1600 masl)</div>
            <div class="rec-pricing">
              <span class="rec-price-main">76.19 AED (약 28,950원)</span>
              <span class="rec-price-sub">(100g당 76.19 AED (약 28,950원))</span>
            </div>
          </div>
        </div>
        <div class="rec-body">
          <div class="rec-box">
            <div class="rec-box-title blue">💎 큐레이터 선별 사유</div>
            <div class="rec-box-text"><strong>온두라스 COE 1위 레전드 카바예로 부부의 '과일 폭탄(Bomba de Fruta)' 시리즈 최신 랏</strong><br>전 세계 스페셜티 씬에서 가장 존경받는 농부 마리사벨 카바예로와 모이세스 에레라(Marysabel Caballero & Moises Herrera) 부부가 정밀 무산소 내추럴로 가공한 랏입니다. 이름 그대로 패션후르츠, 망고, 다크체리의 폭발적인 과일 향미와 달콤한 흑당, 고급 럼의 복합적인 발효 풍미가 일품입니다.</div>
          </div>
          <div class="rec-box">
            <div class="rec-box-title">💬 평가 & 토론 원문</div>
            <div class="rec-box-text">
              The Espresso Lab 공식 커핑: "패션후르츠와 다크체리의 쥬시한 복합미, 벨벳 같은 바디감과 길게 이어지는 럼의 달콤한 여운."<br>
              <a href="https://theespressolab.com/products-details/caballero-bomba-de-fruta-1-6" target="_blank" class="review-origin-link mt-1">🔗 The Espresso Lab 공식 원문 보기 ↗</a>
            </div>
          </div>
        </div>
      </div>
"""

# Insert before the closing `</div>\n  </div>\n\n  <!-- Main Catalog Tables Section -->`
pattern = re.compile(r'(<!-- Expert 3 -->.*?</div>\s*</div>\s*)(</div>\s*</div>\s*<!-- Main Catalog Tables Section -->)', re.DOTALL)

if pattern.search(html):
    html = pattern.sub(r'\1' + new_expert_card + r'\2', html)
    print("Successfully added Caballero Bomba de Fruta #1 to Espresso Lab expert recommendations!")
else:
    print("Could not match exact expert 3 closing pattern, trying broader regex...")
    pattern2 = re.compile(r'(kotowa-las-brujas-ethiopian-natural-lot-4219.*?</div>\s*</div>\s*</div>\s*)(</div>\s*</div>\s*<!-- Main Catalog Tables Section -->)', re.DOTALL)
    if pattern2.search(html):
        html = pattern2.sub(r'\1' + new_expert_card + r'\2', html)
        print("Successfully added via pattern 2!")
    else:
        # direct replace
        target_str = '<!-- Main Catalog Tables Section -->'
        idx = html.find(target_str)
        if idx != -1:
            # find previous </div></div>
            sub_idx = html.rfind('</div>', 0, idx)
            sub_idx2 = html.rfind('</div>', 0, sub_idx)
            html = html[:sub_idx2] + new_expert_card + '\n    ' + html[sub_idx2:]
            print("Successfully inserted via index replacement!")

# Update count references: 54종 -> 56종
html = re.sub(r'총\s*54종', '총 56종', html)
html = re.sub(r'54개\s*원두', '56개 원두', html)
html = re.sub(r'54종\s*원두', '56종 원두', html)

with open('theespressolab_verified.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("The Espresso Lab dashboard recommendations updated successfully!")
