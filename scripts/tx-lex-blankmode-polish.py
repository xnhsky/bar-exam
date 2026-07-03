# -*- coding: utf-8 -*-
"""blank-mode/特殊問題 _lex の恒久polish（冪等）。
1. 選択肢ボタン潰れ修正：非○×の選択肢ボタンを持つ ox-row/ox-btn-group に mc クラスを付与
   （.ox-row.mc .ox-btn-group.mc .ox-btn{width:100%} を効かせ、○×用50px枠の縦潰れを解消）。
2. CSS gate 補完（G35/G37/G39）：gold 359 から該当CSSを注入（古いblank骨格の意匠gate FAIL解消）。
3. 選択肢の交互背景＋重厚化＋質感上げ：answer-ox-grid の ox-row に nth-of-type 交互背景・
   立体感（影/グラデ/枠）、連番バッジ、選択肢ボタンの質感を付与。
使い方: python scripts/tx-lex-blankmode-polish.py <_lex.html> [...]
"""
import re, sys, io, os
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass


def atomic_write(path, data):
    """一時ファイルに書いてから os.replace で原子的に差し替える。
    途中で kill(exit143) されても対象ファイルが 0 バイト空化しない安全策。
    さらに元の 50% 未満に縮む結果は破損とみなし書き込まない（サニティ）。
    """
    orig = os.path.getsize(path) if os.path.exists(path) else 0
    if orig and len(data.encode('utf-8')) < orig * 0.5:
        raise RuntimeError('refuse to write: result <50%% of original (%s)' % path)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

GOLD = 'outputs/ux/000_TX/001_刑法/刑TX359_lex.html'
MARK = '/* === blank-mode polish (恒久) === */'


def gate_css(gold):
    rules = []
    for m in re.finditer(r'\.fa-narrative\s+b\s*\{[^}]*\}', gold):
        rules.append(m.group(0))
    for m in re.finditer(r'[^{}]*\.tx-cycle[^{}]*\{[^}]*\}', gold):
        rules.append(m.group(0))
    for m in re.finditer(r'\.tx-article-flow[^{]*\.tx-flow-label[^{]*\{[^}]*\}', gold):
        rules.append(m.group(0))
    return list(dict.fromkeys(rules))


ENHANCE_CSS = r"""
/* --- 選択肢(空欄)行：交互背景＋重厚化＋質感 --- */
.answer-ox-grid{ display:grid; gap:12px; }
.answer-ox-grid .ox-row{ position:relative; border:1.5px solid rgba(150,128,72,.34) !important;
  border-radius:13px !important; padding:16px 18px 14px !important; margin:0 !important;
  box-shadow:0 6px 16px -9px rgba(120,96,44,.34), inset 0 1px 0 rgba(255,255,255,.65) !important; }
.answer-ox-grid .ox-row:nth-of-type(odd){ background:linear-gradient(180deg,#fffdf7 0%,#fbf5e8 100%) !important; }
.answer-ox-grid .ox-row:nth-of-type(even){ background:linear-gradient(180deg,#fbf3e2 0%,#f5ecd6 100%) !important; }
.answer-ox-grid .ox-row:hover{ box-shadow:0 9px 22px -10px rgba(120,96,44,.44), inset 0 1px 0 rgba(255,255,255,.7) !important; }
.answer-ox-grid .ox-label{ display:inline-flex; align-items:center; justify-content:center;
  min-width:2em; height:2em; padding:0 .35em; border-radius:9px; font-weight:850; font-size:1.0em;
  color:#fff; background:linear-gradient(180deg,#9a7d3e 0%,#7d6330 100%);
  box-shadow:0 3px 8px -3px rgba(120,90,40,.55), inset 0 1px 0 rgba(255,255,255,.4); margin-bottom:6px; }
.answer-ox-grid .ox-row .ox-q, .answer-ox-grid .ox-row .ox-stmt{ line-height:1.85; color:#3f3524; }
/* 選択肢ボタン(mc)の質感 */
.ox-row.mc .ox-btn-group.mc .ox-btn{ border:1.5px solid rgba(150,128,72,.5) !important;
  border-radius:11px !important; background:linear-gradient(180deg,#fffef9 0%,#f7efdc 100%) !important;
  box-shadow:0 3px 9px -5px rgba(120,96,44,.34), inset 0 1px 0 rgba(255,255,255,.7) !important;
  color:#5a4a22 !important; transition:box-shadow .14s, transform .05s; }
.ox-row.mc .ox-btn-group.mc .ox-btn:hover:not(:disabled){ box-shadow:0 6px 15px -6px rgba(120,96,44,.44) !important; }
.ox-row.mc .ox-btn-group.mc .ox-btn.selected{ background:linear-gradient(180deg,#efe6c4 0%,#e6d9a8 100%) !important;
  box-shadow:0 0 0 3px rgba(160,138,70,.4), inset 0 1px 0 rgba(255,255,255,.5) !important; color:#463c14 !important; }
.ox-btn-group.mc .mc-key{ background:linear-gradient(180deg,#a8894a,#8a6d34) !important; color:#fff !important;
  box-shadow:0 2px 5px -2px rgba(120,90,40,.5); }
"""


