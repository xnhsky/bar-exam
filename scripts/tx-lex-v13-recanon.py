# -*- coding: utf-8 -*-
"""TX _lex v12.2.1 → v13.0.0 LOOP-CARD 決定論移行エンジン（内容保持・冪等）。

gold=刑TX359 のビルド連鎖（scratchpad build_v13b〜v14c）の決定論部を統合し、
問題固有の執筆スロット（SVG体系マップ・横断・正誤マーキング）だけを外から与える。

機械変換（本文保持・全問共通）:
  - choice-section の 統合解説(synthesis)/📌POINT を各 inline card 本文へ昇格
  - #basis 条文判例を各カードの📚BASIS箱へ集約（記述N backlink 配分・honbun表示/noteトグル）
  - 相互リンク往復（ref-stat→bref・戻る）・Lexiaプール再配線（THE GIST/POINT）
  - 旧DIV体系マップ・#mindmap-tree/radial・PART B・cross-column-sec を削除
  - v13差分CSS/JS は gold 359 から抽出して付与（書式バイト一致・AI選定パレットは保持）

問題固有スロット（slots dict・呼び出し側が用意）:
  top_title, panels[5], ox_line, nodes(任意・既定=放火三分), cross(dict), mark(dict)

使い方:
  from importlib import util  # 呼び出し側が slots を作り build(path, slots) を呼ぶ
  python scripts/tx-lex-v13-recanon.py <_lex.html> <slots.json> [--out PATH]
検証は呼び出し側で validate-tx-core.py＋check-tx-lex-engine.py＋check-duplicates.py を通すこと。
"""
from __future__ import annotations
import re, json, sys, argparse, io
from pathlib import Path

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

GOLD = 'outputs/ux/000_TX/001_刑法/刑TX359_lex.html'

