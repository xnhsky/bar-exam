# -*- coding: utf-8 -*-
"""TX 二系統化・組合せ型（350方式）ビルダ。

対象＝PART A が「①〜⑤(⑥)の空欄に語句(letter)を入れる組合せ5択」で、
既存 000_TX が ox-grid（各行が組合せ全体 ①a②d… の記号のみ＝G30 違反・プール価値ゼロ）に
エンコードされている問題。これを次の2ファイルへ展開する：

  - outputs/ux/000_TX/001_刑法/刑TXNNN_lex.html
      = 空欄単位 ox-grid（各空欄＝1行・letter 選択肢＋自己完結命題）＋解法ナビ[SCRIPT-COMBO]（常時表示）
  - outputs/000_TX/001_刑法/刑TXNNN.html
      = 公式（単一5択＝組合せ番号 single・data-correct-value=正解組合せ番号）

設計思想は build-ox-lex.py と同一：
  エンジン(JS/CSS)は 350_lex から逐語コピー＝テンプレ。問題固有データは COMBO_SPECS dict のみ。
  ROOT は __file__ 起点で可搬。冪等ガード（公式が既に single/multi なら skip）。
"""
import re, shutil, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBJ = "outputs/000_TX/001_刑法"
UXD  = "outputs/ux/000_TX/001_刑法"
NAV_TEMPLATE = os.path.join(ROOT, UXD, "刑TX350_lex.html")

# ---- 解法ナビ CSS（350_lex から逐語抽出：CSS コメント開始 〜 ox-core-tag まで） ----
_nav_src = open(NAV_TEMPLATE, encoding="utf-8").read()
_css_m = re.search(
    r'(/\* =+\n\s*解法ナビ（試作・議論形式）.*?\.ox-core-wrap \.ox-core-tag\{[^}]*\})',
    _nav_src, re.S)
if not _css_m:
    raise SystemExit("solve-nav CSS block not found in 350_lex template")
CSS = _css_m.group(1)

# ---- 解法ナビ SHELL（350_lex の【発言】用文言を空欄汎用に。逐語構造） ----
NAV_SHELL = ('    <div class="solve-nav" id="solve-nav">\n'
  '      <div class="sn-head">\U0001F4D0 解法ナビ\n'
  '        <span class="sn-sub">__SUB__</span>\n'
  '      </div>\n'
  '      <div class="sn-body">\n'
  '        <div class="sn-combos" id="sn-combos"></div>\n'
  '        <p class="sn-remain" id="sn-remain"></p>\n'
  '        <div id="sn-stage"></div>\n'
  '      </div>\n'
  '    </div>\n\n')

