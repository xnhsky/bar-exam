#!/usr/bin/env bash
# =============================================================================
# jx-cleanup-pdf.sh — 処理済 JX の入力 PDF を安全に削除（git rm）
#
# 方針（CLAUDE.md §8：PDF は重要資産・原本は Drive 常在）：
#   - 削除は「処理済のみ」。生成 HTML が存在し、かつ git に commit 済みである
#     ことを確認してからでないと PDF を削除しない（作業消失の防止）。
#   - 削除は git rm（履歴に残る＝復元可能）。物理 rm はしない。
#   - 既定は dry-run（表示のみ）。実削除は --commit を付けたときだけ。
#
# 使い方：
#   scripts/jx-cleanup-pdf.sh 刑 28                 # dry-run（何が消えるか表示）
#   scripts/jx-cleanup-pdf.sh 刑 28 --commit        # 実際に git rm（commit はしない）
#   scripts/jx-cleanup-pdf.sh 刑 28 29 30 --commit  # 複数まとめて
#
# 終了コード: 0=OK / 1=前提未充足（HTML 無し/未コミット）で中止 / 2=引数不正
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# 科目接頭辞 → 出力サブフォルダ
declare -A PREFIX=( [刑]=刑JX [憲]=憲JX [民]=民JX [商]=商JX [民訴]=民訴JX [刑訴]=刑訴JX [行政]=行政JX )
declare -A PDFDIR=(
  [刑]="inputs/jx/刑/重問PDF"   [憲]="inputs/jx/憲/重問PDF"   [民]="inputs/jx/民/重問PDF"
  [商]="inputs/jx/商/重問PDF"   [民訴]="inputs/jx/民訴/重問PDF" [刑訴]="inputs/jx/刑訴/重問PDF"
  [行政]="inputs/jx/行政/重問PDF"
)

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <科目> <番号...> [--commit]"; exit 2
fi

SUBJECT="$1"; shift
DO_COMMIT=0
NUMS=()
for a in "$@"; do
  if [ "$a" = "--commit" ]; then DO_COMMIT=1; else NUMS+=("$a"); fi
done

if [ -z "${PREFIX[$SUBJECT]:-}" ]; then
  echo "[FATAL] 未知の科目: $SUBJECT"; exit 2
fi
pref="${PREFIX[$SUBJECT]}"
pdfdir="${PDFDIR[$SUBJECT]}"

rc=0
to_remove=()
for n in "${NUMS[@]}"; do
  nnn=$(printf "%03d" "$n")          # HTML は3桁ゼロ埋め
  html="outputs/jx/${pref}/${pref}${nnn}.html"
  pdf="${pdfdir}/${n}.pdf"

  if [ ! -f "$pdf" ]; then
    echo "[skip] $SUBJECT 第${n}問: PDF が無い（$pdf）— 既に削除済みか未配置"; continue
  fi
  if [ ! -f "$html" ]; then
    echo "[HOLD] $SUBJECT 第${n}問: 生成 HTML が無い（$html）→ PDF を削除しない"; rc=1; continue
  fi
  # HTML が git に commit 済みか（追跡され、かつ working tree に未コミット差分が無い）
  if ! git ls-files --error-unmatch "$html" >/dev/null 2>&1; then
    echo "[HOLD] $SUBJECT 第${n}問: HTML が未追跡（未 git add/commit）→ PDF を削除しない"; rc=1; continue
  fi
  if ! git diff --quiet -- "$html" || ! git diff --cached --quiet -- "$html"; then
    echo "[HOLD] $SUBJECT 第${n}問: HTML に未コミット差分あり→ 先に commit してから再実行"; rc=1; continue
  fi
  echo "[ready] $SUBJECT 第${n}問: HTML コミット済を確認 → 削除対象 $pdf"
  to_remove+=("$pdf")
done

if [ "${#to_remove[@]}" -eq 0 ]; then
  echo "削除対象なし。"; exit "$rc"
fi

if [ "$DO_COMMIT" -eq 1 ]; then
  git rm -- "${to_remove[@]}"
  echo "[done] git rm 実行（${#to_remove[@]} 件）。commit は呼び出し側で行ってください："
  echo "       git commit -m \"chore(jx): remove processed input PDFs (${SUBJECT})\""
else
  echo "--- dry-run（--commit を付けると git rm 実行）---"
  printf '  would: git rm %s\n' "${to_remove[@]}"
fi
exit "$rc"
