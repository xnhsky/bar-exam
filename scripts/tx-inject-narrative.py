#!/usr/bin/env python3
"""tx-inject-narrative.py ── 標準 TX _lex（Type B＝独立5択・記述組合せ）の .final-answer 冒頭に
物語解説（読み物）を注入する汎用器。Type A は tx-build-typeA.py が担うが、議論形式でない通常問題は
JSON データを持たないため、本器が narrative.json を受け取って .fa-narrative を挿す。

  python scripts/tx-inject-narrative.py <CODE> <narrative.json>

narrative.json = {"title": "...", "paras": ["段落1","段落2",...], "intent": {"core":..,"angle":..,"aim":..}?}
  - intent は任意。あれば .fa-intent を物語の上に置く。
冪等：既存の .fa-narrative / .fa-intent は除去してから挿し直す。CSS も無ければ注入。
"""
import sys, os, re, json, glob

NARR_CSS = '''/* Type A/B 物語解説（読み物）：問題の流れを一連の文章でコア／テーゼ中心に読ませる */
.fa-narrative{ margin:0 0 18px; padding:16px 18px; border-radius:12px;
  background:var(--light,#fafafa); border:1px solid var(--soft,#e8e8e8); border-left:5px solid var(--accent);
  counter-reset:tx-fa; }
.fa-narrative-title{ margin:0 0 16px; padding-bottom:9px; border-bottom:2px dotted rgba(120,90,40,.32);
  font-weight:800; font-size:1.02em; color:var(--accent); letter-spacing:.02em; }
.fa-narrative p{ margin:0 0 .7em; line-height:1.95; font-size:1.0em; text-align:justify; }
.fa-narrative > p:not(.fa-narrative-title){ position:relative; counter-increment:tx-fa; margin:20px 0 0 0;
  padding:16px 15px 14px 16px; border:1px solid rgba(120,90,40,.16); border-left:3px solid rgba(193,124,42,.62);
  border-radius:12px; box-shadow:0 1px 3px rgba(80,60,20,.06), inset 0 1px 0 rgba(255,255,255,.55); }
.fa-narrative > p:not(.fa-narrative-title):nth-of-type(even){ background:rgba(255,255,255,.66); }
.fa-narrative > p:not(.fa-narrative-title):nth-of-type(odd){ background:rgba(201,140,58,.085); }
.fa-narrative > p:not(.fa-narrative-title):not([data-fa-label])::before{ content:counter(tx-fa); position:absolute; top:-11px; left:14px;
  display:inline-flex; align-items:center; justify-content:center; width:23px; height:23px; text-indent:0;
  color:#fff; background:linear-gradient(180deg,#c8843a,#a8692a); border:1.5px solid rgba(255,255,255,.72);
  border-radius:999px; box-shadow:0 1px 3px rgba(120,80,20,.35); font-size:12px; font-weight:800; line-height:1; }
.fa-narrative > p[data-fa-label]::before{ content:attr(data-fa-label); position:absolute; top:-13px; left:13px;
  display:inline-flex; align-items:center; justify-content:center; box-sizing:border-box; padding:4px 12px 5px; text-align:center; text-indent:0;
  color:#fff; background:linear-gradient(180deg,#c8843a,#a8692a); border:1.5px solid rgba(255,255,255,.72);
  border-radius:999px; box-shadow:0 1px 3px rgba(120,80,20,.35); font-size:12px; font-weight:800; line-height:1.35;
  letter-spacing:0; white-space:nowrap; }
.fa-narrative p:last-child{ margin-bottom:0; }
.fa-narrative b{ color:var(--accent-darker,var(--accent)); font-weight:700; }
'''

