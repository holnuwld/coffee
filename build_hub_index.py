import json
import html
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

INDEX_HTML = r'c:\cowork\coffee\index.html'

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

print(f"Loaded {len(top_20)} ranked coffees for index.html integration.")

def render_top20_rows():
    rows = []
    active_count = 0
    for idx, c in enumerate(top_20):
        is_act = c['is_active']
        row_cls = "active-pick-row" if is_act else "overlap-pick-row"
        
        if is_act:
            active_count += 1
            rank_badge = f'<span class="rank-badge active-rank">Pick #{c["active_pick_num"]} <span class="rank-num">({c["rank"]}위)</span></span>'
            status_badge = '<span class="status-badge active-badge">★ 최종 추천 10선</span>'
        else:
            rank_badge = f'<span class="rank-badge dimmed-rank">{c["rank"]}위</span>'
            status_badge = f'<span class="status-badge dimmed-badge">🚫 중복 제외</span>'

        roastery_cls = "archers-btn" if "Archers" in c['roastery'] else "espressolab-btn"
        
        # Summary analysis from detailed review
        rev = c.get('detailed_review', {})
        t_analysis = rev.get('taste_analysis', '')
        short_analysis = t_analysis[:105] + '...' if len(t_analysis) > 105 else t_analysis

        r = f"""
        <tr class="{row_cls}" data-status="{'active' if is_act else 'overlap'}" data-rank="{c['rank']}" data-total="{c['score_total']}" data-taste="{c['score_taste']}" data-price="{c['score_price']}" data-rarity="{c['score_rarity']}" data-handle="{c['handle']}">
          <td class="text-center cart-check-cell">
            <input type="checkbox" class="cart-row-checkbox" data-idx="{idx}" data-price-aed="{c['price_aed']}" data-price-krw="{c['price_krw']}" data-is-active="{'1' if is_act else '0'}" onchange="updateCartToolbarState()">
          </td>
          <td class="text-center font-mono">
            {rank_badge}
          </td>
          <td class="roastery-cell">
            <a href="{c['source_url']}" target="_blank" rel="noopener noreferrer" class="roastery-link-btn {roastery_cls}" title="클릭 시 공식 웹스토어로 이동">
              {c['roastery_badge']} <span class="out-icon">↗</span>
            </a>
          </td>
          <td class="coffee-name-cell">
            <button type="button" class="coffee-modal-btn" onclick="openCoffeeModal({idx})" title="클릭 시 상세 분석 및 브루잉 가이드 보기">
              <span class="btn-coffee-title">{html.escape(c['title'])}</span>
              <span class="view-detail-chip">🔍 상세분석</span>
            </button>
            <div class="c-spec-sub">
              {html.escape(c['country'])} • {html.escape(c['farm'])} • {html.escape(c['variety'])} ({html.escape(c['process'])})
            </div>
          </td>
          <td class="text-right font-mono price-col">
            <div class="aed-price">{c['price_aed']} AED</div>
            <div class="krw-price">약 {c['price_krw']:,}원</div>
          </td>
          <td class="text-center font-mono score-col">
            <div class="score-breakdown">
              <span title="맛 점수 (50점 만점)">맛 {c['score_taste']}/50</span><br>
              <span title="가격 점수 (30점 만점)">가격 {c['score_price']}/30</span> • 
              <span title="한국 희소성 (20점 만점)">희소 {c['score_rarity']}/20</span>
            </div>
            <div class="total-score-box">
              <span class="total-score">{c['score_total']}</span><span class="total-max">/100</span>
            </div>
          </td>
          <td class="analysis-cell">
            <div class="review-desc">{html.escape(short_analysis)}</div>
            <div class="overlap-reason {'act-reason' if is_act else 'dim-reason'} mt-1">
              <strong>판정:</strong> {html.escape(c['overlap_note'])}
            </div>
          </td>
        </tr>
        """
        rows.append(r)
    return "\n".join(rows)

embedded_json_str = json.dumps(top_20, ensure_ascii=False)

content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UAE 2대 명문 스페셜티 커피 통합 검증 & 구매 가이드</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,800;1,600&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
<script>
  (function() {{
    try {{
      var saved = localStorage.getItem('theme');
      if (saved === 'light') {{
        document.documentElement.setAttribute('data-theme', 'light');
      }}
    }} catch (e) {{}}
  }})();
