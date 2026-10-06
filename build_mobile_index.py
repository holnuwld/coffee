import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('top_20_curation.json', 'r', encoding='utf-8') as f:
    top_20 = json.load(f)

# Sort by rank initially
top_20.sort(key=lambda x: x['rank'])

html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>UAE 2대 명문 스페셜티 커피 100g 통합 큐레이션 (모바일 퀵 가이드)</title>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
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
    --bg-main: #0a0e17;
    --bg-card: #131a26;
    --bg-inner: #192233;
    --border-color: #222e42;
    --border-light: #2d3d57;
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
    --safe-bottom: env(safe-area-inset-bottom, 16px);
  }}

  [data-theme="light"] {{
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --bg-inner: #f1f5f9;
    --border-color: #e2e8f0;
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
  }}

  /* Mobile Light Theme Adjustments */
  [data-theme="light"] .m-header {{
    background: rgba(255, 255, 255, 0.95);
    border-bottom-color: #e2e8f0;
  }}
  [data-theme="light"] .m-brand-title {{
    color: #0f172a;
  }}
  [data-theme="light"] .m-top-btn {{
    background: #f1f5f9;
    border-color: #cbd5e1;
    color: #0f172a;
  }}
  [data-theme="light"] .m-hero {{
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-bottom-color: #e2e8f0;
  }}
  [data-theme="light"] .m-hero-title {{
    background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  [data-theme="light"] .m-stat-pill {{
    background: #f1f5f9;
    border-color: #e2e8f0;
  }}
  [data-theme="light"] .m-roastery-card {{
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  }}
  [data-theme="light"] .m-roastery-title {{
    color: #0f172a;
  }}
  [data-theme="light"] .m-roastery-bullet {{
    color: #475569;
  }}
  [data-theme="light"] .m-criteria-card {{
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  }}
  [data-theme="light"] .m-guide-banner {{
    background: #eff6ff;
    border-color: #bfdbfe;
    color: #1e3a8a;
  }}
  [data-theme="light"] .m-chip {{
    background: #f1f5f9;
    border-color: #e2e8f0;
    color: #475569;
  }}
  [data-theme="light"] .m-chip.active {{
    background: #d97706;
    color: #ffffff;
    border-color: #d97706;
  }}
  [data-theme="light"] .m-sort-bar {{
    background: #ffffff;
    border-bottom-color: #e2e8f0;
  }}
  [data-theme="light"] .m-select {{
    background: #f1f5f9;
    border-color: #cbd5e1;
    color: #0f172a;
  }}
  [data-theme="light"] .btn-select-all {{
    background: #f1f5f9;
    border-color: #cbd5e1;
    color: #0f172a;
  }}
  [data-theme="light"] .m-coffee-card {{
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
  }}
  [data-theme="light"] .m-coffee-card.dimmed {{
    background: #f8fafc;
    border-color: #e2e8f0;
  }}
  [data-theme="light"] .m-coffee-card.checked {{
    border-color: #f59e0b;
    background: #ffffff;
  }}
  [data-theme="light"] .m-coffee-title a {{
    color: #0f172a;
  }}
  [data-theme="light"] .m-notes-box {{
    background: #f8fafc;
    border-color: #e2e8f0;
    color: #334155;
  }}
  [data-theme="light"] .m-toggle-btn {{
    background: #f1f5f9;
    border-color: #e2e8f0;
    color: #475569;
  }}
  [data-theme="light"] .m-toggle-btn.open {{
    background: #e2e8f0;
    color: #0f172a;
  }}
  [data-theme="light"] .m-drawdown-content {{
    background: #f8fafc;
    border-top-color: #e2e8f0;
  }}
  [data-theme="light"] .m-review-box {{
    background: #ffffff;
    border-color: #e2e8f0;
    color: #334155;
  }}
  [data-theme="light"] .m-bottom-cart-bar {{
    background: rgba(255, 255, 255, 0.96);
    border-top-color: #e2e8f0;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
  }}
  [data-theme="light"] .m-cart-count-txt {{
    color: #0f172a;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
  body {{
    background: var(--bg-main);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.5;
    padding-bottom: calc(var(--safe-bottom) + 85px);
    overflow-x: hidden;
  }}

  /* Sticky Top Header */
  .m-header {{
    background: rgba(10, 14, 23, 0.95);
    backdrop-filter: blur(16px);
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .m-brand {{
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--text-primary);
  }}
  .m-brand-badge {{
    background: linear-gradient(135deg, #d29922, #b07d12);
    color: #000;
    font-weight: 800;
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 4px;
    letter-spacing: 0.5px;
  }}
  .m-brand-title {{
    font-size: 15px;
    font-weight: 800;
    color: #fff;
  }}
  .m-top-actions {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .m-top-btn {{
    font-size: 11.5px;
    padding: 6px 10px;
    border-radius: 6px;
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}
  .m-top-btn.cart-link {{
    background: var(--accent-glow);
    border-color: var(--accent);
    color: var(--accent-gold);
    font-weight: 700;
  }}

  /* Mobile Hero Summary */
  .m-hero {{
    padding: 20px 16px 16px 16px;
    background: linear-gradient(180deg, #131a26 0%, #0a0e17 100%);
    border-bottom: 1px solid var(--border-color);
  }}
  .m-hero-badge {{
    display: inline-block;
    background: var(--accent-glow);
    border: 1px solid var(--accent);
    color: var(--accent-gold);
    font-size: 11px;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 999px;
    margin-bottom: 8px;
  }}
  .m-hero-title {{
    font-size: 21px;
    font-weight: 800;
    line-height: 1.35;
    margin-bottom: 6px;
    background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .m-hero-desc {{
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 14px;
  }}

  /* 3 Criteria Mini Legend */
  .m-criteria-chips {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    margin-bottom: 14px;
  }}
  .m-crit-chip {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 6px;
    text-align: center;
  }}
  .m-crit-title {{
    font-size: 11px;
    font-weight: 700;
    color: var(--accent-gold);
    margin-bottom: 2px;
  }}
  .m-crit-val {{
    font-size: 12px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: #fff;
  }}

  /* Search & Filter Bar */
  .m-sticky-controls {{
    position: sticky;
    top: 53px;
    z-index: 90;
    background: rgba(10, 14, 23, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-color);
    padding: 10px 16px;
  }}
  .m-search-wrap {{
    position: relative;
    margin-bottom: 8px;
  }}
  .m-search-input {{
    width: 100%;
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 12px 8px 34px;
    color: var(--text-primary);
    font-size: 13.5px;
    outline: none;
  }}
  .m-search-input:focus {{
    border-color: var(--accent);
  }}
  .m-search-icon {{
    position: absolute;
    left: 10px;
    top: 9px;
    font-size: 13px;
    color: var(--text-muted);
  }}
  .m-chips {{
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding-bottom: 4px;
    scrollbar-width: none;
  }}
  .m-chips::-webkit-scrollbar {{ display: none; }}
  .m-chip {{
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .m-chip.active {{
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
    font-weight: 700;
  }}

  /* Sort & Select Control Row */
  .m-ctrl-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px 4px 16px;
    font-size: 12px;
    color: var(--text-muted);
  }}
  .m-sort-select {{
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11.5px;
    outline: none;
  }}
  .btn-select-all {{
    background: none;
    border: none;
    color: var(--blue);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    padding: 4px 0;
  }}

  /* Cards List */
  .m-cards-list {{
    padding: 10px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  /* Single Coffee Card */
  .m-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px;
    position: relative;
    transition: border-color 0.15s ease;
  }}
  .m-card.active-pick {{
    border-color: rgba(210, 153, 34, 0.45);
    background: linear-gradient(180deg, rgba(19, 26, 38, 0.95) 0%, rgba(13, 18, 27, 0.95) 100%);
  }}
  .m-card.dimmed-pick {{
    opacity: 0.68;
    background: rgba(14, 19, 28, 0.75);
    border-style: dashed;
  }}
  .m-card.checked {{
    border-color: var(--accent-gold);
    box-shadow: 0 0 0 1px var(--accent-gold);
  }}

  /* Card Top Row */
  .m-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
  }}
  .m-card-header-left {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .m-checkbox-label {{
    display: inline-flex;
    align-items: center;
    cursor: pointer;
  }}
  .m-checkbox {{
    width: 19px;
    height: 19px;
    accent-color: var(--accent-gold);
    cursor: pointer;
  }}
  .m-rank-badge {{
    font-size: 11px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
  }}
  .m-rank-active {{
    background: var(--accent-glow);
    color: var(--accent-gold);
    border: 1px solid var(--accent);
  }}
  .m-rank-dimmed {{
    background: rgba(110, 118, 129, 0.2);
    color: var(--text-muted);
    border: 1px solid var(--border-color);
  }}
  .m-roastery-badge {{
    font-size: 10.5px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
  }}
  .badge-archers {{ background: rgba(56, 139, 253, 0.15); color: var(--blue); border: 1px solid rgba(56, 139, 253, 0.3); }}
  .badge-espressolab {{ background: rgba(240, 180, 41, 0.15); color: var(--accent-gold); border: 1px solid rgba(240, 180, 41, 0.3); }}

  /* Score Badge Top Right */
  .m-score-box {{
    text-align: right;
    flex-shrink: 0;
  }}
  .m-score-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 800;
    color: var(--accent-gold);
    line-height: 1;
  }}
  .m-score-sub {{
    font-size: 9.5px;
    color: var(--text-muted);
    margin-top: 2px;
  }}

  /* Coffee Title */
  .m-coffee-title {{
    font-size: 16px;
    font-weight: 800;
    color: #fff;
    line-height: 1.35;
    margin-bottom: 8px;
    word-break: keep-all;
  }}
  .m-coffee-title a {{
    color: inherit;
    text-decoration: none;
    transition: color 0.15s ease;
  }}
  .m-coffee-title a:hover {{
    color: var(--blue);
  }}
  .m-out-link {{
    font-size: 12px;
    color: var(--blue);
    vertical-align: middle;
  }}

  /* Price & Spec Tag Row */
  .m-price-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-color);
  }}
  .m-price-left {{
    display: flex;
    align-items: baseline;
    gap: 6px;
  }}
  .m-price-aed {{
    font-size: 17px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: var(--blue);
  }}
  .m-price-krw {{
    font-size: 12px;
    color: var(--text-secondary);
  }}
  .m-weight-pill {{
    font-size: 10.5px;
    background: var(--bg-inner);
    border: 1px solid var(--border-color);
    padding: 2px 7px;
    border-radius: 999px;
    color: var(--text-muted);
  }}

  /* Quick Spec Chips */
  .m-quick-specs {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 10px;
  }}
  .m-spec-chip {{
    font-size: 11px;
    background: var(--bg-inner);
    color: var(--text-secondary);
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid rgba(46, 62, 87, 0.6);
  }}
  .m-spec-chip.variety {{ color: var(--purple); background: rgba(188, 140, 255, 0.1); border-color: rgba(188, 140, 255, 0.25); }}
  .m-spec-chip.process {{ color: var(--blue); background: rgba(88, 166, 255, 0.1); border-color: rgba(88, 166, 255, 0.25); }}

  /* Notes Box */
  .m-notes-box {{
    background: rgba(240, 180, 41, 0.08);
    border: 1px solid rgba(240, 180, 41, 0.25);
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 12.5px;
    color: #fce881;
    font-weight: 600;
    margin-bottom: 10px;
    line-height: 1.45;
  }}

  /* Similarity Bar Preview */
  .m-sim-preview {{
    font-size: 11.5px;
    background: var(--bg-inner);
    border-radius: 6px;
    padding: 6px 10px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid var(--border-color);
  }}
  .m-sim-text {{
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 70%;
  }}
  .m-sim-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 11.5px;
  }}

  /* Accordion Toggle Button */
  .m-toggle-btn {{
    width: 100%;
    background: rgba(25, 34, 51, 0.7);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    padding: 8px 12px;
    font-size: 12.5px;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .m-toggle-btn:active {{
    background: var(--bg-inner);
  }}
  .m-toggle-icon {{
    font-size: 11px;
    transition: transform 0.2s ease;
  }}
  .m-toggle-btn.open .m-toggle-icon {{
    transform: rotate(180deg);
  }}

  /* Accordion Drawdown Content */
  .m-drawdown-content {{
    display: none;
    padding-top: 14px;
    margin-top: 10px;
    border-top: 1px dashed var(--border-color);
  }}
  .m-drawdown-content.show {{
    display: block;
  }}

  /* Drawdown Sub-sections */
  .m-drawdown-block {{
    margin-bottom: 14px;
  }}
  .m-block-title {{
    font-size: 12px;
    font-weight: 800;
    color: var(--accent-gold);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  /* 4 Scores Mini Grid */
  .m-scores-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    margin-bottom: 12px;
  }}
  .m-sc-item {{
    background: #080c13;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 6px 4px;
    text-align: center;
  }}
  .m-sc-lbl {{ font-size: 10px; color: var(--text-muted); margin-bottom: 2px; }}
  .m-sc-num {{ font-size: 13px; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #fff; }}

  /* Full Specs Grid */
  .m-specs-table {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 6px;
    font-size: 12px;
    background: #080c13;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 12px;
  }}
  .m-spec-row {{
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid rgba(46, 62, 87, 0.35);
    padding-bottom: 4px;
  }}
  .m-spec-row:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .m-spec-k {{ color: var(--text-muted); font-size: 11.5px; }}
  .m-spec-v {{ font-weight: 600; color: #e6edf3; text-align: right; }}

  /* 7-Similarity Grid in Drawdown */
  .m-sim-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    background: #080c13;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 11.5px;
  }}
  .m-sim-item strong {{ color: #fff; font-family: 'JetBrains Mono', monospace; }}

  /* Evaluation Text */
  .m-review-box {{
    background: rgba(10, 14, 23, 0.7);
    border-left: 3px solid var(--blue);
    padding: 10px 12px;
    border-radius: 0 6px 6px 0;
    font-size: 12.5px;
    color: #c9d1d9;
    line-height: 1.55;
    word-break: keep-all;
  }}
  .m-review-box strong {{ color: #fff; }}

  /* Sticky Bottom Cart Bar */
  .m-bottom-cart-bar {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(10, 14, 23, 0.96);
    backdrop-filter: blur(16px);
    border-top: 1px solid var(--border-color);
    padding: 12px 16px;
    padding-bottom: calc(var(--safe-bottom) + 12px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 200;
    box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.5);
  }}
  .m-cart-summary {{
    display: flex;
    flex-direction: column;
  }}
  .m-cart-count-txt {{
    font-size: 12px;
    color: var(--text-secondary);
  }}
  .m-cart-count-txt strong {{
    color: var(--accent-gold);
    font-size: 14px;
    font-family: 'JetBrains Mono', monospace;
  }}
  .m-cart-price-txt {{
    font-size: 15px;
    font-weight: 800;
    color: #fff;
    font-family: 'JetBrains Mono', monospace;
  }}
  .m-cart-price-krw {{
    font-size: 11px;
    color: var(--success);
  }}
  .m-cart-cta-btn {{
    background: linear-gradient(135deg, #d29922, #b07d12);
    color: #000;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 13.5px;
    font-weight: 800;
    cursor: pointer;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 4px 12px rgba(210, 153, 34, 0.35);
  }}

  /* Toast Notification */
  .m-toast {{
    position: fixed;
    top: 65px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(240, 180, 41, 0.95);
    color: #000;
    font-weight: 700;
    font-size: 12.5px;
    padding: 8px 18px;
    border-radius: 999px;
    z-index: 300;
    display: none;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
  }}
</style>
</head>
<body>

<!-- Sticky Top Header -->
<header class="m-header">
  <a href="index.html" class="m-brand">
    <span class="m-brand-badge">TOP 20</span>
    <span class="m-brand-title">UAE 스페셜티 큐레이션</span>
  </a>
  <div class="m-top-actions">
    <button id="themeToggleBtn" class="m-top-btn" onclick="toggleTheme()" title="화면 테마 변경 (브라이트 / 다크)" style="cursor:pointer; padding:6px 9px;">
      <span id="themeIcon">☀️</span>
    </button>
    <a href="index.html" class="m-top-btn" title="데스크톱 포털로 이동">🖥️ 데스크톱</a>
    <a href="mobile_cart.html" class="m-top-btn cart-link" title="모바일 발주서 보기">🛒 발주서 <span id="topCartBadge">10</span></a>
  </div>
</header>

<!-- Mobile Hero Summary -->
<section class="m-hero">
  <span class="m-hero-badge">100g 단위 통합 랭킹</span>
  <h1 class="m-hero-title">아처스 &amp; 에소랩 100g 큐레이션</h1>
  <p class="m-hero-desc">
    131종 전수 중 최고 점수 20종 선발. 7대 유사도 프로파일을 거쳐 중복 없는 <strong>실질 엄선 10선</strong>을 추천합니다.
  </p>

  <!-- 3 Criteria Chips -->
  <div class="m-criteria-chips">
    <div class="m-crit-chip">
      <div class="m-crit-title">☕ 맛/테루아</div>
      <div class="m-crit-val">50점 만점</div>
    </div>
    <div class="m-crit-chip">
      <div class="m-crit-title">💰 현지 가성비</div>
      <div class="m-crit-val">30점 만점</div>
    </div>
    <div class="m-crit-chip">
      <div class="m-crit-title">🇰🇷 국내 희소성</div>
      <div class="m-crit-val">20점 만점</div>
    </div>
  </div>
</section>

<!-- Search & Filter Controls -->
<div class="m-sticky-controls">
  <div class="m-search-wrap">
    <span class="m-search-icon">🔍</span>
    <input type="text" id="mSearchInput" class="m-search-input" placeholder="원두명, 농장, 품종, 컵노트 검색..." oninput="handleSearchFilter()">
  </div>
  <div class="m-chips">
    <button class="m-chip active" onclick="setFilter('all', this)">전체 20종</button>
    <button class="m-chip" onclick="setFilter('active', this)">★ 엄선 10선만</button>
    <button class="m-chip" onclick="setFilter('archers', this)">🏹 아처스만</button>
    <button class="m-chip" onclick="setFilter('tel', this)">☕ 에소랩만</button>
    <button class="m-chip" onclick="setFilter('washed', this)">워시드만</button>
    <button class="m-chip" onclick="setFilter('geisha', this)">게이샤만</button>
  </div>
</div>

<!-- Sort & Select Bar -->
<div class="m-ctrl-row">
  <div>
    정렬: 
    <select id="mSortSelect" class="m-sort-select" onchange="handleSortChange()">
      <option value="score">종합점수 높은순</option>
      <option value="taste">맛 점수 높은순</option>
      <option value="price_asc">가격 낮은순</option>
      <option value="rarity">국내 희소성순</option>
    </select>
  </div>
  <button type="button" class="btn-select-all" onclick="toggleSelectAll()">전체 선택/해제</button>
</div>

<!-- Toast -->
<div class="m-toast" id="mToast">장바구니가 갱신되었습니다.</div>

<!-- Coffee Cards Container -->
<main class="m-cards-list" id="mCardsList">
  <!-- Generated via JS -->
</main>

<!-- Fixed Bottom Floating Cart Bar -->
<div class="m-bottom-cart-bar">
  <div class="m-cart-summary">
    <div class="m-cart-count-txt">선택 <strong id="mBottomCount">10</strong>개 / 20종</div>
    <div class="m-cart-price-txt"><span id="mBottomAed">0.0</span> AED</div>
    <div class="m-cart-price-krw">약 <span id="mBottomKrw">0</span>원</div>
  </div>
  <a href="mobile_cart.html" class="m-cart-cta-btn">
    🛒 발주서 보기 ↗
  </a>
</div>

<script>
  const COFFEES = {json.dumps(top_20, ensure_ascii=False)};
  let currentFilter = 'all';
  let currentSort = 'score';
  let checkedHandles = new Set();

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
    const icon = document.getElementById('themeIcon');
    if (theme === 'light') {{
      document.documentElement.setAttribute('data-theme', 'light');
      if (icon) icon.textContent = '🌙';
    }} else {{
      document.documentElement.removeAttribute('data-theme');
      if (icon) icon.textContent = '☀️';
    }}
  }}

  function toggleTheme() {{
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const nextTheme = isLight ? 'dark' : 'light';
    localStorage.setItem('theme', nextTheme);
    applyTheme(nextTheme);
  }}

  function initApp() {{
    initTheme();
    // 1. Try to load checked state from localStorage
    try {{
      const stored = localStorage.getItem('coffee_cart');
      if (stored) {{
        const items = JSON.parse(stored);
        if (items && items.length) {{
          items.forEach(c => checkedHandles.add(c.handle));
        }}
      }}
    }} catch(e) {{}}

    // 2. Default: If no storage, pre-select the 10 active picks
    if (checkedHandles.size === 0) {{
      COFFEES.forEach(c => {{
        if (c.is_active) checkedHandles.add(c.handle);
      }});
    }}

    renderCards();
    updateCartBar();
  }}

  function renderCards() {{
    const container = document.getElementById('mCardsList');
    container.innerHTML = '';

    const query = (document.getElementById('mSearchInput').value || '').toLowerCase().trim();

    // Filter
    let filtered = COFFEES.filter(c => {{
      if (currentFilter === 'active' && !c.is_active) return false;
      if (currentFilter === 'archers' && !c.roastery.includes('Archers')) return false;
      if (currentFilter === 'tel' && c.roastery.includes('Archers')) return false;
      if (currentFilter === 'washed' && !String(c.process).toLowerCase().includes('washed')) return false;
      if (currentFilter === 'geisha' && !String(c.variety).toLowerCase().includes('geisha')) return false;

      if (query) {{
        const searchPool = (c.title + ' ' + c.country + ' ' + c.farm + ' ' + c.producer + ' ' + c.variety + ' ' + c.process + ' ' + c.notes).toLowerCase();
        if (!searchPool.includes(query)) return false;
      }}
      return true;
    }});

    // Sort
    filtered.sort((a, b) => {{
      if (currentSort === 'score') return b.score_total - a.score_total;
      if (currentSort === 'taste') return b.score_taste - a.score_taste;
      if (currentSort === 'price_asc') return parseFloat(a.price_aed) - parseFloat(b.price_aed);
      if (currentSort === 'rarity') return b.score_rarity - a.score_rarity;
      return a.rank - b.rank;
    }});

    if (!filtered.length) {{
      container.innerHTML = '<div style="text-align:center; padding:50px 20px; color:var(--text-muted); font-size:14px;">조건에 일치하는 커피가 없습니다.</div>';
      return;
    }}

    filtered.forEach((c, idx) => {{
      const isChecked = checkedHandles.has(c.handle);
      const isAct = c.is_active;
      const rev = c.detailed_review || {{}};
      const dt = c.similar_details || {{}};
      const rBadgeCls = c.roastery.includes('Archers') ? 'badge-archers' : 'badge-espressolab';
      const simColor = isAct ? 'var(--success)' : 'var(--danger)';

      const card = document.createElement('article');
      card.className = `m-card ${{isAct ? 'active-pick' : 'dimmed-pick'}} ${{isChecked ? 'checked' : ''}}`;
      card.id = `card_${{c.handle}}`;

      card.innerHTML = `
        <!-- Top Row: Checkbox, Rank, Roastery, Total Score -->
        <div class="m-card-header">
          <div class="m-card-header-left">
            <label class="m-checkbox-label">
              <input type="checkbox" class="m-checkbox" ${{isChecked ? 'checked' : ''}} onchange="toggleItemCheck('${{c.handle}}', this)">
            </label>
            <span class="m-rank-badge ${{isAct ? 'm-rank-active' : 'm-rank-dimmed'}}">
              ${{isAct ? `★ Pick #${{c.active_pick_num}} (${{c.rank}}위)` : `🚫 ${{c.rank}}위 (음영)`}}
            </span>
            <span class="m-roastery-badge ${{rBadgeCls}}">${{c.roastery_badge}}</span>
          </div>
          <div class="m-score-box">
            <div class="m-score-val">${{c.score_total}}<span style="font-size:11px; color:var(--text-muted)">/100</span></div>
            <div class="m-score-sub">맛${{c.score_taste}}·값${{c.score_price}}·희${{c.score_rarity}}</div>
          </div>
        </div>

        <!-- Coffee Title (Link to roastery official product page) -->
        <h2 class="m-coffee-title">
          <a href="${{c.source_url}}" target="_blank" rel="noopener noreferrer" title="공식 판매처 새창 열기">
            ${{c.title}} <span class="m-out-link">↗</span>
          </a>
        </h2>

        <!-- Price & Weight Row -->
        <div class="m-price-row">
          <div class="m-price-left">
            <span class="m-price-aed">${{parseFloat(c.price_aed).toFixed(1)}} AED</span>
            <span class="m-price-krw">(약 ${{Number(c.price_krw).toLocaleString()}}원)</span>
          </div>
          <span class="m-weight-pill">${{c.weight || '100g'}} • ${{c.roast || 'Filter'}}</span>
        </div>

        <!-- Quick Specs Chips -->
        <div class="m-quick-specs">
          <span class="m-spec-chip">🌍 ${{c.country}}</span>
          <span class="m-spec-chip variety">🌱 ${{c.variety}}</span>
          <span class="m-spec-chip process">⚙️ ${{c.process}}</span>
          <span class="m-spec-chip">⛰️ ${{c.altitude}}</span>
        </div>

        <!-- Sensory Tasting Notes -->
        <div class="m-notes-box">
          ✨ ${{c.notes || 'N/A'}}
        </div>

        <!-- 7-Similarity Preview Line -->
        <div class="m-sim-preview">
          <span class="m-sim-text">
            ${{c.similar_target_rank 
              ? `🔍 상위 #${{c.similar_target_rank}}위와 유사도` 
              : `★ 1위 기준 원두 (비교 대조군 없음)`}}
          </span>
          <span class="m-sim-badge" style="color:${{simColor}};">
            ${{c.similar_target_rank ? `${{c.max_prior_sim}}%` : 'Base'}}
          </span>
        </div>

        <!-- Accordion Drawdown Toggle Button -->
        <button type="button" class="m-toggle-btn" onclick="toggleDrawdown('${{c.handle}}', this)">
          <span>상세 스펙 &amp; 7대 유사도 분석 보기</span>
          <span class="m-toggle-icon">▼</span>
        </button>

        <!-- Accordion Drawdown Content Panel -->
        <div class="m-drawdown-content" id="drawdown_${{c.handle}}">
          <!-- 4 Score Items Breakdown -->
          <div class="m-drawdown-block">
            <div class="m-block-title">📊 3대 평가 항목별 배점 내역</div>
            <div class="m-scores-grid">
              <div class="m-sc-item">
                <div class="m-sc-lbl">종합점수</div>
                <div class="m-sc-num" style="color:var(--accent-gold);">${{c.score_total}}</div>
              </div>
              <div class="m-sc-item">
                <div class="m-sc-lbl">맛/테루아</div>
                <div class="m-sc-num">${{c.score_taste}}/50</div>
              </div>
              <div class="m-sc-item">
                <div class="m-sc-lbl">현지 가성비</div>
                <div class="m-sc-num">${{c.score_price}}/30</div>
              </div>
              <div class="m-sc-item">
                <div class="m-sc-lbl">국내 희소성</div>
                <div class="m-sc-num">${{c.score_rarity}}/20</div>
              </div>
            </div>
          </div>

          <!-- Full Specs Grid -->
          <div class="m-drawdown-block">
            <div class="m-block-title">📋 테루아 &amp; 생산자 상세 스펙</div>
            <div class="m-specs-table">
              <div class="m-spec-row"><span class="m-spec-k">국가 / 지역</span><span class="m-spec-v">${{c.country}} • ${{c.location || 'N/A'}}</span></div>
              <div class="m-spec-row"><span class="m-spec-k">농장 / 스테이션</span><span class="m-spec-v">${{c.farm || 'N/A'}}</span></div>
              <div class="m-spec-row"><span class="m-spec-k">프로듀서(생산자)</span><span class="m-spec-v">${{c.producer || 'N/A'}}</span></div>
              <div class="m-spec-row"><span class="m-spec-k">품종 / 가공</span><span class="m-spec-v">${{c.variety}} (${{c.process}})</span></div>
              <div class="m-spec-row"><span class="m-spec-k">재배 고도</span><span class="m-spec-v">${{c.altitude || 'N/A'}}</span></div>
              <div class="m-spec-row"><span class="m-spec-k">배전도</span><span class="m-spec-v">${{c.roast || 'Filter Light Roast'}}</span></div>
            </div>
          </div>

          <!-- 7-Similarity Profile Breakdown -->
          <div class="m-drawdown-block">
            <div class="m-block-title">🧬 7대 기준 유사도 세부 내역 (각 14.3%)</div>
            ${{c.similar_target_rank ? `
              <div class="m-sim-grid">
                <div class="m-sim-item">🌍 지역: <strong>${{dt.region || 0}}%</strong></div>
                <div class="m-sim-item">🏡 농장: <strong>${{dt.farm || 0}}%</strong></div>
                <div class="m-sim-item">👨‍🌾 프로듀서: <strong>${{dt.producer || 0}}%</strong></div>
                <div class="m-sim-item">🍓 컵노트: <strong>${{dt.notes || 0}}%</strong></div>
                <div class="m-sim-item">⚙️ 프로세스: <strong>${{dt.process || 0}}%</strong></div>
                <div class="m-sim-item">🔥 배전도: <strong>14.3%</strong></div>
                <div class="m-sim-item" style="grid-column: span 2;">⛰️ 재배 고도: <strong>${{dt.altitude || 0}}%</strong></div>
              </div>
              <div style="font-size:11.5px; color:var(--text-secondary); margin-top:6px; line-height:1.45;">
                ${{isAct 
                  ? '💡 <strong>선발 이유:</strong> 동일 농장이더라도 컵노트(향미)가 상이하거나 독자적 프로세스를 갖추어 최종 10선으로 선발되었습니다.' 
                  : '💡 <strong>음영 사유:</strong> 상위 랏과 7대 항목 전반에서 높은 유사도를 보여 맛의 다양성을 위해 음영 처리되었습니다.'}}
              </div>
            ` : `
              <div style="font-size:12px; color:var(--text-secondary); background:#080c13; padding:8px 10px; border-radius:6px; border:1px solid var(--border-color);">
                전체 1위 기준 원두로, 모든 후속 원두의 향미 비교 기준점이 됩니다.
              </div>
            `}}
          </div>

          <!-- Curation Analysis -->
          <div class="m-drawdown-block">
            <div class="m-block-title">💡 큐레이터 심층 심사평</div>
            <div class="m-review-box">
              <strong>☕ 센서리 특징:</strong> ${{rev.taste_analysis || c.merit || '품질 우수'}}<br><br>
              <strong>💰 가성비 분석:</strong> ${{rev.price_analysis || '현지 구매 가격 메리트 우수'}}<br><br>
              <strong>🎯 브루잉 팁:</strong> ${{rev.brewing_tip || '93도 푸어오버 추출 권장'}}
            </div>
          </div>
        </div>
      `;

      container.appendChild(card);
    }});
  }}

  function toggleDrawdown(handle, btn) {{
    const panel = document.getElementById(`drawdown_${{handle}}`);
    if (!panel) return;
    const isOpen = panel.classList.contains('show');
    if (isOpen) {{
      panel.classList.remove('show');
      btn.classList.remove('open');
      btn.querySelector('.m-toggle-icon').textContent = '▼';
    }} else {{
      panel.classList.add('show');
      btn.classList.add('open');
      btn.querySelector('.m-toggle-icon').textContent = '▲';
    }}
  }}

  function toggleItemCheck(handle, cb) {{
    if (cb.checked) {{
      checkedHandles.add(handle);
    }} else {{
      checkedHandles.delete(handle);
    }}
    const card = document.getElementById(`card_${{handle}}`);
    if (card) {{
      if (cb.checked) card.classList.add('checked');
      else card.classList.remove('checked');
    }}
    saveCart();
    updateCartBar();
    showToast(`장바구니 ${{checkedHandles.size}}개 갱신`);
  }}

  function toggleSelectAll() {{
    const allChecked = (checkedHandles.size === COFFEES.length);
    if (allChecked) {{
      checkedHandles.clear();
    }} else {{
      COFFEES.forEach(c => checkedHandles.add(c.handle));
    }}
    renderCards();
    saveCart();
    updateCartBar();
    showToast(allChecked ? '전체 해제 완료' : '전체 20종 선택 완료');
  }}

  function setFilter(filt, btn) {{
    currentFilter = filt;
    document.querySelectorAll('.m-chip').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderCards();
  }}

  function handleSearchFilter() {{
    renderCards();
  }}

  function handleSortChange() {{
    currentSort = document.getElementById('mSortSelect').value;
    renderCards();
  }}

  function updateCartBar() {{
    const selectedItems = COFFEES.filter(c => checkedHandles.has(c.handle));
    let totalAed = 0;
    let totalKrw = 0;

    selectedItems.forEach(c => {{
      const a = parseFloat(c.price_aed || 0);
      totalAed += a;
      totalKrw += parseInt(c.price_krw || Math.round(a * 380));
    }});

    document.getElementById('mBottomCount').textContent = selectedItems.length;
    document.getElementById('topCartBadge').textContent = selectedItems.length;
    document.getElementById('mBottomAed').textContent = totalAed.toFixed(1);
    document.getElementById('mBottomKrw').textContent = totalKrw.toLocaleString();
  }}

  function saveCart() {{
    const selectedItems = COFFEES.filter(c => checkedHandles.has(c.handle));
    try {{
      localStorage.setItem('coffee_cart', JSON.stringify(selectedItems));
    }} catch(e) {{}}
  }}

  function showToast(msg) {{
    const t = document.getElementById('mToast');
    t.textContent = msg;
    t.style.display = 'block';
    setTimeout(() => {{ t.style.display = 'none'; }}, 2200);
  }}

  window.addEventListener('DOMContentLoaded', initApp);
</script>

</body>
</html>
"""

with open('mobile_index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"Generated mobile_index.html successfully ({len(html_template)} bytes)")
