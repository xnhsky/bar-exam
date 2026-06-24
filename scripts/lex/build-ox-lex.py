# -*- coding: utf-8 -*-
"""TX 二系統化・汎用ビルダ（パイロット 5 問）。
   各問の 000_TX ox-grid を基盤に
     - ux/000_TX/001_刑法/刑TXNNN_lex.html = ox-grid + 解法ナビ（○×型・常時表示・両モード対応）
     - 000_TX/001_刑法/刑TXNNN.html        = 公式（単一5択／正しい・誤っているを自動判定）
   mode は data-correct-value の ○/× 個数から自動判定（○1個→correct／×1個→incorrect）。
"""
import re, shutil, os, json

# ROOT はスクリプト位置（<repo>/scripts/lex/build-ox-lex.py）から解決＝ローカル/リモート両対応。
# 旧: ROOT = "/home/user/bar-exam"（リモート固定でローカル不可）
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBJ = "outputs/000_TX/001_刑法"
UXD  = "outputs/ux/000_TX/001_刑法"
NAV_TEMPLATE = os.path.join(ROOT, UXD, "刑TX350_lex.html")

# ---- 解法ナビ CSS（350_lex から流用） ----
nav_src = open(NAV_TEMPLATE, encoding="utf-8").read()
CSS = re.search(r'(/\* 解法ナビは「裏ルート」.*?\.cp-hint\{[^}]*\})', nav_src, re.S).group(1)

