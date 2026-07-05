#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex の版スタンプを v13.0.0 LOOP-CARD へ正規化する（冪等・本文不変）。

背景（2026-07-04）:
  v13 LOOP-CARD の本文（<div class="tx-v13-verdict"> 等）は既に 36 本へ展開済みだが、
  版スタンプ文字列（footer feature-tag ＋ lexia-genmeta の `TX vX.Y.Z 名称`）は
  v13 ビルド連鎖で一度も更新されず v12.2.1/v12.1.1/v11.1.0 のまま残っていた。
  これが「v13 実体 0 本・先祖返り」の誤認の原因。ここで本文はそのままに、
  版スタンプだけを v13.0.0 LOOP-CARD へ揃える。

対象の決め方（自己ターゲット・安全）:
  本文に `<div class="tx-v13-verdict"` を含む _lex ファイルだけを処理する。
  含まないファイル（純 v11 等）は触らない。

置換:
  1. footer の版 feature-tag: <span class="feature-tag" hidden="">TX vX.Y.Z 名称</span>
       → TX v13.0.0 LOOP-CARD  （先頭の版タグのみ・他 feature-tag は不変）
  2. lexia-genmeta: ...>Generated: <日時> / TX vX.Y.Z 名称</p>
       → 日時は保持し、末尾の版名だけ TX v13.0.0 LOOP-CARD へ

使い方:
  python scripts/tx-lex-v13-stamp.py            # dry-run（差分表示のみ）
  python scripts/tx-lex-v13-stamp.py --apply    # 実書き込み
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
LEX_DIR = ROOT / "outputs" / "ux" / "000_TX" / "001_刑法"

V13 = "TX v13.0.0 LOOP-CARD"
V13_MARKER = '<div class="tx-v13-verdict'

# 先頭版 feature-tag（版名のみ・他タグは "TX v" で始まらないので不一致＝安全）
P_TAG = re.compile(
    r'(<span class="feature-tag" hidden="">)TX v\d+\.\d+\.\d+ [A-Z][A-Z0-9-]*(</span>)'
)
# genmeta の末尾版名（日時は温存）
P_GENMETA = re.compile(
    r'(class="footer-date lexia-genmeta"[^>]*>Generated:[^<]*/ )'
    r'TX v\d+\.\d+\.\d+ [A-Z][A-Z0-9-]*(</p>)'
)
# footer-problem の版説明行（v12.x LOOP-CORE ＋旧構造＝放射SVG 等）→ v13 汎用説明へ。
# LOOP-CORE を持つ＝旧版のみ対象（LOOP-CARD は不一致＝冪等）。ID・科目・出典は温存。
V13_FOOTER_DESC = (
    "v13.0.0 LOOP-CARD（記述カード＝統合解説＋📚BASIS／正誤表＋体系マップSVG＋物語・PART A ox-grid）"
)
P_FOOTER = re.compile(
    r'(<p class="footer-problem">[^\n]*?)v\d+\.\d+\.\d+ LOOP-CORE[^<]*(</p>)'
)


def process(path: Path, apply: bool):
    html = path.read_text(encoding="utf-8")
    if V13_MARKER not in html:
        return None  # v13 本文でない＝対象外
    before_tag = P_TAG.search(html)
    before_gm = P_GENMETA.search(html)
    new = P_TAG.sub(rf'\g<1>{V13}\g<2>', html)
    new = P_GENMETA.sub(rf'\g<1>{V13}\g<2>', new)
    new = P_FOOTER.sub(rf'\g<1>{V13_FOOTER_DESC}\g<2>', new)
    changed = new != html
    old_ver = "?"
    if before_tag:
        m = re.search(r'TX v\d+\.\d+\.\d+ [A-Z][A-Z0-9-]*', before_tag.group(0))
        old_ver = m.group(0) if m else "?"
    status = "CHANGED" if changed else "already-v13"
    # 検算: 変更後に版が feature-tag・genmeta・footer-problem の3箇所とも v13 になっているか
    ok_tag = bool(re.search(re.escape(V13) + r'</span>', new))
    ok_gm = bool(re.search(r'/ ' + re.escape(V13) + r'</p>', new))
    ok_footer = not P_FOOTER.search(new)  # 旧 LOOP-CORE の footer が残っていない
    if apply and changed:
        path.write_text(new, encoding="utf-8")
    return (path.name, status, old_ver, ok_tag, ok_gm, ok_footer)


def main():
    apply = "--apply" in sys.argv
    files = sorted((ROOT / "outputs" / "ux" / "000_TX").glob("**/*_lex.html"))
    results = [r for r in (process(f, apply) for f in files) if r]
    changed = [r for r in results if r[1] == "CHANGED"]
    print(f"{'[APPLY]' if apply else '[DRY-RUN]'} v13 本文ファイル: {len(results)} 本 / 変更対象: {len(changed)} 本")
    for name, status, old, ok_tag, ok_gm, ok_footer in results:
        flag = "" if (ok_tag and ok_gm and ok_footer) else "  <<< 検算NG（tag={} gm={} footer={}）".format(ok_tag, ok_gm, ok_footer)
        print(f"  {status:12} {old:22} -> {V13}  {name}{flag}")
    bad = [r for r in results if not (r[3] and r[4] and r[5])]
    if bad:
        print(f"\n!! 検算NG {len(bad)} 本（版が3箇所そろっていない）")
        sys.exit(2)


if __name__ == "__main__":
    main()
