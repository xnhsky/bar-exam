#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIADNE 骨子（.bone）の各第N（罪責）を薄グレー箱 .bsec で区切る。
- CSS: .bone .iss{...} の直後に .bsec ルールを 1 回挿入（冪等）
- HTML: <div class="bone" ...> 内を <span class="b1"> 境界で分割し、各セクションを
        <div class="bsec"> で包む（前後空白を trim・pre-wrap は親から継承）
記載方式（pre-wrap・縦並び・b1 を各箱の先頭行）は維持。JS は parentNode.replaceChild で
ネスト非依存に動くため穴埋めパズル・モデル表示とも無改修で動作する。
冪等：既に class="bsec" を含む bone はスキップ。
"""
import re, sys, pathlib

CSS_ANCHOR = '.bone .iss{color:var(--shu-deep); font-weight:700}'
CSS_BLOCK = (
    '\n/* === 骨子 各罪責を薄グレー箱で区切り（2026-06-22） === */\n'
    '.bone .bsec,.kp-model .bsec{white-space:pre-wrap; background:#f3f2f5; '
    'border:1px solid #e6e3ec; border-radius:9px; padding:8px 13px 9px; margin:11px 0 0}\n'
    '.bone .bsec:first-child,.kp-model .bsec:first-child{margin-top:0}'
)

BONE_RE = re.compile(r'(<div class="bone"[^>]*>)(.*?)(</div>)', re.DOTALL)
B1_RE = re.compile(r'<span class="b1">')


def wrap_bone(inner: str) -> str:
    if 'class="bsec"' in inner:
        return inner  # 冪等
    starts = [m.start() for m in B1_RE.finditer(inner)]
    if not starts:
        return inner
    preamble = inner[:starts[0]]
    sections = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(inner)
        body = inner[s:e].strip('\n').rstrip()
        # 先頭の余分な空白のみ除去（b1 span が先頭に来る）。内部の改行・字下げは保持
        body = body.lstrip('\n')
        sections.append('<div class="bsec">' + body + '</div>')
    pre = preamble.strip()
    pre = (pre + '\n') if pre else ''
    return pre + ''.join(sections)


def process(path: pathlib.Path) -> str:
    # newline='' で改行変換を無効化＝元の改行コード（LF/CRLF）を保存
    with open(path, encoding='utf-8', newline='') as fh:
        txt = fh.read()
    nl = '\r\n' if '\r\n' in txt else '\n'
    global CSS_BLOCK
    css = CSS_BLOCK.replace('\n', nl)
    changed = []
    # 1) CSS
    if '.bone .bsec' not in txt and CSS_ANCHOR in txt:
        txt = txt.replace(CSS_ANCHOR, CSS_ANCHOR + css, 1)
        changed.append('css')
    # 2) HTML bone
    def repl(m):
        new_inner = wrap_bone(m.group(2))
        if new_inner != m.group(2):
            changed.append('bone')
        return m.group(1) + new_inner + m.group(3)
    txt = BONE_RE.sub(repl, txt, count=1)
    return txt, changed


def main():
    files = [pathlib.Path(p) for p in sys.argv[1:]]
    dry = '--dry' in sys.argv
    files = [f for f in files if f.suffix == '.html']
    for f in files:
        new, changed = process(f)
        if changed and not dry:
            with open(f, 'w', encoding='utf-8', newline='') as fh:
                fh.write(new)
        print(f"{'DRY ' if dry else ''}{f.name}: {','.join(changed) if changed else 'no-change'}")


if __name__ == '__main__':
    main()
