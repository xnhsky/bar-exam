#!/usr/bin/env python3
"""rx-bodyfix.py — 既存 RX の body を AXIOM v2.8 構造へ揃える（冪等・本文不変）.

rx-restyle.py が <head>（=<style>）を差し替えるのに対し、本スクリプトは body の
**構造シェルだけ**を最新 AXIOM に合わせる（テキスト=法的内容は一切書き換えない）：

  1) 規範を norm-group コンテナに収める：
       <button class="norm-toggle">…</button><div class="norm-box">…</div>
     を <div class="norm-group"> … </div> で包む（既に norm-group があれば skip）。
  2) 関連判例・条文（.refs）の「条文／判例」ラベル行を flex 2カラム化：
       <p><b>条文</b>　本文…</p>  →  <p><b>条文</b><span>本文…</span></p>
     （colon ：/: は除去・全角空白は gap に置換）。これで折返しがラベル下に
     回り込まない（CSS `.refs p:has(> span)`）。
     ※ 先頭が「条文/判例」ラベルでない旧式 refs（判例名そのものをバッジ化した
        もの・<b>無しのプレーン）は **意味的な条文/判例 振り分けが必要＝内容改変**
        になるため触らない（新 CSS で普通に流す）。

冪等：再実行しても二重ラップ/二重 span にならない（span 済み <p> と norm-group 済みは skip）。
既定は dry-run（差分件数のみ表示）。実適用は --apply。
"""
from __future__ import annotations
import argparse
import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO = pathlib.Path(__file__).resolve().parent.parent
RX_DIR = REPO / "outputs/ux/001_RX"

NORM_RE = re.compile(
    r'(<button class="norm-toggle"[^>]*>.*?</button>\s*<div class="norm-box">.*?</div>)',
    re.S,
)
REFS_BLOCK_RE = re.compile(r'(<div class="refs">)(.*?)(</div>)', re.S)
P_RE = re.compile(r"<p\b[^>]*>.*?</p>", re.S)
P_PARTS_RE = re.compile(r"(<p\b[^>]*>)(.*)(</p>)", re.S)
# <p> 本文が「<b>条文/判例[：:]?</b> 本文…」で始まるラベル行か
LABEL_RE = re.compile(
    r"^\s*<b>\s*(条文|判例)\s*[：:]?\s*</b>[\s　：:]*(.+?)\s*$", re.S
)


def fix_norm(html: str) -> tuple[str, bool]:
    if 'class="norm-group"' in html:
        return html, False
    if not NORM_RE.search(html):
        return html, False
    out = NORM_RE.sub(
        lambda m: '<div class="norm-group">' + m.group(1) + "</div>", html, count=1
    )
    return out, out != html


def fix_refs(html: str) -> tuple[str, bool, int]:
    n = [0]

    def repl_block(bm: re.Match) -> str:
        def repl_p(pm: re.Match) -> str:
            full = pm.group(0)
            parts = P_PARTS_RE.match(full)
            if not parts:
                return full
            body = parts.group(2)
            if "<span" in body:  # 既に span 済み = 変換済み → skip（冪等）
                return full
            lm = LABEL_RE.search(body)
            if not lm:  # 旧式 refs（ラベルでない）→ 触らない
                return full
            label, rest = lm.group(1), lm.group(2)
            n[0] += 1
            return f"{parts.group(1)}<b>{label}</b><span>{rest}</span>{parts.group(3)}"

        new_inner = P_RE.sub(repl_p, bm.group(2))
        return bm.group(1) + new_inner + bm.group(3)

    out = REFS_BLOCK_RE.sub(repl_block, html)
    return out, out != html, n[0]


def classify_refs(html: str) -> str:
    m = REFS_BLOCK_RE.search(html)
    if not m:
        return "none"
    inner = m.group(2)
    if re.search(r"<b>\s*(条文|判例)\s*[：:]?\s*</b>", inner):
        return "label"
    if "<b>" in inner:
        return "badge"
    return "plain"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="実書込（既定は dry-run）")
    ap.add_argument("--verbose", action="store_true", help="変更ファイルを列挙")
    args = ap.parse_args()

    files = sorted(RX_DIR.rglob("*.html"))
    norm_wrapped = refs_converted = files_changed = 0
    no_quizgroup = 0
    refs_kind = {"label": 0, "badge": 0, "plain": 0, "none": 0}
    changed_files = []

    for f in files:
        raw = f.read_text(encoding="utf-8")
        html, nchg = fix_norm(raw)
        html, rchg, ncols = fix_refs(html)
        refs_kind[classify_refs(raw)] += 1
        if 'class="quiz-group"' not in raw:
            no_quizgroup += 1
        if nchg:
            norm_wrapped += 1
        if rchg:
            refs_converted += ncols
        if html != raw:
            files_changed += 1
            changed_files.append((f.name, nchg, ncols))
            if args.apply:
                f.write_text(html, encoding="utf-8")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== rx-bodyfix [{mode}] files={len(files)} ===")
    print(f"norm-group wrapped : {norm_wrapped}")
    print(f"refs label rows → 2col span : {refs_converted}")
    print(f"files changed : {files_changed}")
    print(f"refs 種別: label(2col化対象)={refs_kind['label']} "
          f"badge(旧式・流す)={refs_kind['badge']} "
          f"plain(<b>なし・流す)={refs_kind['plain']} none={refs_kind['none']}")
    print(f"quiz-group 未保有（✅チップ非適用・要確認）: {no_quizgroup}")
    if args.verbose:
        for name, nchg, ncols in changed_files:
            print(f"  - {name}: norm={'Y' if nchg else '-'} refs_cols={ncols}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
