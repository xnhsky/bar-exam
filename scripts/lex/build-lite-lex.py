# -*- coding: utf-8 -*-
"""TX 二系統化・057方式/○×軽量ナビ ビルダ（350方式に適合しない組合せ／事例判定型）。

対象＝部分組合せ・多値集合・事例判定型など、SOLVE-NAV の COMBO 消去エンジン
（全空欄が COMBOS に揃う前提）に適合しない問題。057_lex の設計（自己完結命題の
ox-grid ＋ 軽量ナビ）に倣い、次の2ファイルへ展開する：

  - outputs/000_TX/001_刑法/刑TXNNN.html
      = 公式（組合せ番号 single・data-correct-value=正解組合せ番号。事案判定型も番号 single）
  - outputs/ux/000_TX/001_刑法/刑TXNNN_lex.html
      = 既存 ox-grid を流用し、各空欄/各事例を 1 ox-row の実体命題（記号フリー・G30・
        条文判例つき）に置換。軽量ナビ（検討順 ORDER＋💡コツ＋実体命題の誘導のみ・
        厳密な組合せ消去パネルは使わない）。採点記録は ox-grid 一本。

エンジン JS（軽量ナビ）は本ファイル内テンプレ＝問題横断で逐語固定。問題固有データは
LITE_SPECS dict のみ（各 ox-row の q/opts/core・ORDER・各ステップの tip・公式正解番号・
公式 fa-summary・公式 instruction）。ROOT は __file__ 起点で可搬。冪等ガード
（公式が既に single/multi なら skip）。

mode:
  - 'reuse' : 既存 ox-grid（自己完結命題が既にある型）を温存しつつ ox-stmt/core を
              本問値で上書き（任意）。data-correct-value はそのまま。official_num を明示。
  - 'rebuild': symbol-only の per-combo ○× 行（174/351/218 等）を、行ごとの実体命題へ
              置換。○× cv を維持（G29 は ○×ボタンで自動充足）。official_num を明示。
"""
import re, shutil, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBJ = "outputs/000_TX/001_刑法"
UXD  = "outputs/ux/000_TX/001_刑法"
NAV_TEMPLATE = os.path.join(ROOT, UXD, "刑TX350_lex.html")
REFLEX_HEADER = '登場した論点のコア（文言・趣旨・射程・切断点・転用）'
REFLEX_TAGS = ('文言', '趣旨', '射程', '切断点', '転用')
REFLEX_CSS = '''/* TX-LEX short-answer reflex core: 文言・趣旨・射程・切断点・転用 */
.tx-reflex-core{display:grid;gap:6px;margin:0;font-size:.94em;line-height:1.7;}
.tx-reflex-line{margin:0;padding-left:5.4em;text-indent:-5.4em;}
.tx-reflex-tag{display:inline-block;min-width:4.2em;margin-right:.55em;padding:.12em .48em;border-radius:999px;border:1px solid #d7cfa8;background:#efe7cb;color:#65581d;font-weight:800;text-align:center;text-indent:0;}
.tx-reflex-cut .tx-reflex-tag{border-color:#dba9b2;background:#ffefe7;color:#774252;}
'''


def reflex_core_html(core):
    if isinstance(core, dict):
        fallback = core.get('text') or core.get('core') or ''
        values = {tag: core.get(tag, fallback) for tag in REFLEX_TAGS}
    else:
        fallback = str(core)
        values = {
            '文言': fallback,
            '趣旨': '制度趣旨・保護法益から、この命題がなぜ問題になるかを確認する。',
            '射程': fallback,
            '切断点': '誤答を切る条件・危険語を、問題ローカル記号ではなく実体概念で押さえる。',
            '転用': '類似肢では、同じ要件・事実・判例射程を先に確認する。',
        }
    lines = []
    for tag in REFLEX_TAGS:
        cls = ' tx-reflex-cut' if tag == '切断点' else ''
        lines.append(f'<p class="tx-reflex-line{cls}"><span class="tx-reflex-tag">{tag}</span>{values[tag]}</p>')
    return '<div class="tx-reflex-core">' + ''.join(lines) + '</div>'

# ---- 解法ナビ CSS（350_lex から逐語抽出：sn-* と ox-row.mc 等の見栄え定義を流用） ----
_nav_src = open(NAV_TEMPLATE, encoding="utf-8").read()
_css_m = re.search(
    r'(/\* =+\n\s*解法ナビ（試作・議論形式）.*?\.ox-core-wrap \.ox-core-tag\{[^}]*\})',
    _nav_src, re.S)
