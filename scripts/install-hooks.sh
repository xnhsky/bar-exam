#!/usr/bin/env bash
# =============================================================================
# install-hooks.sh — 本リポジトリの versioned git フックを有効化する（各 PC 一度だけ）。
#
# core.hooksPath を scripts/git-hooks に向けるだけ。これで pre-commit（作成日時スタンプの
# 保険・stamp-staged.py）が全コミットで走る。OWNER PC / xnrg2 PC / リモートそれぞれで実行。
# =============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
git config core.hooksPath scripts/git-hooks
chmod +x scripts/git-hooks/* 2>/dev/null || true
echo "[install-hooks] core.hooksPath = scripts/git-hooks に設定しました。"
echo "  → 以後の git commit で pre-commit（作成日時スタンプ保険）が走ります。"
