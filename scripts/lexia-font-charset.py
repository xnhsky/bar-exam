#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lexia 配信 HTML が実際に使う文字集合を抽出する（オフラインフォント同梱の前段・2026-08-26）。

TX/JX/RX/ARIADNE/TREE は 11 書体すべてを Google Fonts から読むため、iPad がオフラインだと
全役割が端末のフォールバック 1〜2 書体へ潰れる（CLAUDE.md §3「実機で『フォントが違う』ときの
一次切り分け」／LEX-442 の真因）。恒久対処は **Lexia アプリ側に woff2 を同梱**することだが、
日本語フォントは 1 書体 2〜3MB あり、35 face をそのまま積むと 100MB 級になる。

そこで **corpus が実際に使う文字だけ**へサブセット化する。本スクリプトはその文字集合
（＝サブセットの単一情報源）を吐く。build-offline-fonts.py がこれを読んで woff2 を作る。

収集対象:
  - Lexia が取り込む HTML 全部（outputs/000_TX・001_JX・ux・references）の**生テキスト**。
    タグを剥がさない＝`<script>` 内の UI 文言・CSS の `content:`（✍ ANSWER・📚BASIS 等）も
    誌面に出るため、取りこぼすとその字だけ端末フォントに落ちる。
  - 安全網（既定 ON・`--no-safety-net` で無効）：JIS X 0208 第1水準漢字（2,965 字）＋
    全ひらがな・カタカナ＋ASCII＋和文約物。**今後生成する問題**が corpus に無い字を使っても
    サブセットに入っているようにする（外れた字はその 1 文字だけ端末フォントで描かれる＝
    豆腐にはならないが書体が混ざる）。

  python scripts/lexia-font-charset.py                 # 既定の出力先へ書き出し
  python scripts/lexia-font-charset.py --stats         # 内訳だけ表示（書き込まない）
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = ("outputs/000_TX", "outputs/001_JX", "outputs/ux", "references")
OUT = ROOT / "docs" / "data" / "lexia-offline-charset.txt"

# 誌面に出ないもの（制御文字・サロゲート・私用領域）は落とす
def _keep(ch: str) -> bool:
    if ch in ("\t", "\n", "\r"):
        return False
    cat = unicodedata.category(ch)
    return cat not in ("Cc", "Cs", "Co", "Cn")


def jis_level1() -> set[str]:
    """JIS X 0208 第1水準漢字（区 16〜47）を euc_jp 経由で列挙する（外部データ不要・決定論）。"""
    out: set[str] = set()
    for ku in range(16, 48):
        for ten in range(1, 95):
            try:
                out.add(bytes([0xA0 + ku, 0xA0 + ten]).decode("euc_jp"))
            except UnicodeDecodeError:
                continue
    return out


def safety_net() -> set[str]:
    out = set(jis_level1())
    out |= {chr(c) for c in range(0x3041, 0x30FF + 1)}          # ひらがな・カタカナ
    out |= {chr(c) for c in range(0x20, 0x7F)}                   # ASCII
    out |= {chr(c) for c in range(0xFF01, 0xFF5F)}               # 全角英数記号
    out |= set("　、。・「」『』（）〔〕【】〈〉《》〜…‥ー―‐±×÷≒≠≦≧∴∵§¶†‡№㎡℃°′″")
    out |= set("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ")
    return {c for c in out if _keep(c)}


def scan(roots=SCAN_ROOTS) -> set[str]:
    chars: set[str] = set()
    files = 0
    for r in roots:
        base = ROOT / r
        if not base.exists():
            continue
        for f in base.rglob("*.html"):
            files += 1
            chars |= set(f.read_text(encoding="utf-8", errors="ignore"))
    return {c for c in chars if _keep(c)}, files  # type: ignore[return-value]


def breakdown(chars: set[str]) -> dict[str, int]:
    def n(lo: int, hi: int) -> int:
        return sum(1 for c in chars if lo <= ord(c) <= hi)
    return {
        "漢字(CJK統合)": n(0x4E00, 0x9FFF) + n(0x3400, 0x4DBF),
        "かな": n(0x3040, 0x30FF),
        "ASCII": n(0x20, 0x7E),
        "和文約物・記号": n(0x2000, 0x33FF),
        "全角英数": n(0xFF00, 0xFFEF),
        "絵文字ほか": sum(1 for c in chars if ord(c) > 0xFFFF),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-safety-net", action="store_true", help="corpus の実使用文字だけにする")
    ap.add_argument("--stats", action="store_true", help="書き込まず内訳だけ表示")
    ap.add_argument("-o", "--out", default=str(OUT))
    a = ap.parse_args()

    used, files = scan()
    print(f"走査 {files} ファイル / corpus 実使用 {len(used)} 字")
    for k, v in breakdown(used).items():
        print(f"    {k}: {v}")

    total = set(used)
    if not a.no_safety_net:
        net = safety_net()
        added = net - used
        total |= net
        print(f"安全網（JIS第1水準＋かな＋ASCII＋約物）: +{len(added)} 字")

    ordered = "".join(sorted(total))
    print(f"→ サブセット対象 合計 {len(total)} 字")
    if a.stats:
        return 0
    out = Path(a.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(ordered + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] {out.relative_to(ROOT)} に書き出した（{len(ordered)} 字）")

    # corpus 実使用ぶんだけを別ファイルにも出す。被覆検査が「誌面に実害が出る欠落」と
    # 「安全網ぶんの欠落（将来リスクどまり）」を切り分けるために使う。
    corpus_out = out.with_suffix(".corpus.txt")
    corpus_out.write_text("".join(sorted(used)) + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] {corpus_out.relative_to(ROOT)} に書き出した（corpus 実使用 {len(used)} 字）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