# 放火の罪 三分ツリー（客体 108/109/110）の既定ノード。他テーマは slots['nodes'] で差し替え。
DEFAULT_HOUKA_NODES = [
    dict(x=265, code='108条', label='現住・現在建造物',
         lines=['犯人以外の人が住む/現にいる建物。', '故意＝現住性か現在性の一方の認識で', '足りる。焼損で既遂＝抽象的危険犯。'],
         fill='#fbeae8', stroke='#b0635c', headfill='#b0635c'),
    dict(x=750, code='109条', label='非現住建造物',
         lines=['人が住まず現にもいない建物。', '①他人所有＝焼損で既遂。', '②自己所有＝公共の危険が必要（2項）。'],
         fill='#f9f0dc', stroke='#c99a3a', headfill='#b58a2e'),
    dict(x=1235, code='110条', label='建造物等以外の物',
         lines=['車両など建物以外の物。公共の危険の', '発生が成立要件＝具体的危険犯。', '火元が他人物なら延焼罪の起点でない。'],
         fill='#e9f0f5', stroke='#5a86a8', headfill='#4d7391'),
]
# 文書偽造の罪 三分ツリー（有形偽造/無形偽造/行使）の既定ノード。slots['subject']='gizou' で選択。
DEFAULT_GIZOU_NODES = [
    dict(x=265, code='有形偽造', label='名義を偽る（155・159）',
         lines=['名義人と作成者の人格の同一性を', '偽る＝作成名義の冒用。公文書155/', '私文書159。原則、公私とも処罰。'],
         fill='#fbeae8', stroke='#b0635c', headfill='#b0635c'),
    dict(x=750, code='無形偽造', label='内容を偽る（156・160）',
         lines=['作成権限者が真実に反する内容を', '記載。公文書は広く処罰（156/157）、', '私文書は虚偽診断書160のみ例外。'],
         fill='#f9f0dc', stroke='#c99a3a', headfill='#b58a2e'),
    dict(x=1235, code='行使', label='真正として使用（158・161）',
         lines=['偽造・虚偽文書を真正な物として', '使用。偽造罪と牽連犯。通貨148・', '有価証券162の偽造・行使も同型。'],
         fill='#e9f0f5', stroke='#5a86a8', headfill='#4d7391'),
]
SUBJECT_NODES = {'houka': None, 'gizou': DEFAULT_GIZOU_NODES}   # houka は DEFAULT_HOUKA_NODES を使う
COLOR = {'red': '#b0635c', 'amber': '#c99a3a', 'blue': '#5a86a8'}
PANEL_X = [165, 463, 761, 1059, 1357]


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_svg(slots):
    """slots: top_title, top_subtitle, nodes, panels[5]{title,sub,color,stmt}, ox_line, aria."""
    nodes = slots.get('nodes') or SUBJECT_NODES.get(slots.get('subject', 'houka')) or DEFAULT_HOUKA_NODES
    top_title = slots['top_title']            # 例: 放火の罪 ── まず焼いた物の「客体」で条文を選ぶ
    head_sub = slots['head_subtitle']         # 体系マップ head の説明
    aria = slots.get('aria', top_title)
    parts = []
    parts.append('<div class="tx-sysmap" id="tx-sysmap" aria-label="%s">' % esc(aria))
    parts.append('<div class="tx-sysmap-head">')
    parts.append('        <span class="tx-sysmap-kicker">体系マップ</span>')
    parts.append('        <span class="tx-sysmap-title">%s</span>' % esc(head_sub))
    parts.append('      </div>')
    parts.append('<div class="tx-sysmap-figure"><svg class="tree-svg tx-sysmap-svg" viewBox="0 0 1500 720" '
                 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">' % esc(aria))
    # top title bar
    parts.append('<g transform="translate(750,68)"><rect x="-320" y="-26" width="640" height="52" rx="13" fill="#7a3f38"/>'
                 '<text x="0" y="6" text-anchor="middle" fill="#fff" font-weight="800" font-size="21">%s</text></g>' % esc(top_title))
    # connectors top->3 nodes
    parts.append('<path d="M750 94 V128 H265 V150" fill="none" stroke="#94504a" stroke-width="2"/>')
    parts.append('<path d="M750 94 V150" fill="none" stroke="#94504a" stroke-width="2"/>')
    parts.append('<path d="M750 94 V128 H1235 V150" fill="none" stroke="#94504a" stroke-width="2"/>')
    # 3 nodes
    for nd in nodes:
        x = nd['x']
        parts.append('<g transform="translate(%d,150)">' % x)
        parts.append('<rect x="-215" y="0" width="430" height="150" rx="12" fill="%s" stroke="%s" stroke-width="2"/>' % (nd['fill'], nd['stroke']))
        parts.append('<rect x="-215" y="0" width="430" height="34" rx="12" fill="%s"/>' % nd['headfill'])
        parts.append('<rect x="-215" y="18" width="430" height="16" fill="%s"/>' % nd['headfill'])
        parts.append('<text x="-198" y="23" fill="#fff" font-weight="800" font-size="18">%s</text>' % esc(nd['code']))
        parts.append('<text x="-120" y="23" fill="#fff" font-weight="700" font-size="16">%s</text>' % esc(nd['label']))
        ys = [58, 84, 110]
        for k, ln in enumerate(nd['lines'][:3]):
            parts.append('<text x="-198" y="%d" fill="#493730" font-size="14.5">%s</text>' % (ys[k], esc(ln)))
        parts.append('</g>')
    # divider to 5 panels
    parts.append('<path d="M750 300 V336" fill="none" stroke="#94504a" stroke-width="2"/>')
    parts.append('<path d="M165 360 H1357" fill="none" stroke="#94504a" stroke-width="2" opacity="0.7"/>')
    parts.append('<path d="M750 336 V360" fill="none" stroke="#94504a" stroke-width="2"/>')
    parts.append('<text x="750" y="352" text-anchor="middle" fill="#7a3f38" font-weight="800" font-size="15">%s</text>'
                 % esc(slots.get('panels_caption', '本問が突く5局面')))
    for px in PANEL_X:
        parts.append('<path d="M%d 360 V392" fill="none" stroke="#94504a" stroke-width="2" opacity="0.7"/>' % px)
    # 5 panels
    for i, pn in enumerate(slots['panels']):
        x = PANEL_X[i]; col = COLOR.get(pn.get('color', 'red'), '#b0635c'); num = i + 1
        stmt = pn.get('stmt', num)
        parts.append('<a href="#stmt-%s"><g transform="translate(%d,392)">' % (stmt, x))
        parts.append('<rect x="-130" y="0" width="260" height="92" rx="10" fill="#fffdf9" stroke="%s" stroke-width="2"/>' % col)
        parts.append('<rect x="-130" y="0" width="7" height="92" rx="3" fill="%s"/>' % col)
        parts.append('<circle cx="-108" cy="22" r="13" fill="%s"/><text x="-108" y="27" text-anchor="middle" fill="#fff" font-weight="800" font-size="14">%d</text>' % (col, num))
        parts.append('<text x="-86" y="27" fill="#3a2b26" font-weight="800" font-size="15.5">%s</text>' % esc(pn['title']))
        parts.append('<text x="-118" y="58" fill="#5a4a42" font-size="13">%s</text>' % esc(pn['sub']))
        parts.append('<text x="118" y="82" text-anchor="end" fill="%s" font-weight="700" font-size="12">記述%s ↗</text>' % (col, stmt))
        parts.append('</g></a>')
    # result box
    parts.append('<g transform="translate(750,548)"><rect x="-330" y="0" width="660" height="92" rx="14" fill="#f3e6df" stroke="#94504a" stroke-width="1.5"/>'
                 '<text x="0" y="30" text-anchor="middle" fill="#7a3f38" font-weight="800" font-size="17">▼ 本問の帰結（○×）</text>'
                 '<text x="0" y="60" text-anchor="middle" fill="#3a2b26" font-size="15.5">%s</text></g>' % esc(slots['ox_line']))
    parts.append('</svg></div>')
    parts.append(build_cross(slots['cross']))
    parts.append('</div>')
    return '\n'.join(parts)


def build_cross(cr):
    """cr: title, header[3], rows[[3]], kimete, throughline. b タグは原文のまま許可。"""
    h = ['<div class="tx-sysmap-cross">']
    h.append('<div class="tx-cross-tabletitle">%s</div>' % cr['title'])
    h.append('<table>')
    hd = cr['header']
    h.append('<thead><tr><th class="jk2" style="width:20%%;">%s</th><th>%s</th><th>%s</th></tr></thead>' % (hd[0], hd[1], hd[2]))
    h.append('<tbody>')
    for i, row in enumerate(cr['rows']):
        thcls = ' class="jk2"' if i == 0 else ''
        h.append('<tr><th%s>%s</th><td>%s</td><td>%s</td></tr>' % (thcls, row[0], row[1], row[2]))
    h.append('</tbody>')
    h.append('</table>')
    h.append('<p class="col-key"><span class="ck-tag">決め手</span>%s</p>' % cr['kimete'])
    h.append('<p class="col-type"><strong>THROUGH-LINE</strong>%s</p>' % cr['throughline'])
    h.append('</div>')
    return '\n'.join(h)


# 📌POINT の先頭ラベルが v13 禁止の旧5点フロー語（G50/第5-bis）と衝突する場合の改名表
_POINT_RENAME = {'文言': '条文の文言', '趣旨': '制度趣旨', '射程': '及ぶ範囲', '切断点': '分かれ目', '転用': '応用の型'}


def sanitize_point_labels(cp_html):
    """<li>（任意の先頭タグ）文言|趣旨|射程|切断点|転用：… を非衝突ラベルへ改名する。"""
    def rep(m):
        return m.group(1) + _POINT_RENAME[m.group(2)] + m.group(3)
    return re.sub(r'(<li>\s*(?:<[^>]+>\s*)?)(文言|趣旨|射程|切断点|転用)([：:])', rep, cp_html)


def balanced_div(s, start):
    open_end = s.index('>', start) + 1
    depth = 1
    for m in re.finditer(r'<div\b|</div>', s[open_end:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            close_start = open_end + m.start()
            return open_end, close_start, open_end + m.end()
    raise RuntimeError('unbalanced div at %d' % start)


def _apply_gold_parity(h):
    """gold-sync(tx-lex-sysmap-gold-sync.py) の fix() を再利用して縞CSS/SVG寸法/正誤表・
    ストーリー挿入JSを冪等補完する。修正ロジックの二重管理を避けるため import 経由で共有。"""
    import importlib.util
    p = Path(__file__).with_name('tx-lex-sysmap-gold-sync.py')
    spec = importlib.util.spec_from_file_location('tx_sysmap_gold_sync', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    new, changes, _skips = mod.fix(h)
    return new, changes


def build(path, slots, out=None, gold_path=GOLD):
    h = Path(path).read_text(encoding='utf-8')
    gold = Path(gold_path).read_text(encoding='utf-8')
    log = []

    MARK = {int(k): v for k, v in slots['mark'].items()}
    LBL = r'[0-9０-９ア-ンA-Za-z]'   # 記述ラベル1文字（1..5 または ア..オ 等）

    # 0. 記述ラベル（数字/カナ非依存）と各記述の stmt-text を position(1..5) へ正規化
    LABELS = re.findall(r'<article class="tx-inline-card"[^>]*data-stmt="([^"]*)"', h)
    if len(LABELS) < 5:
        raise RuntimeError('inline cards < 5 (%d) in %s' % (len(LABELS), path))
    LABELS = LABELS[:5]
    label2pos = {lab: i + 1 for i, lab in enumerate(LABELS)}
    STMT = {}   # label -> stmt-text innerHTML（syn-orig 再構築用）
    for m in re.finditer(r'<article class="tx-inline-card"[^>]*data-stmt="([^"]*)"[^>]*>(.*?)</article>', h, re.S):
        st = re.search(r'<span class="tx-inline-stmt-text">(.*?)</span>', m.group(2), re.S)
        STMT[m.group(1)] = st.group(1).strip() if st else ''

    # 1. choice-section 抽出（choice-1..5 は数字・位置対応）
    choice = {}
    for n in range(1, 6):
        m = re.search(r'<section class="choice-section \w+" id="choice-%d">(.*?)</section>' % n, h, re.S)
        if not m:
            raise RuntimeError('choice-%d not found in %s' % (n, path))
        seg = m.group(1)
        verdict = re.search(r'(<span class="verdict verdict-\w+">.*?</span>)', seg, re.S).group(1)
        syn = re.search(r'<div class="sub-card synthesis">(.*)</div>\s*(?=<div class="choice-points">)', seg, re.S).group(0)
        cp = re.search(r'<div class="choice-points">.*?</ol>\s*</div>', seg, re.S).group(0)
        cp = sanitize_point_labels(cp)   # 📌POINT の先頭ラベルが旧5点語（趣旨等）と衝突する場合に改名（G50）
        choice[n] = dict(verdict=verdict, syn=syn, cp=cp)
    traps = {}
    for lab, t in re.findall(r'<p class="col-warn"><strong>TRAP \d+（記述(%s+)）</strong>(.*?)</p>' % LBL, h, re.S):
        if lab in label2pos:
            traps[label2pos[lab]] = t.strip()

    # 2. #basis 抽出
    bs_sec = re.search(r'<section class="section" id="basis">(.*?)</section>', h, re.S).group(1)
    parts = re.split(r'(<div class="basis-card )', bs_sec)
    cardmap = {}; order = []
    for i in range(1, len(parts), 2):
        chunk = parts[i] + parts[i + 1]
        m = re.match(r'<div class="basis-card ([^"]*)"[^>]*id="([^"]*)"[^>]*>(.*)', chunk, re.S)
        if not m:
            continue
        cls, cid, rest = m.group(1), m.group(2), m.group(3)
        hdr = re.search(r'<div class="basis-card-header">(.*?)</div>', rest, re.S).group(1)
        bstart = rest.index('<div class="basis-card-body">')
        ins, ine, _ = balanced_div(rest, bstart)
        body = rest[ins:ine]
        body = re.sub(r'<div class="ref-backlinks">.*?</div>\s*', '', body, flags=re.S)
        sp_body = re.split(r'(<div class="note">)', body, 1)
        honbun = sp_body[0].strip()
        note = (''.join(sp_body[1:])).strip() if len(sp_body) > 1 else ''
        refs = sorted(set(l for l in re.findall(r'記述(%s)' % LBL, rest) if l in label2pos))
        cardmap[cid] = dict(cls=cls.strip(), hdr=hdr, honbun=honbun, note=note, refs=refs, is_case=('case-card' in cls))
        order.append(cid)
    by_pos = {n: [] for n in range(1, 6)}   # position -> [basis cid]
    for cid in order:
        for lab in cardmap[cid]['refs']:
            by_pos[label2pos[lab]].append(cid)

    def head_codes(head_html):
        t = re.sub(r'<[^>]+>', '', head_html)
        if any(k in t for k in ('大判', '最判', '最決', '最大判', '⚖')):
            return ['case']
        return re.findall(r'(\d+)条', t)

    def basis_items(n):
        label = LABELS[n - 1]
        out_ = []; codemap = {}
        for cid in by_pos[n]:
            c = cardmap[cid]
            codes = head_codes(c['hdr']) or ['x']
            iid = 'bref-%s-%s' % (label, codes[0])
            for cc in codes:
                codemap.setdefault(cc, iid)
            sumlabel = '射程・本問への帰結を開く' if c['is_case'] else '要件・保護法益・本問への帰結を開く'
            more = ('<details class="tx-basis-more"><summary>＋ %s</summary><div class="tx-basis-note">%s</div></details>'
                    % (sumlabel, c['note'])) if c['note'] else ''
            out_.append(
                '<div id="%s" class="tx-basis-item %s">'
                '<div class="tx-basis-head">%s<a class="tx-basis-back" href="#" title="参照元へ戻る">↩ 戻る</a></div>'
                '<div class="tx-basis-honbun">%s</div>%s</div>'
                % (iid, 'is-case' if c['is_case'] else '', c['hdr'], c['honbun'], more))
        return '\n'.join(out_), codemap

    def rebuild_synorig(syn, label):
        """syn-orig（📜記述原文）を stmt-text の逐語で作り直す（gold v13e と同じ）。
        既存 syn-orig が要約でも逐語に統一され、stmt-text 由来のマーク語句が必ず一致する。"""
        stmt_html = STMT.get(label, '')
        fresh = ('<p class="syn-orig"><span class="syn-tag syn-tag-orig">📜 記述原文</span>%s</p>' % stmt_html)
        syn2 = re.sub(r'<p class="syn-orig">.*?</p>\s*', '', syn, count=1, flags=re.S)
        if re.search(r'<div class="sub-card synthesis">\s*<h4>[^<]*</h4>', syn2, re.S):
            syn2 = re.sub(r'(<div class="sub-card synthesis">\s*<h4>[^<]*</h4>)',
                          lambda mm: mm.group(1) + '\n' + fresh, syn2, count=1, flags=re.S)
        else:
            syn2 = re.sub(r'(<div class="sub-card synthesis">)',
                          lambda mm: mm.group(1) + '\n' + fresh, syn2, count=1, flags=re.S)
        return syn2

    def apply_mark(syn, n):
        if n not in MARK:
            return syn
        verdict, phrase, fix = MARK[n]
        if verdict == 'x':
            rep = '<span class="tx-stmt-x"><span class="tx-stmt-mk">✕</span>%s</span>' % phrase
            if fix:
                rep += '<span class="tx-stmt-fix">→ %s</span>' % fix
        else:
            rep = '<span class="tx-stmt-o"><span class="tx-stmt-mk is-ok">✓</span>%s</span>' % phrase

        def repl_orig(mm):
            body = mm.group(2)
            if phrase not in body:
                log.append('WARN: mark phrase not found in 記述%d: %r' % (n, phrase))
                return mm.group(0)
            return mm.group(1) + body.replace(phrase, rep, 1) + mm.group(3)
        return re.sub(r'(<p class="syn-orig"><span class="syn-tag syn-tag-orig">📜 記述原文</span>)(.*?)(</p>)',
                      repl_orig, syn, count=1, flags=re.S)

    def rewire_refstat(html, codemap):
        def ref_repl(rm):
            opentag, inner = rm.group(1), rm.group(2)
            opentag = re.sub(r'\s+href="[^"]*"', '', opentag)
            num = re.search(r'(\d+)条', re.sub(r'<[^>]+>', '', inner))
            iid = codemap.get(num.group(1)) if num else None
            if iid:
                return opentag[:-1] + ' href="#%s">' % iid + inner + '</a>'
            return opentag + inner + '</a>'
        return re.sub(r'(<a class="ref-stat"[^>]*>)(.*?)(</a>)', ref_repl, html, flags=re.S)

    def build_inner(n):
        c = choice[n]
        label = LABELS[n - 1]
        syn = rebuild_synorig(c['syn'], label)   # syn-orig を stmt-text 逐語に統一（Bug2対策）
        syn = apply_mark(syn, n)
        items, codemap = basis_items(n)
        basis = ('<div class="sub-card basis-link"><span class="tx-v13-basis-label">📚 BASIS</span>'
                 '<div class="tx-basis-items">%s</div></div>' % items)
        trap = ('<div class="tx-v13-trap"><span class="tx-v13-trap-label">⚠️ 間違いやすいポイント</span>'
                '<span class="tx-v13-trap-body">%s</span></div>' % traps[n]) if n in traps else ''
        cross_sub = ''
        cx = slots.get('subject_cross', {})
        if str(n) in cx:
            cross_sub = ('<div class="tx-v13-cross"><span class="tx-v13-cross-label">🔗 他科目横断</span>'
                         '<span class="tx-v13-cross-body">%s</span></div>' % cx[str(n)])
        inner = ('\n<div class="tx-v13-verdict">%s</div>\n%s\n%s\n%s\n%s\n%s\n'
                 % (c['verdict'], syn, c['cp'], basis, trap, cross_sub))
        return rewire_refstat(inner, codemap)

    # 3. カード explain 差し替え（ラベル→position）
    def replace_cards(html):
        out_ = []; pos = 0
        for m in re.finditer(r'<article class="tx-inline-card"[^>]*data-stmt="([^"]*)"[^>]*>', html):
            lab = m.group(1)
            if lab not in label2pos:
                continue
            n = label2pos[lab]
            art_start = m.start(); art_end = html.index('</article>', art_start)
            ex = re.search(r'<div class="tx-inline-explain"[^>]*>', html[art_start:art_end])
            if not ex:
                continue
            ex_open_abs = art_start + ex.start()
            ins, ine, after = balanced_div(html, ex_open_abs)
            out_.append(html[pos:ins]); out_.append(build_inner(n)); out_.append(html[ine:after])
            pos = after
        out_.append(html[pos:])
        return ''.join(out_)
    h = replace_cards(h)
    log.append('cards replaced; v13-verdict=%d href-bref=%d' % (h.count('tx-v13-verdict'), h.count('href="#bref-')))

    # 4. 旧DIV体系マップ → SVG（無ければ フォールバック挿入）
    # panels の stmt を実ラベル（ア..オ 等）へ正規化＝#stmt-{label} アンカーと一致させる
    for i, pn in enumerate(slots['panels'][:5]):
        pn['stmt'] = LABELS[i]
    svg_html = build_svg(slots)
    if '<div class="tx-sysmap"' in h:
        i = h.index('<div class="tx-sysmap"')
        _, _, after = balanced_div(h, i)
        h = h[:i] + svg_html + h[after:]
        log.append('DIV sysmap -> SVG')
    else:
        # DIV体系マップ非所持問：最初の inline カード直前（part-a 直下の full-width sibling 位置）へ挿入。
        # 体系マップ縦順（正誤表→体系マップ→肢カード）を保ちつつ、狭い問題文コンテナ内に紛れ込ませない。
        m2 = re.search(r'\s*<div class="problem-text">\s*<span class="choice-num-inline">\s*1\s*</span>', h)
        if not m2:
            m2 = re.search(r'<article class="tx-inline-card"', h)
        anchor = m2.start()
        h = h[:anchor] + '\n' + svg_html + '\n' + h[anchor:]
        log.append('SVG inserted before first inline card (no DIV sysmap / fallback)')

    # 5. #mindmap-tree / #mindmap-radial 削除・目次リンク無効化
    for sid in ('mindmap-tree', 'mindmap-radial'):
        h = re.sub(r'<section class="section" id="%s">.*?</section>\s*' % sid, '', h, flags=re.S)
    h = re.sub(r'<a href="#(?:mindmap-tree|mindmap-radial|cross-column-sec)">[^<]*</a>', '', h)

    # 6. PART B / PART B+ / cross-column-sec 削除
    h = re.sub(r'<section class="choice-section \w+" id="choice-\d+">.*?</section>\s*', '', h, flags=re.S)
    h = re.sub(r'<div class="part-title partb-source-title"[^>]*>.*?</div>\s*', '', h, flags=re.S)
    h = re.sub(r'<details class="partb-details[^"]*"[^>]*>.*?</details>\s*', '', h, flags=re.S)
    h = re.sub(r'<div class="part-title">PART B\+.*?</div>\s*', '', h, flags=re.S)
    h = re.sub(r'<section class="section" id="cross-column-sec">.*?</section>\s*', '', h, flags=re.S)

    # 7. #basis スリム化
    bsec = re.search(r'<section class="section" id="basis">.*?</section>', h, re.S).group(0)
    has_lawnote = 'tx-current-law-note' in bsec
    def slim_basis(m):
        sec = m.group(0)
        head = re.match(r'(<section class="section" id="basis">.*?<div class="tx-current-law-note">.*?</div>\s*</div>)', sec, re.S)
        tail = ('\n<p class="basis-moved-note">各条文・判例は上の各記述カードの「📚 BASIS」内に配置しています。</p>\n'
                '<div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>\n</section>')
        return (head.group(1) if head else sec) + tail
    if has_lawnote:
        h = re.sub(r'<section class="section" id="basis">.*?</section>', slim_basis, h, count=1, flags=re.S)
    else:
        h = re.sub(r'<section class="section" id="basis">.*?</section>',
                   '<section class="section" id="basis">\n<p class="basis-moved-note">各条文・判例は上の各記述カードの「📚 BASIS」内に配置しています。</p>\n<div class="back-to-top"><a href="#top">↑ ページ先頭へ</a></div>\n</section>',
                   h, count=1, flags=re.S)

    # dangling href 無効化
    h = re.sub(r'(<a\b[^>]*?)\shref="#(?:law-|ref-law-|case-|basis)[^"]*"([^>]*>)', r'\1\2', h)

    # 7-bis. 物語解説ラベル段落の本文を .fa-narrative-body で包む（v12.2.1 表示LOCK・G45／冪等）
    def wrap_narr(m):
        inner = m.group(2)
        if 'fa-narrative-body' in inner:
            return m.group(0)
        return m.group(1) + '<span class="fa-narrative-body">' + inner + '</span></p>'
    h = re.sub(r'(<p[^>]*\bdata-fa-label="[^"]*"[^>]*>)(.*?)</p>', wrap_narr, h, flags=re.S)

    # 7-ter. solve-nav「○×型・両モード」変種の未置換テンプレ __NUMS__/__KEYS__ を実値へ（pageerror防止・冪等）
    if '__NUMS__' in h or '__KEYS__' in h:
        nums = '[' + ','.join('"%d"' % i for i in range(1, len(LABELS) + 1)) + ']'
        keys = '[' + ','.join('"%s"' % l for l in LABELS) + ']'
        h = h.replace('__NUMS__', nums).replace('__KEYS__', keys)

    # 8. Lexia プール再配線
    def plain(s):
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()
    def sanitize_plain_label(t):
        m = re.match(r'^(文言|趣旨|射程|切断点|転用)([：:])(.*)$', t, re.S)
        return (_POINT_RENAME[m.group(1)] + m.group(2) + m.group(3)) if m else t
    pool = {}
    for n in range(1, 6):
        sl = re.search(r'<p class="syn-lead">(.*?)</p>', choice[n]['syn'], re.S)
        gist = plain(re.sub(r'<span class="syn-tag">.*?</span>', '', sl.group(1), count=1, flags=re.S)) if sl else ''
        pts = [sanitize_plain_label(plain(x)) for x in re.findall(r'<li>(.*?)</li>', choice[n]['cp'], re.S)]
        pool[n] = (gist, pts)

    def rewire_pool(html):
        # ox-row 開始位置で区切り、各行の ox-pool-explain 内を THE GIST/POINT へ置換（入れ子に強い）
        starts = [m.start() for m in re.finditer(r'<div class="ox-row"', html)]
        if not starts:
            return html
        bounds = starts + [len(html)]
        out_ = []; prev = 0
        for i in range(len(starts)):
            s, e = bounds[i], bounds[i + 1]
            seg = html[s:e]
            ds = re.search(r'data-stmt="([^"]*)"', seg)
            if ds and ds.group(1) in label2pos:
                gist, pts = pool[label2pos[ds.group(1)]]
                gist_html = '<p class="ox-pool-gist">%s</p>' % gist
                pts_html = '<ul class="ox-pool-points">' + ''.join('<li>%s</li>' % p for p in pts) + '</ul>'
                seg = re.sub(r'(<div class="ox-pool-explain"[^>]*>).*?(</div>)',
                             lambda mm: mm.group(1) + gist_html + pts_html + mm.group(2), seg, count=1, flags=re.S)
            out_.append(html[prev:s]); out_.append(seg); prev = e
        out_.append(html[prev:])
        return ''.join(out_)
    h = rewire_pool(h)
    stem = Path(path).stem
    h = re.sub(r'data-source="[^"]*"', 'data-source="%s-v13-gist-point"' % stem, h, count=1)

    # 9. gold から v13 差分 CSS/JS 移植
    c0 = gold.index('/* === v13b:'); c1 = gold.index('</style>', c0)
    css_delta = '\n' + gold[c0:c1].rstrip() + '\n'
    # 体系マップのベースCSS（.tx-sysmap 一式＋表示フック）が無い問（旧DIV体系マップ非所持・366型）へ注入
    gold_style = gold[gold.find('<style'):gold.rfind('</style>')]
    h_style = h[h.find('<style'):h.rfind('</style>')]
    if h_style.count('.tx-sysmap') < 5:
        rules = re.findall(r'[^{}]*tx-sysmap[^{}]*\{[^{}]*\}', gold_style)
        css_delta += '\n/* tx-sysmap base CSS (injected: file had no DIV sysmap) */\n' + '\n'.join(rules) + '\n'
        log.append('injected tx-sysmap base CSS (%d rules)' % len(rules))
    si = h.rfind('</style>'); h = h[:si] + css_delta + h[si:]
    jm = re.search(r'/\* v14b: カード内相互リンク.*?\}\)\(\);', gold, re.S)
    js_block = '\n' + jm.group(0) + '\n'
    eng = re.search(r'(getInlineAnswerTablePanel|moveStatementVerdictTableToTop)', h)
    close = h.index('</' + 'script>', eng.start() if eng else 0)
    h = h[:close] + js_block + h[close:]

    # --- gold-parity 最終正規化（抽出漏れの恒久封じ・単一の真実 = tx-lex-sysmap-gold-sync）---
    # v13差分CSS抽出（/* === v13b: */ 起点）は縞背景CSS・体系マップSVG寸法規則を範囲外に取りこぼす。
    # また移行元(v12)由来の getInlineAnswerTablePanel/StoryPanel は正誤表を冒頭へ挿さない旧JS。
    # ここで gold-sync の fix() を冪等適用し、どの入力から移行しても3点が必ず揃うようにする。
    h, _gp_changes = _apply_gold_parity(h)
    if _gp_changes:
        log.append('gold-parity normalize: ' + ', '.join(_gp_changes))

    outp = out or path
    Path(outp).write_text(h, encoding='utf-8')
    log.append('WROTE %s | scripts=%d styles=%d v13-verdict=%d basis-items=%d bref=%d marks=%d svg=%s mindmap=%d'
               % (outp, h.count('<script'), h.count('<style'), h.count('tx-v13-verdict'),
                  h.count('class="tx-basis-item '), h.count('id="bref-'),
                  h.count('tx-stmt-x"') + h.count('tx-stmt-o"'), 'tree-svg' in h, h.count('id="mindmap-')))
    return '\n'.join(log)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('slots')
    ap.add_argument('--out', default=None)
    ap.add_argument('--gold', default=GOLD)
    a = ap.parse_args()
    slots = json.loads(Path(a.slots).read_text(encoding='utf-8'))
    print(build(a.html, slots, out=a.out, gold_path=a.gold))


if __name__ == '__main__':
    main()
