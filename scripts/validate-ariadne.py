#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate-ariadne.py — ARIADNE（JX 解法ナビ＋周回・Lexia連携）HTML の検証。

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
ATTR_RE_TEMPLATE = r'\b{name}\s*=\s*([\'"])(.*?)\1'
CLASS_RE = re.compile(ATTR_RE_TEMPLATE.format(name='class'), re.I | re.S)
DATA_RX_RE = re.compile(ATTR_RE_TEMPLATE.format(name='data-rx'), re.I | re.S)
DATA_ATHENA_CODE_RE = re.compile(ATTR_RE_TEMPLATE.format(name='data-athena-code'), re.I | re.S)
DATA_ARENA_RE = re.compile(ATTR_RE_TEMPLATE.format(name='data-arena'), re.I | re.S)
DATA_CORRECT_VALUE_RE = re.compile(ATTR_RE_TEMPLATE.format(name='data-correct-value'), re.I | re.S)
DATA_EXPLANATION_RE = re.compile(ATTR_RE_TEMPLATE.format(name='data-explanation'), re.I | re.S)
DATA_VALUE_RE = re.compile(ATTR_RE_TEMPLATE.format(name='data-value'), re.I | re.S)
DATA_RECALL_RE = re.compile(ATTR_RE_TEMPLATE.format(name='data-recall'), re.I | re.S)
ID_RE = re.compile(ATTR_RE_TEMPLATE.format(name='id'), re.I | re.S)
OPEN_TAG_RE = re.compile(r'<[a-zA-Z][\w:-]*\b[^>]*>', re.I | re.S)
DIV_OPEN_RE = re.compile(r'<div\b[^>]*>', re.I | re.S)

def first_attr_value(pattern, text):
    m = pattern.search(text)
    return m.group(2).strip() if m and m.group(2) is not None else ''

def has_class(open_tag, cls):
    classes = first_attr_value(CLASS_RE, open_tag)
    return bool(classes and cls in re.split(r'\s+', classes))

def html_has_class(html, cls):
    return any(has_class(m.group(0), cls) for m in OPEN_TAG_RE.finditer(html))

def has_id(open_tag, expected):
    return first_attr_value(ID_RE, open_tag) == expected

def html_has_id(html, expected):
    return any(has_id(m.group(0), expected) for m in OPEN_TAG_RE.finditer(html))

def id_prefix_count(html, prefix):
    count = 0
    for m in OPEN_TAG_RE.finditer(html):
        value = first_attr_value(ID_RE, m.group(0))
        if value.startswith(prefix):
            count += 1
    return count

def html_has_id_prefix(html, prefix):
    return id_prefix_count(html, prefix) > 0

def class_count(html, cls):
    return sum(1 for m in OPEN_TAG_RE.finditer(html) if has_class(m.group(0), cls))

def first_element_text_by_class(html, tag_name, cls):
    open_re = re.compile(r'<' + re.escape(tag_name) + r'\b[^>]*>', re.I | re.S)
    close_re = re.compile(r'</' + re.escape(tag_name) + r'>', re.I)
    for m in open_re.finditer(html):
        if not has_class(m.group(0), cls):
            continue
        close = close_re.search(html, m.end())
        if close:
            return text_only(html[m.end():close.start()])
    return ''

def element_texts_by_class(html, tag_name, cls):
    texts = []
    open_re = re.compile(r'<' + re.escape(tag_name) + r'\b[^>]*>', re.I | re.S)
    close_re = re.compile(r'</' + re.escape(tag_name) + r'>', re.I)
    for m in open_re.finditer(html):
        if not has_class(m.group(0), cls):
            continue
        close = close_re.search(html, m.end())
        if close:
            texts.append(text_only(html[m.end():close.start()]))
    return texts

def extract_tag_blocks_by_class(html, tag_name, cls):
    blocks = []
    open_re = re.compile(r'<' + re.escape(tag_name) + r'\b[^>]*>', re.I | re.S)
    close_re = re.compile(r'</' + re.escape(tag_name) + r'>', re.I)
    for m in open_re.finditer(html):
        if not has_class(m.group(0), cls):
            continue
        close = close_re.search(html, m.end())
        if close:
            blocks.append((m.group(0), html[m.end():close.start()]))
    return blocks

