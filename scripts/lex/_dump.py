# -*- coding: utf-8 -*-
"""指定番号の TX 問題から spec 執筆に要る一次情報を抽出して /tmp/dump.txt へ。
   instr / 問題文(記述・事例・見解・語句群) / 組合せ選択肢 / ox-stmt / data-explanation /
   verdict-table(label,verdict,core) を出す。新規法理を足さず既存をそのまま写すための素材。"""
import re, sys, os
SUBJ = "outputs/000_TX/001_刑法"
def strip(t): return re.sub(r'<[^>]+>', '', t).replace('\n',' ').strip()
out=[]
for nn in sys.argv[1:]:
    s=open(os.path.join(SUBJ,f"刑TX{nn}.html"),encoding="utf-8").read()
    body=s[s.rfind('</style>'):]
    out.append("="*70); out.append(f"刑TX{nn}")
    m=re.search(r'<title>([^<]*)</title>', s); out.append("TITLE: "+(m.group(1) if m else ''))
    m=re.search(r'<p style="font-weight:600;">(.*?)</p>', body, re.S)
    out.append("INSTR: "+(strip(m.group(1)) if m else '(none)'))
    i=body.find('data-answer-type')
    cv=re.search(r'data-correct-value="([^"]*)"',body[i-260:i+260]); out.append("CV: "+(cv.group(1) if cv else '?'))
    at=re.search(r'data-answer-type="([^"]*)"',body[i-260:i+260]); out.append("ATYPE: "+(at.group(1) if at else '?'))
    # problem-text rows (記述/事例/語句群) with their inline label
    pts=re.findall(r'<div class="problem-text">(.*?)</div>', body, re.S)
    if pts:
        out.append("--- problem-text rows ---")
        for p in pts: out.append("  "+strip(p))
    # case-scene (見解/会話) titles + paragraphs
    cs=re.findall(r'<div class="case-scene-label">(.*?)</div>(.*?)(?=<div class="case-scene"|</div>\s*</div>)', body, re.S)
    sct=re.findall(r'<span class="case-scene-title">(.*?)</span>', body)
    if sct:
        out.append("--- case-scene titles ---")
        for t in sct: out.append("  "+strip(t))
    cps=re.findall(r'<p class="case-paragraph">(.*?)</p>', body, re.S)
    if cps:
        out.append("--- case-paragraphs ---")
        for p in cps: out.append("  "+strip(p))
    # 組合せ選択肢: any h3/p listing 1. ... 2. ... or a 【組合せ】 block
    combo=re.search(r'(【組合せ】[^<]*|【選択肢】[^<]*)', body)
    # ox rows: data-stmt + ox-stmt
    rows=re.findall(r'<div class="ox-row[^"]*" data-stmt="([^"]*)">.*?<span class="ox-stmt">(.*?)</span>', body, re.S)
    out.append("--- ox-stmt rows ---")
    for k,(d,t) in enumerate(rows,1): out.append(f"  [{d}] {strip(t)}")
    # data-explanation
    de=re.search(r'data-answer-type="ox-grid" data-explanation="([^"]*)"',body)
    out.append("--- data-explanation ---")
    out.append("  "+(de.group(1) if de else '(none)'))
    # verdict-table rows
    vt=re.findall(r'<tr data-stmt="([^"]*)"[^>]*>(.*?)</tr>', body, re.S)
    if vt:
        out.append("--- verdict-table (label | verdict | core) ---")
        for d,html in vt:
            tds=re.findall(r'<td[^>]*>(.*?)</td>', html, re.S)
            cells=[strip(x) for x in tds]
            out.append(f"  [{d}] "+" | ".join(cells))
open('/tmp/dump.txt','w',encoding='utf-8').write('\n'.join(out))
print("dumped", sys.argv[1:], "->", len('\n'.join(out)), "chars")
