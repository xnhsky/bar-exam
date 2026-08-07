#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX `_lex` 相互リンク注入（正誤表 ⇄ 物語 ⇄ 各肢解説）。

v13.1.0 LOOP-CARD の「相互リンク往復」を実体化する決定論パッチ。本文不変・冪等。
- 正誤表コンテナのフッターに「ストーリー解説へ」ジャンプリンク
- ストーリー解説の先頭に「正誤表に戻る」＋全肢ジャンプバー、末尾にも全肢ジャンプバー
- 各肢解説カードに「この問題を物語で読む」＝物語パネル先頭へのリンク

v2（2026-07-09）変更点：物語は肢と 1:1 でない（テーマ単位で束ねる仕様）ため、v1 の
「data-fa-label 内の丸数字＝肢番号」推測を廃止。この推測は実コーパスでほぼ一致せず
（半角数字・順不同・重複・テーマ名ラベル）、①各肢カード→物語の飛び先 #tx-story-{肢} が
未生成で死リンク、②物語→肢の順リンクが大半で未付与、の二重不具合を生んでいた。
v2 は「全肢へ確実に飛べるバー」＋「物語パネル先頭へ確実に戻れるリンク」に置換する。

v3（2026-08-07）追加点：**正誤表の各行 ⇄ その肢の解説カードの 1:1 往復**。
正誤表は 4 列（記述／正誤／あなた／原文・コア）で、右端セルだけが長く左 3 列に縦の余白が空く。
そこへ行ごとの小ピル（`.tx-verdict-jump`「解説 ↓」）を置き、行→カードを直結する（従来は
「物語→全肢バー」経由の 2 ホップしかなく、行から対応カードへ直接飛べなかった）。
戻りは各行に `id="tx-verdict-row-{{data-stmt}}"` を振り、カード側 xnav 行の
`↑ 正誤表の記述Xへ` から**その行へ**戻す（従来の戻り先は表の先頭のみ）。
行は再描画で作り直されるため id が一時的に消えうる。リンクは `data-fallback` に
`tx-verdict-anchor` を持ち、行 id が解決できないときは表の先頭へ着地する（死リンクを作らない）。

配置：
- CSS ＝ `<style id="tx-xnav-style">` を `</head>` 直前に1枚。中身は
         `/* TX-XNAV-CSS:BEGIN vN */ … /* TX-XNAV-CSS:END vN */` の sentinel で挟む。
         **strip はこの sentinel 区間だけ**（v2 までは `<style id="tx-xnav-style">` 要素を丸ごと
         消していたが、後発の `tx-lex-css-canonize.py` が同要素の末尾へ canonical CSS
         （§v13n 原文不可侵ブロック・v13m cross-cut チップ 等）を追記するようになったため、
         再注入のたびにその canonical CSS を巻き添えで消す事故になっていた。sentinel 化で解消。
         v2 形（sentinel 無し）は「TX-XNAV 見出しコメント〜`.tx-inline-card[id^="stmt-"]` 規則」の
         逐語レンジだけを剥がし、残りの CSS には触らない）。
- JS  ＝ `/* TX-XNAV:BEGIN vN */ ... /* TX-XNAV:END vN */` で挟んだ IIFE を
         **最初の `<script>`（canonical エンジン）** の `</script>` 直前へ。script 本数は増やさない（G41）。

正誤表/物語パネルは JS で遅延生成・再描画されるため、IIFE 側は MutationObserver で追随し冪等に付与する。

対象は「インライン肢カード＋物語＋正誤表エンジン」を持つ `_lex` のみ（純 v11 ox-grid・公式 000_TX は自動 SKIP）。
canonical/GENESIS-CARD.html を含める場合は --canonical。

使い方:
  python scripts/tx-lex-inject-xnav.py                         # dry-run: outputs/ux/000_TX の 360以降 を走査
  python scripts/tx-lex-inject-xnav.py --apply                 # 適用（360以降・全科目）
  python scripts/tx-lex-inject-xnav.py --canonical --apply     # canonical も含めて適用
  python scripts/tx-lex-inject-xnav.py --min 360 --apply
  python scripts/tx-lex-inject-xnav.py outputs/ux/000_TX/001_刑法/刑TX369_lex.html --apply
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XNAV_VERSION = "v3"

