#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ariadne-draftproblem-backfill.py
================================
ARIADNE 解法ナビの「試験下書き」`.drafting` ブロックの問題文再掲を
**原文（再掲）＋圧縮メモの二段構成**へ揃えるバックフィル（冪等）。

経緯（2026-06-21・ユーザー指示）：
  spec §9-4 は `.draft-problem`＝「問題文原文（再掲）」と定めるが、生成プロンプトが
  曖昧で、実ファイルでは原文ではなく圧縮メモ調が入っていた。答案構成（骨子）の直前で
  上部の問題文まで遡らずに済むよう、原文を `.draft-problem` に再掲し、従来の圧縮メモは
  `.draft-digest`（骨子用一行圧縮）として併存させる。

挙動：
  各 ARIADNE HTML について――
   1. 上部 `<p class="pq">…</p>`（問題文原文）を抽出。
   2. 下書きブロックの `<div class="draft-problem">…</div>`（現状＝圧縮メモ）があれば、
      その中身を圧縮メモとして退避し、
        <div class="draft-problem">{原文}</div>
        <div class="draft-digest"><span class="ddl">骨子用に一行圧縮</span>{圧縮メモ}</div>
      へ置換。
   3. `.draft-problem` が無い旧フォーマット（054/055 等）は、`.dh` 見出し直後に
      `<div class="draft-problem">{原文}</div>` を挿入（圧縮メモが無いため digest は付けない）。
   4. `.draft-digest` 用 CSS を未定義なら `.draft-problem b{…}` 規則の直後に追記。
  既に `.draft-digest`（本体）を持つファイルは本体変換をスキップ（冪等）。

使い方：
  python scripts/ariadne-draftproblem-backfill.py                 # dry-run（既定・差分要約のみ）
  python scripts/ariadne-draftproblem-backfill.py --apply         # 書き込み
  python scripts/ariadne-draftproblem-backfill.py <file|dir> ...  # 対象指定（既定は刑法フォルダ）
"""
import sys, re, glob, os

DEFAULT_DIR = "outputs/ux/000_ARIADNE/001_刑法"

CSS_DIGEST = (
    "\n.draft-digest{font-family:var(--f-soft); font-size:.84rem; line-height:1.8; "
    "color:var(--ink-soft); background:rgba(0,0,0,.018); border:1px solid var(--line-2); "
    "border-radius:10px; padding:9px 13px; margin:0 0 13px}"
    "\n.draft-digest .ddl{display:inline-block; font-family:var(--f-soft); font-weight:700; "
    "font-size:.68rem; letter-spacing:.05em; color:#fff; background:var(--gd-line); "
    "border-radius:6px; padding:1px 8px; margin-right:8px; vertical-align:1px}"
    "\n.draft-digest b{color:var(--shu-deep); font-weight:700}"
)

PQ_RE      = re.compile(r'<p class="pq">(.*?)</p>', re.S)
# draft-problem は <div> でも <p> でも書かれている（旧 052 は <p>）。タグを捕捉して閉じる。
DP_RE      = re.compile(r'<(div|p) class="draft-problem">(.*?)</\1>', re.S)
DH_RE      = re.compile(r'(<p class="dh">.*?</p>)', re.S)
CSS_ANCHOR = '.draft-problem b{color:var(--shu-deep)}'
DIGEST_LABEL = '骨子用に一行圧縮'
DH_DEFAULT = ('<p class="dh">✍ まず下書き用紙にこう整理する'
              '<small>論点名・規範はまだ書かない＝それが想起の対象</small></p>')


def process(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    orig = src
    notes = []

    # --- CSS: .draft-digest 規則を未定義なら追記 ---
    if ".draft-digest{" not in src and CSS_ANCHOR in src:
        src = src.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_DIGEST, 1)
        notes.append("css+")

    # --- 本体: 既に digest 本体があれば変換済み（冪等スキップ）---
    has_digest_body = '<div class="draft-digest">' in src
    if not has_digest_body:
        m_pq = PQ_RE.search(src)
        if not m_pq:
            notes.append("NO-PQ(skip)")
        else:
            full = m_pq.group(1).strip()
            m_dp = DP_RE.search(src)
            if m_dp:
                condensed = m_dp.group(2).strip()
                # 原文と圧縮メモが同一なら digest は付けず原文だけ残す
                if _norm(condensed) == _norm(full):
                    repl = '<div class="draft-problem">' + full + '</div>'
                    notes.append("dp=full(no-digest)")
                else:
                    repl = (
                        '<div class="draft-problem">' + full + '</div>\n'
                        '    <div class="draft-digest"><span class="ddl">'
                        + DIGEST_LABEL + '</span>' + condensed + '</div>'
                    )
                    notes.append("dp->full+digest")
                src = src[:m_dp.start()] + repl + src[m_dp.end():]
            else:
                draft_idx = src.find('<div class="drafting">')
                if draft_idx != -1:
                    # 旧フォーマット：drafting はあるが draft-problem 無し → dh 直後に原文を挿入
                    m_dh = DH_RE.search(src, draft_idx)
                    if not m_dh:
                        notes.append("NO-DH(skip)")
                    else:
                        ins = ('\n    <div class="draft-problem">' + full + '</div>')
                        src = src[:m_dh.end()] + ins + src[m_dh.end():]
                        notes.append("dp inserted(full)")
                else:
                    # drafting ブロックごと無い（055 等）→ skeleton 直前に最小ブロックを新設
                    sk_idx = src.find('<div class="skeleton">')
                    if sk_idx == -1:
                        notes.append("NO-SKELETON(skip)")
                    else:
                        block = ('<div class="drafting">\n'
                                 '    ' + DH_DEFAULT + '\n'
                                 '    <div class="draft-problem">' + full + '</div>\n'
                                 '  </div>\n  ')
                        src = src[:sk_idx] + block + src[sk_idx:]
                        notes.append("drafting block inserted")

    changed = src != orig
    return changed, notes, src


def _norm(s):
    return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', s))


def main(argv):
    apply = "--apply" in argv
    targets = [a for a in argv if not a.startswith("--")]
    files = []
    if not targets:
        files = sorted(glob.glob(os.path.join(DEFAULT_DIR, "*_ARIADNE.html")))
    else:
        for t in targets:
            if os.path.isdir(t):
                files += sorted(glob.glob(os.path.join(t, "*_ARIADNE.html")))
            else:
                files.append(t)

    n_changed = 0
    for path in files:
        changed, notes, out = process(path)
        tag = "CHANGED" if changed else "ok     "
        print(f"[{tag}] {os.path.basename(path):28s} {' '.join(notes)}")
        if changed:
            n_changed += 1
            if apply:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out)

    mode = "APPLIED" if apply else "DRY-RUN (use --apply to write)"
    print(f"\n{mode}: {n_changed}/{len(files)} file(s) changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
