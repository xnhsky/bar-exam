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

    # ---- A23 教示↔周回ドリル 字面の近接コピー backstop（spec §4・2026-06-22）----
    # 各手の教示（.do＋details.peek 本文）と、その手内の周回ドリル（設問＋解説）の
    # 文字 8-gram 重複率を測る。これは「教示をほぼそのまま貼った」字面コピーの再発検知に限る。
    # ※本質的な重複は“意味の言い換え”（同じ命題を別語で問う＝再認）であり字面検出は不能。
    #   意味重複の排除は spec §4「教示↔ドリル 非重複の原則」のルーブリック（人/LLM判断）で担保する。
    def _ngrams(s, n=8):
        s = re.sub(r'[\s　、。「」（）()・,.]', '', s)
        return set(s[i:i+n] for i in range(len(s) - n + 1)) if len(s) >= n else ({s} if s else set())
    OVERLAP_TH = 0.30
    overlap_hits = []  # (step_title, drill_idx, ratio)
    for stag, sinner in extract_divs(html, 'step'):
        instr = ''
        for dm in re.finditer(r'class="do"[^>]*>(.*?)</p>', sinner, re.S):
            instr += ' ' + text_only(dm.group(1))
        for pm in re.finditer(r'class="peek".*?class="body"[^>]*>(.*?)</details>', sinner, re.S):
            instr += ' ' + text_only(pm.group(1))
        instr_ng = _ngrams(instr)
        if not instr_ng:
            continue
        ttl_m = re.search(r'class="ttl"[^>]*>(.*?)</div>', sinner, re.S)
        stitle = text_only(ttl_m.group(1)) if ttl_m else '(無題の手)'
        for di, (qtag, qinner) in enumerate(extract_divs(sinner, 'self-check-quiz'), 1):
            qm = re.search(r'class="quiz-question"[^>]*>(.*?)</p>', qinner, re.S)
            am = re.search(r'class="quiz-answer"[^>]*>(.*?)</div>', qinner, re.S)
            drill = (text_only(qm.group(1)) if qm else '') + ' ' + (text_only(am.group(1)) if am else '')
            d_ng = _ngrams(drill)
            if not d_ng:
                continue
            ratio = len(d_ng & instr_ng) / len(d_ng)
            if ratio >= OVERLAP_TH:
                overlap_hits.append((stitle, di, ratio))
    if overlap_hits:
        detail = '；'.join(f'「{t}」ドリル{i}(字面{r:.0%})' for t, i, r in overlap_hits[:8])
        W('A23', f'教示の字面コピー疑い {len(overlap_hits)} 枚（転用知識の想起へ書換・spec §4）: {detail}')
    else:
        P('A23', '教示↔ドリルの字面コピーなし（意味重複は spec §4 ルーブリックで担保）')

    # ---- A24 模範答案 問規当結カード（spec §ARIADNE・誌面リスキン・当面 WARNING）----
    ma = extract_divs(html, 'model-answer')
    if ma:
        inner = ma[0][1]
        role_ps = re.findall(r'<p[^>]*class="[^"]*\br-(?:issue|norm|apply|concl)\b', inner)
        total_ps = re.findall(r'<p\b(?![^>]*\bma-h\b)', inner)
        has_css = 'MA-ROLE-RESTYLE' in html
        if not has_css:
            W('A24', '模範答案リスキンCSS未注入（scripts/ariadne-ma-restyle.py で付与）')
        elif len(role_ps) == 0:
            W('A24', f'模範答案の問規当結カード未適用（役割クラス r-issue/r-norm/r-apply/r-concl が0・段落{len(total_ps)}個）')
        else:
            fe = '＋事実/評価語' if ('class="fact"' in inner or 'class="eval"' in inner) else '（事実/評価語スパン未付与）'
            P('A24', f'模範答案 問規当結カード {len(role_ps)} 段落{fe}')

    # ---- A25 深掘り層をアテナ級に（TX 参考条文判例書式・spec §2-7／§11・当面 WARNING）----
    deep = re.search(r'<details id="deep-dive".*?</details>', html, re.S)
    deep_inner = deep.group(0) if deep else ''
    if deep_inner:
        has_case = 'basis-card case-card' in deep_inner or 'case-card' in deep_inner
        has_stat = 'statute-card' in deep_inner
        if has_case and has_stat:
            P('A25', '深掘り層がTX参考条文判例書式（判例case-card＋条文statute-card）でアテナ級')
        else:
            miss = []
            if not has_case: miss.append('判例case-card')
            if not has_stat: miss.append('条文statute-card')
            W('A25', f'深掘り層がアテナ級でない（不足: {"／".join(miss)}・TX書式へ・spec §2-7／§11）')

    # ---- A26 アテナで詳しく（百科事典版へのジャンプ・spec §11・当面 WARNING）----
    ga = re.search(r'class="go-athena"[^>]*data-athena-code="([^"]*)"', html)
    if not ga:
        ga = re.search(r'data-athena-code="([^"]*)"[^>]*class="go-athena"', html)
    if ga and ga.group(1).strip():
        P('A26', f'アテナ版ジャンプボタンあり（targetCode={ga.group(1)}）')
    else:
        W('A26', 'アテナ版ジャンプボタン(.go-athena data-athena-code)がない（postMessage lexia:navigate 連携・spec §11）')

    for line in passes + warns + errors:
        print(line)
    print(f"\n=== ARIADNE 検証: PASS {len(passes)} / WARN {len(warns)} / ERROR {len(errors)} ===")
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
