#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIADNE 適合ギャップの「機械修正」だけを担当（本文不変・冪等・LF/CRLF 保存）。
展開(ロールアウト)前後の後片付け用。内容判断の要る修正はここでは扱わない。

やること（純粋な文字列置換＝安全・冪等）：
  1) 版スタンプを現行 "ARIADNE v1.2.0 PLACEHOLDER-LOCK" に統一（旧 v0.3 / v1.0.0 / v1.1.0 / MATRIX-THREAD）。
     CSS 先頭コメント・フッター <b>…</b>・lexia-genmeta の版トークンをまとめて置換（Generated 日時は不変）。
  2) 未定義の .warn-box を .key-box へ（<style> に .warn-box が無い＝素描画のときだけ）。

やらないこと（内容判断＝LLM / 既存スクリプトに委譲。docs/ariadne-rollout-playbook.md 参照）：
  - 骨子 matrix-bone → simple .bone の蒸留          … LLM ワークフロー
  - 深掘りテンプレ流用（018型）の本問論点への再鋳造  … LLM ワークフロー（元JX を一次情報）
  - current-law-note の他問流用→本問への差替        … LLM
  - .draft-problem の原文逐語化                     … scripts/ariadne-draftproblem-backfill.py（冪等）
  - .bc-inst / .draft-digest の 2カラム化           … scripts/ariadne-restyle-backfill.py 系 / fix ワークフロー

使い方：
  python -X utf8 scripts/ariadne-conform-fix.py "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"
  python -X utf8 scripts/ariadne-conform-fix.py <file> --dry-run
"""
import sys
import re
import glob

CUR = "ARIADNE v1.2.0 PLACEHOLDER-LOCK"

# 旧版トークン（長い順＝部分一致を避ける）。既に現行なら該当なし＝冪等。
OLD_VERSIONS = [
    "ARIADNE v1.1.0 MATRIX-THREAD",
    "ARIADNE v1.0.0 MATRIX-THREAD",
    "ARIADNE v1.1.0",
    "ARIADNE v1.0.0",
    "ARIADNE v0.3",
    "ARIADNE v0.1",
]


def fix_text(txt):
    changes = []

    # 1) 版スタンプ統一
    for old in OLD_VERSIONS:
        if old != CUR and old in txt:
            cnt = txt.count(old)
            txt = txt.replace(old, CUR)
            changes.append(f"version {old} -> {CUR} x{cnt}")

    # 2) 未定義 .warn-box -> .key-box（<style> に定義が無いときだけ）
    style = "".join(re.findall(r"<style[^>]*>(.*?)</style>", txt, re.S))
    if ".warn-box" not in style and re.search(r'class="[^"]*\bwarn-box\b', txt):
        def _repl(m):
            cls = re.sub(r"(?<![\w-])warn-box(?![\w-])", "key-box", m.group(1))
            return f'class="{cls}"'
        new = re.sub(r'class="([^"]*\bwarn-box\b[^"]*)"', _repl, txt)
        if new != txt:
            txt = new
            changes.append("warn-box -> key-box (未定義CSSの素描画解消)")

    return txt, changes


def process(path, dry):
    # newline='' で既存の改行コード（LF/CRLF）を一切変換しない＝byte 実質不変。
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    new, changes = fix_text(raw)
    if changes and not dry:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new)
    return changes


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    patterns = [a for a in argv if not a.startswith("--")]
    if not patterns:
        print("usage: python -X utf8 scripts/ariadne-conform-fix.py <file|glob> [--dry-run]")
        sys.exit(2)

    files = []
    for pat in patterns:
        files += glob.glob(pat, recursive=True)
    files = sorted(set(files))
    if not files:
        print("no files matched")
        sys.exit(1)

    changed = 0
    for f in files:
        chs = process(f, dry)
        if chs:
            changed += 1
            print(f"[{'DRY' if dry else 'FIX'}] {f}: " + " / ".join(chs))
        else:
            print(f"[ok ] {f}: no change (already conformant)")
    print(f"\n{changed} file(s) {'would be ' if dry else ''}changed of {len(files)}.")


if __name__ == "__main__":
    main()