if not _css_m:
    raise SystemExit("solve-nav CSS block not found in 350_lex template")
CSS = _css_m.group(1)

# ---- 解法ナビ SHELL（軽量版・350_lex と同一構造シェル） ----
NAV_SHELL = ('    <div class="solve-nav" id="solve-nav">\n'
  '      <div class="sn-head">\U0001F4D0 解法ナビ\n'
  '        <span class="sn-sub">__SUB__</span>\n'
  '      </div>\n'
  '      <div class="sn-body">\n'
  '        <p class="sn-remain" id="sn-remain"></p>\n'
  '        <div id="sn-stage"></div>\n'
  '      </div>\n'
  '    </div>\n\n')

# ---- 軽量ナビ JS（組合せ消去に依存しない＝検討順 ORDER＋💡コツ＋実体命題の誘導のみ）。
#      下の ox-grid を監視し、現在ステップの行をハイライト。採点は ox-grid 一本（reveal）。 ----
NAV_JS = r'''<script>
/* 解法ナビ（軽量版・057系）：組合せ消去パネルは使わず、検討順に各空欄/事例を下の一問一答で
   1つずつ回答するよう誘導し、要所で💡コツと論点のコア（実体命題）を提示する。
   採点は下の ox-grid 一本（記録は ox-grid＝Lexia 復習プール）。エンジンは問題横断で固定。 */
(function(){
  var root = document.getElementById('solve-nav');
  var area = document.querySelector('.answer-area[data-answer-type="ox-grid"]');
  if (!root || !area) return;
  var remainBox = document.getElementById('sn-remain');
  var stage = document.getElementById('sn-stage');
  /* ===== 問題固有データ（new-tx/ビルダが本問値で置換・ここだけ編集）===== */
  var ORDER = __ORDER__;   // 検討順（ox-row の data-stmt 値の配列）
  var STEP  = __STEP__;    // { '<data-stmt>': {label:'①', q:'…', tip:'…'} , … }
  /* ===== 問題固有データ ここまで。以下のエンジンは固定＝編集しない ===== */
  function rowOf(s){ return area.querySelector('.ox-row[data-stmt="'+s+'"]'); }
  function answered(s){ var r=rowOf(s); return !!(r && r.querySelector('.ox-btn.selected')); }
  function currentStep(){ for (var i=0;i<ORDER.length;i++){ if(!answered(ORDER[i])) return ORDER[i]; } return null; }
  function doneCount(){ var n=0; ORDER.forEach(function(s){ if(answered(s)) n++; }); return n; }
  function render(){
    var cur = currentStep();
    var done = doneCount();
    remainBox.innerHTML = '回答済み：<strong>'+done+' / '+ORDER.length+'</strong>　─　各設問を検討順に、下の一問一答で1つずつ判断しよう。';
    area.querySelectorAll('.ox-row').forEach(function(r){
      r.classList.toggle('sn-current', !!cur && r.getAttribute('data-stmt') === cur);
    });
    var h = '';
    if (cur){
      var s = STEP[cur] || {};
      h += '<p class="sn-progress">STEP '+(done+1)+' / '+ORDER.length+'　─　'+(s.label||'')+' を検討</p>';
      if (s.q)   h += '<p class="sn-step-q">'+s.q+'</p>';
      if (s.tip) h += '<div class="sn-tip"><span class="sn-tip-h">💡 コツ</span><span class="sn-tip-b">'+s.tip+'</span></div>';
      h += '<p class="sn-step-loc">↓ 下の一問一答の '+(s.label||'当該設問')+' で語句を選ぶと、次の設問へ進みます。</p>';
    } else {
      h += '<div class="sn-result"><div class="sn-big">全部そろいました</div>下の「解答を表示」で採点。番号でなく、いま辿った各設問の判別の筋道（論点のコア）ごと身につけよう。採点後、各行に論点のコアが展開されます。</div>';
    }
    stage.innerHTML = h;
  }
  area.addEventListener('click', function(e){ if (e.target.closest('.ox-btn') || e.target.closest('.reveal-answer-btn')) setTimeout(render, 0); }, false);
  document.body.classList.add('snav-on');
  render();
})();
</script>
'''

