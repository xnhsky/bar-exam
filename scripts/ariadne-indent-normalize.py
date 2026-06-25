#!/usr/bin/env python3
"""ARIADNE 字下げリセット＆トラッキング相殺の一括正規化（2026-06-23）。
本文 p{text-indent:1em} の遺伝がインラインUI（バッジ/ラベル/タグ/::before見出しタブ）へ
波及する問題と letter-spacing の右余白ズレを根治。<style> 末尾に !important ブロックを
1つ追記し、(A) 全バッジ系を text-indent:0!important で遺伝遮断、(B) letter-spacing を持つ
shrink-to-fit ピル/タブには ls 同値の text-indent!important を与え中央化。
冪等（マーカー検出でskip）・LF保存。"""
import glob, sys

MARK = '/* === BADGE-INDENT-NORMALIZE v1 === */'

BLOCK = MARK + '\n' + """\
/* (A) 字下げ遺伝の遮断＝バッジ/ラベル/タグ/見出しタブ/サマリを text-indent:0 に強制リセット */
.tag-issue,.badge,.bc-inst .ji,.mast-type b,.bone .b1,.kp-model .b1,
.kicker,.sec-h .kick,.case-kick,.bc-col .col-h,.bc-body .ph,.bc-flow,
.go-athena,details.reveal-answer > summary,details#deep-dive > summary,.kp-toggle,
.athena-graft .graft-h,.athena-graft .basis-card-header,.basis-card-header,.athena-graft th,
.basis-card-body .judgment-text,.basis-card-body .ron-mark,.steps-rail span b,.step .num .code{text-indent:0 !important;}
/* (B) letter-spacing の右余白ズレ相殺＝同値 text-indent で枠内中央化（shrink-to-fit ピル/タブ） */
.self-check-quiz::before{text-indent:.03em !important;}
.model-answer p.role::before{text-indent:.03em !important;}
.bc-flow span{text-indent:.03em !important;}
.basis-card-body .para-num{text-indent:.04em !important;}
.athena-graft blockquote.case::before{text-indent:.04em !important;}
.athena-graft .key-box::before{text-indent:.1em !important;}
.freq-badge,.athena-graft .freq-badge{text-indent:.06em !important;}
.kd-label{text-indent:.05em !important;}
.athena-graft h5{text-indent:.06em !important;}
.athena-graft .rank-A,.athena-graft .rank-B,.athena-graft .rank-C,.athena-graft .tan{text-indent:.06em !important;}
.basis-card-body p.hanging > strong:first-child{text-indent:.05em !important;}
.model-answer .ma-h{text-indent:.05em !important;}
.draft-digest .ddl{text-indent:.05em !important;}
"""

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    if MARK in s:
        return False
    idx = s.rfind('</style>')
    if idx == -1:
        return False
    s2 = s[:idx] + BLOCK + s[idx:]
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s2)
    return True

def main():
    targets = sys.argv[1:] or (sorted(glob.glob('outputs/ux/001_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html'])
    n = 0
    for p in targets:
        if process(p):
            n += 1
    print(f"[indent-normalize] {n}/{len(targets)} updated")

if __name__ == '__main__':
    main()
