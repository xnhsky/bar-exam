#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-arena-pure.py — 既存 ARIADNE を v1.4.0 ARENA-PURE へ一括是正（決定論・冪等）。

2026-07-11 監査の恒久対策（プール汚染の止血）。各ファイルに対して：
  1. `.bc-wrap`（答案構成の作法）内の .self-check-quiz から data-arena="1" を除去
     ＝作法ドリルをページ内確認専用にし、Lexia 復習プールへ流さない。
  2. `.bc-wrap` 外（解法ナビ等）の data-arena カードで、設問が科目共通の
     答案方法論（ariadne_arena_rules.METHOD_RE）に該当するものをブロック削除
     ＝体系順・4点セット・評価語 等の同一命題がプールへ量産されるのを止める。
  3. 版スタンプ ARIADNE v1.3.0 TXLEX-UNIFY → v1.4.0 ARENA-PURE（CSS/フッター/genmeta）。

本文（法的実体ドリル・教示・骨子・深掘り）は不変。編集は生テキスト上で行い
再エンコードしない＝**混在改行（CRLF/LF混じり）でも無関係行の改行を一切変えない**
（全体を CRLF↔LF へ均すと数百行の偽 diff が出る・feedback_preserve_crlf_in_python_tools）。

使い方:
  python -X utf8 scripts/ariadne-arena-pure.py --dry-run   # 変更内容の集計のみ
  python -X utf8 scripts/ariadne-arena-pure.py             # 適用（既定 glob 全件）
  python -X utf8 scripts/ariadne-arena-pure.py <file...>   # 対象指定
"""
from __future__ import annotations

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ariadne_arena_rules import METHOD_RE

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_GLOB = 'outputs/ux/001_ARIADNE/**/*_ARIADNE.html'
VER_MAP = [
    ('ARIADNE v1.3.0 TXLEX-UNIFY', 'ARIADNE v1.4.0 ARENA-PURE'),
    ('ARIADNE v1.2.0 PLACEHOLDER-LOCK', 'ARIADNE v1.4.0 ARENA-PURE'),
]


def extract_divs_pos(html, cls):
    blocks = []
    open_re = re.compile(r'<div\b[^>]*\bclass="[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*>', re.I)
    tag_re = re.compile(r'<(/?)div\b', re.I)
    for m in open_re.finditer(html):
        start = m.end(); depth = 1
        for t in tag_re.finditer(html, start):
            depth += 1 if t.group(1) == '' else -1
            if depth == 0:
                blocks.append((m.start(), t.start() + len('</div>'), m.group(0), html[start:t.start()]))
                break
    return blocks


def text_only(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()


def block_span_with_line(html, s, e):
    """ブロック span を「行頭の空白＋末尾の改行1つ」まで広げる（削除で空行を残さない）。
    CRLF / LF どちらの行末も 1 行ぶんだけ消費する（生テキスト前提）。"""
    ls = html.rfind('\n', 0, s)
    if ls >= 0 and html[ls + 1:s].strip() == '':
        s = ls + 1
    if html.startswith('\r\n', e):
        e += 2
    elif e < len(html) and html[e] == '\n':
        e += 1
    return s, e


def process(html):
    """LF正規化済み html を受け、(new_html, stripped, deleted, stamped) を返す。"""
    stripped = deleted = stamped = 0
    bc_spans = [(s, e) for s, e, _t, _i in extract_divs_pos(html, 'bc-wrap')]
    edits = []  # (start, end, replacement)
    for s, e, tag, inner in extract_divs_pos(html, 'self-check-quiz'):
        in_bc = any(b0 < s < b1 for b0, b1 in bc_spans)
        has_arena = 'data-arena="1"' in tag
        if in_bc:
            if has_arena:
                new_tag = tag.replace(' data-arena="1"', '', 1)
                edits.append((s, s + len(tag), new_tag))
                stripped += 1
            continue
        if not has_arena:
            continue
        qm = re.search(r'class="quiz-question"[^>]*>(.*?)</p>', inner, re.S)
        q = text_only(qm.group(1)) if qm else ''
        if q and METHOD_RE.search(q):
            ds, de = block_span_with_line(html, s, e)
            edits.append((ds, de, ''))
            deleted += 1
    for s, e, rep in sorted(edits, key=lambda x: -x[0]):
        html = html[:s] + rep + html[e:]
    for old, new in VER_MAP:
        n = html.count(old)
        if n:
            html = html.replace(old, new)
            stamped += n
    return html, stripped, deleted, stamped


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    files = []
    for pat in (args or [DEFAULT_GLOB]):
        p = pat if os.path.isabs(pat) else os.path.join(ROOT, pat)
        files.extend(sorted(glob.glob(p, recursive=True)))
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        print('[ERROR] 対象なし'); return 2

    t_strip = t_del = t_stamp = touched = 0
    for path in files:
        # 生テキストのまま編集する（\r\n を正規化しない）＝無関係行の改行を保つ。
        raw = open(path, 'rb').read().decode('utf-8')
        new_html, stripped, deleted, stamped = process(raw)
        if (stripped, deleted, stamped) == (0, 0, 0):
            continue
        touched += 1
        t_strip += stripped; t_del += deleted; t_stamp += stamped
        fid = os.path.basename(path)
        print(f'{"[DRY] " if dry else ""}{fid}: bc-arena除去 {stripped}／方法論ドリル削除 {deleted}／版スタンプ {stamped}')
        if not dry:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(new_html)
    print(f'\n=== arena-pure: files={len(files)} touched={touched} '
          f'bc-arena除去 {t_strip}／方法論ドリル削除 {t_del}／版スタンプ {t_stamp} ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
