#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jx-v4-retrofit.py — 既存 v3.2 生成 JX を v4 LOOP-FOLD 構造へ機械変換する。

CLAUDE.md §4-1-bis / spec/jx-v4.0.0-core.md / canonical/ATHENA.html（v4 正典）に従い、
問題固有の本文（解説・規範・あてはめ・採点講評・用語集 等）は一切書き換えず、
構造シェルだけを v4 へ再編する：

  1. v4 LOOP-FOLD 用 CSS ブロックを </style> 直前へ注入（reveal / deep-dive / 照合ナビ / 口頭骨格）
  2. #exec-summary カードを削除（答え先出しの撤去・JC1）。TOC 項目を除去し、本編バックリンクは
     #issue-extraction（論点抽出）へ repoint。
  3. 第3部に .collation-nav（照合ナビ）を挿入し、模範答案(.model-answer)＋採点講評(.grading)を
     <details class="reveal-answer"> で封じる（JC4）。採点講評は answer-full 内・reveal 内へ移送。
  4. 第4部＋第5部(5-1〜5-4) を <details id="deep-dive"> で折りたたむ（JC3）。
  5. 用語集(5-5)＋略語(5-6) を折りたたみ外の <section id="part5-ref"> へ分離。
  6. 末尾 xref JS を「閉じた details を祖先までたどって開いてからスクロール」版へ差し替え。

oral-skeleton（各 H 末尾の口頭骨格・問題固有 4 点）は本スクリプトでは付与しない
（検証 JC/JD 対象外・問題ごとの執筆が必要なため）。

冪等：既に v4（<details id="deep-dive"> 検出）なら何もしない。
出力は生 HTML を文字列操作で最小改変（BeautifulSoup 再シリアライズはしない）。
"""

import re
import sys
from pathlib import Path

# ---- v4 コンポーネント定数（canonical/ATHENA.html と byte 一致） -------------

V4_CSS = """
/* ==========================================
   v4 LOOP-FOLD：reveal（模範答案）／deep-dive（深掘り層）折りたたみ・照合ナビ・口頭骨格
   ※印刷は @media print の details{display:block}/summary{display:none} で全文強制展開
   ========================================== */
