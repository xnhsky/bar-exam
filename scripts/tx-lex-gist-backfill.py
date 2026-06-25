#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tx-lex-gist-backfill.py — TX `_lex` の「要点一行＋全文折りたたみ」整備ツール（全7科目）

2026-06-25 ユーザー指示「記号選択肢を移動中に高速で解ける形に」を、新規生成だけでなく
既存 `_lex` にも横展開するための後追い掃き取り器。**機械でできる部分（ox-gist CSS の冪等
注入）を全科目に適用し、人手（=モデル）が要る部分（各選択肢の要点執筆）は worklist に出す**。

正典の形（gold = outputs/ux/000_TX/001_刑法/刑TX351_lex.html）：
  各 .ox-row は  .ox-label ＋ .ox-main（= <p class="ox-gist">要点</p> ＋
  <details class="ox-detail"><summary>全文</summary><span class="ox-stmt">…</span></details>）
  ＋ .ox-btn-group。CSS は canonical/SOLVE-NAV.html [STYLE] と同一（本ツールが注入する塊）。
  💡コツ（STEP/STMT の tip）は「決め手は<b>◯◯</b>。…」一行。

安全則：
  - `.ox-stmt` 本文（Lexia 復習プールの記録・検証 G30/G31 の対象）は一切触らない。
  - mc/空欄補充型（ox-stmt が <p class="ox-core-wrap"> 内＝解答後展開コア）は要点折りたたみの
    対象外（解答前ネタバレになる）。本ツールも worklist から除外する。
  - CSS 注入は冪等（既にあれば無変更）。本文の自動書き換えはしない。

使い方：
  python scripts/tx-lex-gist-backfill.py                 # 全科目を dry-run 集計（書き換えなし）
  python scripts/tx-lex-gist-backfill.py --subject 007_憲法
  python scripts/tx-lex-gist-backfill.py --inject-css    # ox-gist CSS を欠落ファイルへ注入（書込み）
  python scripts/tx-lex-gist-backfill.py --worklist out.md  # 要点執筆が必要な問の一覧を出力