# ---- 解法ナビ JS（[SCRIPT-COMBO] ガイド専念型・350_lex 逐語＝エンジン不可侵） ----
# COMBOS / ORDER / TIP のみ問題固有（差替）。それ以外のロジックは 350_lex から1文字も変えない。
NAV_JS_TMPL = r'''<script>
/* 解法ナビ（ガイド専念）：回答ボタンは持たず、検討順＋💡コツ＋組合せ消去パネルで誘導する。
   ユーザーは下の ox-grid（多肢選択の一問一答）で各空欄を1つずつ回答 → ここが消去を更新 →
   全部そろったら下の「解答を表示」で採点（記録は ox-grid 一本＝Lexia 復習プール）。 */
(function(){
  var root = document.getElementById('solve-nav');
  var area = document.querySelector('.answer-area[data-answer-type="ox-grid"]');
  if (!root || !area) return;
  var combosBox = document.getElementById('sn-combos');
  var remainBox = document.getElementById('sn-remain');
  var stage = document.getElementById('sn-stage');
  var CIRC = {'1':'①','2':'②','3':'③','4':'④','5':'⑤','6':'⑥','7':'⑦','8':'⑧','9':'⑨'};
  // 本物の組合せ5択（番号→各空欄の語句）
  var COMBOS = __COMBOS__;
  var ORDER = __ORDER__;
  var TIP = __TIP__;
  function picks(){
    var p = {};
    area.querySelectorAll('.ox-row').forEach(function(r){
      var b = r.getAttribute('data-stmt'); var sel = r.querySelector('.ox-btn.selected');
      if (b && sel) p[b] = (sel.getAttribute('data-value') || '');
    });
    return p;
  }
  function liveNums(p){
    var out = [];
    for (var n in COMBOS){ if(!COMBOS.hasOwnProperty(n)) continue;
      var ok = true;
      for (var b in p){ if(p.hasOwnProperty(b) && COMBOS[n][b] !== p[b]){ ok = false; break; } }
      if (ok) out.push(n);
    }
    return out;
  }
  function renderCombos(p){
    var live = {}; liveNums(p).forEach(function(n){ live[n] = true; });
    var html = '';
    Object.keys(COMBOS).forEach(function(n){
      var seq = '';
      ORDER_ALL.forEach(function(b){
        var L = COMBOS[n][b]; if (L === undefined) return;
        var on = (p[b] && p[b] === L);
        seq += (on ? '<b>' : '') + CIRC[b] + L + (on ? '</b>' : '') + ' ';
      });
      html += '<div class="sn-combo ' + (live[n] ? 'live' : 'dead') + '"><span class="sn-cno">' + n + '</span><div class="sn-cseq">' + seq + '</div></div>';
    });
    combosBox.innerHTML = html;
  }
  function currentBlank(p){
    for (var i=0;i<ORDER.length;i++){ if(!p[ORDER[i]]) return ORDER[i]; }
    return null;
  }
  var ORDER_ALL = Object.keys(COMBOS['1'] || {});
  function render(){
    var p = picks();
    renderCombos(p);
    var live = liveNums(p);
    remainBox.innerHTML = '残っている組合せ番号：<strong>' + live.join('・') + '</strong>（' + live.length + ' 件）';
    var cb = currentBlank(p);
    var done = Object.keys(p).length;
    var total = ORDER.length;
    area.querySelectorAll('.ox-row').forEach(function(r){
      r.classList.toggle('sn-current', !!cb && r.getAttribute('data-stmt') === cb);
    });
    var h = '';
    if (cb){
      h += '<p class="sn-progress">STEP ' + (done+1) + ' / ' + total + '　─　次は空欄 ' + CIRC[cb] + ' を、下の一問一答で回答</p>';
      h += '<div class="sn-tip"><span class="sn-tip-h">💡 コツ</span><span class="sn-tip-b">' + TIP[cb] + '</span></div>';
      h += '<p class="sn-step-loc">↓ 下の一問一答の ' + CIRC[cb] + ' で語句を選ぶと、ここの候補が絞られます。</p>';
    } else if (live.length === 1){
      h += '<div class="sn-result"><div class="sn-big">残った組合せは ' + live[0] + '</div>全部そろいました。下の「解答を表示」で採点。番号でなく、いま辿った検討の筋道（どの空欄で立場と理由が定まり、どこが確認だったか）ごと身につけよう。</div>';
    } else {
      h += '<div class="sn-result' + (live.length===0?' miss':'') + '">' + (live.length===0 ? '選んだ語句が互いに矛盾して残る番号がありません。どこかを選び直そう。' : '残り：' + live.join('・') + '。あと一歩、残りの空欄を決めよう。') + '</div>';
    }
    stage.innerHTML = h;
  }
  area.addEventListener('click', function(e){ if (e.target.closest('.ox-btn') || e.target.closest('.reveal-answer-btn')) setTimeout(render, 0); }, false);
  document.body.classList.add('snav-on');
  render();
})();
</script>
'''

# ---- ox-grid の1空欄行テンプレ（350_lex 逐語構造） ----
ROW_TMPL = ('        <div class="ox-row mc" data-stmt="__B__">\n'
  '          <span class="ox-label">__CIRC__</span>\n'
  '          <div class="ox-main">\n'
  '            <p class="ox-q">__Q__</p>\n'
  '          <span class="ox-btn-group mc">\n'
  '__OPTS__'
  '          </span>\n'
  '            <p class="ox-core-wrap"><span class="ox-core-tag">論点のコア</span><span class="ox-stmt">__CORE__</span></p>\n'
  '          </div>\n'
  '        </div>\n')
