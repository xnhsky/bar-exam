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
  J14  .container max-width: 1080px
  J15  .doc-header に position:absolute
  J16  旧 <strong>第N項</strong> 表記の不在
  J17  配色パターン名の <body> 内不在
  J18  PART 5 (back-refs) ≥ 3
  J19  フッターに励まし文言
  J20  スムーズスクロール JS

使い方：
  python scripts/validate-jx.py outputs/jx/刑JX/刑JX001.html
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
    elif int(m.group(1)) != 1080:
        results.append(('J14', 'ERROR',
                        f'.container max-width は 1080px 必須: '
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
    palette_names = [
        'ホワイト・ノーブル', 'ローズシャンブル', 'セージブラリー',
        'ラベンダードーン', 'P1', 'P2', 'P3'
    ]
    # P1/P2/P3 は本文に他用法あり得るので除外
    palette_strict = ['ホワイト・ノーブル', 'ローズシャンブル',
                      'セージブラリー', 'ラベンダードーン']
    for name in palette_strict:
        if name in body_text:
            results.append(('J17', 'ERROR',
                            f'配色パターン名 "{name}" が <body> 内に出現'))


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


# ============================================================
# Driver
# ============================================================

def validate(html_path, verbose=False):
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

    errors = [r for r in results if r[1] == 'ERROR']
    warnings = [r for r in results if r[1] == 'WARN']

    print(f'\n{"=" * 60}')
    print(f'JX v3.2 検証結果: {html_path}')
    print(f'{"=" * 60}')

    if not results:
        print(f'\n✅ 全件通過（J1〜J20）')
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
  python scripts/validate-jx.py outputs/jx/刑JX/刑JX001.html

ERROR が 0 件なら配信可能。
        """
    )
    parser.add_argument('html_path', help='検証対象の HTML ファイルパス')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='詳細出力')
    args = parser.parse_args()

    return validate(args.html_path, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
