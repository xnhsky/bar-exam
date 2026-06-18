#!/usr/bin/env bash
# =============================================================================
# jx-cleanup-pdf.sh — 処理済 JX の入力 PDF＋講義逐語 を安全に削除（git rm）
#
# 方針（CLAUDE.md §8 / 2026-06-08 改訂：入力 PDF・逐語の原本は Drive 常在へ）：
#   - 「生成後に inputs から PDF・逐語を消す」運用（ユーザー指示 2026-06-08）。
#     TX の「抽出PDF」と同型に、Drive の {2 JX_論 文}\{00N_科目}\重問PDF\・\講義逐語\
#     を入力原本の恒久バックアップとし、inputs 側は git rm で消す（履歴に残り復元可）。
#   - 削除の前提（多重ガード。1 つでも欠ければ削除しない）：
#       ① 生成 HTML が存在し、git に commit 済み（未コミット差分も無い）
#       ② その PDF・逐語が Drive バックアップに存在（jx-deploy.ps1 が配置時にコピー済）
#   - 削除は git rm（履歴に残る＝復元可能）。物理 rm はしない。
#   - 既定は dry-run（表示のみ）。実削除は --commit を付けたときだけ。
#
# 使い方：
#   scripts/jx-cleanup-pdf.sh 刑 28                 # dry-run（何が消えるか表示）
#   scripts/jx-cleanup-pdf.sh 刑 28 --commit        # 実際に git rm（commit はしない）
#   scripts/jx-cleanup-pdf.sh 刑 28 29 30 --commit  # 複数まとめて
#   scripts/jx-cleanup-pdf.sh 刑 28 --commit --no-drive-check  # Drive 未マウント時の緊急用
#
# 終了コード: 0=OK / 1=前提未充足（HTML 未コミット/Drive 未バックアップ等）で中止 / 2=引数不正
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# 科目接頭辞 → 出力サブフォルダ
declare -A PREFIX=( [刑]=刑JX [憲]=憲JX [民]=民JX [商]=商JX [民訴]=民訴JX [刑訴]=刑訴JX [行政]=行政JX )
declare -A SUBJDIR=( [刑]=001_刑法 [刑訴]=002_刑事訴訟法 [民]=003_民法 [商]=004_商法 [民訴]=005_民事訴訟法 [行政]=006_行政法 [憲]=007_憲法 )
declare -A PDFDIR=(
  [刑]="inputs/jx/刑/重問PDF"   [憲]="inputs/jx/憲/重問PDF"   [民]="inputs/jx/民/重問PDF"
  [商]="inputs/jx/商/重問PDF"   [民訴]="inputs/jx/民訴/重問PDF" [刑訴]="inputs/jx/刑訴/重問PDF"
  [行政]="inputs/jx/行政/重問PDF"
)
declare -A TRANSDIR=(
  [刑]="inputs/jx/刑/講義逐語"   [憲]="inputs/jx/憲/講義逐語"   [民]="inputs/jx/民/講義逐語"
  [商]="inputs/jx/商/講義逐語"   [民訴]="inputs/jx/民訴/講義逐語" [刑訴]="inputs/jx/刑訴/講義逐語"
  [行政]="inputs/jx/行政/講義逐語"
)
# 科目 → Drive バックアップ科目フォルダ名（重問PDF / 講義逐語 はこの直下）
declare -A DRIVE_HTML=(
  [刑]=001_刑法 [刑訴]=002_刑事訴訟法 [民]=003_民法 [商]=004_商法
  [民訴]=005_民事訴訟法 [行政]=006_行政法 [憲]=007_憲法
)
# Drive のマウント形態は PC により異なる（H:\マイドライブ … or D:\GoogleDrive …）。
# 候補を順に試し、最初に存在したものを DRIVE_ROOT に採用する。
DRIVE_ROOT=""
for cand in \
  "/h/マイドライブ/CATALINA＿G共有/■予備試験進行中/2 JX_論 文" \
  "/d/GoogleDrive/CATALINA＿G共有/■予備試験進行中/2 JX_論 文" \
  "/g/マイドライブ/CATALINA＿G共有/■予備試験進行中/2 JX_論 文" ; do
  if [ -d "$cand" ]; then DRIVE_ROOT="$cand"; break; fi
done
# どれも無ければ既定（H:）を残す＝未マウント扱いで以降のガードが働く
[ -z "$DRIVE_ROOT" ] && DRIVE_ROOT="/h/マイドライブ/CATALINA＿G共有/■予備試験進行中/2 JX_論 文"

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <科目> <番号...> [--commit] [--no-drive-check]"; exit 2
fi

SUBJECT="$1"; shift
DO_COMMIT=0
DRIVE_CHECK=1
NUMS=()
for a in "$@"; do
  case "$a" in
    --commit)         DO_COMMIT=1 ;;
    --no-drive-check) DRIVE_CHECK=0 ;;
    *)                NUMS+=("$a") ;;
  esac