# ---- reuse 型：ox-stmt（実体命題）と ox-q を行ごとに上書きするためのテンプレ無し
#      （既存 ox-grid を温存し、必要時のみ Edit 的に置換）。
# ---- rebuild 型：○× 行を実体命題で作り直すための行テンプレ
ROW_OX = ('        <div class="ox-row" data-stmt="__S__">\n'
  '          <span class="ox-label">__LABEL__</span>\n'
  '          <span class="ox-stmt">__STMT__</span>\n'
  '          <span class="ox-btn-group">\n'
  '            <button class="answer-slot ox-btn" type="button" data-value="○">○</button>\n'
  '            <button class="answer-slot ox-btn" type="button" data-value="×">×</button>\n'
  '          </span>\n'
  '        </div>\n')

HEAD_NEW = ('<h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; '
  'margin:26px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); '
  'font-family:var(--font-display);">__TXT__</h3>\n\n    ')


def find_block(html, start_tag='<div class="answer-area"'):
    i = html.find(start_tag)
    depth = 0
    for m in re.finditer(r'<(/?)div\b', html[i:], re.I):
        if m.group(1) == '':
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                j = i + m.end(); gt = html.find('>', j); return i, gt + 1
    raise SystemExit("close not found")


def inject_lex(lex, spec):
    """_lex に CSS／SHELL／軽量ナビ JS を注入（answer-area 改変は呼び出し側で済ませた lex を受ける）。"""
    # CSS（</style> 直前）
    k = lex.rfind('</style>')
    lex = lex[:k] + "\n/* === 解法ナビ（Lexia用・軽量版・常時表示） === */\n" + CSS + "\n" + REFLEX_CSS + "\n" + lex[k:]
    # SHELL ＋ 新【解答】h3 を answer-area 直前へ（旧【解答】h3 は除去）
    la0, la1 = find_block(lex)
    lhead = re.search(r'<h3[^>]*>【解答】[^<]*</h3>\s*$', lex[:la0])
    cut0 = lhead.start() if lhead else la0
    shell = NAV_SHELL.replace('__SUB__', spec['sub'])
    head_new = HEAD_NEW.replace('__TXT__', '【解答】')
    lex = lex[:cut0] + shell + head_new + lex[la0:]
    # JS（</body> 直前へ）
    js = (NAV_JS.replace('__ORDER__', json.dumps(spec['order'], ensure_ascii=False))
                .replace('__STEP__', json.dumps(spec['step'], ensure_ascii=False)))
    bclose = lex.rfind('</body>')
    lex = lex[:bclose] + js + "\n" + lex[bclose:]
    return lex


def write_official(src, a0, a1, head_m, ans, expl, summary, instr, nopt):
    head_official = HEAD_NEW.replace('__TXT__', '【解答】── 正しい組合せ番号を 1〜'+str(nopt)+' から1つ選ぶ')
    slots = ''.join('        <button class="answer-slot" type="button" data-value="%d">%d</button>\n' % (n, n) for n in range(1, nopt+1))
    official_area = ('<div class="answer-area" id="answer-area" data-correct-value="'+str(ans)+'" '
      'data-answer-type="single" data-explanation="'+expl+'">\n'
      '      <p class="answer-instruction">'+instr+'</p>\n\n'
      '      <div class="answer-row">\n'+slots+'      </div>\n\n'
      '      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>\n'
      '      <div id="answer-feedback" hidden=""></div>\n\n'
      '      <div class="final-answer" hidden="">\n'
      '        <p class="fa-summary">'+summary+'</p>\n'
      '      </div>')
    cut0 = head_m.start() if head_m else a0
    return src[:cut0] + head_official + official_area + src[a1:]


