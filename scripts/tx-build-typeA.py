#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tx-build-typeA.py — Type A（議論形式・空欄補充）_lex を「解法ナビ主役・空欄単位記録」へ変換。

刑TX351 で実証した gold 構造を、問題固有データ（JSON）だけ差し替えて任意の Type A 問題へ適用する。
エンジン JS・ox-grid 構造・ox-core-wrap によるネタバレ防止は固定。問題ごとに変わるのは各空欄の
loc/frag/q/tip/opts/ans/core と検討順 order・正解組合せ win・解説 expl のみ。

使い方:
  python scripts/tx-build-typeA.py <CODE> <DATA.json>
    例: python scripts/tx-build-typeA.py 刑TX350 /tmp/typeA-350.json

DATA.json の形:
{
  "order": ["7","3","4","5","1","2","6"],   // 検討順＝一番堅く決まる空欄(アンカー)から
  "win": "1",                                // 全部正しく選んだとき一致する組合せ番号(表示用)
  "expl": "…data-explanation 本文…",         // 各空欄の論点を要約(組合せ番号は結果と明記)
  "blanks": {
     "1": {"loc":"…会話のどこか","frag":"…会話断片(2択を <span class=\\"opt\\">…</span> で)…",
            "q":"…解く前の中立な問い(答えを言わない)…","tip":"…💡決め手(出題意図・論点)…",
            "opts":[{"k":"限定説","t":"延焼の危険に限る(限定説)"},{"k":"非限定説","t":"…"}],
            "ans":"限定説","core":"…論点のコア(記号フリー・自己完結=Lexia記録)…"},
     ...
  }
}
注意: blanks のキーは "1".."N"（空欄①..⑩に対応）。opts は各空欄ちょうど2つ。core は記号フリー
（①②/a〜j を使わない・実体の語句で）。frag/q/tip では会話の語をそのまま使ってよい。
"""
import json, re, sys, os

REPO_ROOT = os.path.abspath(os.environ.get(
    'BAREXAM_PROJECT_ROOT',
    os.path.join(os.path.dirname(__file__), '..')
))

CIRC = {str(i): c for i, c in enumerate('①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮', start=1)}

ENGINE = '''<script>
/* 解法ナビ（Type A・空欄単位／議論・穴埋め）：本文を読み返さず、一番堅く決まる空欄（アンカー）から
   2択を1つずつ判断 → 各空欄の論点（＝転用可能な学習単位）が決まれば正解の組合せが定まる。
   採点・記録は下の ox-grid（空欄単位）一本＝Lexia は外した論点だけを復習プールへ。エンジンは問題横断で固定。 */
(function(){
  var root=document.getElementById('solve-nav');
  var area=document.querySelector('.answer-area[data-answer-type="ox-grid"]');
  if(!root||!area) return;
  var remainBox=document.getElementById('sn-remain');
  var stage=document.getElementById('sn-stage');
  /* ===== 問題固有データ（ビルダが本問値で置換・ここだけ編集）===== */
  var ORDER=__ORDER__;   // 検討順＝アンカー（一番堅く決まる空欄）から
  var WIN="__WIN__";      // 全部正しく選んだとき一致する組合せ番号（表示用）
  var B=__B__;            // { '<空欄>':{loc,frag,q,tip,opts:[{k,t}],ans,core}, … }
  /* ===== 問題固有データ ここまで。以下のエンジンは固定＝編集しない ===== */
  var CC=["","①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩","⑪","⑫","⑬","⑭","⑮"];
  var C={}; Object.keys(B).forEach(function(n){ C[n]=CC[parseInt(n,10)]||n; });
  var ALL=Object.keys(B);
  var picks={},i=0;
  function trail(){var k=Object.keys(picks);if(!k.length)return '';var t='<div class="sn-trail">これまでの判断：';ALL.forEach(function(b){if(picks[b])t+='<span class="sn-pick">'+C[b]+' = '+picks[b]+'</span>';});return t+'</div>';}
  function step(){
    var done=Object.keys(picks).length;
    remainBox.innerHTML='判断した論点：<strong>'+done+' / '+ORDER.length+'</strong>　─　一番堅く決まる空欄（アンカー）から、2択を1つずつ。';
    area.querySelectorAll('.ox-row').forEach(function(r){r.classList.toggle('sn-current', i<ORDER.length && r.getAttribute('data-stmt')===ORDER[i]);});
    if(i>=ORDER.length) return finish();
    var b=ORDER[i],s=B[b],h='';
    h+='<p class="sn-progress">STEP '+(i+1)+' / '+ORDER.length+'　─　空欄 '+C[b]+' を検討'+(i===0?'<span class="sn-anchor-badge">アンカー</span>':'')+'</p>';
    h+='<p class="sn-step-loc">📍 '+s.loc+'</p>';
    h+='<div class="sn-frag">'+s.frag+'</div>';
    h+='<p class="sn-step-q">'+s.q+'</p>';
    h+='<div class="sn-tip"><span class="sn-tip-h">💡 決め手</span><span class="sn-tip-b">'+s.tip+'</span></div>';
    h+='<div class="sn-opts">';
    s.opts.forEach(function(o){h+='<button type="button" class="sn-opt" data-b="'+b+'" data-k="'+o.k+'"><span class="sn-key">'+o.k.charAt(0)+'</span><span>'+o.t+'</span></button>';});
    h+='</div>'+trail();
    h+='<div class="sn-actions"><button type="button" class="sn-btn ghost" id="sn-reset">最初からやり直す</button></div>';
    stage.innerHTML=h;
  }
  function pick(b,k){
    picks[b]=k;i++;var s=B[b],ok=(k===s.ans);
    step();
    var fb=document.createElement('div');fb.className='sn-feedback'+(ok?'':' miss');
    fb.innerHTML='<strong>'+C[b]+'：'+(ok?'✓ これでOK':'✗ 取り違え注意')+'</strong>　'+s.core;
    stage.insertBefore(fb,stage.firstChild);
  }
  function finish(){
    var allRight=ORDER.every(function(b){return picks[b]===B[b].ans;});
    var seq='';ALL.forEach(function(b){if(picks[b])seq+=C[b]+picks[b]+'　';});
    var h='<div class="sn-result'+(allRight?'':' miss')+'"><div class="sn-big">'+(allRight?'全論点クリア':'論点に取り違えあり')+'</div>あなたの判断：'+seq+'<br>'+(allRight?'この配置に一致する正しい組合せは <b>'+WIN+'</b>。番号でなく、各論点の決め手ごと身につけよう。':'下で取り違えた論点を確認しよう。')+'</div>';
    h+='<div class="sn-actions"><button type="button" class="sn-btn primary" id="sn-apply">この判断で確定（採点）</button><button type="button" class="sn-btn ghost" id="sn-reset">やり直す</button></div>'+trail();
    stage.innerHTML=h;
  }
  function commit(){
    if(area.classList.contains('answered')) return;
    ALL.forEach(function(b){
      if(!picks[b])return;
      var v=(picks[b]===B[b].ans)?'○':'×';
      var row=area.querySelector('.ox-row[data-stmt="'+b+'"]');if(!row)return;
      var btn=row.querySelector('.ox-btn[data-value="'+v+'"]');if(btn)btn.click();
    });
    var rv=area.querySelector('.reveal-answer-btn');if(rv&&!rv.disabled)rv.click();
    var allRight=ORDER.every(function(b){return picks[b]===B[b].ans;});
    var h='<div class="sn-result'+(allRight?'':' miss')+'"><div class="sn-big">'+(allRight?'✓ 全論点クリア（正解は組合せ '+WIN+'）':'✗ 取り違えあり')+'</div>下の「論点のコア」で、外した論点を重点復習しよう。</div><div class="sn-actions"><button type="button" class="sn-btn ghost" id="sn-reset">もう一度やる</button></div>'+trail();
    stage.innerHTML=h;
    var fa=area.querySelector('.final-answer');if(fa)fa.scrollIntoView({behavior:'smooth',block:'start'});
  }
  function reset(){picks={};i=0;step();}
  root.addEventListener('click',function(e){
    var t=e.target;if(!t||!t.closest)return;
    var o=t.closest('.sn-opt');if(o){pick(o.getAttribute('data-b'),o.getAttribute('data-k'));return;}
    if(t.closest('#sn-reset')){reset();return;}
    if(t.closest('#sn-apply')){commit();return;}
  },false);
  document.body.classList.add('snav-on');
  step();
  /* 採点せず解説だけ見る：answered を付けず・○×も押さないので Lexia は記録しない（復習プール再判定なし） */
  var pkb=area.querySelector('.peek-explain-btn');
  if(pkb){pkb.addEventListener('click',function(){
    area.classList.add('peek');
    var fa=area.querySelector('.final-answer');if(fa)fa.hidden=false;
    pkb.textContent='📖 解説を表示中（採点していません）';pkb.disabled=true;
    if(fa)fa.scrollIntoView({behavior:'smooth',block:'start'});
  });}
})();
</script>'''

FRAG_CSS = '''/* === 解法ナビ Type A（議論形式・空欄単位）：会話断片ボックス === */
.sn-frag{ margin:0 0 10px; padding:10px 13px; border-radius:9px; background:#fff;
  border:1px dashed var(--border-mid,#ccc); font-size:.9em; line-height:1.85; color:var(--bg-dark,#333); }
.sn-frag .blk{ font-weight:800; color:var(--accent); }
.sn-frag .opt{ font-weight:700; }
.sn-anchor-badge{ display:inline-block; margin-left:6px; padding:1px 8px; border-radius:999px;
  background:var(--accent); color:#fff; font-size:.72em; font-weight:800; }
'''

# 採点せず解説だけ見る（peek）用 CSS。.sn-frag とは独立に注入（既存ファイルにも確実に入れる）。
PEEK_CSS = '''/* 採点せず解説だけ見る（peek）：論点コアと正誤表を表示するが answered にしない＝Lexia 記録なし */
.answer-area.peek .answer-ox-grid .ox-core-wrap{ display:block; }
.peek-explain-btn{ display:inline-block; margin:10px 0 0 8px; padding:9px 16px; border-radius:9px;
  border:1.5px solid var(--accent); background:#fff; color:var(--accent); font-weight:700; font-size:.9em; cursor:pointer; }
.peek-explain-btn:hover{ background:var(--soft,#f3f3f3); }
.peek-explain-btn:disabled{ opacity:.7; cursor:default; }
'''

# 物語解説（読み物）用 CSS。.final-answer 冒頭の .fa-narrative を読みやすい本文体裁にする。
NARR_CSS = '''/* Type A 物語解説（読み物）：問題の流れを一連の文章でコア／テーゼ中心に読ませる */
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
.fa-narrative > p[data-fa-label]::before{ content:attr(data-fa-label); position:relative; top:-31px;
  display:block; box-sizing:border-box; width:fit-content; max-width:min(38em, calc(100% - 8px));
  margin:0 0 -18px 0; padding:5px 15px 6px; text-align:center; text-indent:0;
  color:#fff; background:linear-gradient(180deg,#c8843a,#a8692a); border:1.5px solid rgba(255,255,255,.72);
  border-radius:999px; box-shadow:0 1px 3px rgba(120,80,20,.35); font-size:12.5px; font-weight:500; line-height:1.45;
  letter-spacing:.025em; font-feature-settings:"palt" 0; font-stretch:normal; transform:none;
  white-space:normal; overflow-wrap:break-word; word-break:normal; }
.fa-narrative p:last-child{ margin-bottom:0; }
.fa-narrative b{ color:var(--accent-darker,var(--accent)); font-weight:700; }
'''

# 出題趣旨サマリー用 CSS。.final-answer 最上部の .fa-intent を俯瞰ボックスにする。
INTENT_CSS = '''/* Type A 出題趣旨サマリー：出題者視点でコア・命題／角度／ねらいを俯瞰する */
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


def build(code, data):
    f = os.path.join(REPO_ROOT, 'outputs', 'ux', '000_TX', '001_刑法', f'{code}_lex.html')
    if not os.path.exists(f):
        # 科目フォルダ総当たり
        import glob
        cand = glob.glob(os.path.join(REPO_ROOT, 'outputs', 'ux', '000_TX', '*', f'{code}_lex.html'))
        if not cand:
            raise SystemExit(f'not found: {code}_lex.html')
        f = cand[0]
    h = open(f, encoding='utf-8').read()
    order = data['order']; win = str(data['win']); blanks = data['blanks']
    nums = sorted(blanks.keys(), key=lambda x: int(x))
    N = len(nums)
    expl = data.get('expl', '各空欄の論点を1つずつ判断する。各空欄の論点こそが転用可能な学習単位で、組合せ番号は結果にすぎない。')

    # 物語解説（読み物）── .final-answer 冒頭に置く。記号(①〜/a〜)を使わず、問題の冒頭から
    # 結末までを会話・主張の流れに沿ってコア／テーゼで一本の読み物として説明する。
    # data['narrative'] = {"title": "...", "paras": ["段落1", "段落2", ...]}（段落内 <b> 可）。
    narrative_html = ''
    nar = data.get('narrative')
    if nar:
        ntitle = nar.get('title', 'この問題を物語で読む')
        paras = ''.join(f'        <p>{p}</p>\n' for p in nar.get('paras', []))
        narrative_html = f'''        <div class="fa-narrative">
          <p class="fa-narrative-title">📖 {ntitle}</p>
{paras}        </div>
'''

    # 出題趣旨サマリー（出題者視点の俯瞰）── .final-answer 最上部に置く。
    # data['intent'] = {"core": "問われているコア・命題", "angle": "問われ方（角度）", "aim": "出題のねらい"}。
    intent_html = ''
    intent = data.get('intent')
    if intent:
        rows_i = ''
        for lbl, k in (('問われているコア・命題', 'core'), ('問われ方（角度）', 'angle'), ('出題のねらい', 'aim')):
            v = intent.get(k)
            if v:
                rows_i += f'          <li><span class="fa-intent-label">{lbl}</span><span class="fa-intent-body">{v}</span></li>\n'
        intent_html = f'''        <div class="fa-intent">
          <p class="fa-intent-title">🎯 出題趣旨 ── この問題は何を試しているか</p>
          <ul class="fa-intent-list">
{rows_i}          </ul>
        </div>
'''

    rows = ''
    for n in nums:
        rows += f'''        <div class="ox-row mc" data-stmt="{n}">
          <span class="ox-label">{CIRC[n]}</span>
          <div class="ox-main">
            <p class="ox-q">{blanks[n]["q"]}</p>
            <div class="ox-core-wrap"><span class="ox-core-tag">🔑 論点のコア</span><span class="ox-stmt">{blanks[n]["core"]}</span></div>
          </div>
          <span class="ox-btn-group">
            <button class="answer-slot ox-btn" type="button" data-value="○">○</button>
            <button class="answer-slot ox-btn" type="button" data-value="×">×</button>
          </span>
        </div>
'''
    verdict = ''
    for n in nums:
        verdict += f'            <tr data-stmt="{n}" data-verdict="o"><td style="text-align:center;font-weight:700;">{CIRC[n]}</td><td style="text-align:center;font-weight:800;color:var(--recall-correct-light);">○</td><td>{blanks[n]["core"]}</td></tr>\n'
    key = ','.join(f'{n}:o' for n in nums)
    cv = '○' * N

    new_area = f'''<div class="answer-area" id="answer-area" data-correct-value="{cv}" data-answer-type="ox-grid" data-oxgrid-mode="blank" data-explanation="{expl}">
      <p class="answer-instruction">下の<strong>解法ナビ</strong>が、一番堅く決まる空欄（アンカー）から順に、各空欄を1つずつ2択で誘導します（本文を全部読み返す必要はありません）。判断し終えたら「確定」で採点。各空欄の<strong>論点のコア</strong>が学習資産で、外した論点だけが復習プールに入ります。</p>

      <div class="answer-ox-grid">
{rows}      </div>

      <button class="reveal-answer-btn" type="button" disabled="">解答を表示</button>
      <button class="peek-explain-btn" type="button">📖 採点せず解説を見る</button>
      <div id="answer-feedback" hidden=""></div>

      <div class="final-answer" hidden="">
{intent_html}{narrative_html}        <p class="fa-summary"><strong>正解</strong>　各空欄の正しい選択がすべて揃う配置＝<strong>組合せ{win}</strong>。組合せ番号を覚えるのではなく、下表の<strong>論点のコア</strong>（各空欄の決め手）を身につける。</p>
        <table class="statement-verdict-table" data-answer-key="{key}">
          <thead><tr><th style="width:3em;">空欄</th><th style="width:3.5em;">判定</th><th>論点のコア（転用可能な法理）</th></tr></thead>
          <tbody>
{verdict}          </tbody>
        </table>
      </div>
    </div>
'''
    # answer-area 置換
    h2 = re.sub(r'<div class="answer-area" id="answer-area".*?(?=\n\s*<div class="back-to-top">)', lambda m: new_area, h, count=1, flags=re.S)
    if h2 == h:
        raise SystemExit('answer-area 置換に失敗（パターン不一致）')
    h = h2
    # 解答見出し
    h = re.sub(r'【解答】──[^<]*', '【解答】── 解法ナビがアンカー順に各空欄を2択誘導（判断し終えたら「確定」で採点）', h, count=1)
    # sn-sub
    h = re.sub(r'<span class="sn-sub">.*?</span>',
               '<span class="sn-sub">本文は読み返さず、ナビが薦める空欄（アンカー）から1つずつ2択で判断。各空欄の論点が決まれば、正解の組合せは自然に定まります。</span>',
               h, count=1, flags=re.S)
    # navi エンジン
    eng = ENGINE.replace('__ORDER__', json.dumps(order, ensure_ascii=False)).replace('__WIN__', win).replace('__B__', json.dumps(blanks, ensure_ascii=False))
    h3, nrep = re.subn(r'<script>\s*/\* 解法ナビ.*?</script>', lambda m: eng, h, count=1, flags=re.S)
    if nrep == 0:
        raise SystemExit('navi script 置換に失敗（/* 解法ナビ ブロック不一致）')
    h = h3
    # sn-frag CSS（無ければ注入）
    if '.sn-frag{' not in h:
        anchor = '.answer-ox-grid .ox-row{ align-items:flex-start; }'
        if anchor in h:
            h = h.replace(anchor, FRAG_CSS + anchor, 1)
        else:
            h = h.replace('</style>', FRAG_CSS + '</style>', 1)
    # peek CSS（無ければ注入・.sn-frag とは独立）
    if '.peek-explain-btn{' not in h:
        h = h.replace('</style>', PEEK_CSS + '</style>', 1)
    # 物語解説 CSS（無ければ注入・冪等）
    if '.fa-narrative{' not in h:
        h = h.replace('</style>', NARR_CSS + '</style>', 1)
    # 出題趣旨 CSS（無ければ注入・冪等）
    if '.fa-intent{' not in h:
        h = h.replace('</style>', INTENT_CSS + '</style>', 1)
    open(f, 'w', encoding='utf-8').write(h)
    return f, N


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python scripts/tx-build-typeA.py <CODE> <DATA.json>'); sys.exit(2)
    code = sys.argv[1]
    data = json.load(open(sys.argv[2], encoding='utf-8'))
    f, N = build(code, data)
    print(f'built {code}: 空欄 {N} 個 / order={data["order"]} / win={data["win"]} -> {f}')
