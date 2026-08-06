#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-restore-original.py ── 公式 000_TX の設問・問題文原文を `_lex` の不可侵原文ブロックへ復元する。

背景（2026-08-05・LEX-005・§v13s）
--------------------------------
TX は 1 問＝公式（`outputs/000_TX/…`＝本物5択）＋ Lexia 用 `_lex`（`outputs/ux/000_TX/…_lex.html`）の
二系統で出力する。公式側は PDF 原文の設問リード・【会話】【事例】【語句群】【記述】【組合せ】を
そのまま持つのに、`_lex` を記述カード（v13 LOOP-CARD）へ組み替える工程で **共有本体だけが落ちる**
事故が起きていた（実害＝刑訴TX005_lex：おとり捜査の【会話】①〜⑥と【記述】ア〜クが丸ごと不在で、
周回画面に設問リードだけが出て問題が解けない状態で出荷されていた）。

`#part-a:has(.tx-inline-card) > .problem-text{display:none}` に巻き込まれて消える型は G74 が捕まえるが、
**そもそも `_lex` へ移送しなかった型**（DOM に存在しない）は G74 の対象外で、機械検出が不在だった。

このツールは「公式に在って `_lex` に無い原文」を、公式を単一情報源として `.tx-original-block`
（§v13n の不可侵原文ブロック＝display:none に当たらない別クラス）へ**逐語のまま**移送する。
原文の文字は 1 字も書き換えない（要約・言い換え・補足の混入は §v13r で禁止）。

安全設計
--------
* **判定は検出ゲートと同一**：`scripts/tx_source_text.py` が単一情報源。`validate-tx-core.py` の
  G75 と同じ式で判定するので「直したのに ERROR」「ERROR は出ないのに欠けている」が構造的に起きない。
* **冪等**：復元済み（欠落なし）のファイルは無変更。
* **本文不変**：`_lex` 側の既存テキストは、ブロックへ移した原文リードと同一の裸段落を畳む以外は触らない。
* **原文以外は載せない**：参照条文・解答・編集注記（「📖 本問…の本物の5択」）と、正解の先出し
  （「正解：肢3」「／正答率89%」＝§v13r・G19）は落としてから移送する。
* **G62 安全**：`.tx-charge` を出すのは記述数＝`.ox-row` 数が一致する時だけ。
* **改行不変**：raw のまま読み書きする。corpus には CRLF ファイルと「LF 主体だが数十行だけ CRLF」の
  混在ファイルがあり、多数派へ寄せて書き戻すと混在ファイルが全行 diff になる（刑訴TX029/085/117）。
* **触らない型**：`_lex` が自前の共有本体（言い換え版の事例・会話・見解）を持つ問題は、二重掲載に
  なるため機械復元しない。G75 は WARNING（REVIEW）で可視化し、入力 PDF を見て 1 問ずつ直す。

使い方
------
    python scripts/tx-restore-original.py --check              # 対象一覧だけ表示（既定）
    python scripts/tx-restore-original.py --apply              # corpus 一括復元
    python scripts/tx-restore-original.py --apply <file...>    # 個別ファイル
    python scripts/tx-restore-original.py --report             # REVIEW/原文層なしも含む監査表
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tx_source_text as st  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LEX_GLOB = "outputs/ux/000_TX/**/*_lex.html"


def restore(lex_path: Path, apply: bool) -> dict | None:
    lex, nl = st.read_keep_newlines(lex_path)   # lex は raw（改行は 1 バイトも変えない）
    verdict, payload = st.analyze(lex_path, lex_html=lex)
    if verdict != "restorable":
        return None

    # ブロックへ移した原文リードと同一の裸段落は畳む（同じ文の二重掲載を避ける）
    region = payload["region"]
    for m in list(re.finditer(r"<p[^>]*>([\s\S]*?)</p>\s*", region)):
        if st.norm(st.plain(m.group(1))) in payload["moved"]:
            region = region.replace(m.group(0), "", 1)

    # 操作指示（「…正誤（○×）を判定する。」）の直後、無ければ見出し直後に差し込む
    anchor = re.search(r'<p style="font-weight:600;">[^<]*判定する。</p>\s*', region)
    pos = anchor.end() if anchor else 0
    block = payload["block"].replace("\n", nl)
    region = region[:pos] + block + nl + region[pos:]

    out = lex[:payload["lstart"]] + region + lex[payload["lend"]:]
    if apply:
        # newline="" ＝ Python に改行を触らせない（raw をそのまま書き戻す）
        with open(lex_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(out)
    return dict(lex=str(lex_path), official=payload["official"],
                ratio=round(payload["ratio"], 2), added=len(payload["block"]),
                body=sum(1 for k, _, _ in payload["items"] if k in ("body", "verbatim")),
                groups=sum(1 for k, _, _ in payload["items"] if k == "list"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="対象 _lex（省略時は corpus 全体）")
    ap.add_argument("--apply", action="store_true", help="実際に書き換える（既定は --check）")
    ap.add_argument("--report", action="store_true",
                    help="復元対象に加え REVIEW／原文層なしも一覧する（監査用）")
    args = ap.parse_args()

    os.chdir(ROOT)
    targets = [Path(f) for f in args.files] if args.files else sorted(Path(".").glob(LEX_GLOB))

    if args.report:
        buckets: dict[str, list[str]] = {"restorable": [], "review": [], "no-layer": []}
        for t in targets:
            verdict, _ = st.analyze(t)
            if verdict:
                buckets[verdict].append(t.name)
        print(f"走査 {len(targets)} ファイル")
        print(f"  復元可（G75 ERROR）      : {len(buckets['restorable'])}")
        print(f"  要内容照合（G75 WARNING）: {len(buckets['review'])}")
        print(f"  原文層なし（G75 WARNING）: {len(buckets['no-layer'])}")
        for k in ("restorable", "review"):
            for n in buckets[k]:
                print(f"    [{k}] {n}")
        return 0

    hits = []
    for t in targets:
        info = restore(t, args.apply)
        if info:
            hits.append(info)
            print(("[RESTORE] " if args.apply else "[TARGET]  ")
                  + f"{Path(info['lex']).name}  欠落率={info['ratio']}"
                    f"  本体={info['body']} 記述群={info['groups']}")
    print(f"\n{'復元' if args.apply else '対象'}: {len(hits)} ファイル / 走査 {len(targets)}")
    if not args.apply and hits:
        print("--apply を付けると書き換えます。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
