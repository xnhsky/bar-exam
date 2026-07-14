#!/usr/bin/env python3
"""図解挿入用アンカー候補を印字（読み取り専用）。
usage: python scripts/tx-dgm-anchors.py <_lex.html>
"""
import re, sys, html
src = open(sys.argv[1], encoding='utf-8', newline='').read()
def u(s): return src.count(s)

print("### CARD syn-path close anchors")
for m in re.finditer(r'<article class="tx-inline-card" data-stmt="([^"]+)".*?</article>', src, re.S):
    n, c = m.group(1), m.group(0)
    sp = re.search(r'(</span></p>\s*</div>)\s*(?=<p class="syn-image"|<div class="syn-image"|<div class="tx-v13-trap"|<details|<div class="choice-points"|<div class="sub-card|<p class="tx-onepoint"|<div class="tx-onepoint")', c, re.S)
    if sp:
        # find its absolute tail in file via preceding unique text
        seg = sp.group(1)
        # get 40 chars before syn-path close within card for uniqueness
        idx = c.rfind(seg)
        pre = re.sub(r'<[^>]+>','', c[max(0,idx-60):idx])
        pre = re.sub(r'\s+','',pre)[-26:]
        anchor = pre + '</span></p>'
        print(f"  [stmt {n}] anchor={anchor!r} uniq={u(anchor)}")
    else:
        print(f"  [stmt {n}] NO match")

print("\n### NARRATIVE <p data-fa-label> raw tails")
for m in re.finditer(r'<p data-fa-label="([^"]*)"[^>]*>(.*?)</p>', src, re.S):
    lab = m.group(1)
    raw = m.group(0)
    # candidate anchor: last 30 raw chars ending at </p>
    tailraw = raw[-46:]
    # plain text preview
    txt = re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',m.group(2))).strip()
    print(f"  label={lab!r} …{txt[-30:]!r}")
    print(f"      rawtail={tailraw!r} uniq={u(tailraw)}")
