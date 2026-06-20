# -*- coding: utf-8 -*-
"""validate-rx.py — RX 論証カード (Lexia 取込用) の検証

Usage:
    python scripts/validate-rx.py <output_dir> <rx_basename>
    例: python scripts/validate-rx.py outputs/ux/001_RX/刑RX 刑RX032

検証対象: <output_dir>/<rx_basename>_*.html (1 ファイル = 1 論点)

Checks (R1-R9):
    R1: 対象ファイルが 1 つ以上存在する
    R2: 連番が 1 始まりで欠番なし
    R3: <title> が非空 (かつ 'Document' 等のプレースホルダでない)
    R4: .self-check-quiz が 2〜4 個
    R5: 各クイズに data-correct-value (全角 ○/×) がある
    R6: 各クイズに .quiz-question (非空) がある
    R7: 各クイズに data-explanation (非空) がある  [欠落は WARNING]
    R8: '</body>' の出現が 1 回のみ (script 内リテラル禁止 — Lexia killer)
    R9: ファイルサイズ 4KB〜300KB / 外部リソース参照なし
        (作り込みフォント Google Fonts の link は許容・それ以外の外部参照は WARNING)
    R10: 正典 AXIOM 整合 [WARNING] — 作り込みフォント link / カード幅 920px / 規範レモン(#fff7a8)

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


def err(msg):
    errors.append(msg)
    print(f"[ERROR] {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"[WARN ] {msg}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    out_dir = Path(sys.argv[1])
    basename = sys.argv[2]

    if not out_dir.is_dir():
        err(f"出力ディレクトリが存在しない: {out_dir}")
        return 1

    files = sorted(out_dir.glob(f"{basename}_*.html"))
    # R1
    if not files:
        err(f"R1: {basename}_*.html が 1 つも無い ({out_dir})")
        return 1

    # R2: 連番チェック
    nums = []
    for f in files:
        m = re.fullmatch(re.escape(basename) + r"_(\d+)\.html", f.name)
        if m:
            nums.append(int(m.group(1)))
        else:
            warn(f"R2: 連番形式でないファイル名 (検証対象外にしない): {f.name}")
    nums.sort()
    if nums and nums != list(range(1, len(nums) + 1)):
        err(f"R2: 連番が 1 始まり欠番なしでない: {nums}")

    for f in files:
        html = f.read_text(encoding="utf-8", errors="replace")
        tag = f.name

        # R3: title
        m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
        title = (m.group(1).strip() if m else "")
        if not title:
            err(f"R3: <title> が無い/空: {tag}")
        elif title.lower() in ("document", "untitled", "card"):
            err(f"R3: <title> がプレースホルダ ('{title}'): {tag}")

        # R4: quiz count
        quizzes = re.findall(
            r'<div[^>]*class="[^"]*self-check-quiz[^"]*"[^>]*>', html)
        n = len(quizzes)
        if n == 0:
            err(f"R4: self-check-quiz が無い: {tag}")
        elif n < 2 or n > 4:
            warn(f"R4: クイズ数が推奨範囲 (2〜4) 外: {n} 問: {tag}")

        # R5: data-correct-value (全角 ○/×)
        for q in quizzes:
            m = re.search(r'data-correct-value="([^"]*)"', q)
            if not m:
                err(f"R5: data-correct-value 欠落クイズあり: {tag}")
            elif m.group(1) not in ("○", "×"):
                err(f"R5: data-correct-value が全角 ○/× でない ('{m.group(1)}'): {tag}")

        # R6: quiz-question 非空 (個数で近似チェック)
        qq = re.findall(
            r'class="[^"]*quiz-question[^"]*"[^>]*>\s*([^<]+)', html)
        if len([t for t in qq if t.strip()]) < n:
            err(f"R6: 非空の .quiz-question がクイズ数より少ない: {tag}")

        # R7: data-explanation
        n_expl = len([1 for q in quizzes
                      if re.search(r'data-explanation="[^"]+?"', q)])
        if n_expl < n:
            warn(f"R7: data-explanation 欠落 {n - n_expl} 問 (弱点克服帳で解説が出ない): {tag}")

        # R8: </body> リテラル (Lexia killer)
        if html.count("</body>") != 1:
            err(f"R8: '</body>' の出現が {html.count('</body>')} 回 "
                f"(script 内リテラル禁止・正しくは 1 回): {tag}")

        # R9: サイズと外部参照
        size = f.stat().st_size
        if size < 4 * 1024:
            err(f"R9: ファイルが小さすぎる ({size}B < 4KB) — 内容欠落の疑い: {tag}")
        elif size > 300 * 1024:
            err(f"R9: ファイルが大きすぎる ({size // 1024}KB > 300KB): {tag}")
        ext = re.findall(r'(?:src|href)="(https?://[^"]+)"', html)
        # 作り込みフォント（Google Fonts）の link は正典仕様なので許容。それ以外を WARNING。
        non_font = [u for u in ext if not re.search(r'fonts\.(?:googleapis|gstatic)\.com', u)]
        if non_font:
            warn(f"R9: 外部リソース参照あり (オフラインで欠ける): {non_font[0]} : {tag}")

        # R10: 正典 AXIOM 整合（作り込み品質の機械チェック・当面 WARNING）
        if not re.search(r"fonts\.googleapis\.com/css2", html):
            warn(f"R10: 作り込みフォント link が無い (AXIOM 正典と不一致): {tag}")
        if "max-width:920px" not in html.replace(" ", "").replace("\n", ""):
            warn(f"R10: カード幅 920px でない (AXIOM 正典と不一致): {tag}")
        if "#fff7a8" not in html.lower():
            warn(f"R10: 規範ボックスがレモンイエロー(#fff7a8)でない: {tag}")

    print(f"\n=== validate-rx: {basename} — files={len(files)}, "
          f"ERROR={len(errors)}, WARNING={len(warnings)} ===")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