# ---- 解法ナビ JS テンプレート（両モード対応・プレースホルダ差替） ----
NAV_JS_TMPL = r'''<script>
/* 解法ナビ（○×型・両モード）：各記述を順に○×判定 → 5択から外れて残った番号へ。
   mode=correct=「正しいものはどれか」／incorrect=「誤っているものはどれか」。
   最後に「確定」で ox-grid を裏で記入して採点（記録は ox-grid 一本）。 */
(function(){
  var MODE = '__MODE__';                 // 'correct' | 'incorrect'
  var STMT = __STMT__;
  var ORDER = __ORDER__;
  var root = document.getElementById('solve-nav');
  var area = document.querySelector('.answer-area[data-answer-type="ox-grid"]');
  if (!root || !area) return;
  var combosBox = document.getElementById('sn-combos');
  var remainBox = document.getElementById('sn-remain');
  var stage = document.getElementById('sn-stage');
  var TARGET = (MODE === 'correct') ? '○' : '×';   // 答えに残る記述の判定
  var DEAD   = (MODE === 'correct') ? '×' : '○';   // 付けると候補が消える判定
  var CAND   = (MODE === 'correct') ? '「正しい」' : '「誤っている」';
  var ANSLBL = (MODE === 'correct') ? '正しいのは記述 ' : '誤っているのは記述 ';

  var picks = {};   // stmt -> '○'|'×'
  var idx = 0;

  function correctNum(){
    var cv = (area.getAttribute('data-correct-value')||'').replace(/[^○×]/g,'');
    var i = cv.indexOf(TARGET);
    return i >= 0 ? String(i+1) : '1';
  }
  function liveNums(){
    var out = [];
    ['1','2','3','4','5'].forEach(function(n){ if (picks[n] !== DEAD) out.push(n); });
    return out;
  }
  function renderCombos(winNum){
    var html = '';
    ['1','2','3','4','5'].forEach(function(n){
      var st = picks[n]; var mark = st ? st : '？';
      var cls = 'sn-combo ';
      if (winNum === n) cls += 'win';
      else if (st === DEAD) cls += 'dead';
      else cls += 'live';
      html += '<div class="'+cls+'"><span class="sn-cno">'+n+'</span><div class="sn-cseq">記述'+n+'<br><b>'+mark+'</b></div></div>';
    });
    combosBox.innerHTML = html;
  }
  function trailHTML(){
    if (!Object.keys(picks).length) return '';
    var t = '<div class="sn-trail">これまでの判定：';
    ORDER.forEach(function(b){ if (picks[b]) t += '<span class="sn-pick">記述'+b+' = '+picks[b]+'</span>'; });
    return t + '</div>';
  }
  function renderStep(){
    renderCombos(null);
    var live = liveNums();
    remainBox.innerHTML = CAND+'候補に残る番号：<strong>'+live.join('・')+'</strong>（'+live.length+' 件）';
    if (idx >= ORDER.length){ return finish(); }
    var b = ORDER[idx]; var s = STMT[b];
    var h = '';
    h += '<p class="sn-progress">STEP '+(idx+1)+' / '+ORDER.length+'　─　記述 '+b+' を判定</p>';
    h += '<p class="sn-step-q">'+s.q+'</p>';
    h += '<div class="sn-tip"><span class="sn-tip-h">\U0001F4A1 コツ</span>'+s.tip+'</div>';
    h += '<div class="sn-opts">';
    h += '<button type="button" class="sn-opt" data-stmt="'+b+'" data-v="○"><span class="sn-key">○</span><span>正しい</span></button>';
    h += '<button type="button" class="sn-opt" data-stmt="'+b+'" data-v="×"><span class="sn-key">×</span><span>誤り</span></button>';
    h += '</div>';
    h += trailHTML();
    h += '<div class="sn-actions"><button type="button" class="sn-btn ghost" id="sn-reset">最初からやり直す</button></div>';
    stage.innerHTML = h;
  }
  function onPick(b, v){
    picks[b] = v; var note = STMT[b].note; idx += 1;
    renderStep();
    var fb = document.createElement('div');
    fb.className = 'sn-feedback' + (v === DEAD ? ' miss' : '');
    fb.innerHTML = '<strong>記述'+b+' = '+v+'</strong>　'+note;
    stage.insertBefore(fb, stage.firstChild);
  }
  function finish(){
    var live = liveNums(); var ansn = correctNum(); var h = '';
    if (live.length === 1){
      renderCombos(live[0]);
      var ok = (live[0] === ansn);
      h += '<div class="sn-result'+(ok?'':' miss')+'"><div class="sn-big">残った番号は '+live[0]+'</div>'+
        (ok ? '番号を暗記するのではなく、いま辿った判別の筋道ごと身につけよう。'
            : 'ただし基準では'+ANSLBL+ansn+'。下の解説と ox-grid で見直そう。')+'</div>';
    } else {
      h += '<div class="sn-result">候補が複数（'+live.join('・')+'）残っています。各記述の法理を確かめて１つに絞ろう。</div>';
    }
    h += '<div class="sn-actions"><button type="button" class="sn-btn primary" id="sn-apply">この判定で確定（採点）</button>'+
         '<button type="button" class="sn-btn ghost" id="sn-reset">最初からやり直す</button></div>';
    stage.innerHTML = h + trailHTML();
  }
  function commitAnswer(){
    if (area.classList.contains('answered')) return;
    ['1','2','3','4','5'].forEach(function(b){
      var v = picks[b]; if (!v) return;
      var row = area.querySelector('.ox-row[data-stmt="'+b+'"]');
      if (!row) return;
      var btn = row.querySelector('.ox-btn[data-value="'+v+'"]');
      if (btn) btn.click();
    });
    var rv = area.querySelector('.reveal-answer-btn');
    if (rv && !rv.disabled) rv.click();
    var ansn = correctNum(); var mine = liveNums();
    var ok = (mine.length === 1 && mine[0] === ansn);
    var h = '<div class="sn-result'+(ok?'':' miss')+'">'+
      (ok ? '<div class="sn-big">✓ 正解（'+ANSLBL+ansn+'）</div>下の解説で論点のコアを確認しよう。'
          : '<div class="sn-big">✗ 不正解</div>'+ANSLBL+ansn+'。下の解説と ox-grid で外した記述を確認しよう。')+
      '</div><div class="sn-actions"><button type="button" class="sn-btn ghost" id="sn-reset">もう一度やる</button></div>' + trailHTML();
    stage.innerHTML = h; renderCombos(ansn);
    var fa = area.querySelector('.final-answer');
    if (fa) fa.scrollIntoView({ behavior:'smooth', block:'start' });
  }
  function restart(){ picks = {}; idx = 0; renderStep(); }
  root.addEventListener('click', function(e){
    var t = e.target; if (!t || !t.closest) return;
    var opt = t.closest('.sn-opt');
    if (opt){ onPick(opt.getAttribute('data-stmt'), opt.getAttribute('data-v')); return; }
    if (t.closest('#sn-reset')){ restart(); return; }
    if (t.closest('#sn-apply')){ commitAnswer(); return; }
  }, false);
  document.body.classList.add('snav-on');
  renderStep();
})();
</script>
'''

