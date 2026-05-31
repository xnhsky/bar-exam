#!/usr/bin/env bash
#
# remote-intake.sh — 外出先ドロップゾーンの PDF を batch が拾える形へ正規化する取り込み導線。
#
# 背景:
#   batch-tx / night-batch-runner.ps1 は inputs/{tx|jx}-pdfs/ の *直下* の {NNN}.pdf を読む。
#   外出先からアップロードした PDF は専用フォルダ _remote-inbox/ に入る（任意のファイル名）。
#   本スクリプトはそれを CLAUDE.md §2-3 の命名規則で {NNN}.pdf へ正規化し、直下へ展開する。
#
# 役割（CLAUDE.md §2-3 準拠）:
#   - ファイル名の *最初の連続数字* を抽出
#   - 3 桁未満は前ゼロ埋め（1→001 / 22→022）。3 桁超はそのまま（1234→1234）
#   - 数字が無いファイルは *推定せずスキップ*（無断推定禁止・§2-3 rule 5）
#   - 展開先に同番号が既存なら上書きせずスキップ（§3-2 上書き確認の精神）
#
# 使い方:
#   bash scripts/remote-intake.sh                 # TX: _remote-inbox/*.pdf → inputs/tx-pdfs/{NNN}.pdf（コピー）
#   bash scripts/remote-intake.sh --jx            # JX 版（inputs/jx-pdfs/）
#   bash scripts/remote-intake.sh --move          # コピーではなく移動（inbox から消す）
#   bash scripts/remote-intake.sh --dry-run       # 判定結果を表示するだけ

set -euo pipefail

# === 引数解析 ===
SERIES="tx"
DO_MOVE=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --jx) SERIES="jx" ;;
    --tx) SERIES="tx" ;;
    --move) DO_MOVE=1 ;;
    --dry-run) DRY_RUN=1 ;;
    *) echo "不明なオプション: $arg" >&2; exit 2 ;;
  esac
done

# === プロジェクトルートへ移動 ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

DEST_DIR="inputs/${SERIES}-pdfs"
INBOX_DIR="${DEST_DIR}/_remote-inbox"

echo "=== remote-intake 開始 $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "シリーズ: ${SERIES^^} / inbox: ${INBOX_DIR} → 展開先: ${DEST_DIR}/"
echo "モード: $([ "$DO_MOVE" -eq 1 ] && echo 移動 || echo コピー)$([ "$DRY_RUN" -eq 1 ] && echo ' / --dry-run')"

if [ ! -d "$INBOX_DIR" ]; then
  echo "inbox がありません: $INBOX_DIR" >&2
  exit 1
fi

# === inbox の PDF を走査 ===
shopt -s nullglob
PDFS=("$INBOX_DIR"/*.pdf "$INBOX_DIR"/*.PDF)
shopt -u nullglob

if [ ${#PDFS[@]} -eq 0 ]; then
  echo "inbox に PDF がありません。終了。"
  exit 0
fi

PROMOTED=0
SKIPPED=0
PROMOTED_NUMS=()

for src in "${PDFS[@]}"; do
  base="$(basename "$src")"
  name="${base%.*}"

  # 最初の連続数字を抽出
  num="$(printf '%s' "$name" | grep -oE '[0-9]+' | head -n1 || true)"
  if [ -z "$num" ]; then
    echo "  [SKIP] 数字なし → 番号確認が必要（§2-3 rule 5）: $base"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # 10 進強制で 3 桁ゼロ埋め（3 桁超はそのまま）
  serial="$(printf '%03d' "$((10#$num))")"
  dest="${DEST_DIR}/${serial}.pdf"

  if [ -e "$dest" ]; then
    echo "  [SKIP] 展開先に既存（上書きしない）: $base → ${serial}.pdf"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [DRY ] $base → ${dest}"
    PROMOTED=$((PROMOTED + 1))
    PROMOTED_NUMS+=("$serial")
    continue
  fi

  if [ "$DO_MOVE" -eq 1 ]; then
    git mv -f "$src" "$dest" 2>/dev/null || mv "$src" "$dest"
    echo "  [MOVE] $base → ${serial}.pdf"
  else
    cp "$src" "$dest"
    echo "  [COPY] $base → ${serial}.pdf"
  fi
  PROMOTED=$((PROMOTED + 1))
  PROMOTED_NUMS+=("$serial")
done

echo "---"
echo "展開: ${PROMOTED} 件 / スキップ: ${SKIPPED} 件"

if [ "$PROMOTED" -gt 0 ] && [ "$DRY_RUN" -eq 0 ]; then
  # 最若番を案内
  IFS=$'\n' first="$(printf '%s\n' "${PROMOTED_NUMS[@]}" | sort | head -n1)"; unset IFS
  if [ "$SERIES" = "tx" ]; then
    echo "次のステップ: /batch-tx ${first}  （バッチ）または  /new-tx ${DEST_DIR}/${first}.pdf"
  else
    echo "次のステップ: /new-jx ${DEST_DIR}/${first}.pdf  （JX は単発運用が安定）"
  fi
fi

echo "=== remote-intake 完了 $(date '+%Y-%m-%d %H:%M:%S') ==="