# ---- 注入する CSS（<style id="tx-xnav-style"> 内の sentinel 区間） ---------------
CSS_BODY = """/* TX-XNAV-CSS:BEGIN {ver} */
/* TX-XNAV {ver}: 正誤表 ⇄ 物語(ストーリー解説) ⇄ 各肢解説 の相互リンク */
.tx-xnav{{
  display:inline-flex; align-items:center; gap:5px; padding:5px 14px 6px;
  border:1px solid rgba(139,121,166,.55); border-radius:999px;
  background:linear-gradient(180deg, var(--light,#faf7ff) 0%, var(--soft,#ece4f5) 100%);
  color:var(--accent-darker,#4f3577); font-family:var(--font-soft); font-size:.83em; font-weight:850;
  text-decoration:none; cursor:pointer; transition:filter .15s ease;
  box-shadow:0 2px 6px -2px rgba(90,70,130,.3), inset 0 1px 0 rgba(255,255,255,.65);
}}
.tx-xnav:hover{{ filter:brightness(1.05); }}
.tx-xnav-footer{{ margin-top:16px; padding-top:13px; border-top:1px dashed rgba(139,121,166,.45); text-align:center; }}
.tx-xnav-footer .tx-xnav{{ font-size:.9em; }}
.tx-story-backrow{{ margin:0 0 16px; }}
.tx-story-fwdrow{{ margin:18px 0 2px; padding-top:13px; border-top:1px dashed rgba(139,121,166,.45); }}
.tx-xnav-stmtbar{{ display:flex; flex-wrap:wrap; align-items:center; gap:7px; margin-top:9px; }}
.tx-xnav-stmtbar-lead{{ font-family:var(--font-soft); font-size:.82em; font-weight:800; color:var(--accent-darker,#4f3577); }}
.tx-xnav-stmtbar .tx-xnav{{ font-size:.8em; padding:4px 12px 5px; }}
.tx-xnav-row{{ margin:13px 0 2px; display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; }}
#tx-verdict-anchor, #tx-story-anchor{{ scroll-margin-top:24px; }}
.tx-inline-card[id^="stmt-"]{{ scroll-margin-top:24px; }}
/* v3: 正誤表の行 ⇄ 対応する肢カードの 1:1 往復。
   「記述」列は 1 文字（ア）だけで縦に余白が空くので、そこへ 2 段の小ピルを落とす。
   列幅を広げて右端の本文列を圧迫しないよう、幅は見出し「記述」と同等に抑える。 */
.tx-verdict-jump.tx-xnav{{
  display:block; width:max-content; max-width:100%; margin:7px auto 0;
  padding:3px 7px 4px; gap:0; border-radius:9px; white-space:nowrap;
  font-size:.62em; font-weight:800; line-height:1.3; letter-spacing:0; text-indent:0;
  background:linear-gradient(180deg,#fffdf3 0%,#f2e6c2 100%);
  border-color:rgba(122,102,41,.5); color:#6a5a24;
  box-shadow:0 2px 5px -2px rgba(90,72,25,.35), inset 0 1px 0 rgba(255,255,255,.7);
}}
.tx-verdict-jump .tx-vj-arrow{{ display:block; font-size:1.15em; line-height:1; }}
/* 戻り先の行。scroll-margin は tr でも scrollIntoView に効く。 */
.statement-verdict-table tbody tr[id^="tx-verdict-row-"]{{ scroll-margin-top:24px; }}
/* 行のハイライトは td の box-shadow で出す（td の background は !important 指定済みで
   キーフレームからは上書きできないため、影の層で光らせる）。 */
tr[id^="tx-verdict-row-"].tx-basis-flash > td{{ animation:txRowFlash 1.6s ease; }}
@keyframes txRowFlash{{
  0%{{ box-shadow:inset 0 0 0 3px rgba(90,134,168,.62); }}
  70%{{ box-shadow:inset 0 0 0 3px rgba(90,134,168,.22); }}
  100%{{ box-shadow:inset 0 0 0 0 rgba(90,134,168,0); }}
}}
/* TX-XNAV-CSS:END {ver} */
""".format(ver=XNAV_VERSION)

