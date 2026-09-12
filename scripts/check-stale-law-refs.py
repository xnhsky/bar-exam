#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旧法表記・旧項番号の残存ゲート（内容監査・2026-09-04）

改正で**言い回しや項番号が動いた条文**を、旧のまま本文で引いていないかを検出する。
条番号は実在し、ファイル内の整合も取れているため、既存のどのゲートにも掛からない型。

実害（2026-09-04・§v13x 執筆中に発覚）:
  刑訴TX100（公式＋_lex）が、身体検査に関する条件の規定を「218条5項」として引いていた。
  現行法では 218条6項（2011 年改正で 2 項が挿入され、以降が 1 つずつ繰り下がった）。
  判例（最決昭55.10.23）当時は 5 項だったため、旧解説・過去問 PDF は 5 項と書く。
  本文は現行法へそろえ、旧番号は現行法ノート（.tx-current-law-note）で補足する、が正典の運用。

判定:
  ルールは scripts/stale-law-refs.json（データ駆動）。1 ルール ＝
    { "law": 法域, "pattern": 旧表記の正規表現, "context": 併存を要求する語（省略可）,
      "exclude": 新旧対照として正しい書き方を示す語（省略可）, "correct": 現行の表記, "note": 経緯 }
  **現行法ノート（.tx-current-law-note）と判例カード（.tx-basis-item.is-case）の中は対象外**
  ＝旧法・判例当時の表記をそこに書くのは正典の運用どおりなので弾かない。

使い方:
    python scripts/check-stale-law-refs.py                 # outputs 全体を走査（既定・exit 1 で止める）
    python scripts/check-stale-law-refs.py --warn-only     # 可視化のみ
    python scripts/check-stale-law-refs.py <path...>       # ファイル/ディレクトリ指定
"""
import sys
import os
import re
import json
import html
import glob

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(REPO, "scripts", "stale-law-refs.json")
DEFAULT_ROOTS = [os.path.join(REPO, "outputs")]
SUBJECT = re.compile(r"^(刑訴|民訴|行政|刑|民|商|憲)TX")


def subject_of(path):
    m = SUBJECT.match(os.path.basename(path))
    return m.group(1) if m else "?"


def strip_exempt(raw):
    """旧表記を書いてよい領域（現行法ノート・判例カード・script/style）を落とす。"""
    raw = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.S | re.I)
    # 現行法ノート（旧法・改正経緯を書く場所）
    raw = re.sub(r'<div[^>]*class="[^"]*tx-current-law-note[^"]*".*?</div>\s*</div>', " ", raw, flags=re.S)
    raw = re.sub(r'<[^>]*class="[^"]*current-law-note[^"]*"[^>]*>.*?</div>', " ", raw, flags=re.S)
    # 判例カード（判旨は当時の表記のまま引く）
    raw = re.sub(r'<div[^>]*class="[^"]*tx-basis-item[^"]*is-case[^"]*".*?(?=<div[^>]*class="tx-basis-item|</div></div>)',
                 " ", raw, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    warn_only = "--warn-only" in sys.argv[1:]
    roots = args or DEFAULT_ROOTS
    with open(RULES, encoding="utf-8") as f:
        rules = json.load(f)["rules"]

    files = []
    for r in roots:
        if os.path.isfile(r):
            files.append(r)
        else:
            files += glob.glob(os.path.join(r, "**", "*.html"), recursive=True)
    files = sorted(set(files))

    hits = []
    for f in files:
        subj = subject_of(f)
        text = None
        for rule in rules:
            if rule.get("law") and rule["law"] != subj:
                continue
            if text is None:
                text = strip_exempt(open(f, encoding="utf-8").read())
            for m in re.finditer(rule["pattern"], text):
                window = text[max(0, m.start() - 40):m.end() + 40]
                ctx = rule.get("context")
                if ctx and not re.search(ctx, window):
                    continue
                exc = rule.get("exclude")
                if exc and re.search(exc, window):
                    continue      # 「〔現6項〕」「改正前は…」等の新旧対照は正しい書き方
                hits.append((f, rule, " ".join(window.split())))
                break        # 1 ファイル 1 ルール 1 件だけ報告（同じ誤りの列挙を避ける）

    print("=== 旧法表記・旧項番号の残存ゲート (check-stale-law-refs) ===")
    print(f"走査 {len(files)} ファイル / ルール {len(rules)} 件")
    if not hits:
        print("[OK] 旧表記の残存なし")
        return 0
    byrule = {}
    for f, rule, w in hits:
        byrule.setdefault(rule["correct"], []).append((f, rule, w))
    print(f"\n--- 旧表記の残存 {len(hits)} 件 ---")
    for correct, items in byrule.items():
        rule = items[0][1]
        print(f"\n[{rule.get('law','*')}] {rule['pattern']} → 現行は **{correct}**")
        print(f"   {rule['note']}")
        for f, _, w in items[:8]:
            print(f"   ・{os.path.relpath(f, REPO)}: {w[:110]}")
        if len(items) > 8:
            print(f"   …ほか {len(items) - 8} ファイル")
    print("\n本文は現行法へそろえ、旧番号・旧表記は現行法ノート（tx-current-law-note）で補足する。")
    return 0 if warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
