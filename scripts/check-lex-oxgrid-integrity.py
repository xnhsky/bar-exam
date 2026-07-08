#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-lex-oxgrid-integrity.py — TX _lex ○×グリッド健全性ゲート（2026-07-08）

刑TX368 監査で判明した「非○×型（組合せ・穴埋め・会話）の問題を記述単位○×へ
無理に流し込んだ結果、○×が無意味/矛盾になる」欠陥を機械検出する push 前ゲート。

検出する 4 欠陥（いずれも決定論・トークン0）：

  L1 CONTRADICTION   各記述カードの tx-v13-verdict バッジと answer-key（正誤表
                     data-answer-key／answer-area data-correct-value）が食い違う。
                     ＝カード本体が「組合せの当否」を論じ、見出し/keyは「事例の
                     成否」を判定している 368 型の矛盾。
  L2 COMBO-SOLVENAV  解法ナビ STEP が「組合せN…正しいか／正しい組合せ／は正しい
                     当てはめか」と記号の組合せの当否を○×で問う（無意味設問）。
  L3 COMBO-HEADER    解答見出しが「各組合せの○×を判定」等、組合せ当否フレーム。
  L4 DEGENERATE-FILL answer-key が全同一（全○/全×）かつ本文が穴埋め/会話/組合せ
                     由来（空欄①／【組合せ】／【語句群】／会話＋（　）＋語句）。
                     ＝「正しい語句を埋めた文を全部○と確認するだけ」で○×に判別性
                     が無い退化グリッド（381/418/428 型）。genuine な全×5択
                     （空欄マーカー無し）は除外する。

