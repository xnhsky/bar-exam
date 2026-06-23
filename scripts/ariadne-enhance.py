#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ariadne-enhance.py ― ARIADNE 解法ナビへ 3 つの体裁強化を冪等付与する。

  ① 条文プロファイルの「N項」をバッジ化＋項どうしを点線で区切る（深層部 statute-card）
  ③ マストヘッドに目次ジャンプ（TOC チップ）を新設し各セクションへアンカー
  ④ 各セクション区切り＋深掘り層の前に「▲ 先頭へ戻る」ボタン（#top）

  ② 本文インライン相互リンクは別スクリプト scripts/ariadne-autolink.py で付与する
     （本スクリプト → autolink の順で流す）。

使い方:  python scripts/ariadne-enhance.py <file.html> [--dry-run]
冪等:    既に付与済み（.toc-nav / stat-para）なら該当処理をスキップ。
"""
import re, sys, argparse

ICON_MAP = {
    '📄': ('sec-prob', '📄', '問題文'),
    '🧭': ('sec-nav',  '🧭', '解法ナビ'),
    '🎓': ('sec-build', '🎓', '作法'),
    '🏁': ('sec-goal', '🏁', '骨子'),
    '🧠': ('sec-recall', '🧠', '想起'),
    '📋': ('sec-check', '📋', '照合'),
}
TO_TOP = '<div class="to-top"><a href="#top">▲ 先頭へ戻る</a></div>\n  '

CSS_BUNDLE = """
/* ==== ARIADNE-ENHANCE v1 （①項バッジ・点線／③目次／④先頭へ戻る） ==== */
/* ① 条文の項をバッジ化＋項どうしを点線で区切る */
.athena-graft blockquote.statute .stat-para{display:flex; align-items:baseline; gap:10px; margin:0; padding:11px 0; text-indent:0; border-top:1px dashed #bcd8d6}
.athena-graft blockquote.statute .stat-para:first-child{padding-top:2px; border-top:none}
.athena-graft blockquote.statute .stat-para:last-child{padding-bottom:2px}
.athena-graft blockquote.statute .stat-pn{flex:0 0 auto; align-self:flex-start; margin-top:.2em; font-family:"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif; font-size:.72rem; font-weight:700; letter-spacing:.04em; text-indent:0; color:#fff; background:linear-gradient(135deg,#7fb1ad,#4E8597); border-radius:999px; padding:2px 11px; line-height:1.6; white-space:nowrap; box-shadow:0 1px 2px rgba(46,73,83,.18)}
.athena-graft blockquote.statute .stat-pt{flex:1 1 auto; min-width:0; text-indent:0}
/* ② 本文インライン相互リンク（語そのものをリンク） */
a.xref{color:#1a2540; font-weight:700; text-decoration:none; background:rgba(20,40,90,.05); border-bottom:1.5px solid rgba(20,40,90,.32); border-radius:2px; padding:0 1.5px; transition:background .12s,color .12s}
a.xref:hover{color:#fff; background:#3a4a78; border-bottom-color:#3a4a78}
.step a.xref,.quiz-answer a.xref,.box a.xref{font-weight:700}
/* ③ ヘッダー目次ジャンプ（TOC） */
.toc-nav{display:flex; flex-wrap:wrap; gap:7px; padding:2px 0 18px}
.toc-nav a{display:inline-flex; align-items:center; font-family:var(--f-soft); font-size:.76rem; font-weight:700; letter-spacing:.02em; text-decoration:none; color:#fff; background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.30); border-radius:999px; padding:4px 13px; transition:background .12s, transform .1s}
.toc-nav a:hover{background:rgba(255,255,255,.32); transform:translateY(-1px)}
.toc-nav a .i{margin-right:5px; font-size:.96em}
/* ④ セクション区切りの「先頭へ戻る」 */
.to-top{display:flex; justify-content:flex-end; margin:30px 0 -16px}
.to-top a{display:inline-flex; align-items:center; gap:5px; font-family:var(--f-soft); font-size:.73rem; font-weight:700; text-decoration:none; color:var(--li-deep); background:var(--card); border:1px solid var(--li-line); border-radius:999px; padding:3px 13px; box-shadow:0 1px 3px rgba(80,60,80,.08); transition:background .12s, transform .1s}
.to-top a:hover{background:var(--li-soft); transform:translateY(-1px)}
@media print{ .toc-nav,.to-top{display:none} }
"""

# 深層部カード→解法ナビへ戻る（相互リンクの帰り道・控えめなテキストリンク／autolink が本文へ挿入）
CARD_RETURN_CSS = """
/* 深層部カード→解法ナビへ戻る（相互リンクの帰り道） */
.athena-graft .card-return{margin-top:13px; padding-top:9px; border-top:1px dashed #D6C9DC; text-align:right}
.athena-graft .card-return a{display:inline-flex; align-items:center; gap:4px; font-family:"Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif; font-size:.74rem; font-weight:700; color:#4E8597; text-decoration:none; border-bottom:1.5px dashed #9fc3c0; padding:1px 3px; border-radius:3px; transition:background .12s,color .12s}
.athena-graft .card-return a:hover{color:#fff; background:#4E8597; border-bottom-color:#4E8597}
@media print{ .card-return{display:none} }
"""

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)

# ---- ① 条文 項バッジ＋点線 ----
def _transform_bq(bq, hdr):
    m = re.search(r'<blockquote class="statute">(.*?)</blockquote>', bq, re.S)
    inner = m.group(1)
    pm = re.search(r'<p[^>]*>(.*?)</p>', inner, re.S)
    body = pm.group(1) if pm else inner
    segs = [s for s in re.split(r'<br\s*/?>', body)]
    items = []
    allmarked = True
    for s in segs:
        mm = re.match(r'\s*(\d+項)　(.*)$', s.strip(), re.S)
        if mm:
            items.append((mm.group(1), mm.group(2).strip()))
        else:
            allmarked = False
            break
    if allmarked and items:
        ps = ''.join(
            f'<p class="stat-para"><span class="stat-pn">{k}</span><span class="stat-pt">{v}</span></p>'
            for k, v in items)
    else:
        nonempty = [s for s in segs if s.strip()]
        hjo = re.search(r'(\d+項)', hdr)
        if hjo and len(nonempty) == 1:
            ps = (f'<p class="stat-para"><span class="stat-pn">{hjo.group(1)}</span>'
                  f'<span class="stat-pt">{body.strip()}</span></p>')
        else:
            return bq   # 項の無い条文はそのまま
    return '<blockquote class="statute">' + ps + '</blockquote>'

def transform_statutes(html):
    pat = re.compile(
        r'(<div class="basis-card statute-card"[^>]*>\s*<div class="basis-card-header">(?P<hdr>.*?)</div>)'
        r'(?P<rest>.*?)(?P<bq><blockquote class="statute">.*?</blockquote>)', re.S)
    def repl(m):
        if 'stat-para' in m.group('bq'):
            return m.group(0)
        newbq = _transform_bq(m.group('bq'), strip_tags(m.group('hdr')))
        return m.group(1) + m.group('rest') + newbq
    return pat.sub(repl, html)

# ---- ③④ 目次＋先頭へ戻る ----
def add_toc_and_totop(html):
    if 'class="toc-nav"' in html:
        return html
    secs = []
    def assign(m):
        attrs = m.group('attrs'); ico = m.group('ico').strip(); full = m.group(0)
        entry = ICON_MAP.get(ico)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
        else:
            sid = entry[0] if entry else f'sec-{len(secs)+1}'
            full = full.replace('<div class="sec-h"', f'<div class="sec-h" id="{sid}"', 1)
        secs.append((sid, ico, entry))
        return full
    html = re.sub(r'<div class="sec-h"(?P<attrs>[^>]*)>.*?<span class="ico">(?P<ico>[^<]+)</span>',
                  assign, html, flags=re.S)

    # ④ 2 番目以降の sec-h と deep-dive の前に to-top
    for sid, _ico, _e in secs[1:]:
        html = html.replace(f'<div class="sec-h" id="{sid}">',
                            TO_TOP + f'<div class="sec-h" id="{sid}">', 1)
    if '<!-- 深掘り -->' in html:
        html = html.replace('<!-- 深掘り -->', TO_TOP + '<!-- 深掘り -->', 1)
    elif '<details id="deep-dive">' in html:
        html = html.replace('<details id="deep-dive">', TO_TOP + '<details id="deep-dive">', 1)

    # ③ TOC チップを masthead に挿入
    chips = ''
    for sid, _ico, entry in secs:
        if entry:
            chips += f'      <a href="#{sid}"><span class="i">{entry[1]}</span>{entry[2]}</a>\n'
    if '<details id="deep-dive">' in html:
        chips += '      <a href="#deep-dive"><span class="i">📚</span>深掘り</a>\n'
    toc = '    <nav class="toc-nav" aria-label="目次">\n' + chips + '    </nav>\n    '
    html = html.replace('<header class="masthead">', '<header class="masthead" id="top">', 1)
    html = re.sub(r'(\s*)<div class="rainbow"></div>', '\n    ' + toc + '<div class="rainbow"></div>',
                  html, count=1)
    return html

def assign_step_ids(html):
    """解法ナビの各 .step に id="step-N"（出現順）を冪等付与（autolink の帰り道リンク先）。"""
    cnt = [0]
    def repl(m):
        cnt[0] += 1
        tag = m.group(0)
        if 'id=' in tag:
            return tag   # 既存 id は温存（番号は出現順なので整合）
        return tag.replace('<div class="step"', f'<div class="step" id="step-{cnt[0]}"', 1)
    return re.sub(r'<div class="step"[^>]*>', repl, html)

def inject_css(html):
    add = ''
    if '.toc-nav{' not in html and 'ARIADNE-ENHANCE v1' not in html:
        add += CSS_BUNDLE
    if '.card-return{' not in html:
        add += CARD_RETURN_CSS
    if add:
        html = html.replace('</style>', add + '</style>', 1)
    return html

def enhance(html):
    html = transform_statutes(html)
    html = assign_step_ids(html)
    html = add_toc_and_totop(html)
    html = inject_css(html)
    return html

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    with open(a.file, encoding='utf-8') as f:
        html = f.read()
    out = enhance(html)
    if a.dry_run:
        sys.stderr.write(f'(dry-run) changed={out != html}\n'); return
    with open(a.file, 'w', encoding='utf-8') as f:
        f.write(out)
    sys.stderr.write(f'enhanced: {a.file}\n')

if __name__ == '__main__':
    main()
