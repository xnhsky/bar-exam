#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v11 真コア化（第2パス・刑TX326-445 全120問で適用済 2026-06-13）: 既に ox-grid 化済みの v11 ファイルを「真のコア」へ。

第1パス（_v11_upgrade_recipe.md）は validate は通すが 2 点を保留していた：
  (A) 教授ブロックを①②③④のまま残置（コア本来は①②のみ・③④/key-phrase-box/analogy/
      warning/cross-link は別冊 D-1 送り）。
  (B) choice-points が末尾のまま（v11 は「論点コア前倒し」＝ヘッダー直後）。

本スクリプトは各 choice-section について次を行う（冪等）：
  1. choice-points を choice-header-block の直後へ移動（既に前なら skip）。
  2. 教授ブロックを①②のみへ（③ヘッダー or key-phrase-box 以降を削除・既に①②なら skip）。

文字列手術で該当箇所だけ書き換え、他は byte 単位で温存（BS4 全書換はしない）。
使い方: python scripts/tx-v11-coreify.py <html...>  /  --check <html>（判定のみ）
"""
import re
import sys
from pathlib import Path

PROF_OPEN = '<div class="sub-card professor">'
CP_OPEN = '<div class="choice-points">'
HDR_OPEN = '<div class="choice-header-block">'
ORIG_OPEN = '<div class="sub-card original">'
BT_OPEN = '<div class="back-to-top">'
CUT_PATTERNS = [
    '<div class="key-phrase-box">',
    '<div class="prof-heading"><span class="prof-num">3</span>',
]


def transform_section(s: str):
    """1 つの choice-section 文字列を変換。返り値 (new_s, changed_flags)。"""
    flags = []
    # --- (A) 教授ブロック ①② 化 -------------------------------------------
    if PROF_OPEN in s and '<span class="prof-num">3</span>' in s:
        prof_start = s.index(PROF_OPEN)
        # professor の終端 </div>：直後ブロック（choice-points か back-to-top）の手前
        after = min((s.index(x, prof_start) for x in (CP_OPEN, BT_OPEN) if x in s[prof_start:]),
                    default=len(s))
        prof_close_end = s.rfind('</div>', prof_start, after) + len('</div>')
        prof_block = s[prof_start:prof_close_end]
        cuts = [prof_block.find(p) for p in CUT_PATTERNS]
        cuts = [c for c in cuts if c != -1]
        if cuts:
            cut = min(cuts)
            new_prof = prof_block[:cut].rstrip() + '\n    </div>'
            s = s[:prof_start] + new_prof + s[prof_close_end:]
            flags.append('prof->①②')
    # --- (B) choice-points 前倒し ------------------------------------------
    if CP_OPEN in s and HDR_OPEN in s and ORIG_OPEN in s:
        cp_start = s.index(CP_OPEN)
        orig_start = s.index(ORIG_OPEN)
        if cp_start > orig_start:  # まだ末尾＝要移動（前にあるなら冪等 skip）
            cp_ol = s.index('</ol>', cp_start)
            cp_end = s.index('</div>', cp_ol) + len('</div>')
            cp_block = s[cp_start:cp_end]
            line_start = s.rfind('\n', 0, cp_start)
            # choice-points を現在位置から除去（前の改行ごと）
            s = s[:line_start] + s[cp_end:]
            # header-block の終端 </div>（sub-card original の手前）直後へ挿入
            hdr_start = s.index(HDR_OPEN)
            orig2 = s.index(ORIG_OPEN, hdr_start)
            hdr_close_end = s.rfind('</div>', hdr_start, orig2) + len('</div>')
            s = s[:hdr_close_end] + '\n\n    ' + cp_block + s[hdr_close_end:]
            flags.append('cp->front')
    return s, flags


SEC_RE = re.compile(r'(<section class="choice-section[^"]*" id="choice-\d+">.*?</section>)', re.DOTALL)


def transform_file(html: str):
    all_flags = []

    def repl(m):
        new_s, flags = transform_section(m.group(1))
        all_flags.extend(flags)
        return new_s

    return SEC_RE.sub(repl, html), all_flags


def main():
    args = sys.argv[1:]
    check = '--check' in args
    files = [a for a in args if a != '--check']
    for fp in files:
        p = Path(fp)
        html = p.read_text(encoding='utf-8')
        new, flags = transform_file(html)
        n_prof = flags.count('prof->①②')
        n_cp = flags.count('cp->front')
        if check:
            print(f"{p.name}: prof_to_strip={n_prof} cp_to_move={n_cp}")
            continue
        if new != html:
            p.write_text(new, encoding='utf-8')
            print(f"[OK] {p.name}: prof->①②×{n_prof}, cp->front×{n_cp}")
        else:
            print(f"[--] {p.name}: 変更なし（既に真コア or 対象外）")


if __name__ == '__main__':
    main()
