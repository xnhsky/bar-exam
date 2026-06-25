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


def build(code, data):
    f = f'outputs/ux/000_TX/001_刑法/{code}_lex.html'
    if not os.path.exists(f):
        # 科目フォルダ総当たり
        import glob
        cand = glob.glob(f'outputs/ux/000_TX/*/{code}_lex.html')
        if not cand:
            raise SystemExit(f'not found: {code}_lex.html')
        f = cand[0]
    h = open(f, encoding='utf-8').read()
    order = data['order']; win = str(data['win']); blanks = data['blanks']
    nums = sorted(blanks.keys(), key=lambda x: int(x))
    N = len(nums)
    expl = data.get('expl', '各空欄の論点を1つずつ判断する。各空欄の論点こそが転用可能な学習単位で、組合せ番号は結果にすぎない。')

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
      <div id="answer-feedback" hidden=""></div>

      <div class="final-answer" hidden="">
        <p class="fa-summary"><strong>正解</strong>　各空欄の正しい選択がすべて揃う配置＝<strong>組合せ{win}</strong>。組合せ番号を覚えるのではなく、下表の<strong>論点のコア</strong>（各空欄の決め手）を身につける。</p>
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
    h3 = re.sub(r'<script>\s*/\* 解法ナビ.*?</script>', lambda m: eng, h, count=1, flags=re.S)
    if h3 == h:
        raise SystemExit('navi script 置換に失敗（/* 解法ナビ ブロック不一致）')
    h = h3
    # sn-frag CSS（無ければ注入）
    if '.sn-frag{' not in h:
        anchor = '.answer-ox-grid .ox-row{ align-items:flex-start; }'
        if anchor in h:
            h = h.replace(anchor, FRAG_CSS + anchor, 1)
        else:
            h = h.replace('</style>', FRAG_CSS + '</style>', 1)
    open(f, 'w', encoding='utf-8').write(h)
    return f, N


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python scripts/tx-build-typeA.py <CODE> <DATA.json>'); sys.exit(2)
    code = sys.argv[1]
    data = json.load(open(sys.argv[2], encoding='utf-8'))
    f, N = build(code, data)
    print(f'built {code}: 空欄 {N} 個 / order={data["order"]} / win={data["win"]} -> {f}')
