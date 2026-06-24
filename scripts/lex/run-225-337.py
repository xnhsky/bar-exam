# -*- coding: utf-8 -*-
"""Band 225-337（②③型）の _lex＋公式を生成する薄ランナー。
   build-lite-lex.py / build-combo-lex.py の build() を再利用（両ファイル未改変）。
   問題固有データは specs_225_337.py（LITE / COMBO）のみ。
   引数で番号を絞れる（例: python run-225-337.py 226 227）。冪等（公式が single/multi なら skip）。

   spec['kind'] で公式の出し分け（_lex は常に ox-grid＋解法ナビ）:
     'single'(既定) : bl.build をそのまま（reuse=官 single 組合せ番号 / keep_official=ox-grid 温存 / rebuild）
     'multi'        : _lex を keep_official reuse で作り、公式を multi（正解記述を機械合成）へ書換
     'count'        : _lex を keep_official reuse で作り、公式を single（個数 0〜N・機械合成）へ書換
   ○×・正解番号は data-correct-value（answer-key）から機械合成＝手書きしない（符号反転事故ゼロ）。"""
import importlib.util, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # build-lite-lex の `from lite_specs import ...` 解決用

def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

bl = _load("build_lite_lex", "build-lite-lex.py")
bc = _load("build_combo_lex", "build-combo-lex.py")
S  = _load("specs_225_337", "specs_225_337.py")

ROOT, SUBJ = bl.ROOT, bl.SUBJ

def _read_official(num):
    p = os.path.join(ROOT, SUBJ, f"刑TX{num}.html")
    return p, open(p, encoding="utf-8").read()

MULTI_AREA = (
  '<div class="answer-area" id="answer-area" data-correct-value="{cval}" data-answer-type="multi" data-explanation="{expl}">\n'
  '      <p class="answer-instruction">{instr}</p>\n\n'
  '      <div class="answer-row">\n{buttons}      </div>\n'
  '      <p class="selection-counter">選択中: 0 / {n} 個</p>\n\n'
  '      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>\n'
  '      <div id="answer-feedback" hidden=""></div>\n\n'
  '      <div class="final-answer" hidden="">\n'
  '        <p class="fa-summary">{summary}</p>\n'
  '      </div>')

def _rewrite_official(num, new_area, head_txt):
    p, src = _read_official(num)
    a0, a1 = bl.find_block(src)
    head_m = re.search(r'<h3[^>]*>【解答】[^<]*</h3>\s*$', src[:a0])
    cut0 = head_m.start() if head_m else a0
    head_official = bl.HEAD_NEW.replace('__TXT__', head_txt)
    open(p, "w", encoding="utf-8").write(src[:cut0] + head_official + new_area + src[a1:])

def build_multi(num, spec):
    # 公式が既に single/multi なら（再実行時）skip：bl.build が冪等ガードを持つので keep_official 経由で _lex のみ更新
    p, src = _read_official(num)
    a0, a1 = bl.find_block(src)
    at = re.search(r'data-answer-type="([^"]*)"', src[a0:a1])
    already = at and at.group(1) == 'multi'
    # (1) _lex を keep_official reuse で生成（公式は触らない）
    s2 = dict(spec); s2['keep_official'] = True; s2.setdefault('mode', 'reuse'); s2.setdefault('official_num', 'multi')
    bl.build(num, s2)
    if already:
        print(f"刑TX{num}: 公式は既に multi → 公式書換は skip（_lex のみ更新）"); return
    # (2) 公式を multi へ書換（正解記述は cv＋極性から機械合成）
    p, src = _read_official(num); a0, a1 = bl.find_block(src); area = src[a0:a1]
    expl = re.search(r'data-explanation="([^"]*)"', area, re.S).group(1)
    cv = re.search(r'data-correct-value="([^"]*)"', area).group(1)
    keys = re.findall(r'<div class="ox-row[^"]*" data-stmt="([^"]*)"', area)
    seq = re.sub(r'[^○×]', '', cv)
    assert len(keys) == len(seq), f"{num}: keys/seq 不一致 {keys} {seq}"
    sel = spec['select']  # '○'=正しいものを選ぶ / '×'=誤っているものを選ぶ
    correct = [keys[i] for i, ch in enumerate(seq) if ch == sel]
    n = len(correct)
    assert n >= 1, f"{num}: 正解記述0件（cv/select 不整合）"
    cval = ','.join(correct)
    buttons = ''.join('        <button class="answer-slot" type="button" data-value="%s">%s</button>\n' % (k, k) for k in keys)
    qlead = spec['qlead']
    rng = f"{keys[0]}〜{keys[-1]}"
    instr = f"次の{rng}のうち、{qlead}を{n}個選び、「解答を表示」を押してください。"
    head_txt = f"【解答】── {qlead}を{n}個選ぶ"
    new_area = MULTI_AREA.format(cval=cval, expl=expl, instr=instr, buttons=buttons, n=n, summary=spec['summary'])
    _rewrite_official(num, new_area, head_txt)
    print(f"刑TX{num}: kind=multi 公式 correct={cval}（{qlead}{n}個）  select={sel}")

