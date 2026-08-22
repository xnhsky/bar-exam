#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13v-extract.py ── §v13v「📖 ものがたり」執筆の素材抽出。usage: python3 v13v-extract.py <file.html>

正誤表の各行に入れる data-brief-story（物語解説の全体＋当該記述の要約＋具体例）を書くために、
執筆者（人／headless エージェント）が読むべき素材だけを 1 画面に出す：

  - 物語解説（.fa-narrative）のラベル付き段落（＝その問題を貫く一本の物差し）
  - 正誤表の各行：記述キー・○×・印付き原文（data-brief-mark）・5点フローの切断点/転用
  - 既に data-brief-story が入っている行（＝執筆済み・冪等判定）

出力は素の日本語テキスト（プロンプトへそのまま貼れる形）。HTML は書き換えない。
"""
import io
import re
import sys


def text_of(html):
    t = re.sub(r'<[^>]*>', '', html or '')
    t = (t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
          .replace('&quot;', '"').replace('&nbsp;', ' '))
    return re.sub(r'\s+', ' ', t).strip()


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 v13v-extract.py <file.html>')
    path = sys.argv[1]
    with io.open(path, encoding='utf-8', newline='') as f:
        s = f.read()

    print('== FILE: %s' % path)
    has_css = 'TX-VERDICT-STORY:BEGIN' in s
    has_eng = 'function appendStoryLine(' in s
    print('== 土台: CSS=%s ENGINE=%s（どちらか無ければ先に '
          'python -X utf8 scripts/tx-lex-verdict-redesign.py <file> を通す）'
          % ('あり' if has_css else 'なし', 'あり' if has_eng else 'なし'))

    m = re.search(r'<div class="fa-narrative">(.*?)</div>', s, re.S)
    if m:
        t = re.search(r'fa-narrative-title[^>]*>(.*?)</p>', m.group(1), re.S)
        if t:
            print('\n== 物語解説（題）: %s' % text_of(t.group(1)))
        for label, body in re.findall(r'<p[^>]*data-fa-label="([^"]*)"[^>]*>(.*?)</p>', m.group(1), re.S):
            print('[物語:%s] %s' % (label, text_of(body)))
    else:
        print('\n== 物語解説なし（物差しは各記述の切断点・転用から組み立てる）')

    print('\n== 正誤表の記述')
    rows = re.findall(r'<tr data-stmt="([^"]+)" data-verdict="([^"]+)"(.*?)</tr>', s, re.S)
    if not rows:
        print('（正誤表の行が見つからない＝対象外の可能性）')
    for stmt, verdict, body in rows:
        done = 'data-brief-story=' in body
        mk = re.search(r'data-brief-mark="(.*?)"><td', body, re.S)
        print('--- 記述%s [%s]%s %s' % (stmt, verdict, '（執筆済み）' if done else '',
                                       text_of(mk.group(1)) if mk else ''))
        for tag, line in re.findall(
                r'<p class="tx-reflex-line[^"]*"><span class="tx-reflex-tag">(.*?)</span>(.*?)</p>', body, re.S):
            if tag in ('切断点', '転用'):
                print('   %s: %s' % (tag, text_of(line)))
    todo = [r[0] for r in rows if 'data-brief-story=' not in r[2]]
    print('\n== 未執筆の記述キー: %s' % (('、'.join(todo)) if todo else 'なし（全記述 執筆済み）'))


if __name__ == '__main__':
    main()
