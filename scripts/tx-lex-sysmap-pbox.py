#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx-lex-sysmap-pbox.py ── v13.1.0 体系マップ「親カテゴリ箱」を 371 改善スタイル（太字キー行＋淡色補足＋
色チップ）へ標準化する決定論ツール。親箱は問題固有でなく「科目の骨格」なので、科目別の正典ブロックへ
差し替える（放火＝客体三分108/109/110・文書偽造＝有形/無形/行使）。非標準マップ（五概念/二軸/派生等）は
SKIP して問題固有の作り込みを温存する。冪等（既に pbox-chip 済なら NOCHANGE）。本文（肢カード/正誤表/学説）不変。

対象領域＝`<g transform="translate(265,150)">` から `<path d="M750 300 V336"`（本問5局面への接続線）直前まで。
CSS `.tx-sysmap-svg .pbox-chip{…}` を nb-badge の隣へ注入（無ければ）。

使い方: python -X utf8 scripts/tx-lex-sysmap-pbox.py <file1> [file2 ...]
"""
import sys
import re

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PBOX_CSS = '.tx-sysmap-svg .pbox-chip{ filter:drop-shadow(0 1.5px 2px rgba(50,25,20,.34)); }'

# 放火（客体三分 108/109/110）正典ブロック。色＝108赤/109アンバー/110青（既存踏襲）。
FANG_BLOCK = '''<g transform="translate(265,150)">
<rect x="-215" y="0" width="430" height="150" rx="12" fill="#fbeae8" stroke="#b0635c" stroke-width="2"/>
<rect x="-215" y="0" width="430" height="34" rx="12" fill="#b0635c"/>
<rect x="-215" y="18" width="430" height="16" fill="#b0635c"/>
<text x="0" y="23" text-anchor="middle" fill="#fff" font-weight="700" font-size="16"><tspan font-weight="800" font-size="18">108条</tspan>　現住・現在建造物等</text>
<text x="0" text-anchor="middle" y="60" fill="#6e2f2a" font-weight="600" font-size="14">犯人以外の人が住む・現にいる建造物等</text>
<text x="0" text-anchor="middle" y="84" fill="#7a5a52" font-size="12.5">汽車・電車・艦船・鉱坑も含む。法定刑は最重。</text>
<g transform="translate(-58,100)"><rect class="pbox-chip" x="-54" y="0" width="108" height="24" rx="12" fill="#b0635c"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">抽象的危険犯</text></g>
<g transform="translate(58,100)"><rect class="pbox-chip" x="-54" y="0" width="108" height="24" rx="12" fill="#8f4a44"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">焼損で既遂</text></g>
</g>
<g transform="translate(750,150)">
<rect x="-215" y="0" width="430" height="150" rx="12" fill="#f9f0dc" stroke="#c99a3a" stroke-width="2"/>
<rect x="-215" y="0" width="430" height="34" rx="12" fill="#b58a2e"/>
<rect x="-215" y="18" width="430" height="16" fill="#b58a2e"/>
<text x="0" y="23" text-anchor="middle" fill="#fff" font-weight="700" font-size="16"><tspan font-weight="800" font-size="18">109条</tspan>　非現住・非現在建造物</text>
<text x="0" text-anchor="middle" y="60" fill="#7a5a18" font-weight="600" font-size="14">人が住まず現にもいない建物</text>
<text x="0" text-anchor="middle" y="84" fill="#7a6640" font-size="12.5">所有者によって成立要件が①②に分かれる。</text>
<g transform="translate(-58,100)"><rect class="pbox-chip" x="-54" y="0" width="108" height="24" rx="12" fill="#b58a2e"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">①他人＝既遂</text></g>
<g transform="translate(58,100)"><rect class="pbox-chip" x="-54" y="0" width="108" height="24" rx="12" fill="#9a7328"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">②自己＝危険要</text></g>
</g>
<g transform="translate(1235,150)">
<rect x="-215" y="0" width="430" height="150" rx="12" fill="#e9f0f5" stroke="#5a86a8" stroke-width="2"/>
<rect x="-215" y="0" width="430" height="34" rx="12" fill="#4d7391"/>
<rect x="-215" y="18" width="430" height="16" fill="#4d7391"/>
<text x="0" y="23" text-anchor="middle" fill="#fff" font-weight="700" font-size="16"><tspan font-weight="800" font-size="18">110条</tspan>　建造物等以外の物</text>
<text x="0" text-anchor="middle" y="60" fill="#35566e" font-weight="600" font-size="14">車両など建造物・艦船以外の物</text>
<text x="0" text-anchor="middle" y="84" fill="#4d6472" font-size="12.5">公共の危険の発生が成立要件。</text>
<g transform="translate(-58,100)"><rect class="pbox-chip" x="-54" y="0" width="108" height="24" rx="12" fill="#4d7391"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">具体的危険犯</text></g>
<g transform="translate(58,100)"><rect class="pbox-chip" x="-54" y="0" width="108" height="24" rx="12" fill="#3f6a8c"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">未遂処罰なし</text></g>
</g>
'''

# 文書偽造（有形/無形/行使）正典ブロック＝刑TX371 で確定した改善版そのまま。
BUNSHO_BLOCK = '''<g transform="translate(265,150)">
<rect x="-215" y="0" width="430" height="150" rx="12" fill="#fbeae8" stroke="#b0635c" stroke-width="2"/>
<rect x="-215" y="0" width="430" height="34" rx="12" fill="#b0635c"/>
<rect x="-215" y="18" width="430" height="16" fill="#b0635c"/>
<text x="0" y="23" text-anchor="middle" fill="#fff" font-weight="700" font-size="16"><tspan font-weight="800" font-size="18">有形偽造</tspan>　名義を偽る（155・159）</text>
<text x="0" text-anchor="middle" y="60" fill="#6e2f2a" font-weight="600" font-size="14">名義人と作成者の人格の同一性を偽る＝作成名義の冒用</text>
<text x="0" text-anchor="middle" y="84" fill="#7a5a52" font-size="12.5">原則、公文書も私文書も処罰される。</text>
<g transform="translate(-48,100)"><rect class="pbox-chip" x="-44" y="0" width="88" height="24" rx="12" fill="#b0635c"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">公文書155</text></g>
<g transform="translate(48,100)"><rect class="pbox-chip" x="-44" y="0" width="88" height="24" rx="12" fill="#8f4a44"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">私文書159</text></g>
</g>
<g transform="translate(750,150)">
<rect x="-215" y="0" width="430" height="150" rx="12" fill="#f9f0dc" stroke="#c99a3a" stroke-width="2"/>
<rect x="-215" y="0" width="430" height="34" rx="12" fill="#b58a2e"/>
<rect x="-215" y="18" width="430" height="16" fill="#b58a2e"/>
<text x="0" y="23" text-anchor="middle" fill="#fff" font-weight="700" font-size="16"><tspan font-weight="800" font-size="18">無形偽造</tspan>　内容を偽る（156・160）</text>
<text x="0" text-anchor="middle" y="60" fill="#7a5a18" font-weight="600" font-size="14">作成権限者が真実に反する内容を記載する無形偽造</text>
<text x="0" text-anchor="middle" y="84" fill="#7a6640" font-size="12.5">公文書は広く処罰、私文書は虚偽診断書のみ例外。</text>
<g transform="translate(-53,100)"><rect class="pbox-chip" x="-49" y="0" width="98" height="24" rx="12" fill="#b58a2e"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">公156・157</text></g>
<g transform="translate(53,100)"><rect class="pbox-chip" x="-49" y="0" width="98" height="24" rx="12" fill="#9a7328"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">私診断書160</text></g>
</g>
<g transform="translate(1235,150)">
<rect x="-215" y="0" width="430" height="150" rx="12" fill="#e9f0f5" stroke="#5a86a8" stroke-width="2"/>
<rect x="-215" y="0" width="430" height="34" rx="12" fill="#4d7391"/>
<rect x="-215" y="18" width="430" height="16" fill="#4d7391"/>
<text x="0" y="23" text-anchor="middle" fill="#fff" font-weight="700" font-size="16"><tspan font-weight="800" font-size="18">行使</tspan>　真正として使用（158・161）</text>
<text x="0" text-anchor="middle" y="60" fill="#35566e" font-weight="600" font-size="14">偽造・虚偽文書を真正な物として使用する行為</text>
<text x="0" text-anchor="middle" y="84" fill="#4d6472" font-size="12.5">各偽造罪と牽連犯。通貨・有価証券も同型。</text>
<g transform="translate(-46,100)"><rect class="pbox-chip" x="-42" y="0" width="84" height="24" rx="12" fill="#4d7391"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">公文書158</text></g>
<g transform="translate(46,100)"><rect class="pbox-chip" x="-42" y="0" width="84" height="24" rx="12" fill="#3f6a8c"/><text x="0" y="16.5" text-anchor="middle" fill="#fff" font-weight="700" font-size="12.5">私文書161</text></g>
</g>
'''

REGION_RE = re.compile(r'<g transform="translate\(265,150\)">.*?(?=<path d="M750 300 V336")', re.DOTALL)
# 対象の骨格キー（親箱＝この3ノードを translate(265/750/1235,150) に持つ標準マップだけ差し替える）
STD_START = '<g transform="translate(265,150)">'
STD_CONNECT = '<path d="M750 300 V336"'


def subject_of(html):
    """親箱領域の構造で科目を判定（aria-label でなく実体の箱で見る）。363(五概念)/366(二軸)も
    親箱は標準 108/109/110 なので放火として拾う。360(派生111-115)等は領域に該当語が無く SKIP。"""
    m = REGION_RE.search(html)
    region = m.group(0) if m else ''
    if not region:
        return None
    if '有形偽造' in region and '無形偽造' in region:
        return 'bunsho'
    if '108条' in region and '109条' in region and '110条' in region:
        return 'fang'
    return None


def process(html):
    subj = subject_of(html)
    if subj is None:
        return html, 'SKIP(非標準マップ)'
    if STD_START not in html or STD_CONNECT not in html:
        return html, 'NO-MATCH(標準骨格なし)'
    # 冪等ガードは chip 実体（class="pbox-chip" 要素）で判定する。
    # 生の 'pbox-chip' で見ると、verdict-redesign が 371 の <style> ごとコピーして
    # 漏入する CSS ルール `.tx-sysmap-svg .pbox-chip{…}` に誤マッチし、親箱未標準化でも
    # NOCHANGE で誤スキップする（redesign→pbox の順で昇格する全ファイルで再現するバグ）。
    if 'class="pbox-chip"' in html:
        return html, 'NOCHANGE(既に改善済)'
    block = FANG_BLOCK if subj == 'fang' else BUNSHO_BLOCK
    new, cnt = REGION_RE.subn(block, html, count=1)
    if cnt == 0:
        return html, 'NO-MATCH(領域抽出失敗)'
    # CSS 注入（nb-badge の隣・無ければ）
    if '.tx-sysmap-svg .pbox-chip' not in new:
        anchor = '.tx-sysmap-svg .nb-badge{ filter:drop-shadow(0 2.5px 2.5px rgba(50,25,20,.42)); }'
        if anchor in new:
            new = new.replace(anchor, anchor + '\n' + PBOX_CSS, 1)
        else:
            return new, 'WARN(CSS注入先 nb-badge なし・pbox-chip 未注入)'
    return new, 'OK(%s)' % subj


def main():
    files = sys.argv[1:]
    if not files:
        raise SystemExit("usage: tx-lex-sysmap-pbox.py <file> [file ...]")
    for path in files:
        # 改行コードは元ファイルのもの（CRLF/LF）を保持する＝二台運用での巨大 diff/競合を防ぐ。
        with open(path, "rb") as f:
            raw = f.read()
        crlf = b"\r\n" in raw[:8192]
        html = raw.decode("utf-8").replace("\r\n", "\n")
        new, status = process(html)
        if new != html:
            out = (new.replace("\n", "\r\n") if crlf else new).encode("utf-8")
            with open(path, "wb") as f:
                f.write(out)
        print("[%s] %s" % (status, path.split("/")[-1]))


if __name__ == "__main__":
    main()
