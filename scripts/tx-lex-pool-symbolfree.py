# -*- coding: utf-8 -*-
"""_lex 復習プール(.syn-lead/.choice-points li/.ox-pool)の問題ローカル記号を除去（G32・冪等・CSS不変）。
記述N 相互参照/自己参照を自己完結表現へ。A説/丸数字等の実体化が要る型はここでは扱わない（要人手/AI）。
使い方: python scripts/tx-lex-pool-symbolfree.py <_lex.html> [...]
"""
import re, sys, io
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass


def strip_refs(seg):
    seg = re.sub(r'\s*[（(]記述[0-9０-９ア-オア-ンa-jＡ-Ｚ、・\s]+[）)]', '', seg)             # （記述N）括弧参照
    seg = re.sub(r'記述[0-9０-９ア-オ]+(?=は(?:正しい|誤り|正解|不正解|妥当|当たる|不当))', '本記述', seg)  # 記述Nは正しい
    seg = re.sub(r'記述[0-9０-９ア-オ]+', 'この記述', seg)                                    # 残る裸の記述N
    return seg


def strip_refs_cp(seg):
    """choice-points 用：記号除去に加え、G22 で禁止の結論再掲『(本)記述は正しい/誤り』を除去。"""
    seg = strip_refs(seg)
    # <li>先頭の結論ラベル『(<strong>)本記述は正しい(</strong>)：』等を除去（タグ包み対応）
    seg = re.sub(r'(<li>\s*)(?:<[^>]+>\s*)*(?:本)?記述は(?:正しい|誤り|正解|不正解|妥当|当たる|不当)(?:\s*</[^>]+>)*\s*[：:]\s*',
                 r'\1', seg)
    # 文中の『、本記述は正しい』等も除去
    seg = re.sub(r'[、,]?\s*(?:本)?記述は(?:正しい|誤り|正解|不正解|妥当|当たる|不当)(?=[。．、,）)])', '', seg)
    return seg


def symbolfree(h):
    h = re.sub(r'(<p class="syn-lead">)(.*?)(</p>)',
               lambda m: m.group(1) + strip_refs(m.group(2)) + m.group(3), h, flags=re.S)
    h = re.sub(r'(<div class="choice-points">)(.*?)(</div>\s*</div>)',
               lambda m: m.group(1) + strip_refs_cp(m.group(2)) + m.group(3), h, flags=re.S)
    for pat in (r'(<div class="ox-pool-explain"[^>]*>)(.*?)(</div>)',
                r'(<ul class="ox-pool-points">)(.*?)(</ul>)'):
        h = re.sub(pat, lambda m: m.group(1) + strip_refs(m.group(2)) + m.group(3), h, flags=re.S)
    return h


def main():
    for p in sys.argv[1:]:
        h = open(p, encoding='utf-8').read()
        h2 = symbolfree(h)
        if h2 != h:
            open(p, 'w', encoding='utf-8').write(h2)
            print('[FIX] %s' % p)
        else:
            print('[--] %s (変更なし)' % p)


if __name__ == '__main__':
    main()
