# -*- coding: utf-8 -*-
"""ARIADNE リスキン backfill（2026-06-18）

TX v11（V3 Twilight Violet）を見本にした配色・フォント統一＋「難易度別ベースカラー
染色選定」を、既存 ARIADNE 生成物と canonical/ARIADNE.html へ恒久反映する。

設計ソース = outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html（手作業で完成済み）。
そこから「css2 フォントリンク 〜 </style>」のデザインブロックを抽出し、各対象ファイルの
同区間を丸ごと差し替える（body=問題固有内容は不変）。差し替え後、各ファイルの難易度に
応じて :root の「▼ ACTIVE」プリセット（EASY ローズ / STD ブルー / HARD バイオレット）を選定する。

新規生成は更新後の canonical を clone するため、本スクリプトは既存分の一括反映用（冪等）。
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html"

# 設計ブロック = フォント css2 リンク 〜 </style>
BLOCK_RE = re.compile(r'<link href="https://fonts\.googleapis\.com/css2.*?</style>', re.S)
# 設計ブロック内の「▼ ACTIVE」プリセット（ラベル＋値2行）
ACTIVE_RE = re.compile(r'/\* ▼ ACTIVE = .*? \*/\n  --a-base:[^\n]*\n  --li:[^\n]*')

PRESETS = {
    "HARD": ("  --a-base:#f7f1e9; --a-head:#8e6e9a; --a-head-lt:#a78ab0; --a-foot:#463a50;\n"
             "  --li:#8e6e9a; --li-soft:#e6dae8; --li-line:#c7aed1; --li-deep:#534260;"),
    "STD":  ("  --a-base:#edf3f6; --a-head:#4d83a3; --a-head-lt:#6ba0bf; --a-foot:#2e5266;\n"
             "  --li:#4d83a3; --li-soft:#dde9f1; --li-line:#aecadd; --li-deep:#335066;"),
    "EASY": ("  --a-base:#fbf0f1; --a-head:#c06a86; --a-head-lt:#d690a6; --a-foot:#7e3f57;\n"
             "  --li:#c06a86; --li-soft:#f4dde4; --li-line:#e6b3c4; --li-deep:#8a4a62;"),
}

# 対象ファイル -> (難易度, ACTIVE ラベル注記)
TARGETS = {
    "outputs/ux/001_ARIADNE/001_刑法/刑JX025_ARIADNE.html":
        ("HARD", "刑JX025＝強盗予備・共犯関係からの離脱・予備の共同正犯＝難論点"),
    "outputs/ux/001_ARIADNE/001_刑法/刑JX026_ARIADNE.html":
        ("STD", "刑JX026＝正当防衛の急迫性・共同正犯と正当防衛＝頻出・中堅"),
    "outputs/ux/001_ARIADNE/001_刑法/刑JX027_ARIADNE.html":
        ("STD", "刑JX027＝過失の共同正犯・業務上過失致傷＝応用・中堅"),
    "outputs/ux/001_ARIADNE/001_刑法/刑JX028_ARIADNE.html":
        ("HARD", "刑JX028＝原因において自由な行為・不作為による幇助＝難論点重畳"),
    "outputs/ux/001_ARIADNE/001_刑法/刑JX029_ARIADNE.html":
        ("HARD", "刑JX029＝自殺関与罪の着手・承諾の錯誤（錯誤論）＝最難関級"),
    "canonical/ARIADNE.html":
        ("HARD", "テンプレ既定。問題の難易度で EASY/STD/HARD を選定する"),
}


def active_block(preset, note):
    return f"/* ▼ ACTIVE = {preset}（{note}） */\n{PRESETS[preset]}"


def main():
    src = SRC.read_text(encoding="utf-8")
    m = BLOCK_RE.search(src)
    if not m:
        raise SystemExit("FATAL: 設計ブロックを 001 から抽出できません")
    design = m.group(0)

    for rel, (preset, note) in TARGETS.items():
        p = ROOT / rel
        html = p.read_text(encoding="utf-8")
        if not BLOCK_RE.search(html):
            print(f"SKIP (block not found): {rel}")
            continue
        block = ACTIVE_RE.sub(lambda _m: active_block(preset, note), design, count=1)
        new = BLOCK_RE.sub(lambda _m: block, html, count=1)
        p.write_text(new, encoding="utf-8")
        ok = "--a-head:#5c4566" not in new and "Oswald" not in new
        print(f"{'OK ' if ok else 'WARN'} {preset:4} {rel}")


if __name__ == "__main__":
    main()