worklist の各問は、gold(刑TX351) に倣って 1 問 1 サブエージェント（または new-tx と同じ規律）で
要点＋コツを執筆 → validate-tx-core.py Errors:0 を確認 → commit する。
"""
import argparse, glob, os, re, sys

ANCHOR = '.sn-btn.ghost{background:none; border:1.5px solid var(--accent); color:var(--accent);}'
GIST_MARK = '.answer-ox-grid .ox-gist{'   # 注入済み判定マーカー
CSS_BLOCK = '''

/* === 選択肢の高速化：要点一行（ox-gist）＋全文は折りたたみ（ox-detail）── 2026-06-25 === */
.answer-ox-grid .ox-row{ align-items:flex-start; }
.answer-ox-grid .ox-main{ flex:1 1 auto; min-width:0; }
.answer-ox-grid .ox-gist{ margin:0; font-weight:700; line-height:1.7; color:var(--bg-dark,#333); font-size:.97em; }
.answer-ox-grid .ox-gist b{ font-weight:800; color:var(--accent); }
.answer-ox-grid .ox-detail{ margin-top:8px; }
.answer-ox-grid .ox-detail > summary{ cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  font-size:.78em; font-weight:700; color:var(--accent); list-style:none; user-select:none;
  padding:2px 10px; border:1px solid var(--border-mid,#ccc); border-radius:999px; background:#fff; }
.answer-ox-grid .ox-detail > summary::-webkit-details-marker{ display:none; }
.answer-ox-grid .ox-detail > summary::before{ content:'＋ '; font-weight:800; }
.answer-ox-grid .ox-detail[open] > summary::before{ content:'− '; }
.answer-ox-grid .ox-detail[open] > summary{ background:var(--soft,#f3f3f3); }
.answer-ox-grid .ox-detail .ox-stmt{ display:block; flex:none; margin:8px 0 0; font-size:.85em;
  line-height:1.8; color:var(--bg-dark,#444); opacity:.85; }'''

ROOT = os.path.join('outputs', 'ux', '000_TX')
LONG = 90   # ox-stmt の素の本文がこの字数以上なら「長い＝要点化の効果大」


def visible_len(html_fragment):
    return len(re.sub(r'<[^>]+>', '', html_fragment))


def needs_authoring(text):
    """要点執筆が必要か：解く前に見える素の長い ox-stmt があり、まだ ox-gist 化されていない。
    mc/空欄補充型（ox-stmt が ox-core-wrap 内）は対象外（解答前ネタバレ回避）。"""
    if '<p class="ox-gist">' in text or '決め手は' in text:
        return False, 0   # 既に要点化 or コツ処理済み
    n = 0
    for m in re.finditer(r'<span class="ox-stmt">(.*?)</span>', text, re.S):
        pre = text[max(0, m.start() - 140):m.start()]
        if 'ox-core-wrap' in pre:
            continue   # 解答後展開コア＝対象外
        if visible_len(m.group(1)) >= LONG:
            n += 1
    return (n > 0), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject', help='科目フォルダ名（例 001_刑法 / 007_憲法）。省略で全科目')
    ap.add_argument('--inject-css', action='store_true', help='ox-gist CSS を欠落ファイルへ注入（書込み）')
    ap.add_argument('--worklist', help='要点執筆が必要な問の一覧を書き出すパス（.md）')
    args = ap.parse_args()

    pat = os.path.join(ROOT, args.subject if args.subject else '*', '*_lex.html')
    files = sorted(glob.glob(pat))
    if not files:
        print(f'対象 _lex なし: {pat}')
        return 0

    css_injected, css_pending, anchor_missing = 0, 0, []
    worklist = []
    bysubj = {}
    for f in files:
        subj = f.split(os.sep)[3]
        bysubj.setdefault(subj, {'n': 0, 'todo': 0})
        bysubj[subj]['n'] += 1
        t = open(f, encoding='utf-8').read()
        # 1) 要点執筆の要否（mc/空欄補充＝ox-core-wrap は対象外）
        need, cnt = needs_authoring(t)
        # 2) CSS は「要点を載せる問」だけに冪等注入（短文/mc には入れない＝無駄 diff 回避）
        if need and GIST_MARK not in t:
            if ANCHOR in t:
                if args.inject_css:
                    t = t.replace(ANCHOR, ANCHOR + CSS_BLOCK, 1)
                    open(f, 'w', encoding='utf-8').write(t)
                    css_injected += 1
                else:
                    css_pending += 1   # dry-run: 注入予定
            else:
                anchor_missing.append(os.path.basename(f))
        if need:
            worklist.append((f, cnt))
            bysubj[subj]['todo'] += 1

    print('=== TX _lex 要点化 整備 ===')
    print(f'対象ファイル: {len(files)}')
    for s in sorted(bysubj):
        d = bysubj[s]
        print(f'  {s}: {d["n"]} 問 / 要点執筆が必要 {d["todo"]} 問')
    if args.inject_css:
        print(f'CSS 注入: {css_injected} ファイル（要点執筆対象のうち未注入だったもの）')
    elif css_pending:
        print(f'CSS 未注入（--inject-css で要点執筆対象 {css_pending} ファイルへ注入予定）')
    if anchor_missing:
        print(f'⚠ アンカー（solve-nav style）欠落で CSS 注入不可: {anchor_missing}')
    print(f'要点執筆が必要な問: {len(worklist)}')

    if args.worklist and worklist:
        with open(args.worklist, 'w', encoding='utf-8') as w:
            w.write('# TX _lex 要点化 worklist（gold=刑TX351 に倣い 1問1エージェントで執筆）\n\n')
            for f, cnt in worklist:
                w.write(f'- [ ] `{f}`  （長い選択肢 {cnt} 件）\n')
        print(f'worklist 出力: {args.worklist}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
