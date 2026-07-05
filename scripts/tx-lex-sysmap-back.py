#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-lex-sysmap-back.py ── v13 LOOP-CARD の「体系マップに戻る」ハブ復路リンクを各記述カード末尾に挿入する。

設計意図（v13 LOOP-CARD）:
  体系マップ（.tx-sysmap 内 SVG）の記述札 `<a href="#stmt-N">` が「往路」（マップ→肢）。
  その復路（肢→マップ）として、各 .tx-inline-card > .tx-inline-explain の末尾へ
    <div class="tx-sysmap-back"><a href="#tx-sysmap">↑ 体系マップに戻る</a></div>
  を置き、ハブ往復させる。CSS（.tx-sysmap-back）は canonical に既存・要素だけが未挿入だった。

規律:
  - 本文不変・冪等（既に持つカードは skip・再実行で二重挿入しない）。
  - 挿入は .tx-inline-explain の最後の子（trap / cross のどちらで終わっても可）。
  - v13 判定＝カードに .tx-v13-verdict を持つファイルのみ対象（v11/v12 は触らない）。

使い方:
  python -X utf8 scripts/tx-lex-sysmap-back.py                 # census 自動発見（outputs/ux/000_TX ＋ canonical）
  python -X utf8 scripts/tx-lex-sysmap-back.py <file> [<file>...]   # 明示パス
  python -X utf8 scripts/tx-lex-sysmap-back.py --dry-run       # 変更せず件数だけ
"""
import sys
import re
import glob
import os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BACK_LINK = '<div class="tx-sysmap-back"><a href="#tx-sysmap">↑ 体系マップに戻る</a></div>'

# <article class="tx-inline-card" ...> ... </article>（非入れ子・最短一致）
ARTICLE_RE = re.compile(r'(<article class="tx-inline-card"[^>]*>)(.*?)(</article>)', re.DOTALL)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_v13_body(html: str) -> bool:
    """本文タグ <div class="tx-v13-verdict"...> を持つ＝v13 LOOP-CARD 本文。"""
    return '<div class="tx-v13-verdict"' in html


def process_html(html: str):
    """各カードの .tx-inline-explain 末尾に BACK_LINK を挿入。(new_html, inserted, skipped) を返す。"""
    stats = {"inserted": 0, "skipped": 0, "no_explain": 0}

    def fix(m):
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        # v13 カードでなければ触らない
        if "tx-v13-verdict" not in body:
            return m.group(0)
        # 既に復路リンクを持つ＝冪等 skip
        if "tx-sysmap-back" in body:
            stats["skipped"] += 1
            return m.group(0)
        # explain の閉じ = article 内で最後の </div>。その直前に挿入すると explain の最後の子になる。
        idx = body.rfind("</div>")
        if idx == -1:
            stats["no_explain"] += 1
            return m.group(0)
        new_body = body[:idx] + BACK_LINK + "\n" + body[idx:]
        stats["inserted"] += 1
        return open_tag + new_body + close_tag

    new_html = ARTICLE_RE.sub(fix, html)
    return new_html, stats


def discover_targets():
    """census 自動発見：outputs/ux/000_TX 配下の v13 本文 ＋ canonical/GENESIS-CARD.html。"""
    targets = []
    for path in glob.glob(os.path.join(REPO, "outputs", "ux", "000_TX", "**", "*_lex.html"), recursive=True):
        try:
            with open(path, encoding="utf-8") as f:
                if is_v13_body(f.read()):
                    targets.append(path)
        except Exception as e:
            print(f"[WARN] read fail: {path}: {e}")
    canonical = os.path.join(REPO, "canonical", "GENESIS-CARD.html")
    if os.path.exists(canonical):
        with open(canonical, encoding="utf-8") as f:
            if is_v13_body(f.read()):
                targets.append(canonical)
    return sorted(set(targets))


def main():
    argv = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    files = argv if argv else discover_targets()

    total_ins = total_skip = total_files_changed = 0
    for path in files:
        try:
            with open(path, encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            print(f"[WARN] read fail: {path}: {e}")
            continue
        if not is_v13_body(html):
            print(f"[skip non-v13] {os.path.relpath(path, REPO)}")
            continue
        new_html, stats = process_html(html)
        total_ins += stats["inserted"]
        total_skip += stats["skipped"]
        rel = os.path.relpath(path, REPO)
        if new_html != html:
            total_files_changed += 1
            if not dry:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new_html)
            tag = "DRY" if dry else "OK "
            print(f"[{tag}] {rel}: +{stats['inserted']} 復路リンク挿入 (skip {stats['skipped']})")
        else:
            print(f"[==] {rel}: 変更なし (既存 {stats['skipped']} / no-explain {stats['no_explain']})")

    print("-" * 60)
    print(f"files changed: {total_files_changed} / {len(files)}  inserted: {total_ins}  already-had: {total_skip}"
          + ("   [DRY-RUN]" if dry else ""))


if __name__ == "__main__":
    main()
