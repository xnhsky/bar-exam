# -*- coding: utf-8 -*-
"""rollout/combo-last-A: 自動ビルダ非対応の最難ケース（○×組合せ／matching/letter／部分組合せ／
   個数／個別判定 ox-other）を二系統化する薄ランナー。

   build-lite-lex.py の build()（reuse）を再利用（同ファイル未改変＝マージ衝突回避）。
   _lex は常に ox-grid＋自己完結命題＋軽量ナビ。公式は spec['kind'] で出し分け：
     'multi' : _lex を keep_official reuse で作り、公式を multi（正解記述を cv＋極性 select から機械合成）へ
     'count' : _lex を keep_official reuse で作り、公式を single（個数 0〜N・機械合成）へ
     'keep'  : _lex のみ（公式は元の ox-grid を温存＝各記述○×/1·2 個別判定で単一番号が無い型）
   ○×・正解番号・選択個数は data-correct-value（answer-key）から機械合成＝手書きしない（符号反転事故ゼロ）。

   各行の ox-stmt は spec['stmt']（記号フリー・自己完結命題・条文判例つき・G30）へ
   data-stmt 順に positional 置換する（現行 ox-stmt span を実物から抽出＝old 一致を保証）。
   冪等：公式が既に single/multi なら公式書換 skip（_lex は keep_official で再生成）。"""
import importlib.util, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # build-lite-lex の `from lite_specs import ...` 解決用

def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

bl = _load("build_lite_lex", "build-lite-lex.py")
S  = _load("specs_combo_last_A", "specs_combo_last_A.py")
ROOT, SUBJ = bl.ROOT, bl.SUBJ

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

def _read_official(num):
    p = os.path.join(ROOT, SUBJ, f"刑TX{num}.html")
    return p, open(p, encoding="utf-8").read()

def _rewrite_official(num, new_area, head_txt):
    p, src = _read_official(num)
    a0, a1 = bl.find_block(src)
    head_m = re.search(r'<h3[^>]*>【解答】[^<]*</h3>\s*$', src[:a0])
    cut0 = head_m.start() if head_m else a0
    head_official = bl.HEAD_NEW.replace('__TXT__', head_txt)
    open(p, "w", encoding="utf-8").write(src[:cut0] + head_official + new_area + src[a1:])

def _auto_replacements(area, stmt_map):
    """現行 ox-stmt span を data-stmt 順に抽出し、spec['stmt'] へ positional 置換する old/new を作る。
       old は実物から取るので build-lite-lex の `assert rep['old'] in lex` を必ず満たす。"""
    keys = re.findall(r'<div class="ox-row" data-stmt="([^"]*)"', area)
    spans = re.findall(r'<span class="ox-stmt">.*?</span>', area, re.S)
    assert len(keys) == len(spans), f"keys({len(keys)})/ox-stmt({len(spans)}) 不一致"
    reps = []
    for key, old in zip(keys, spans):
        if key not in stmt_map:
            continue
        new = '<span class="ox-stmt">' + stmt_map[key] + '</span>'
        if old != new:
            reps.append({'old': old, 'new': new})
    return reps

def _lex_via_reuse(num, spec):
    """_lex を keep_official reuse で生成（公式は触らない）。ox-stmt を spec['stmt'] へ置換。"""
    p, src = _read_official(num)
    a0, a1 = bl.find_block(src)
    area = src[a0:a1]
    s2 = dict(spec)
    s2['mode'] = 'reuse'
    s2['keep_official'] = True
    s2.setdefault('official_num', 'keep')
    if spec.get('stmt'):
        s2['replacements'] = _auto_replacements(area, spec['stmt'])
    bl.build(num, s2)

def build_multi(num, spec):
    p, src = _read_official(num)
    a0, a1 = bl.find_block(src)
    at = re.search(r'data-answer-type="([^"]*)"', src[a0:a1])
    already = bool(at and at.group(1) != 'ox-grid')
    _lex_via_reuse(num, spec)
    if already:
        print(f"刑TX{num}: 公式は既に {at.group(1)} → 公式書換 skip（_lex のみ更新）"); return
    p, src = _read_official(num); a0, a1 = bl.find_block(src); area = src[a0:a1]
    expl = re.search(r'data-explanation="([^"]*)"', area, re.S).group(1)
    cv = re.search(r'data-correct-value="([^"]*)"', area).group(1)
    keys = re.findall(r'<div class="ox-row" data-stmt="([^"]*)"', area)
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
    print(f"刑TX{num}: kind=multi 公式 correct={cval}（{qlead}{n}個） select={sel}")

def build_count(num, spec):
    p, src = _read_official(num)
    a0, a1 = bl.find_block(src)
    at = re.search(r'data-answer-type="([^"]*)"', src[a0:a1])
    already = bool(at and at.group(1) != 'ox-grid')
    _lex_via_reuse(num, spec)
    if already:
        print(f"刑TX{num}: 公式は既に {at.group(1)} → 公式書換 skip（_lex のみ更新）"); return
    p, src = _read_official(num); a0, a1 = bl.find_block(src); area = src[a0:a1]
    expl = re.search(r'data-explanation="([^"]*)"', area, re.S).group(1)
    cv = re.search(r'data-correct-value="([^"]*)"', area).group(1)
    seq = re.sub(r'[^○×]', '', cv)
    sel = spec['select']
    cnt = sum(1 for ch in seq if ch == sel)  # 機械合成：該当記述の個数
    N = len(seq)
    qlead = spec['qlead']
    buttons = ''.join('        <button class="answer-slot" type="button" data-value="%d">%d</button>\n' % (i, i) for i in range(0, N + 1))
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

def build_keep(num, spec):
    # 各記述○×/1·2 個別判定型＝単一の組合せ番号が無い → 公式は元の ox-grid を温存、_lex のみ生成。
    _lex_via_reuse(num, spec)
    print(f"刑TX{num}: kind=keep 公式=ox-grid 温存（_lex のみ）")

def run(num, spec):
    kind = spec.get('kind', 'keep')
    if kind == 'multi':   build_multi(num, spec)
    elif kind == 'count': build_count(num, spec)
    else:                 build_keep(num, spec)

if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(S.SPECS.keys())
    for num in targets:
        if num not in S.SPECS:
            print(f"刑TX{num}: SPECS 未定義 → skip"); continue
        run(num, S.SPECS[num])
    print("COMBO-LAST-A DONE")
