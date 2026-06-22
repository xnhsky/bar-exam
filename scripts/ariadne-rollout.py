#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刑JX001 で確定した手動CSS編集（バッジ濃淡・スロット・余白・タブ縮小）を他ARIADNEへ複製。
HTML変換（bsec強化/番号box/text-indent）は ariadne-matrix/stepnum/badge-indent が担当。
本スクリプトは「全ファイル共通の基盤CSS文字列」を OLD→NEW 置換する（LF/CRLF保存・冪等）。
OLD が見つからないファイルは報告のみ（既適用 or 構造差）。
"""
import sys, pathlib, glob

PAIRS = [
    # 1) 緑ピル（判旨内strong）：白on濃緑グラデ → 濃緑on淡緑＋枠＋text-indent
    ('.basis-card-body p.hanging > strong:first-child{display:inline-block; background:linear-gradient(135deg,var(--ai),var(--ai-deep)); color:#fff; font-family:var(--f-soft); font-size:.72em; font-weight:800; padding:2px 8px 1px; border-radius:4px; margin-right:7px; letter-spacing:.05em; vertical-align:2px}',
     '.basis-card-body p.hanging > strong:first-child{display:inline-block; background:var(--ai-soft); color:var(--ai-deep); border:1px solid var(--ai); font-family:var(--f-soft); font-size:.72em; font-weight:800; padding:1px 7px; border-radius:4px; margin-right:7px; letter-spacing:.05em; text-indent:.05em; vertical-align:1px}'),
    # 2) rank-A / tan-super：白on濃teal → 濃字on淡teal
    ('.athena-graft .rank-A,.athena-graft .tan-super{color:#fff; background:#4E8597}',
     '.athena-graft .rank-A,.athena-graft .tan-super{color:#173f49; background:#bfdce2}'),
    # 3) rank-B / tan-high：淡teal化
    ('.athena-graft .rank-B,.athena-graft .tan-high{color:#2E4953; background:#88AEBA}',
     '.athena-graft .rank-B,.athena-graft .tan-high{color:#1f4651; background:#d6e8ec}'),
    # 4) 見出しスロットをブロック化（パズル崩れ解消）
    ('.kslot[data-type="b1"]{border-color:var(--li-line); min-width:11em}',
     '.kslot[data-type="b1"]{border-color:var(--li-line); min-width:11em; display:block; width:max-content; max-width:100%; margin:2px 0 7px}'),
    # 5) 判旨カードのバッジ↔本文の余白拡大
    ('.athena-graft blockquote.case{position:relative; margin:20px 0 12px; padding:14px 16px 12px; border-radius:6px;',
     '.athena-graft blockquote.case{position:relative; margin:24px 0 12px; padding:22px 16px 12px; border-radius:6px;'),
    # 6) 模範答案の役割タブ（食み出しバッジ）を縮小
    ('.model-answer p.role::before{\n  content:var(--lbl); position:absolute; top:-12px; left:13px; padding:4px 13px 3px;\n  font-family:var(--f-soft); font-weight:800; font-size:.68rem; letter-spacing:.1em; color:var(--cd);\n  background:var(--cb); border:none; border-radius:9px; box-shadow:0 2px 6px rgba(80,60,80,.13); text-indent:.1em;\n}',
     '.model-answer p.role::before{\n  content:var(--lbl); position:absolute; top:-10px; left:13px; padding:2px 9px 1px;\n  font-family:var(--f-soft); font-weight:800; font-size:.6rem; letter-spacing:.08em; color:var(--cd);\n  background:var(--cb); border:none; border-radius:7px; box-shadow:0 2px 6px rgba(80,60,80,.13); text-indent:.08em;\n}'),
    # 7) 周回ドリル○× タブの上下幅を狭める
    ('.self-check-quiz::before{content:"周回ドリル ○×"; position:absolute; top:-10px; left:14px; font-family:var(--f-soft);\n  background:linear-gradient(135deg,var(--li),var(--li-deep)); color:#fff; font-size:.66rem; font-weight:800; border-radius:7px; padding:2px 10px; letter-spacing:.03em}',
     '.self-check-quiz::before{content:"周回ドリル ○×"; position:absolute; top:-9px; left:14px; font-family:var(--f-soft);\n  background:linear-gradient(135deg,var(--li),var(--li-deep)); color:#fff; font-size:.64rem; font-weight:800; line-height:1.4; border-radius:7px; padding:0 10px 1px; letter-spacing:.03em; text-indent:.03em}'),
]


def process(path):
    with open(path, encoding='utf-8', newline='') as fh:
        txt = fh.read()
    nl = '\r\n' if '\r\n' in txt else '\n'
    applied, missing = 0, []
    for i, (old, new) in enumerate(PAIRS, 1):
        o = old.replace('\n', nl); n = new.replace('\n', nl)
        if o in txt:
            txt = txt.replace(o, n, 1); applied += 1
        elif n in txt:
            pass  # 既適用＝冪等
        else:
            missing.append(i)
    if applied:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(txt)
    return applied, missing


def main():
    files = []
    for a in sys.argv[1:]:
        if not a.startswith('--'):
            files += glob.glob(a)
    for fp in files:
        if fp.endswith('.html'):
            ap, miss = process(pathlib.Path(fp))
            tag = f" MISSING={miss}" if miss else ""
            print(f"{pathlib.Path(fp).name}: applied={ap}/7{tag}")


if __name__ == '__main__':
    main()