def extract_tag_block_by_id(html, tag_name, expected_id):
    open_re = re.compile(r'<' + re.escape(tag_name) + r'\b[^>]*>', re.I | re.S)
    close_re = re.compile(r'</' + re.escape(tag_name) + r'>', re.I)
    for m in open_re.finditer(html):
        if not has_id(m.group(0), expected_id):
            continue
        close = close_re.search(html, m.end())
        if close:
            return html[m.start():close.end()]
    return ''

def class_prefix_count(html, tag_name, prefixes):
    count = 0
    open_re = re.compile(r'<' + re.escape(tag_name) + r'\b[^>]*>', re.I | re.S)
    for m in open_re.finditer(html):
        classes = first_attr_value(CLASS_RE, m.group(0))
        if any(c.startswith(prefixes) for c in re.split(r'\s+', classes) if c):
            count += 1
    return count

def attr_values_on_classed_tags(html, cls, pattern):
    vals = []
    for m in OPEN_TAG_RE.finditer(html):
        tag = m.group(0)
        if has_class(tag, cls):
            value = first_attr_value(pattern, tag)
            if value:
                vals.append(value)
    return vals

def go_athena_target(html):
    for m in OPEN_TAG_RE.finditer(html):
        tag = m.group(0)
        if has_class(tag, 'go-athena'):
            target = first_attr_value(DATA_ATHENA_CODE_RE, tag)
            if target:
                return target
    return ''