NAV_HTML_TMPL = ('    <div class="solve-nav" id="solve-nav">\n'
  '      <div class="sn-head">\U0001F4D0 解法ナビ\n'
  '        <span class="sn-sub">__SUB__</span>\n'
  '      </div>\n'
  '      <div class="sn-body">\n'
  '        <div class="sn-combos" id="sn-combos"></div>\n'
  '        <p class="sn-remain" id="sn-remain"></p>\n'
  '        <div id="sn-stage"></div>\n'
  '      </div>\n'
  '    </div>\n\n')

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

def build(num, spec):
    src_path = os.path.join(ROOT, SUBJ, f"刑TX{num}.html")
    lex_path = os.path.join(ROOT, UXD, f"刑TX{num}_lex.html")
    src = open(src_path, encoding="utf-8").read()
    a0, a1 = find_block(src)
    area = src[a0:a1]
    # 冪等ガード：公式が既に単一5択（single/multi）へ変換済みなら再変換しない。
    # 全SPECSを残したまま再実行でき、未変換（ox-grid）の問だけを処理する。
    at = re.search(r'data-answer-type="([^"]*)"', area)
    if at and at.group(1) != 'ox-grid':
        print(f"刑TX{num}: 変換済み（data-answer-type={at.group(1)}）→ skip")
        return
    expl = re.search(r'data-explanation="([^"]*)"', area).group(1)
    cv = re.search(r'data-correct-value="([^"]*)"', area).group(1)
    seq = re.sub(r'[^○×]', '', cv)
    mode = 'correct' if seq.count('○') == 1 else ('incorrect' if seq.count('×') == 1 else None)
    if not mode: raise SystemExit(f"{num}: mode 判定不能 cv={cv}")
    target = '○' if mode == 'correct' else '×'
    ans = str(seq.index(target) + 1)
    head_ox = re.search(r'<h3[^>]*>【解答】[^<]*</h3>', src).group(0)

    # ---- (1) Lexia 用 ----
    shutil.copyfile(src_path, lex_path)
    lex = open(lex_path, encoding="utf-8").read()
    k = lex.rfind('</style>')
    lex = lex[:k] + "\n/* === 解法ナビ（Lexia用・常時表示） === */\n" + CSS + "\n" + lex[k:]
    nav_html = NAV_HTML_TMPL.replace('__SUB__', spec['sub'])
    hi = lex.find(head_ox)
    lex = lex[:hi] + nav_html + lex[hi:]
    stmt_json = json.dumps(spec['stmt'], ensure_ascii=False)
    js = (NAV_JS_TMPL.replace('__MODE__', mode)
                     .replace('__STMT__', stmt_json)
                     .replace('__ORDER__', json.dumps(spec['order'])))
    bclose = lex.rfind('</body>')
    lex = lex[:bclose] + js + "\n" + lex[bclose:]
    open(lex_path, "w", encoding="utf-8").write(lex)

    # ---- (2) 公式（単一5択） ----
    if mode == 'correct':
        head_txt = '【解答】── 記述1〜5のうち正しいものを1つ選ぶ'
        instr = '記述1〜5のうち正しいものを1つ選び、「解答を表示」を押してください。'
    else:
        head_txt = '【解答】── 記述1〜5のうち誤っているものを1つ選ぶ'
        instr = '記述1〜5のうち誤っているものを1つ選び、「解答を表示」を押してください。'
    head_official = ('<h3 style="background:transparent; border-left:none; padding:8px 0 4px 0; '
      'margin:26px 0 8px 0; border-bottom:2px dotted var(--border-mid); color:var(--accent); '
      'font-family:var(--font-display);">'+head_txt+'</h3>')
    official_area = ('<div class="answer-area" id="answer-area" data-correct-value="'+ans+'" '
      'data-answer-type="single" data-explanation="'+expl+'">\n'
      '      <p class="answer-instruction">'+instr+'</p>\n\n'
      '      <div class="answer-row">\n'
      + ''.join('        <button class="answer-slot" type="button" data-value="%d">%d</button>\n'%(i,i) for i in range(1,6)) +
      '      </div>\n\n'
      '      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>\n'
      '      <div id="answer-feedback" hidden=""></div>\n\n'
      '      <div class="final-answer" hidden="">\n'
      '        <p class="fa-summary">'+spec['summary']+'</p>\n'
      '      </div>')
    off = src[:a0] + official_area + src[a1:]
    off = off.replace(head_ox, head_official, 1)
    open(src_path, "w", encoding="utf-8").write(off)
    print(f"刑TX{num}: mode={mode} ans={ans}  lex={len(lex)}B official={len(off)}B")