INTENT_CSS = '''/* Type A/B 出題趣旨サマリー：出題者視点でコア・命題／角度／ねらいを俯瞰する */
.fa-intent{ margin:0 0 16px; padding:14px 16px; border-radius:12px;
  background:var(--mid-soft,#fff7e6); border:1px solid var(--mid,#e0c068); border-left:5px solid var(--mid,#d4a017); }
.fa-intent-title{ margin:0 0 10px; font-weight:800; font-size:1.0em; color:var(--accent-darker,var(--accent)); letter-spacing:.02em; }
.fa-intent-list{ margin:0; padding:0; list-style:none; }
.fa-intent-list li{ display:flex; gap:10px; align-items:flex-start; margin:0 0 8px; line-height:1.8; }
.fa-intent-list li:last-child{ margin-bottom:0; }
.fa-intent-label{ flex:0 0 8.5em; font-weight:700; font-size:.86em; color:var(--accent);
  background:rgba(255,255,255,.6); border-radius:6px; padding:2px 8px; text-align:center; }
.fa-intent-body{ flex:1 1 auto; }
.fa-intent-body b{ color:var(--accent-darker,var(--accent)); font-weight:700; }
'''


def find_lex(code):
    f = f'outputs/ux/000_TX/001_刑法/{code}_lex.html'
    if os.path.exists(f):
        return f
    cand = glob.glob(f'outputs/ux/000_TX/*/{code}_lex.html')
    if not cand:
        raise SystemExit(f'not found: {code}_lex.html')
    return cand[0]


def build_blocks(data):
    intent_html = ''
    intent = data.get('intent')
    if intent:
        rows_i = ''
        for lbl, k in (('問われているコア・命題', 'core'), ('問われ方（角度）', 'angle'), ('出題のねらい', 'aim')):
            v = intent.get(k)
            if v:
                rows_i += f'          <li><span class="fa-intent-label">{lbl}</span><span class="fa-intent-body">{v}</span></li>\n'
        if rows_i:
            intent_html = ('        <div class="fa-intent">\n'
                           '          <p class="fa-intent-title">🎯 出題趣旨 ── この問題は何を試しているか</p>\n'
                           '          <ul class="fa-intent-list">\n'
                           f'{rows_i}'
                           '          </ul>\n'
                           '        </div>\n')
    ntitle = data.get('title', 'この問題を物語で読む')
    paras = ''.join(f'        <p>{p}</p>\n' for p in data.get('paras', []))
    narrative_html = ('        <div class="fa-narrative">\n'
                      f'          <p class="fa-narrative-title">📖 {ntitle}</p>\n'
                      f'{paras}'
                      '        </div>\n')
    return intent_html + narrative_html


def inject(code, data):
    f = find_lex(code)
    h = open(f, encoding='utf-8').read()
    if '<div class="final-answer"' not in h:
        raise SystemExit(f'{code}: .final-answer が無い（注入先なし）')
    # 既存ブロックを除去（冪等）
    h = re.sub(r'\s*<div class="fa-intent">.*?</div>\s*(?=\n)', '\n', h, count=1, flags=re.S)
    h = re.sub(r'\s*<div class="fa-narrative">.*?</div>\s*(?=\n)', '\n', h, count=1, flags=re.S)
    block = build_blocks(data)
    # final-answer 開きタグ直後に挿入
    h2, n = re.subn(r'(<div class="final-answer"[^>]*>\n)', lambda m: m.group(1) + block, h, count=1)
    if n == 0:
        raise SystemExit(f'{code}: final-answer 開きタグ直後への挿入に失敗')
    h = h2
    # CSS（無ければ注入・冪等）
    if '.fa-narrative{' not in h:
        h = h.replace('</style>', NARR_CSS + '</style>', 1)
    if data.get('intent') and '.fa-intent{' not in h:
        h = h.replace('</style>', INTENT_CSS + '</style>', 1)
    open(f, 'w', encoding='utf-8').write(h)
    return f, len(data.get('paras', []))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python scripts/tx-inject-narrative.py <CODE> <narrative.json>'); sys.exit(2)
    code = sys.argv[1]
    data = json.load(open(sys.argv[2], encoding='utf-8'))
    f, np = inject(code, data)
    print(f'injected {code}: 段落 {np} 個 -> {f}')
