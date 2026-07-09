#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX `_lex` 相互リンク注入（正誤表 ⇄ 物語 ⇄ 各肢解説）。

v13.1.0 LOOP-CARD の「相互リンク往復」を実体化する決定論パッチ。本文不変・冪等。
- 正誤表コンテナのフッターに「ストーリー解説へ」ジャンプリンク
- ストーリー解説の先頭に「正誤表に戻る」リンク
- 物語の各記述段落(①〜) ⇄ 対応する各肢解説カード の双方向リンク

配置：
- CSS ＝ `<style id="tx-xnav-style">` を `</head>` 直前に1枚（strip 時はこの1枚だけ除去）。
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
XNAV_VERSION = "v1"

# ---- 注入する CSS（<style id="tx-xnav-style"> の1枚に閉じる） -------------------
CSS_BLOCK = """<style id="tx-xnav-style">
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
.tx-story-backrow{{ margin:0 0 14px; text-align:left; }}
.tx-xnav-story-fwd{{ display:block; margin:8px 0 2px; text-align:right; }}
.tx-xnav-row{{ margin:13px 0 2px; display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; }}
#tx-verdict-anchor, #tx-story-anchor, [id^="tx-story-"]{{ scroll-margin-top:24px; }}
</style>
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
  function labelFor(letter){{
    var card=document.getElementById('stmt-'+letter);
    var n=card && card.querySelector('.choice-num-inline');
    return (n && n.textContent.trim()) || letter;
  }}
  function mkLink(cls, href, html){{
    var a=document.createElement('a');
    a.className='tx-xnav '+cls; a.setAttribute('href', href); a.innerHTML=html;
    return a;
  }}
  function enhanceVerdict(){{
    var panel=document.querySelector(VERDICT);
    if(!panel) return;
    panel.id='tx-verdict-anchor';
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
    if(!panel.querySelector('.tx-story-backrow')){{
      var row=document.createElement('div');
      row.className='tx-story-backrow';
      row.appendChild(mkLink('tx-xnav-to-verdict','#tx-verdict-anchor','↑ 正誤表に戻る'));
      panel.insertBefore(row, panel.firstChild);
    }}
    var order=cardOrder();
    Array.prototype.forEach.call(panel.querySelectorAll('p[data-fa-label]'), function(p){{
      var m=(p.getAttribute('data-fa-label')||'').match(/[①-⑳]/); // ①〜⑳
      if(!m) return;
      var letter=order[m[0].charCodeAt(0)-0x2460];
      if(!letter) return;
      p.id='tx-story-'+letter;
      if(p.querySelector('.tx-xnav-story-fwd')) return;
      var wrap=document.createElement('span');
      wrap.className='tx-xnav-story-fwd';
      wrap.appendChild(mkLink('tx-xnav-to-card','#stmt-'+letter,'→ 記述'+labelFor(letter)+'の詳しい解説へ'));
      p.appendChild(wrap);
    }});
  }}
  function enhanceCards(){{
    if(!document.querySelector(STORY)) return;             // 物語生成後に付与
    Array.prototype.forEach.call(document.querySelectorAll('.tx-inline-card[data-stmt]'), function(card){{
      var letter=card.getAttribute('data-stmt');
      var explain=card.querySelector('.tx-inline-explain');
      if(!explain || explain.querySelector('.tx-xnav-to-story-card')) return;
      var row=document.createElement('div');
      row.className='tx-xnav-row';
      row.appendChild(mkLink('tx-xnav-to-story-card','#tx-story-'+letter,'📖 この記述を物語で読む'));
      var back=explain.querySelector('.tx-sysmap-back');
      if(back) back.parentNode.insertBefore(row, back); else explain.appendChild(row);
    }});
  }}
  var guard=false;
  function run(){{ if(guard) return; guard=true; try{{ enhanceVerdict(); enhanceStory(); enhanceCards(); }}catch(e){{}} guard=false; }}
  document.addEventListener('click', function(e){{
    if(e.target.closest && e.target.closest('.reveal-answer-btn,.tx-inline-reveal-btn,.tx-inline-browse-btn,.peek-explain-btn,.tx-inline-ox,.ox-btn')){{
      setTimeout(run,60); setTimeout(run,300);
    }}
  }}, false);
  try{{
    var ob=new MutationObserver(function(){{ run(); }});
    var start=function(){{ ob.observe(document.body,{{childList:true,subtree:true}}); run(); }};
    if(document.readyState!=='loading') start(); else document.addEventListener('DOMContentLoaded', start);
  }}catch(e){{ run(); }}

  /* 動的リンクはロード時 bind の対象外なので自前でスムーズスクロール＋フラッシュ */
  function flash(el){{ if(!el) return; el.classList.add('tx-basis-flash'); setTimeout(function(){{ el.classList.remove('tx-basis-flash'); }},1500); }}
  document.addEventListener('click', function(e){{
    var a=e.target.closest && e.target.closest('a.tx-xnav[href^="#"]');
    if(!a) return;
    var tgt=document.getElementById(a.getAttribute('href').slice(1));
    if(!tgt) return;
    e.preventDefault();
    tgt.scrollIntoView({{behavior:'smooth', block:'start'}});
    flash(tgt);
  }}, false);
}})();
/* TX-XNAV:END {ver} */
""".format(ver=XNAV_VERSION)

# strip 用（旧プロトタイプ形／sentinel 形の双方に対応）
RE_CSS = re.compile(r'<style id="tx-xnav-style">.*?</style>\r?\n?', re.S)
RE_CSS_PROTO = re.compile(r'<style>\r?\n/\* ==== プロトタイプ.*?</style>\r?\n?', re.S)
RE_JS = re.compile(r'\r?\n?/\* TX-XNAV:BEGIN.*?TX-XNAV:END[^\n]*\*/\r?\n?', re.S)
RE_JS_PROTO = re.compile(r'\r?\n?/\* ==== プロトタイプ\(369\).*?\}\)\(\);\r?\n(?=</script>)', re.S)


def has_engine(html: str) -> bool:
    return ('inline-prototype-mode' in html
            and 'fa-narrative' in html
            and re.search(r'class="tx-inline-card[^"]*"[^>]*data-stmt=', html) is not None)


def strip_existing(html: str) -> str:
    for rx in (RE_CSS, RE_CSS_PROTO, RE_JS, RE_JS_PROTO):
        html = rx.sub('', html)
    return html


def inject(html: str, nl: str) -> str:
    css = CSS_BLOCK.replace('\n', nl)
    js = JS_BLOCK.replace('\n', nl)
    # CSS → 最初の </head> 直前
    html, n_head = re.subn(r'(</head>)', css + r'\1', html, count=1)
    if n_head != 1:
        raise RuntimeError('</head> が見つからない')
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
