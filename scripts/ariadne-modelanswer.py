#!/usr/bin/env python3
"""ARIADNE 模範答案フォーマット統一（2026-06-23・ユーザー指示3要件）：
(要件1) 番号なし通常段落＝text-indent:1em（1字下げ）
(要件2) 階層インデント＝大項目「N」=L0／中項目「(N)」=L1／小項目「ア」=L2 を margin-left で段階字下げ
(要件3) 番号段落のぶら下がり＝番号(.pn)と本文(.pb)を分離し flex で2行目以降を頭揃え
新型(p.role・既に.pn/.pb)と旧型(プレーン<p>＋<b>N</b>　)の両構造を統一処理。.ma-h見出し・太字小見出し
(<b>…</b>のみ)・「以上」行は不変。明示クラス(mahang/lvl1/lvl2/manorm)＝:has不使用でLexia webview安全。冪等・LF保存。"""
import glob, re, sys

MARK = '/* === MODELANSWER-FMT v1 === */'
CSS = MARK + '\n' + """\
.model-answer p.role{display:flex; align-items:flex-start; column-gap:.45em; text-indent:0}
.model-answer p.role > .pn{flex:0 0 auto; font-weight:800; color:var(--cd); line-height:var(--lh); white-space:nowrap}
.model-answer p.role > .pb{flex:1 1 auto; min-width:0; text-indent:0}
.model-answer p.mahang{display:flex; align-items:flex-start; column-gap:.45em; text-indent:0}
.model-answer p.mahang > .pn{flex:0 0 auto; font-weight:800; white-space:nowrap}
.model-answer p.mahang > .pb{flex:1 1 auto; min-width:0; text-indent:0}
.model-answer p.lvl1{margin-left:1.6em}
.model-answer p.lvl2{margin-left:3.1em}
.model-answer p.manorm{text-indent:1em}
.model-answer p.manorm > .pb{text-indent:1em}
"""

MA_BLOCK = re.compile(r'(<div class="model-answer">)(.*?)(</div>)', re.S)
P_RE = re.compile(r'<p\b([^>]*)>(.*?)</p>', re.S)
PN_PB = re.compile(r'^\s*<span class="pn">(.*?)</span><span class="pb">(.*?)</span>\s*$', re.S)
PB_ONLY = re.compile(r'^\s*<span class="pb">(.*?)</span>\s*$', re.S)
BOLD_ONLY = re.compile(r'^\s*<b>.*</b>\s*$', re.S)

def strip_tags(x): return re.sub(r'<[^>]+>', '', x)

def classify(mk):
    if re.match(r'^[(（]', mk): return 1
    if re.match(r'^[ア-ンｱ-ﾝ]', mk) and len(mk) <= 3: return 2
    if re.match(r'^第?[0-9０-９]', mk): return 0
    return None

def try_split(core):
    if '　' not in core: return None, None, None
    pre, rest = core.split('　', 1)
    pt = strip_tags(pre).strip()
    if pt and len(pt) <= 6 and classify(pt) is not None and not re.search(r'[ぁ-ん]', pt):
        return pre.strip(), rest, pt
    return None, None, None

def set_classes(attrs, add, drop=()):
    m = re.search(r'class="([^"]*)"', attrs)
    cur = m.group(1).split() if m else []
    cur = [c for c in cur if c not in drop and c not in add] + list(add)
    cls = ' '.join(cur)
    if m:
        return attrs[:m.start()] + f'class="{cls}"' + attrs[m.end():]
    return attrs + f' class="{cls}"'

def proc_p(m):
    attrs, inner = m.group(1), m.group(2)
    cls = re.search(r'class="([^"]*)"', attrs)
    classlist = cls.group(1).split() if cls else []
    if 'ma-h' in classlist: return m.group(0)
    if 'text-align:right' in attrs: return m.group(0)          # 「以上」行
    if BOLD_ONLY.match(inner): return m.group(0)               # 太字小見出し
    is_role = 'role' in classlist
    # determine marker + body
    pn = PN_PB.match(inner)
    if pn:
        marker_html, body_html, mk = pn.group(1), pn.group(2), strip_tags(pn.group(1)).strip()
    else:
        pb = PB_ONLY.match(inner)
        core = pb.group(1) if pb else inner
        marker_html, body_html, mk = try_split(core)
    # rebuild
    attrs2 = set_classes(attrs, [], drop=['mahang','lvl0','lvl1','lvl2','manorm'])  # reset our classes (idempotent)
    if mk and classify(mk) is not None:
        lv = classify(mk)
        add = ([] if is_role else ['mahang']) + ([f'lvl{lv}'] if lv else [])
        attrs2 = set_classes(attrs2, add)
        return f'<p{attrs2}><span class="pn">{marker_html}</span><span class="pb">{body_html}</span></p>'
    else:
        # normal paragraph
        attrs2 = set_classes(attrs2, ['manorm'])
        if is_role:
            pb = PB_ONLY.match(inner); body = pb.group(1) if pb else inner
            return f'<p{attrs2}><span class="pb">{body}</span></p>'
        return f'<p{attrs2}>{inner}</p>'

def proc_block(m):
    return m.group(1) + P_RE.sub(proc_p, m.group(2)) + m.group(3)

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    orig = s
    s = MA_BLOCK.sub(proc_block, s)
    if MARK not in s:
        i = s.rfind('</style>')
        if i != -1: s = s[:i] + CSS + s[i:]
    if s != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
        return True
    return False

def main():
    targets = sys.argv[1:] or (sorted(glob.glob('outputs/ux/001_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html'])
    n = sum(process(p) for p in targets)
    print(f"[modelanswer] {n}/{len(targets)} updated")

if __name__ == '__main__':
    main()
