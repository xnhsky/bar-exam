#!/usr/bin/env python3
"""ARIADNE 模範答案 p.role のぶら下がりインデント（2026-06-23）。
文頭番号（1 / (2) / 2(1) 等・全角スペース区切り）の折返し2行目が番号下へ回り込む問題を、
番号と本文を <span class="pn">/<span class="pb"> に分離し p.role を display:flex 化して
auto 幅ハンギングで解決（番号幅が可変でも本文開始位置が各行で揃う）。原稿用紙風の罫線(::after)・
役割バッジ(::before)は absolute なので flex 非干渉。冪等・LF保存。"""
import glob, re, sys

MARK = '/* === ROLE-HANGING v1 === */'
CSS = MARK + '\n' + """\
.model-answer p.role{display:flex; align-items:flex-start; column-gap:.45em; text-indent:0 !important;}
.model-answer p.role > .pn{flex:0 0 auto; font-weight:800; color:var(--cd); line-height:var(--lh); white-space:nowrap}
.model-answer p.role > .pb{flex:1 1 auto; min-width:0; text-indent:0}
.model-answer p.role > .pb > b:first-child,.model-answer p.role > .pn > b:first-child{color:var(--cd); font-weight:800}
"""

MARK_OK = re.compile(r'^(?:第)?[\d(（][\d()（）ア-ンｱ-ﾝa-zA-Z①-⑳・.\-]*$')
ROLE_RE = re.compile(r'(<p class="role[^"]*">)(.*?)(</p>)', re.S)

def strip_tags(x): return re.sub(r'<[^>]+>', '', x)

def wrap(m):
    open_tag, content, close = m.group(1), m.group(2), m.group(3)
    if '<span class="pn"' in content or '<span class="pb"' in content:
        return m.group(0)  # already wrapped
    if '　' in content:
        pre, rest = content.split('　', 1)
        pre_txt = strip_tags(pre).strip()
        if pre_txt and len(pre_txt) <= 6 and MARK_OK.match(pre_txt):
            return f'{open_tag}<span class="pn">{pre.strip()}</span><span class="pb">{rest}</span>{close}'
    # no marker → wrap whole as body
    return f'{open_tag}<span class="pb">{content}</span>{close}'

def process(path):
    with open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    orig = s
    if MARK not in s:
        idx = s.rfind('</style>')
        if idx != -1:
            s = s[:idx] + CSS + s[idx:]
    s = ROLE_RE.sub(wrap, s)
    if s != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
        return True
    return False

def main():
    targets = sys.argv[1:] or (sorted(glob.glob('outputs/ux/000_ARIADNE/001_刑法/*_ARIADNE.html')) + ['canonical/ARIADNE.html'])
    n = sum(process(p) for p in targets)
    print(f"[role-hanging] {n}/{len(targets)} updated")

if __name__ == '__main__':
    main()
