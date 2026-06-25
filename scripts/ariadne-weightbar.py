#!/usr/bin/env python3
"""ARIADNE 配点バー再設計（2026-06-23）：細いセグメントに長ラベルを詰めると
縦に潰れる/見切れる構造欠陥を解消。バー内は『％のみ』（必ず収まる）、フルラベルは
直下のスウォッチ凡例 .bc-legend へ移す。比率(flex)は保持＝視覚的な重みは不変。
冪等・LF保存。span class=wy/wx/wc/ww → legend l y/x/c/w。"""
import glob, re, sys

CSS_OLD = '.bc-weight > span{display:flex; align-items:center; justify-content:center; text-align:center; color:#fff; padding:3px 5px; white-space:normal; line-height:1.2; word-break:break-word; text-shadow:0 1px 2px rgba(0,0,0,.18); min-width:2.7em; overflow:hidden}'
CSS_NEW = ('.bc-weight > span{display:flex; align-items:center; justify-content:center; text-align:center; color:#fff; padding:3px 4px; white-space:nowrap; line-height:1.2; text-shadow:0 1px 2px rgba(0,0,0,.18); min-width:2.3em; overflow:hidden; font-family:var(--f-code); letter-spacing:.02em}\n'
           '.bc-legend{display:flex; flex-direction:column; gap:5px; margin:9px 0 0}\n'
           '.bc-legend > span{display:flex; align-items:flex-start; gap:8px; font-size:.82rem; line-height:1.5; color:var(--ink)}\n'
           '.bc-legend > span::before{content:""; flex:0 0 auto; width:14px; height:14px; border-radius:4px; margin-top:2px; box-shadow:0 1px 2px rgba(80,60,80,.2)}\n'
           '.bc-legend .ly::before{background:linear-gradient(135deg,var(--shu),var(--shu-deep))}\n'
           '.bc-legend .lx::before{background:linear-gradient(135deg,var(--ai),var(--ai-deep))}\n'
           '.bc-legend .lc::before{background:linear-gradient(135deg,var(--gd),var(--gd-deep))}\n'
           '.bc-legend .lw::before{background:linear-gradient(135deg,var(--li),var(--li-deep))}')

CLS2LEG = {'wy':'ly','wx':'lx','wc':'lc','ww':'lw'}
SPAN_RE = re.compile(r'<span class="(w[ywxc])"\s+style="flex:(\d+)">(.*?)</span>', re.S)
BAR_RE = re.compile(r'<div class="bc-weight">(.*?)</div>', re.S)

def pct_of(label, flex):
    m = re.search(r'(\d+)\s*%', label)
    return (m.group(1) if m else flex) + '%'

def rebuild_bar(m):
    inner = m.group(1)
    spans = SPAN_RE.findall(inner)
    if not spans:
        return m.group(0)  # leave untouched if unparseable
    # detect indentation from original inner (leading spaces of first span line)
    bar_spans = []
    leg_spans = []
    for cls, flex, label in spans:
        label = label.strip()
        pct = pct_of(label, flex)
        bar_spans.append(f'          <span class="{cls}" style="flex:{flex}">{pct}</span>')
        leg_spans.append(f'          <span class="{CLS2LEG[cls]}">{label}</span>')
    bar = '<div class="bc-weight">\n' + '\n'.join(bar_spans) + '\n        </div>\n' \
          + '        <div class="bc-legend">\n' + '\n'.join(leg_spans) + '\n        </div>'
    return bar

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    orig = s
    if 'bc-legend' in s:               # idempotent
        return False
    # CSS
    if CSS_OLD in s:
        s = s.replace(CSS_OLD, CSS_NEW)
    # HTML bars
    s = BAR_RE.sub(rebuild_bar, s)
    if s != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
        return True
    return False

def main():
    targets = sys.argv[1:] or (sorted(glob.glob('outputs/ux/001_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html'])
    n = 0
    for p in targets:
        if process(p):
            n += 1; print(f"  rebuilt {p}")
    print(f"[weightbar] {n}/{len(targets)} updated")

if __name__ == '__main__':
    main()
