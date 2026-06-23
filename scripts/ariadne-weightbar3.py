#!/usr/bin/env python3
"""ARIADNE 配点バー v3（2026-06-23・ユーザー指示）：
(1) %二重表示バグ修復＝括弧なしラベルで名称抽出が%ごと拾い再付加していた問題を、
    title属性（全文ラベル＝真実）から短ラベルを再計算して是正。
(2) 窮屈解消＝strict比例(flex-basis:0)をやめ flex:N 1 auto（basis=内容幅＋余剰をNで比例配分）
    に変更し各セグメントへ余裕。min-width 床＋nowrap+ellipsis+safe center は維持。冪等・LF保存。"""
import glob, re, sys

SPAN = re.compile(r'<span class="(w[ywxc])" style="flex:(\d+)(?: 1 auto)?"(?: title="([^"]*)")?>([^<]*)</span>')
SPAN_RULE = re.compile(r'\.bc-weight > span\{[^}]*\}')
SPAN_FINAL = ('.bc-weight > span{display:flex; align-items:center; justify-content:safe center; '
  'text-align:center; color:#fff; padding:5px 10px; white-space:nowrap; line-height:1.3; '
  'text-shadow:0 1px 2px rgba(0,0,0,.22); min-width:3.4em; overflow:hidden; text-overflow:ellipsis; '
  'font-family:var(--f-code); letter-spacing:.02em}')

def short(full, flex):
    full = full.strip()
    name_part = re.split(r'[（(]', full, 1)[0].strip()
    name = re.sub(r'\s*約?\s*\d+\s*%\s*$', '', name_part).strip()  # drop trailing % from name
    m = re.search(r'約?\s*\d+\s*%', full)
    pct = m.group(0).replace(' ', '') if m else f'{flex}%'
    return f'{name} {pct}' if name else pct

def fix_span(m):
    cls, flex, title, oldtxt = m.group(1), m.group(2), m.group(3), m.group(4)
    full = title if title else oldtxt
    txt = short(full, flex)
    t = title if title else full
    return f'<span class="{cls}" style="flex:{flex} 1 auto" title="{t}">{txt}</span>'

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    orig = s
    s = SPAN.sub(fix_span, s)
    s = SPAN_RULE.sub(SPAN_FINAL, s)
    if s != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
        return True
    return False

def main():
    targets = sys.argv[1:] or (sorted(glob.glob('outputs/ux/000_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html'])
    n = sum(process(p) for p in targets)
    print(f"[weightbar3] {n}/{len(targets)} updated")

if __name__ == '__main__':
    main()
