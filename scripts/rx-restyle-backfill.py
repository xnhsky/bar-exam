# -*- coding: utf-8 -*-
"""RX リスキン backfill（2026-06-20）

TX v11（V3 配色・12 役割フォント・ボックス／バッジ作り込み）を見本にした
RX 論証カードの誌面デザインを、既存 RX 生成物へ恒久反映する。

設計ソース = canonical/RX.html（gold RX skeleton）。
そこから「<link rel=preconnect> 〜 </style>」の head デザインブロックを抽出し、
各既存 RX ファイルの同区間を丸ごと差し替える。

  ・差し替えるのは <head> のデザインブロック（フォントリンク＋<style>）のみ。
  ・<body>（＝論点固有の中身）と <script>（toggleNorm / lexiaAnswer）は不変。
  ・よって Lexia 取込契約（.self-check-quiz / data-correct-value / .quiz-* /
    data-explanation / <title>=論点名 / </body> 1 回）は完全に保持される。
  ・既存クラス名（.card / h1 / .src / h2 / .lead / .norm-toggle / .norm-box /
    .refs / .self-check-quiz / .quiz-* / .qnum）は skeleton CSS が踏襲するので、
    masthead 無しの素の body でも見出し・ボックス・バッジが TX 風に化粧される。

新規生成は更新後の canonical/RX.html を clone するため、本スクリプトは
既存分の一括反映用（冪等：再実行しても重複フォントリンクを生まない）。

Usage:
    python scripts/rx-restyle-backfill.py            # outputs/ux/001_RX 配下の全 RX を反映
    python scripts/rx-restyle-backfill.py --dry-run  # 変更対象の確認のみ（書き込まない）
    python scripts/rx-restyle-backfill.py outputs/ux/001_RX/001_刑法/刑JX042  # 範囲限定
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SKELETON = ROOT / "canonical" / "RX.html"
DEFAULT_DIR = ROOT / "outputs" / "ux" / "001_RX"

# canonical/RX.html の head デザインブロック = preconnect 〜 </style>
SKELETON_BLOCK_RE = re.compile(
    r'<link rel="preconnect".*?</style>', re.S)

# 既存ファイル側で差し替える区間：
#   （前回反映で入った preconnect / fonts リンクがあれば一緒に飲み込み）<style>…</style>
#   → 冪等（再実行でフォントリンクが二重化しない）
TARGET_BLOCK_RE = re.compile(
    r'(?:<link rel="preconnect"[^>]*>\s*)*'
    r'(?:<link href="https://fonts\.googleapis\.com/css2[^>]*>\s*)?'
    r'<style>.*?</style>',
    re.S)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv

    if not SKELETON.exists():
        raise SystemExit(f"FATAL: skeleton が無い: {SKELETON}")
    design = SKELETON_BLOCK_RE.search(SKELETON.read_text(encoding="utf-8"))
    if not design:
        raise SystemExit("FATAL: canonical/RX.html から head デザインブロックを抽出できません")
    design_block = design.group(0)

    targets_root = Path(args[0]) if args else DEFAULT_DIR
    if not targets_root.is_absolute():
        targets_root = ROOT / targets_root
    files = sorted(targets_root.rglob("*.html"))
    if not files:
        raise SystemExit(f"対象 RX ファイルが見つかりません: {targets_root}")

    changed = skipped = 0
    for p in files:
        html = p.read_text(encoding="utf-8")
        if "self-check-quiz" not in html:
            print(f"SKIP (RX でない): {p.relative_to(ROOT)}")
            skipped += 1
            continue
        if not TARGET_BLOCK_RE.search(html):
            print(f"SKIP (<style> 区間なし): {p.relative_to(ROOT)}")
            skipped += 1
            continue
        new = TARGET_BLOCK_RE.sub(lambda _m: design_block, html, count=1)
        if new == html:
            print(f"OK   (既に最新): {p.relative_to(ROOT)}")
            skipped += 1
            continue
        # 安全確認：契約要素が消えていないこと
        if new.count("</body>") != 1 or "self-check-quiz" not in new:
            print(f"WARN (契約検査 NG・スキップ): {p.relative_to(ROOT)}")
            skipped += 1
            continue
        if not dry:
            p.write_text(new, encoding="utf-8")
        print(f"{'DRY ' if dry else 'DONE'} {p.relative_to(ROOT)}")
        changed += 1

    print(f"\n=== rx-restyle-backfill: changed={changed}, skipped={skipped}, "
          f"total={len(files)}{' (dry-run)' if dry else ''} ===")


if __name__ == "__main__":
    main()
