#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate-ariadne.py — ARIADNE v1.2.0（JX 解法ナビ＋周回・Lexia連携）HTML の検証。

ARIADNE は ATHENA（百科事典型 JX 正典）と役割分担する別正典。
本検証器は「構造（誌面の骨格）」「Lexia 周回契約（自己完結○×が復習プールに乗るか）」
「Lexia 安全制約（</body>リテラル・メタ除去regex）」を機械検査する。

使い方:  python scripts/validate-ariadne.py outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html
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
    if len(steps) >= 6: P('A6', f'解法ナビ STEP {len(steps)} 個')
    else: E('A6', f'解法ナビの STEP が少なすぎ（{len(steps)}個・7ステップ想定）')
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
    if 'ux/001_ARIADNE/' in norm:
        base = os.path.basename(norm)
        if re.match(r'^.+JX\d{3}_ARIADNE\.html$', base): P('A21', f'命名規則OK（{base}）')
        else: W('A21', f'命名が {{科目}}JX{{NNN}}_ARIADNE.html と不一致（{base}）')

    # ---- A22 答案構成パズルエンジン（spec §9・当面 WARNING） ----
    has_engine = ('KP-PUZZLE-BACKFILL' in html) or ('kp-levels' in html and 'kslot' in html)
    if has_engine: P('A22', '答案構成パズルエンジンあり')
    else: W('A22', 'パズルエンジン未実装（canonical 複製 or ariadne-puzzle-backfill.py で付与・spec §9）')

    # ---- A28 論点チップの冠番号ネタバレ禁止（spec §9-3・2026-06-23）----
    # 本物の論点チップ <span class="iss">【論点①】… が番号付きだと、無番号おとり
    # （iss:【論点】…）と番号の有無で見分けられ、配置順(①→第1)も丸見え＝ネタバレ。
    # 本物 .iss・おとり双方とも 【論点】… で統一する（番号は禁止）。
    NUMRE = r'[0-9０-９①-⑳]+'
    bone_tag = bone[0][0] if bone else ''
    bone_inner = bone[0][1] if bone else ''
    numbered_iss = re.findall(r'class="iss">【論点' + NUMRE + r'】', bone_inner)
    numbered_dcv = re.findall(r'iss:【論点' + NUMRE + r'】', bone_tag)
    nbad = len(numbered_iss) + len(numbered_dcv)
    if nbad:
        E('A28', f'論点チップに冠番号【論点①②…】が {nbad} 件（おとりと識別可能＝ネタバレ）'
                 '。scripts/ariadne-iss-denumber-backfill.py で除去し【論点】に統一')
    else:
        P('A28', '論点チップに冠番号なし（おとりと識別不能＝ネタバレ防止）')

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

    # ---- A25 深掘り層をアテナ級に（TX 参考条文判例書式 or アテナ移植・spec §2-7／§11・当面 WARNING）----
    deep = re.search(r'<details id="deep-dive".*?</details>', html, re.S)
    deep_inner = deep.group(0) if deep else ''
    if deep_inner:
        has_case = 'case-card' in deep_inner
        has_stat = 'statute-card' in deep_inner
        # アテナ移植(graft)形式：athena-graft 内に条文/判例 ref-entry がある
        has_graft = 'athena-graft' in deep_inner and 'id="ref-stat' in deep_inner and 'id="ref-case' in deep_inner
        if has_graft:
            ns = len(re.findall(r'id="ref-stat', deep_inner)); nc = len(re.findall(r'id="ref-case', deep_inner)); nd = len(re.findall(r'id="ref-doctrine', deep_inner))
            P('A25', f'深掘り層がアテナ移植（条文{ns}・判例{nc}・学説{nd}の完全プロファイル）でアテナ級')
        elif has_case and has_stat:
            P('A25', '深掘り層がTX参考条文判例書式（判例case-card＋条文statute-card）でアテナ級')
        else:
            miss = []
            if not has_case: miss.append('判例case-card')
            if not has_stat: miss.append('条文statute-card')
            W('A25', f'深掘り層がアテナ級でない（不足: {"／".join(miss)}・TX書式 or アテナ移植へ・spec §2-7／§11）')

    # ---- A26 アテナで詳しく（百科事典版へのジャンプ・spec §11）----
    ga = re.search(r'class="go-athena"[^>]*data-athena-code="([^"]*)"', html)
    if not ga:
        ga = re.search(r'data-athena-code="([^"]*)"[^>]*class="go-athena"', html)
    if ga and ga.group(1).strip():
        P('A26', f'アテナ版ジャンプボタンあり（targetCode={ga.group(1)}）')
    else:
        E('A26', 'アテナ版ジャンプボタン(.go-athena data-athena-code)がない（postMessage lexia:navigate 連携・spec §11）')

    # ---- A27 答案構成の作法（教授のひとことコラム＋ステップ別周回ドリル・spec §12・2026-06-22・当面 WARNING）----
    bc = extract_divs(html, 'bc-wrap')
    if bc:
        body = bc[0][1]
        cols = body.count('class="bc-col"')          # 🎓 教授のひとこと（5ステップ）
        quizzes = body.count('self-check-quiz')        # ステップ別 周回ドリル
        if cols >= 5 and quizzes >= 5:
            P('A27', f'答案構成の作法あり（🎓教授のひとこと {cols}・周回ドリル {quizzes}）')
        else:
            W('A27', f'答案構成の作法が不完全（コラム {cols}・ドリル {quizzes}・各5想定・spec §12）')
    else:
        W('A27', '答案構成の作法(.bc-wrap)が無い（canonical 複製で付与・spec §12）')

    # ---- A29 想起カード→対応RX論証カードのリンク（data-rx・Lexia LXA_FEAT_008・2026-06-25）----
    # 各想起カード（data-recall）に、その論点に対応する RX 論証カードのコードを data-rx で持たせる。
    # Lexia は想起の誤答時、この RX を復習プールへ注入する（弱点RXの失敗駆動レビュー）。
    # 移行期は欠落=WARN。値の科目/JX不整合・参照先RX不在=ERROR（誤リンク＝別論点RXを注入する事故を防ぐ）。
    abase = os.path.basename(norm)
    mfile = re.match(r'^(.+?)JX(\d{3})_ARIADNE\.html$', abase)
    recall_cards = [(t, i) for (t, i) in cards if 'data-recall' in t]
    if mfile and recall_cards:
        subj, num = mfile.group(1), mfile.group(2)        # 例 ('刑','004')
        rx_pat = re.compile(r'^' + re.escape(subj) + r'RX' + num + r'_\d+$')
        # 同JX配下のRX出力ディレクトリ（実在すれば参照先の存在も検査）
        rx_dir = None
        if 'ux/001_ARIADNE/' in norm:
            cand = os.path.dirname(norm).replace('ux/001_ARIADNE/', 'ux/002_RX/') + '/' + subj + 'JX' + num
            if os.path.isdir(cand):
                rx_dir = cand
        miss, badfmt, notfound = 0, [], []
        for tag, _inner in recall_cards:
            mrx = re.search(r'data-rx="([^"]*)"', tag)
            rxv = mrx.group(1).strip() if mrx else ''
            if not rxv:
                miss += 1
            elif not rx_pat.match(rxv):
                badfmt.append(rxv)
            elif rx_dir and not os.path.isfile(rx_dir + '/' + rxv + '.html'):
                notfound.append(rxv)
        if badfmt or notfound:
            parts = []
            if badfmt: parts.append(f'科目/JX不整合 {len(badfmt)}件({"・".join(badfmt[:5])})')
            if notfound: parts.append(f'参照先RX不在 {len(notfound)}件({"・".join(notfound[:5])})')
            E('A29', f'想起カードの data-rx 異常: {"／".join(parts)}（誤リンク＝Lexiaが別論点のRXを注入）')
        elif miss == len(recall_cards):
            # 1枚も刻まれていない＝未バックフィル。総論カードのみで対応RXが無い問題もここに含むが
            # 人手確認を促す意味で WARN（移行期）。
            W('A29', f'想起カード {len(recall_cards)}枚すべて data-rx 欠落（未バックフィル）'
                     '（scripts/ariadne-backfill-rx-link.py／spec §9-5・移行期WARN）')
        elif miss:
            # 一部に data-rx あり＝バックフィル済。残りの欠落は総論/解法の型/汎用想起で
            # 対応RXが無く意図的に省略したもの（spec §9-5「対応RX無しは省略可」）。
            P('A29', f'想起カード {len(recall_cards)-miss}/{len(recall_cards)} 枚に対応RX data-rx'
                     f'（残 {miss} 枚は総論/汎用で省略）' + ('＋参照先実在' if rx_dir else ''))
        else:
            P('A29', f'全想起カード({len(recall_cards)}枚)に対応RX data-rx あり'
                     + ('＋参照先実在' if rx_dir else ''))

    # ---- A30 正典CSS回帰防止（問題文字下げ・2026-06-29）----
    # CASE/問題本文は、バッジや見出し以外の本文として1字下げを維持する。
    # text-indent:0 への退行は、正典指定後の読みづらさ再発として ERROR にする。
    pq_rule = re.search(r'\.problem \.pq\{[^}]*\}', html)
    if pq_rule:
        pq_css = re.sub(r'\s+', '', pq_rule.group(0))
        if 'text-indent:0' in pq_css:
            E('A30', '問題文(.problem .pq)が text-indent:0（本文字下げの正典から退行）')
        elif 'text-indent:1em' in pq_css:
            P('A30', '問題文(.problem .pq)は1字下げ')
        else:
            W('A30', '問題文(.problem .pq)の字下げ指定が非標準（正典は text-indent:1em）')
    else:
        W('A30', '問題文CSS(.problem .pq)が見つからない（本文字下げの自動確認不可）')

    # ---- A31 正典回帰防止（拾う文言2カラム＋下書きカード構造・2026-06-30）----
    # 新正典は「人物関係図・時系列＝上段2カラム／拾う文言＝全幅」。
    # cue の先頭に装飾記号を本文として出す退行も ERROR。
    compact_html = re.sub(r'\s+', '', html)
    old_wide_facts = (
        'grid-template-columns:minmax(24em,1.35fr)minmax(18em,1fr);column-gap:24px'
        in compact_html
    )
    facts_grid = re.search(r'\.facts li\{[^}]*display:grid[^}]*\}', html)
    a31_errors = []
    if old_wide_facts:
        a31_errors.append('拾う文言(.facts li)が旧ワイド2カラム（右余白過多・左右が離れすぎ）')
    elif facts_grid:
        facts_css = re.sub(r'\s+', '', facts_grid.group(0))
        has_compact_cols = (
            'grid-template-columns:minmax(18em,32em)minmax(16em,28em)' in facts_css
            and 'column-gap:18px' in facts_css
            and 'justify-content:start' in facts_css
        )
        if not has_compact_cols:
            a31_errors.append('拾う文言2カラムが正典近接型でない（列幅・間隔・左寄せを確認）')

    draft_cards = re.findall(
        r'<div\s+class="draft-card([^"]*)">\s*<(?:p|div)\s+class="ct">([^<]*)',
        html,
        flags=re.S,
    )
    has_relation_card = False
    has_facts_card = False
    for class_suffix, title in draft_cards:
        classes = set(class_suffix.split())
        is_relation_card = (
            '①' in title
            or ('関係' in title and '拾う文言' not in title and '時系列' not in title)
        )
        is_facts_card = '③' in title or '拾う文言' in title
        if is_relation_card:
            has_relation_card = True
            if 'span2' in classes:
                a31_errors.append('①関係図カードが全幅(span2)になっている（正典は時系列との2カラム）')
        if is_facts_card:
            has_facts_card = True
            if 'span2' not in classes:
                a31_errors.append('拾う文言カードが全幅(span2)でない（正典は下段全幅）')
    if draft_cards and (has_relation_card or has_facts_card) and (not has_relation_card or not has_facts_card):
        a31_errors.append('下書きカード（人物関係図／拾う文言）の正典構造を確認できない')

    if re.search(r'<span\s+class="cue">\s*(?:\.{3}|…)', html):
        a31_errors.append('拾う文言の理由(cue)先頭に「...」または「…」が本文として出ている')

    if a31_errors:
        E('A31', ' / '.join(a31_errors))
    else:
        P('A31', '拾う文言2カラムは正典近接型＋下書き構造固定')

    # ---- A32 正典回帰防止（照合〜深掘りを骨子コンテナ内へ固定・2026-06-30）----
    # 自己採点・模範答案 reveal・深掘りは、背景上に浮かせず骨子コンテナ内に収める。
    a32_errors = []
    collate_rule = re.search(r'\.collate\{[^}]*\}', html)
    reveal_rule = re.search(r'details\.reveal-answer\{[^}]*\}', html)
    collate_css = re.sub(r'\s+', '', collate_rule.group(0)) if collate_rule else ''
    reveal_css = re.sub(r'\s+', '', reveal_rule.group(0)) if reveal_rule else ''
    self_idx = html.find('<!-- 照合・自己採点 -->')
    deep_idx = html.find('<!-- 深掘り -->')
    main_idx = html.find('</main>', deep_idx if deep_idx >= 0 else 0)
    if not collate_css:
        a32_errors.append('照合カード(.collate)のCSSが見つからない')
    elif 'max-width:calc(var(--maxw)-120px)' in collate_css or 'width:100%' in collate_css:
        a32_errors.append('照合カード(.collate)が旧・外置き幅調整CSSのまま')
    elif 'margin:0014px' not in collate_css:
        a32_errors.append('照合カード(.collate)が骨子コンテナ内の正典余白でない')
    if not reveal_css:
        a32_errors.append('模範答案reveal(details.reveal-answer)のCSSが見つからない')
    elif 'max-width:calc(var(--maxw)-120px)' in reveal_css or 'width:100%' in reveal_css:
        a32_errors.append('模範答案revealが旧・外置き幅調整CSSのまま')
    elif 'margin:14px00' not in reveal_css:
        a32_errors.append('模範答案revealが骨子コンテナ内の正典余白でない')
    if '.skeleton-check-sep{' not in html or '<div class="skeleton-check-sep"></div>' not in html:
        a32_errors.append('照合前の骨子コンテナ内セパレータ(.skeleton-check-sep)がない')
    if self_idx < 0 or deep_idx < 0 or self_idx > deep_idx or main_idx < 0:
        a32_errors.append('照合セクションと深掘りセクションの順序が確認できない')
    else:
        between_self_deep = html[self_idx:deep_idx]
        deep_to_main = html[deep_idx:main_idx + len('</main>')]
        if '\n\n  </div>\n\n  <div class="to-top"><a href="#top">▲ 先頭へ戻る</a></div>\n  <!-- 深掘り -->' in between_self_deep:
            a32_errors.append('深掘り前に骨子コンテナが閉じている')
        if '\n\n  </div>\n\n  <!-- 深掘り -->' in between_self_deep:
            a32_errors.append('深掘り前に骨子コンテナが閉じている')
        if '</details>\n\n  </div>\n\n  </main>' not in deep_to_main:
            a32_errors.append('深掘り終了後に骨子コンテナが閉じられていない')
    if a32_errors:
        E('A32', ' / '.join(a32_errors))
    else:
        P('A32', '照合・模範答案・深掘りは骨子コンテナ内に固定')

    # ---- A33 役割別品質ゲート（2026-07-01）----
    # ARIADNE は「次に何をするか」を再現する教材なので、汎用誘導・薄い解説・骨子欠落を ERROR にする。
    a33_errors = []
    bad_generic = [
        '問題文のキーワード',
        'まず考えよう',
        '重要です。',
        '確認しましょう。',
    ]
    leaked = [p for p in bad_generic if p in html]
    if leaked:
        a33_errors.append('汎用誘導文が残存: ' + '／'.join(leaked))

    for si, (stag, sinner) in enumerate(extract_divs(html, 'step'), 1):
        do_texts = [text_only(m.group(1)) for m in re.finditer(r'class="do"[^>]*>(.*?)</p>', sinner, re.S)]
        for di, dt in enumerate(do_texts, 1):
            if len(dt) < 18:
                a33_errors.append(f'STEP{si} .do {di} が短すぎる（切断軸不足）')
            if re.fullmatch(r'.*(確認する|考える|整理する)[。.]?', dt) and not re.search(r'条|罪|規範|要件|事実|結論|違法|責任|故意|因果|共犯|罪数', dt):
                a33_errors.append(f'STEP{si} .do {di} が汎用作業指示のみ')

    for ci, (_tag, inner) in enumerate(cards, 1):
        qm = re.search(r'class="quiz-question"[^>]*>(.*?)</p>', inner, re.S)
        am = re.search(r'class="quiz-answer"[^>]*>(.*?)</div>', inner, re.S)
        qtext = text_only(qm.group(1)) if qm else ''
        atext = text_only(am.group(1)) if am else ''
        if re.search(r'正解はどれ|本問の正解|正解の組', qtext):
            a33_errors.append(f'周回ドリル{ci} が正解再問型')
        if len(atext) < 18:
            a33_errors.append(f'周回ドリル{ci} の解説が短すぎる')
        if atext and not re.search(r'から|ため|ので|要件|条|判例|規範|結論|成立|不成立|故意|違法|責任|因果|客体|射程|区別|限ら|正当防衛|緊急避難|阻却|否定|肯定|対象外|無効|有効|減点|条文|主体|過失|未遂|既遂|法益|補充性|相当性|公共|評価|検討対象|実益|配点|自殺|承諾|共犯|急迫|不正|侵害|継続|終了|加害|意思|可能性|時間的|場所的|接着|総合|判断|失点|罪名|行為|検討|漏れ|起動|詐欺|傷害|殺人|正犯|道具|利用|定義|形態', atext):
            a33_errors.append(f'周回ドリル{ci} の解説に理由・要件・結論の手掛かりが不足')

    if bone_inner:
        if 'matrix-bone' in bone_tag:
            # legacy matrix-bone（§9-2・§17 で旧型指定）：問規当結の4マーカーを確認
            for marker, label in [
                ('class="iss"', '論点'),
                ('class="krule"', '規範'),
                ('class="kfact"', 'あてはめキー事実'),
                ('<u>', '結論'),
            ]:
                if marker not in bone_inner:
                    a33_errors.append(f'答案構成骨子に {label} マーカーが不足')
        else:
            # simple-bone（§17 正典）：論点＋結論を最低要件
            for marker, label in [
                ('class="iss"', '論点'),
                ('<u>', '結論'),
            ]:
                if marker not in bone_inner:
                    a33_errors.append(f'答案構成骨子（simple-bone）に {label} マーカーが不足')

    if ma:
        inner = ma[0][1]
        role_count = len(re.findall(r'<p[^>]*class="[^"]*\br-(?:issue|norm|apply|concl)\b', inner))
        apply_blocks = re.findall(r'<p[^>]*class="[^"]*\br-apply\b[^"]*"[^>]*>(.*?)</p>', inner, re.S)
        if role_count == 0:
            a33_errors.append('模範答案に問規当結の役割クラスがない')
        if apply_blocks:
            thin_apply = 0
            for block in apply_blocks:
                if 'class="fact"' not in block and 'class="eval"' not in block:
                    thin_apply += 1
            if thin_apply == len(apply_blocks):
                a33_errors.append('模範答案のあてはめ段落に fact/eval マーカーがない')

    if a33_errors:
        E('A33', ' / '.join(a33_errors[:12]) + (f' / 他{len(a33_errors)-12}件' if len(a33_errors) > 12 else ''))
    else:
        P('A33', '役割別品質ゲート通過（汎用誘導・薄いドリル・骨子欠落なし）')

    # ---- A34 骨子 SIMPLE-BONE 正典・matrix-bone 旧型検出（§17・2026-07-02）----
    # 骨子は simple 型 .bone が正典（刑JX001 型）。旧 .bone.matrix-bone（問規当結グリッド）は
    # WARNING で移行残を可視化する（既存出力は順次移行のため ERROR にしない）。
    if 'matrix-bone' in bone_tag:
        W('A34', '骨子が旧型 .bone.matrix-bone（問規当結グリッド）＝§17 で simple 型 .bone へ差し戻し済み。内容保持のまま simple `.bone`（刑JX001 型）へ要移行')
    elif bone_inner:
        P('A34', '骨子は simple 型 .bone（§17 正典）')

    # ---- A35 深掘りテンプレ流用検出（別問題の人物記号混入＝018型・§11/§4・2026-07-02）----
    # 深掘り層に、本問（.cast/問題文/模範答案/骨子/解法ナビ）に一切登場しない人物記号が
    # 「本問の◯」「◯：」等の強い文脈で使われていたら、別問題からの深掘り丸ごと流用の疑い＝ERROR。
    deep = extract_divs(html, 'deep-body')
    if deep:
        deep_full = deep[0][0] + deep[0][1] + '</div>'
        rest_text = text_only(html.replace(deep_full, ''))
        deep_text = text_only(deep[0][1])
        PERSON = ['甲', '乙', '丙', '丁', '戊', 'Ｘ', 'Ｙ', 'Ｚ', 'Ｖ', 'Ｗ', 'X', 'Y', 'Z', 'V', 'W']
        leaked = []
        for p in PERSON:
            if p in rest_text:
                continue  # 本問に登場する人物は流用でない
            ctx = re.findall(re.escape(p) + r'(?:は|が|を|に|の|も|へ|と|、|：)', deep_text)
            strong = ('本問の' + p) in deep_text or (p + '：') in deep_text or len(ctx) >= 3
            if strong:
                leaked.append(f'{p}(深掘り{len(ctx)}箇所)')
        if leaked:
            E('A35', '深掘り層に本問(.cast/問題文/模範答案)へ一切出ない人物記号が強い文脈で出現＝別問題の深掘り流用の疑い: ' + '／'.join(leaked) + '（元JXから本問論点で再鋳造すること）')
        else:
            P('A35', '深掘り層に本問外の人物記号なし（テンプレ流用の兆候なし）')

    # ---- A36 版スタンプ整合（旧版残置検出・§17・2026-07-02・WARN）----
    old_ver = sorted(set(re.findall(r'ARIADNE v(?:0\.\d+|1\.0\.\d+|1\.1\.\d+)[0-9A-Za-z .\-]*', html)))
    if old_ver:
        W('A36', '旧版スタンプ残置（現行は ARIADNE v1.2.0 PLACEHOLDER-LOCK・CSS先頭/フッター/lexia-genmeta を更新）: ' + '／'.join(v.strip() for v in old_ver[:5]))
    elif 'ARIADNE v1.2.0' not in html:
        W('A36', '版スタンプに ARIADNE v1.2.0 が見当たらない（genmeta/フッター/CSS へ現行版を刻む）')
    else:
        P('A36', '版スタンプは現行 ARIADNE v1.2.0')

    # ---- A37 未定義 box/card クラス（.warn-box 等の素描画検出・2026-07-02・WARN）----
    style_css = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S))
    body_html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    SUSPECT = ['warn-box', 'note-box', 'danger-box', 'success-box', 'info-box', 'tip-box', 'caution-box']
    undef = [c for c in SUSPECT if re.search(r'class="[^"]*\b' + c + r'\b', body_html) and ('.' + c) not in style_css]
    if undef:
        W('A37', 'body で使う box クラスが <style> 未定義＝枠なし素描画: ' + '／'.join(undef) + '（.key-box/.note 等へ寄せる）')
    else:
        P('A37', '未定義の box/card クラスなし')

    # ---- A38 下書き問題文の逐語（§9-4・.draft-problem ≒ .problem .pq）----
    dp = extract_divs(html, 'draft-problem')
    if dp and prob:
        pq_matches = re.findall(r'<p class="pq"[^>]*>(.*?)</p>', prob[0][1], re.S)
        pq_text = text_only(' '.join(pq_matches))
        dp_text = text_only(dp[0][1])
        if pq_text and dp_text and len(dp_text) < 0.85 * len(pq_text):
            W('A38', f'.draft-problem が .problem .pq より圧縮（{len(dp_text)}字<{len(pq_text)}字）＝原文逐語でない（§9-4・一行圧縮は .draft-digest 側へ）')
        elif pq_text and dp_text:
            P('A38', '.draft-problem は .problem .pq の逐語相当')

    # ---- A39 答案構成の作法 bc-inst の2カラム（.bi ラッパ・§12-1・WARN）----
    bcinst = extract_divs(html, 'bc-inst')
    p_bcinst = len(re.findall(r'<p[^>]*class="[^"]*\bbc-inst\b', html))
    if bcinst or p_bcinst:
        nobi = sum(1 for _t, inner in bcinst if 'class="bi"' not in inner) + p_bcinst
        if nobi:
            W('A39', f'.bc-inst が .bi 2カラム未実装（{nobi}箇所）＝ラベル横に本文直置き（§12-1・<div class="bi">本文</div> で包む）')
        else:
            P('A39', f'.bc-inst {len(bcinst)}件すべて .bi 2カラム')

    for line in passes + warns + errors:
        print(line)
    print("NOTE: PASS は構造・表示ゲートの通過です。最新法令・判例・学説（新旧差分時の立法経緯・改正経緯を含む）は spec/jx-ariadne-v1.2.0-core.md の最高エフォートレビューを別途必須とします。")
    print(f"\n=== ARIADNE 検証: PASS {len(passes)} / WARN {len(warns)} / ERROR {len(errors)} ===")
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
