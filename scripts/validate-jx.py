#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JX v3.2 軽量検証スクリプト

対象範囲：
  J1   <html lang="ja">
  J2   <title> 設定
  J3   Google Fonts <link> 11 役割書体
  J4   --font-* 11 変数
  J5   --accent / --mid 定義
  J6   body の font-weight / line-height / letter-spacing
  J7   .key-box 防御セレクタ
  J8   .key-box ::before に KEY
  J9   .note-box / .warn-box / .success-box / .danger-box ::before
  J10  .judgment-text クラス
  J11  .para-num クラス
  J12  .model-answer ::before に MODEL ANSWER
  J13  .grading ::before に GRADING
  J14  .container max-width: 1320px
  J15  .doc-header に position:absolute
  J16  旧 <strong>第N項</strong> 表記の不在
  J17  配色パターン名（V3 11 パレット名・役割割合）の <body> 内不在
  J18  PART 5 (back-refs) ≥ 3
  J19  フッターに励まし文言
  J20  スムーズスクロール JS
  J21  深度フロア（bytes/h4/li/第4部見出し4-1〜4-6/重要度ランクrank-A〜D網羅）※当面WARNING

  --- v4 LOOP-FOLD 追加（<details id="deep-dive"> 検出時のみ・当面WARNING）---
  JC1  エグゼクティブサマリー(#exec-summary)の不在（答えを先出ししない）
  JC2  物理順序：コア（模範答案）→ deep（折りたたみ）
  JC3  第4部・第5部が <details id="deep-dive"> 内に折りたたまれている
  JC4  模範答案が <details class="reveal-answer"> で封じられている
  JD1  コア前半の自己充足（事案足場・模範答案・講師アドバイス・論点抽出）

使い方：
  python scripts/validate-jx.py outputs/001_JX/001_刑法/刑JX001.html
  python scripts/validate-jx.py outputs/001_JX/001_刑法/刑JX001.html --core-only   # J1-J20＋JC/JD（J21省略）
  python scripts/validate-jx.py outputs/001_JX/001_刑法/刑JX001.html --deep-only   # J21 深度フロアのみ
"""

import sys
import re
import argparse
from pathlib import Path

# Windows cp932 で絵文字出力時の UnicodeEncodeError 対策
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。以下を実行してインストールしてください：")
    print("  pip install beautifulsoup4")
    sys.exit(1)


# ============================================================
# J21 深度フロア定数（再較正はここ1箇所を編集するだけ）
#   ※ floor は validate 側のみに置く。prompt new-jx-headless.md には
#     数値を一切書かない（モデルが floor に最適化する水増しを防ぐため）。
#   ※ 値は 刑JX032.bak.html（162KB 手動ゴールド版）の実測由来の仮値。
#     刑JX032 再生成の実測が出たら再較正し、WARNING→ERROR 格上げを検討（末尾 TODO 参照）。
# ============================================================
J21_MIN_BYTES = 120000        # 実測 161,982
J21_MIN_H4 = 50               # 実測 79
J21_MIN_LI = 60               # 実測 90
J21_PART4_HEADINGS = ['4-1', '4-2', '4-3', '4-4', '4-5', '4-6']  # <h3>4-N. で検出（h4 ではない）
J21_REQUIRED_RANKS = ['rank-A', 'rank-B', 'rank-C', 'rank-D']    # 重要度4段階（rank-E〜H は存在しない）


# ============================================================
# ヘルパー
# ============================================================

def get_style_text(soup):
    return '\n'.join(s.get_text() for s in soup.find_all('style'))


def get_script_text(soup):
    return '\n'.join(s.get_text() for s in soup.find_all('script'))


def find_rule_block(style_text, selector):
    """指定セレクタのルールブロックを抽出"""
    escaped = re.escape(selector)
    pattern = rf'(?:^|[\s,}}]){escaped}\s*\{{([^}}]*)\}}'
    m = re.search(pattern, style_text)
    return m.group(1) if m else None


def find_before_content(style_text, selector):
    """selector::before { content: ... } を抽出"""
    escaped = re.escape(selector)
    pattern = rf'{escaped}::before\s*\{{([^}}]*)\}}'
    m = re.search(pattern, style_text)
    if not m:
        return None
    block = m.group(1)
    cm = re.search(r'content\s*:\s*["\']([^"\']*)["\']', block)
    return cm.group(1) if cm else None


# ============================================================
# 検証
# ============================================================

def check_J1_html_lang(soup, results):
    html_tag = soup.find('html')
    if not html_tag:
        results.append(('J1', 'ERROR', '<html> タグが見つかりません'))
        return
    lang = html_tag.get('lang', '')
    if lang != 'ja':
        results.append(('J1', 'ERROR', f'<html lang="ja"> が必要ですが lang="{lang}"'))


def check_J2_title(soup, results):
    title = soup.find('title')
    if not title or not title.get_text().strip():
        results.append(('J2', 'ERROR', '<title> が設定されていません'))


def check_J3_google_fonts(soup, results):
    links = soup.find_all('link', href=re.compile(r'fonts\.googleapis\.com'))
    if not links:
        results.append(('J3', 'ERROR', 'Google Fonts <link> が見つかりません'))
        return
    href_all = ' '.join(l.get('href', '') for l in links)
    required = [
        'Noto+Serif+JP',
        'Shippori+Mincho+B1',
        'Shippori+Antique',
        'Zen+Old+Mincho',
        'Zen+Maru+Gothic',
        'Zen+Kaku+Gothic+Antique',
        'Kosugi+Maru',
        'Kaisei+Decol',
        'Source+Code+Pro',
    ]
    missing = [r for r in required if r not in href_all]
    if missing:
        results.append(('J3', 'ERROR',
                        f'Google Fonts に以下が不足: {", ".join(missing)}'))


def check_J4_font_vars(style_text, results):
    required_vars = [
        '--font-body', '--font-soft', '--font-display', '--font-statute',
        '--font-quote', '--font-answer', '--font-keyword', '--font-judgment',
        '--font-note', '--font-professor', '--font-mono',
    ]
    missing = [v for v in required_vars
               if not re.search(rf'{re.escape(v)}\s*:', style_text)]
    if missing:
        results.append(('J4', 'ERROR',
                        f'--font-* 変数が不足 ({len(missing)}/11): '
                        f'{", ".join(missing)}'))


def check_J5_accent_mid(style_text, results):
    if not re.search(r'--accent\s*:', style_text):
        results.append(('J5', 'ERROR', '--accent が未定義'))
    if not re.search(r'--mid\s*:', style_text):
        results.append(('J5', 'ERROR', '--mid が未定義'))


def check_J6_body_typography(style_text, results):
    block = find_rule_block(style_text, 'body')
    if not block:
        results.append(('J6', 'ERROR', 'body セレクタが見つかりません'))
        return
    # font-weight
    fw = re.search(r'font-weight\s*:\s*(\d+)', block)
    if not fw:
        results.append(('J6', 'ERROR', 'body の font-weight が未指定'))
    elif int(fw.group(1)) < 500:
        results.append(('J6', 'ERROR',
                        f'body の font-weight が 500 未満: {fw.group(1)}'))
    # line-height
    lh = re.search(r'line-height\s*:\s*([\d.]+)', block)
    if not lh:
        results.append(('J6', 'ERROR', 'body の line-height が未指定'))
    elif float(lh.group(1)) < 1.9:
        results.append(('J6', 'ERROR',
                        f'body の line-height が 1.9 未満: {lh.group(1)}'))
    # letter-spacing
    ls = re.search(r'letter-spacing\s*:\s*\.?(\d*\.?\d+)em', block)
    if not ls:
        results.append(('J6', 'ERROR', 'body の letter-spacing が未指定'))
    else:
        val = float('0.' + ls.group(1).lstrip('.')) if ls.group(1).startswith('0') or '.' not in ls.group(1) else float(ls.group(1))
        # 簡易：.03em 以上か
        raw = ls.group(0)
        m2 = re.search(r'([\d.]+)em', raw)
        if m2 and float(m2.group(1)) < 0.03:
            results.append(('J6', 'ERROR',
                            f'body の letter-spacing が .03em 未満: {m2.group(1)}em'))


def check_J7_keybox_specificity(style_text, results):
    """.key-box の specificity 防御セレクタ"""
    # 「.key-box, .section .key-box, .container .key-box」または同等
    pattern1 = re.search(
        r'\.key-box\s*,\s*\.section\s+\.key-box\s*,\s*\.container\s+\.key-box',
        style_text
    )
    pattern2 = re.search(
        r'\.container\s+\.key-box\s*,\s*\.section\s+\.key-box\s*,\s*\.key-box',
        style_text
    )
    # 別順も許容
    has_three = (
        '.section .key-box' in style_text and
        '.container .key-box' in style_text
    )
    if not (pattern1 or pattern2 or has_three):
        results.append(('J7', 'ERROR',
                        '.key-box の specificity 防御セレクタが不足 '
                        '（.section .key-box / .container .key-box 等）'))


def check_J8_keybox_before(style_text, results):
    content = find_before_content(style_text, '.key-box')
    if content is None:
        results.append(('J8', 'ERROR', '.key-box::before の content が未定義'))
        return
    if 'KEY' not in content:
        results.append(('J8', 'ERROR',
                        f'.key-box::before の content に "KEY" を含む必要: '
                        f'実際 "{content}"'))


def check_J9_label_boxes(style_text, results):
    """note-box / warn-box / success-box / danger-box ::before"""
    for cls in ['.note-box', '.warn-box', '.success-box', '.danger-box']:
        if not re.search(rf'{re.escape(cls)}::before\s*\{{', style_text):
            results.append(('J9', 'ERROR',
                            f'{cls}::before のラベル定義が見つかりません'))


def check_J10_judgment_text(style_text, results):
    if not re.search(r'\.judgment-text\s*[\s,{]', style_text):
        results.append(('J10', 'ERROR',
                        '.judgment-text クラス定義が見つかりません'))


def check_J11_para_num(style_text, results):
    if not re.search(r'\.para-num\s*[\s,{]', style_text):
        results.append(('J11', 'ERROR',
                        '.para-num クラス定義が見つかりません'))


def check_J12_model_answer(style_text, results):
    content = find_before_content(style_text, '.model-answer')
    if content is None:
        results.append(('J12', 'ERROR',
                        '.model-answer::before の content が未定義'))
        return
    if 'MODEL ANSWER' not in content:
        results.append(('J12', 'ERROR',
                        f'.model-answer::before content に "MODEL ANSWER" 必須: '
                        f'実際 "{content}"'))


def check_J13_grading(style_text, results):
    content = find_before_content(style_text, '.grading')
    if content is None:
        results.append(('J13', 'ERROR',
                        '.grading::before の content が未定義'))
        return
    if 'GRADING' not in content:
        results.append(('J13', 'ERROR',
                        f'.grading::before content に "GRADING" 必須: '
                        f'実際 "{content}"'))


def check_J14_container_maxwidth(style_text, results):
    block = find_rule_block(style_text, '.container')
    if not block:
        results.append(('J14', 'ERROR', '.container セレクタが見つかりません'))
        return
    m = re.search(r'max-width\s*:\s*(\d+)px', block)
    if not m:
        results.append(('J14', 'ERROR', '.container max-width が未指定'))
    elif int(m.group(1)) != 1320:
        results.append(('J14', 'ERROR',
                        f'.container max-width は 1320px 必須: '
                        f'実際 {m.group(1)}px'))


def check_J15_docheader_absolute(style_text, results):
    block = find_rule_block(style_text, '.doc-header')
    if not block:
        results.append(('J15', 'ERROR', '.doc-header セレクタが見つかりません'))
        return
    pos = re.search(r'position\s*:\s*(\w+)', block)
    if not pos:
        results.append(('J15', 'ERROR', '.doc-header の position 未指定'))
        return
    if pos.group(1) != 'absolute':
        results.append(('J15', 'ERROR',
                        f'.doc-header position は absolute 必須 '
                        f'(sticky/fixed 不可): 実際 {pos.group(1)}'))


def check_J16_no_legacy_paragraph_num(soup, results):
    """<strong>第N項</strong> 等の旧表記検出"""
    pattern = re.compile(r'第[一二三四五六七八九十百千０-９0-9]+項')
    for strong in soup.find_all('strong'):
        text = strong.get_text(strip=True)
        if pattern.fullmatch(text):
            results.append(('J16', 'ERROR',
                            f'旧条文番号表記検出 (para-num使用に置換): '
                            f'<strong>{text}</strong>'))
            return  # 1件報告で十分


def check_J17_no_palette_names_in_body(soup, results):
    body = soup.find('body')
    if not body:
        return
    body_text = body.get_text()
    # 配色 V3（2026-06-02 TX 統一）：11 名前付きパレット名・役割割合を本文に出さない。
    # 配色情報は :root{} のみで管理し、ヘッダー／フッター／凡例の表示テキストに書かない。
    palette_strict = [
        # V3 11 名前付きパレット（英名）
        'Sweet Berry', 'Fresh Citrus', 'Rose Mist', 'Antique Pearl',
        'Maison Blanche', 'Crystal Blue', 'Dusty Sage', 'Mint Tea',
        'Fresh Mint', 'Twilight Violet', 'Sunset Harmony',
        # 役割割合の記載（TX G8 と同趣旨）
        'ベース 70', 'メイン 25', 'アクセント 5',
        # 旧パレット名（歴史的・残存検出）
        'ホワイト・ノーブル', 'ローズシャンブル', 'セージブラリー', 'ラベンダードーン',
    ]
    for name in palette_strict:
        if name in body_text:
            results.append(('J17', 'ERROR',
                            f'配色パターン名／役割割合 "{name}" が <body> 内に出現'))


def check_J18_back_refs(soup, results):
    refs = soup.find_all(class_='back-refs')
    if len(refs) < 3:
        results.append(('J18', 'ERROR',
                        f'PART 5 に back-refs が 3 箇所未満: 実際 {len(refs)}'))


def check_J19_footer_encouragement(soup, results):
    footer = soup.find('footer') or soup.find(class_=re.compile(r'footer'))
    if not footer:
        results.append(('J19', 'ERROR', 'フッター要素が見つかりません'))
        return
    text = footer.get_text()
    keywords = ['必ず合格', '合格', '頑張', '応援', '健闘']
    if not any(k in text for k in keywords):
        results.append(('J19', 'ERROR',
                        'フッターに励まし文言が見つかりません '
                        '（"必ず合格"等のキーワード）'))


def check_J20_smooth_scroll(script_text, style_text, results):
    """スムーズスクロール JS の存在"""
    has_js = ('scrollIntoView' in script_text or
              "behavior: 'smooth'" in script_text or
              'behavior:"smooth"' in script_text or
              'scroll-behavior' in style_text)
    if not has_js:
        results.append(('J20', 'ERROR',
                        'スムーズスクロール JS/CSS が見つかりません'))


def check_J21_depth(html, soup, results):
    """深度フロア（水増し検出）。当面 WARNING（floor は未較正の仮値のため）。
    計測: bytes / <h4> / <li> / 第4部見出し 4-1〜4-6(h3) / 重要度ランク rank-A〜D 網羅。
    各メッセージに実測値と floor を併記する（例: "h4=79 (floor 50)"）。
    """
    # bytes（UTF-8 実バイト数 = wc -c 相当）
    nbytes = len(html.encode('utf-8'))
    if nbytes < J21_MIN_BYTES:
        results.append(('J21', 'WARN',
                        f'本文量が薄い: bytes={nbytes} (floor {J21_MIN_BYTES})'))

    # <h4> 数
    nh4 = len(soup.find_all('h4'))
    if nh4 < J21_MIN_H4:
        results.append(('J21', 'WARN',
                        f'見出し階層が浅い: h4={nh4} (floor {J21_MIN_H4})'))

    # <li> 数
    nli = len(soup.find_all('li'))
    if nli < J21_MIN_LI:
        results.append(('J21', 'WARN',
                        f'箇条書きが少ない: li={nli} (floor {J21_MIN_LI})'))

    # 第4部見出し 4-1〜4-6（<h3> テキスト先頭一致で検出。h4 ではない）
    h3_texts = [h.get_text(strip=True) for h in soup.find_all('h3')]
    missing_h = [p for p in J21_PART4_HEADINGS
                 if not any(t.startswith(p + '.') for t in h3_texts)]
    if missing_h:
        found = len(J21_PART4_HEADINGS) - len(missing_h)
        results.append(('J21', 'WARN',
                        f'第4部見出し <h3>4-N. 不足: {", ".join(missing_h)} '
                        f'(検出 {found}/{len(J21_PART4_HEADINGS)})'))

    # 重要度ランク網羅 rank-A〜D（各 1 回以上出現すること）
    #   論点が薄いとランク付けが欠落し網羅が崩れる → 水増し検出に資する。
    missing_r = [r for r in J21_REQUIRED_RANKS if soup.find(class_=r) is None]
    if missing_r:
        present = len(J21_REQUIRED_RANKS) - len(missing_r)
        results.append(('J21', 'WARN',
                        f'重要度ランク網羅不足: {", ".join(missing_r)} 不在 '
                        f'(検出 {present}/{len(J21_REQUIRED_RANKS)} 段階)'))


# TODO(J21): 刑JX032 再生成の実測値で floor(J21_MIN_BYTES/H4/LI) を再較正後、
#            WARNING → ERROR への格上げを検討する。
#            将来強化案: rank-A〜D の網羅を「第4部見出し 4-1〜4-6 の各配下スコープ」で判定。


# ============================================================
# v4 LOOP-FOLD 追加チェック（JC1〜JD1）
#   単一ファイル維持・前半コア/後半deep折りたたみ・exec-summary削除・模範答案reveal。
#   v4 判定（<details id="deep-dive"> の存在）時のみ実行。当面 WARNING。
#   ※ 既存 v3.2 生成物（exec-summary あり・deep-dive なし）は v4 判定されず影響なし。
#   ※ 新 v 系の生成が安定したら ERROR へ格上げ（末尾 TODO）。
# ============================================================

def is_v4_loopfold(soup):
    """v4 LOOP-FOLD かどうか（後半 deep 折りたたみの存在で判定）"""
    return soup.find('details', id='deep-dive') is not None


def check_JC1_no_exec_summary(soup, results):
    """答えを先出しするエグゼクティブサマリーが無いこと（reveal 前確定の構造担保）"""
    if soup.find(id='exec-summary') is not None:
        results.append(('JC1', 'WARN',
                        'エグゼクティブサマリー(#exec-summary)が残存。v4 では削除する'
                        '（答えを先出ししない・事案足場は別カードに残す）'))


def check_JC2_core_before_deep(html, soup, results):
    """物理順序：コア（模範答案）→ deep（折りたたみ）になっていること"""
    if soup.find(class_='model-answer') is None:
        return
    pos_ma = html.find('class="model-answer"')
    pos_deep = html.find('id="deep-dive"')
    if pos_ma != -1 and pos_deep != -1 and pos_deep < pos_ma:
        results.append(('JC2', 'WARN',
                        'deep 層(#deep-dive)が模範答案より前にある。'
                        '前半コア→後半deep の物理順序にする'))


def check_JC3_deep_folds_part45(soup, results):
    """第4部・第5部が <details id="deep-dive"> 内に折りたたまれていること"""
    deep = soup.find('details', id='deep-dive')
    if deep is None:
        return
    if deep.find('section', id='part4') is None:
        results.append(('JC3', 'WARN', '第4部(#part4)が deep-dive 折りたたみ内にない'))
    if deep.find('section', id='part5') is None:
        results.append(('JC3', 'WARN', '第5部(#part5)が deep-dive 折りたたみ内にない'))


def check_JC4_reveal_answer(soup, results):
    """模範答案が reveal（<details class="reveal-answer">）で封じられていること"""
    reveal = soup.find('details', class_='reveal-answer')
    if reveal is None:
        results.append(('JC4', 'WARN',
                        '模範答案の reveal(<details class="reveal-answer">)が無い。'
                        '模範答案を先に見せない構造にする'))
        return
    if reveal.find(class_='model-answer') is None:
        results.append(('JC4', 'WARN', 'reveal-answer 内に .model-answer が無い'))


def check_JD1_core_self_sufficient(soup, results):
    """コア前半が周回＋誤答修正で自己充足（事案足場・模範答案・講師アドバイス・論点抽出）"""
    missing = []
    if soup.find(id='case-overview') is None and soup.find(id='relationship-diagram') is None:
        missing.append('事案足場(case-overview/relationship-diagram)')
    if soup.find(class_='model-answer') is None:
        missing.append('模範答案(.model-answer)')
    if soup.find(class_='lecturer-advice') is None:
        missing.append('講師のアドバイス(.lecturer-advice)')
    if soup.find(id='issue-extraction') is None:
        missing.append('論点抽出(#issue-extraction)')
    if missing:
        results.append(('JD1', 'WARN',
                        'コア前半の自己充足要素が不足: ' + ', '.join(missing)))


def check_JSB_tag_balance(html, results):
    """div/section/details の開閉タグ均衡（生成時の閉じタグ欠落を検出）。
    BeautifulSoup は寛容パースで自動補完するため J 系では拾えない構造欠陥を、
    生 HTML のタグ計数で検出する。全ファイル対象・当面 WARNING（誤検出回避）。
    ※ 開タグは `<div ...>` / `<div>`、閉は `</div>` を数える（属性内の文字列は対象外の近似）。
    """
    for tag in ('div', 'section', 'details'):
        opens = len(re.findall(rf'<{tag}(?=[\s>])', html))
        closes = len(re.findall(rf'</{tag}\s*>', html))
        if opens != closes:
            diff = opens - closes
            results.append(('JSB', 'WARN',
                            f'<{tag}> 開閉不均衡: 開 {opens} / 閉 {closes} '
                            f'(差 {diff:+d}・{"閉じタグ欠落" if diff > 0 else "閉じタグ過多"}の可能性)'))


# TODO(JC/JD): 新 v 系（v4 LOOP-FOLD）の生成が安定したら WARNING → ERROR へ格上げ。
#              既存 v3.2 生成物は is_v4_loopfold=False で対象外のまま温存する。


# ============================================================
# Driver
# ============================================================

def validate(html_path, verbose=False, mode='all'):
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
    run_core = mode in ('all', 'core')
    run_deep = mode in ('all', 'deep')

    if run_core:
        check_J1_html_lang(soup, results)
        check_J2_title(soup, results)
        check_J3_google_fonts(soup, results)
        check_J4_font_vars(style_text, results)
        check_J5_accent_mid(style_text, results)
        check_J6_body_typography(style_text, results)
        check_J7_keybox_specificity(style_text, results)
        check_J8_keybox_before(style_text, results)
        check_J9_label_boxes(style_text, results)
        check_J10_judgment_text(style_text, results)
        check_J11_para_num(style_text, results)
        check_J12_model_answer(style_text, results)
        check_J13_grading(style_text, results)
        check_J14_container_maxwidth(style_text, results)
        check_J15_docheader_absolute(style_text, results)
        check_J16_no_legacy_paragraph_num(soup, results)
        check_J17_no_palette_names_in_body(soup, results)
        check_J18_back_refs(soup, results)
        check_J19_footer_encouragement(soup, results)
        check_J20_smooth_scroll(script_text, style_text, results)
        check_JSB_tag_balance(html, results)
        # v4 LOOP-FOLD 追加（<details id="deep-dive"> 検出時のみ・当面 WARNING）
        if is_v4_loopfold(soup):
            check_JC1_no_exec_summary(soup, results)
            check_JC2_core_before_deep(html, soup, results)
            check_JC3_deep_folds_part45(soup, results)
            check_JC4_reveal_answer(soup, results)
            check_JD1_core_self_sufficient(soup, results)

    if run_deep:
        check_J21_depth(html, soup, results)

    errors = [r for r in results if r[1] == 'ERROR']
    warnings = [r for r in results if r[1] == 'WARN']

    ver_label = ' [v4 LOOP-FOLD]' if is_v4_loopfold(soup) else ' [v3.2]'
    mode_label = '' if mode == 'all' else f' ({mode}-only)'
    print(f'\n{"=" * 60}')
    print(f'JX 検証結果{ver_label}{mode_label}: {html_path}')
    print(f'{"=" * 60}')

    if not results:
        print(f'\n✅ 全件通過（J1〜J21）')
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
        print(f'❌ ERROR {len(errors)} 件。修正が必要です。')
        return 1
    else:
        print(f'⚠️  WARNING のみ。必須項目はすべて通過しています。')
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='JX v3.2 軽量検証スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使い方:
  python scripts/validate-jx.py outputs/001_JX/001_刑法/刑JX001.html

ERROR が 0 件なら配信可能。
        """
    )
    parser.add_argument('html_path', help='検証対象の HTML ファイルパス')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='詳細出力')
    parser.add_argument('--core-only', action='store_true',
                       help='コア検査のみ（J1-J20＋JC/JD・J21 深度フロアを省略）')
    parser.add_argument('--deep-only', action='store_true',
                       help='深度フロア(J21)のみ')
    args = parser.parse_args()

    mode = 'all'
    if args.core_only:
        mode = 'core'
    elif args.deep_only:
        mode = 'deep'
    return validate(args.html_path, args.verbose, mode)


if __name__ == '__main__':
    sys.exit(main())
