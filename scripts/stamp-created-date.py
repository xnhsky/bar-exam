#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""作成日＋版スタンプ（時刻つき・冪等・2026-06-23 改修）.

JX(ATHENA)・副産物(RX/TREE/ARIADNE) のフッターに機械可読の
「作成日：YYYY-MM-DD HH:MM ／ <版>」(class=lexia-genmeta) を刻む。Lexia は raw 取得した
本文からこれを読み、GitHub Commits API を叩かずに生成日時・版を取得する(レート制限回避)。

日時の決め方（「再生成では更新する」を満たす肝）:
  - 生成/再生成直後でファイルが **dirty（未追跡 or HEAD と差分あり）** → **現在時刻(JST)**。
  - 追跡済みで未変更（＝既存ファイルの後追い刻印） → **git 初出コミット日時**。
冪等: 既に lexia-genmeta スタンプを持つファイルはスキップ（旧 <!-- 作成日：… --> コメントは
stamp_footer 側が刻印時に除去する）。

呼び出し元: jx-push.sh 工程0（リモート/ローカルの回収動線）。対象は **Lexia が取り込む
全カテゴリ**（outputs/000_TX・001_JX・ux/** ＋ top-level references/**）。既に「作成日」を
持つファイル（TX 既存フッター・genmeta 済み等）は触らず、作成日の無いものだけ刻む。
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from stamp_footer import stamp_file, infer_version, JST, has_genmeta_stamp  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout


def is_dirty(rel: str) -> bool:
    """未追跡 or HEAD と差分あり（＝いま生成/再生成された）か。"""
    return bool(_git("status", "--porcelain", "--", rel).strip())


def first_commit_dt(rel: str) -> datetime | None:
    out = _git("log", "--follow", "--format=%cI", "--", rel).strip().splitlines()
    return datetime.fromisoformat(out[-1]).astimezone(JST) if out else None


def targets() -> list[pathlib.Path]:
    # Lexia が取り込む全カテゴリ（TX/JX/副産物/参考資料/references）。
    files: list[pathlib.Path] = []
    for d in ("outputs/000_TX", "outputs/001_JX", "outputs/ux", "references"):
        base = REPO / d
        if base.is_dir():
            files += sorted(base.rglob("*.html"))
    return files


def main() -> int:
    now = datetime.now(JST)
    stamped = skipped = 0
    for f in targets():
        txt = f.read_text(encoding="utf-8")
        # 既に英語スタンプ(genmeta)済みは触らない＝冪等。コメント/script 内の文字列は除外する。
        if has_genmeta_stamp(txt):
            skipped += 1
            continue
        rel = f.relative_to(REPO).as_posix()
        # 再生成/新規（dirty）は現在時刻、未変更の既存は初出コミット日時。
        dt = now if is_dirty(rel) else (first_commit_dt(rel) or now)
        stamp_file(str(f), dt, infer_version(rel, txt))
        stamped += 1
    print(f"stamped={stamped}  skipped(作成日あり)={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