done

if [ -z "${PREFIX[$SUBJECT]:-}" ]; then
  echo "[FATAL] 未知の科目: $SUBJECT"; exit 2
fi
pref="${PREFIX[$SUBJECT]}"
pdfdir="${PDFDIR[$SUBJECT]}"
transdir="${TRANSDIR[$SUBJECT]}"
drive_subj="${DRIVE_HTML[$SUBJECT]}"
drive_pdf_dir="${DRIVE_ROOT}/${drive_subj}/重問PDF"
drive_trans_dir="${DRIVE_ROOT}/${drive_subj}/講義逐語"

# Drive マウント確認
drive_mounted=0
if [ -d "$DRIVE_ROOT" ]; then drive_mounted=1; fi
if [ "$DRIVE_CHECK" -eq 1 ] && [ "$drive_mounted" -eq 0 ]; then
  echo "[FATAL] Drive 未マウント（$DRIVE_ROOT が無い）。バックアップ確認不可のため中止。"
  echo "        Drive をマウントするか、緊急時のみ --no-drive-check で実行（git 履歴のみが復元元）。"
  exit 1
fi

# 番号 n に一致する逐語ファイル（重問逐語NN / 旧 重問NN・.txt 優先）を探す
find_transcript() {
  local n="$1" f base num
  for f in "$transdir"/*.txt "$transdir"/*.md; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    if [[ "$base" =~ 重問(逐語)?0*([0-9]+) ]]; then
      num="${BASH_REMATCH[2]}"
      if [ "$((10#$num))" -eq "$n" ]; then echo "$f"; return 0; fi
    fi
  done
  return 1
}

rc=0
to_remove=()
for n in "${NUMS[@]}"; do
  nnn=$(printf "%03d" "$n")          # HTML は3桁ゼロ埋め
  html="outputs/001_JX/${SUBJDIR[$SUBJECT]}/${pref}${nnn}.html"
  pdf="${pdfdir}/${n}.pdf"
  trans="$(find_transcript "$n" || true)"

  if [ ! -f "$pdf" ] && [ -z "$trans" ]; then
    echo "[skip] $SUBJECT 第${n}問: PDF も逐語も無い（既に削除済みか未配置）"; continue
  fi
  # ① HTML 存在＋コミット済み
  if [ ! -f "$html" ]; then
    echo "[HOLD] $SUBJECT 第${n}問: 生成 HTML が無い（$html）→ 削除しない"; rc=1; continue
  fi
  if ! git ls-files --error-unmatch "$html" >/dev/null 2>&1; then
    echo "[HOLD] $SUBJECT 第${n}問: HTML が未追跡（未 git add/commit）→ 削除しない"; rc=1; continue
  fi
  if ! git diff --quiet -- "$html" || ! git diff --cached --quiet -- "$html"; then
    echo "[HOLD] $SUBJECT 第${n}問: HTML に未コミット差分あり→ 先に commit してから再実行"; rc=1; continue
  fi
  # ② Drive バックアップ存在（--no-drive-check ならスキップ）
  if [ "$DRIVE_CHECK" -eq 1 ]; then
    if [ -f "$pdf" ] && [ ! -f "${drive_pdf_dir}/${n}.pdf" ]; then
      echo "[HOLD] $SUBJECT 第${n}問: PDF の Drive バックアップ無し（${drive_pdf_dir}/${n}.pdf）→ 先に jx-deploy で配置"; rc=1; continue
    fi
    if [ -n "$trans" ]; then
      tbase="$(basename "$trans")"
      if [ ! -f "${drive_trans_dir}/${tbase}" ]; then
        echo "[HOLD] $SUBJECT 第${n}問: 逐語の Drive バックアップ無し（${drive_trans_dir}/${tbase}）→ 先に jx-deploy で配置"; rc=1; continue
      fi
    fi
  fi
  # ここまで通れば削除対象に追加
  if [ -f "$pdf" ]; then
    echo "[ready] $SUBJECT 第${n}問: HTML コミット済＋Drive バックアップ確認 → 削除対象 $pdf"
    to_remove+=("$pdf")
  fi
  if [ -n "$trans" ]; then
    echo "[ready] $SUBJECT 第${n}問: → 削除対象 $trans"
    to_remove+=("$trans")
  fi
done

if [ "${#to_remove[@]}" -eq 0 ]; then
  echo "削除対象なし。"; exit "$rc"
fi

if [ "$DO_COMMIT" -eq 1 ]; then
  git rm -- "${to_remove[@]}"
  echo "[done] git rm 実行（${#to_remove[@]} 件）。commit は呼び出し側で行ってください："
  echo "       git commit -m \"chore(jx): remove processed input PDF+逐語 (${SUBJECT})\""
else
  echo "--- dry-run（--commit を付けると git rm 実行）---"
  printf '  would: git rm %s\n' "${to_remove[@]}"
fi
exit "$rc"
