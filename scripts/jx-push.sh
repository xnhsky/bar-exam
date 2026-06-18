#!/usr/bin/env bash
# =============================================================================
# jx-push.sh — リモートコンテナからの成果物回収＝git commit & push の動線
#
# 背景：リモート実行（Claude Code on the web 等）は ephemeral でコンテナが回収される。
#   生成した HTML は git に commit/push して GitHub に残すのが唯一の永続化（CLAUDE.md §9）。
#   本スクリプトは「ファイルを回収して push する」一連の動線を1コマンドにまとめる。
#
# 動作：
#   1) 対象（既定 outputs/001_JX 配下の追加/変更/未追跡 HTML）を git add
#   2) 差分が無ければ何もしない
#   3) commit（メッセージは引数 or 既定）
#   4) git push -u origin <現ブランチ> をネットワークエラー時に指数バックオフ再試行
#      （2s, 4s, 8s, 16s／最大4回）
#   5) 回収マニフェスト（scripts/jx-retrieval-manifest.py）を表示
#
# 使い方：
#   scripts/jx-push.sh "feat(jx): 刑JX028 を生成保存（J1〜J21 PASS）"
#   scripts/jx-push.sh "msg" outputs/001_JX/001_刑法/刑JX028.html      # 対象を明示
#   scripts/jx-push.sh --dry "msg"                            # add/commit せず確認のみ
# =============================================================================
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DRY=0
if [ "${1:-}" = "--dry" ]; then DRY=1; shift; fi

MSG="${1:-chore(jx): persist generated outputs}"
shift || true
TARGETS=("$@")
if [ "${#TARGETS[@]}" -eq 0 ]; then
  TARGETS=("outputs/001_JX")
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "=== JX push 動線（branch=$BRANCH）==="

# 1) stage
echo "--- stage: ${TARGETS[*]} ---"
if [ "$DRY" -eq 0 ]; then
  git add -- "${TARGETS[@]}"
fi

# 2) 差分確認
if git diff --cached --quiet; then
  echo "ステージ差分なし（既に最新 or 変更なし）。push をスキップ。"
  python3 scripts/jx-retrieval-manifest.py 2>/dev/null || true
  exit 0
fi

echo "--- staged files ---"
git -c core.quotepath=false diff --cached --name-only | sed 's/^/  + /'

if [ "$DRY" -eq 1 ]; then
  echo "[dry-run] commit/push は行いません。"
  exit 0
fi

# 3) commit
git commit -m "$MSG" || { echo "[FATAL] commit 失敗"; exit 1; }

# 4) push with exponential backoff
delays=(2 4 8 16)
attempt=0
ok=0
while :; do
  if git push -u origin "$BRANCH"; then ok=1; break; fi
  if [ "$attempt" -ge "${#delays[@]}" ]; then break; fi
  d="${delays[$attempt]}"
  echo "[retry] push 失敗。${d}s 待って再試行（$((attempt+1))/${#delays[@]}）..."
  sleep "$d"
  attempt=$((attempt+1))
done

if [ "$ok" -ne 1 ]; then
  echo "[FATAL] push がネットワーク再試行後も失敗。commit はローカルに残っています。"
  exit 1
fi

echo "[done] push 完了 → origin/$BRANCH"
echo ""
# 5) 回収マニフェスト
python3 scripts/jx-retrieval-manifest.py 2>/dev/null || true
