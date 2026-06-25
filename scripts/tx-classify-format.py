#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tx-classify-format.py — TX _lex の出題形式を Type A / Type B に機械分類（全7科目）

2026-06-25 ユーザー指示。議論形式・空欄補充の「組合せ問題」は、最終番号が
複数の小判断（各空欄の2択＝論点）の“集計”にすぎず、各小判断こそが転用可能な学習単位。
→ こうした問題は **解法ナビ主役・空欄/論点単位記録**へ作り直す（Type A）。
一方、記述ア〜オが各々独立の真偽命題である問題は、記述単位○×が正しい（Type B＝現状維持）。

判定（PART A の 5 解答選択肢のトークン構成が決め手）：
  - **Type A**：選択肢が「空欄記号→選択肢記号の割当」（例 `①a　②d　⑤j　⑥l`）＝丸数字+英字ペアが3つ以上。
      会話/文章に `①（ a.… ・ b.… ）` 型の埋め込み2択があれば更に確証。→ 解法ナビ主役へ作り直す対象。
  - **Type B-combo**：選択肢がカタカナ記述ラベルの組合せ（例 `1 ア　エ`）＝各記述が独立命題。現状維持。
  - **Type B-single**：選択肢が完全文/単一選択（独立5択「正しい/誤っているものはどれか」）。現状維持。

使い方：
  python scripts/tx-classify-format.py                 # 全科目・標準出力に集計
  python scripts/tx-classify-format.py --subject 001_刑法
  python scripts/tx-classify-format.py --map out.md    # A/B 分類マップ（人手検証用）を出力
  python scripts/tx-classify-format.py --list-a        # Type A のコードだけ改行区切りで出力（バッチ用）
"""
import argparse, glob, os, re, sys

ROOT = os.path.join('outputs', 'ux', '000_TX')
PAIR = re.compile(r'[①-⑩]\s*[a-zａ-ｚ]')          # ①a ②d … （空欄→選択肢の割当）
EMBED = re.compile(r'[①-⑩]\s*[（(][^）)]{0,80}?[ａ-ｚa-z]\s*[\.．]')  # ①（ a.… 型の埋め込み2択
CHOICE = re.compile(r'<div class="problem-text"><span class="choice-num-inline">\s*\d+\s*</span>(.*?)</div>', re.S)
KATA = re.compile(r'[ア-ンｱ-ﾝ]')


def strip(s):
    return re.sub(r'<[^>]+>', '', s).strip()


def classify(text):
    choices = [strip(m.group(1)) for m in CHOICE.finditer(text)]
    joined = ' '.join(choices)
    pair = len(PAIR.findall(joined))
    embed = len(EMBED.findall(text))
    if pair >= 3:
        blanks = sorted(set(re.findall(r'[①-⑩]', joined)))
        return 'A', {'blanks': len(blanks), 'blank_syms': ''.join(blanks), 'embed2opt': embed, 'pairs': pair}
    if not choices:
        return 'B-single', {'reason': '選択肢列なし＝単一選択(独立5択)'}
    # カタカナ記述ラベルだけの短い組合せ（ア　エ 等）か、完全文か
    avg_len = sum(len(c) for c in choices) / max(1, len(choices))
    kata = len(KATA.findall(joined))
    if avg_len <= 12 and kata >= 2:
        return 'B-combo', {'reason': '記述ラベル(ア〜オ)の組合せ＝各記述が独立命題'}
    return 'B-single', {'reason': '完全文の選択肢＝独立記述系'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject')
    ap.add_argument('--map')
    ap.add_argument('--list-a', action='store_true')
    args = ap.parse_args()
    pat = os.path.join(ROOT, args.subject if args.subject else '*', '*_lex.html')
    files = sorted(glob.glob(pat))
    res = {'A': [], 'B-combo': [], 'B-single': []}
    detail = {}
    for f in files:
        t = open(f, encoding='utf-8').read()
        cat, info = classify(t)
        code = os.path.basename(f).replace('_lex.html', '')
        res[cat].append(code)
        detail[code] = (cat, info, f)

    if args.list_a:
        print('\n'.join(res['A']))
        return 0

    print('=== TX 出題形式 分類（A=ナビ主役へ作り直し / B=記述単位のまま）===')
    print(f'対象: {len(files)} 問')
    print(f'  Type A   （議論形式・空欄補充＝組合せ）: {len(res["A"])}')
    print(f'  Type B-combo（記述ア〜オの正誤組合せ） : {len(res["B-combo"])}')
    print(f'  Type B-single（独立5択・単一選択）     : {len(res["B-single"])}')
    print(f'  → Type A 一覧: {res["A"]}')

    if args.map:
        with open(args.map, 'w', encoding='utf-8') as w:
            w.write('# TX 出題形式 分類マップ\n\n')
            w.write('- **Type A** … 解法ナビ主役・空欄/論点単位記録へ作り直す対象\n')
            w.write('- **Type B-combo / B-single** … 記述単位○×（要点一行＋折りたたみ）のまま\n\n')
            w.write('## Type A（作り直し対象）\n\n')
            for c in res['A']:
                _, info, _ = detail[c]
                w.write(f'- [ ] **{c}** … 空欄 {info["blanks"]} 個（{info["blank_syms"]}）／埋め込み2択 {info["embed2opt"]}\n')
            for grp, title in [('B-combo', 'Type B-combo（記述組合せ・独立）'), ('B-single', 'Type B-single（独立5択）')]:
                w.write(f'\n## {title}（{len(res[grp])} 問・現状維持）\n\n')
                w.write('  ' + ' '.join(res[grp]) + '\n')
        print(f'マップ出力: {args.map}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