# ---- 注入する JS（sentinel で挟んだ IIFE・最初の <script> 内へ） ---------------
JS_BLOCK = r"""
/* TX-XNAV:BEGIN {ver} ── 正誤表 ⇄ 物語(ストーリー解説) ⇄ 各肢解説 の相互リンク
   正誤表/物語パネルは JS で遅延生成・再描画されるため MutationObserver で追随し冪等に付与する。 */
(function(){{
  var VERDICT='.tx-inline-answer-table-panel', STORY='.tx-inline-story-panel';
  function cardOrder(){{
    return Array.prototype.map.call(
      document.querySelectorAll('.tx-inline-card[data-stmt]'),
      function(c){{ return c.getAttribute('data-stmt'); }});
  }}
  // カードは id="stmt-{{data-stmt}}" が原則だが、data-stmt が記述記号（ア/イ…）で
  // id は stmt-1.. の連番、という世代が corpus に混在する（刑TX038_lex）。id の直引きだけだと
  // その世代でリンクが全部死ぬ（v2 の全肢ジャンプバーも同じ理由で死んでいた）ため、
  // data-stmt での引き当てを併用し、飛び先は必ずカードの実 id から作る。
  function cardFor(stmt){{
    return document.getElementById('stmt-'+stmt)
        || document.querySelector('.tx-inline-card[data-stmt="'+stmt+'"]');
  }}
  function cardHref(stmt){{
    var c=cardFor(stmt);
    if(!c) return null;
    if(!c.id) c.id='stmt-'+stmt;
    return '#'+c.id;
  }}
  function labelFor(letter){{
    var card=cardFor(letter);
    var n=card && card.querySelector('.choice-num-inline');
    return (n && n.textContent.trim()) || letter;
  }}
  function mkLink(cls, href, html){{
    var a=document.createElement('a');
    a.className='tx-xnav '+cls; a.setAttribute('href', href); a.innerHTML=html;
    return a;
  }}
  // 全肢ジャンプバー：物語は肢と 1:1 でない（テーマ単位で束ねる）ため、段落ごとの
  // 対応を丸数字で推測せず、全肢へ確実に飛べるバーを置く（どの肢へも必ず正しく解決）。
  function stmtBar(){{
    var bar=document.createElement('div');
    bar.className='tx-xnav-stmtbar';
    var lead=document.createElement('span');
    lead.className='tx-xnav-stmtbar-lead';
    lead.textContent='各肢の詳しい解説へ：';
    bar.appendChild(lead);
    cardOrder().forEach(function(letter){{
      var href=cardHref(letter);
      if(href) bar.appendChild(mkLink('tx-xnav-to-card',href,'記述'+labelFor(letter)));
    }});
    return bar;
  }}
  // v3: 正誤表の行 ⇄ 肢カードの 1:1 往復。行に id を振り、「記述」列の余白へ
  // その肢の解説カードへ落ちる小ピルを置く（行→カード）。冪等・再描画で再付与。
  function rowId(stmt){{ return 'tx-verdict-row-'+stmt; }}
  function enhanceVerdictRows(panel){{
    Array.prototype.forEach.call(panel.querySelectorAll('tbody tr[data-stmt]'), function(row){{
      var stmt=row.getAttribute('data-stmt');
      var href=stmt && cardHref(stmt);
      if(!href) return;                                             // 対応カードが無い行は触らない
      row.id=rowId(stmt);
      var cell=row.cells && row.cells[0];
      if(!cell || cell.querySelector('.tx-verdict-jump')) return;
      var a=mkLink('tx-verdict-jump',href,'解説<span class="tx-vj-arrow">↓</span>');
      a.setAttribute('title','記述'+labelFor(stmt)+'の解説へ');
      cell.appendChild(a);
    }});
  }}
  function enhanceVerdict(){{
    var panel=document.querySelector(VERDICT);
    if(!panel) return;
    panel.id='tx-verdict-anchor';
    enhanceVerdictRows(panel);                            // 行→カードは物語の有無に依らず張る
    if(!document.querySelector(STORY)) return;            // 物語が未生成ならフッターは付けない
    if(panel.querySelector('.tx-xnav-footer')) return;    // 再描画で消えたら再付与（冪等）
    var foot=document.createElement('div');
    foot.className='tx-xnav-footer';
    foot.appendChild(mkLink('tx-xnav-to-story','#tx-story-anchor','📖 この問題を物語で読む（ストーリー解説）へ ↓'));
    panel.appendChild(foot);
  }}
  function enhanceStory(){{
    var panel=document.querySelector(STORY);
    if(!panel) return;
    panel.id='tx-story-anchor';
    if(!cardOrder().length) return;                        // 肢カード未生成ならバーは張らない
    if(!panel.querySelector('.tx-story-backrow')){{         // 冒頭：正誤表に戻る＋全肢バー
      var row=document.createElement('div');
      row.className='tx-story-backrow';
      row.appendChild(mkLink('tx-xnav-to-verdict','#tx-verdict-anchor','↑ 正誤表に戻る'));
      row.appendChild(stmtBar());
      panel.insertBefore(row, panel.firstChild);
    }}
    if(!panel.querySelector('.tx-story-fwdrow')){{          // 末尾：読了後に各肢の詳説へ
      var frow=document.createElement('div');
      frow.className='tx-story-fwdrow';
      frow.appendChild(stmtBar());
      panel.appendChild(frow);
    }}
  }}
  // カード内の xnav 行（無ければ体系マップ戻りリンクの直前に作る）。
  function xnavRow(explain){{
    var row=explain.querySelector('.tx-xnav-row');
    if(row) return row;
    row=document.createElement('div');
    row.className='tx-xnav-row';
    var back=explain.querySelector('.tx-sysmap-back');
    if(back) back.parentNode.insertBefore(row, back); else explain.appendChild(row);
    return row;
  }}
  function enhanceCards(){{
    if(!document.querySelector(STORY)) return;             // 物語生成後に付与
    Array.prototype.forEach.call(document.querySelectorAll('.tx-inline-card[data-stmt]'), function(card){{
      var explain=card.querySelector('.tx-inline-explain');
      if(!explain || explain.querySelector('.tx-xnav-to-story-card')) return;
      // 飛び先は物語パネル先頭（必ず存在）。旧 #tx-story-{{肢}} は物語側で ID 未生成の
      // ことが多く死リンクだった。物語は 1:1 でないため段落ピンポイントには飛ばさない。
      xnavRow(explain).appendChild(mkLink('tx-xnav-to-story-card','#tx-story-anchor','📖 この問題を物語で読む'));
    }});
  }}
  // v3: カード→正誤表の**その行**へ戻す（従来の戻り先は表の先頭だけだった）。
  // 行 id は再描画で一時的に消えるので data-fallback で表の先頭へ退避させる。
  function enhanceCardBacklinks(){{
    if(!document.querySelector(VERDICT)) return;            // 正誤表（解答表示後）にのみ張る
    Array.prototype.forEach.call(document.querySelectorAll('.tx-inline-card[data-stmt]'), function(card){{
      var explain=card.querySelector('.tx-inline-explain');
      if(!explain || explain.querySelector('.tx-xnav-to-verdict-row')) return;
      var stmt=card.getAttribute('data-stmt');
      var a=mkLink('tx-xnav-to-verdict-row','#'+rowId(stmt),'↑ 正誤表の記述'+labelFor(stmt)+'へ');
      a.setAttribute('data-fallback','tx-verdict-anchor');
      var row=xnavRow(explain);
      row.insertBefore(a, row.firstChild);
    }});
  }}
  var guard=false;
  function run(){{ if(guard) return; guard=true; try{{ enhanceVerdict(); enhanceStory(); enhanceCards(); enhanceCardBacklinks(); }}catch(e){{}} guard=false; }}
  document.addEventListener('click', function(e){{
    if(e.target.closest && e.target.closest('.reveal-answer-btn,.tx-inline-reveal-btn,.tx-inline-browse-btn,.peek-explain-btn,.tx-inline-ox,.ox-btn')){{
      setTimeout(run,60); setTimeout(run,300);
    }}
  }}, false);
  // v3: 「解答を表示」の着地点を正誤表にそろえる。
  // reveal は 5 肢の解説を一斉に開くので本文が一気に伸び、ブラウザのスクロールアンカリングが
  // 押し下げられた位置を追って**最後の肢カードまで**飛ばしてしまう（v3 以前からの挙動）。
  // 露出順は 正誤表 → 体系マップ → 肢カード なので、明示的に正誤表へ着地させる。
  // 伸長は遅延描画で数回に分かれて起きるため、短い窓の中で数回だけ再アサートする
  // （「解説だけ閲覧」は最初の解説へ飛ぶ既存動線なので対象にしない）。
  function landOnVerdict(){{
    var panel=document.querySelector(VERDICT);
    if(panel && !panel.hidden) jumpTo(panel);
  }}
  document.addEventListener('click', function(e){{
    if(!(e.target.closest && e.target.closest('.tx-inline-reveal-btn,.reveal-answer-btn'))) return;
    [60,180,360,700].forEach(function(ms){{ setTimeout(landOnVerdict, ms); }});
  }}, false);
  try{{
    var ob=new MutationObserver(function(){{ run(); }});
    var start=function(){{ ob.observe(document.body,{{childList:true,subtree:true}}); run(); }};
    if(document.readyState!=='loading') start(); else document.addEventListener('DOMContentLoaded', start);
  }}catch(e){{ run(); }}

  /* 動的リンクはロード時 bind の対象外なので自前でスクロール＋フラッシュ。
     behavior:'smooth' はインラインエンジンの遅延再描画に中断されページが動かない
     （＝「リンクが効かない」の実体）ため、確実に着地する即時スクロールにし、
     再描画の押し戻し対策として次フレームで一度だけ再アサートする。
     v3: 引数省略では html{{scroll-behavior:smooth}} を継承してしまい（数千〜万 px の
     アニメーションになる＝「なかなか着かない／途中で止まる」）、再アサートのたびに
     滑走がやり直しになる。behavior:'instant' で明示的に打ち消す（非対応環境は従来どおり）。 */
  function jumpTo(el){{
    try{{ el.scrollIntoView({{block:'start', behavior:'instant'}}); }}
    catch(e){{ el.scrollIntoView({{block:'start'}}); }}
  }}
  function flash(el){{ if(!el) return; el.classList.add('tx-basis-flash'); setTimeout(function(){{ el.classList.remove('tx-basis-flash'); }},1500); }}
  document.addEventListener('click', function(e){{
    var a=e.target.closest && e.target.closest('a.tx-xnav[href^="#"]');
    if(!a) return;
    var tgt=document.getElementById(a.getAttribute('href').slice(1));
    if(!tgt && a.getAttribute('data-fallback')) tgt=document.getElementById(a.getAttribute('data-fallback'));
    if(!tgt) return;
    e.preventDefault();
    var go=function(){{ jumpTo(tgt); }};
    go();
    if(window.requestAnimationFrame) requestAnimationFrame(go); else setTimeout(go,16);
    flash(tgt);
  }}, false);
}})();
/* TX-XNAV:END {ver} */
""".format(ver=XNAV_VERSION)

