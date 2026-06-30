#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex inline-explain リフロー：答案圧縮→解説冒頭の ANSWER 箱、記憶フック→ワンポイント。

各 .tx-inline-card の .tx-inline-explain について（本文テキストは不変・移設のみ・冪等）:
  - .tx-cycle-aids 内の「答案圧縮」(.tx-cycle-label.is-compress) を解説の先頭（問題文直下）へ
    .tx-answer-box（英語食み出しタブ「✍ ANSWER」）として移設。
  - 「記憶フック」(.tx-cycle-label) を .tx-onepoint（💡 ワンポイント）に変換し、
    cycle-aids のあった位置（解説末尾・詳説トグルの前）へ。
  - 空になった .tx-cycle-aids を除去。

CSS は canonical/GENESIS-CORE.html 同梱（restyle で全 v12 _lex へ伝播）。本スクリプトは
DOM 移設のみを担い、restyle（CSS 載せ替え）と対で propagation に使う。既に .tx-answer-box を
持つカードはスキップ（冪等）。canonical 本体のサンプルカードにも適用して構造を一致させる。

使い方:
  python -X utf8 scripts/tx-lex-answerbox.py outputs/ux/000_TX/001_刑法            # dry-run
  python -X utf8 scripts/tx-lex-answerbox.py outputs/ux/000_TX/001_刑法 --apply    # 反映
  python -X utf8 scripts/tx-lex-answerbox.py canonical/GENESIS-CORE.html --apply
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

CARD_RE = re.compile(r'(<article class="tx-inline-card"[^>]*>)(.*?)(</article>)', re.S)
CYCLE_RE = re.compile(r'<div class="tx-cycle-aids">(.*?)</div>', re.S)
EXPLAIN_OPEN_RE = re.compile(r'(<div class="tx-inline-explain"[^>]*>)')
STMT_RE = re.compile(r'data-stmt="([^"]+)"')
DETAIL_RE = re.compile(r'<details class="tx-inline-detail">.*?</details>', re.S)
ANS_RE = re.compile(
    r'<span class="tx-cycle-label is-compress">[^<]*</span>\s*<span class="tx-cycle-body">(.*?)</span>',
    re.S,
)
HOOK_RE = re.compile(
    r'<span class="tx-cycle-label">([^<]*)</span>\s*<span class="tx-cycle-body">(.*?)</span>',
    re.S,
)

PARTB_SOURCE_LABELS = {
    "ア": "1", "イ": "2", "ウ": "3", "エ": "4", "オ": "5",
    "カ": "6", "キ": "7", "ク": "8", "ケ": "9", "コ": "10",
    "A": "1", "B": "2", "C": "3", "D": "4", "E": "5",
    "F": "6", "G": "7", "H": "8", "I": "9", "J": "10",
    "Ａ": "1", "Ｂ": "2", "Ｃ": "3", "Ｄ": "4", "Ｅ": "5",
    "Ｆ": "6", "Ｇ": "7", "Ｈ": "8", "Ｉ": "9", "Ｊ": "10",
}


def partb_source_id(stmt_no: str) -> str:
    key = (stmt_no or "").strip()
    for prefix in ("記述", "肢", "空欄"):
        if key.startswith(prefix):
            key = key[len(prefix):].strip()
            break
    if not key:
        return ""
    if key.isdecimal():
        return key
    return PARTB_SOURCE_LABELS.get(key) or PARTB_SOURCE_LABELS.get(key.upper(), key)


def add_detail_panel(inner: str, stmt_no: str) -> tuple[str, bool]:
    """空の <details class="tx-inline-detail">（panel 欠落）に
    <div class="tx-detail-panel tx-detail-partb" data-partb-source="N"> を補完する。
    エンジン hydrateInlinePartBDetails が #choice-N（PART B）から内容を流し込めるようにする。
    既に panel を持つ details は無改変（冪等）。N が取れない／details 無しなら無改変。
    data-stmt がア/イ等でも choice-1/2 等へ解決できる数値IDを入れる。"""
    source_id = partb_source_id(stmt_no)
    if not source_id:
        return inner, False

    changed = False

    def fix(m):
        nonlocal changed
        det = m.group(0)
        if "tx-detail-panel" in det:
            return det  # 既に panel あり
        panel = (
            '\n<div class="tx-detail-panel tx-detail-partb" data-partb-source="'
            + source_id
            + '"></div>\n'
        )
        changed = True
        return det[: -len("</details>")] + panel + "</details>"

    new = DETAIL_RE.sub(fix, inner, count=1)
    return new, changed


def transform_card(inner: str, stmt_no: str = "") -> tuple[str, bool]:
    changed = False
    # (b) 詳説 panel 補完（reflow とは独立・冪等）
    inner, det_changed = add_detail_panel(inner, stmt_no)
    changed = changed or det_changed

    # (a) 答案圧縮→ANSWER／記憶フック→ワンポイントの reflow（冪等）
    if "tx-answer-box" in inner:
        return inner, changed
    cm = CYCLE_RE.search(inner)
    if not cm:
        return inner, changed
    cycle_full, cycle_in = cm.group(0), cm.group(1)
    ans = ANS_RE.search(cycle_in)
    hook = HOOK_RE.search(cycle_in)
    if not ans and not hook:
        return inner, changed

    answer_box = ""
    if ans:
        answer_box = (
            '<div class="tx-answer-box"><span class="tx-answer-body">'
            + ans.group(1).strip()
            + "</span></div>\n"
        )
    one_point = ""
    if hook:
        label = hook.group(1).strip() or "記憶フック"
        one_point = (
            '<div class="tx-onepoint"><span class="tx-op-label">'
            + label
            + '</span><span class="tx-op-body">'
            + hook.group(2).strip()
            + "</span></div>"
        )

    # 1) cycle-aids → 記憶フック ワンポイント（同じ位置＝解説末尾）
    new = inner.replace(cycle_full, one_point, 1)
    # 2) 答案圧縮 → 解説先頭（問題文直下）の ANSWER 箱
    if answer_box:
        new = EXPLAIN_OPEN_RE.sub(lambda m: m.group(1) + "\n" + answer_box, new, count=1)
    return new, True


def transform(text: str) -> tuple[str, int]:
    count = 0

    def repl(m):
        nonlocal count
        sm = STMT_RE.search(m.group(1))
        stmt_no = sm.group(1) if sm else ""
        new_inner, changed = transform_card(m.group(2), stmt_no)
        if changed:
            count += 1
        return m.group(1) + new_inner + m.group(3)

    return CARD_RE.sub(repl, text), count


def collect(paths):
    files = []
    for p in paths:
        ap = Path(p)
        ap = ap if ap.is_absolute() else ROOT / ap
        if ap.is_file() and ap.suffix == ".html":
            files.append(ap)
        elif ap.is_dir():
            files.extend(sorted(ap.rglob("*_lex.html")))
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="_lex.html / canonical html / ディレクトリ")
    ap.add_argument("--apply", action="store_true", help="実際に上書きする（既定 dry-run）")
    args = ap.parse_args()

    files = collect(args.paths)
    total_files = changed_files = total_cards = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        if "tx-cycle-aids" not in text and "tx-inline-card" not in text:
            continue
        total_files += 1
        new, cards = transform(text)
        if new == text:
            continue
        changed_files += 1
        total_cards += cards
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        if args.apply:
            f.write_text(new, encoding="utf-8")
            print(f"  [w] {rel}  (cards reflowed: {cards})")
        else:
            print(f"  [.] would reflow {rel}  (cards: {cards})")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] scanned={total_files} / changed={changed_files} / cards reflowed={total_cards}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