def polish(h, gold, gcss=None):
    if gcss is None:
        gcss = gate_css(gold)
    # 1. 潰れ修正：非○×の選択肢ボタンを持つファイルは、ox-btn-group/ox-row を mc 化
    #    （選択肢ボタンは長ラベル→.ox-row.mc .ox-btn-group.mc .ox-btn{width:100%} で full-width 化）
    has_choice_btn = re.search(r'answer-slot[^>]*data-value="[A-Za-zＡ-Ｚぁ-んァ-ヶ0-9０-９]', h) is not None
    if has_choice_btn:
        h = h.replace('<span class="ox-btn-group">', '<span class="ox-btn-group mc">')
        h = re.sub(r'<div class="ox-row"(?![^>]*\bmc\b)', '<div class="ox-row mc"', h)

    # 1b. G32 復習プール自己完結化：syn-lead / choice-points li / ox-pool 内の
    #     「（記述N）」他記述クロス参照を除去（冗長・記号フリー・冪等）
    def strip_refs(seg):
        seg = re.sub(r'\s*[（(]記述[0-9０-９ア-オア-ンa-jＡ-Ｚ、・\s]+[）)]', '', seg)   # （記述N）括弧参照を除去
        seg = re.sub(r'記述[0-9０-９ア-オ]+(?=は(?:正しい|誤り|正解|不正解|妥当|当たる|不当))', '本記述', seg)  # 記述Nは正しい→本記述は
        seg = re.sub(r'記述[0-9０-９ア-オ]+', 'この記述', seg)   # 残る裸の記述N参照
        return seg
    for pat in (r'(<p class="syn-lead">)(.*?)(</p>)',
                r'(<div class="choice-points">)(.*?)(</div>\s*</div>)',
                r'(<div class="ox-pool-explain"[^>]*>)(.*?)(</div>)',
                r'(<ul class="ox-pool-points">)(.*?)(</ul>)'):
        h = re.sub(pat, lambda m: m.group(1) + strip_refs(m.group(2)) + m.group(3), h, flags=re.S)

    # 2b. G37 H1 ヘッダのゼロ埋め（No.98 → No.098・3桁）
    def pad_h1(m):
        return m.group(1) + m.group(2).zfill(3) + m.group(3)
    h = re.sub(r'(<h1[^>]*>\s*No\.)(\d{1,2})(\s*──)', pad_h1, h, count=1)

    if MARK not in h:
        css = '\n' + MARK + '\n' + '\n'.join(gcss) + '\n' + ENHANCE_CSS + '\n'
        si = h.rfind('</style>')
        h = h[:si] + css + h[si:]
        # G35: 既存 .fa-narrative b の 700 を 560 に
        h = re.sub(r'(\.fa-narrative b\s*\{[^}]*font-weight:\s*)700', r'\g<1>560', h, count=1)
    return h


def main():
    gold = open(GOLD, encoding='utf-8').read()
    gcss = gate_css(gold)  # gold から一度だけ抽出（毎ファイル再計算しない）
    for p in sys.argv[1:]:
        h = open(p, encoding='utf-8').read()
        if 'answer-ox-grid' not in h:
            print('[SKIP] %s' % p); continue
        out = polish(h, gold, gcss)
        if out == h:
            print('[--] %s (変更なし)' % p); continue
        atomic_write(p, out)
        print('[OK] %s' % p)


if __name__ == '__main__':
    main()
