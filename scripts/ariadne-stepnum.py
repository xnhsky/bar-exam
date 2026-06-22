#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIADNE 骨子（.bone）のステップ番号（行頭 1/2/3…）を 1️⃣ 風のボックスに包む。
- bone をバランス div で正しく抽出（bsec 入れ子に強い）→ その範囲内だけで番号を拾う
- 第1ステップは b1 見出し直後（</span>␣␣\\d␣）、以降は 改行直後（\\n␣␣\\d␣）
- 「199/203」「217条」等の本文中の数字は行頭でないので巻き込まない
冪等：bone に class="bn" があればスキップ。LF/CRLF 保存。
"""
import re, sys, pathlib, glob

CSS_ANCHOR = "letter-spacing:.01em}"  # ariadne-matrix が入れた .b1 ルール末尾
CSS_BN = (
    '\n.bone .bn,.kp-model .bn{display:inline-block; min-width:1.4em; text-align:center; '
    'font-family:var(--f-disp); font-weight:800; font-size:.82em; color:var(--gd-deep); '
    'background:var(--gd-soft); border:1.5px solid var(--gd-line); border-radius:6px; '
    'padding:0 5px; margin-right:4px; line-height:1.5; vertical-align:1px}'
)


def find_bone(txt):
    start = txt.find('<div class="bone"')
    if start < 0:
        return None
    depth = 0
    for m in re.finditer(r'<div\b|</div>', txt[start:]):
        if m.group() == '</div>':
            depth -= 1
            if depth == 0:
                return start, start + m.end()
        else:
            depth += 1
    return None


def process(path: pathlib.Path):
    with open(path, encoding='utf-8', newline='') as fh:
        txt = fh.read()
    nl = '\r\n' if '\r\n' in txt else '\n'
    changed = []
    # 1) CSS
    if '.bone .bn' not in txt and CSS_ANCHOR in txt:
        txt = txt.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_BN.replace('\n', nl), 1)
        changed.append('css')
    # 2) 番号ボックス（bone 範囲限定）
    span = find_bone(txt)
    if span:
        s, e = span
        bone = txt[s:e]
        if 'class="bn"' not in bone:
            # 第1ステップ：b1 見出し直後
            bone = re.sub(r'(<span class="b1">[^<]*</span>  )(\d)( )',
                          r'\1<span class="bn">\2</span>\3', bone)
            # 以降：改行直後（2スペース字下げの行頭番号のみ）
            bone = re.sub(r'(' + re.escape(nl) + r'  )(\d)( )',
                          r'\1<span class="bn">\2</span>\3', bone)
            if bone != txt[s:e]:
                txt = txt[:s] + bone + txt[e:]
                changed.append('bn')
    if changed:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(txt)
    return changed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = []
    for a in args:
        files += glob.glob(a)
    for fp in files:
        if fp.endswith('.html'):
            c = process(pathlib.Path(fp))
            print(f"{pathlib.Path(fp).name}: {','.join(c) if c else 'no-change'}")


if __name__ == '__main__':
    main()
