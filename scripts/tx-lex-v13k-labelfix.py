#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-lex-v13k-labelfix.py — v13 _lex に「表見出し中央揃え」と「コツ箱ぶら下がり修正」を
決定論・冪等・CRLF保存で適用する（ユーザー訂正 2026-07-04 の正典化）。

背景（正典と見比べて正しい形を適用）：
  ① 表の見出しセルが左寄せ：静的正誤表 .tx-sysmap-cross の thead/tbody th に中央揃えが無い。
     既存の .cross-column th{ text-align:center; vertical-align:middle }（見出し/ラベルは中央・
     データtdは左）と同概念を .tx-sysmap-cross と JS正誤表 .statement-verdict-table 見出し・
     .freq-badge にも展開する（本文データ td は左のまま）。→ CSS block v13k を挿入。
  ② 「💡 コツ」箱の本文がぶら下がる：旧世代の solve-nav renderStep が本文 s.tip を
     .sn-tip-b で包まず生挿入していた（grid の子がインライン断片に分裂＝各<b>が左端に落ちる）。
     正典 canonical/SOLVE-NAV.html / GENESIS-CARD.html は既に <span class="sn-tip-b"> で包む
     正しい形。35問の旧エンジンをその形へ揃える（text-indent:1em も効く＝本文頭1字下げ）。

いずれも本文・問題固有データ不変。冪等（再実行で無変化）。CRLF を保存する。
  適用: python scripts/tx-lex-v13k-labelfix.py --apply
  点検: python scripts/tx-lex-v13k-labelfix.py           # would-fix のみ表示
"""
import sys, glob, io, os

# --- ① 表見出し中央揃え CSS（.tx-sysmap-cross tbody th 行の直後へ挿入） ---
CSS_ANCHOR = ".tx-sysmap-cross tbody th{ letter-spacing:normal !important; text-indent:0 !important; }"
CSS_BLOCK = """
/* === v13k: 表の見出しセル・番号ラベル・バッジは中央揃え＋均等字間（本文データtdは左のまま）＝ .cross-column th と同概念 === */
.tx-sysmap-cross thead th, .tx-sysmap-cross tbody th{ text-align:center; vertical-align:middle; }
.statement-verdict-table thead th{ text-align:center; }
.freq-badge{ text-align:center; }"""

# --- ③ 本文強調を一段細く(v13l)＋体系マップSVGの立体感(v13m)。v13k ブロック末尾へ続けて挿入 ---
CSS2_ANCHOR = ".freq-badge{ text-align:center; }"
CSS2_BLOCK = """
/* === v13l: 本文中の強調(<b>/<strong>)を一段細く。見出しバッジ(.syn-step+strong)・ラベル・表は据え置き === */
.tx-inline-explain .syn-lead strong, .tx-inline-explain .syn-lead b,
.tx-inline-explain .syn-image strong, .tx-inline-explain .syn-image b,
.tx-inline-explain .syn-orig strong, .tx-inline-explain .syn-orig b,
.tx-inline-explain .syn-body strong, .tx-inline-explain .syn-body b{ font-weight:600 !important; }
.tx-mini-law-body b, .tx-mini-law-body strong, .basis-card-body b, .basis-card-body strong{ font-weight:640 !important; }
.tx-answer-box .tx-answer-body strong, .tx-answer-box .tx-answer-body b{ font-weight:680 !important; }
/* === v13m: 体系マップSVGの重厚感・立体感（各箱の主 rect にドロップシャドウ／ヘッダー帯・文字は据え置き）=== */
.tx-sysmap-svg g > rect:first-of-type{ filter:drop-shadow(0 5px 8px rgba(60,40,30,.32)); }"""

# --- ④ コツ箱の本文を .sn-tip-b で包む（renderStep の生挿入を正典形へ） ---
SNTIP_OLD = "<span class=\"sn-tip-h\">💡 コツ</span>'+s.tip+'</div>"
SNTIP_NEW = "<span class=\"sn-tip-h\">💡 コツ</span><span class=\"sn-tip-b\">'+s.tip+'</span></div>"


def fix(text):
    changes = []
    if "v13k:" not in text and CSS_ANCHOR in text:
        text = text.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_BLOCK, 1)
        changes.append("css:v13k-center")
    if "v13l:" not in text and CSS2_ANCHOR in text:
        text = text.replace(CSS2_ANCHOR, CSS2_ANCHOR + CSS2_BLOCK, 1)
        changes.append("css:v13l-thinbold+v13m-svg3d")
    if SNTIP_OLD in text:
        text = text.replace(SNTIP_OLD, SNTIP_NEW)
        changes.append("js:sntip-b-wrap")
    return text, changes


def targets():
    files = sorted(glob.glob("outputs/ux/000_TX/**/*_lex.html", recursive=True))
    for canon in ("canonical/GENESIS-CARD.html",):
        if os.path.exists(canon):
            files.append(canon)
    return files


def main():
    apply = "--apply" in sys.argv
    n = 0
    for f in targets():
        with io.open(f, "r", encoding="utf-8", newline="") as fh:
            raw = fh.read()
        is_crlf = "\r\n" in raw
        src = raw.replace("\r\n", "\n")
        # ① 表見出し中央(v13k) は .tx-sysmap-cross を持つ v13 LOOP-CARD（getInlineAnswerTablePanel）だけ
        #    アンカー越しに入る（他は CSS_ANCHOR 不在で自動スキップ）。
        # ② コツ箱の .sn-tip-b 未包み は solve-nav renderStep を持つ全 _lex 世代に存在するため、
        #    裸パターンを持つファイルも対象にする（同一defect・同一の安全な修正）。GENESIS-CARD は baseline。
        is_target = (
            "getInlineAnswerTablePanel" in src
            or SNTIP_OLD in src
            or "canonical" in f
        )
        if not is_target:
            continue
        new, changes = fix(src)
        if not changes:
            continue
        n += 1
        status = "APPLIED" if apply else "WOULD-FIX"
        print(f"[{status}] {os.path.basename(f)}: {', '.join(changes)}")
        if apply and new != src:
            out = new.replace("\n", "\r\n") if is_crlf else new
            with io.open(f, "w", encoding="utf-8", newline="") as fh:
                fh.write(out)
    print(f"\n{'applied' if apply else 'would-fix'} files: {n}")


if __name__ == "__main__":
    main()
