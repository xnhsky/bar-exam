# -*- coding: utf-8 -*-
"""v13 _lex の意匠polish（ユーザーレビュー6点・冪等）。
1. 物語パネルを肢カード（judge-list）直後へ移動（正誤表→体系マップ→横断→肢カード→物語の順）。
2. 物語/GIST の強調太字を軽減（潰れ防止）。
3. 取扱説明の定型文（basis-moved-note・answer-instruction 等）を削除。
4. 体系マップ上部タイトルを枠幅に合わせて font-size 自動縮小（はみ出し防止）。
5. 肢カードの交互背景を nth-child→nth-of-type に（problem-text と交互でも効くように）。
使い方: python scripts/tx-lex-v13-polish.py <_lex.html> [...]
"""
import re, sys, io
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

MARK = '/* === v13 polish (review 6pt) === */'


def polish(h):
    if MARK in h:
        # 冪等：CSS/JS再注入は避けるが、構造系(4:title/1:story JS/3:note)は再適用しても安全なので続行
        pass

    # --- 5+1anchor. 肢カード群を .tx-inline-list で包む（recanon偽造は未包み＝縞も物語アンカーも壊れる） ---
    if re.search(r'<article class="tx-inline-card"', h) and not re.search(r'<div class="tx-inline-list"', h):
        first = re.search(r'<article class="tx-inline-card"', h)
        starts = [m.start() for m in re.finditer(r'<article class="tx-inline-card"', h)]
        last_start = starts[-1]
        last_end = h.index('</article>', last_start) + len('</article>')
        seg = h[first.start():last_end]
        # カード群が連続（間に別要素が少ない）ときのみ包む
        h = h[:first.start()] + '<div class="tx-inline-list">\n' + seg + '\n</div>' + h[last_end:]
    # 縞：nth-child(even) → nth-of-type(even)（.tx-inline-list 内で確実に効く）
    h = h.replace('.tx-inline-card:nth-child(even)', '.tx-inline-card:nth-of-type(even)')
    h = h.replace('.tx-inline-card:nth-child(odd)', '.tx-inline-card:nth-of-type(odd)')

    # --- 4. 体系マップ上部タイトル font-size 自動縮小（枠 640px・全角≈font px） ---
    def fit_title(m):
        pre, txt, post = m.group(1), m.group(2), m.group(3)
        n = len(txt)
        fs = 21 if n <= 28 else max(14, int(600 / n))
        pre2 = re.sub(r'font-size="\d+(?:\.\d+)?"', 'font-size="%d"' % fs, pre)
        return pre2 + txt + post
    h = re.sub(r'(<text x="0" y="6"[^>]*font-size="\d+"[^>]*>)([^<]*)(</text>)', fit_title, h)

    # --- 3+note. 取扱説明の定型文を削除 ---
    h = re.sub(r'<p class="basis-moved-note">.*?</p>\s*', '', h, flags=re.S)          # 6. BASIS内に配置note
    h = re.sub(r'<p class="answer-instruction">.*?</p>\s*', '', h, flags=re.S)        # 解法ナビ誘導の定型
    # solve-nav の sn-sub 定型（「〜下の一問一答で…」等の取説）は機能に無関係な説明文なので簡素化
    h = re.sub(r'(<span class="sn-sub">).*?(</span>)', r'\1\2', h, count=1, flags=re.S)

    # --- 追記CSS/JS（末尾・1回だけ） ---
    if MARK not in h:
        css = ('\n' + MARK + '\n'
               # 2. 太字軽減（潰れ防止）
               '.fa-narrative p{ font-weight:450 !important; }\n'
               '.fa-narrative b{ font-weight:520 !important; }\n'
               '.tx-inline-explain .syn-lead{ font-weight:500 !important; }\n'
               '.tx-inline-explain .syn-lead b, .tx-inline-explain .syn-image b{ font-weight:560 !important; }\n')
        si = h.rfind('</style>')
        h = h[:si] + css + h[si:]
        # 1. 物語をカード直後へ移動：canonical エンジン script 末尾へ統合（新規scriptを足さない・G41）
        # story/judge-list は browse/reveal 時に JS 生成されるので、クリック後＋MutationObserver で移設
        mvjs = ("\n/* v13 polish: 物語を肢カード直後へ（生成後に移設） */\n"
                "(function(){function mv(){var st=document.querySelector('.tx-inline-story-panel');"
                "var jl=document.querySelector('.tx-inline-judge-list, .tx-inline-list');"
                "if(st&&jl&&jl.parentNode&&st.previousElementSibling!==jl){jl.parentNode.insertBefore(st, jl.nextSibling);}}"
                "document.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('.tx-inline-browse-btn,.reveal-answer-btn,.tx-inline-reveal-btn,.peek-explain-btn')){setTimeout(mv,50);setTimeout(mv,250);}});"
                "try{var ob=new MutationObserver(function(){mv();});var st0=function(){ob.observe(document.body,{childList:true,subtree:true});mv();};"
                "if(document.readyState!=='loading')st0();else document.addEventListener('DOMContentLoaded',st0);}catch(e){}})();\n")
        eng = re.search(r'(getInlineAnswerTablePanel|moveStatementVerdictTableToTop)', h)
        if eng:
            close = h.index('</' + 'script>', eng.start())
            h = h[:close] + mvjs + h[close:]
    return h


def main():
    for p in sys.argv[1:]:
        h = open(p, encoding='utf-8').read()
        if '.tx-inline-card' not in h:
            print('[SKIP] %s (v13 inline でない)' % p); continue
        h2 = polish(h)
        # write_bytes で LF 固定（Windows text-mode 書込みの CRLF 変換＝全行偽差分を防ぐ）。
        open(p, 'wb').write(h2.encode('utf-8'))
        print('[OK] %s polished' % p)


if __name__ == '__main__':
    main()