def build(num, spec):
    src_path = os.path.join(ROOT, SUBJ, f"刑TX{num}.html")
    lex_path = os.path.join(ROOT, UXD, f"刑TX{num}_lex.html")
    if not os.path.exists(src_path):
        print(f"刑TX{num}: NO FILE → skip"); return
    src = open(src_path, encoding="utf-8").read()
    a0, a1 = find_block(src)
    area = src[a0:a1]
    at = re.search(r'data-answer-type="([^"]*)"', area)
    if at and at.group(1) != 'ox-grid':
        print(f"刑TX{num}: 変換済み（data-answer-type={at.group(1)}）→ skip"); return

    expl = re.search(r'data-explanation="([^"]*)"', area, re.S).group(1)
    pre = src[:a0]
    head_m = re.search(r'<h3[^>]*>【解答】[^<]*</h3>\s*$', pre)
    ans = spec['official_num']
    nopt = spec.get('nopt', 5)

    # ===== (1) _lex =====
    shutil.copyfile(src_path, lex_path)
    lex = open(lex_path, encoding="utf-8").read()

    if spec['mode'] == 'rebuild':
        # symbol-only ○× 行を実体命題で作り直す（ox-grid 全体を差し替え）
        lrows = ''
        for r in spec['rows']:
            lrows += (ROW_OX.replace('__S__', r['s']).replace('__LABEL__', r['label'])
                      .replace('__STMT__', r['stmt']))
        cv = spec['cv']
        akey = ','.join(f"{r['s']}:{('o' if r['verdict']=='○' else 'x')}" for r in spec['rows'])
        vrows = ''
        for r in spec['rows']:
            color = 'var(--recall-correct-light)' if r['verdict'] == '○' else 'var(--recall-incorrect)'
            vrows += (f'            <tr data-stmt="{r["s"]}" data-verdict="{("o" if r["verdict"]=="○" else "x")}">'
                f'<td style="text-align:center;font-weight:700;">{r["label"]}</td>'
                f'<td style="text-align:center;font-weight:800;color:{color};">{r["verdict"]}</td>'
                f'<td>{reflex_core_html(r["core"])}</td></tr>\n')
        lex_area = (
          f'<div class="answer-area" id="answer-area" data-correct-value="{cv}" data-answer-type="ox-grid" data-explanation="{expl}">\n'
          f'      <p class="answer-instruction">各組合せ（肢1〜{nopt}）に ○（①〜の対応がすべて正しい組合せ）／×（いずれかが誤り）を付けてから「解答を表示」を押してください。下表「論点のコア」が学習資産です。</p>\n\n'
          f'      <div class="answer-ox-grid">\n{lrows}      </div>\n\n'
          '      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>\n'
          '      <div id="answer-feedback" hidden=""></div>\n\n'
          '      <div class="final-answer" hidden="">\n'
          '        <p class="fa-summary"><strong>正解</strong>　各組合せの○×は下表のとおり。組合せ番号を覚えるのではなく、各組合せが主張する<strong>法理</strong>で正誤を判定する。下表「論点のコア」が学習資産。</p>\n'
          f'        <table class="statement-verdict-table" data-answer-key="{akey}">\n'
          f'          <thead><tr><th style="width:3em;">組合せ</th><th style="width:3.5em;">正誤</th><th>{REFLEX_HEADER}</th></tr></thead>\n'
          f'          <tbody>\n{vrows}          </tbody>\n'
          '        </table>\n'
          '      </div>')
        la0, la1 = find_block(lex)
        lex = lex[:la0] + lex_area + lex[la1:]
    else:  # reuse：既存 ox-grid を温存しつつ ox-stmt/ox-q を本問値で上書き（任意）
        for rep in spec.get('replacements', []):
            assert rep['old'] in lex, f"{num}: 置換対象が無い: {rep['old'][:40]}"
            lex = lex.replace(rep['old'], rep['new'], 1)

    lex = inject_lex(lex, spec)
    open(lex_path, "w", encoding="utf-8").write(lex)

    # ===== (2) 公式 =====
    if spec.get('keep_official'):
        # マークシート個別判定型（各事例に1/2/3 等）＝過去問そのものが個別判定で、
        # 単一の組合せ番号が存在しない。公式は既存 ox-grid を温存（ナビは入れない）。
        print(f"刑TX{num}: mode={spec['mode']} 公式=ox-grid 温存（番号single なし）  lex={len(lex)}B")
        return
    instr = spec.get('instr', f'①〜の語句の正しい組合せを、上記【組合せ】の 1〜{nopt} から1つ選び、「解答を表示」を押してください。')
    off = write_official(src, a0, a1, head_m, ans, expl, spec['summary'], instr, nopt)
    open(src_path, "w", encoding="utf-8").write(off)
    print(f"刑TX{num}: mode={spec['mode']} 公式single={ans}  lex={len(lex)}B official={len(off)}B")


# 問題固有データは別ファイルから読み込む（巨大化回避・section 分割）
from lite_specs import LITE_SPECS  # noqa: E402

if __name__ == '__main__':
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(LITE_SPECS.keys())
    for num in targets:
        if num not in LITE_SPECS:
            print(f"刑TX{num}: LITE_SPECS 未定義 → skip"); continue
        build(num, LITE_SPECS[num])
    print("DONE")