def extract_divs(html, cls):
    """class に cls を含む <div> を深さ計数で抽出 → [(open_tag, inner_html)]。"""
    blocks = []
    tag_re = re.compile(r'<(/?)div\b', re.I)
    for m in DIV_OPEN_RE.finditer(html):
        if not has_class(m.group(0), cls):
            continue
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
    if html_has_class(html, 'masthead'): P('A3', 'マストヘッドあり')
    else: E('A3', 'マストヘッド(.masthead)がない')
    if html_has_class(html, 'foot'): P('A4', 'フッターあり')
    else: W('A4', 'フッター(.foot)がない')
    prob = extract_divs(html, 'problem')
    if prob and text_only(prob[0][1]): P('A5', '問題文あり')
    else: E('A5', '問題文(.problem)が空/なし')
    steps = extract_divs(html, 'step')
    if len(steps) >= 6: P('A6', f'解法ナビ STEP {len(steps)} 個')
    else: E('A6', f'解法ナビの STEP が少なすぎ（{len(steps)}個・7ステップ想定）')
    if html_has_class(html, 'steps-rail'): P('A7', 'ステッパーあり')
    else: W('A7', 'ステッパー(.steps-rail)がない')
    bone = extract_divs(html, 'bone')
    if bone and text_only(bone[0][1]): P('A8', '骨子あり')
    else: E('A8', '骨子(.bone)が空/なし')
    if html_has_class(html, 'rubric') or html_has_class(html, 'collate'): P('A9', '自己採点チェックあり')
    else: W('A9', '照合/自己採点(.rubric)がない')
    if html_has_class(html, 'reveal-answer') and html_has_class(html, 'model-answer'): P('A10', '模範答案(reveal)あり')
    else: E('A10', '模範答案(details.reveal-answer > .model-answer)がない')
    if html_has_id(html, 'deep-dive'): P('A11', '深掘り層あり')
    else: W('A11', '深掘り層(details#deep-dive)がない')

    # ---- Lexia 周回契約 A12〜A18（自己完結○×が復習プールに乗るか） ----
    cards = extract_divs(html, 'self-check-quiz')
    if len(cards) >= 8: P('A12', f'周回ドリル○× {len(cards)} 枚')
    elif len(cards) >= 1: W('A12', f'周回ドリル○×が少ない（{len(cards)}枚・10〜15推奨）')
    else: E('A12', '周回ドリル(.self-check-quiz)が無い＝周回不能')

    bad_arena = bad_dcv = bad_q = bad_a = bad_btn = meta_hit = 0
    for tag, inner in cards:
        if first_attr_value(DATA_ARENA_RE, tag) != '1': bad_arena += 1
        dcv = first_attr_value(DATA_CORRECT_VALUE_RE, tag)
        if dcv not in ('○', '×'): bad_dcv += 1
        qtext = first_element_text_by_class(inner, 'p', 'quiz-question')
        if not qtext: bad_q += 1
        if not (html_has_class(inner, 'quiz-answer') or DATA_EXPLANATION_RE.search(tag)): bad_a += 1
        vals = attr_values_on_classed_tags(inner, 'quiz-btn', DATA_VALUE_RE)
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
    numbered_iss = [t for t in element_texts_by_class(bone_inner, 'span', 'iss') if re.match(r'【論点' + NUMRE + r'】', t)]
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
        for text in element_texts_by_class(sinner, 'p', 'do'):
            instr += ' ' + text
        for _peek_tag, peek_inner in extract_tag_blocks_by_class(sinner, 'details', 'peek'):
            instr += ' ' + first_element_text_by_class(peek_inner, 'div', 'body')
        instr_ng = _ngrams(instr)
        if not instr_ng:
            continue
        stitle = first_element_text_by_class(sinner, 'div', 'ttl') or '(無題の手)'
        for di, (qtag, qinner) in enumerate(extract_divs(sinner, 'self-check-quiz'), 1):
            drill = first_element_text_by_class(qinner, 'p', 'quiz-question') + ' ' + first_element_text_by_class(qinner, 'div', 'quiz-answer')
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
        role_ps = class_prefix_count(inner, 'p', ('r-issue', 'r-norm', 'r-apply', 'r-concl'))
        total_ps = re.findall(r'<p\b(?![^>]*\bma-h\b)', inner)
        has_css = 'MA-ROLE-RESTYLE' in html
        if not has_css:
            W('A24', '模範答案リスキンCSS未注入（scripts/ariadne-ma-restyle.py で付与）')
        elif role_ps == 0:
            W('A24', f'模範答案の問規当結カード未適用（役割クラス r-issue/r-norm/r-apply/r-concl が0・段落{len(total_ps)}個）')
        else:
            fe = '＋事実/評価語' if (html_has_class(inner, 'fact') or html_has_class(inner, 'eval')) else '（事実/評価語スパン未付与）'
            P('A24', f'模範答案 問規当結カード {role_ps} 段落{fe}')

    # ---- A25 深掘り層をアテナ級に（TX 参考条文判例書式 or アテナ移植・spec §2-7／§11・当面 WARNING）----
    deep_inner = extract_tag_block_by_id(html, 'details', 'deep-dive')
    if deep_inner:
        has_case = html_has_class(deep_inner, 'case-card')
        has_stat = html_has_class(deep_inner, 'statute-card')
        # アテナ移植(graft)形式：athena-graft 内に条文/判例 ref-entry がある
        has_graft = html_has_class(deep_inner, 'athena-graft') and html_has_id_prefix(deep_inner, 'ref-stat') and html_has_id_prefix(deep_inner, 'ref-case')
        if has_graft:
            ns = id_prefix_count(deep_inner, 'ref-stat'); nc = id_prefix_count(deep_inner, 'ref-case'); nd = id_prefix_count(deep_inner, 'ref-doctrine')
            P('A25', f'深掘り層がアテナ移植（条文{ns}・判例{nc}・学説{nd}の完全プロファイル）でアテナ級')
        elif has_case and has_stat:
            P('A25', '深掘り層がTX参考条文判例書式（判例case-card＋条文statute-card）でアテナ級')
        else:
            miss = []
            if not has_case: miss.append('判例case-card')
            if not has_stat: miss.append('条文statute-card')
            W('A25', f'深掘り層がアテナ級でない（不足: {"／".join(miss)}・TX書式 or アテナ移植へ・spec §2-7／§11）')

    # ---- A26 アテナで詳しく（百科事典版へのジャンプ・spec §11）----
    ga = go_athena_target(html)
    if ga:
        P('A26', f'アテナ版ジャンプボタンあり（targetCode={ga}）')
    else:
        E('A26', 'アテナ版ジャンプボタン(.go-athena data-athena-code)がない（postMessage lexia:navigate 連携・spec §11）')

    # ---- A27 答案構成の作法（教授のひとことコラム＋ステップ別周回ドリル・spec §12・2026-06-22・当面 WARNING）----
    bc = extract_divs(html, 'bc-wrap')
    if bc:
        body = bc[0][1]
        cols = class_count(body, 'bc-col')          # 🎓 教授のひとこと（5ステップ）
        quizzes = class_count(body, 'self-check-quiz')        # ステップ別 周回ドリル
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
    recall_cards = [(t, i) for (t, i) in cards if first_attr_value(DATA_RECALL_RE, t)]
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
            rxv = first_attr_value(DATA_RX_RE, tag)
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

    for line in passes + warns + errors:
        print(line)
    print(f"\n=== ARIADNE 検証: PASS {len(passes)} / WARN {len(warns)} / ERROR {len(errors)} ===")
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
