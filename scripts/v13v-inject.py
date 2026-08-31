#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13v-inject.py ── §v13v/§v13w「📖 CONTEXT」帯の決定論注入。

usage: python3 v13v-inject.py <file.html> <payload.json> [--force]

payload 形式:
{
  "stmts": [
    {"n": "1",
     "story": "…体系的位置づけ→趣旨→考え方のコツ（HTML 可・<b> のみ）…",
     "practice": "…⚙ IN PRACTICE 小箱＝実務での動き方 1〜2文（省略可）…",
     "example": "…\U0001F4C1 CASE FILE 小箱＝実名の具体例 1〜3文（省略可）…"},
    ...全記述分
  ]
}

保証:
  - 改行様式（LF/CRLF 混在）と本文を 1 バイトも動かさない（属性を1つ足すだけ）。
  - 属性は二重引用符で括るので、story/example に `"` があればエラー（鉤括弧「」を使う）。
  - 既に data-brief-story がある行はスキップ（冪等）。--force で置き換える。
  - CSS 区画（TX-VERDICT-STORY）とエンジン（appendStoryLine）が無ければエラー。
    先に `python -X utf8 scripts/tx-lex-verdict-redesign.py <file>` で土台を入れること。
"""
import io
import json
import sys

PRAC = "<span class='tx-vb-prac'><span class='tx-vb-prac-tag'>\u2699 IN PRACTICE</span>{}</span>"
EX = "<span class='tx-vb-ex'><span class='tx-vb-ex-tag'>\U0001F4C1 CASE FILE</span>{}</span>"


def main():
    args = [a for a in sys.argv[1:] if a != '--force']
    force = '--force' in sys.argv[1:]
    if len(args) < 2:
        raise SystemExit('usage: python3 v13v-inject.py <file.html> <payload.json> [--force]')
    path, payload_path = args[0], args[1]

    with io.open(path, encoding='utf-8', newline='') as f:
        html = f.read()
    with io.open(payload_path, encoding='utf-8') as f:
        payload = json.load(f)

    assert 'TX-VERDICT-STORY:BEGIN' in html, \
        'CSS 区画が無い。先に scripts/tx-lex-verdict-redesign.py で土台を入れる'
    assert 'function appendStoryLine(' in html, \
        'エンジンが無い。先に scripts/tx-lex-verdict-redesign.py で土台を入れる'

    n_ok = n_skip = 0
    for item in payload['stmts']:
        stmt = str(item['n'])
        story = item['story'].strip()
        practice = (item.get('practice') or '').strip()
        example = (item.get('example') or '').strip()
        body = story
        if practice:
            body += PRAC.format(practice)
        if example:
            body += EX.format(example)
        assert '"' not in body, '記述%s: 二重引用符は属性を壊す。「」を使う' % stmt

        key = '<tr data-stmt="%s" data-verdict=' % stmt
        assert html.count(key) == 1, '記述%s の行が 1 つに定まらない（%d 件）' % (stmt, html.count(key))
        i = html.index(key)
        j = html.index('data-brief-mark=', i)
        head = html[i:j]
        if 'data-brief-story=' in head:
            if not force:
                n_skip += 1
                continue
            k = head.index('data-brief-story="')
            e = head.index('"', k + len('data-brief-story="')) + 1
            while e < len(head) and head[e] == ' ':
                e += 1
            html = html[:i + k] + html[i + e:]
            j = html.index('data-brief-mark=', i)
        html = html[:j] + 'data-brief-story="%s" ' % body + html[j:]
        n_ok += 1

    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    print('[v13v-inject] %s  注入 %d 行 / スキップ（執筆済み）%d 行' % (path, n_ok, n_skip))


if __name__ == '__main__':
    main()
