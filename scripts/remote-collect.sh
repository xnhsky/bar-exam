#!/usr/bin/env bash
#
# remote-collect.sh — リモート（Claude Code on the web）ナイトバッチ専用の成果物回収導線。
#
# 背景:
#   通常 outputs/**/*.html は .gitignore で除外され（git は code/spec のみ管理）、
#   成果物 HTML は Google Drive で配信される。しかしリモート実行環境（Linux コンテナ）
#   には Drive が無く、コンテナは非アクティブで破棄されるため、生成した HTML を
#   そのまま放置すると外出先で回収できない。
#
# 役割:
#   生成済み HTML を *明示的に* `git add -f` で gitignore を上書きしてステージし、
#   現在のブランチへ commit & push する。これにより GitHub 経由で成果物を回収できる。
#   グローバルな .gitignore 方針（HTML は通常 ignore）は変更しないため、master の
#   「code/spec のみ管理」ポリシーは保たれる。回収用ブランチ限定の運用。
#
# 注意:
#   - このスクリプトで作られる HTML コミットは *回収用ブランチ専用*。
#     master へはマージしない（master は code/spec のみ）。
#
# 使い方:
#   bash scripts/remote-collect.sh                    # outputs/tx + outputs/jx の全 HTML を回収
#   bash scripts/remote-collect.sh outputs/tx/刑TX    # 特定フォルダのみ
#   bash scripts/remote-collect.sh --dry-run          # 対象を表示するだけ（commit/push しない）

set -euo pipefail

# === 引数解析 ===
DRY_RUN=0
TARGETS=()
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -*) echo "不明なオプション: $arg" >&2; exit 2 ;;
    *) TARGETS+=("$arg") ;;
  esac
done

# 対象未指定なら outputs/tx と outputs/jx を既定とする
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=(outputs/tx outputs/jx)
fi

# === プロジェクトルートへ移動 ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "=== remote-collect 開始 $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "ブランチ: $BRANCH"
echo "対象: ${TARGETS[*]}"

# === 対象 HTML の収集 ===
HTML_FILES=()
while IFS= read -r -d '' f; do
  HTML_FILES+=("$f")
done < <(find "${TARGETS[@]}" -type f -name '*.html' -print0 2>/dev/null | sort -z)

if [ ${#HTML_FILES[@]} -eq 0 ]; then
  echo "回収対象の HTML がありません。終了。"
  exit 0
fi

echo "回収対象 HTML: ${#HTML_FILES[@]} 件"
printf '  - %s\n' "${HTML_FILES[@]}"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[--dry-run] commit/push はスキップしました。"
  exit 0
fi

# === ステージ（gitignore を -f で上書き）===
git add -f "${HTML_FILES[@]}"

# 変更が無ければ何もしない
if git diff --cached --quiet; then
  echo "ステージされた変更なし（既にコミット済み）。終了。"
  exit 0
fi

STAGED_COUNT="$(git diff --cached --name-only | wc -l | tr -d ' ')"
git commit -m "chore(collect): リモートナイトバッチ成果物 ${STAGED_COUNT} 件を回収

外出先回収用に outputs HTML を当ブランチへ収集（master へは非マージ）。

https://claude.ai/code/session_01DV7TMMvV52nnakZXsVqdHc"

# === push（ネットワーク失敗時は指数バックオフで最大 4 回リトライ）===
backoff=2
for attempt in 1 2 3 4 5; do
  if git push -u origin "$BRANCH"; then
    echo "push 成功（試行 $attempt 回目）。"
    echo "=== remote-collect 完了 $(date '+%Y-%m-%d %H:%M:%S') ==="
    exit 0
  fi
  if [ "$attempt" -eq 5 ]; then
    echo "push が 5 回失敗しました。手動で確認してください。" >&2
    exit 1
  fi
  echo "push 失敗。${backoff}s 待機して再試行..." >&2
  sleep "$backoff"
  backoff=$((backoff * 2))
done
