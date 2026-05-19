#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v8.11.6 自己検証スクリプト（中程度版）

対象範囲：
  S1〜S5    タグ開閉バランス
  S7        id 重複
  S8        href リンク先存在
  S10〜S14  PART 構造
  S15〜S17  answer-area 必須属性 / sub-card
  S20〜S22  ref-stat/ref-case/ref-backlinks
  S38       A-2 直後スポイラー禁止
  S46       DOM 骨格逐語適用（sec-icon 等）
  S51       footer-spec バージョンと feature-tag
  S60〜S63  AP-24 / K302-16 検出
  S64       §24 readability layer 6 サブセクション
  S65       §24-6 hanging 構造
  S66       PART 順序（basis が PART B 後・PART C 前）
  S67       font-weight 改訂検証 + AP-26/27/28 検出
  S68       final-answer hidden 属性 (AP-30 検出・v8.11.1 新規)
  S69       §22-quater-3 CSS パッチ存在 (AP-31 検出・v8.11.1 新規)
  S70       fa-summary 内「正解はN」リテラル禁止 (AP-32 検出・v8.11.1 新規)
  S71       answer-instruction canonical 文言 (AP-33 検出・v8.11.2 新規)
  S72       reveal-answer-btn 存在 (AP-34 検出・v8.11.2 新規)
  S73       data-answer-type 整合性 (AP-35 検出・v8.11.3 新規)
  S74       PART A / data-explanation の正解値リテラル禁止 (AP-36/37 検出・v8.11.4 新規)
  S75       FA answer-num が正解の数字のみ (AP-38 検出・v8.11.4 新規)
  S76       PART A <strong>N（XX）</strong> + ox-grid FA 統一 (AP-39/40 検出・v8.11.5 新規)
  S77       script ブロック内に body 閉じタグ文字列が含まれない (AP-41 検出・v8.11.6-hotfix1 新規)
            ※ host側の正規表現注入を誤動作させない為のガード
            ※ クイズハンドル・リンクジャンプが iframe 内で完全に死ぬ重大バグ防止

使い方：
  python scripts/validate.py outputs/ktx/K302.html
  python scripts/validate.py outputs/ktx/K302.html --verbose
