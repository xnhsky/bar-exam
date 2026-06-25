#!/usr/bin/env python3
"""ARIADNE 配点バー：凡例分離を撤回しラベルをバー内へ戻す（2026-06-23・ユーザー指示）。
項目名+％を各バー内に中央配置(justify-content:safe center＝収まれば中央/溢れたら左寄せで…表示)／
flex比率配分／nowrap+overflow:hidden+text-overflow:ellipsis／角丸/白文字/レスポンシブ。
全文は title 属性に温存。直下 .bc-legend は除去。CSS span 規則は regex で最終形へ正規化（冪等）。LF保存。"""
import glob, re, sys

BAR_LEG = re.compile(r'<div class="bc-weight">(.*?)</div>\s*<div class="bc-legend">(.*?)</div>', re.S)
BAR_SPAN = re.compile(r'<span class="(w[ywxc])" style="flex:(\d+)"[^>]*>[^<]*</span>')
LEG_SPAN = re.compile(r'<span class="l[yxcw]">(.*?)</span>', re.S)
SPAN_RULE = re.compile(r'\.bc-weight > span\{[^}]*\}')
LEG_CSS = re.compile(r'\n?\.bc-legend\{.*?\.bc-legend \.lw::before\{[^}]*\}', re.S)

SPAN_FINAL = ('.bc-weight > span{display:flex; align-items:center; justify-content:safe center; '
  'text-align:center; color:#fff; padding:4px 6px; white-space:nowrap; line-height:1.25; '
  'text-shadow:0 1px 2px rgba(0,0,0,.22); min-width:2.4em; overflow:hidden; text-overflow:ellipsis; '
  'font-family:var(--f-code); letter-spacing:.02em}')

def short(label, flex):
    label = label.strip()
    name = re.split(r'[（(]', label, 1)[0].strip()
    m = re.search(r'約?\s*\d+\s*%', label)
    pct = m.group(0).replace(' ', '') if m else f'{flex}%'
    return f'{name} {pct}'

def rebuild(m):
    bars = BAR_SPAN.findall(m.group(1)); legs = LEG_SPAN.findall(m.group(2))
    rows = []
    for i, (cls, flex) in enumerate(bars):
        label = legs[i].strip() if i < len(legs) else ''
        txt = short(label, flex); title = label or txt
        rows.append(f'          <span class="{cls}" style="flex:{flex}" title="{title}">{txt}</span>')
    return '<div class="bc-weight">\n' + '\n'.join(rows) + '\n        </div>'

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    orig = s
    if 'bc-legend' in s:
        s = BAR_LEG.sub(rebuild, s)
        s = LEG_CSS.sub('', s)
    # normalize span rule to final form (idempotent)
    s = SPAN_RULE.sub(SPAN_FINAL, s)
    if s != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
        return True
    return False

def main():
    targets = sys.argv[1:] or (sorted(glob.glob('outputs/ux/001_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html'])
    n = sum(process(p) for p in targets)
    print(f"[weightbar2] {n}/{len(targets)} updated")

if __name__ == '__main__':
    main()
