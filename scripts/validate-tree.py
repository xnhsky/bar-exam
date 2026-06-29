# -*- coding: utf-8 -*-
"""validate-tree.py — ARBOR 横向き樹形図 (Lexia 取込用 TREE 副産物) の軽量検証

Usage:
    python scripts/validate-tree.py <file.html>
    例: python scripts/validate-tree.py outputs/ux/003_TREE/001_刑法/刑JX042_TREE.html

位置づけ:
    ARBOR の完全仕様 (S1-S20) は外部 arbor リポジトリの verify.py にあり、ローカル専用。
    リモート実行 (Claude Code on the web) には arbor repo が無いため、本スクリプトは
    canonical/ARBOR.html (vendored 正典) と同形であることを保証する **構造＋Lexia 取込の
    不変条件** だけを機械検査する軽量ゲート。フル S1-S20 はローカルバッチ側で担保する。

Checks (T1-T9):
    T1: ファイルが存在し非空
    T2: <title> が非空かつ 'ARBOR' を含む (例: '... — 横向き樹形図 / ARBOR v5.0')
    T3: ファイル名が *_TREE.html (Lexia が科目＋TREE カテゴリを接尾辞判定)
    T4: 13 分枝構造 = class="mm-name" が 13 個 (ARBOR の幹分枝)            [本数差は WARNING]
    T5: 葉 class="mm-leaf" が 40 個以上 (標準密度 57)                       [不足は WARNING]
    T6: 問題ノード class="mm-q" が 10 個以上 (標準 15)                      [不足は WARNING]
    T7: '</body>' リテラルが <script> 内に出現しない (Lexia killer・致命)
    T8: ファイルサイズ 30KB〜200KB (標準 約 68KB)                          [範囲外は WARNING]
    T9: <svg> を使っていない (ARBOR は CSS グリッド樹形図・SVG は別系統)    [出現は WARNING]

Exit code: 0 = PASS (ERROR 0 / WARNING 許容), 1 = ERROR あり, 2 = 使い方誤り
"""
import io
import re
import sys
from pathlib import Path

# Windows コンソールでも UTF-8 で確実に出す
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

errors = []
warnings = []


def attr_value(tag: str, name: str) -> str | None:
    m = re.search(rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1", tag, re.I | re.S)
    return m.group(2) if m else None


def has_class(tag: str, class_name: str) -> bool:
    value = attr_value(tag, "class")
    return bool(value and class_name in value.split())


def class_count(html: str, class_name: str) -> int:
    return sum(
        1
        for m in re.finditer(r"<[a-zA-Z][\w:-]*\b[^>]*>", html, re.I | re.S)
        if has_class(m.group(0), class_name)
    )


def err(msg):
    errors.append(msg)
    print(f"[ERROR] {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"[WARN ] {msg}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])

    # T1
    if not path.is_file():
        err(f"T1: ファイルが存在しない: {path}")
        return 1
    html = path.read_text(encoding="utf-8", errors="replace")
    size = len(html.encode("utf-8"))
    if size == 0:
        err(f"T1: ファイルが空: {path}")
        return 1

    # T2: <title> 非空かつ ARBOR を含む
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    title = (m.group(1).strip() if m else "")
    if not title:
        err("T2: <title> が空")
    elif "ARBOR" not in html[: html.find("</head>") if "</head>" in html else len(html)] and "ARBOR" not in title:
        warn("T2: <title>/head に 'ARBOR' 表記が見当たらない (正典題号の踏襲推奨)")

    # T3: 命名
    if not path.name.endswith("_TREE.html"):
        err(f"T3: ファイル名が *_TREE.html でない: {path.name} (Lexia の TREE カテゴリ判定に必須)")

    # T4: 13 分枝
    n_name = class_count(html, "mm-name")
    if n_name == 0:
        err("T4: class=\"mm-name\" が 0 個 (ARBOR 樹形構造が無い・素材取り違え疑い)")
    elif n_name != 13:
        warn(f"T4: 幹分枝 mm-name が 13 本でない (実際 {n_name} 本・ARBOR 標準は 13)")

    # T5: 葉
    n_leaf = class_count(html, "mm-leaf")
    if n_leaf < 40:
        warn(f"T5: 葉 mm-leaf が {n_leaf} 個 (標準密度 57・40 未満は薄い)")

    # T6: 問題ノード
    n_q = class_count(html, "mm-q")
    if n_q < 10:
        warn(f"T6: 問題ノード mm-q が {n_q} 個 (標準 15・10 未満は薄い)")

    # T7: <script> 内の </body> リテラル (Lexia killer)
    for sm in re.finditer(r"<script\b[^>]*>(.*?)</script>", html, re.S | re.I):
        if "</body>" in sm.group(1):
            err("T7: <script> 内に '</body>' リテラルがある (Lexia 正規表現マッチで全機能死亡)")
            break

    # T8: サイズ
    if not (30 * 1024 <= size <= 200 * 1024):
        warn(f"T8: ファイルサイズ {size/1024:.1f}KB (標準 約 68KB・推奨 30〜200KB)")

    # T9: SVG 不使用 (ARBOR は CSS グリッド)
    if re.search(r"<svg\b", html, re.I):
        warn("T9: <svg> が含まれる (ARBOR は CSS グリッド樹形図・SVG は TX/JX 系統)")

    # サマリ
    print("-" * 56)
    print(f"TREE 検証: {path.name}  title='{title[:40]}'")
    print(f"  分枝 mm-name={n_name} / 葉 mm-leaf={n_leaf} / 問題 mm-q={n_q} / {size/1024:.1f}KB")
    print(f"  ERROR={len(errors)}  WARNING={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
