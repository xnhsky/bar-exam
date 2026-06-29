#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pre-commit 用：ステージ済み HTML に作成日時スタンプを埋める（経路非依存の保険）.

背景（2026-06-23）: JX/副産物の作成日時スタンプは jx-push.sh / jx-finalize.ps1 内で
stamp-created-date.py を呼ぶ設計だが、生成セッションが**それらを経由せず素の git commit**
をすると stamp が走らず、Lexia が作成日時を取得できないファイルが GitHub に残る
（実害：刑JX064〜070＋副産物がスタンプ無しで push された）。

そこで「どんなコミット経路でも必ず stamp が走る」よう、**ステージ対象の Lexia 取込 HTML**
（outputs/000_TX・001_JX・ux／top-level references）のうち lexia-genmeta スタンプを持たない
ものを **現在時刻(JST)** で刻み、再ステージする。新規/再生成＝コミット時点が生成時点
なので now が正しい（既存ファイルの後追い刻印は stamp-created-date.py が git 初出日時で行う）。
`git add -N` で index が空 blob の intent-to-add になっている HTML は、既に genmeta 済みでも
本文が commit に載らないため実体を再ステージする。

冪等: 既に genmeta を持つファイルは触らない（stamp_file が no-change を返す）。
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from stamp_footer import stamp_file, infer_version, JST, has_genmeta_stamp  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent
# Lexia が取り込むカテゴリのみ対象（それ以外の HTML はスタンプしない）。
PREFIXES = ("outputs/000_TX/", "outputs/001_JX/", "outputs/ux/", "references/")
EMPTY_BLOB_SHA1 = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def is_lexia_html(rel: str) -> bool:
    return rel.endswith(".html") and rel.startswith(PREFIXES)


def cached_changed_html() -> list[str]:
    # -z で NUL 区切り＝日本語ファイル名の quotepath エスケープを回避（刑JX 等）。
    out = subprocess.run(
        ["git", "-C", str(REPO), "diff", "--cached", "--name-only",
         "--diff-filter=ACM", "-z"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout
    files = []
    for rel in out.split("\x00"):
        rel = rel.strip()
        if is_lexia_html(rel):
            files.append(rel)
    return files


def parse_intent_to_add_stage(output: str) -> list[str]:
    files = []
    for item in output.split("\x00"):
        if not item:
            continue
        meta, sep, rel = item.partition("\t")
        if not sep:
            continue
        fields = meta.split()
        if len(fields) >= 3 and fields[1] == EMPTY_BLOB_SHA1 and is_lexia_html(rel):
            files.append(rel)
    return files


def intent_to_add_html() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "--stage", "-z", "--", *PREFIXES],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout
    return parse_intent_to_add_stage(out)


def merge_staged_paths(cached: list[str], intent: list[str]) -> list[str]:
    return list(dict.fromkeys(cached + intent))


def main() -> int:
    now = datetime.now(JST)
    restage: list[str] = []
    intent = set(intent_to_add_html())
    for rel in merge_staged_paths(cached_changed_html(), list(intent)):
        f = REPO / rel
        if not f.is_file():
            continue
        txt = f.read_text(encoding="utf-8")
        if has_genmeta_stamp(txt):  # 既にスタンプ済み＝冪等スキップ
            if rel in intent:
                restage.append(rel)
            continue
        if stamp_file(str(f), now, infer_version(rel, txt)):
            restage.append(rel)
    if restage:
        subprocess.run(["git", "-C", str(REPO), "add", "--", *restage], check=False)
        print(f"[stamp-staged] {len(restage)} 件に作成日時を刻んで再ステージ:")
        for r in restage:
            print(f"  + {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
