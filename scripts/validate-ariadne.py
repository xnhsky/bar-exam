#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate-ariadne.py — ARIADNE（JX 解法ナビ＋周回・Lexia連携）HTML の検証。

ARIADNE は ATHENA（百科事典型 JX 正典）と役割分担する別正典。
本検証器は「構造（誌面の骨格）」「Lexia 周回契約（自己完結○×が復習プールに乗るか）」
「Lexia 安全制約（</body>リテラル・メタ除去regex）」を機械検査する。

使い方:  python scripts/validate-ariadne.py outputs/ux/000_ARIADNE/001_刑法/刑JX001_ARIADNE.html
ERROR が 1 件でもあれば exit 1。WARNING は配信可。
"""
import sys, re, os
try:
    sys.stdout.reconfigure(encoding='utf-8')  # Windows コンソールの文字化け回避
except Exception:
    pass

# Lexia のメタ問題除去 regex（App.jsx:1401 と一致）。当たると周回プールから削除される。
META_RE = re.compile(r'(本問|本設問)[^。\n]{0,20}正解|正解は肢|正解はどれ|正解の組(合せ|み合わせ)')

def extract_divs(html, cls):
    """class に cls を含む <div> を深さ計数で抽出 → [(open_tag, inner_html)]。"""
    blocks = []
    open_re = re.compile(r'<div\b[^>]*\bclass="[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*>', re.I)
    tag_re = re.compile(r'<(/?)div\b', re.I)
    for m in open_re.finditer(html):
        start = m.end(); depth = 1
        for t in tag_re.finditer(html, start):
            depth += 1 if t.group(1) == '' else -1
            if depth == 0:
                blocks.append((m.group(0), html[start:t.start()])); break
    return blocks

def text_only(s):
    return re.sub(r'<[^>]+>', '', s).strip()

def main():
    if len(sys.argv) < 2:
        print("usage: validate-ariadne.py <file.html>"); sys.exit(2)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"[ERROR] file not found: {path}"); sys.exit(2)
    html = open(path, encoding='utf-8', newline='').read()
    errors, warns, passes = [], [], []
    def E(c, m): errors.append(f"[ERROR] {c}: {m}")
    def W(c, m): warns.append(f"[WARN]  {c}: {m}")
    def P(c, m): passes.append(f"[PASS]  {c}: {m}")

    # ---- 構造 A1〜A11 ----
    if 'lang="ja"' in html: P('A1', 'lang=ja')
    else: E('A1', 'lang="ja" がない')
    if re.search(r'<title>.+?</title>', html): P('A2', 'title あり')
    else: E('A2', '<title> がない')
    if 'class="masthead"' in html: P('A3', 'マストヘッドあり')
    else: E('A3', 'マストヘッド(.masthead)がない')
    if 'class="foot"' in html: P('A4', 'フッターあり')
    else: W('A4', 'フッター(.foot)がない')
    prob = extract_divs(html, 'problem')
    if prob and text_only(prob[0][1]): P('A5', '問題文あり')
    else: E('A5', '問題文(.problem)が空/なし')
    steps = extract_divs(html, 'step')
    if len(steps) >= 6: P('A6', f'解法ナビ手 {len(steps)} 個')
    else: E('A6', f'解法ナビ手が少なすぎ（{len(steps)}個・7手想定）')
    if 'class="steps-rail"' in html: P('A7', 'ステッパーあり')
    else: W('A7', 'ステッパー(.steps-rail)がない')
    bone = extract_divs(html, 'bone')
    if bone and text_only(bone[0][1]): P('A8', '骨子あり')
    else: E('A8', '骨子(.bone)が空/なし')
    if re.search(r'class="rubric"|class="collate"', html): P('A9', '自己採点チェックあり')
    else: W('A9', '照合/自己採点(.rubric)がない')
    if 'reveal-answer' in html and 'model-answer' in html: P('A10', '模範答案(reveal)あり')
    else: E('A10', '模範答案(details.reveal-answer > .model-answer)がない')
    if 'id="deep-dive"' in html: P('A11', '深掘り層あり')
    else: W('A11', '深掘り層(details#deep-dive)がない')

    # ---- Lexia 周回契約 A12〜A18（自己完結○×が復習プールに乗るか） ----
    cards = extract_divs(html, 'self-check-quiz')
    if len(cards) >= 8: P('A12', f'周回ドリル○× {len(cards)} 枚')
    elif len(cards) >= 1: W('A12', f'周回ドリル○×が少ない（{len(cards)}枚・10〜15推奨）')
    else: E('A12', '周回ドリル(.self-check-quiz)が無い＝周回不能')

    bad_arena = bad_dcv = bad_q = bad_a = bad_btn = meta_hit = 0
    for tag, inner in cards:
        if 'data-arena="1"' not in tag: bad_arena += 1
        mdcv = re.search(r'data-correct-value="(.)"', tag)
        dcv = mdcv.group(1) if mdcv else ''
        if dcv not in ('○', '×'): bad_dcv += 1
        qm = re.search(r'class="quiz-question"[^>]*>(.*?)</p>', inner, re.S)
        qtext = text_only(qm.group(1)) if qm else ''
        if not qtext: bad_q += 1
        if not (re.search(r'class="quiz-answer"', inner) or 'data-explanation=' in tag): bad_a += 1
        vals = re.findall(r'class="quiz-btn"[^>]*data-value="(.)"', inner)
        if set(vals) != {'○', '×'} or (dcv and dcv not in vals): bad_btn += 1
        if qtext and META_RE.search(qtext): meta_hit += 1

    (E if bad_arena else P)('A13', f'data-arena="1" 欠落 {bad_arena} 枚（欠落するとkind=self-checkで復習プール除外）' if bad_arena else '全カード data-arena="1"（kind=arena でプール対象）')
    (E if bad_dcv else P)('A14', f'data-correct-value(○/×) 不正 {bad_dcv} 枚' if bad_dcv else '全カード data-correct-value 正常')
    (E if bad_q else P)('A15', f'.quiz-question 空/欠落 {bad_q} 枚' if bad_q else '全カード設問あり')
    (E if bad_a else P)('A16', f'解説(.quiz-answer/data-explanation) 欠落 {bad_a} 枚' if bad_a else '全カード解説あり')
    (E if bad_btn else P)('A17', f'○/×ボタン data-value 不整合 {bad_btn} 枚' if bad_btn else '全カード ○×ボタン整合')
    (E if meta_hit else P)('A18', f'メタ除去regex該当の設問 {meta_hit} 枚（Lexiaが削除）' if meta_hit else 'メタ除去regex非該当')

    # ---- Lexia 安全制約 A19〜A20 ----
    body_lit = False
    for sm in re.finditer(r'<script\b[^>]*>(.*?)</script>', html, re.S | re.I):
        if '</body>' in sm.group(1): body_lit = True
    (E if body_lit else P)('A19', '<script>内に </body> リテラル（lastIndexOf注入が壊れる）' if body_lit else '<script>内に </body> リテラルなし')
    if re.search(r"closest\('\.quiz-btn'\)|onQuizBtn|\.quiz-btn", html): P('A20', '○×採点JSあり')
    else: W('A20', '○×採点JS(.quiz-btn ハンドラ)が見当たらない')

    # ---- 命名・配置 A21（パスがARIADNE配下のとき） ----
    norm = path.replace('\\', '/')
    if 'ux/000_ARIADNE/' in norm:
        base = os.path.basename(norm)
        if re.match(r'^.+JX\d{3}_ARIADNE\.html$', base): P('A21', f'命名規則OK（{base}）')
        else: W('A21', f'命名が {{科目}}JX{{NNN}}_ARIADNE.html と不一致（{base}）')

    # ---- A22 答案構成パズルエンジン（spec §9・当面 WARNING） ----
    has_engine = ('KP-PUZZLE-BACKFILL' in html) or ('kp-levels' in html and 'kslot' in html)
    if has_engine: P('A22', '答案構成パズルエンジンあり')
    else: W('A22', 'パズルエンジン未実装（canonical 複製 or ariadne-puzzle-backfill.py で付与・spec §9）')

    for line in passes + warns + errors:
        print(line)
    print(f"\n=== ARIADNE 検証: PASS {len(passes)} / WARN {len(warns)} / ERROR {len(errors)} ===")
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
