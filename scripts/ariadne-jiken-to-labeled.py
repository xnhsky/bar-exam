#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""事件情報を複数行ラベル形式（③型・裁判所：/判決日：/出典：/事件番号：/事件名：）に統一。

ユーザー選好＝ラベル付き複数行の方が見やすい。1行完全引用（百選型）を解析してフィールド分解する。
「{裁判所}{和暦年月日}{法廷}{決定/判決}／{掲載}／{事件番号}（{事件名}）」等を
裁判所/判決日/出典/事件番号/事件名 に分ける。審級経過など非引用段落は温存。既にラベル付きは不変（冪等）。

usage: python scripts/ariadne-jiken-to-labeled.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JIKEN = re.compile(
    r'(<div class="cx-sec cr-jouhou"><span class="cx-lab">事件情報</span><div class="cx-body">)(.*?)(</div></div>)',
    re.S)
DATE = re.compile(r'(?:明治|大正|昭和|平成|令和)(?:元|\d+)年\d+月\d+日')
NUM = re.compile(r'(?:明治|大正|昭和|平成|令和)?\s*(?:元|\d+)年\s*[（(][^）)]{1,4}[）)]\s*第[\d０-９]+号')
NAME = re.compile(r'（([^（）]{2,80}?(?:被告事件|事件))）')
TEI = re.compile(r'^\s*(第[一二三四五六]小法廷|大法廷)?\s*(決定|判決)?')

def parse_citation(s):
    s = re.sub(r'\s+', ' ', s).strip()
    d = {}
    mn = NAME.search(s)
    if mn:
        d["事件名"] = mn.group(1).strip()
    mnum = NUM.search(s)
    if mnum:
        d["事件番号"] = re.sub(r'\s+', '', mnum.group(0))
    md = DATE.search(s)
    if md:
        head = s[:md.start()].strip(" 　／/（(")
        after = s[md.end():]
        mt = TEI.match(after)
        court = head
        typ = ""
        if mt:
            if mt.group(1):
                court += mt.group(1)
            if mt.group(2):
                typ = mt.group(2)
        court = re.sub(r'^最高裁(?!判所)', '最高裁判所', court)
        if court:
            d["裁判所"] = court
        d["判決日"] = md.group(0) + typ
    if d.get("事件名") and d.get("事件番号") and d["事件番号"] in re.sub(r'\s+', '', d["事件名"]):
        nm = re.sub(re.escape(d["事件番号"]), "", re.sub(r'\s+', '', d["事件名"])).lstrip("・、 ").strip()
        if nm:
            d["事件名"] = nm
    # 出典（掲載）＝頁を含むセグメント（事件名/番号は除外）
    for seg in re.split(r'[／/]', s):
        seg = seg.strip()
        if "頁" in seg and "被告事件" not in seg:
            seg = re.sub(r'^[（(]|[）)]$', '', seg)
            d["出典"] = seg
            break
    return d

def to_labeled(d, extra):
    order = ["裁判所", "判決日", "出典", "事件番号", "事件名"]
    lines = [f"<p><strong>{k}</strong>：{d[k]}</p>" for k in order if d.get(k)]
    lines += [f"<p>{e}</p>" for e in extra]
    return "\n".join(lines)

def unify_body(inner):
    if "<strong>裁判所" in inner or "<strong>判決日" in inner:
        return inner, False  # 既にラベル付き
    ps = re.findall(r'<p[^>]*>(.*?)</p>', inner, re.S)
    if not ps:
        return inner, False
    cite_txt = re.sub(r'<[^>]+>', '', ps[0]).strip()
    extra = [p.strip() for p in ps[1:]]
    d = parse_citation(cite_txt)
    if "判決日" not in d and "出典" not in d:
        return inner, False  # 解析不能＝触らない
    return to_labeled(d, extra), True

def transform(html):
    n = 0
    def rep(m):
        nonlocal n
        nb, ch = unify_body(m.group(2))
        if ch:
            n += 1
            return m.group(1) + "\n" + nb + "\n" + m.group(3)
        return m.group(0)
    return JIKEN.sub(rep, html), n

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    new, n = transform(raw)
    changed = new != raw
    if changed and apply:
        Path(path).write_bytes(new.encode("utf-8"))
    return changed, n

def main():
    apply = "--apply" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        files = sorted(glob.glob(str(ROOT / "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"), recursive=True))
        files.append(str(ROOT / "canonical/ARIADNE.html"))
    tot = 0
    for f in files:
        if not Path(f).exists():
            continue
        c, n = process(f, apply)
        tot += n
        if c:
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}  {n}件")
    print(f"\n{tot} 件をラベル形式へ ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
