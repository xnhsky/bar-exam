#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-solvenav-engine-keys.py ── ○×消去法ナビ（build-ox-lex 系エンジン）の行キー写像修理。

LEX388 調査（2026-07-14）で発覚した同族バグ群：
  (1) `var NUMS = __NUMS__;` / `var KEYS = __KEYS__;` のプレースホルダ未置換
      → ReferenceError でナビ JS 全体が死ぬ（刑TX341/346/349/354）。
  (2) ox-row の data-stmt が「ア〜オ」なのに、エンジンが positional な
      `['1','2','3','4','5']` ループ＋ `.ox-row[data-stmt="'+b+'"]` 直参照
      → ナビの回答が ox-grid のどの行にも同期しない（刑TX010/358/372）。

修理は正動作ファイル（刑TX337 型）のエンジン差分の機械移植のみ（本文・設問データ不変・
決定論・冪等・改行保持）：
  - `var NUMS = ["1"..."N"];` / `var KEYS = [<実 data-stmt ラベル>];` を充填（無ければ ORDER 直後に挿入）
  - `['1','2','3','4','5']` ハードコードループ → `NUMS.forEach`
  - `.ox-row[data-stmt="'+b+'"]` → `KEYS[parseInt(b,10)-1]` で実ラベルへ写像

  python -X utf8 scripts/fix-solvenav-engine-keys.py --check   # 検出のみ（終了コード1=要修理あり）
  python -X utf8 scripts/fix-solvenav-engine-keys.py --apply   # 修理を書き込み
"""
from __future__ import annotations

import glob
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEX_GLOB = str(ROOT / "outputs" / "ux" / "000_TX" / "*" / "*_lex.html")

HARDCODED = "['1','2','3','4','5']"
POSITIONAL_LOOKUP = "var row = area.querySelector('.ox-row[data-stmt=\"'+b+'\"]');"
KEYED_LOOKUP = ("var key = KEYS[parseInt(b,10)-1] || b;\n"
                "      var row = area.querySelector('.ox-row[data-stmt=\"'+key+'\"]');")


def read(p) -> str:
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, t) -> None:
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def stmt_script_span(html: str):
    for m in re.finditer(r"<script>.*?</script>", html, re.S):
        if "var STMT" in m.group(0):
            return m
    return None


def diagnose(html: str, script: str, rows: list[str]):
    reasons = []
    if "__NUMS__" in script or "__KEYS__" in script:
        reasons.append("placeholder __NUMS__/__KEYS__ 未置換（JS ReferenceError）")
    rows_positional = rows == [str(i) for i in range(1, len(rows) + 1)]
    # positional 参照が壊れるのは、ループ変数 b が 1..N の番号（固定リスト or NUMS）を回る型のみ。
    # ORDER 自体が実ラベル（ア〜オ等）を回る型（刑TX362）は b＝実ラベルで正しく同期する。
    iterates_numbers = HARDCODED in script or re.search(r"\bNUMS\.forEach\b|var NUMS\b", script)
    if POSITIONAL_LOOKUP in script and not rows_positional and iterates_numbers:
        reasons.append("positional 行参照が実ラベル %s と不一致（同期不能）" % rows)
    if HARDCODED in script and len(rows) != 5:
        reasons.append("固定 1..5 ループが記述数 %d と不一致" % len(rows))
    return reasons


def repair(script: str, rows: list[str]) -> str:
    nums = json.dumps([str(i) for i in range(1, len(rows) + 1)], ensure_ascii=False)
    keys = json.dumps(rows, ensure_ascii=False)
    nums_line = "  var NUMS = %s;                    // ['1'..'N'] positional row numbers" % nums
    keys_line = "  var KEYS = %s;                    // actual data-stmt keys in order (ア..オ or 1..5)" % keys
    if re.search(r"(?m)^[ \t]*var NUMS\b.*$", script):
        script = re.sub(r"(?m)^[ \t]*var NUMS\b.*$", lambda _: nums_line, script, count=1)
    else:
        script = re.sub(r"(?m)^([ \t]*var ORDER\b.*)$", lambda m: m.group(1) + "\n" + nums_line, script, count=1)
    if re.search(r"(?m)^[ \t]*var KEYS\b.*$", script):
        script = re.sub(r"(?m)^[ \t]*var KEYS\b.*$", lambda _: keys_line, script, count=1)
    else:
        script = re.sub(r"(?m)^([ \t]*var NUMS\b.*)$", lambda m: m.group(1) + "\n" + keys_line, script, count=1)
    script = script.replace(HARDCODED + ".forEach", "NUMS.forEach")
    script = script.replace(POSITIONAL_LOOKUP, KEYED_LOOKUP)
    return script


def main() -> int:
    apply = "--apply" in sys.argv
    found = failures = 0
    for f in sorted(glob.glob(LEX_GLOB)):
        p = Path(f)
        html = read(p)
        m = stmt_script_span(html)
        if not m:
            continue
        rows = re.findall(r'<div class="ox-row" data-stmt="([^"]+)"', html)
        if not rows:
            continue
        # 改行を LF に正規化して診断（ファイル自体は newline='' で原文保持）
        script = m.group(0).replace("\r\n", "\n")
        reasons = diagnose(html, script, rows)
        if not reasons:
            continue
        found += 1
        if not apply:
            print("  [BAD ] %s: %s" % (p.name, "; ".join(reasons)))
            continue
        fixed = repair(script, rows)
        if diagnose(html, fixed, rows):
            print("  [FAIL] %s: repair incomplete" % p.name)
            failures += 1
            continue
        crlf = "\r\n" in m.group(0)
        if crlf:
            fixed = fixed.replace("\n", "\r\n")
        html = html[:m.start()] + fixed + html[m.end():]
        write(p, html)
        print("  [FIX ] %s (%s)" % (p.name, "; ".join(reasons)))
    if found == 0:
        print("[OK] no broken solve-nav engine variants found")
        return 0
    if not apply:
        print("[FOUND] %d files need engine key repair (run with --apply)" % found)
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