exit 1 で欠陥検出（push 前ゲート）。--list で全走査ファイルの状態を一覧。
"""
import sys, re, glob, os

try:
    from bs4 import BeautifulSoup
except Exception:
    print("ERROR: beautifulsoup4 が必要です。pip install beautifulsoup4", file=sys.stderr)
    sys.exit(2)


def norm(v):
    s = (v or '').strip().lower()
    if s in ('o', '○', '◯'):
        return 'o'
    if s in ('x', '×', '✕', '✗'):
        return 'x'
    return ''


def answer_key(soup):
    key = {}
    t = soup.select_one('.statement-verdict-table[data-answer-key]')
    if t:
        for pair in t.get('data-answer-key', '').split(','):
            if ':' in pair:
                k, v = pair.split(':', 1)
                n = norm(v)
                if n:
                    key[k.strip()] = n
    if key:
        return key
    a = soup.select_one('.answer-area[data-correct-value]')
    if a:
        for i, ch in enumerate(a.get('data-correct-value', ''), start=1):
            n = norm(ch)
            if n:
                key[str(i)] = n
    return key


def badge_of(card):
    b = card.select_one('.tx-v13-verdict .verdict')
    if not b:
        return ''
    cls = ' '.join(b.get('class', []))
    if 'verdict-correct' in cls:
        return 'o'
    if 'verdict-incorrect' in cls:
        return 'x'
    txt = b.get_text()
    if '○' in txt:
        return 'o'
    if '×' in txt:
        return 'x'
    return ''


# 穴埋め/会話/組合せ 由来（＝native が独立記述○×でない）のマーカー
_FILL_MARKERS = re.compile(r'空欄[①-⑳0-9]|【組合せ】|【語句群】|に入る語句|の組合せとして正しい|語句が正しいか')
# 会話型（学生の議論）＋空所
_CONV_MARKERS = re.compile(r'【会話】|学生[ABＡＢ].{0,6}(会話|議論|次のとおり)')
# 解法ナビ/見出しの組合せ当否フレーム（疑問形の当否問い＝退化設問のみ。
#   「組合せNは正しい根拠…」のような平叙文で誤検出しないよう疑問形に限定）
_COMBO_QUIZ = re.compile(r'組合せ[0-9０-９][^"<]{0,40}?(正しい当てはめか|は正しいか)|正しい組合せ.{0,12}か[？?]|各組合せの[○×]')
_COMBO_HEADER = re.compile(r'各組合せの[○×]{1,2}を判定|各組合せの正誤|組合せの当否')


def problem_text(soup):
    parts = []
    for sel in ('#part-a', '.answer-area', '.solve-nav'):
        el = soup.select_one(sel)
        if el:
            parts.append(el.get_text(' ', strip=True))
    # solve-nav STEP は script 内なので raw も足す
    return ' '.join(parts)


def check(path):
    html = open(path, encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    findings = []

    key = answer_key(soup)
    cards = soup.select('article.tx-inline-card[data-stmt]')

    # L1 contradiction (inline-card 型のみ)
    mism = []
    for c in cards:
        s = c.get('data-stmt')
        bk = badge_of(c)
        ak = key.get(s, '')
        if bk and ak and bk != ak:
            mism.append('%s:badge%s≠key%s' % (s, bk, ak))
    if mism:
        findings.append(('L1-CONTRADICTION', ' '.join(mism)))

    # L2 combination-quiz solve-nav（script 全体を対象）
    if _COMBO_QUIZ.search(html):
        m = _COMBO_QUIZ.findall(html)
        findings.append(('L2-COMBO-SOLVENAV', 'x%d' % len(m)))

    # L3 combination header
    if _COMBO_HEADER.search(html):
        findings.append(('L3-COMBO-HEADER', ''))

    # L4 degenerate fill/conversation grid
    #   全同一キー（全○/全×）× 3行以上 × 穴埋め/会話/組合せ由来マーカー。
    #   genuine 5択（マーカー無し）や 2行以下の小グリッドは除外。
    #   blank-mode（data-oxgrid-mode="blank"＝各空欄を2択で選ばせる誘導型）は、
    #   2択そのものが判別性を担い全○の裏グリッドは意図的な設計なので L4 から除外。
    vals = [v for v in (key[k] for k in key) if v]
    blank_mode = bool(soup.select_one('.answer-area[data-oxgrid-mode="blank"]'))
    if len(vals) >= 3 and len(set(vals)) == 1 and not blank_mode:
        has_fill = bool(_FILL_MARKERS.search(html) or _CONV_MARKERS.search(html))
        if has_fill:
            findings.append(('L4-DEGENERATE-FILL',
                             'key=all-%s(%d行) marker=fill' % (vals[0], len(vals))))

    return key, len(cards), findings


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    do_list = '--list' in sys.argv
    # --warn-only: 検出しても exit 0（既存バックログ移行期用。CLAUDE.md の
    #   「当面 WARNING・安定後 ERROR 化」方針。新規 corpus が 0 になったら外す）。
    warn_only = '--warn-only' in sys.argv
    files = []
    for a in args:
        if os.path.isdir(a):
            files += glob.glob(os.path.join(a, '**', '*_lex.html'), recursive=True)
        else:
            files += glob.glob(a)
    files = sorted(set(files))
    if not files:
        print('対象 _lex ファイルなし', file=sys.stderr)
        return 2
    bad = 0
    for f in files:
        key, ncards, findings = check(f)
        num = re.search(r'TX(\d+)', os.path.basename(f))
        num = num.group(1) if num else os.path.basename(f)
        if findings:
            bad += 1
            tags = '  '.join('%s(%s)' % (t, d) if d else t for t, d in findings)
            print('[NG] %s  cards=%d  key=%s  %s' %
                  (num, ncards, ''.join(key.get(str(i), '-') for i in range(1, ncards + 1)) or '-', tags))
        elif do_list:
            print('[ok] %s' % num)
    print('\n=== check-lex-oxgrid-integrity: %d/%d ファイルで欠陥検出%s ===' %
          (bad, len(files), '（--warn-only：exit0）' if warn_only else ''))
    if bad and warn_only:
        return 0
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
