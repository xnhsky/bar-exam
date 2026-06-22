#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周回ドリルタブ(.self-check-quiz::before)を初期サイズへ戻し、
模範答案の役割バッジ(.model-answer p.role::before)を同サイズに統一する。
規則全体を regex で置換＝現状（narrowed/旧 text-indent:0 等）に依存せず最終形に揃う。
LF/CRLF 保存・冪等。
"""
import re, sys, pathlib, glob

DRILL = ('.self-check-quiz::before{content:"周回ドリル ○×"; position:absolute; top:-10px; left:14px; font-family:var(--f-soft);'
         '\n  background:linear-gradient(135deg,var(--li),var(--li-deep)); color:#fff; font-size:.66rem; font-weight:800; border-radius:7px; padding:2px 10px; letter-spacing:.03em}')

ROLE = ('.model-answer p.role::before{'
        '\n  content:var(--lbl); position:absolute; top:-10px; left:13px; padding:2px 10px;'
        '\n  font-family:var(--f-soft); font-weight:800; font-size:.66rem; line-height:1.9; letter-spacing:.03em; color:var(--cd);'
        '\n  background:var(--cb); border:none; border-radius:7px; box-shadow:0 2px 6px rgba(80,60,80,.13); text-indent:.03em;'
        '\n}')

DRILL_RE = re.compile(r'\.self-check-quiz::before\{[^}]*\}', re.DOTALL)
ROLE_RE = re.compile(r'\.model-answer p\.role::before\{[^}]*\}', re.DOTALL)


def process(path):
    with open(path, encoding='utf-8', newline='') as fh:
        t = fh.read()
    nl = '\r\n' if '\r\n' in t else '\n'
    n = 0
    t2, c1 = DRILL_RE.subn(DRILL.replace('\n', nl), t, count=1); n += c1
    t3, c2 = ROLE_RE.subn(ROLE.replace('\n', nl), t2, count=1); n += c2
    if t3 != t:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(t3)
    return c1, c2


def main():
    files = []
    for a in sys.argv[1:]:
        if not a.startswith('--'):
            files += glob.glob(a)
    for fp in files:
        if fp.endswith('.html'):
            c1, c2 = process(pathlib.Path(fp))
            print(f"{pathlib.Path(fp).name}: drill={c1} role={c2}")


if __name__ == '__main__':
    main()
