#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-qa-mark-fix.py — 周回ドリル答えの円バッジを qa-mark 契約へ移行（決定論・冪等）。

2026-07-26 実機報告（刑JX020・iPad/Lexia）の恒久対策。旧エンジン CSS
`.quiz-answer b:first-child{…width:1.5em…border-radius:50%…}` は「答え冒頭の
○/× 1文字を白丸バッジで出す」意図だが、:first-child はテキストノードを無視する
ため、**想起（recall）型の答えのように文中に最初の <b> が来る場合も誤マッチ**し、
長いキーワードが 1.5em 幅へ押し込まれ 1 文字ずつ縦落ちする（corpus 実測：
想起型 103 answer が縦落ち・冒頭2〜9字ラベル 23 answer が円内潰れ）。

各ファイルに対して：
  1. CSS セレクタ `.quiz-answer b:first-child{` → `.quiz-answer b.qa-mark{`
     （宣言部は不変＝円バッジの見た目は維持）。
  2. `.recall .quiz-btn{min-width:96px; …}` へ `width:auto; padding:0 14px;
     white-space:nowrap;` を前置（基底 `.quiz-btn{width:48px}` の固定幅が勝ち
     「書けなかった」が2行に折れる実機崩れの同時修正）。
  3. `.quiz-answer` 直後の冒頭 `<b>○</b>`／`<b>×</b>` に class="qa-mark" を付与
     （○×型 1,726＋想起型 53 の正当な円バッジを維持）。

本文（設問・答えの文章・data-* 属性）は不変。編集は生テキスト上で行い
再エンコードしない＝混在改行（CRLF/LF）でも無関係行の改行を一切変えない
（feedback_preserve_crlf_in_python_tools）。

使い方:
  python -X utf8 scripts/ariadne-qa-mark-fix.py --check     # 未移行の検出のみ（exit 1）
  python -X utf8 scripts/ariadne-qa-mark-fix.py --dry-run   # 変更集計のみ
  python -X utf8 scripts/ariadne-qa-mark-fix.py             # 適用（canonical＋既定 glob 全件）
  python -X utf8 scripts/ariadne-qa-mark-fix.py <file...>   # 対象指定
"""
from __future__ import annotations

import glob
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TARGETS = ['canonical/ARIADNE.html', 'outputs/ux/001_ARIADNE/**/*_ARIADNE.html']

OLD_CSS_SEL = '.quiz-answer b:first-child{'
NEW_CSS_SEL = '.quiz-answer b.qa-mark{'
OLD_BTN_RULE = '.recall .quiz-btn{min-width:96px; font-size:.86rem; font-family:var(--f-soft); font-weight:700}'
NEW_BTN_RULE = ('.recall .quiz-btn{width:auto; min-width:96px; padding:0 14px; white-space:nowrap; '
                'font-size:.86rem; font-family:var(--f-soft); font-weight:700}')
MARK_RE = re.compile(r'(<div class="quiz-answer"[^>]*>)(\s*)<b>([○×])</b>')


def process(text: str):
    """text → (new_text, stats)。冪等：適用済みなら変更 0。"""
    stats = {'css_sel': 0, 'btn_rule': 0, 'qa_mark': 0}
    if OLD_CSS_SEL in text:
        stats['css_sel'] = text.count(OLD_CSS_SEL)
        text = text.replace(OLD_CSS_SEL, NEW_CSS_SEL)
    if OLD_BTN_RULE in text:
        stats['btn_rule'] = text.count(OLD_BTN_RULE)
        text = text.replace(OLD_BTN_RULE, NEW_BTN_RULE)
    text, n = MARK_RE.subn(r'\1\2<b class="qa-mark">\3</b>', text)
    stats['qa_mark'] = n
    return text, stats


def main():
    args = [a for a in sys.argv[1:]]
    check = '--check' in args
    dry = '--dry-run' in args
    paths = [a for a in args if not a.startswith('--')]
    if not paths:
        paths = []
        for pat in DEFAULT_TARGETS:
            paths.extend(sorted(glob.glob(os.path.join(ROOT, pat), recursive=True)))
    changed = pending = 0
    total = {'css_sel': 0, 'btn_rule': 0, 'qa_mark': 0}
    for p in paths:
        raw = open(p, 'rb').read()
        text = raw.decode('utf-8')
        new, st = process(text)
        if new == text:
            continue
        pending += 1
        for k in total:
            total[k] += st[k]
        rel = os.path.relpath(p, ROOT)
        if check or dry:
            print(f"[{'CHECK' if check else 'DRY'}] {rel}: css_sel={st['css_sel']} btn_rule={st['btn_rule']} qa_mark={st['qa_mark']}")
            continue
        open(p, 'wb').write(new.encode('utf-8'))
        changed += 1
        print(f"[FIX] {rel}: css_sel={st['css_sel']} btn_rule={st['btn_rule']} qa_mark={st['qa_mark']}")
    print(f"-- files={len(paths)} 要変更={pending} 適用={changed} "
          f"(css_sel={total['css_sel']} btn_rule={total['btn_rule']} qa_mark={total['qa_mark']})")
    if check and pending:
        sys.exit(1)


if __name__ == '__main__':
    main()
