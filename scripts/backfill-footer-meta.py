#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""既存の問題HTMLに「生成日時＋版」フッター刻印を一括バックフィルする。

生成日時の源泉は **git 履歴 (そのファイルが最初に commit された日時 = 生成日)**。
JX/RX/TREE/ARIADNE は従来テンプレ固定の日付コメントしか持たず実生成日が不明だったため、
git の初出コミット日時で正しい日付を復元する。TX は既に可視フッターに実日付を持つので
既定では対象外 (--include-tx で含められる)。

依存: リポジトリの **完全な git 履歴** (shallow clone では初出日時が取れない。
事前に `git fetch --unshallow` 済みであること)。

使い方:
    python scripts/backfill-footer-meta.py --dry-run --limit 5     # 先頭5件をプレビュー
    python scripts/backfill-footer-meta.py                          # JX+RX+TREE+ARIADNE を刻印
    python scripts/backfill-footer-meta.py --include-tx            # TX も時刻つきへ更新
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stamp_footer import stamp_file, JST  # noqa: E402

DEFAULT_DIRS = [
    "outputs/001_JX",
    "outputs/ux/001_RX",
    "outputs/ux/002_TREE",
    "outputs/ux/000_ARIADNE",
]
TX_DIR = "outputs/000_TX"


def first_commit_dt(path: str) -> datetime | None:
    """そのパスが最初に現れた commit の committer 日時 (=生成日時) を返す。"""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%cI", "--", path],
            capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        return None
    if not out:
        return None
    # 末尾 = 最古 = 初出 (=生成)。
    return datetime.fromisoformat(out[-1]).astimezone(JST)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="先頭 N 件だけ処理 (0=全件)")
    ap.add_argument("--include-tx", action="store_true", help="TX も対象に含める")
    ap.add_argument("--all", action="store_true", help="Lexia 取込全カテゴリ(TX/JX/ux/references)")
    ap.add_argument("--restamp", action="store_true", help="作成日があっても再刻印する(既定はスキップ)")
    a = ap.parse_args()

    if a.all:
        dirs = ["outputs/000_TX", "outputs/001_JX", "outputs/ux", "references"]
    else:
        dirs = list(DEFAULT_DIRS) + ([TX_DIR] if a.include_tx else [])
    dirs = [d for d in dirs if Path(d).is_dir()]
    files: list[str] = []
    for d in dirs:
        files.extend(str(p) for p in sorted(Path(d).rglob("*.html")))
    if a.limit:
        files = files[: a.limit]

    stamped = nochange = nodate = skipped = 0
    for f in files:
        # 既に作成日があるファイルは触らない（冪等・誤って実日付を git 日時で上書きしない）。
        if not a.restamp and "作成日" in Path(f).read_text(encoding="utf-8", errors="replace"):
            skipped += 1
            continue
        dt = first_commit_dt(f)
        if dt is None:
            nodate += 1
            print(f"[no-git-date] {f}")
            continue
        changed = stamp_file(f, dt, dry_run=a.dry_run)
        if changed:
            stamped += 1
            print(f"[{'would ' if a.dry_run else ''}stamp] {dt.strftime('%Y-%m-%d %H:%M')}  {f}")
        else:
            nochange += 1
    print(f"\n--- {'DRY-RUN ' if a.dry_run else ''}summary: stamped={stamped} skipped(作成日あり)={skipped} nochange={nochange} no-git-date={nodate} total={len(files)} ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
