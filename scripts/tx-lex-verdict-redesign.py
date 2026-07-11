#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-lex-verdict-redesign.py ── v13 LOOP-CARD の正誤表リデザイン「土台」を注入する決定論ツール。

注入する汎用インフラ（問題固有でない部分＝機械的に伝播できる部分）:
  1. CSS 一式（体系マップ規範核バッジ .nb-badge / 正誤表パネルの成績バッジ・タイトル行 /
     印付き原文＋法理コアの verdict-brief / 額装フレーム・金プレート見出し等の重厚感 / ラベル字下げ解除）。
  2. エンジン JS（makeBriefLine ＋ compactReviewTableClone[印付き原文対応] ＋ computeInlineScore ＋
     renderInlineAnswerTablePanel[成績バナー]）。旧 2 関数を丸ごと差し替える。
  3. 体系マップの「本問の帰結（○×）」ネタバレ箱を削除（設計方針＝結論を先出ししない）。

問題固有で本ツールが触らない部分（生成/移行時に手で鋳造する）:
  - 体系マップ各ノードの ✍規範核バッジ（<rect class="nb-badge">＋text）とノード高さ・viewBox。
  - 親カテゴリ箱の本文中央寄せ・子ノードのタイトル縮小（マップごとに要否が違う）。
  - 正誤表各行の data-brief-mark（印付き原文の要約＝記述ごとに執筆）。

参照元（--ref）から CSS/エンジンを実体抽出して注入するので、正典改定時は --ref を新正典にすれば追従する。
冪等（computeInlineScore 有 → エンジン skip／marker 有 → CSS skip／帰結箱無 → 除去 skip）。本文の他部分は不変。

使い方:
  python -X utf8 scripts/tx-lex-verdict-redesign.py --ref outputs/ux/000_TX/001_刑法/刑TX371_lex.html canonical/GENESIS-CARD.html
  python -X utf8 scripts/tx-lex-verdict-redesign.py <target> [<target>...]      # --ref 既定＝canonical/GENESIS-CARD.html
  python -X utf8 scripts/tx-lex-verdict-redesign.py --dry-run <target>
"""
import sys
import os
import re

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REF = os.path.join(REPO, "canonical", "GENESIS-CARD.html")

CSS_START = "/* === TX371 試作: 体系マップ規範核バッジ"
CSS_MARKER = "TX-VERDICT-REDESIGN"                    # 冪等判定＋注入後のマーカー
ENG_START = "  function extractReviewCoreSummary(cell){"      # コア＝転用可能な法理（転用タグ優先）から含めて差し替える
ENG_END = "  function setInlineAnswerTableVisible(open){"
OLD_ENG_START = "  function extractReviewCoreSummary(cell){"
KIKETSU = "▼ 本問の帰結（○×）"


def extract_css(ref):
    """参照元から CSS 土台を抽出（先頭マーカー〜 </style></head> 直前）。"""
    s = ref.find(CSS_START)
    if s < 0:
        # 既に clean marker 版の参照元かもしれない
        s = ref.find("/* === " + CSS_MARKER)
    e = ref.find("</style>\n</head>")
    if s < 0 or e < 0 or e <= s:
        raise SystemExit("[ERR] 参照元から CSS 土台を抽出できない（マーカー/</style></head> 不在）")
    css = ref[s:e].rstrip("\n") + "\n"
    css = css.replace("TX371 試作: ", CSS_MARKER + ": ").replace("TX371 試作 追補: ", CSS_MARKER + " 追補: ")
    return css


def extract_engine(ref):
    """参照元から新エンジン塊を抽出（makeBriefLine〜renderInlineAnswerTablePanel 末尾）。"""
    s = ref.find(ENG_START)
    e = ref.find(ENG_END)
    if s < 0 or e < 0 or e <= s:
        raise SystemExit("[ERR] 参照元から新エンジンを抽出できない")
    return ref[s:e].rstrip("\n") + "\n"


def inject(html, css, engine):
    changed = []
    # 1) CSS 注入（冪等）
    if CSS_MARKER not in html and CSS_START not in html:
        if "</style>\n</head>" not in html:
            raise SystemExit("[ERR] target に </style></head> が無い（CSS 注入不可）")
        html = html.replace("</style>\n</head>", "\n" + css + "</style>\n</head>", 1)
        changed.append("CSS")
    # 2) エンジン差し替え（冪等：computeInlineScore 未導入時のみ）
    if "function computeInlineScore(" not in html:
        s = html.find(OLD_ENG_START)
        e = html.find(ENG_END)
        if s < 0 or e < 0 or e <= s:
            raise SystemExit("[ERR] target の旧エンジン境界（compactReviewTableClone〜setInlineAnswerTableVisible）が見つからない")
        html = html[:s] + engine + html[e:]  # html[e:] は次関数のインデント2スペースを含む
        changed.append("ENGINE")
    # 3) 本問の帰結（○×）箱の除去（行単位・keyed on ラベル）
    if KIKETSU in html:
        lines = html.split("\n")
        kept = [ln for ln in lines if KIKETSU not in ln]
        if len(kept) != len(lines):
            html = "\n".join(kept)
            changed.append("KIKETSU(-%d行)" % (len(lines) - len(kept)))
    return html, changed


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    ref_path = DEFAULT_REF
    if "--ref" in args:
        i = args.index("--ref")
        ref_path = args[i + 1]
        del args[i:i + 2]
    targets = args
    if not targets:
        raise SystemExit("usage: tx-lex-verdict-redesign.py [--ref REF] [--dry-run] <target> [<target>...]")

    with open(ref_path, encoding="utf-8") as f:
        ref = f.read()
    css = extract_css(ref)
    engine = extract_engine(ref)
    print(f"[ref] {os.path.relpath(ref_path, REPO)}  CSS {len(css)}B / ENGINE {len(engine)}B")

    n_changed = 0
    for t in targets:
        with open(t, "rb") as f:
            raw = f.read()
        use_crlf = b"\r\n" in raw           # 生成物HTMLはCRLF・autocrlf=false。改行を保持する
        html = raw.decode("utf-8").replace("\r\n", "\n")
        new, changed = inject(html, css, engine)
        rel = os.path.relpath(os.path.abspath(t), REPO)
        if new != html:
            n_changed += 1
            if not dry:
                out = new.replace("\n", "\r\n") if use_crlf else new
                with open(t, "w", encoding="utf-8", newline="") as f:
                    f.write(out)
            print(f"[{'DRY' if dry else 'OK '}] {rel}: {', '.join(changed)}")
        else:
            print(f"[==] {rel}: 変更なし（既に土台導入済み）")
    print("-" * 56)
    print(f"changed {n_changed}/{len(targets)}" + ("  [DRY-RUN]" if dry else ""))


if __name__ == "__main__":
    main()
