#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""事件情報の表示形式を百選型(1行完全引用)に統一。

③型（旧カード変換）の事件情報は「裁判所：… / 判決日：… / 出典：…」の複数行ラベル形式。
④型（百選起草）は「裁判所+年月日 ／ 掲載 ／ 事件番号（事件名）」の1行完全引用。
これを揃えるため、③型のラベル付き段落を1行の引用へ結合する（審級経過など非ラベル段落は
第2段落として温存）。ラベルが無い事件情報(=既に④型)は不変。冪等・内容保持・LF保持。

usage: python scripts/ariadne-unify-jiken.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JIKEN = re.compile(
    r'(<div class="cx-sec cr-jouhou"><span class="cx-lab">事件情報</span><div class="cx-body">)(.*?)(</div></div>)',
    re.S)
LABELED = re.compile(
    r'^\s*(?:<strong>)?\s*(裁判所|裁判所名|判決日|決定日|言渡日|出典|掲載誌?|事件番号|事件名|審級)\s*(?:</strong>)?\s*[：:]\s*(.*)$',
    re.S)
COMBINED = re.compile(r'^\s*(?:<strong>)?\s*裁判所[・／/][^<：:]{0,8}(?:</strong>)?\s*[：:]\s*(.*)$', re.S)

def unify_body(inner):
    ps = re.findall(r'<p[^>]*>(.*?)</p>', inner, re.S)
    if not ps:
        return inner, False
    cite = {}
    extra = []
    combined = None
    for p in ps:
        m = LABELED.match(p)
        if m:
            cite[m.group(1)] = m.group(2).strip()
            continue
        cm = COMBINED.match(p)
        if cm:
            combined = cm.group(1).strip()
            continue
        extra.append(p.strip())
    if not cite and not combined:
        return inner, False  # 既に④型（ラベル無し）
    if combined and not cite:   # 「裁判所・判決日：{完全引用}」型は前置ラベルを剥がすだけ
        out = f"<p>{combined}</p>"
        for e in extra:
            out += f"\n<p>{e}</p>"
        return out, True
    court = cite.get("裁判所") or cite.get("裁判所名", "")
    date = cite.get("判決日") or cite.get("決定日") or cite.get("言渡日", "")
    src = cite.get("出典") or cite.get("掲載", "")
    num = cite.get("事件番号", "")
    name = cite.get("事件名", "")
    line = (court + ("　" if court and date else "") + date).strip()
    tail = [x for x in [src, num] if x]
    if tail:
        line += ("／" if line else "") + "／".join(tail)
    if name:
        line += f"（{name}）"
    out = f"<p>{line}</p>"
    for e in extra:
        out += f"\n<p>{e}</p>"
    return out, True

def transform(html):
    n = 0
    def rep(m):
        nonlocal n
        new_body, changed = unify_body(m.group(2))
        if changed:
            n += 1
            return m.group(1) + "\n" + new_body + "\n" + m.group(3)
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
    print(f"\n{tot} 件の事件情報を1行引用へ統一 ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