# ===================== 各問の文面（本文・解説に基づき執筆） =====================
SPECS = {
 "001": {"order":["1","2","3","4","5"],
   "sub":"記述を上から順に○×判定 →「正しいものはどれか」の候補から誤りが消え、残った番号へ。要所で判定のコツも出ます。",
   "summary":"<strong>正解 3</strong>　記述3のみが正しい。応報刑論は自由意思に基づく非難を前提とするため、「意思の自由が科学的に証明されていない」という決定論からの批判（記述3）が前提を突く正当な批判となる。記述1は刑罰論史の向きが逆、記述2・4・5はいずれも批判の矛先が<strong>目的刑論</strong>であって応報刑論には妥当しない（矛先の取り違え）。",
   "stmt":{
     "1":{"q":"記述1：累犯増加を契機に応報刑論の支持者が増えた——正しい？","tip":"刑罰論史の<b>方向</b>を確認。累犯増加（応報刑では再犯を防げない）を契機に、むしろ応報刑論が批判を浴び、実証的な<b>目的刑論（近代学派）</b>が台頭した。向きが逆。","note":"× 方向が逆。→ 選択肢1は消える。"},
     "2":{"q":"記述2：「再犯可能性がなければ刑罰を科せない」との批判——応報刑論に妥当？","tip":"その批判は<b>誰に向くか</b>。刑罰を犯罪防止の目的で基礎づける<b>目的刑論（特別予防）</b>への批判であり、応報それ自体で正当化する応報刑論には当たらない（<b>矛先の取り違え</b>）。","note":"× 矛先が目的刑論。→ 選択肢2は消える。"},
     "3":{"q":"記述3：「前提とする意思の自由が科学的に証明されていない」との批判——妥当？","tip":"応報刑論は<b>自由意思に基づく非難</b>を前提にする。<b>決定論</b>からは意思の自由が科学的に証明されていないと批判され、応報刑論の前提そのものを突く正当な批判。","note":"○ 決定論からの批判＝応報刑論の核心を突く。→ 選択肢3が残る。"},
     "4":{"q":"記述4：「罪刑の均衡を失した重罰化を招くおそれ」との批判——応報刑論に妥当？","tip":"応報刑論は<b>行為に均衡した応報</b>を要求し、むしろ重罰化を<b>抑止</b>する側。重罰化のおそれは犯罪防止を急ぐ<b>目的刑論</b>への批判。","note":"× 重罰化批判は目的刑論向け。→ 選択肢4は消える。"},
     "5":{"q":"記述5：「刑罰と保安処分の区別がなくなる」との批判——応報刑論に妥当？","tip":"応報刑論は刑罰（応報）と保安処分（危険性への対処）を区別する<b>二元主義</b>に親和的。区別が失われる批判は危険性に着目する<b>目的刑論（一元主義傾向）</b>に向く。","note":"× 区別喪失批判は目的刑論向け。→ 選択肢5は消える。残るは3。"}}},
 "010": {"order":["1","2","3","4","5"],
   "sub":"各肢の2語が両方とも文脈に合うかを判定 →「正しい組合せはどれか」の候補から誤りが消え、残った番号へ。",
   "summary":"<strong>正解 4</strong>　肢4のみが2語とも正しい（③過失＋⑧一般人）。肢1は⑤（正しくは相当因果関係）、肢2は②（正しくは責任主義）、肢3は⑦（正しくは注意義務）、肢5は⑥（正しくは予見可能性）がそれぞれ誤り。組合せ番号でなく、各語が文脈に合致するかを1語ずつ独立に検証する。",
   "stmt":{
     "1":{"q":"肢1：①因果関係（ク）＋⑤実行行為性（コ）——2語とも正しい？","tip":"2語のうち<b>1語でも</b>合わなければ肢は×。①『基本犯と加重結果の間に求めるもの』＝<b>因果関係</b>で正。だが⑤『学生Aの因果限定基準』は<b>相当因果関係（サ）</b>で、実行行為性ではない。","note":"× ⑤が誤り。→ 肢1は消える。"},
     "2":{"q":"肢2：②法益保護主義（ス）＋④条件関係（ケ）——2語とも正しい？","tip":"④『最も緩やかに解した因果関係概念』＝<b>条件関係</b>で正。だが②『判例批判の根拠原理』は<b>責任主義（シ）</b>で、法益保護主義ではない。","note":"× ②が誤り。→ 肢2は消える。"},
     "3":{"q":"肢3：②責任主義（シ）＋⑦故意（ア）——2語とも正しい？","tip":"②『判例批判の根拠』＝<b>責任主義</b>で正。だが⑦『予見可能性を前提要件とするもの』は<b>注意義務（ウ）</b>で、故意ではない。","note":"× ⑦が誤り。→ 肢3は消える。"},
     "4":{"q":"肢4：③過失（イ）＋⑧一般人（カ）——2語とも正しい？","tip":"③『通説が加重結果に要求する落ち度』＝<b>過失</b>、⑧『予見可能性を客観的に判断する基準』＝<b>一般人</b>。両方とも合致する<b>唯一の肢</b>。","note":"○ 2語とも正しい。→ 肢4が残る。"},
     "5":{"q":"肢5：⑤相当因果関係（サ）＋⑥期待可能性（エ）——2語とも正しい？","tip":"⑤『学生Aの因果限定基準』＝<b>相当因果関係</b>で正。だが⑥『注意義務の前提要件』は<b>予見可能性（オ）</b>で、期待可能性ではない。","note":"× ⑥が誤り。→ 肢5は消える。残るは4。"}}},
 "055": {"order":["1","2","3","4","5"],
   "sub":"記述を上から順に○×判定 →「正しいものはどれか」の候補から誤りが消え、残った番号へ。",
   "summary":"<strong>正解 3</strong>　記述3のみが正しい（重過失＝注意義務違反の程度が著しい）。記述1は区別基準（認容ではなく認識の有無）、記述2は『傷害』の縮小解釈、記述4は刑法にない過失相殺、記述5は監督者の予見可能性を不要とする点でいずれも誤り。",
   "stmt":{
     "1":{"q":"記述1：認識のない／ある過失の区別を『認容』の有無で画する——正しい？","tip":"区別基準は『<b>認識</b>の有無』。結果発生の認識がありつつ認容なしが『認識のある過失』。『認容』で画すのは故意（未必の故意）との境界の話。","note":"× 基準は『認識』であって『認容』ではない。→ 選択肢1は消える。"},
     "2":{"q":"記述2：軽微な結果なら業務上過失傷害は不成立で過失傷害にとどまる——正しい？","tip":"211条の『傷害』は過失傷害罪（209条）の『傷害』と<b>同一意義</b>。業務上加重の根拠から成立範囲を縮小する理由はない。","note":"× 『傷害』は同義で範囲は縮小しない。→ 選択肢2は消える。"},
     "3":{"q":"記述3：重過失＝注意義務違反の程度が著しい（わずかな注意で予見・回避可能）——正しい？","tip":"重過失は<b>注意義務違反の程度</b>が著しいことを指す（結果の重大性ではない）。定義として正確。","note":"○ 重過失の定義として正確。→ 選択肢3が残る。"},
     "4":{"q":"記述4：過失相殺が適用され、著しい義務違反でも重過失は認められない——正しい？","tip":"刑法に<b>過失相殺は存在しない</b>（民722条2項の制度）。被害者側事情は『信頼の原則』で考慮されるにとどまる。","note":"× 刑法に過失相殺はない。→ 選択肢4は消える。"},
     "5":{"q":"記述5：監督過失には監督者自身の予見可能性は不要——正しい？","tip":"過失責任は<b>個別</b>に判断する。監督者にも<b>監督者自身の</b>予見可能性が必要。直接行為者の予見だけで足りるとはしない。","note":"× 監督者自身の予見可能性が必要。→ 選択肢5は消える。残るは3。"}}},
 "056": {"order":["1","2","3","4","5"],
   "sub":"記述を上から順に○×判定 →「正しいものはどれか」の候補から誤りが消え、残った番号へ。",
   "summary":"<strong>正解 5</strong>　記述5のみが正しい（注意義務は法令に限らず契約・慣習・条理等から確定／最判昭27.6.24）。記述1は監督者の予見可能性、記述2は重過失の定義（結果の重大性）、記述3は信頼の原則の適用範囲、記述4は刑法にない過失相殺でいずれも誤り。",
   "stmt":{
     "1":{"q":"記述1：監督過失は直接行為者の予見可能性で足り、監督者自身の予見可能性は不要——正しい？","tip":"<b>個別責任主義</b>。監督者にも<b>結果発生の予見可能性</b>が必要。直接行為者の予見だけで監督者は罰せない。","note":"× 監督者自身の予見可能性が必要。→ 選択肢1は消える。"},
     "2":{"q":"記述2：重過失＝注意義務違反が著しく、かつ発生した結果が重大なもの——正しい？","tip":"重過失は<b>注意義務違反の程度</b>が著しいこと（117条の2・211条後段）。<b>結果の重大性とは無関係</b>。","note":"× 結果の重大性は要件でない。→ 選択肢2は消える。"},
     "3":{"q":"記述3：信頼の原則は交通事故の過失犯だけに適用される——正しい？","tip":"信頼の原則は<b>チーム医療・工事現場</b>など交通事故以外にも適用される。限定する理由はない。","note":"× 交通事故に限定されない。→ 選択肢3は消える。"},
     "4":{"q":"記述4：相手方に重大な過失があれば過失相殺で刑法上も責任を免れる——正しい？","tip":"民722条2項の<b>過失相殺は刑法上観念されない</b>（大判大11.5.11）。相手の過失で行為者の刑責は消えない。","note":"× 刑法に過失相殺はない。→ 選択肢4は消える。"},
     "5":{"q":"記述5：必要な注意義務は必ずしも法令上の根拠を要しない——正しい？","tip":"注意義務は<b>法令のみならず契約・慣習・条理</b>等から確定される（最判昭27.6.24）。法令上の根拠は必須でない。","note":"○ 注意義務の発生根拠として正確。→ 選択肢5が残る。"}}},
 "057": {"order":["1","2","3","4","5"],
   "sub":"記述を上から順に○×判定 →「誤っているものはどれか」の候補から正しい記述が消え、残った番号へ。",
   "summary":"<strong>正解 5</strong>　記述5のみが誤り。A説（予見義務説）に立っても、結果回避可能性が無ければ条件関係・客観的帰属が否定され結果は帰属しない。結果回避可能性は両説の対立と独立に要求される客観的要件である。記述1〜4は各説の理解・批判として正確。",
   "stmt":{
     "1":{"q":"記述1：A説では信頼の原則を『予見可能性が否定される場面の一類型』と理解できる——正しい？","tip":"A説（予見義務説）の核は<b>予見可能性</b>。信頼の原則が働く場面は予見可能性が否定される類型として整合的に説明できる。位置づけとして正確。","note":"○ A説での信頼の原則の位置づけとして正確。→ 選択肢1は消える。"},
     "2":{"q":"記述2：B説は『過失犯は構成要件・違法でも故意犯と異なる』体系と矛盾しない——正しい？","tip":"B説（回避義務説＝新過失論）は結果回避義務違反を<b>構成要件・違法</b>段階で捉える。故意犯と段階から異なるとする体系と整合。","note":"○ 新過失論の体系として正確。→ 選択肢2は消える。"},
     "3":{"q":"記述3：A説には『予見可能性のみで過失を認めると処罰範囲が広がりすぎる』との批判がある——正しい？","tip":"A説（旧過失論）への<b>典型的批判</b>。予見可能性だけを基準にすると処罰が広がる、と新過失論側から指摘される。","note":"○ A説への批判として正確。→ 選択肢3は消える。"},
     "4":{"q":"記述4：B説には『結果回避義務が行政取締法規に帰着し結果的加重犯化する』との批判がある——正しい？","tip":"B説（新過失論）への<b>典型的批判</b>。回避義務の内容を行政法規に求めると過失犯が事実上の結果責任に傾く、と指摘される。","note":"○ B説への批判として正確。→ 選択肢4は消える。"},
     "5":{"q":"記述5：A説からは結果回避可能性は過失犯の成立に不要となる——正しい？","tip":"<b>ここが誤り</b>。A説でも、義務を尽くしても結果が回避できなければ<b>条件関係／客観的帰属</b>が否定され結果は帰属しない。結果回避可能性は<b>両説と独立</b>に要求される客観的要件。","note":"× A説でも結果回避可能性は必要。→ これが『誤っている記述』＝答え。"}}},
}

for num, spec in SPECS.items():
    build(num, spec)
print("DONE")