</script>
<style>
  :root {{
    --bg: #090d13;
    --card-bg: #131a26;
    --card-hover: #182333;
    --border: #222f42;
    --border-light: #2e3e57;
    --accent: #d29922;
    --accent-gold: #f0b429;
    --accent-glow: rgba(210, 153, 34, 0.15);
    --text-primary: #f0f6fc;
    --text-secondary: #9da7b3;
    --text-muted: #6e7681;
    --success: #3fb950;
    --blue: #58a6ff;
    --purple: #bc8cff;
    --danger: #f85149;
    --table-head-bg: #0f1622;
    --toolbar-bg: #0f1622;
    --badge-bg: #111722;
    --modal-bg: #101622;
    --modal-inner-bg: #0d121b;
    --modal-score-bg: #0b0f17;
    --active-row-bg: rgba(19, 26, 38, 0.7);
    --overlap-row-bg: rgba(10, 14, 20, 0.6);
  }}

  [data-theme="light"] {{
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --card-hover: #f1f5f9;
    --border: #e2e8f0;
    --border-light: #cbd5e1;
    --accent: #b45309;
    --accent-gold: #d97706;
    --accent-glow: rgba(217, 119, 6, 0.12);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --success: #15803d;
    --blue: #0284c7;
    --purple: #7e22ce;
    --danger: #dc2626;
    --table-head-bg: #f1f5f9;
    --toolbar-bg: #ffffff;
    --badge-bg: #f1f5f9;
    --modal-bg: #ffffff;
    --modal-inner-bg: #f8fafc;
    --modal-score-bg: #f1f5f9;
    --active-row-bg: #ffffff;
    --overlap-row-bg: #f8fafc;
  }}

  /* Light Theme Specific Contrast Enhancements */
  [data-theme="light"] .hub-title {{
    background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  [data-theme="light"] .roastery-card {{
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  }}
  [data-theme="light"] .roastery-card:hover {{
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
  }}
  [data-theme="light"] .r-name {{
    color: #0f172a;
  }}
  [data-theme="light"] .r-highlights {{
    color: #475569;
  }}
  [data-theme="light"] .pref-note-card {{
    background: #ffffff;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  }}
  [data-theme="light"] .table-box {{
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  }}
  [data-theme="light"] .top20-table th {{
    background: #f1f5f9;
    color: #334155;
    border-bottom: 2px solid #e2e8f0;
  }}
  [data-theme="light"] .top20-table td {{
    border-bottom: 1px solid #e2e8f0;
  }}
  [data-theme="light"] .active-pick-row {{
    background: #ffffff;
  }}
  [data-theme="light"] .active-pick-row:hover {{
    background: #f8fafc;
  }}
  [data-theme="light"] .overlap-pick-row {{
    opacity: 0.72;
    background: #f8fafc;
  }}
  [data-theme="light"] .overlap-pick-row:hover {{
    opacity: 1;
    background: #f1f5f9;
  }}
  [data-theme="light"] .btn-coffee-title {{
    color: #0f172a;
  }}
  [data-theme="light"] .coffee-modal-btn:hover .btn-coffee-title {{
    color: var(--accent);
  }}
  [data-theme="light"] .dimmed-rank {{
    background: #e2e8f0;
    color: #64748b;
    border-color: #cbd5e1;
  }}
  [data-theme="light"] .total-score-box {{
    background: #f1f5f9;
    border-color: #cbd5e1;
  }}
  [data-theme="light"] .cart-action-toolbar {{
    background: #ffffff;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  }}
  [data-theme="light"] .cart-ctrl-btn {{
    background: #f1f5f9;
    border-color: #e2e8f0;
    color: #475569;
  }}
  [data-theme="light"] .cart-ctrl-btn:hover {{
    background: #e2e8f0;
    color: #0f172a;
  }}
  [data-theme="light"] .cart-ctrl-btn.active-gold {{
    background: #fef3c7;
    color: #b45309;
    border-color: #f59e0b;
  }}
  [data-theme="light"] .calc-count {{
    color: #0f172a;
  }}
  [data-theme="light"] .cart-action-btn.btn-add {{
    background: #eff6ff;
    border-color: #0284c7;
    color: #0284c7;
  }}
  [data-theme="light"] .cart-action-btn.btn-add:hover {{
    background: #dbeafe;
    color: #0369a1;
  }}
  [data-theme="light"] .f-btn {{
    background: #f1f5f9;
    border-color: #e2e8f0;
    color: #475569;
  }}
  [data-theme="light"] .f-btn:hover {{
    background: #e2e8f0;
    color: #0f172a;
  }}
  [data-theme="light"] .f-btn.active {{
    background: #d97706;
    color: #ffffff;
    border-color: #d97706;
  }}
  [data-theme="light"] .modal-window {{
    background: #ffffff;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.2);
    color: #0f172a;
  }}
  [data-theme="light"] .modal-close-btn {{
    background: #f1f5f9;
    border-color: #e2e8f0;
    color: #64748b;
  }}
  [data-theme="light"] .modal-close-btn:hover {{
    background: #fee2e2;
    border-color: #fca5a5;
    color: #dc2626;
  }}
  [data-theme="light"] .m-title {{
    color: #0f172a;
  }}
  [data-theme="light"] .m-score-grid {{
    background: #f8fafc;
    border-color: #e2e8f0;
  }}
  [data-theme="light"] .m-specs-grid {{
    background: #f8fafc;
    border-color: #e2e8f0;
  }}
  [data-theme="light"] .spec-row {{
    border-bottom: 1px solid #e2e8f0;
  }}
  [data-theme="light"] .m-section-body {{
    background: #f8fafc;
    border-color: #e2e8f0;
    color: #334155;
  }}
  [data-theme="light"] .brew-guide-box {{
    background: #eff6ff;
    border-color: #bfdbfe;
    color: #1e3a8a;
  }}
  [data-theme="light"] .m-btn-close {{
    background: #f1f5f9;
    border-color: #e2e8f0;
    color: #475569;
  }}
  [data-theme="light"] .m-btn-close:hover {{
    background: #e2e8f0;
    color: #0f172a;
  }}
  [data-theme="light"] .cart-toast {{
    background: #ffffff;
    border-color: #d97706;
    color: #0f172a;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  }}
  [data-theme="light"] .sub-sort-item {{
    color: #475569;
  }}
  [data-theme="light"] .sub-sort-item:hover {{
    color: #0f172a;
    background: #e2e8f0;
  }}
  [data-theme="light"] .sub-sort-item.active-sort {{
    color: #b45309;
    background: #fef3c7;
    border-color: #f59e0b;
  }}
  [data-theme="light"] .score-head-title:hover {{
    color: #b45309;
    background: #fef3c7;
  }}
  [data-theme="light"] .score-head-title.active-sort {{
    color: #b45309;
    background: #fef3c7;
    border-color: #f59e0b;
  }}
  [data-theme="light"] .btn-mobile-gold,
  [data-theme="light"] .btn-mobile-blue {{
    background: #f1f5f9;
    border-color: #cbd5e1;
    color: #0f172a;
  }}
  [data-theme="light"] .btn-mobile-gold:hover {{
    background: #e2e8f0;
    border-color: var(--accent);
  }}
  [data-theme="light"] .btn-mobile-blue:hover {{
    background: #e2e8f0;
    border-color: var(--blue);
  }}
  [data-theme="light"] .summary-badge {{
    background: #f1f5f9;
    border-color: #e2e8f0;
    color: #475569;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    line-height: 1.6;
    min-height: 100vh;
    padding: 40px 20px 80px 20px;
  }}

  .container {{
    max-width: 1260px;
    margin: 0 auto;
  }}

  /* Top Navigation Bar */
  .top-nav-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
    gap: 14px;
  }}
  .top-nav-left {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .nav-platform-title {{
    font-weight: 800;
    font-size: 13px;
    color: var(--text-secondary);
  }}
  .nav-btn {{
    background: var(--badge-bg);
    border: 1px solid var(--border);
    color: var(--text-primary);
    padding: 6px 13px;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}
  .nav-btn:hover {{
    border-color: var(--border-light);
    transform: translateY(-1px);
  }}
  .nav-btn-gold {{
    background: var(--accent-glow);
    border-color: var(--accent);
    color: var(--accent-gold);
  }}
  .nav-btn-blue {{
    color: var(--blue);
  }}
  .top-nav-right {{
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
  }}
  .nav-currency-info {{
    font-size: 12px;
    color: var(--text-muted);
  }}

  /* Theme Switcher Button */
  .theme-toggle-btn {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: var(--badge-bg);
    border: 1px solid var(--border);
    color: var(--text-primary);
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  }}
  .theme-toggle-btn:hover {{
    border-color: var(--accent);
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(210, 153, 34, 0.25);
  }}
  .theme-icon {{
    font-size: 14px;
    transition: transform 0.3s ease;
  }}
  .theme-toggle-btn:hover .theme-icon {{
    transform: rotate(20deg);
  }}
  [data-theme="light"] .theme-toggle-btn {{
    background: #ffffff;
    border-color: #cbd5e1;
    color: #0f172a;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }}
  [data-theme="light"] .theme-toggle-btn:hover {{
    border-color: var(--accent);
    background: #f8fafc;
  }}

  /* Mobile Banner */
  .mobile-switch-banner {{
    background: rgba(210, 153, 34, 0.12);
    border: 1px solid var(--accent);
    border-radius: 12px;
    padding: 12px 18px;
    margin: 20px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
  }}
  .mobile-switch-text {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    color: var(--text-primary);
  }}
  .mobile-switch-link {{
    background: linear-gradient(135deg, #d29922, #b07d12);
    color: #000;
    font-weight: 800;
    font-size: 12.5px;
    padding: 7px 14px;
    border-radius: 6px;
    text-decoration: none;
    transition: transform 0.15s ease;
  }}
  .mobile-switch-link:hover {{
    transform: translateY(-1px);
  }}
  [data-theme="light"] .mobile-switch-banner {{
    background: #fffbeb;
    border-color: #f59e0b;
  }}
  [data-theme="light"] .mobile-switch-text {{
    color: #78350f;
  }}

  /* Header Section */
  .hub-header {{
    text-align: center;
    margin-bottom: 40px;
  }}
  .hub-badge {{
    display: inline-block;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-gold);
    font-weight: 800;
    background: var(--accent-glow);
    border: 1px solid var(--accent);
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 18px;
  }}
  .hub-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 42px;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 16px;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  @media (max-width: 768px) {{
    .hub-title {{ font-size: 30px; }}
  }}
  .hub-desc {{
    color: var(--text-secondary);
    font-size: 16px;
    max-width: 840px;
    margin: 0 auto 24px auto;
    line-height: 1.7;
  }}

  .stats-summary-bar {{
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 40px;
  }}
  .summary-badge {{
    background: #111722;
    border: 1px solid var(--border);
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .summary-badge.green {{ border-color: rgba(63, 185, 80, 0.4); color: var(--success); }}
  .summary-badge.gold {{ border-color: var(--accent); color: var(--accent-gold); }}

  /* User Preference Note Card */
  .pref-note-card {{
    background: rgba(19, 26, 38, 0.7);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    gap: 20px;
  }}
  @media (max-width: 680px) {{
    .pref-note-card {{ flex-direction: column; align-items: flex-start; }}
  }}
  .pref-icon {{
    font-size: 36px;
    flex-shrink: 0;
  }}
  .pref-content h3 {{
    font-size: 16px;
    font-weight: 700;
    color: var(--accent-gold);
    margin-bottom: 4px;
  }}
  .pref-content p {{
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.6;
  }}

  /* Roastery Showcase Grid */
  .roastery-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
    margin-bottom: 56px;
  }}
  @media (max-width: 860px) {{
    .roastery-grid {{ grid-template-columns: 1fr; }}
  }}

  .roastery-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 32px 28px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
    transition: all 0.25s ease;
  }}
  .roastery-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  }}
  .roastery-card.espressolab {{
    border-top: 5px solid #d29922;
  }}
  .roastery-card.archers {{
    border-top: 5px solid #58a6ff;
  }}

  .r-top-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 14px;
  }}
  .tag-gold {{ background: var(--accent-glow); color: var(--accent-gold); border: 1px solid var(--accent); }}
  .tag-blue {{ background: rgba(88, 166, 255, 0.15); color: var(--blue); border: 1px solid var(--blue); }}

  .r-name {{
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
    color: #fff;
  }}
  .r-subtitle {{
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 20px;
  }}

  .r-highlights {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 24px;
    font-size: 13px;
    color: #c9d1d9;
  }}
  .r-highlights li {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    line-height: 1.5;
  }}
  .r-highlights li span {{
    color: var(--accent-gold);
    font-weight: 800;
    flex-shrink: 0;
  }}
  .roastery-card.archers .r-highlights li span {{
    color: var(--blue);
  }}

  .r-actions {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: auto;
  }}
  .r-btn {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px 10px;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.2s ease;
    text-align: center;
  }}
  .r-btn .btn-title {{
    font-size: 13.5px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .r-btn .btn-sub {{
    font-size: 10.5px;
    opacity: 0.8;
    margin-top: 2px;
    font-weight: 500;
  }}

  .btn-desktop-gold {{
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
  }}
  .btn-desktop-gold:hover {{ background: linear-gradient(135deg, #e3b341, #c89617); }}

  .btn-mobile-gold {{
    background: #1c2638;
    border: 1px solid var(--border-light);
    color: var(--text-primary);
  }}
  .btn-mobile-gold:hover {{ border-color: var(--accent); background: #223047; }}

  .btn-desktop-blue {{
    background: linear-gradient(135deg, #238636, #1e702d);
    color: #fff;
  }}
  .btn-desktop-blue:hover {{ background: linear-gradient(135deg, #2ea043, #238636); }}

  .btn-mobile-blue {{
    background: #1c2638;
    border: 1px solid var(--border-light);
    color: var(--text-primary);
  }}
  .btn-mobile-blue:hover {{ border-color: var(--blue); background: #223047; }}

  /* ========================================================
     TOP 20 RANKED 100g CURATION SECTION
     ======================================================== */
  .top20-section {{
    margin-top: 60px;
    border-top: 2px solid var(--border);
    padding-top: 48px;
  }}
  .top20-header {{
    text-align: center;
    margin-bottom: 32px;
  }}
  .top20-badge {{
    display: inline-block;
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
    font-size: 12px;
    font-weight: 800;
    padding: 5px 14px;
    border-radius: 999px;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .top20-title {{
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.8px;
    margin-bottom: 12px;
  }}
  .top20-desc {{
    font-size: 15px;
    color: var(--text-secondary);
    max-width: 920px;
    margin: 0 auto 24px auto;
    line-height: 1.65;
  }}

  /* Score Criteria Legend Box (50 / 30 / 20) */
  .criteria-box {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 24px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }}
  @media (max-width: 768px) {{
    .criteria-box {{ grid-template-columns: 1fr; gap: 12px; }}
  }}
  .criterion-item {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .crit-name {{
    font-size: 13.5px;
    font-weight: 700;
    color: var(--accent-gold);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .crit-desc {{
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.5;
  }}

  /* Interactive Navigation Tip */
  .interaction-guide {{
    background: rgba(88, 166, 255, 0.08);
    border: 1px solid rgba(88, 166, 255, 0.25);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 13px;
    color: var(--blue);
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }}

  /* Cart Action Toolbar */
  .cart-action-toolbar {{
    background: #0f1622;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
    margin-bottom: 16px;
  }}
  .cart-action-toolbar.mt-3 {{
    margin-top: 16px;
    margin-bottom: 0;
  }}
  .cart-left-controls {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .cart-right-controls {{
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
  }}
  .cart-ctrl-btn {{
    background: #162030;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .cart-ctrl-btn:hover {{
    color: var(--text-primary);
    border-color: var(--border-light);
    background: #1c283c;
  }}
  .cart-ctrl-btn.active-gold {{
    background: var(--accent-glow);
    color: var(--accent-gold);
    border-color: var(--accent);
  }}
  .cart-ctrl-btn.active-gold:hover {{
    background: rgba(210, 153, 34, 0.25);
  }}

  .cart-calc-box {{
    font-size: 13px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .calc-count {{ color: #fff; font-weight: 700; }}
  .calc-aed {{ color: var(--accent-gold); font-size: 15px; font-weight: 800; }}
  .calc-krw {{ color: var(--text-muted); font-size: 12px; }}
  .calc-sep {{ color: var(--border); }}

  .cart-action-btn {{
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }}
  .cart-action-btn.btn-add {{
    background: #1e293b;
    border: 1px solid var(--blue);
    color: var(--blue);
  }}
  .cart-action-btn.btn-add:hover {{
    background: rgba(88, 166, 255, 0.18);
    color: #fff;
  }}
  .cart-action-btn.btn-view {{
    background: linear-gradient(135deg, #d29922, #b8860b);
    border: 1px solid var(--accent);
    color: #000;
  }}
  .cart-action-btn.btn-view:hover {{
    background: linear-gradient(135deg, #e3b341, #c89617);
    color: #000;
    transform: translateY(-1px);
  }}

  /* Filter Controls */
  .top20-filters {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
  }}
  .filter-btns {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .f-btn {{
    background: #111722;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }}
  .f-btn:hover {{
    color: var(--text-primary);
    border-color: var(--border-light);
  }}
  .f-btn.active {{
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
  }}
  .legend-note {{
    font-size: 12.5px;
    color: var(--text-muted);
  }}

  /* Table Design */
  .table-box {{
    overflow-x: auto;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
  }}
  .top20-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13px;
    white-space: normal;
  }}
  .top20-table th {{
    background: #0f1622;
    color: var(--text-secondary);
    font-weight: 700;
    text-align: left;
    padding: 14px 16px;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }}
  .top20-table td {{
    padding: 16px 16px;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }}

  /* Cart Checkbox Style */
  .cart-check-cell {{
    width: 45px;
  }}
  .cart-row-checkbox, #selectAllCheckbox {{
    width: 17px;
    height: 17px;
    cursor: pointer;
    accent-color: var(--accent-gold);
  }}

  /* Active vs Overlap Styling */
  .active-pick-row {{
    background: rgba(19, 26, 38, 0.7);
    transition: background 0.15s ease;
  }}
  .active-pick-row:hover {{
    background: rgba(24, 35, 51, 0.95);
  }}
  .overlap-pick-row {{
    background: rgba(10, 14, 20, 0.6);
    opacity: 0.55;
    transition: all 0.2s ease;
  }}
  .overlap-pick-row:hover {{
    opacity: 0.95;
    background: rgba(16, 22, 32, 0.9);
  }}

  /* Cell Details */
  .rank-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 800;
    font-size: 12px;
    white-space: nowrap;
  }}
  .active-rank {{
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
  }}
  .active-rank .rank-num {{
    font-size: 10.5px;
    opacity: 0.85;
    font-weight: 600;
  }}
  .dimmed-rank {{
    background: #1c2430;
    color: var(--text-muted);
    border: 1px solid var(--border);
  }}

  /* Roastery Link Button in Table */
  .roastery-cell {{
    min-width: 145px;
  }}
  .roastery-link-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    transition: all 0.15s ease;
    white-space: nowrap;
  }}
  .roastery-link-btn .out-icon {{
    font-size: 10px;
    opacity: 0.8;
  }}
  .archers-btn {{
    background: rgba(88, 166, 255, 0.15);
    color: var(--blue);
    border: 1px solid rgba(88, 166, 255, 0.35);
  }}
  .archers-btn:hover {{
    background: rgba(88, 166, 255, 0.28);
    border-color: var(--blue);
    color: #fff;
    transform: translateY(-1px);
  }}
  .espressolab-btn {{
    background: var(--accent-glow);
    color: var(--accent-gold);
    border: 1px solid var(--accent);
  }}
  .espressolab-btn:hover {{
    background: rgba(210, 153, 34, 0.28);
    border-color: #ffd166;
    color: #fff;
    transform: translateY(-1px);
  }}

  /* Coffee Name Modal Trigger Button */
  .coffee-name-cell {{
    min-width: 250px;
  }}
  .coffee-modal-btn {{
    background: none;
    border: none;
    text-align: left;
    padding: 0;
    margin: 0;
    cursor: pointer;
    display: inline-flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    color: inherit;
    width: 100%;
  }}
  .btn-coffee-title {{
    font-size: 14.5px;
    font-weight: 700;
    color: #fff;
    transition: color 0.15s ease;
    line-height: 1.35;
  }}
  .coffee-modal-btn:hover .btn-coffee-title {{
    color: var(--accent-gold);
    text-decoration: underline;
  }}
  .view-detail-chip {{
    display: inline-block;
    font-size: 10.5px;
    color: var(--accent-gold);
    background: rgba(210, 153, 34, 0.12);
    border: 1px solid rgba(210, 153, 34, 0.3);
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
    letter-spacing: 0.3px;
    margin-top: 2px;
  }}
  .coffee-modal-btn:hover .view-detail-chip {{
    background: var(--accent);
    color: #000;
  }}
  .c-spec-sub {{
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 4px;
    line-height: 1.4;
  }}

  .price-col {{
    min-width: 105px;
  }}
  .aed-price {{
    font-size: 15px;
    font-weight: 800;
    color: var(--accent-gold);
  }}
  .krw-price {{
    font-size: 11.5px;
    color: var(--text-muted);
  }}

  /* Clickable Score Header & Sub-sort Controls */
  .score-col-header {{
    min-width: 175px;
    user-select: none;
    padding: 10px 14px !important;
  }}
  .score-head-title {{
    font-size: 13.5px;
    font-weight: 800;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 6px;
    transition: all 0.15s ease;
    color: var(--text-primary);
    border: 1px solid transparent;
  }}
  .score-head-title:hover {{
    color: var(--accent-gold);
    background: rgba(210, 153, 34, 0.12);
    border-color: rgba(210, 153, 34, 0.3);
  }}
  .score-head-title.active-sort {{
    color: var(--accent-gold);
    background: rgba(210, 153, 34, 0.2);
    border: 1px solid var(--accent);
  }}
  .score-sub-sorts {{
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }}
  .sub-sort-item {{
    cursor: pointer;
    padding: 2px 7px;
    border-radius: 5px;
    font-weight: 700;
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 3px;
    color: #cbd5e1;
    border: 1px solid transparent;
  }}
  .sub-sort-item:hover {{
    color: #fff;
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.25);
  }}
  .sub-sort-item.active-sort {{
    color: var(--accent-gold);
    background: rgba(210, 153, 34, 0.22);
    border-color: var(--accent);
  }}
  .sort-sub-ind {{
    font-size: 10.5px;
    opacity: 0.85;
  }}
  .sort-sep {{
    color: var(--border-light);
    font-size: 11px;
    user-select: none;
  }}

  .score-col {{
    min-width: 135px;
  }}
  .score-breakdown {{
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 3px;
    line-height: 1.35;
  }}
  .total-score-box {{
    display: inline-block;
    background: #0d131c;
    border: 1px solid var(--border);
    padding: 3px 8px;
    border-radius: 6px;
  }}
  .total-score {{
    font-size: 16px;
    font-weight: 800;
    color: var(--success);
  }}
  .total-max {{
    font-size: 10px;
    color: var(--text-muted);
  }}

  .analysis-cell {{
    min-width: 290px;
  }}
  .review-desc {{
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
  }}
  .overlap-reason {{
    font-size: 11px;
    padding: 3px 6px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 5px;
  }}
  .act-reason {{
    background: rgba(63, 185, 80, 0.1);
    color: var(--success);
    border: 1px solid rgba(63, 185, 80, 0.25);
  }}
  .dim-reason {{
    background: rgba(248, 81, 73, 0.1);
    color: #ff7b72;
    border: 1px solid rgba(248, 81, 73, 0.25);
  }}

  /* Toast Notification */
  .cart-toast {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #111a28;
    border: 1px solid var(--accent);
    color: #fff;
    padding: 14px 20px;
    border-radius: 10px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
    font-size: 13.5px;
    z-index: 10000;
    display: none;
    align-items: center;
    gap: 10px;
    animation: toastFadeIn 0.2s ease;
  }}
  @keyframes toastFadeIn {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  /* ========================================================
     MODAL POPUP STYLING
     ======================================================== */
  .modal-backdrop {{
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.82);
    backdrop-filter: blur(8px);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    padding: 20px;
    overflow-y: auto;
  }}
  .modal-backdrop.active {{
    display: flex;
  }}
  .modal-window {{
    background: #101622;
    border: 1px solid var(--border-light);
    border-radius: 20px;
    max-width: 820px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.7);
    padding: 32px;
    position: relative;
    color: var(--text-primary);
    animation: modalSlideIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }}
  @keyframes modalSlideIn {{
    from {{ opacity: 0; transform: translateY(16px) scale(0.98); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
  }}
  .modal-close-btn {{
    position: absolute;
    top: 20px;
    right: 20px;
    background: #1c2638;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    font-size: 20px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
  }}
  .modal-close-btn:hover {{
    color: #fff;
    border-color: var(--danger);
    background: rgba(248, 81, 73, 0.2);
  }}

  .m-header-tags {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }}
  .m-rank-badge {{
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
  }}
  .m-title {{
    font-size: 24px;
    font-weight: 800;
    line-height: 1.3;
    margin-bottom: 18px;
    color: #fff;
  }}
  
  /* Modal Score Grid */
  .m-score-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
    background: #0b0f17;
    border: 1px solid var(--border);
    padding: 16px;
    border-radius: 12px;
    text-align: center;
  }}
  @media (max-width: 600px) {{
    .m-score-grid {{ grid-template-columns: 1fr 1fr; }}
  }}
  .m-score-box .s-label {{
    font-size: 11.5px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }}
  .m-score-box .s-val {{
    font-size: 20px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
  }}
  .s-val.tot {{ color: var(--success); }}
  .s-val.taste {{ color: var(--accent-gold); }}
  .s-val.price {{ color: var(--blue); }}
  .s-val.rarity {{ color: var(--purple); }}

  /* Modal Specs Grid */
  .m-specs-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 24px;
    background: rgba(19, 26, 38, 0.5);
    border: 1px solid var(--border);
    padding: 18px;
    border-radius: 12px;
    font-size: 13px;
  }}
  @media (max-width: 600px) {{
    .m-specs-grid {{ grid-template-columns: 1fr; }}
  }}
  .spec-row {{
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid rgba(34, 47, 66, 0.5);
    padding-bottom: 6px;
  }}
  .spec-k {{ color: var(--text-muted); font-weight: 500; }}
  .spec-v {{ color: var(--text-primary); font-weight: 700; text-align: right; }}

  /* Modal Section Blocks */
  .m-section {{
    margin-bottom: 22px;
  }}
  .m-section-title {{
    font-size: 14.5px;
    font-weight: 700;
    color: var(--accent-gold);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .m-section-body {{
    background: #0d121b;
    border: 1px solid var(--border);
    padding: 14px 16px;
    border-radius: 10px;
    font-size: 13.5px;
    color: #c9d1d9;
    line-height: 1.65;
  }}
  .brew-guide-box {{
    background: rgba(88, 166, 255, 0.08);
    border: 1px solid rgba(88, 166, 255, 0.25);
    color: #e6edf3;
  }}

  /* Modal Actions */
  .m-actions {{
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 28px;
    border-top: 1px solid var(--border);
    padding-top: 20px;
  }}
  .m-btn-out {{
    background: linear-gradient(135deg, #d29922, #b8860b);
    color: #000;
    text-decoration: none;
    font-weight: 800;
    font-size: 13.5px;
    padding: 10px 20px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }}
  .m-btn-out:hover {{
    background: linear-gradient(135deg, #e3b341, #c89617);
    transform: translateY(-2px);
  }}
  .m-btn-close {{
    background: #1c2638;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    font-weight: 700;
    font-size: 13.5px;
    padding: 10px 18px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .m-btn-close:hover {{
    color: #fff;
    border-color: var(--border-light);
  }}

  /* Footer */
  footer {{
    text-align: center;
    font-size: 13px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 24px;
    margin-top: 60px;
  }}
  footer a {{ color: var(--blue); text-decoration: none; }}
</style>
</head>
<body>

<div class="container">

  <!-- Top Navigation Bar -->
  <div class="top-nav-bar">
    <div class="top-nav-left">
      <span class="nav-platform-title">🌐 플랫폼 바로가기:</span>
      <a href="mobile_index.html" class="nav-btn nav-btn-gold">📱 모바일 전용 뷰 ↗</a>
      <a href="cart.html" class="nav-btn">🛒 데스크톱 발주서 (cart.html)</a>
      <a href="mobile_cart.html" class="nav-btn nav-btn-blue">📱 모바일 발주서</a>
    </div>
    <div class="top-nav-right">
      <button id="themeToggleBtn" class="theme-toggle-btn" onclick="toggleTheme()" title="화면 테마 변경 (브라이트 / 다크)">
        <span class="theme-icon">☀️</span>
        <span class="theme-label">브라이트 모드</span>
      </button>
      <span class="nav-currency-info">1 AED ≈ 380 KRW • 현지 방문 구매 무관세 기준</span>
    </div>
  </div>

  <!-- Header -->
  <header class="hub-header">
    <div class="hub-badge">UAE Specialty Coffee Intelligence Portal</div>
    <h1 class="hub-title">UAE 2대 명문 스페셜티 로스터리<br>전수 검증 & 현지 구매 허브</h1>
    <p class="hub-desc">
      두바이 현지 방문 구매를 위해 아랍에미리트 최고의 로스터리 <strong>The Espresso Lab</strong>과 <strong>Archers Coffee</strong>의 전수 원두(총 171종)를 수집하고, <code>verify_quotes.py</code> 순수 코드로 기계 검증(100% PASS)을 완료한 공식 인덱스 포털입니다.
    </p>

    <!-- Mobile Switcher Banner (Noticeable on phones) -->
    <div class="mobile-switch-banner">
      <div class="mobile-switch-text">
        <span style="font-size:18px;">📱</span>
        <span>스마트폰/태블릿으로 접속하셨나요? <strong>좌우 스크롤 없는 모바일 전용 페이지</strong>를 제공합니다.</span>
      </div>
      <a href="mobile_index.html" class="mobile-switch-link">모바일 뷰 전환하기 ↗</a>
    </div>

    <!-- Stats Summary -->
    <div class="stats-summary-bar">
      <div class="summary-badge green">
        <span>✓</span> 총 171종 원두 100% 기계 검증 완료
      </div>
      <div class="summary-badge gold">
        <span>📷</span> 양대 로스터리 171종 전수 실물 패키지 사진 완비
      </div>
      <div class="summary-badge">
        <span>🇦🇪</span> UAE 현지 매장 무관세 구매 가이드
      </div>
    </div>
  </header>

  <!-- User Taste Matching Notice -->
  <div class="pref-note-card">
    <div class="pref-icon">☕</div>
    <div class="pref-content">
      <h3>선호 취향 맞춤형 필터링 안내</h3>
      <p>
        사용자님의 선호 취향인 <strong>"파나마/에티오피아 원산지 + 워시드 가공 + 백차/자스민 티라이크(Tea-like) 텍스처 + 라이트로스트 푸어오버"</strong>에 맞추어 각 로스터리별 1순위 추천 및 전문가 추천 원두를 상단에 독립 배치했습니다.
      </p>
    </div>
  </div>

  <!-- 2 Major Roasteries Grid -->
  <div class="roastery-grid">

    <!-- ROASTERY 1: The Espresso Lab -->
    <div class="roastery-card espressolab">
      <div>
        <div class="r-top-tag tag-gold">Featured Roastery • 전수 54종</div>
        <h2 class="r-name">The Espresso Lab (UAE)</h2>
        <p class="r-subtitle">
          두바이 D3(디자인 디스트릭트) 및 알 사르칼 에비뉴에 플래그십을 둔 하이엔드 로스터리. 2022 Best of Panama 1위 Auromar Firestone 및 2021 에티오피아 COE 1위 Bombe Washed 보유.
        </p>
        <ul class="r-highlights">
          <li><span>📷</span> <strong>패키지 실물 사진 전수 탑재:</strong> 매장 진열대 실물과 즉시 비교 가능</li>
          <li><span>🥇</span> <strong>BOP 챔피언 Auromar Firestone:</strong> 국내 시세 대비 35% 할인</li>
          <li><span>💰</span> <strong>에티오피아 Bombe Washed:</strong> 200g 80 AED (100g당 1.5만원) 반값 종결</li>
          <li><span>🔍</span> <strong>파나마 게이샤 & 하이엔드 25종:</strong> 전수 100% 기계 검증 PASS</li>
        </ul>
      </div>

      <div class="r-actions">
        <a href="theespressolab_verified.html" class="r-btn btn-desktop-gold">
          <span class="btn-title">🖥️ 데스크톱 대시보드</span>
          <span class="btn-sub">18개 컬럼 양방향 정렬 표</span>
        </a>
        <a href="theespressolab_mobile.html" class="r-btn btn-mobile-gold">
          <span class="btn-title">📱 모바일 퀵 가이드</span>
          <span class="btn-sub">패키지 카드 & 원터치 필터</span>
        </a>
      </div>
    </div>

    <!-- ROASTERY 2: Archers Coffee -->
    <div class="roastery-card archers">
      <div>
        <div class="r-top-tag tag-blue">Global Specialty Champion • 전수 117종</div>
        <h2 class="r-name">Archers Coffee (UAE)</h2>
        <p class="r-subtitle">
          샤르자 및 두바이를 거점으로 전 세계 유명 바리스타들과 직거래하는 UAE 최대 스페셜티 로스터리. 컴피티션, 마이크로랏 리저브, 셀렉션 3대 컬렉션 완비.
        </p>
        <ul class="r-highlights">
          <li><span>📷</span> <strong>패키지 실물 사진 전수 탑재:</strong> 117종 전수 실물 사진 & 라이트박스 확대 지원</li>
          <li><span>🥇</span> <strong>Auromar Geisha Washed Peaberry:</strong> 아처스 독점 피베리 나노랏</li>
          <li><span>🥈</span> <strong>Hamasho Village Washed:</strong> 다예 벤사 독점 랏 (100g 1.2만원대)</li>
          <li><span>🏆</span> <strong>Elida Estate Geisha Washed Plano:</strong> 라마스투스 옥션 명문</li>
          <li><span>📋</span> <strong>3대 컬렉션 117종 전수 완비:</strong> 국내 시세 및 커뮤니티 리뷰 대조</li>
        </ul>
      </div>

      <div class="r-actions">
        <a href="archers_coffee_clean_verified.html" class="r-btn btn-desktop-blue">
          <span class="btn-title">🖥️ 데스크톱 대시보드</span>
          <span class="btn-sub">전 컬렉션 정밀 비교 분석</span>
        </a>
        <a href="mobile.html" class="r-btn btn-mobile-blue">
          <span class="btn-title">📱 모바일 퀵 가이드</span>
          <span class="btn-sub">현지 쇼핑 최적화 모바일 뷰</span>
        </a>
      </div>
    </div>

  </div>

  <!-- ========================================================
       TOP 20 RANKED 100g CURATION SECTION
       ======================================================== -->
  <section class="top20-section" id="top20Section">
    <div class="top20-header">
      <div class="top20-badge">Integrated 100g Master Curation</div>
      <h2 class="top20-title">🏆 2대 로스터리 통합 100g 원두 랭킹 TOP 20<br>& 최종 엄선 10선 (Active Picks)</h2>
      <p class="top20-desc">
        두 로스터리의 100g 패키지 원두 131종 전체를 3대 기준(<strong>맛 50점 + 가격 합리성 30점 + 한국 희소성 20점 = 총 100점 만점</strong>)으로 정밀 평가했습니다.<br>
        프로파일 중복 여부는 점수 산정에서 배제하고 순수 점수로 1~20위를 매긴 후, <strong>7대 기준(지역, 농장, 프로듀서, 컵노트, 프로세스, 배전도, 고도) 유사도 프로파일</strong>을 적용하여 상위 순위와 겹치는 하위 10종을 음영(톤다운) 처리했습니다.<br>
        <em>※ 동일 농장이더라도 컵노트가 다르면 중복 제외하지 않고 실질 추천 랏으로 당당히 선발했습니다.</em>
      </p>
    </div>

    <!-- Criteria Breakdown Box (50 / 30 / 20) -->
    <div class="criteria-box">
      <div class="criterion-item">
        <div class="crit-name">☕ 1. 맛이 좋은가 (50점 만점)</div>
        <div class="crit-desc">클린 워시드/발효 가공(+10), 재스민·베르가못·얼그레이·복숭아 티라이크 플로럴 센서리(+15), 파나마/에티오피아 최고 테루아(+12), 게이샤/SL28/피베리/BOP/COE 명문 혈통(+13).</div>
      </div>
      <div class="criterion-item">
        <div class="crit-name">💰 2. 가격이 합리적인가 (30점 만점)</div>
        <div class="crit-desc">100g당 현지 가격 구간(40 AED 이하: 30점 만점부터 차등) 및 국내 동일/유사 등급 시세(7~12만원) 대비 35~50% 이상 저렴한 메리트 반영.</div>
      </div>
      <div class="criterion-item">
        <div class="crit-name">🇰🇷 3. 한국에서 구하기 어려운가 (20점 만점)</div>
        <div class="crit-desc">국내 공식 수입 전무 여부(20점 만점), UAE 현지 로스터리 단독 다이렉트 독점 랏, 마이크로/나노랏 및 국내 대체 불가성 평가.</div>
      </div>
    </div>

    <!-- Interactive Navigation Tip -->
    <div class="interaction-guide">
      <div>💡 <strong>인터랙션 안내:</strong></div>
      <div>• <strong>표 좌측 체크박스</strong>로 원하는 원두를 선택한 뒤 <code>[🛒 장바구니 담기]</code> 및 <code>[📋 장바구니 보기]</code>를 누르면 <strong>공식 구매 발주서(cart.html)</strong>로 바로 연결됩니다.</div>
      <div>• <strong>커피 이름</strong>을 클릭하면 <strong>7대 유사도 분석</strong>과 브루잉 팁이 담긴 <strong>상세 분석 모달</strong>이 열립니다.</div>
      <div>• <strong>로스터리 이름</strong>을 클릭하면 해당 커피의 <strong>공식 웹스토어 판매 페이지</strong>로 새 창 이동합니다.</div>
    </div>

    <!-- Cart Action Toolbar (Top) -->
    <div class="cart-action-toolbar" id="cartToolbarTop">
      <div class="cart-left-controls">
        <button type="button" class="cart-ctrl-btn" onclick="toggleSelectAllCart(true)">☑ 전체 선택</button>
        <button type="button" class="cart-ctrl-btn active-gold" onclick="selectRecommended10()">🎯 추천 10선만 선택</button>
        <button type="button" class="cart-ctrl-btn" onclick="clearCartSelection()">☐ 선택 해제</button>
      </div>
      <div class="cart-right-controls">
        <div class="cart-calc-box">
          <span class="calc-label">선택 항목:</span>
          <strong id="selectedItemsCountTop" class="calc-count">0</strong>개
          <span class="calc-sep">|</span>
          <strong id="selectedTotalPriceAedTop" class="calc-aed">0.0</strong> AED 
          <span class="calc-krw">(약 <strong id="selectedTotalPriceKrwTop">0</strong>원)</span>
        </div>
        <button type="button" class="cart-action-btn btn-add" onclick="saveSelectedToCart()">🛒 장바구니 담기</button>
        <button type="button" class="cart-action-btn btn-view" onclick="openCartPage()">📋 장바구니 보기 (<span class="cart-badge-count">0</span>개) ↗</button>
      </div>
    </div>

    <!-- Filter Buttons & Legend -->
    <div class="top20-filters">
      <div class="filter-btns">
        <button class="f-btn active" onclick="filterRanked('all', this)">전체 20개 보기 (중복 음영 포함)</button>
        <button class="f-btn" onclick="filterRanked('active', this)">🎯 최종 추천 10선만 모아보기</button>
        <button class="f-btn" onclick="filterRanked('overlap', this)">🚫 중복 제외 10종 보기</button>
      </div>
      <div class="legend-note">
        💡 <strong>안내:</strong> 점수는 순수 기준으로만 매겨졌으며, 유사도 프로파일(7대 기준)을 적용하여 몇위 어느 커피와 몇% 유사한지 표기했습니다.
      </div>
    </div>

    <!-- Table Responsive Box -->
    <div class="table-box">
      <table class="top20-table" id="top20Table">
        <thead>
          <tr>
            <th style="width:45px; text-align:center;">
              <input type="checkbox" id="selectAllCheckbox" onchange="toggleSelectAllCart(this.checked)" title="전체 선택/해제">
            </th>
            <th class="text-center" style="width:110px;">선정 / 순위</th>
            <th>로스터리 (공식 링크 ↗)</th>
            <th>커피 이름 (클릭 시 분석 모달 🔍) & 스펙</th>
            <th class="text-right">100g 가격</th>
            <th class="text-center score-col-header">
              <div class="score-head-title active-sort" id="sortTrigger_total" onclick="sortTableByScore('total')" title="종합 총점 기준 정렬 (클릭 시 오름차순/내림차순 토글)">
                종합 점수 (100점) <span class="sort-ind" id="sortInd_total">▼</span>
              </div>
              <div class="score-sub-sorts">
                <span class="sub-sort-item" id="sortTrigger_taste" onclick="sortTableByScore('taste')" title="맛 점수(50점 만점) 기준 정렬">
                  맛 <span class="sort-sub-ind" id="sortInd_taste">↕</span>
                </span>
                <span class="sort-sep">/</span>
                <span class="sub-sort-item" id="sortTrigger_price" onclick="sortTableByScore('price')" title="가격 점수(30점 만점) 기준 정렬">
                  가격 <span class="sort-sub-ind" id="sortInd_price">↕</span>
                </span>
                <span class="sort-sep">/</span>
                <span class="sub-sort-item" id="sortTrigger_rarity" onclick="sortTableByScore('rarity')" title="한국 희소성(20점 만점) 기준 정렬">
                  희소 <span class="sort-sub-ind" id="sortInd_rarity">↕</span>
                </span>
              </div>
            </th>
            <th>검토 내용 요약 & 선발 / 중복 사유 (유사도 %)</th>
          </tr>
        </thead>
        <tbody>
          {render_top20_rows()}
        </tbody>
      </table>
    </div>

    <!-- Cart Action Toolbar (Bottom) -->
    <div class="cart-action-toolbar mt-3" id="cartToolbarBottom">
      <div class="cart-left-controls">
        <button type="button" class="cart-ctrl-btn" onclick="toggleSelectAllCart(true)">☑ 전체 선택</button>
        <button type="button" class="cart-ctrl-btn active-gold" onclick="selectRecommended10()">🎯 추천 10선만 선택</button>
        <button type="button" class="cart-ctrl-btn" onclick="clearCartSelection()">☐ 선택 해제</button>
      </div>
      <div class="cart-right-controls">
        <div class="cart-calc-box">
          <span class="calc-label">선택 항목:</span>
          <strong id="selectedItemsCountBottom" class="calc-count">0</strong>개
          <span class="calc-sep">|</span>
          <strong id="selectedTotalPriceAedBottom" class="calc-aed">0.0</strong> AED 
          <span class="calc-krw">(약 <strong id="selectedTotalPriceKrwBottom">0</strong>원)</span>
        </div>
        <button type="button" class="cart-action-btn btn-add" onclick="saveSelectedToCart()">🛒 장바구니 담기</button>
        <button type="button" class="cart-action-btn btn-view" onclick="openCartPage()">📋 장바구니 보기 (<span class="cart-badge-count">0</span>개) ↗</button>
      </div>
    </div>
  </section>

  <!-- ========================================================
       MODAL POPUP DIALOG
       ======================================================== -->
  <div class="modal-backdrop" id="coffeeModalBackdrop" onclick="closeCoffeeModalOnBackdrop(event)">
    <div class="modal-window" id="coffeeModalWindow">
      <button type="button" class="modal-close-btn" onclick="closeCoffeeModal()" title="닫기 (ESC)">✕</button>

      <!-- Modal Header Tags -->
      <div class="m-header-tags" id="mHeaderTags"></div>

      <!-- Modal Title -->
      <h2 class="m-title" id="mTitle"></h2>

      <!-- Modal Score Grid -->
      <div class="m-score-grid">
        <div class="m-score-box">
          <div class="s-label">종합 총점</div>
          <div class="s-val tot" id="mScoreTotal"></div>
        </div>
        <div class="m-score-box">
          <div class="s-label">맛 평가 (50점)</div>
          <div class="s-val taste" id="mScoreTaste"></div>
        </div>
        <div class="m-score-box">
          <div class="s-label">가격 합리성 (30점)</div>
          <div class="s-val price" id="mScorePrice"></div>
        </div>
        <div class="m-score-box">
          <div class="s-label">한국 희소성 (20점)</div>
          <div class="s-val rarity" id="mScoreRarity"></div>
        </div>
      </div>

      <!-- Terroir & Specs Grid -->
      <div class="m-specs-grid" id="mSpecsGrid"></div>

      <!-- 7-Item Similarity Analysis Section -->
      <div class="m-section" id="mSimilaritySection">
        <div class="m-section-title">📊 7대 기준 유사도 프로파일 분석 (Similarity Breakdown)</div>
        <div class="m-section-body" id="mSimilarityBody"></div>
      </div>

      <!-- Sensory Notes Section -->
      <div class="m-section">
        <div class="m-section-title">🍓 센서리 테이스팅 노트 (Sensory Profile)</div>
        <div class="m-section-body" id="mNotesBody"></div>
      </div>

      <!-- In-depth Expert Analysis -->
      <div class="m-section">
        <div class="m-section-title">🔍 심층 분석 및 평가 (In-depth Review)</div>
        <div class="m-section-body" id="mAnalysisBody"></div>
      </div>

      <!-- Selection / Overlap Reason -->
      <div class="m-section">
        <div class="m-section-title">⚖️ 선발 및 중복 판정 결과</div>
        <div class="m-section-body" id="mOverlapBody"></div>
      </div>

      <!-- Brewing Recipe Guide -->
      <div class="m-section">
        <div class="m-section-title">🫖 추천 브루잉 가이드 (Brewing Guide)</div>
        <div class="m-section-body brew-guide-box" id="mBrewGuideBody"></div>
      </div>

      <!-- Actions -->
      <div class="m-actions">
        <button type="button" class="m-btn-close" onclick="closeCoffeeModal()">닫기</button>
        <a href="#" target="_blank" rel="noopener noreferrer" class="m-btn-out" id="mOfficialLinkBtn">
          공식 웹스토어로 바로가기 ↗
        </a>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="cartToast" class="cart-toast"></div>

  <!-- Footer -->
  <footer>
    <p>
      UAE Specialty Coffee Verification Pipeline • Powered by Pure Code Verification Engine (<code>verify_quotes.py</code>)<br>
      GitHub Repository: <a href="https://github.com/holnuwld/coffee" target="_blank">github.com/holnuwld/coffee</a>
    </p>
  </footer>

</div>

<script>
  // Embedded Ranked Dataset (Pure Score Top 20)
  const COFFEES = {embedded_json_str};

  let currentSortKey = 'total';
  let currentSortDir = 'desc';
  let currentFilter = 'all';

  // Theme Management
  function initTheme() {{
    const saved = localStorage.getItem('theme');
    if (saved === 'light') {{
      applyTheme('light');
    }} else {{
      applyTheme('dark');
    }}
  }}

  function applyTheme(theme) {{
    const btn = document.getElementById('themeToggleBtn');
    if (theme === 'light') {{
      document.documentElement.setAttribute('data-theme', 'light');
      if (btn) {{
        btn.innerHTML = '<span class="theme-icon">🌙</span><span class="theme-label">다크 모드</span>';
        btn.setAttribute('title', '다크 모드로 전환하기');
      }}
    }} else {{
      document.documentElement.removeAttribute('data-theme');
      if (btn) {{
        btn.innerHTML = '<span class="theme-icon">☀️</span><span class="theme-label">브라이트 모드</span>';
        btn.setAttribute('title', '브라이트 모드로 전환하기');
      }}
    }}
  }}

  function toggleTheme() {{
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const nextTheme = isLight ? 'dark' : 'light';
    localStorage.setItem('theme', nextTheme);
    applyTheme(nextTheme);
  }}

  function initPage() {{
    initTheme();
    updateCartCountBadge();
    selectRecommended10();
  }}

  function sortTableByScore(key) {{
    if (currentSortKey === key) {{
      currentSortDir = (currentSortDir === 'desc') ? 'asc' : 'desc';
    }} else {{
      currentSortKey = key;
      currentSortDir = 'desc';
    }}

    const keys = ['total', 'taste', 'price', 'rarity'];
    keys.forEach(k => {{
      const el = document.getElementById('sortTrigger_' + k);
      const ind = document.getElementById('sortInd_' + k);
      if (k === currentSortKey) {{
        if (el) el.classList.add('active-sort');
        if (ind) {{
          ind.textContent = (currentSortDir === 'desc') ? '▼' : '▲';
          ind.style.color = 'var(--accent-gold)';
        }}
      }} else {{
        if (el) el.classList.remove('active-sort');
        if (ind) {{
          ind.textContent = '↕';
          ind.style.color = '';
        }}
      }}
    }});

    const tbody = document.querySelector('#top20Table tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {{
      const valA = parseFloat(a.getAttribute('data-' + key) || 0);
      const valB = parseFloat(b.getAttribute('data-' + key) || 0);
      
      let diff = (currentSortDir === 'desc') ? (valB - valA) : (valA - valB);
      if (diff !== 0) return diff;

      // Secondary sort: total score desc
      const totA = parseFloat(a.getAttribute('data-total') || 0);
      const totB = parseFloat(b.getAttribute('data-total') || 0);
      if (totA !== totB) return totB - totA;

      // Tertiary sort: original rank asc
      const rankA = parseInt(a.getAttribute('data-rank') || 0);
      const rankB = parseInt(b.getAttribute('data-rank') || 0);
      return rankA - rankB;
    }});

    rows.forEach(r => tbody.appendChild(r));
    applyFilter(currentFilter);
    updateCartToolbarState();
  }}

  function filterRanked(type, btn) {{
    currentFilter = type;
    document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    applyFilter(type);
  }}

  function applyFilter(type) {{
    const rows = document.querySelectorAll('#top20Table tbody tr');
    rows.forEach(row => {{
      const st = row.getAttribute('data-status');
      if (type === 'all') {{
        row.style.display = '';
      }} else if (type === 'active') {{
        row.style.display = (st === 'active') ? '' : 'none';
      }} else if (type === 'overlap') {{
        row.style.display = (st === 'overlap') ? '' : 'none';
      }}
    }});
  }}

  /* ========================================================
     CART MANAGEMENT FUNCTIONS
     ======================================================== */
  function toggleSelectAllCart(checked) {{
    const boxes = document.querySelectorAll('.cart-row-checkbox');
    boxes.forEach(b => {{
      // Only select visible rows if filtered
      const tr = b.closest('tr');
      if (tr && tr.style.display !== 'none') {{
        b.checked = checked;
      }}
    }});
    const masterBox = document.getElementById('selectAllCheckbox');
    if (masterBox) masterBox.checked = checked;
    updateCartToolbarState();
  }}

  function selectRecommended10() {{
    const boxes = document.querySelectorAll('.cart-row-checkbox');
    boxes.forEach(b => {{
      const isAct = b.getAttribute('data-is-active') === '1';
      b.checked = isAct;
    }});
    updateCartToolbarState();
  }}

  function clearCartSelection() {{
    const boxes = document.querySelectorAll('.cart-row-checkbox');
    boxes.forEach(b => b.checked = false);
    const masterBox = document.getElementById('selectAllCheckbox');
    if (masterBox) masterBox.checked = false;
    updateCartToolbarState();
  }}

  function updateCartToolbarState() {{
    const boxes = document.querySelectorAll('.cart-row-checkbox:checked');
    let totalCount = boxes.length;
    let totalAed = 0;
    let totalKrw = 0;

    boxes.forEach(b => {{
      totalAed += parseFloat(b.getAttribute('data-price-aed') || 0);
      totalKrw += parseInt(b.getAttribute('data-price-krw') || 0);
    }});

    // Update Top toolbar
    document.getElementById('selectedItemsCountTop').textContent = totalCount;
    document.getElementById('selectedTotalPriceAedTop').textContent = totalAed.toFixed(1);
    document.getElementById('selectedTotalPriceKrwTop').textContent = totalKrw.toLocaleString();

    // Update Bottom toolbar
    document.getElementById('selectedItemsCountBottom').textContent = totalCount;
    document.getElementById('selectedTotalPriceAedBottom').textContent = totalAed.toFixed(1);
    document.getElementById('selectedTotalPriceKrwBottom').textContent = totalKrw.toLocaleString();
  }}

  function getSelectedCoffees() {{
    const boxes = document.querySelectorAll('.cart-row-checkbox:checked');
    const selected = [];
    boxes.forEach(b => {{
      const idx = parseInt(b.getAttribute('data-idx'));
      if (COFFEES[idx]) {{
        selected.push(COFFEES[idx]);
      }}
    }});
    return selected;
  }}

  function saveSelectedToCart() {{
    const items = getSelectedCoffees();
    if (!items.length) {{
      showToast('⚠️ 선택된 커피가 없습니다. 체크박스를 선택해주세요.');
      return;
    }}
    try {{
      localStorage.setItem('coffee_cart', JSON.stringify(items));
      updateCartCountBadge();
      showToast(`🛒 ${{items.length}}개의 원두가 장바구니에 담겼습니다! [장바구니 보기]를 눌러 구매 발주서를 확인하세요.`);
    }} catch (e) {{
      console.error(e);
      showToast('장바구니 저장 중 오류가 발생했습니다.');
    }}
  }}

  function updateCartCountBadge() {{
    let count = 0;
    try {{
      const stored = localStorage.getItem('coffee_cart');
      if (stored) {{
        const arr = JSON.parse(stored);
        count = arr.length;
      }}
    }} catch (e) {{
      console.error(e);
    }}
    document.querySelectorAll('.cart-badge-count').forEach(el => {{
      el.textContent = count;
    }});
  }}

  function openCartPage() {{
    const items = getSelectedCoffees();
    if (items.length > 0) {{
      // Automatically save selected items before opening
      try {{
        localStorage.setItem('coffee_cart', JSON.stringify(items));
      }} catch (e) {{}}
    }}
    window.location.href = 'cart.html';
  }}

  function showToast(msg) {{
    const toast = document.getElementById('cartToast');
    toast.textContent = msg;
    toast.style.display = 'flex';
    setTimeout(() => {{
      toast.style.display = 'none';
    }}, 3500);
  }}

  /* ========================================================
     MODAL FUNCTIONS
     ======================================================== */
  function openCoffeeModal(idx) {{
    const c = COFFEES[idx];
    if (!c) return;

    const isAct = c.is_active;
    const rev = c.detailed_review || {{}};

    // Header Tags
    const tagsContainer = document.getElementById('mHeaderTags');
    const pickBadge = isAct 
      ? `<span class="m-rank-badge active-rank">★ 최종 추천 10선 (Pick #${{c.active_pick_num}})</span>`
      : `<span class="m-rank-badge dimmed-rank">🚫 중복 제외 (순위권 음영)</span>`;
    const roasteryTag = `<span class="roastery-tag ${{c.roastery.includes('Archers') ? 'archers-badge' : 'espressolab-badge'}}">${{c.roastery_badge}}</span>`;
    const rankNumBadge = `<span style="font-size:12px; color:var(--text-muted); font-family:monospace; margin-left:4px;">전체 순위: ${{c.rank}}위 / 131개</span>`;
    tagsContainer.innerHTML = pickBadge + roasteryTag + rankNumBadge;

    // Title
    document.getElementById('mTitle').textContent = c.title;

    // Scores
    document.getElementById('mScoreTotal').innerHTML = `${{c.score_total}}<span style="font-size:12px; color:var(--text-muted)">/100</span>`;
    document.getElementById('mScoreTaste').innerHTML = `${{c.score_taste}}<span style="font-size:12px; color:var(--text-muted)">/50</span>`;
    document.getElementById('mScorePrice').innerHTML = `${{c.score_price}}<span style="font-size:12px; color:var(--text-muted)">/30</span>`;
    document.getElementById('mScoreRarity').innerHTML = `${{c.score_rarity}}<span style="font-size:12px; color:var(--text-muted)">/20</span>`;

    // Specs Grid
    const specsHtml = `
      <div class="spec-row"><span class="spec-k">국가 (Country)</span><span class="spec-v">${{c.country || 'N/A'}}</span></div>
      <div class="spec-row"><span class="spec-k">농장 / 스테이션</span><span class="spec-v">${{c.farm || 'N/A'}}</span></div>
      <div class="spec-row"><span class="spec-k">프로듀서 (농장주)</span><span class="spec-v">${{c.producer || 'N/A'}}</span></div>
      <div class="spec-row"><span class="spec-k">품종 (Variety)</span><span class="spec-v">${{c.variety || 'N/A'}}</span></div>
      <div class="spec-row"><span class="spec-k">가공 방식 (Process)</span><span class="spec-v">${{c.process || 'N/A'}}</span></div>
      <div class="spec-row"><span class="spec-k">재배 고도 (Altitude)</span><span class="spec-v">${{c.altitude || 'N/A'}}</span></div>
      <div class="spec-row"><span class="spec-k">로스팅 프로파일</span><span class="spec-v">${{c.roast || 'Filter'}}</span></div>
      <div class="spec-row"><span class="spec-k">패키지 용량 & 가격</span><span class="spec-v">${{c.price_aed}} AED (약 ${{Number(c.price_krw).toLocaleString()}}원) / 100g</span></div>
    `;
    document.getElementById('mSpecsGrid').innerHTML = specsHtml;

    // 7-Item Similarity Profile
    const simBody = document.getElementById('mSimilarityBody');
    if (c.similar_target_rank) {{
      const dt = c.similar_details || {{}};
      const simColor = isAct ? 'var(--success)' : 'var(--danger)';
      simBody.innerHTML = `
        <div style="margin-bottom:10px; font-weight:700; color:var(--text-primary);">
          🔍 가장 유사한 상위 원두: <span style="color:var(--accent-gold);">#${{c.similar_target_rank}}위 ${{c.similar_target_title}}</span> 
          (종합 유사도: <strong style="color:${{simColor}};">${{c.max_prior_sim}}%</strong>)
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:8px; font-size:12.5px; background:var(--modal-score-bg); padding:12px; border-radius:8px; border:1px solid var(--border);">
          <div>🌍 지역 (14.3%): <strong>${{dt.region || 0}}%</strong></div>
          <div>🏡 농장 (14.3%): <strong>${{dt.farm || 0}}%</strong></div>
          <div>👨‍🌾 프로듀서 (14.3%): <strong>${{dt.producer || 0}}%</strong></div>
          <div>🍓 컵노트 (14.3%): <strong>${{dt.notes || 0}}%</strong> <span style="font-size:11px; color:var(--text-muted);">(자카드 ${{dt.notes_jaccard || 0}}%)</span></div>
          <div>⚙️ 프로세스 (14.3%): <strong>${{dt.process || 0}}%</strong></div>
          <div>🔥 배전도 (14.3%): <strong>14.3%</strong></div>
          <div>⛰️ 고도 (14.3%): <strong>${{dt.altitude || 0}}%</strong></div>
        </div>
        <div style="margin-top:8px; font-size:12px; color:var(--text-secondary);">
          ${{isAct 
            ? '💡 <strong>선발 근거:</strong> 동일 농장이더라도 컵노트가 상이하거나 독자적인 프로세스/테루아를 지녀 최종 10선으로 당당히 선발되었습니다.' 
            : '💡 <strong>음영 근거:</strong> 상위 랏과 7대 항목 전반에서 높은 유사도를 보여, 맛의 다양성 확보를 위해 음영 처리되었습니다.'}}
        </div>
      `;
    }} else {{
      simBody.innerHTML = `
        <div style="font-weight:700; color:var(--accent-gold);">★ 전체 1위 기준 원두 (비교 대조군 없음)</div>
        <div style="font-size:12.5px; color:var(--text-secondary); margin-top:4px;">
          최상위 94점을 획득한 에티오피아 사마 워시드로, 모든 후속 원두의 향미 및 테루아 평가 기준점이 됩니다.
        </div>
      `;
    }}

    // Tasting Notes
    document.getElementById('mNotesBody').innerHTML = `
      <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:6px;">✨ ${{c.notes || 'N/A'}}</div>
      <div style="font-size:12px; color:var(--text-muted);">향미 분류: ${{c.flavor_category || 'Specialty Coffee'}}</div>
    `;

    // Analysis Body
    document.getElementById('mAnalysisBody').innerHTML = `
      <div style="margin-bottom:10px;"><strong>☕ 맛 & 센서리 품질:</strong> ${{rev.taste_analysis || c.merit || '품질 우수'}}</div>
      <div style="margin-bottom:10px;"><strong>💰 가격 & 가성비 분석:</strong> ${{rev.price_analysis || '현지 구매 가격 메리트 우수'}}</div>
      <div><strong>🇰🇷 국내 수입 & 희소성:</strong> ${{rev.rarity_analysis || c.korea_shop || '국내 미수입'}}</div>
    `;

    // Overlap Body
    const overlapStyle = isAct ? 'color:var(--success)' : 'color:#ff7b72';
    document.getElementById('mOverlapBody').innerHTML = `
      <div style="font-weight:700; font-size:14px; margin-bottom:6px; ${{overlapStyle}}">${{c.overlap_note}}</div>
      <div style="color:var(--text-secondary); font-size:13px;">${{rev.selection_reason || ''}}</div>
    `;

    // Brew Guide Body
    document.getElementById('mBrewGuideBody').innerHTML = `
      <div style="font-weight:600;">💧 권장 추출 레시피:</div>
      <div style="margin-top:4px;">${{rev.brewing_guide || 'Hario V60 / 92~94℃ / 1:15~16 비율 추천'}}</div>
    `;

    // Link
    const linkBtn = document.getElementById('mOfficialLinkBtn');
    linkBtn.href = c.source_url;
    linkBtn.textContent = `${{c.roastery}} 공식 판매 페이지 열기 ↗`;

    // Show
    document.getElementById('coffeeModalBackdrop').classList.add('active');
    document.body.style.overflow = 'hidden';
  }}

  function closeCoffeeModal() {{
    document.getElementById('coffeeModalBackdrop').classList.remove('active');
    document.body.style.overflow = '';
  }}

  function closeCoffeeModalOnBackdrop(e) {{
    if (e.target.id === 'coffeeModalBackdrop') {{
      closeCoffeeModal();
    }}
  }}

  window.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') {{
      closeCoffeeModal();
    }}
  }});

  window.addEventListener('DOMContentLoaded', initPage);
</script>

</body>
</html>
"""

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Generated Updated index.html with Cart System & Similarity: {INDEX_HTML} ({len(content)} bytes)")
