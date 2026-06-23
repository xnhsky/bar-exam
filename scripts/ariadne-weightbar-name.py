#!/usr/bin/env python3
"""ARIADNE 配点バー 名称補完（2026-06-23・恒久対策）：
横グラフ（.bc-weight）の各セグメントが「論点名＋％」でなく "35%" 等の数字だけになる
名称欠落バグ（刑JX063 実害）を、直下の凡例（.bc-legend の l{y,x,c,w}）から名称を引いて
「論点名＋％」へ補完する。正典 ARIADNE／他全問と同じ字面（title=凡例原文・本文=名称＋％）を
再現する。冪等（既に名称があれば触らない）・LF 保存。既定 dry-run・--apply で書き込み。

mapping: wy↔ly  wx↔lx  wc↔lc  ww↔lw
既定で書込（ポリッシュ各段と同様）・--dry-run でプレビューのみ。"""
import glob, re, sys

WSPAN = re.compile(r'<span class="(w[ywxc])"( style="[^"]*")?(?: title="[^"]*")?>([^<]*)</span>')
PCT = re.compile(r'約?\s*\d+\s*%')
BARE = re.compile(r'^約?\s*\d+\s*%?$')


def legend_map(html):
    """凡例 l{y,x,c,w} → 原文テキスト（例 'ly' → '一体性 約35%'）"""
    m = {}
    for cls, txt in re.findall(r'<span class="(l[ywxc])"[^>]*>([^<]*)</span>', html):
        m[cls] = txt.strip()
    return m


def process(path, apply):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    leg = legend_map(s)
    fixed = []

    def repl(m):
        cls, style, txt = m.group(1), m.group(2) or '', m.group(3).strip()
        if not BARE.match(txt):           # 既に名称あり＝触らない（冪等）
            return m.group(0)
        lcls = 'l' + cls[1]               # wy→ly 等
        name = leg.get(lcls)
        if not name:                      # 凡例が無ければ補完不能（検証器が拾う）
            return m.group(0)
        pm = PCT.search(name)
        if pm:                            # 凡例に％あり：そのまま表示・title も凡例原文
            display, title = name, name
        else:                             # 凡例に名称のみ（例 構成・文章）：本問の％を付す
            bpm = PCT.search(txt)
            pct = bpm.group(0).replace(' ', '') if bpm else None
            display = f'{name} {pct}' if pct else name
            title = name
        fixed.append((cls, txt, display))
        return f'<span class="{cls}"{style} title="{title}">{display}</span>'

    out = WSPAN.sub(repl, s)
    if fixed and apply and out != s:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(out)
    return fixed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    apply = '--dry-run' not in sys.argv   # 既定で書込・--dry-run でプレビュー
    targets = args or (sorted(glob.glob('outputs/ux/000_ARIADNE/**/*_ARIADNE.html', recursive=True))
                       + ['canonical/ARIADNE.html'])
    total = 0
    for p in targets:
        fixed = process(p, apply)
        if fixed:
            total += 1
            tag = 'fixed' if apply else 'would-fix'
            print(f'[{tag}] {p}')
            for cls, old, new in fixed:
                print(f'    {cls}: "{old}" -> "{new}"')
    verb = 'fixed' if apply else 'would fix (--dry-run)'
    print(f'[weightbar-name] {verb} {total} file(s)')


if __name__ == '__main__':
    main()