OPT_TMPL = ('            <button class="answer-slot ox-btn" type="button" data-value="__K__"><span class="mc-key">__K__</span>__T__</button>\n')

CIRC = {'1':'①','2':'②','3':'③','4':'④','5':'⑤','6':'⑥','7':'⑦','8':'⑧','9':'⑨'}

def find_block(html, start_tag='<div class="answer-area"'):
    i = html.find(start_tag)
    depth = 0
    for m in re.finditer(r'<(/?)div\b', html[i:], re.I):
        if m.group(1) == '': depth += 1
        else:
            depth -= 1
            if depth == 0:
                j = i + m.end(); gt = html.find('>', j); return i, gt+1
    raise SystemExit("close not found")

def answer_num(combos, official):
    """official(各空欄正解letter) に一致する組合せ番号を返す。"""
    for n in combos:
        if all(combos[n].get(b) == official.get(b) for b in official):
            return n
    raise SystemExit("answer_num: 正解組合せが COMBOS に無い（official/combos 不整合）")

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

    combos   = spec['combos']
    official = spec['official']
    order    = spec['order']
    blanks   = spec['blanks']
    ans      = answer_num(combos, official)
    blank_ids = list(blanks.keys())

    expl = re.search(r'data-explanation="([^"]*)"', area, re.S).group(1)
    # answer-area の直前にある【解答】h3（あれば）を捕捉＝置換領域に含める（重複防止）。
    # 無い問（例 119：answer-area が【組合せ】h3 直後）もあるため optional 扱い。
    pre = src[:a0]
    head_m = re.search(r'<h3[^>]*>【解答】[^<]*</h3>\s*$', pre)
    head_ox = head_m.group(0) if head_m else None
    HEAD_NEW = ('<h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; '
      'margin:26px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); '
      'font-family:var(--font-display);">__TXT__</h3>\n\n    ')

    # ===== (1) Lexia 用 _lex =====
    shutil.copyfile(src_path, lex_path)
    lex = open(lex_path, encoding="utf-8").read()
    # 1c. ox-grid を空欄単位へ置換（最初に行う＝以降の挿入でオフセットがずれないよう、
    #     置換→再検索の順で確定的に処理する）
    rows = ''
    for b in blank_ids:
        bl = blanks[b]
        opts = ''.join(OPT_TMPL.replace('__K__', o['k']).replace('__T__', o['t']) for o in bl['opts'])
        rows += (ROW_TMPL.replace('__B__', b).replace('__CIRC__', CIRC[b])
                 .replace('__Q__', bl['q']).replace('__OPTS__', opts).replace('__CORE__', bl['core']))
    # 1d. ox-grid 内容（answer-instruction 〜 answer-ox-grid 〜 final-answer）を再構築
    cv = ''.join(official[b] for b in blank_ids)
    akey = ','.join(f"{b}:{official[b]}" for b in blank_ids)
    verdict_rows = ''
    for b in blank_ids:
        bl = blanks[b]
        verdict_rows += (f'            <tr data-stmt="{b}"><td style="text-align:center;font-weight:700;">{CIRC[b]}</td>'
            f'<td style="text-align:center;font-weight:700;">{bl["label"]}</td><td>{bl["core"]}</td></tr>\n')
    lex_area = (
      f'<div class="answer-area" id="answer-area" data-correct-value="{cv}" data-answer-type="ox-grid" data-explanation="{expl}">\n'
      f'      <p class="answer-instruction">上の解法ナビが示す順に、各空欄{CIRC[blank_ids[0]]}〜{CIRC[blank_ids[-1]]}の語句を1つずつ選んでください（選ぶたびに上の組合せ候補が絞られます）。全空欄を選んだら「解答を表示」で採点。採点後、各行に<strong>論点のコア（転用可能な法理）</strong>が展開されます。復習プールにはこの法理命題だけが入ります。</p>\n\n'
      f'      <div class="answer-ox-grid">\n{rows}      </div>\n\n'
      '      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>\n'
      '      <div id="answer-feedback" hidden=""></div>\n\n'
      '      <div class="final-answer" hidden="">\n'
      f'        <p class="fa-summary"><strong>正解</strong>　各空欄の正解と<strong>論点のコア（転用可能な法理）</strong>は下表のとおり。組合せ番号でなく、各空欄の法理で判定する。下表が学習資産。</p>\n'
      f'        <table class="statement-verdict-table" data-answer-key="{akey}">\n'
      '          <thead><tr><th style="width:3em;">空欄</th><th style="width:8em;">正解</th><th>登場した論点のコア（転用可能な法理）</th></tr></thead>\n'
      f'          <tbody>\n{verdict_rows}          </tbody>\n'
      '        </table>\n'
      '      </div>')
    la0, la1 = find_block(lex)            # lex 上で answer-area を再検索（src と同位置だが安全に再取得）
    # 旧【解答】h3 があれば置換領域に含めて除去（重複防止）
    lhead = re.search(r'<h3[^>]*>【解答】[^<]*</h3>\s*$', lex[:la0])
    cut0 = lhead.start() if lhead else la0
    # solve-nav SHELL ＋ 新しい【解答】h3 を answer-area の直前に置く
    shell = NAV_SHELL.replace('__SUB__', spec['sub'])
    head_new = HEAD_NEW.replace('__TXT__', '【解答】── 上の解法ナビの順に、各空欄の語句を1つずつ選ぶ（全部選んだら「解答を表示」）')
    lex = lex[:cut0] + shell + head_new + lex_area + lex[la1:]
    # 1a. CSS 注入（</style> 直前）
    k = lex.rfind('</style>')
    lex = lex[:k] + "\n/* === 解法ナビ（Lexia用・常時表示） === */\n" + CSS + "\n" + lex[k:]
    # 1e. SCRIPT-COMBO（ガイド専念型）を </body> 直前へ
    js = (NAV_JS_TMPL.replace('__COMBOS__', json.dumps(combos, ensure_ascii=False))
                     .replace('__ORDER__', json.dumps(order, ensure_ascii=False))
                     .replace('__TIP__', json.dumps(spec['tip'], ensure_ascii=False)))
    bclose = lex.rfind('</body>')
    lex = lex[:bclose] + js + "\n" + lex[bclose:]
    open(lex_path, "w", encoding="utf-8").write(lex)

    # ===== (2) 公式（単一5択・組合せ番号 single） =====
    nopt = len(combos)
    instr = f'①〜{CIRC[blank_ids[-1]]}に入る語句の正しい組合せを、上記【組合せ】の 1〜{nopt} から1つ選び、「解答を表示」を押してください。'
    head_official = HEAD_NEW.replace('__TXT__', '【解答】── 正しい組合せ番号を 1〜'+str(nopt)+' から1つ選ぶ')
    slots = ''.join('        <button class="answer-slot" type="button" data-value="%s">%s</button>\n'%(n,n) for n in combos)
    official_area = ('<div class="answer-area" id="answer-area" data-correct-value="'+ans+'" '
      'data-answer-type="single" data-explanation="'+expl+'">\n'
      '      <p class="answer-instruction">'+instr+'</p>\n\n'
      '      <div class="answer-row">\n'+slots+'      </div>\n\n'
      '      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>\n'
      '      <div id="answer-feedback" hidden=""></div>\n\n'
      '      <div class="final-answer" hidden="">\n'
      '        <p class="fa-summary">'+spec['summary']+'</p>\n'
      '      </div>')
    # 旧【解答】h3（あれば）を含めて answer-area を差し替え（重複防止）
    cut0 = head_m.start() if head_m else a0
    off = src[:cut0] + head_official + official_area + src[a1:]
    open(src_path, "w", encoding="utf-8").write(off)
    print(f"刑TX{num}: ans=組合せ{ans}  cv={cv}  lex={len(lex)}B official={len(off)}B")

