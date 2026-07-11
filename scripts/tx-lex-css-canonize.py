#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX _lex v13 の <style> を正典CSS（gold 刑TX359）に統一する／照合ゲート。

背景：旧→v13 のパッチ連鎖や個別移行で、マーキング(.tx-stmt-o/x)・整理表(.tx-cross-tabletitle)・
solve-nav(.sn-*) 等の描画必須CSSが**ファイルごとにバラバラに欠落**し、「ゲート緑なのに見た目崩れ」
が頻発した（ユーザー指摘「毎回CSSで引っかかる」）。

恒久対処：v13 の <style> は **:root（パレット）以外は全問共通**であるべき。本ツールは
正典CSS（gold 359 の <style>）を唯一の真実とし、各 _lex の <style> を正典へ載せ替える
（:root=各問のパレットだけ保持・余分な未使用CSSは無害）。パレット要素は var() 駆動なので
他問へ流しても色は漏れない（420 実証済み）。

  適用: python scripts/tx-lex-css-canonize.py --apply [files or default=全v13]
  照合(ゲート): python scripts/tx-lex-css-canonize.py --check [files]   # 不一致で exit 1

正典を更新したら本ツールで全展開し、check をゲート（push前）に通す。
【2026-07-11 監査】CANON を corpus 内の gold コピー（刑TX359_lex）から正典本体
canonical/GENESIS-CARD.html へ変更（単一情報源の原則。359_lex は正典より古い実体で
基準にならない）。比較対象は先頭の素の <style> ブロックのみ＝第2の <style id="tx-xnav-style">
（XNAV/v13n/チップ CSS）は比較・置換の対象外。現状は世代差で不一致が多数（実測 102/110）
のため check-tx-lex-engine では**非ブロッキング可視化**として走らせ、--apply 全展開＋実機確認の
完了後にブロッキング昇格する。
"""
import re, sys, glob, io

CANON = 'canonical/GENESIS-CARD.html'  # v13 正典CSSの供給元（単一情報源＝正典本体・2026-07-11〜）

def get_style(text):
    m = re.search(r'<style>(.*?)</style>', text, re.S)
    return m.group(1) if m else None

def get_palette_root(style):
    """パレット :root（--accent を含む方）を返す。先頭の :root はフォント/スケール変数で
    パレットではないため、必ず --accent を含むブロックを選ぶ（漏れ防止）。"""
    for m in re.finditer(r':root\{.*?\}', style, re.S):
        if '--accent' in m.group(0):
            return m.group(0)
    return None

def style_minus_root(style):
    """パレット :root を除いた CSS（=全問共通であるべき本体）。照合に使う。"""
    pr = get_palette_root(style)
    if pr:
        style = style.replace(pr, '', 1)
    return style.strip()

def canon_style_for(file_style, canon_style):
    """正典の <style> の palette :root を、対象ファイルの palette :root に差し替えて返す。
    （共通CSS=正典／パレット=各問保持）。"""
    fp = get_palette_root(file_style)
    cp = get_palette_root(canon_style)
    if fp is None or cp is None:
        return canon_style
    return canon_style.replace(cp, fp, 1)

def is_v13(text):
    return 'getInlineAnswerTablePanel' in text

def main():
    apply = '--apply' in sys.argv
    check = '--check' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = args or [f for f in sorted(glob.glob('outputs/ux/000_TX/**/*_lex.html', recursive=True))]

    canon_text = io.open(CANON, encoding='utf-8').read().replace('\r\n', '\n')
    canon_style = get_style(canon_text)
    canon_core = style_minus_root(canon_style)

    changed = fails = scanned = 0
    for f in files:
        raw = io.open(f, 'r', encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        text = raw.replace('\r\n', '\n')
        if not is_v13(text):
            continue
        scanned += 1
        st = get_style(text)
        core = style_minus_root(st)
        ok = (core == canon_core)
        if check:
            if not ok:
                fails += 1
                # どのセレクタが欠けているか要約
                def sels(s):
                    return set(re.sub(r'\s+', ' ', m.group(1).strip())
                               for m in re.finditer(r'([^{}]+)\{[^{}]*\}', re.sub(r'/\*.*?\*/', '', s, flags=re.S))
                               if not m.group(1).strip().startswith('@'))
                miss = sels(canon_core) - sels(core)
                print(f"[CSS-NG] {f.split('/')[-1]}: 正典CSSと不一致"
                      + (f"（欠落セレクタ {len(miss)}: {', '.join(list(miss)[:5])}…）" if miss else "（差分あり）"))
            continue
        if ok:
            continue
        if apply:
            new_style = canon_style_for(st, canon_style)
            new = text.replace('<style>' + st + '</style>', '<style>' + new_style + '</style>', 1)
            out = new.replace('\n', '\r\n') if crlf else new
            io.open(f, 'w', encoding='utf-8', newline='').write(out)
            changed += 1
            print(f"[CANONIZE] {f.split('/')[-1]}")
        else:
            changed += 1
            print(f"[WOULD-CANONIZE] {f.split('/')[-1]}")

    if check:
        print(f"\nCSS canonical check: v13走査={scanned} / 不一致={fails}")
        sys.exit(1 if fails else 0)
    print(f"\n{'applied' if apply else 'would-change'}: {changed} / v13走査={scanned}")

if __name__ == '__main__':
    main()