# strip 用（旧プロトタイプ形／v2 逐語形／sentinel 形に対応）
# CSS は要素ごと消さない：後発の tx-lex-css-canonize.py が同じ <style id="tx-xnav-style"> の
# 末尾へ canonical CSS を追記するため、要素丸ごとの除去は他人の CSS を巻き添えにする。
RE_CSS_SENTINEL = re.compile(r'/\* TX-XNAV-CSS:BEGIN.*?TX-XNAV-CSS:END[^\n]*\*/\r?\n?', re.S)
# v2 までの sentinel 無し形＝注入器が書いた逐語レンジ（見出しコメント〜最後の規則行）だけを剥がす。
RE_CSS_V2 = re.compile(
    r'/\* TX-XNAV v\d+: 正誤表.*?'
    r'\.tx-inline-card\[id\^="stmt-"\]\{ scroll-margin-top:24px; \}\r?\n?', re.S)
# 中身が空になった容器は畳む（他の CSS が残っていれば当然マッチしない）。
RE_CSS_EMPTY = re.compile(r'<style id="tx-xnav-style">\s*</style>\r?\n?')
RE_CSS_PROTO = re.compile(r'<style>\r?\n/\* ==== プロトタイプ.*?</style>\r?\n?', re.S)
RE_JS = re.compile(r'\r?\n?/\* TX-XNAV:BEGIN.*?TX-XNAV:END[^\n]*\*/\r?\n?', re.S)
RE_JS_PROTO = re.compile(r'\r?\n?/\* ==== プロトタイプ\(369\).*?\}\)\(\);\r?\n(?=</script>)', re.S)