# ============================= 各問の問題固有データ =============================
COMBO_SPECS = {
 # ----- 114 責任能力・鑑定意見の扱い（混合的方法／法律判断）-----
 "114": {
   "sub": "検討順に、下の一問一答で各空欄の語句を1つずつ選ぶ → 矛盾する組合せ番号が消えて、残った番号にたどり着く。要所で解法のコツも出ます。",
   "combos": {
     "1":{"1":"a","2":"d","3":"e","4":"g","5":"i"},
     "2":{"1":"a","2":"d","3":"f","4":"h","5":"j"},
     "3":{"1":"b","2":"c","3":"e","4":"g","5":"j"},
     "4":{"1":"b","2":"c","3":"f","4":"g","5":"i"},
     "5":{"1":"b","2":"d","3":"e","4":"h","5":"i"}},
   "official": {"1":"b","2":"c","3":"e","4":"g","5":"j"},
   "order": ["1","2","5","3","4"],
   "tip": {
     "1":"不可知論で『分からない』対象を読む。精神医学は<b>生物学的要素（精神障害の有無・程度）</b>を診断できるが、それが弁識・制御能力に与えた影響＝<b>心理学的要素</b>は知り得ないと説く。Aが『分からない』とするのは心理学的要素。",
     "2":"心神喪失の定義の連結詞。判例（大判昭6.12.3）は弁識能力<b>『又は』</b>制御能力の欠如＝いずれか一方を欠けば足りる（選択的）。『かつ』は両能力欠如を要する過度に厳格な読み。",
     "5":"該当性は誰が決めるか。心神喪失・耗弱に当たるかは<b>法律判断＝裁判所の専権</b>（最決昭58.9.13・最判平20.4.25）。事実判断とすると鑑定拘束に傾く。",
     "3":"診断の性質。生物学的要素・その影響の<b>診断は『臨床精神医学の本分』</b>（最判平20.4.25）。『非医学的知見も加味した総合的判断』は裁判所が下す最終判断の性質で、診断そのものの性質ではない。",
     "4":"鑑定意見の扱い。診断が専門医の本分だからこそ、鑑定意見は<b>『採用し得ない合理的事情がない限り尊重』</b>（g）。『従って』（h）は<b>拘束</b>を意味し、⑤の『裁判所の専権』と正面から矛盾する。"},
   "blanks": {
     "1":{"q":"不可知論で『分からない』とされる対象は、生物学的要素か、心理学的要素か？",
          "label":"心理学的要素（b）",
          "opts":[{"k":"a","t":"生物学的要素"},{"k":"b","t":"心理学的要素"}],
          "core":"責任能力は混合的方法（生物学的要素＝精神の障害／心理学的要素＝弁識能力・制御能力）で判断する。不可知論は、精神医学が診断し得るのは生物学的要素であって、それが弁識・制御能力（心理学的要素）に与えた影響は知り得ないと説く。"},
     "2":{"q":"心神喪失の定義における弁識能力と制御能力の連結は、『又は』か、『かつ』か？",
          "label":"又は＝選択的（c）",
          "opts":[{"k":"c","t":"又は"},{"k":"d","t":"かつ"}],
          "core":"心神喪失とは、精神の障害により、事物の理非善悪を弁識する能力が欠如し、又はその弁識に従って行動する能力が欠如している状態をいう（大判昭6.12.3）。弁識能力・制御能力のいずれか一方を欠けば足りる（選択的）。"},
     "3":{"q":"生物学的要素及びその心理学的要素への影響の『診断』の性質は？",
          "label":"臨床精神医学の本分（e）",
          "opts":[{"k":"e","t":"臨床精神医学の本分"},{"k":"f","t":"非医学的知見も加味した総合的判断"}],
          "core":"生物学的要素である精神障害の有無・程度及びこれが心理学的要素に与えた影響の有無・程度の診断は、臨床精神医学の本分である（最判平20.4.25）。総合的判断は裁判所が下す最終的な該当性判断の性質であって、診断そのものの性質ではない。"},
     "4":{"q":"専門医の鑑定意見が証拠となっている場合、裁判所はこれをどう扱うべきか？",
          "label":"合理的事情なき限り尊重（g）",
          "opts":[{"k":"g","t":"採用し得ない合理的な事情が認められない限り、その意見を十分に尊重して"},{"k":"h","t":"生物学的要素の判断に関する限り、その意見に従って"}],
          "core":"専門家たる精神医学者の鑑定意見が証拠となっている場合、これを採用し得ない合理的な事情が認められるのでない限り、その意見を十分に尊重して認定すべきである（最判平20.4.25）。『従う＝拘束』ではなく『尊重』にとどまる。"},
     "5":{"q":"心神喪失・心神耗弱に該当するかの判断は、事実判断か、法律判断か？",
          "label":"法律判断＝裁判所の専権（j）",
          "opts":[{"k":"i","t":"事実判断"},{"k":"j","t":"法律判断"}],
          "core":"被告人の精神状態が心神喪失・心神耗弱に該当するかは法律判断であって裁判所の専権事項であり、その前提となる生物学的要素・心理学的要素の評価も究極的には裁判所の判断に委ねられる（最決昭58.9.13・最判平20.4.25）。"}},
   "summary":"<strong>正解 3</strong>　①b ②c ③e ④g ⑤j。責任能力は混合的方法で判断する。①不可知論で『分からない』対象＝心理学的要素（b）／②心神喪失の定義は『又は』（c・選択的・大判昭6.12.3）／③診断は臨床精神医学の本分（e・最判平20.4.25）／④鑑定意見は採用し得ない合理的事情なき限り尊重（g・拘束ではない）／⑤該当性は法律判断で裁判所の専権（j・最決昭58.9.13）。番号でなく各空欄の法理で判定する。"},

 # ----- 119 原因において自由な行為（共通H23-4）-----
 "119": {
   "sub": "検討順に、下の一問一答で各空欄の語句を1つずつ選ぶ → 矛盾する組合せ番号が消えて、残った番号にたどり着く。要所で解法のコツも出ます。",
   "combos": {
     "1":{"1":"a","2":"c","3":"e","4":"g","5":"j","6":"l","7":"m"},
     "2":{"1":"a","2":"d","3":"f","4":"g","5":"i","6":"l","7":"n"},
     "3":{"1":"b","2":"c","3":"f","4":"g","5":"j","6":"l","7":"m"},
     "4":{"1":"b","2":"c","3":"f","4":"h","5":"i","6":"k","7":"n"},
     "5":{"1":"b","2":"d","3":"e","4":"g","5":"j","6":"k","7":"m"}},
   "official": {"1":"b","2":"c","3":"f","4":"g","5":"j","6":"l","7":"m"},
   "order": ["1","2","3","4","5","6","7"],
   "tip": {
     "1":"事例の罪名を確定。酩酊して正常な運転が困難な状態で人を死亡させた行為は<b>危険運転致死</b>（自動車運転死傷行為処罰法2条1号）。業務上過失致死（a）は正常運転困難状態の危険運転には当たらない。",
     "2":"運転開始時に是非善悪の識別・制御能力を失った状態は心神喪失＝<b>責任能力</b>が欠ける（c）。行為能力（d）は私法上の概念で刑法の責任要件ではない。",
     "3":"責任無能力状態で結果を実現した場合の可罰性を根拠づける理論＝<b>原因において自由な行為</b>（f）。『原因において違法な行為』（e）という概念は存在しない。",
     "4":"責任能力は実行行為時に存在することを要するとする原則＝<b>行為と責任の同時存在の原則</b>（g）。罪刑法定主義（h）は別系統で無関係。",
     "5":"責任無能力の自分を道具として利用すると捉え、同時存在の原則を維持する構成要件モデル＝<b>間接正犯</b>類似説（j）。共謀共同正犯（i）は共犯論で場違い。",
     "6":"道具性が問題となるのは完全な責任無能力ではない限定責任能力＝<b>心神耗弱</b>（l）。心神喪失（k）まで至ると道具性の問題はむしろ生じにくい。",
     "7":"判例（最決昭43.2.27）は心神耗弱状態でも飲酒の際に運転の意思が認められれば39条2項の減軽をすべきでないとして理論を<b>適用している</b>（m）。"},
   "blanks": {
     "1":{"q":"本事例の構成要件上の罪名は？",
          "label":"危険運転致死（b）",
          "opts":[{"k":"a","t":"業務上過失致死"},{"k":"b","t":"危険運転致死"}],
          "core":"酩酊により正常な運転が困難な状態で自動車を走行させ人を死亡させた行為は、危険運転致死罪（自動車の運転により人を死傷させる行為等の処罰に関する法律2条1号）に当たる。"},
     "2":{"q":"運転開始時に欠けていたのは何の能力か？",
          "label":"責任能力（c）",
          "opts":[{"k":"c","t":"責任能力"},{"k":"d","t":"行為能力"}],
          "core":"是非善悪の識別能力及びその識別に従って行動を制御する能力を失った状態（心神喪失）では責任能力が欠ける。行為能力は私法上の概念であって刑法の責任要件ではない。"},
     "3":{"q":"責任無能力状態で結果を実現した者の可罰性を根拠づける理論は？",
          "label":"原因において自由な行為（f）",
          "opts":[{"k":"e","t":"原因において違法な行為"},{"k":"f","t":"原因において自由な行為"}],
          "core":"原因において自由な行為とは、結果惹起行為の時点で責任能力を欠いても、その原因となった行為の時点で完全な責任能力があれば完全な責任を問い得るとする理論をいう。"},
     "4":{"q":"原因において自由な行為が修正・例外を論じる対象となる原則は？",
          "label":"行為と責任の同時存在の原則（g）",
          "opts":[{"k":"g","t":"行為と責任の同時存在の原則"},{"k":"h","t":"罪刑法定主義"}],
          "core":"行為と責任の同時存在の原則とは、責任非難の対象たる実行行為の時点に責任能力が存在することを要するとする原則をいう。原因において自由な行為はこの原則の維持・例外をめぐって構成が分かれる。"},
     "5":{"q":"同時存在の原則を維持しつつ責任無能力の自分を道具として利用すると捉える構成は、何と同様に考えるか？",
          "label":"間接正犯（j）",
          "opts":[{"k":"i","t":"共謀共同正犯"},{"k":"j","t":"間接正犯"}],
          "core":"構成要件モデル（同時存在の原則を維持する立場）は、責任無能力状態の自己を道具として利用したと捉え、他人を道具とする間接正犯と同様に原因行為に実行行為性を認める。"},
     "6":{"q":"結果惹起時に『道具といえるか』が問題となるのは、どの責任状態の場合か？",
          "label":"心神耗弱（l）",
          "opts":[{"k":"k","t":"心神喪失"},{"k":"l","t":"心神耗弱"}],
          "core":"心神耗弱（限定責任能力）の場合は意思による制御の余地が残るため、結果惹起時の行為者を完全な『道具』と評価できるかが問題となる。完全な責任無能力（心神喪失）ではこの問題は生じにくい。"},
     "7":{"q":"判例は心神耗弱の場合に原因において自由な行為の理論を適用しているか、していないか？",
          "label":"適用している（m）",
          "opts":[{"k":"m","t":"適用している"},{"k":"n","t":"適用していない"}],
          "core":"判例（最決昭43.2.27）は、心神耗弱状態であっても、飲酒の際に運転の意思が認められる場合には39条2項による刑の減軽をすべきでないとして、原因において自由な行為の理論を適用している。"}},
   "summary":"<strong>正解 3</strong>　①b ②c ③f ④g ⑤j ⑥l ⑦m。①酩酊運転致死＝危険運転致死（b）／②欠けるのは責任能力（c）／③可罰性の根拠＝原因において自由な行為（f）／④維持・例外の対象＝行為と責任の同時存在の原則（g）／⑤道具利用構成は間接正犯類似（j）／⑥道具性が問題となるのは心神耗弱（l）／⑦判例は心神耗弱に理論を適用している（m・最決昭43.2.27）。番号でなく各空欄の法理で判定する。"},
}

if __name__ == '__main__':
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(COMBO_SPECS.keys())
    for num in targets:
        if num not in COMBO_SPECS:
            print(f"刑TX{num}: COMBO_SPECS 未定義 → skip"); continue
        build(num, COMBO_SPECS[num])
    print("DONE")
