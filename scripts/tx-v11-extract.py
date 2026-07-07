#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v11 _lex から slots authoring に必要な素材を1発ダンプする。"""
import re, html, sys
f = sys.argv[1]
s = open(f, encoding='utf-8').read()
def strip(t):
    t = re.sub(r'<rt>.*?</rt>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()
print("TITLE:", re.search(r'<title>(.*?)</title>', s).group(1))
ak = re.search(r'data-answer-key="([^"]*)"', s)
print("ANSWER-KEY:", ak.group(1) if ak else "??")
print("\n=== 記述原文（problem-text）===")
for i, p in enumerate(re.findall(r'<div class="problem-text"><span class="choice-num-inline">\d+</span>(.*?)</div>', s, re.S)[:5], 1):
    print(i, strip(p)[:260]); print()
print("=== ox-stmt 論点コア ===")
for m in re.findall(r'data-stmt="(\d)"[^>]*>(.*?)</div>', s, re.S)[:5]:
    print(m[0], strip(m[1])[:150])
print("\n=== basis-card headers（条文/判例）===")
for m in re.findall(r'class="basis-card-header[^"]*"[^>]*>(.*?)</', s, re.S)[:20]:
    t = strip(m)
    if t: print(" -", t[:100])
print("\n=== THE GIST（各記述の解説核）===")
for i, m in enumerate(re.findall(r'class="syn-lead"[^>]*>(.*?)</p>', s, re.S)[:6], 1):
    print(i, strip(m)[:280]); print()