def has_engine(html: str) -> bool:
    return ('inline-prototype-mode' in html
            and 'fa-narrative' in html
            and re.search(r'class="tx-inline-card[^"]*"[^>]*data-stmt=', html) is not None)


def strip_existing(html: str) -> str:
    for rx in (RE_CSS_SENTINEL, RE_CSS_V2, RE_CSS_EMPTY, RE_CSS_PROTO, RE_JS, RE_JS_PROTO):
        html = rx.sub('', html)
    return html


def inject(html: str, nl: str) -> str:
    css = CSS_BODY.replace('\n', nl)
    js = JS_BLOCK.replace('\n', nl)
    # CSS → 既存の容器があればその先頭へ（末尾に追記された canonical CSS を保つ）。
    #       無ければ容器ごと最初の </head> 直前へ新設。
    if '<style id="tx-xnav-style">' in html:
        html, n_head = re.subn(r'(<style id="tx-xnav-style">\r?\n?)', lambda m: m.group(1) + css,
                               html, count=1)
    else:
        wrapped = '<style id="tx-xnav-style">' + nl + css + '</style>' + nl
        html, n_head = re.subn(r'(</head>)', lambda m: wrapped + m.group(1), html, count=1)
    if n_head != 1:
        raise RuntimeError('CSS の挿入先が見つからない')
    # JS → 最初の </script> 直前（＝canonical エンジン script）
    html, n_scr = re.subn(r'(</script>)', js + r'\1', html, count=1)
    if n_scr != 1:
        raise RuntimeError('</script> が見つからない')
    return html


