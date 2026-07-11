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
  python -X utf8 scripts/check-ariadne-quiz-dedup.py                    # 既定 glob 全件
  python -X utf8 scripts/check-ariadne-quiz-dedup.py <glob> [...]       # 対象指定
  python -X utf8 scripts/check-ariadne-quiz-dedup.py --report-similar   # 意味重複の定期点検用：
      完全一致でなく 8-gram Jaccard >=0.5 の横断クラスタを一覧表示（情報のみ・exit に影響しない。
      同一規範の言い換え想起が何問に散っているかを眺めて間引く運用のため）
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


def _ngrams(s, n=8):
    return set(s[i:i + n] for i in range(len(s) - n + 1)) if len(s) >= n else ({s} if s else set())


def report_similar(entries, th=0.5):
    """entries=[(fid, 原文設問, 正規化)]。別ファイル間 Jaccard>=th のクラスタを greedy に束ねて表示。"""
    grams = [_ngrams(nq) for _f, _q, nq in entries]
    n = len(entries)
    used = set()
    clusters = []
    for i in range(n):
        if i in used or not grams[i]:
            continue
        group = [i]
        for j in range(i + 1, n):
            if j in used or not grams[j] or entries[i][0] == entries[j][0]:
                continue
            inter = len(grams[i] & grams[j])
            if inter and inter / len(grams[i] | grams[j]) >= th:
                group.append(j)
        if len({entries[k][0] for k in group}) >= 2:
            used.update(group)
            clusters.append(group)
    clusters.sort(key=len, reverse=True)
    print(f'--- 類似クラスタ（8-gram Jaccard>={th}・別ファイル間・情報のみ）: {len(clusters)}組 ---')
    for g in clusters:
        fids = '・'.join(sorted({entries[k][0] for k in g}))
        print(f'  x{len(g)} [{fids}] {entries[g[0]][1][:56]}')


def main() -> int:
    do_similar = '--report-similar' in sys.argv
    patterns = [a for a in sys.argv[1:] if not a.startswith('--')] or [DEFAULT_GLOB]
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
    entries = []            # (fid, 原文, 正規化) — --report-similar 用
    ox = {'○': 0, '×': 0}   # 通常○×（想起除く）の全体バランス（情報表示）
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
                entries.append((fid, q, norm_question(q)))
            if 'data-recall' not in tag:
                mdcv = re.search(r'data-correct-value="(.)"', tag)
                if mdcv and mdcv.group(1) in ox:
                    ox[mdcv.group(1)] += 1

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
    if do_similar:
        report_similar(entries)
    total = sum(len(v) for v in seen.values())
    n_ox = ox['○'] + ox['×']
    rate = f'／通常○× {n_ox}枚 ○率{ox["○"]/n_ox:.0%}（当て勘目安25〜75%・per-fileはA41）' if n_ox else ''
    print(f'\n=== ARIADNE quiz corpus dedup: files={len(files)} arena設問={total}{rate} '
          f'/ WARN {len(warns)} / ERROR {len(errors)} ===')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