def build_count(num, spec):
    # 個数問題：_lex は ox-grid（各記述○×）＋ナビ、公式は「誤り/正しいものの個数」single（0〜N・機械合成）
    p, src = _read_official(num)
    a0, a1 = bl.find_block(src)
    at = re.search(r'data-answer-type="([^"]*)"', src[a0:a1])
    already = at and at.group(1) == 'single'
    s2 = dict(spec); s2['keep_official'] = True; s2.setdefault('mode', 'reuse'); s2.setdefault('official_num', 'count')
    bl.build(num, s2)
    if already:
        print(f"刑TX{num}: 公式は既に single → 公式書換 skip（_lex のみ更新）"); return
    p, src = _read_official(num); a0, a1 = bl.find_block(src); area = src[a0:a1]
    expl = re.search(r'data-explanation="([^"]*)"', area, re.S).group(1)
    cv = re.search(r'data-correct-value="([^"]*)"', area).group(1)
    seq = re.sub(r'[^○×]', '', cv)
    sel = spec['select']
    cnt = sum(1 for ch in seq if ch == sel)         # 機械合成：該当記述の個数
    N = len(seq)
    qlead = spec['qlead']
    opts = list(range(0, N + 1))
    buttons = ''.join('        <button class="answer-slot" type="button" data-value="%d">%d</button>\n' % (i, i) for i in opts)
    instr = f"{qlead}の個数（0〜{N}）を1つ選び、「解答を表示」を押してください。"
    head_txt = f"【解答】── {qlead}の個数（0〜{N}）を選ぶ"
    new_area = ('<div class="answer-area" id="answer-area" data-correct-value="' + str(cnt) + '" '
      'data-answer-type="single" data-explanation="' + expl + '">\n'
      '      <p class="answer-instruction">' + instr + '</p>\n\n'
      '      <div class="answer-row">\n' + buttons + '      </div>\n\n'
      '      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>\n'
      '      <div id="answer-feedback" hidden=""></div>\n\n'
      '      <div class="final-answer" hidden="">\n'
      '        <p class="fa-summary">' + spec['summary'] + '</p>\n'
      '      </div>')
    _rewrite_official(num, new_area, head_txt)
    print(f"刑TX{num}: kind=count 公式 個数={cnt}/{N}  select={sel}")

def run(num, spec):
    kind = spec.get('kind', 'single')
    if kind == 'multi':   build_multi(num, spec)
    elif kind == 'count': build_count(num, spec)
    else:                 bl.build(num, spec)

targets = set(sys.argv[1:])
for num, spec in S.LITE.items():
    if targets and num not in targets: continue
    run(num, spec)
for num, spec in S.COMBO.items():
    if targets and num not in targets: continue
    bc.build(num, spec)
print("BAND 225-337 DONE")
