#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARIADNE 番号付き問題文の重厚化：番号｜本文の2カラム＋点線区切り＋交互背景＋本文1字下げ。

番号付き段落（<p class="pq">1　… / 2　… / 3　…）を持つ問題だけを対象に、
連続する .pq を <div class="pq-list"> の 2カラム行（.pq-grid ＞ .pq-n / .pq-b）へ再構築する。
末尾の設問文（上記事例…／以下の小問…）は番号「問」。単一段落問題は不変（.pq のまま）。
CSS は marker ブロックを <style> 末尾に注入（冪等）。既存 .problem .pq{text-indent:1em} は温存（A30）。

usage: python scripts/ariadne-problem-restyle.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "/* === ARIADNE-PROBLEM-COLUMNS v1 (auto) BEGIN === */"
END = "/* === ARIADNE-PROBLEM-COLUMNS v1 (auto) END === */"

CSS = f"""{BEGIN}
/* 番号付き問題文＝番号｜本文の2カラム＋点線区切り＋交互背景＋1字下げ（重厚化）*/
.problem .pq-list{{margin:8px 0 4px}}
.problem .pq-list .pq-grid{{display:grid; grid-template-columns:2.5em minmax(0,1fr); column-gap:12px; align-items:start; padding:13px 15px 12px; border-top:1px dashed var(--line-2); border-radius:9px}}
.problem .pq-list .pq-grid:first-child{{border-top:none}}
.problem .pq-list .pq-grid:nth-child(even){{background:var(--sheet)}}
.problem .pq-list .pq-n{{justify-self:center; display:flex; align-items:center; justify-content:center; width:1.9em; height:1.9em; margin-top:.15em; border-radius:50%; background:linear-gradient(180deg,var(--shu-line),var(--shu-deep)); color:#fff; font-family:var(--f-soft); font-weight:800; font-size:.82em; text-indent:0 !important; letter-spacing:0; box-shadow:0 2px 6px rgba(120,50,50,.24)}}
.problem .pq-list .pq-n.pq-q{{width:auto; height:auto; padding:.28em .7em; border-radius:999px; font-size:.76em; letter-spacing:.04em}}
.problem .pq-list .pq-n:empty{{background:none; box-shadow:none}}
.problem .pq-list .pq-b{{min-width:0; text-indent:1em; line-height:2.05; color:#322b34}}
.problem .pq-list .pq-b:last-child{{margin-bottom:0}}
{END}"""

PQ_BLOCK = re.compile(r'(?:<p class="pq">.*?</p>\s*)+', re.S)
PQ_ONE = re.compile(r'<p class="pq">(.*?)</p>', re.S)
NUM = re.compile(r'^\s*([0-9０-９]{1,2})[　.．\s]\s*(.*)$', re.S)
DIRECTIVE = re.compile(r'^\s*(?:<b>)?\s*(?:上記|以上|以下|次の|問\b)')

def split_num(inner):
    m = NUM.match(inner)
    if m:
        return m.group(1).strip(), m.group(2), False
    if DIRECTIVE.match(inner):
        return "問", inner, True
    return "", inner, False

def convert_block(block):
    inners = PQ_ONE.findall(block)
    parsed = [split_num(i) for i in inners]
    numbered = sum(1 for n, _, q in parsed if n and not q)
    if numbered < 2:
        return block, 0  # 番号付きが2未満＝対象外
    rows = []
    for n, body, is_q in parsed:
        ncls = ' pq-q' if is_q else ''
        rows.append(f'<div class="pq-grid"><span class="pq-n{ncls}">{n}</span><span class="pq-b">{body.strip()}</span></div>')
    return '<div class="pq-list">\n' + '\n'.join(rows) + '\n</div>\n', len(rows)

def transform_body(html):
    if 'class="pq-list"' in html:
        return html, 0  # 既に変換済（冪等）
    total = 0
    def rep(m):
        nonlocal total
        new, n = convert_block(m.group(0))
        total += n if new != m.group(0) else 0
        return new
    return PQ_BLOCK.sub(rep, html), total

def inject_css(html):
    if BEGIN in html and END in html:
        return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: CSS, html, flags=re.S)
    i = html.rfind("</style>")
    return html if i < 0 else html[:i] + CSS + "\n" + html[i:]

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    body, nrows = transform_body(raw)
    new = inject_css(body)
    changed = new != raw
    if changed and apply:
        Path(path).write_bytes(new.encode("utf-8"))
    return changed, nrows

def main():
    apply = "--apply" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        files = [str(ROOT / "canonical/ARIADNE.html")]
        files += sorted(glob.glob(str(ROOT / "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"), recursive=True))
    ch = 0
    for f in files:
        if not Path(f).exists():
            continue
        c, nr = process(f, apply)
        ch += 1 if c else 0
        if c:
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}  {nr} rows" + ("" if nr else " (CSS only)"))
    print(f"\n{ch} files {'updated' if apply else 'would change'} ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