"""

import sys
import re
import argparse
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。以下を実行してインストールしてください：")
    print("  pip install beautifulsoup4")
    sys.exit(1)


# ============================================================
# ヘルパー関数
# ============================================================

def count_tag_pairs(html, tag):
    """タグの開閉バランスをチェック"""
    opens = len(re.findall(f'<{tag}[\\s>]', html, re.IGNORECASE))
    closes = len(re.findall(f'</{tag}>', html, re.IGNORECASE))
    return opens, closes


def get_style_text(soup):
    """<style> ブロック全体のテキスト連結を取得"""
    styles = soup.find_all('style')
    return '\n'.join(s.get_text() for s in styles)


def get_script_text(soup):
    """<script> ブロック全体のテキスト連結を取得"""
    scripts = soup.find_all('script')
    return '\n'.join(s.get_text() for s in scripts)


def normalize_css(text):
    """CSS テキストから空白を除去（簡易マッチ用）"""
    return re.sub(r'\s', '', text)


def find_css_rule_block(style_text, selector):
    """CSS から指定セレクタのルールブロックを抽出（{ から } まで）"""
    escaped = re.escape(selector)
    pattern = rf'{escaped}\s*\{{([^}}]*)\}}'
    m = re.search(pattern, style_text)
    return m.group(1) if m else None


# ============================================================
# 検証チェック関数群
# ============================================================

def check_S1_S5_tag_balance(html, results):
    """S1〜S5: タグ開閉バランス"""
    tags = [('div', 'S1'), ('section', 'S2'), ('a', 'S3'), ('span', 'S4'), ('p', 'S5')]
    for tag, sid in tags:
        opens, closes = count_tag_pairs(html, tag)
        if opens != closes:
            results.append((sid, 'ERROR', f'<{tag}> 開閉不一致 (open={opens}, close={closes})'))


def check_S7_duplicate_ids(soup, results):
    """S7: id 重複なし"""
    ids = [el.get('id') for el in soup.find_all(id=True)]
    seen = set()
    dups = set()
    for i in ids:
        if i in seen:
            dups.add(i)
        seen.add(i)
    if dups:
        results.append(('S7', 'ERROR', f'id 重複: {sorted(dups)}'))


def check_S8_href_resolution(soup, results):
    """S8: href="#X" の X がすべて id で実在"""
    ids = {el.get('id') for el in soup.find_all(id=True) if el.get('id')}
    bad = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('#') and len(href) > 1:
            target = href[1:]
            if target not in ids and target != 'top':
                bad.append(href)
    if bad:
        if '#top' in bad and not soup.find(id='top'):
            results.append(('S8', 'ERROR', '<body id="top"> が存在しない'))
        bad_unique = list(dict.fromkeys(b for b in bad if b != '#top'))
        if bad_unique:
            sample = bad_unique[:10]
            results.append(('S8', 'WARN', f'未解決リンク {len(bad_unique)} 件: {sample}'))


def check_S10_four_parts(soup, results):
    """S10: 4 PART すべて存在"""
    part_titles = soup.select('.part-title')
    if len(part_titles) < 4:
        results.append(('S10', 'ERROR', f'part-title 数 = {len(part_titles)} (期待値: 4)'))


def check_S11_part_a_sections(soup, results):
    """S11: PART A に 2 section（A-1, A-2）← v8.11.0 改訂"""
    part_a = soup.find(id='part-a')
    answer_area = soup.find(id='answer-area')
    missing = []
    if not part_a:
        missing.append('part-a')
    if not answer_area:
        missing.append('answer-area')
    if missing:
        results.append(('S11', 'ERROR', f'PART A section 欠落: {missing}'))


def _derive_cv_info(soup):
    """answer-area の data-correct-value から (mode, n_choices, n_correct) を導出。
    - mode: 'ox-grid' | 'multi' | 'single' | 'fill-in' | 'unknown'
    - n_choices: 選択肢総数 N（multi/single/fill-in は 5 固定、ox-grid は cv の桁数）
    - n_correct: 正解数 K（multi はカンマ区切り要素数、ox-grid は cv 桁数、single は 1、
                          fill-in は埋まっている空欄数 = '=' 区切りペア数）
    取得できなければ既定 ('ox-grid', 5, 5) にフォールバック。
    fill-in: data-answer-type='fill-in' で識別し、cv は 'A=5,B=7,C=3,D=6' 形式
             (slotmap §6.6 §2.4)。"""
    answer_area = soup.find(id='answer-area')
    if not answer_area:
        return ('ox-grid', 5, 5)
    aa_div = answer_area.find(class_='answer-area')
    if not aa_div:
        return ('ox-grid', 5, 5)
    cv = aa_div.get('data-correct-value', '')
    # data-answer-type で 新形式 (fill-in / ox3comb8) を最優先判定
    # (cv パターンだけでは既存 single / multi と区別不能なため)
    at_attr = aa_div.get('data-answer-type', '')
    if at_attr == 'fill-in':
        pairs = [p for p in cv.split(',') if p.strip()] if cv else []
        return ('fill-in', 5, len(pairs))
    # ox3comb8 (slotmap §6.7): 3 記述 + 1〜8 組合せ単一選択
    if at_attr == 'ox3comb8':
        return ('ox3comb8', 3, 1)
    if not cv:
        return ('ox-grid', 5, 5)
    if ',' in cv:
        parts = [p.strip() for p in cv.split(',') if p.strip()]
        return ('multi', 5, len(parts))
    if re.match(r'^[12]{2,}$', cv):
        return ('ox-grid', len(cv), len(cv))
    if re.match(r'^\d+$', cv):
        return ('single', 5, 1)
    return ('unknown', 5, 5)


def _derive_expected_choice_count(soup):
    """既存 API 互換: 期待 choice-section 数 N を返す。
    ox-grid 系では cv 桁数、multi/single 系では 5（template 固定）。"""
    _, n, _ = _derive_cv_info(soup)
    return n


def check_S12_part_b_choices(soup, results):
    """S12: PART B に N choice-section。mode 別の三者一致検査も実施。
    - ox-grid: choice-section 数 == ox-row 数 == cv 桁数（N）
    - multi:   choice-section 数 == answer-slot 数 == 5（template 固定）、
               K=cv のカンマ区切り要素数は K <= N を要件とする"""
    mode, n, k = _derive_cv_info(soup)
    choices = [soup.find(id=f'choice-{i}') for i in range(1, n + 1)]
    missing = [i for i, c in enumerate(choices, 1) if c is None]
    if missing:
        results.append(('S12', 'ERROR', f'choice-section 欠落: choice-{missing} (mode={mode}, 期待 N={n})'))
    # 余分な choice-{N+1..} が無いことを確認（add-only 拡張 — ox-grid-5 で N=5 の挙動は不変）
    extra = []
    for i in range(n + 1, 11):
        if soup.find(id=f'choice-{i}'):
            extra.append(i)
    if extra:
        results.append(('S12', 'ERROR',
                       f'余分な choice-section 検出: choice-{extra} (mode={mode}, 期待 N={n})'))
    # mode 別の三者一致 sanity check
    actual_choice_sections = soup.select('section[id^="choice-"]')
    n_sections = len(actual_choice_sections)
    if mode == 'ox-grid':
        n_ox_rows = len(soup.select('.answer-ox-grid .ox-row'))
        if n_sections != n or n_ox_rows != n:
            results.append(('S12', 'ERROR',
                           f'三者一致違反 (ox-grid): cv桁数={n}, choice-section数={n_sections}, '
                           f'ox-row数={n_ox_rows} (slotmap §5.1 §6)'))
    elif mode == 'multi':
        n_slots = len(soup.select('.answer-area[data-answer-type="multi"] .answer-slot'))
        if n_sections != n or n_slots != n:
            results.append(('S12', 'ERROR',
                           f'三者一致違反 (multi): N={n}, choice-section数={n_sections}, '
                           f'answer-slot数={n_slots} (slotmap §5.2 §6)'))
        if k > n:
            results.append(('S12', 'ERROR',
                           f'multi: 正解数 K={k} が選択肢数 N={n} を超過'))
    elif mode == 'single':
        n_slots = len(soup.select('.answer-area[data-answer-type="single"] .answer-slot'))
        if n_sections != n or n_slots != n:
            results.append(('S12', 'ERROR',
                           f'三者一致違反 (single): N={n}, choice-section数={n_sections}, '
                           f'answer-slot数={n_slots} (slotmap §5.3 §6)'))


def check_S13_part_c_sections(soup, results):
    """S13: PART C に 7 section (id="c-1"〜"c-7")"""
    cs = [soup.find(id=f'c-{i}') for i in range(1, 8)]
    missing = [i for i, c in enumerate(cs, 1) if c is None]
    if missing:
        results.append(('S13', 'ERROR', f'PART C section 欠落: c-{missing}'))


def check_S14_drill_count(soup, results):
    """S14: PART D に 12 drill-block"""
    drills = soup.select('.drill-block')
    if len(drills) != 12:
        results.append(('S14', 'WARN', f'drill-block 数 = {len(drills)} (期待値: 12)'))

    # S26: ○:× 比率 6:6
    correct_q = 0
    incorrect_q = 0
    for quiz in soup.select('.self-check-quiz[data-arena="1"]'):
        cv = quiz.get('data-correct-value', '')
        if cv == '○':
            correct_q += 1
        elif cv == '×':
            incorrect_q += 1
    if drills and (correct_q != 6 or incorrect_q != 6):
        results.append(('S26', 'WARN',
                       f'○×比率不均衡: ○={correct_q}, ×={incorrect_q} (期待値: 6:6)'))


def check_S15_S16_answer_area_attrs(soup, results):
    """S15, S16: answer-area data-correct-value / data-explanation"""
    answer_area = soup.find(id='answer-area')
    if answer_area:
        aa_div = answer_area.find(class_='answer-area')
        if aa_div:
            if not aa_div.get('data-correct-value'):
                results.append(('S15', 'ERROR', 'answer-area に data-correct-value がない'))
            if not aa_div.get('data-explanation'):
                results.append(('S16', 'ERROR', 'answer-area に data-explanation がない'))


def check_S17_subcards(soup, results):
    """S17: 各 choice-section に 4 sub-card（範囲は ox-grid-N から動的導出）"""
    expected_types = {'original', 'explanation', 'basis-link', 'professor'}
    n = _derive_expected_choice_count(soup)
    for i in range(1, n + 1):
        cs = soup.find(id=f'choice-{i}')
        if not cs:
            continue
        sub_cards = cs.select('.sub-card')
        types_found = set()
        for sc in sub_cards:
            classes = sc.get('class', [])
            for t in expected_types:
                if t in classes:
                    types_found.add(t)
        missing = expected_types - types_found
        if missing:
            results.append(('S17', 'WARN', f'choice-{i} の sub-card 欠落: {sorted(missing)}'))


def check_S20_ref_targets(soup, results):
    """S20: ref-stat/ref-case のリンク先 id が basis-card 内に存在"""
    basis = soup.find(id='basis')
    if not basis:
        return
    valid_ids = {el.get('id') for el in basis.find_all(id=True) if el.get('id')}
    bad = []
    for a in soup.find_all('a', class_=['ref-stat', 'ref-case']):
        href = a.get('href', '')
        if href.startswith('#'):
            target = href[1:]
            if target and target not in valid_ids:
                bad.append(href)
    if bad:
        sample = list(dict.fromkeys(bad))[:5]
        results.append(('S20', 'WARN', f'ref-stat/ref-case 解決失敗 {len(bad)} 件: {sample}'))


def check_S21_backlinks(soup, results):
    """S21: basis-card に ref-backlinks 存在"""
    basis = soup.find(id='basis')
    if not basis:
        return
    cards = basis.select('.basis-card')
    no_backlinks = []
    for card in cards:
        if not card.select('.ref-backlinks'):
            no_backlinks.append(card.get('id', '(no-id)'))
    if no_backlinks:
        results.append(('S21', 'WARN',
                       f'ref-backlinks 欠落の basis-card: {no_backlinks[:5]}'))


def check_S38_no_spoiler_after_a2(soup, results):
    """S38: A-2 直後（PART B 前）にスポイラー禁止"""
    answer_area = soup.find(id='answer-area')
    choice_1 = soup.find(id='choice-1')
    if not (answer_area and choice_1):
        return
    cursor = answer_area
    intermediate_text = []
    while cursor:
        cursor = cursor.find_next_sibling()
        if cursor is None or cursor == choice_1:
            break
        if hasattr(cursor, 'get_text'):
            intermediate_text.append(cursor.get_text())
    full_text = '\n'.join(intermediate_text)
    if re.search(r'verdict-(correct|incorrect)', full_text):
        results.append(('S38', 'WARN', 'A-2 と PART B の間に verdict 露出の可能性'))


def check_S46_sec_icon(soup, results):
    """S46: section-title に sec-icon 配置"""
    titles = soup.select('.section-title')
    missing = 0
    for t in titles:
        if not t.select('.sec-icon'):
            missing += 1
    if missing > 0:
        results.append(('S46', 'WARN', f'section-title に sec-icon 欠落: {missing} 件'))


def check_S51_footer_version(soup, results):
    """S51: footer-spec に "TX v8.11.0" ＋ 必須 feature-tag 完備"""
    footer = soup.find(class_='footer-spec')
    if not footer:
        results.append(('S51', 'ERROR', 'footer-spec が存在しない'))
        return
    footer_text = footer.get_text()
    if 'TX v8.11.6' not in footer_text and 'TX v8.11.4' not in footer_text:
        results.append(('S51', 'WARN', 'footer-spec に TX v8.11.6 表記なし'))
    required_tags = [
        'ktx301-canon', 'readability-layer', 'hanging-grid',
        'basis-order-v2', 'a2-feedback-canon', 'k302-immune',
        'spoiler-safe', 'multi-answer-css', 'a2-two-stage-reveal',
        'a2-multi-ox-support', 'spoiler-leak-eradication',
        'spoiler-strong-elimination', 'ox-grid-fa-unification'
    ]
    missing_tags = [t for t in required_tags if t not in footer_text]
    if missing_tags:
        results.append(('S51', 'WARN', f'footer-spec 必須 feature-tag 欠落: {missing_tags}'))


def check_S60_S61_pattern_override(soup, results):
    """S60, S61: AP-24 検出（P2/P3 override 形式・pattern marker）"""
    body = soup.find('body')
    html_tag = soup.find('html')
    for el, name in [(body, 'body'), (html_tag, 'html')]:
        if not el:
            continue
        classes = el.get('class', [])
        for c in classes:
            if c in ('p1', 'p2', 'p3') or c.startswith('pattern-'):
                results.append(('S61', 'ERROR',
                              f'<{name}> に pattern marker class: {c} (AP-24違反)'))
        for attr in el.attrs:
            if attr.startswith('data-pattern'):
                results.append(('S61', 'ERROR',
                              f'<{name}> に {attr}: AP-24違反'))


def check_S62_S63_feedback_canon(style_text, script_text, results):
    """S62, S63: K302-16 検出（A-2 feedback クラッシュ防止）"""
    # 旧バグ規則検出
    bad_pattern = re.search(
        r'#answer-feedback\s+strong\s*\{[^}]*color\s*:\s*#fff', style_text)
    if bad_pattern and ':not' not in bad_pattern.group(0):
        results.append(('S62', 'ERROR',
                      'K302-16: #answer-feedback strong{color:#fff} 検出（:not ガードなし）'))

    # fb-verdict / fb-answer canonical 7 規則の存在確認
    required_rules = [
        '#answer-feedback{',
        '#answer-feedback .fb-verdict{',
        '#answer-feedback .fb-verdict.fb-correct{',
        '#answer-feedback .fb-verdict.fb-incorrect{',
        '#answer-feedback .fb-answer{',
        '#answer-feedback strong:not(.fb-verdict){',
        '#answer-feedback p{',
    ]
    norm_style = normalize_css(style_text)
    missing_rules = []
    for rule in required_rules:
        if normalize_css(rule) not in norm_style:
            missing_rules.append(rule)
    if missing_rules:
        results.append(('S62', 'ERROR',
                       f'fb-verdict canonical 規則欠落: {missing_rules}'))

    # JS の fb-verdict/fb-answer 出力チェック
    if script_text:
        if 'fb-verdict' not in script_text:
            results.append(('S63', 'ERROR', 'JS 内に fb-verdict 出力がない'))
        if 'fb-answer' not in script_text:
            results.append(('S63', 'ERROR', 'JS 内に fb-answer 出力がない'))


def check_S64_readability_layer(style_text, results):
    """S64: §24 readability layer 全 6 サブセクション存在"""
    norm = normalize_css(style_text)
    checks = [
        ('.section h3{', '24-1'),
        ('.cross-grid .cross-card:nth-child', '24-2'),
        ('.memory-list .memory-item.priority-a:nth-of-type', '24-3'),
        ('.lead-list > li{', '24-4'),
        ('.basis-card-body > p.hanging{', '24-6'),
    ]
    missing = []
    for needle, subnum in checks:
        if normalize_css(needle) not in norm:
            missing.append(f'§24-{subnum}')

    # §24-5: 全 p text-indent:1em
    if not re.search(r'(?<![\w\-.])p\s*\{[^}]*text-indent\s*:\s*1em', style_text):
        missing.append('§24-5')

    if missing:
        results.append(('S64', 'ERROR', f'§24 readability layer 欠落: {missing}'))


def check_S65_hanging_structure(soup, results):
    """S65: §24-6 ハンギングインデント HTML 構造"""
    hangings = soup.select('.basis-card-body > p.hanging')
    hang_bodies = soup.select('.basis-card-body > p.hanging > .hang-body')
    if len(hangings) != len(hang_bodies):
        results.append(('S65', 'ERROR',
                       f'hanging段落とhang-body数不一致 '
                       f'(p={len(hangings)}, span={len(hang_bodies)})'))

    # bare 形式のラベル始まり段落
    bare_count = 0
    bare_samples = []
    for p in soup.select('.basis-card-body > p:not(.hanging)'):
        first_child = None
        for child in p.children:
            if hasattr(child, 'name') and child.name:
                first_child = child
                break
        if first_child:
            classes = first_child.get('class') or []
            text = first_child.get_text(strip=True)
            is_label = False
            if 'para-num' in classes:
                is_label = True
            elif first_child.name == 'strong':
                if text.startswith('【') or re.match(r'^[IVX]+\.$', text):
                    is_label = True
            if is_label:
                bare_count += 1
                if len(bare_samples) < 3:
                    bare_samples.append(text[:30])
    if bare_count > 0:
        results.append(('S65', 'WARN',
                       f'bare 形式のラベル始まり段落: {bare_count} 件 '
                       f'(例: {bare_samples}) — class="hanging" 必要'))


def check_S66_part_order(soup, results):
    """S66: PART 順序検証（basis が PART B 後ろ・PART C 前）"""
    basis = soup.find(id='basis')
    choice_5 = soup.find(id='choice-5')
    c_1 = soup.find(id='c-1')

    if not (basis and choice_5 and c_1):
        return

    basis_pos = basis.sourceline or 0
    choice_5_pos = choice_5.sourceline or 0
    c_1_pos = c_1.sourceline or 0

    if not (choice_5_pos < basis_pos < c_1_pos):
        results.append(('S66', 'ERROR',
                       f'PART順序違反 (choice-5={choice_5_pos}, '
                       f'basis={basis_pos}, c-1={c_1_pos}) — '
                       f'basis は choice-5 と c-1 の間にあるべき'))


def check_S67_fontweight_and_AP(style_text, results):
    """S67: font-weight 改訂検証 + AP-26/27/28 検出"""

    # AP-28: .ron-mark に display:inline-block なし
    ron_block = find_css_rule_block(style_text, '.ron-mark')
    if ron_block:
        norm_ron = normalize_css(ron_block)
        if 'display:inline-block' in norm_ron:
            results.append(('S67-AP28', 'ERROR',
                          '.ron-mark に display:inline-block (AP-28違反)'))

    # AP-27: .basis-card-body > p に display:flex/grid 直当てなし
    bcb_p_pattern = re.compile(
        r'\.basis-card-body\s*>\s*p(?!\s*\.hanging)\s*\{([^}]*)\}',
        re.IGNORECASE)
    for m in bcb_p_pattern.finditer(style_text):
        block = m.group(1)
        norm_block = normalize_css(block)
        if 'display:flex' in norm_block or 'display:grid' in norm_block:
            results.append(('S67-AP27', 'ERROR',
                          '.basis-card-body > p に display:flex/grid 直当て (AP-27違反)'))

    # AP-26: 負 text-indent
    if re.search(r'text-indent\s*:\s*-\s*\d', style_text):
        results.append(('S67-AP26', 'WARN',
                       '負 text-indent を含む規則あり (AP-26 の可能性)'))

    # .basis-card-body font-weight 改訂検証
    bcb_block = find_css_rule_block(style_text, '.basis-card-body')
    if bcb_block:
        norm_bcb = normalize_css(bcb_block)
        fw_match = re.search(r'font-weight:(\d+)', norm_bcb)
        if fw_match:
            fw = int(fw_match.group(1))
            if fw < 600:
                results.append(('S67-fontweight', 'ERROR',
                              f'.basis-card-body font-weight = {fw} '
                              f'(期待値: 600以上)'))

    # ref-stat / ref-case font-weight: 700
    ref_pattern = re.compile(
        r'a\.ref-stat\s*,\s*a\.ref-case\s*\{([^}]*)\}',
        re.IGNORECASE | re.DOTALL)
    m = ref_pattern.search(style_text)
    if m:
        norm_block = normalize_css(m.group(1))
        fw_match = re.search(r'font-weight:(\d+)', norm_block)
        if fw_match and int(fw_match.group(1)) < 700:
            results.append(('S67-fontweight', 'ERROR',
                          f'a.ref-stat/ref-case font-weight = {fw_match.group(1)} '
                          f'(期待値: 700)'))



def check_S68_final_answer_hidden(soup, results):
    """S68: final-answer hidden 属性検証（AP-30 検出・v8.11.1 新規）"""
    final_answers = soup.find_all('div', class_='final-answer')
    if not final_answers:
        return
    for fa in final_answers:
        # 'hidden' 属性の存在チェック
        if 'hidden' not in fa.attrs:
            results.append(('S68-AP30', 'ERROR',
                          '<div class="final-answer"> に hidden 属性が欠落 (AP-30違反)'))


def check_S69_multi_answer_css(style_text, results):
    """S69: §22-quater-3 CSS パッチ存在検証（AP-31 検出・v8.11.1 新規）"""
    required_patterns = [
        ('.answer-num.answer-num-multi', '.answer-num.answer-num-multi セレクタ'),
        ('.answer-num-multi .ans-cell', '.answer-num-multi .ans-cell セレクタ'),
        ('.ans-cell.ans-correct', '.ans-cell.ans-correct セレクタ'),
        ('.ans-cell.ans-incorrect', '.ans-cell.ans-incorrect セレクタ'),
        ('.final-answer[hidden]', '.final-answer[hidden] セレクタ'),
        ('@keyframes faReveal', '@keyframes faReveal'),
    ]
    norm_style = normalize_css(style_text)
    for pattern, description in required_patterns:
        norm_pattern = normalize_css(pattern)
        if norm_pattern not in norm_style:
            results.append(('S69-AP31', 'ERROR',
                          f'§22-quater-3 CSS パッチに {description} が欠落 (AP-31違反)'))


def check_S70_fa_summary_no_literal(soup, results):
    """S70: fa-summary 内「正解はN」リテラル禁止検証（AP-32 検出・v8.11.1 新規）"""
    fa_summaries = soup.find_all('p', class_='fa-summary')
    # 「正解は」+ 1〜15 文字の数字・カタカナ・X・中点 + 句点
    literal_pattern = re.compile(r'正解は[0-9XＸア-ン・]{1,15}[。．]')
    for p in fa_summaries:
        text = p.get_text()
        match = literal_pattern.search(text)
        if match:
            results.append(('S70-AP32', 'ERROR',
                          f'<p class="fa-summary"> 内に「{match.group()}」リテラル (AP-32違反)'))




def check_S71_answer_instruction(soup, results):
    """S71: answer-instruction canonical 文言固定検証（AP-33 検出・v8.11.2/v8.11.3）"""
    instructions = soup.find_all('p', class_='answer-instruction')
    if not instructions:
        return
    # v8.11.3: Type 別 canonical 文言 (3 種)
    canonical_patterns = [
        re.compile(r'^選択肢を選んで「解答を表示」を押してください。$'),          # single
        re.compile(r'^選択肢を\d+個選んで「解答を表示」を押してください。$'),     # multi
        re.compile(r'^各記述に「1（正）」または「2（誤）」を選んで「解答を表示」を押してください。$'),  # ox-grid
    ]
    literal_pattern = re.compile(r'正解は|正答は')
    for p in instructions:
        text = p.get_text().strip()
        if literal_pattern.search(text):
            results.append(('S71-AP33', 'ERROR',
                          f'<p class="answer-instruction"> 内に正解値リテラル: 「{text[:40]}...」 (AP-33違反)'))
        elif not any(pat.match(text) for pat in canonical_patterns):
            results.append(('S71-AP33', 'WARN',
                          f'<p class="answer-instruction"> が canonical 文言と相違: 「{text[:40]}」'))


def check_S72_reveal_btn(soup, results):
    """S72: A-2 解答エリアに reveal-answer-btn 存在検証（AP-34 検出・v8.11.2 新規）"""
    answer_areas = soup.find_all('div', class_='answer-area')
    for area in answer_areas:
        btn = area.find('button', class_='reveal-answer-btn')
        if not btn:
            results.append(('S72-AP34', 'ERROR',
                          '<div class="answer-area"> 内に <button class="reveal-answer-btn"> が欠落 (AP-34違反)'))
        elif btn.get('type') != 'button':
            results.append(('S72-AP34', 'WARN',
                          '<button class="reveal-answer-btn"> に type="button" がない'))




def check_S73_answer_type_consistency(soup, results):
    """S73: data-answer-type と data-correct-value の整合性検証（AP-35 検出・v8.11.3 新規）"""
    answer_areas = soup.find_all('div', class_='answer-area')
    if not answer_areas:
        return
    for area in answer_areas:
        cv = area.get('data-correct-value', '')
        at = area.get('data-answer-type', '')
        if not cv:
            continue
        # 自動判定
        # fill-in (slotmap §6.6 §2.4): cv = 'A=5,B=7,C=3,D=6' のように '=' を含む
        # ox3comb8 (slotmap §6.7): cv 単一数字だが data-answer-type で区別済 (下記参照)
        if at == 'ox3comb8':
            expected_type = 'ox3comb8'
        elif '=' in cv and all('=' in p and re.match(r'^[A-Z]=', p.strip()) for p in cv.split(',') if p.strip()):
            expected_type = 'fill-in'
        elif ',' in cv and all(re.match(r'^\d+$', p.strip()) for p in cv.split(',') if p.strip()):
            # K=1 末尾カンマ ("3,") も multi として認識 (render.py との同期、空要素は無視)
            expected_type = 'multi'
        elif re.match(r'^[12]{2,}$', cv):
            expected_type = 'ox-grid'
        elif re.match(r'^\d+$', cv):
            expected_type = 'single'
        else:
            expected_type = 'single'
        # 属性欠落
        if not at:
            results.append(('S73-AP35', 'ERROR',
                          f'<div class="answer-area"> に data-answer-type 属性が欠落 '
                          f'(期待値: "{expected_type}" based on data-correct-value="{cv}") (AP-35違反)'))
            continue
        # 不整合
        if at != expected_type:
            results.append(('S73-AP35', 'ERROR',
                          f'data-answer-type="{at}" だが data-correct-value="{cv}" から '
                          f'判定される type は "{expected_type}" (AP-35違反)'))
            continue
        # Type B (multi): selection-counter 存在 + answer-slot 数チェック
        if at == 'multi':
            if not area.find('p', class_='selection-counter'):
                results.append(('S73-AP35', 'WARN',
                              'Type B (multi) で <p class="selection-counter"> が欠落'))
            slots = area.find_all('button', class_='answer-slot')
            n_correct = len(cv.split(','))
            if len(slots) < n_correct:
                results.append(('S73-AP35', 'ERROR',
                              f'Type B (multi) で answer-slot 数 ({len(slots)}) が '
                              f'正解値の選択数 ({n_correct}) を下回る (AP-35違反)'))
        # Type C (ox-grid): ox-grid 存在 + ox-row 数チェック
        elif at == 'ox-grid':
            grid = area.find('div', class_='answer-ox-grid')
            if not grid:
                results.append(('S73-AP35', 'ERROR',
                              'Type C (ox-grid) で <div class="answer-ox-grid"> が欠落 (AP-35違反)'))
            else:
                rows = grid.find_all('div', class_='ox-row')
                if len(rows) != len(cv):
                    results.append(('S73-AP35', 'ERROR',
                                  f'Type C (ox-grid) で ox-row 数 ({len(rows)}) と '
                                  f'data-correct-value 桁数 ({len(cv)}) が不一致 (AP-35違反)'))




def check_S74_no_spoiler_literals(soup, results):
    """S74: PART A 内 / data-explanation 内の正解値リテラル禁止（AP-36/37 検出・v8.11.4 新規）"""
    # AP-36: PART A 内「N（XX）正解」
    partA = soup.find('section', id='problem-text')
    if partA:
        text = partA.get_text()
        # パターン: 数字 + （文字列） + 正解/正答
        m = re.search(r'\d+\s*[（(][^）)]+[）)]\s*正[解答]', text)
        if m:
            results.append(('S74-AP36', 'ERROR',
                          f'PART A 内に正解リテラル混入: 「{m.group()[:40]}」 (AP-36違反)'))
        # 「N 正解」「N 正答」(括弧なし) のミニマムパターンも検出
        m2 = re.search(r'\b(\d+)\s*正[解答]\b', text)
        if m2 and not m:
            results.append(('S74-AP36', 'WARN',
                          f'PART A 内に正解リテラル混入の可能性: 「{m2.group()[:40]}」'))
    
    # AP-37: data-explanation 先頭の正解値リテラル
    answer_areas = soup.find_all('div', class_='answer-area')
    for area in answer_areas:
        exp = area.get('data-explanation', '')
        if not exp:
            continue
        # 先頭の正解値リテラルパターン
        prefix_pat = re.compile(
            r'^\s*\d+(?:,\s*\d+)*(?:\s*[（(][^）)]+[）)])?\s*[。、:：]'
        )
        if prefix_pat.match(exp):
            results.append(('S74-AP37', 'ERROR',
                          f'data-explanation 先頭に正解値リテラル: 「{exp[:50]}」 (AP-37違反)'))


def check_S75_fa_answer_num_correct_only(soup, results):
    """S75: FA answer-num が正解の数字のみ表示しているか（AP-38 検出・v8.11.4 新規）"""
    fa = soup.find('div', class_='final-answer')
    if not fa:
        return
    answer_num = fa.find(class_='answer-num')
    if not answer_num:
        return
    
    # answer-area から正解値と Type を取得
    answer_area = soup.find('div', class_='answer-area')
    if not answer_area:
        return
    cv = answer_area.get('data-correct-value', '')
    at = answer_area.get('data-answer-type', 'single')
    
    if at == 'multi':
        # ans-correct セル数 = 正解数, ans-incorrect セル数 = 0
        correct_cells = answer_num.find_all(class_='ans-correct')
        incorrect_cells = answer_num.find_all(class_='ans-incorrect')
        n_correct_expected = len(cv.split(','))
        if len(incorrect_cells) > 0:
            results.append(('S75-AP38', 'ERROR',
                          f'FA multi で不正解セル ({len(incorrect_cells)} 個) が表示されている (AP-38違反)'))
        elif len(correct_cells) != n_correct_expected:
            results.append(('S75-AP38', 'ERROR',
                          f'FA multi で正解セル数 ({len(correct_cells)}) が正解値数 ({n_correct_expected}) と不一致'))
    elif at == 'ox-grid':
        # v8.11.5: ox-grid 型は <span class="answer-num">{N桁文字列}</span> 形式に変更
        # ans-cell ベースの旧検証はスキップ (S76/AP-40 で別途検証)
        pass




def check_S76_spoiler_strong_and_ox_grid_fa(soup, results):
    """S76: PART A 内 <strong>N（XX）</strong> + ox-grid FA 形式統一（AP-39/40 検出・v8.11.5 新規）"""
    # AP-39: PART A 内 <strong>N（XX）</strong> 残存
    partA = soup.find('section', id='problem-text')
    if partA:
        for strong in partA.find_all('strong'):
            text = strong.get_text().strip()
            # 数字 + （カタカナ等） パターン
            if re.match(r'^\d+\s*[（(][^）)]+[）)]\s*$', text):
                results.append(('S76-AP39', 'ERROR',
                              f'PART A 内に <strong>N（XX）</strong> 形式の正解強調: 「{text}」 (AP-39違反)'))
                break
    
    # AP-40: ox-grid 型 FA が answer-num-multi 構造 (記述ラベル表示) になっていないか
    answer_area = soup.find('div', class_='answer-area')
    if answer_area:
        at = answer_area.get('data-answer-type', 'single')
        cv = answer_area.get('data-correct-value', '')
        if at == 'ox-grid':
            fa = soup.find('div', class_='final-answer')
            if fa:
                an_multi = fa.find('div', class_='answer-num-multi')
                if an_multi:
                    results.append(('S76-AP40', 'ERROR',
                                  f'ox-grid 型 FA で answer-num-multi 構造が残存。<span class="answer-num">{cv}</span> 形式に変更要 (AP-40違反)'))
                else:
                    # 期待: <span class="answer-num">N桁文字列</span>
                    an = fa.find(class_='answer-num')
                    if an and an.get_text().strip() != cv:
                        results.append(('S76-AP40', 'WARN',
                                      f'ox-grid 型 FA の answer-num テキスト「{an.get_text().strip()}」 ≠ data-correct-value「{cv}」'))


def check_S77_no_body_in_script(html, results):
    """S77: script ブロック内に body 閉じタグ文字列が含まれていないか（AP-41 検出・v8.11.6-hotfix1 新規）

    背景:
      Lexia 等の host アプリは TX 単一HTML を iframe srcdoc に注入する際、
      `</body>` を正規表現で検出してその直前にホスト用スクリプトを注入する。
      script ブロック内 (コメント・文字列リテラル等) に `</body>` が含まれていると、
      正規表現の最初の一致がそちらになり、ホスト用スクリプトが script タグ内部に
      注入されて構文崩壊する。結果としてクイズハンドル・リンクジャンプ等のすべての
      JS 機能が iframe 内で完全に死ぬ。

      この事故は v8.11.6 以前の annex-C.js 冒頭コメントに「</body> 直前の
      <script> ブロック内部に逐語コピー」と書いてあったため、全 TX ファイルで再現
      した (例: 刑TX299, K299 等)。Lexia 側にも lastIndexOf 採用の防御策を入れる
      べきだが、生成側でも S77 として禁止する。

    検出:
      <script>...</script> の中身を抽出し、`</body>` リテラルが含まれていればエラー。
      コメント/文字列を区別せず、生のテキストとして禁止。
    """
    # 全 <script> ブロックの中身を抽出 (BeautifulSoup ではなく生 HTML で見る)
    for m in re.finditer(r'<script\b[^>]*>([\s\S]*?)</script>', html, re.IGNORECASE):
        body = m.group(1)
        if re.search(r'</\s*body\s*>', body, re.IGNORECASE):
            # 該当行を1行だけ抜く (デバッグ用に)
            offset = m.start(1)
            sub_idx = body.lower().find('</body>')
            if sub_idx < 0:
                sub_idx = re.search(r'</\s*body\s*>', body, re.IGNORECASE).start()
            absolute_pos = offset + sub_idx
            # 行番号を計算
            line_num = html[:absolute_pos].count('\n') + 1
            # スニペット
            line_start = html.rfind('\n', 0, absolute_pos) + 1
            line_end = html.find('\n', absolute_pos)
            if line_end < 0:
                line_end = len(html)
            snippet = html[line_start:line_end].strip()[:100]
            results.append(('S77-AP41', 'ERROR',
                          f'<script> 内に body 閉じタグ文字列が含まれる (line {line_num}): '
                          f'「{snippet}」 ホスト側注入バグの原因になる為禁止 (AP-41違反)'))
            return  # 1件見つけたら十分


def check_S78_views_section(soup, results):
    """S78: views-section が存在する場合、view-block が固定 3 件であること
    （slotmap §5.3 §8: single-choice-5 等で使用する【見解】slot の構造検証）。
    views-section が存在しない HTML（ox-grid / multi-select / combination 系）では何もしない。"""
    views_section = soup.find(class_='views-section')
    if not views_section:
        return  # 該当 template でない場合はスキップ
    view_blocks = views_section.find_all(class_='view-block')
    if len(view_blocks) != 3:
        results.append(('S78', 'ERROR',
                       f'view-block 数 = {len(view_blocks)} (期待 3 件、slotmap §5.3 §8 固定 3 件方式)'))
    # 各 view-block に label と body の両方が存在するか
    for i, vb in enumerate(view_blocks, 1):
        if not vb.find(class_='view-label'):
            results.append(('S78', 'WARN', f'view-block #{i} に <span class="view-label"> がない'))
        if not vb.find(class_='view-body'):
            results.append(('S78', 'WARN', f'view-block #{i} に <p class="view-body"> がない'))


def check_S79_combinations_section(soup, results):
    """S79: combinations-section が存在する場合、combo-block 件数を検証。
    （slotmap §5.4 §6: combination-5 = 5 件、slotmap §6.7 §2.4: ox3comb8 = 8 件）。
    data-answer-type で形式判定し、許容件数を分岐する。
    combinations-section が存在しない HTML では何もしない。"""
    combos_section = soup.find(class_='combinations-section')
    if not combos_section:
        return  # 該当 template でない場合はスキップ
    combo_blocks = combos_section.find_all(class_='combo-block')
    # 形式判定 (mode) で許容件数を決定
    mode, _, _ = _derive_cv_info(soup)
    expected = 8 if mode == 'ox3comb8' else 5
    if len(combo_blocks) != expected:
        results.append(('S79', 'ERROR',
                       f'combo-block 数 = {len(combo_blocks)} (期待 {expected} 件、mode={mode})'))
    # 各 combo-block に label と set 表示要素の両方が存在するか
    for i, cb in enumerate(combo_blocks, 1):
        if not cb.find(class_='combo-label'):
            results.append(('S79', 'WARN', f'combo-block #{i} に <span class="combo-label"> がない'))
        if not cb.find(class_='combo-set'):
            results.append(('S79', 'WARN', f'combo-block #{i} に <span class="combo-set"> がない'))


# ============================================================
# メイン処理
# ============================================================

def validate(html_path, verbose=False):
    """HTMLファイルを検証して結果を返す"""
    path = Path(html_path)
    if not path.exists():
        print(f'ERROR: ファイルが存在しません: {html_path}')
        return 2

    try:
        html = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        print(f'ERROR: UTF-8 として読み込めません: {html_path}')
        return 2

    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        print(f'ERROR: HTML パースに失敗: {e}')
        return 2

    style_text = get_style_text(soup)
    script_text = get_script_text(soup)

    results = []

    # 構造系
    check_S1_S5_tag_balance(html, results)
    check_S7_duplicate_ids(soup, results)
    check_S8_href_resolution(soup, results)
    check_S10_four_parts(soup, results)
    check_S11_part_a_sections(soup, results)
    check_S12_part_b_choices(soup, results)
    check_S13_part_c_sections(soup, results)
    check_S14_drill_count(soup, results)

    # 必須属性・カード系
    check_S15_S16_answer_area_attrs(soup, results)
    check_S17_subcards(soup, results)
    check_S20_ref_targets(soup, results)
    check_S21_backlinks(soup, results)

    # コンテンツ規律
    check_S38_no_spoiler_after_a2(soup, results)
    check_S46_sec_icon(soup, results)
    check_S51_footer_version(soup, results)

    # AP / K302 検出
    check_S60_S61_pattern_override(soup, results)
    check_S62_S63_feedback_canon(style_text, script_text, results)

    # v8.11.0 新規
    check_S64_readability_layer(style_text, results)
    check_S65_hanging_structure(soup, results)
    check_S66_part_order(soup, results)
    check_S67_fontweight_and_AP(style_text, results)

    # v8.11.1 新規 (spoiler-safe + multi-answer-css)
    check_S68_final_answer_hidden(soup, results)
    check_S69_multi_answer_css(style_text, results)
    check_S70_fa_summary_no_literal(soup, results)

    # v8.11.6 拡張 (slotmap §5.3 §6: single-choice-5 の【見解】slot 検証)
    check_S78_views_section(soup, results)

    # v8.11.6 拡張 (slotmap §5.4 §6: combination-5 の【組合せ】slot 検証)
    check_S79_combinations_section(soup, results)

    # v8.11.2 新規 (a2-two-stage-reveal)
    check_S71_answer_instruction(soup, results)
    check_S72_reveal_btn(soup, results)

    # v8.11.3 新規 (a2-multi-ox-support)
    check_S73_answer_type_consistency(soup, results)

    # v8.11.4 新規 (spoiler-leak-eradication)
    check_S74_no_spoiler_literals(soup, results)
    check_S75_fa_answer_num_correct_only(soup, results)

    # v8.11.5 新規 (spoiler-strong-elimination + ox-grid-fa-unification)
    check_S76_spoiler_strong_and_ox_grid_fa(soup, results)

    # v8.11.6-hotfix1 新規 (script-no-body-close-literal)
    check_S77_no_body_in_script(html, results)

    # 結果出力
    errors = [r for r in results if r[1] == 'ERROR']
    warnings = [r for r in results if r[1] == 'WARN']

    print(f'\n{"=" * 60}')
    print(f'TX v8.11.6 検証結果: {html_path}')
    print(f'{"=" * 60}')

    if not results:
        print(f'\n✅ すべてのチェックを通過しました')
        return 0

    if errors:
        print(f'\n❌ ERROR ({len(errors)} 件):')
        for sid, sev, msg in errors:
            print(f'  [{sid}] {msg}')

    if warnings:
        print(f'\n⚠️  WARNING ({len(warnings)} 件):')
        for sid, sev, msg in warnings:
            print(f'  [{sid}] {msg}')

    print(f'\n{"=" * 60}')
    if errors:
        print(f'❌ ERROR が {len(errors)} 件あります。修正が必要です。')
        return 1
    else:
        print(f'⚠️  WARNING のみ。必須項目はすべて通過しています。')
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='TX v8.11.6 自己検証スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使い方:
  python scripts/validate.py outputs/ktx/K302.html
  python scripts/validate.py outputs/ktx/K302.html --verbose

ERROR が 0 件なら配信可能。WARNING は内容を確認して必要なら修正。
        """
    )
    parser.add_argument('html_path', help='検証対象の HTML ファイルパス')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='詳細出力')
    args = parser.parse_args()

    return validate(args.html_path, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
