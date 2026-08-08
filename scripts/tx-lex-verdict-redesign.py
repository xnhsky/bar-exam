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
ENG_START = "  // TX-VERDICT-CORE2:"                          # v2 エンジン塊の先頭コメント
ENG_END = "  function setInlineAnswerTableVisible(open){"
OLD_ENG_START = "  function extractReviewCoreSummary(cell){"  # v1 エンジンの先頭（旧版ファイルの境界）
KIKETSU = "▼ 本問の帰結（○×）"

# --- v2（2026-08-08・正誤表コア列の実体名ラベル化＋残り法理の details）---------------------
CORE2_MARK = "TX-VERDICT-CORE2"                              # CSS/エンジン共通の版マーカー
CORE2_CSS_START = "/* TX-VERDICT-CORE2:BEGIN"
CORE2_CSS_END = "/* TX-VERDICT-CORE2:END */"
CORE2_ENG_FN = "function extractReviewCoreLines("            # v2 エンジンの識別子（冪等判定）


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
    """参照元から新エンジン塊を抽出（extractReviewCoreLines〜renderInlineAnswerTablePanel 末尾）。"""
    s = ref.find(ENG_START)
    e = ref.find(ENG_END)
    if s < 0 or e < 0 or e <= s:
        raise SystemExit("[ERR] 参照元から新エンジンを抽出できない")
    if CORE2_ENG_FN not in ref[s:e]:
        raise SystemExit("[ERR] 参照元のエンジンが v2（extractReviewCoreLines）でない")
    return ref[s:e].rstrip("\n") + "\n"


def extract_core2_css(ref):
    """参照元から v2 CSS 区画（TX-VERDICT-CORE2:BEGIN〜END）を抽出。"""
    s = ref.find(CORE2_CSS_START)
    e = ref.find(CORE2_CSS_END)
    if s < 0 or e < 0 or e <= s:
        raise SystemExit("[ERR] 参照元から TX-VERDICT-CORE2 の CSS 区画を抽出できない")
    return ref[s:e + len(CORE2_CSS_END)] + "\n"


def inject_into_first_style(html, block):
    """第1 <style>（tx-lex-css-canonize が単一情報源とみなすブロック）の末尾へ差し込む。"""
    s = html.find("<style>")
    if s < 0:
        raise SystemExit("[ERR] target に素の <style> が無い（CSS 注入不可）")
    e = html.find("</style>", s)
    if e < 0:
        raise SystemExit("[ERR] target の第1 <style> が閉じていない")
    nl = local_newline(html[s:e])
    return html[:e] + nl + to_newline(block, nl) + html[e:]


def local_newline(chunk):
    """差し込み先の改行様式を局所判定する（生成物は LF/CRLF 混在があるため全体正規化はしない）。"""
    return "\r\n" if "\r\n" in chunk else "\n"


def to_newline(block, nl):
    """ブロック（参照元＝LF）の改行を差し込み先の様式へ合わせる。"""
    body = block.replace("\r\n", "\n")
    return body if nl == "\n" else body.replace("\n", "\r\n")


def inject(html, css, engine, core2_css):
    changed = []
    # 1) CSS 土台（v1）注入（冪等）
    if CSS_MARKER not in html and CSS_START not in html:
        anchor = next((a for a in ("</style>\n</head>", "</style>\r\n</head>") if a in html), None)
        if not anchor:
            raise SystemExit("[ERR] target に </style></head> が無い（CSS 注入不可）")
        nl = local_newline(anchor)
        html = html.replace(anchor, nl + to_newline(css, nl) + anchor, 1)
        changed.append("CSS")
    # 1-bis) v2 CSS 区画（コア列の実体名ラベル＋残り法理 details）を正典へ同期（冪等）。
    #        既に在る場合も**正典と差があれば載せ替える**＝正典追補が全ファイルへ必ず届く
    #        （skip だけの冪等にすると、改定のたびに手作業の再注入が要り接ぎ木の温床になる）。
    if CORE2_CSS_START in html:
        s = html.find(CORE2_CSS_START)
        e = html.find(CORE2_CSS_END, s)
        if e < 0:
            raise SystemExit("[ERR] target の TX-VERDICT-CORE2 CSS 区画が閉じていない")
        e += len(CORE2_CSS_END)
        cur = html[s:e]
        new_block = to_newline(core2_css, local_newline(cur)).rstrip("\r\n")
        if cur != new_block:
            html = html[:s] + new_block + html[e:]
            changed.append("CSS2(sync)")
    else:
        html = inject_into_first_style(html, core2_css)
        changed.append("CSS2")
    # 2) エンジンを正典へ同期（v1/旧どちらの境界からでも載せ替える・差が無ければ無変更）
    s = html.find(ENG_START)
    if s < 0:
        s = html.find(OLD_ENG_START)
    e = html.find(ENG_END)
    if s < 0 or e < 0 or e <= s:
        raise SystemExit("[ERR] target の旧エンジン境界（extractReviewCore*〜setInlineAnswerTableVisible）が見つからない")
    # 旧エンジン塊と同じ改行様式で載せ替える（周辺バイトは1文字も動かさない）
    new_engine = to_newline(engine, local_newline(html[s:e]))
    if html[s:e] != new_engine:
        html = html[:s] + new_engine + html[e:]
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
    core2_css = extract_core2_css(ref)
    print(f"[ref] {os.path.relpath(ref_path, REPO)}  CSS {len(css)}B / CSS2 {len(core2_css)}B / ENGINE {len(engine)}B")

    n_changed = 0
    for t in targets:
        with open(t, "rb") as f:
            raw = f.read()
        # 生成物 HTML は LF/CRLF が混在しうる（歴代ツールの書き戻し差）。全体正規化すると
        # 全行差分になるので、原文の改行はそのまま保持し、差し込み箇所だけ局所様式に合わせる。
        html = raw.decode("utf-8")
        new, changed = inject(html, css, engine, core2_css)
        rel = os.path.relpath(os.path.abspath(t), REPO)
        if new != html:
            n_changed += 1
            if not dry:
                with open(t, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
            print(f"[{'DRY' if dry else 'OK '}] {rel}: {', '.join(changed)}")
        else:
            print(f"[==] {rel}: 変更なし（既に土台導入済み）")
    print("-" * 56)
    print(f"changed {n_changed}/{len(targets)}" + ("  [DRY-RUN]" if dry else ""))


if __name__ == "__main__":
    main()