def process(path: Path, apply: bool) -> str:
    with open(path, 'r', encoding='utf-8', errors='surrogatepass', newline='') as fh:
        raw = fh.read()  # newline='' で CRLF を温存（read_text は改行を LF へ翻訳するため使わない）
    nl = '\r\n' if '\r\n' in raw else '\n'
    if not has_engine(raw):
        return 'SKIP(no-engine)'
    cleaned = strip_existing(raw)
    out = inject(cleaned, nl)
    already = (raw == out)
    if apply and not already:
        path.write_text(out, encoding='utf-8', errors='surrogatepass', newline='')
    return 'NOCHANGE' if already else ('APPLIED' if apply else 'WOULD-APPLY')


def num_of(path: Path):
    m = re.search(r'TX(\d+)_lex', path.name)
    return int(m.group(1)) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='*', help='対象ファイル（省略時は outputs/ux/000_TX を走査）')
    ap.add_argument('--min', type=int, default=360, help='この番号以降を対象（既定 360）')
    ap.add_argument('--apply', action='store_true', help='書き込む（既定は dry-run）')
    ap.add_argument('--canonical', action='store_true', help='canonical/GENESIS-CARD.html も対象に含める')
    args = ap.parse_args()

    targets: list[Path] = []
    if args.paths:
        targets = [Path(p) for p in args.paths]
    else:
        for p in sorted((ROOT / 'outputs' / 'ux' / '000_TX').rglob('*_lex.html')):
            n = num_of(p)
            if n is not None and n >= args.min:
                targets.append(p)
    if args.canonical:
        targets.insert(0, ROOT / 'canonical' / 'GENESIS-CARD.html')

    counts: dict[str, int] = {}
    for p in targets:
        if not p.exists():
            print(f'  MISSING  {p}')
            counts['MISSING'] = counts.get('MISSING', 0) + 1
            continue
        try:
            st = process(p, args.apply)
        except Exception as e:  # noqa
            st = f'ERROR({e})'
        counts[st.split('(')[0]] = counts.get(st.split('(')[0], 0) + 1
        rel = p.relative_to(ROOT) if ROOT in p.parents else p
        print(f'  {st:14} {rel}')

    print('\n=== 集計 ===')
    for k in sorted(counts):
        print(f'  {k:14} {counts[k]}')
    if not args.apply:
        print('\n(dry-run。--apply で書き込み)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
