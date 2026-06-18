#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JX 回収マニフェスト生成（リモート実行時の成果物回収の動線）

背景：
  Claude Code on the web 等のリモート実行は ephemeral でコンテナが回収される。
  生成した HTML は git に commit/push して GitHub に残すのが唯一の永続化（CLAUDE.md §9）。
  本スクリプトは「今回のセッションで作った成果物を、どこからどう回収すればよいか」を
  一覧（マニフェスト）として出力し、回収の動線を明確にする。

出力内容：
  - 現在のブランチ名 / リモート URL / 比較基準（既定 origin/master）
  - 今回のブランチで追加・変更された outputs/001_JX 配下の HTML 一覧（サイズ付き）
  - 各ファイルの GitHub blob URL（ブラウザでそのまま開ける／Raw でダウンロード可）
  - コピペ用の回収手順（git pull / 直接 DL）

使い方：
  python scripts/jx-retrieval-manifest.py                 # outputs/001_JX 全体
  python scripts/jx-retrieval-manifest.py --base origin/master
  python scripts/jx-retrieval-manifest.py --glob 'outputs/001_JX/001_刑法/*.html'
  python scripts/jx-retrieval-manifest.py --md > deploy/retrieval-latest.md
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sh(*args):
    # git の場合は quotepath を無効化（日本語パスが \345... と8進エスケープされるのを防ぐ）
    if args and args[0] == "git":
        args = ("git", "-c", "core.quotepath=false") + args[1:]
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def remote_to_https(url):
    """各種 remote 形式から (owner/repo, https base) を得る。
    - git@github.com:owner/repo.git
    - https://github.com/owner/repo(.git)
    - http://local_proxy@127.0.0.1:PORT/git/owner/repo  （リモート実行のプロキシ形式）
    """
    if not url:
        return None, None
    m = re.search(r"github\.com[:/]+([^/]+)/(.+?)(?:\.git)?$", url)
    if not m:
        # プロキシ形式 .../git/owner/repo を救う
        m = re.search(r"/git/([^/]+)/(.+?)(?:\.git)?/?$", url)
    if not m:
        return None, None
    slug = f"{m.group(1)}/{m.group(2)}"
    return slug, f"https://github.com/{slug}"


def resolve_base(given):
    """比較基準を候補順に解決。verify できる最初のものを返す。無ければ None。"""
    candidates = [given, "origin/master", "origin/main", "master", "main"]
    for c in candidates:
        if c and sh("git", "rev-parse", "--verify", "--quiet", c):
            return c
    return None


def _keep(line):
    return line.startswith("outputs/001_JX/") and line.endswith(".html")


def changed_files(base, glob):
    """『今回のセッションの成果物』を可能な限り正確に：
       (base..HEAD のコミット差分) ∪ (未コミット差分) ∪ (未追跡新規)。
       いずれも空なら作業ツリー全 glob にフォールバック。"""
    files = set()
    if base:
        for line in sh("git", "diff", "--name-only", f"{base}...HEAD").splitlines():
            if _keep(line):
                files.add(line)
    # 未コミットの変更（modified / staged）
    for line in sh("git", "diff", "--name-only", "HEAD").splitlines():
        if _keep(line):
            files.add(line)
    # 未追跡の新規ファイル
    for line in sh("git", "ls-files", "--others", "--exclude-standard").splitlines():
        if _keep(line):
            files.add(line)
    if not files:
        for p in sorted(ROOT.glob(glob)):
            files.add(str(p.relative_to(ROOT)))
    return sorted(files)


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/master", help="比較基準（既定 origin/master）")
    ap.add_argument("--glob", default="outputs/001_JX/**/*.html", help="フォールバック glob")
    ap.add_argument("--md", action="store_true", help="Markdown で出力")
    args = ap.parse_args()

    branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD")
    remote = sh("git", "remote", "get-url", "origin")
    slug, https = remote_to_https(remote)
    head = sh("git", "rev-parse", "HEAD")

    base = resolve_base(args.base)

    files = changed_files(base, args.glob)

    lines = []
    p = lines.append
    p("# JX 回収マニフェスト（成果物の回収動線）")
    p("")
    p(f"- ブランチ: `{branch}`")
    p(f"- HEAD: `{head[:12]}`")
    p(f"- リモート: `{remote or '(なし)'}`")
    p(f"- 比較基準: `{base or '(基準なし→作業ツリー全列挙)'}`")
    p(f"- 成果物: **{len(files)} 件**")
    p("")
    if not files:
        p("> 対象 HTML が見つかりません（まだ生成/コミットされていない可能性）。")
    else:
        p("| ファイル | サイズ | GitHub で開く |")
        p("|---|---|---|")
        for f in files:
            ap_ = ROOT / f
            size = human(ap_.stat().st_size) if ap_.exists() else "—"
            if https:
                blob = f"{https}/blob/{branch}/{f}"
                cell = f"[blob]({blob})"
            else:
                cell = "(remote 不明)"
            p(f"| `{f}` | {size} | {cell} |")
        p("")
        p("## 回収手順（いずれか）")
        p("")
        p("**A. ローカルへ pull（推奨）**")
        p("```")
        p(f"git fetch origin {branch}")
        p(f"git checkout {branch}   # もしくは git pull origin {branch}")
        p("```")
        if https:
            p("")
            p("**B. ブラウザから直接ダウンロード（Raw）**")
            p("```")
            for f in files:
                p(f"{https}/raw/{branch}/{f}")
            p("```")
        p("")
        p("**C. Drive ミラー（任意・手動）**")
        p("GitHub から DL → `マイドライブ / 2 JX_論文 / 00N_科目` へアップロード（docs/drive-folders.md 参照）。")

    out = "\n".join(lines)
    # --md 無しでも Markdown は読めるのでそのまま出す（端末でも可読）
    print(out)


if __name__ == "__main__":
    main()