details.reveal-answer, details#deep-dive{
  border:2px dashed var(--accent,#7c4a12); border-radius:12px; margin:24px 0;
}
details.reveal-answer > summary, details#deep-dive > summary{
  cursor:pointer; list-style:none; padding:15px 20px; font-weight:700;
  color:var(--accent,#7c4a12); font-size:1.05em; line-height:1.6; border-radius:10px;
}
details#deep-dive > summary{ background:var(--accent,#7c4a12); color:#fff; }
details.reveal-answer > summary::-webkit-details-marker,
details#deep-dive > summary::-webkit-details-marker{ display:none; }
details.reveal-answer > summary::before,
details#deep-dive > summary::before{ content:"▶  "; }
details.reveal-answer[open] > summary::before,
details#deep-dive[open] > summary::before{ content:"▼  "; }
details.reveal-answer[open] > summary, details#deep-dive[open] > summary{
  border-bottom:1px solid rgba(0,0,0,.12); border-radius:10px 10px 0 0;
}
.collation-nav{
  border:1px solid var(--accent,#7c4a12); border-left:5px solid var(--accent,#7c4a12);
  border-radius:0 10px 10px 0; padding:14px 20px; margin:22px 0;
}
.collation-nav h4{ margin:0 0 10px; }
.collation-nav ol{ margin:0 0 0 1.4em; } .collation-nav li{ margin-bottom:.5em; }
.oral-skeleton{
  border-top:1px dashed rgba(0,0,0,.25); margin-top:14px; padding-top:10px; font-size:.96em;
}
.oral-skeleton .os-label{ font-weight:700; color:var(--accent,#7c4a12); }
"""

COLLATION_NAV = """<nav class="collation-nav" id="collation-nav">
<h4>\U0001F4CB 照合ナビ ― 自分の答案構成を確定してから下の模範答案を開く</h4>
<ol>
  <li><strong>① 論点の過不足</strong>：<a href="#issue-extraction">第1部 論点抽出</a>と各論点の <strong>H（失点回避チェックリスト）</strong>で、拾うべき論点を数え合わせる。</li>
  <li><strong>② 規範の正確性</strong>：各論点の <strong>G（頻出論証ブロック＝規範コア）</strong>・<strong>A（条文分析）</strong>で、立てた規範のズレを照合する。</li>
  <li><strong>③ あてはめに使った事実</strong>：各論点の <strong>D（解法アルゴリズム）</strong>・<strong>F（答案表現集）</strong>で、評価に使う事実の過不足を照合する。</li>
</ol>
<p style="margin:8px 0 0;font-size:.9em">3周目以降は各 H 末尾の口頭骨格だけで「論点→条文→規範→結論」を3〜5分で言い切る。</p>
</nav>
"""

REVEAL_OPEN = ('<details class="reveal-answer">\n'
               '<summary>✋ 自分の答案構成を確定してから開く'
               '（模範答案＋採点講評）</summary>\n')

DEEPDIVE_OPEN = ('\n\n<details id="deep-dive">\n'
                 '<summary class="deep-summary">\U0001F4DA 深掘り層'
                 '（第4部 体系化＋第5部 条文・判例・学説・論証集）'
                 '｜ 1周目は開かない・同じ論点を2回ズラしたら'
                 '／直前期に開く</summary>\n')

PART5REF_BOUNDARY = ('\n\n</section>\n</details><!-- /#deep-dive 深掘り層ここまで -->\n\n'
                     '<!-- ============================================\n'
                     '     用語集・略語（毎周クイック参照・折りたたみ外）\n'
                     '     ============================================ -->\n'
                     '<section id="part5-ref">\n'
                     '<h2>用語集・略語（クイック参照）</h2>\n')

OLD_JS = "      if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'});}"
NEW_JS = ("      if(t){\n"
          "        e.preventDefault();\n"
          "        // xref が閉じた details（deep-dive / reveal-answer）内を指す場合、祖先 details を全て開いてからスクロール\n"
          "        var d=t.closest&&t.closest('details');\n"
          "        while(d){ d.open=true; d=d.parentElement&&d.parentElement.closest&&d.parentElement.closest('details'); }\n"
          "        t.scrollIntoView({behavior:'smooth',block:'start'});\n"
          "      }")


# ---- 入れ子タグの深さ計数マッチャ -------------------------------------------

def _matching_end(s, open_idx, tag):
    """open_idx（'<tag' の '<' 位置）から対応する閉じ '</tag>' の直後 index を返す。"""
    depth = 0
    pat = re.compile(r'<' + tag + r'\b|</' + tag + r'\s*>')
    for m in pat.finditer(s, open_idx):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
    raise ValueError(f'matching </{tag}> not found from {open_idx}')


def matching_div_end(s, open_idx):
    return _matching_end(s, open_idx, 'div')


def matching_section_end(s, open_idx):
    return _matching_end(s, open_idx, 'section')


# ---- 各変換ステップ ---------------------------------------------------------

def op_inject_css(s, log):
    if 'details.reveal-answer' in s:
        log.append('CSS: 既存 skip')
        return s
    idx = s.find('</style>')
    if idx == -1:
        raise ValueError('</style> not found')
    log.append('CSS: 注入')
    return s[:idx] + V4_CSS + s[idx:]


def op_remove_exec_summary(s, log):
    # (a) TOC 項目を除去
    s2, n = re.subn(r'\n?[ \t]*<li class="l2"><a href="#exec-summary">[^<]*</a></li>', '', s)
    if n:
        log.append(f'exec: TOC項目 {n} 件除去')
    s = s2
    # (b) 本編バックリンクを #issue-extraction へ repoint（主ラベルは「論点抽出」に）
    s, n1 = re.subn(r'<a href="#exec-summary">第1部 エグゼクティブサマリー</a>',
                    '<a href="#issue-extraction">第1部 論点抽出</a>', s)
    s, n2 = re.subn(r'href="#exec-summary"', 'href="#issue-extraction"', s)
    if n1 or n2:
        log.append(f'exec: バックリンク repoint {n1 + n2} 件')
    # (c) #exec-summary カード本体を削除（後続 back-to-toc も巻き取り）
    start = s.find('<div class="card" id="exec-summary">')
    if start == -1:
        log.append('exec: カード無し skip')
        return s
    end = matching_div_end(s, start)
    m = re.match(r'\s*<a href="#toc" class="back-to-toc">[^<]*</a>', s[end:])
    if m:
        end += m.end()
    # start 直前の余分な空行を 1 つに圧縮
    s = s[:start].rstrip('\n') + '\n\n' + s[end:].lstrip('\n')
    log.append('exec: カード削除')
    return s


def op_part3_reveal(s, log):
    """第3部に照合ナビを挿入し、模範答案(.model-answer)＋採点講評(#grading-comment)を
    1 つの <details class="reveal-answer"> で封じる。3 つの構造バリアントを統一処理：
      A 標準     ：<div class="card" id="answer-full"> 内に model-answer、grading は外（直後）
      B 統合(034)：<div class="model-answer" id="answer-full"> が answer-full を兼ねる
      C 別カード(032/035)：answer-full カードと grading カードの間に back-to-toc が挟まる
    方針：reveal は model-answer〜grading を内包。両者の間に挟まる answer-full 閉じ </div> と
    中間 back-to-toc は除去し、answer-full の閉じは reveal の外側へ再配置する。"""
    # 照合ナビを「第3部」見出し直後へ挿入
    m = re.search(r'(<section id="part3">\s*\n<h2>[^<]*</h2>)', s)
    if not m:
        raise ValueError('part3 header not found')
    s = s[:m.end()] + '\n\n' + COLLATION_NAV + s[m.end():]
    log.append('part3: 照合ナビ挿入')

    # 別 answer-full カードの有無で A/C と B を判別
    has_af_card = bool(re.search(r'<div class="card" id="answer-full">', s))

    mma = re.search(r'<div class="model-answer"[^>]*>', s)
    if not mma:
        raise ValueError('model-answer not found')
    ma, ma_end = mma.start(), matching_div_end(s, mma.start())

    mgr = re.search(r'<div class="[^"]*" id="grading-comment">', s)
    if not mgr:
        raise ValueError('grading-comment not found')
    gr, gr_end = mgr.start(), matching_div_end(s, mgr.start())
    if not (ma < ma_end <= gr < gr_end):
        raise ValueError('part3 model-answer/grading ordering unexpected')

    between = s[ma_end:gr]
    # 中間 back-to-toc を除去
    between = re.sub(r'[ \t]*<a href="#toc" class="back-to-toc">[^<]*</a>[ \t]*\n?', '', between)
    # A/C では answer-full 閉じ </div> を 1 つ撤去（reveal 外へ再配置するため）
    if has_af_card:
        between, nrm = re.subn(r'</div>', '', between, count=1)
        if nrm == 0:
            raise ValueError('answer-full close not found between model-answer and grading')
    between = re.sub(r'\n{3,}', '\n\n', between)

    reveal_close = '\n</details>' + ('\n</div>' if has_af_card else '')
    s = (s[:ma] + REVEAL_OPEN + s[ma:ma_end] + between +
         s[gr:gr_end] + reveal_close + s[gr_end:])
    log.append('part3: reveal-answer で模範答案＋採点講評を封印'
               + ('（統合型）' if not has_af_card else ''))
    return s


def op_deepdive_open(s, log):
    p3 = s.find('<section id="part3">')
    p3_end = matching_section_end(s, p3)
    s = s[:p3_end] + DEEPDIVE_OPEN + s[p3_end:]
    log.append('deep-dive: 第3部直後に開始タグ挿入')
    return s


def op_part5ref_split(s, log):
    hh = re.search(r'<h3>5-5[\s　]*用語集', s)
    if not hh:
        raise ValueError('5-5 用語集 heading not found')
    idx_card = s.rfind('<div class="card"', 0, hh.start())
    if idx_card == -1:
        raise ValueError('5-5 card div not found')
    # カード直前のコメント（<!-- 5-5 用語集 --> 等・複数行可）があればその手前を分割点に
    # （tempered dot で直前の1コメントだけを捕捉し、用語集側＝part5-ref 内へ送る）
    mb = re.search(r'<!--(?:(?!<!--).)*?-->\s*$', s[:idx_card], re.DOTALL)
    insert_at = mb.start() if mb else idx_card
    s = s[:insert_at].rstrip('\n') + PART5REF_BOUNDARY + s[insert_at:].lstrip('\n')
    log.append('part5-ref: 用語集/略語を折りたたみ外へ分離')
    return s


def op_swap_js(s, log):
    if "closest('details')" in s:
        log.append('JS: 既存 skip')
        return s
    if OLD_JS not in s:
        log.append('JS: 旧 xref JS 見つからず skip（要手動確認）')
        return s
    s = s.replace(OLD_JS, NEW_JS)
    log.append('JS: 祖先 details 展開対応版へ差替')
    return s


def retrofit(path: Path):
    s = path.read_text(encoding='utf-8')
    if 'id="deep-dive"' in s:
        return False, ['既に v4（deep-dive 検出）→ skip']
    log = []
    s = op_inject_css(s, log)
    s = op_remove_exec_summary(s, log)
    s = op_part3_reveal(s, log)
    s = op_deepdive_open(s, log)
    s = op_part5ref_split(s, log)
    s = op_swap_js(s, log)
    path.write_text(s, encoding='utf-8')
    return True, log


def main(argv):
    if len(argv) < 2:
        print('usage: jx-v4-retrofit.py <file.html> [file2.html ...]')
        return 2
    rc = 0
    for f in argv[1:]:
        p = Path(f)
        try:
            changed, log = retrofit(p)
            tag = 'CONVERTED' if changed else 'SKIP'
            print(f'[{tag}] {p.name}')
            for line in log:
                print(f'        - {line}')
        except Exception as e:
            rc = 1
            print(f'[ERROR] {p.name}: {e}')
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
