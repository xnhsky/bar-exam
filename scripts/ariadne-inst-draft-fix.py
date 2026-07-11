#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-inst-draft-fix.py — A39/A38 の一括是正（決定論・冪等・生テキスト編集）。

A39: 答案構成の作法 `.bc-inst` を「ラベル（.ji）＋本文（.bi）」の2カラム正典へ：
  - div型で .bi 無し → `<span class="ji">…</span>` 直後から閉じまでを `<div class="bi">…</div>` で包む
  - p型 `<p class="bc-inst">…</p>` → div へ変換して同様に .bi ラップ（p は div を内包できないため）
A38: `.draft-problem` を上部問題文 `.problem .pq` の逐語コピーへ（§9-4・一行圧縮は .draft-digest の役目）：
  - `.dp-b` span があればその中身を、無ければ `.draft-problem` 直下の中身を pq の innerHTML で置換

生テキスト編集（再エンコードなし）＝無関係行の改行を一切変えない。ji 無し・pq 複数などの
非標準形は変更せず報告（手動判断へ）。

使い方:
  python -X utf8 scripts/ariadne-inst-draft-fix.py --dry-run
  python -X utf8 scripts/ariadne-inst-draft-fix.py            # 既定 glob 全件
  python -X utf8 scripts/ariadne-inst-draft-fix.py <file...>
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
DEFAULT_GLOB = 'outputs/ux/001_ARIADNE/**/*_ARIADNE.html'
JI_RE = re.compile(r'<span\b[^>]*class="[^"]*\bji\b[^"]*"[^>]*>.*?</span>', re.S)


def extract_divs_pos(html, cls):
    blocks = []
    open_re = re.compile(r'<div\b[^>]*\bclass="[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*>', re.I)
    tag_re = re.compile(r'<(/?)div\b', re.I)
    for m in open_re.finditer(html):
        start = m.end(); depth = 1
        for t in tag_re.finditer(html, start):
            depth += 1 if t.group(1) == '' else -1
            if depth == 0:
                blocks.append((m.start(), m.end(), t.start(), m.group(0)))  # (open_s, inner_s, inner_e, open_tag)
                break
    return blocks


def fix_bcinst(raw, report):
    edits = []  # (start, end, replacement)
    # --- div型（.bi 無し） ---
    for open_s, inner_s, inner_e, open_tag in extract_divs_pos(raw, 'bc-inst'):
        inner = raw[inner_s:inner_e]
        if 'class="bi"' in inner:
            continue
        jm = JI_RE.search(inner)
        if not jm:
            report.append(f'  [SKIP] div型bc-instにjiラベル無し: {inner[:40]!r}')
            continue
        body = inner[jm.end():]
        new_inner = inner[:jm.end()] + '<div class="bi">' + body + '</div>'
        edits.append((inner_s, inner_e, new_inner))
    # --- p型 → div型＋.bi ---
    for m in re.finditer(r'<p\b([^>]*\bclass="[^"]*\bbc-inst\b[^"]*"[^>]*)>(.*?)</p>', raw, re.S):
        attrs, inner = m.group(1), m.group(2)
        jm = JI_RE.search(inner)
        if not jm:
            report.append(f'  [SKIP] p型bc-instにjiラベル無し: {inner[:40]!r}')
            continue
        body = inner[jm.end():]
        new_block = '<div' + attrs + '>' + inner[:jm.end()] + '<div class="bi">' + body + '</div></div>'
        edits.append((m.start(), m.end(), new_block))
    return edits


def fix_draft_problem(raw, report):
    pqs = re.findall(r'<p class="pq"[^>]*>(.*?)</p>', raw, re.S)
    if len(pqs) != 1:
        if re.search(r'class="draft-problem"', raw):
            report.append(f'  [SKIP] pq段落が{len(pqs)}個＝draft-problem自動置換対象外')
        return []
    pq_inner = pqs[0]

    def text_only(s):
        return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', s))

    blocks = extract_divs_pos(raw, 'draft-problem')
    if not blocks:
        return []
    open_s, inner_s, inner_e, _tag = blocks[0]
    inner = raw[inner_s:inner_e]
    # 既に逐語相当（validator A38 と同じ 0.85 基準）なら不変
    if len(text_only(inner)) >= 0.85 * len(text_only(pq_inner)):
        return []
    dpb = re.search(r'(<span class="dp-b"[^>]*>)(.*?)(</span>)', inner, re.S)
    if dpb:
        new_inner = inner[:dpb.start()] + dpb.group(1) + pq_inner + dpb.group(3) + inner[dpb.end():]
    else:
        new_inner = pq_inner
    return [(inner_s, inner_e, new_inner)]


def main() -> int:
    dry = '--dry-run' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = []
    for pat in (args or [DEFAULT_GLOB]):
        p = pat if os.path.isabs(pat) else os.path.join(ROOT, pat)
        files.extend(sorted(glob.glob(p, recursive=True)))
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        print('[ERROR] 対象なし'); return 2

    t_bi = t_dp = touched = 0
    for path in files:
        raw = open(path, 'rb').read().decode('utf-8')
        report = []
        e_bi = fix_bcinst(raw, report)
        e_dp = fix_draft_problem(raw, report)
        edits = e_bi + e_dp
        if report:
            print(os.path.basename(path) + ':')
            for r in report:
                print(r)
        if not edits:
            continue
        for s, e, rep in sorted(edits, key=lambda x: -x[0]):
            raw = raw[:s] + rep + raw[e:]
        touched += 1
        t_bi += len(e_bi); t_dp += len(e_dp)
        print(f'{"[DRY] " if dry else ""}{os.path.basename(path)}: bc-inst 2カラム化 {len(e_bi)}／draft-problem 逐語化 {len(e_dp)}')
        if not dry:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(raw)
    print(f'\n=== inst-draft-fix: files={len(files)} touched={touched} bc-inst {t_bi}箇所／draft-problem {t_dp}件 ===')
    return 0


if __name__ == '__main__':
    main()
