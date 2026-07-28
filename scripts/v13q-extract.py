#!/usr/bin/env python3
"""§v13q 改訂用の素材抽出。usage: python3 v13q_extract.py <file.html>
記述カード・正誤表・#basis・CSS の現状を執筆に必要な範囲だけ出力する。"""
import io, re, sys

path = sys.argv[1]
with io.open(path, encoding='utf-8', newline='') as f:
    html = f.read()

strip = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or '')).strip()

key = re.search(r'data-answer-key="([^"]*)"', html)
print(f'== FILE {path}')
print(f'answer-key: {key.group(1) if key else "?"}')
print(f'CSS TX-ANSCOMP: {"あり" if "TX-ANSCOMP:BEGIN" in html else "なし"}')
ver = re.search(r'lexia-genmeta[^>]*>([^<]*)<', html)
print(f'genmeta: {ver.group(1).strip() if ver else "?"}')

b = re.search(r'<section class="section" id="basis"[^>]*>(.*?)</section>', html, re.S)
if b:
    hid = 'hidden' in b.group(0)[:60]
    t = strip(b.group(1)).replace('↑ ページ先頭へ', '').strip()
    print(f'#basis: {"hidden" if hid else ("空箱(可視)" if not t else "中身あり(可視)")} text={len(t)}字')
else:
    print('#basis: 無し')

arts = re.findall(r'<article class="tx-inline-card" data-stmt="([^"]+)".*?</article>', html, re.S)
for m in re.finditer(r'<article class="tx-inline-card" data-stmt="([^"]+)"(.*?)</article>', html, re.S):
    n, seg = m.group(1), m.group(2)
    print(f'\n===== 記述 {n} =====')
    st = re.search(r'<span class="tx-inline-stmt-text">(.*?)</span>', seg, re.S)
    print(f'[問題文] {strip(st.group(1)) if st else "?"}')
    v = re.search(r'<div class="tx-v13-verdict">(.*?)</div>', seg, re.S)
    print(f'[判定] {strip(v.group(1)) if v else "?"}')
    om = re.search(r'<p class="syn-orig">(.*?)</p>', seg, re.S)
    if om:
        print(f'[記述原文 raw] {om.group(1).strip()[:800]}')
    lead = re.search(r'<p class="syn-lead"><span class="syn-tag">[^<]*</span>(.*?)</p>', seg, re.S)
    print(f'[現GIST] {strip(lead.group(1)) if lead else "?"}')
    for p in re.findall(r'<p><span class="syn-step">.*?</p>', seg, re.S):
        print(f'[path] {strip(p)[:300]}')
    for h in re.findall(r'<div class="tx-basis-head">(.*?)</div>', seg, re.S):
        print(f'[BASIS] {strip(h)[:110]}')
    img = re.search(r'<p class="syn-image"><span class="syn-tag">[^<]*</span>(.*?)</p>', seg, re.S)
    print(f'[フック] {strip(img.group(1)) if img else "?"}')
    print(f'[図解] {"あり" if "tx-dgm" in seg else "なし"}')
    print(f'[anscomp既存] {"あり" if "tx-anscomp-line" in seg else "なし"}')

print('\n===== 正誤表 data-brief-mark =====')
for m in re.finditer(r'<tr data-stmt="([^"]+)" data-verdict="([xo])" data-brief-mark="(.*?)">', html, re.S):
    print(f'row{m.group(1)}({m.group(2)}): {m.group(3).strip()[:600]}')
