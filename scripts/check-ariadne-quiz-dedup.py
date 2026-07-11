#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-ariadne-quiz-dedup.py — ARIADNE 周回ドリルの corpus 横断ゲート（v1.4.0 ARENA-PURE）。

validate-ariadne.py は 1 ファイル内しか見ないため、
「同じ設問が何十ファイルにも複製され Lexia 復習プールへ同一命題が量産される」
事故（2026-07-11 監査：完全一致 436/1544 枚＝28%）はここで検出する。

検査対象＝ arena カード（`data-arena="1"` の .self-check-quiz）のみ：
  D1: 正規化した設問文が 3 ファイル以上に出現 → ERROR（テンプレ複製の水準）
      ※同一規範が偶然 2 問で出るのは教育上ありうるため 2 ファイルは WARN。
  D2: 設問が科目共通の答案方法論（ariadne_arena_rules.METHOD_RE）→ ERROR
  D3: .bc-wrap（作法）内カードに data-arena → ERROR（作法ドリルはページ内専用）

使い方:
  python -X utf8 scripts/check-ariadne-quiz-dedup.py                 # 既定 glob 全件
  python -X utf8 scripts/check-ariadne-quiz-dedup.py <glob> [...]    # 対象指定
ERROR が 1 件でもあれば exit 1。
"""
from __future__ import annotations

import glob
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ariadne_arena_rules import METHOD_RE, norm_question

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_GLOB = 'outputs/ux/001_ARIADNE/**/*_ARIADNE.html'


def extract_divs_pos(html, cls):
    blocks = []
    open_re = re.compile(r'<div\b[^>]*\bclass="[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*>', re.I)
    tag_re = re.compile(r'<(/?)div\b', re.I)
    for m in open_re.finditer(html):
        start = m.end(); depth = 1
        for t in tag_re.finditer(html, start):
            depth += 1 if t.group(1) == '' else -1
            if depth == 0:
                blocks.append((m.start(), t.start(), m.group(0), html[start:t.start()])); break
    return blocks


def text_only(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()


def main() -> int:
    patterns = sys.argv[1:] or [DEFAULT_GLOB]
    files = []
    for pat in patterns:
        p = pat if os.path.isabs(pat) else os.path.join(ROOT, pat)
        files.extend(sorted(glob.glob(p, recursive=True)))
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        print('[ERROR] 対象 ARIADNE が見つからない:', patterns)
        return 2

    errors, warns = [], []
    # question_norm -> {file_id: 原文}
    seen = defaultdict(dict)
    for path in files:
        fid = re.sub(r'_ARIADNE\.html$', '', os.path.basename(path))
        html = open(path, encoding='utf-8', newline='').read().replace('\r\n', '\n')
        bc_spans = [(s, e) for s, e, _t, _i in extract_divs_pos(html, 'bc-wrap')]
        for s, _e, tag, inner in extract_divs_pos(html, 'self-check-quiz'):
            has_arena = 'data-arena="1"' in tag
            in_bc = any(b0 < s < b1 for b0, b1 in bc_spans)
            qm = re.search(r'class="quiz-question"[^>]*>(.*?)</p>', inner, re.S)
            q = text_only(qm.group(1)) if qm else ''
            if in_bc:
                if has_arena:
                    errors.append(f'[D3] {fid}: bc-wrap内ドリルに data-arena（作法はページ内専用）: {q[:36]}')
                continue
            if not has_arena:
                continue
            if q and METHOD_RE.search(q):
                errors.append(f'[D2] {fid}: arenaドリルが答案方法論: {q[:44]}')
            if q:
                seen[norm_question(q)].setdefault(fid, q)

    for _k, byfile in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        n = len(byfile)
        if n >= 3:
            fids = '・'.join(sorted(byfile)[:6]) + ('…' if n > 6 else '')
            errors.append(f'[D1] 同一設問が {n} ファイル（{fids}）: {next(iter(byfile.values()))[:44]}')
        elif n == 2:
            fids = '・'.join(sorted(byfile))
            warns.append(f'[D1] 同一設問が 2 ファイル（{fids}）: {next(iter(byfile.values()))[:44]}')

    for w in warns:
        print('[WARN] ', w)
    for e in errors:
        print('[ERROR]', e)
    total = sum(len(v) for v in seen.values())
    print(f'\n=== ARIADNE quiz corpus dedup: files={len(files)} arena設問={total} '
          f'/ WARN {len(warns)} / ERROR {len(errors)} ===')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
