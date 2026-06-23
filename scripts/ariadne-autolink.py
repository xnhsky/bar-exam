#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ariadne-autolink.py ― ARIADNE 深層部の「本文インライン相互リンク」付与。

深層部の 条文/判例/学説/用語 カード（.basis-card *-card[id]）をレジストリ化し、
本文中にその語が現れたら <a class="xref" href="#id"> でその語自体をリンクにする。
対象ゾーン:
  (A) 解法ナビの各 .step（→ 深層部カードへ前方リンク）
  (B) 深層部 .athena-graft 内の各カード本文（→ 他カードへ相互リンク・自カードは除外）

規律:
  - 語そのものをリンク（バッジは作らない）。
  - 1カード本文／1ステップにつき同一ターゲットは初出のみリンク（リンク過多を回避）。
  - 見出し(.basis-card-header / h5 / th / summary / button)・既存<a>内はリンクしない。
  - 自カードの語は自カード内ではリンクしない（自己リンク回避）。
  - 漢字で前後に連結する部分一致は弾く（例:「故意犯」「麻薬罪」では 故意/麻薬 を貼らない）。
使い方:
  python scripts/ariadne-autolink.py <file.html> [--dry-run] [--report]
"""
import re, sys, argparse

SKIP_OPEN = re.compile(r'<(a|h5|th|summary|button|script|style)\b', re.I)
SKIP_CLOSE = re.compile(r'</(a|h5|th|summary|button|script|style)>', re.I)

def is_kanji(ch):
    if not ch:
        return False
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF) or ch in '々〆〤' or ch == 'ー' or (0x30A0 <= o <= 0x30FF)

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)

CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩'

def clean_header(raw):
    """カードヘッダ HTML → 素のラベル文字列（freq-badge/絵文字/丸番号/判例①等を除去）"""
    t = re.sub(r'<span[^>]*class="[^"]*freq-badge[^"]*"[^>]*>.*?</span>', '', raw, flags=re.S)
    t = strip_tags(t)
    t = t.replace('　', ' ')
    # 絵文字・記号を除去
    t = re.sub(r'[📜⚖📖📕🧭🔑]', '', t)
    # 「判例①」「①」など先頭の丸番号/連番ラベル
    t = re.sub(r'^\s*(判例|学説|条文|用語)?\s*[' + CIRCLED + r']?\s*', '', t)
    return t.strip()

def primary_label(label):
    """（読み）や（説明）の前までを主ラベルに"""
    return re.split(r'[（(]', label, 1)[0].strip()

def build_registry(html):
    """(id, type, [aliases]) を返す"""
    cards = []
    for m in re.finditer(
        r'<div class="basis-card (statute|case|doctrine|term)-card" id="([^"]+)">\s*'
        r'<div class="basis-card-header">(.*?)</div>', html, re.S):
        ctype, cid, hdr = m.group(1), m.group(2), m.group(3)
        label = clean_header(hdr)
        prim = primary_label(label)
        aliases = set()
        if prim:
            aliases.add(prim)
        if ctype == 'statute':
            # 末尾の「N条(のM)(K項)」トークン
            jo = re.search(r'\d+条(?:の\d+)?(?:\d+項)?$', prim)
            if jo:
                aliases.add(jo.group(0))
            # 略称（…取締法）: 「麻薬及び向精神薬取締法」→「麻薬取締法」
            sp = re.sub(r'麻薬及び向精神薬取締法', '麻薬取締法', prim)
            if sp != prim:
                aliases.add(sp)
                jo2 = re.search(r'\d+条(?:の\d+)?(?:\d+項)?$', sp)
                if jo2:
                    aliases.add(jo2.group(0))
        elif ctype == 'case':
            mm = re.search(r'(最(?:大)?(?:決|判))昭和(\d+)年(\d+)月(\d+)日', prim)
            if mm:
                kind, yy, mo, dd = mm.group(1), mm.group(2), mm.group(3), mm.group(4)
                aliases.add(f'{kind}昭{yy}.{mo}.{dd}')
                aliases.add(f'昭{yy}.{mo}.{dd}')
                aliases.add(f'昭和{yy}年{"決定" if "決" in kind else "判決"}')
        elif ctype == 'term':
            if prim == '構成要件の実質的重なり合い':
                aliases.add('実質的重なり合い')
        cards.append({'id': cid, 'type': ctype, 'aliases': aliases})
    return cards

# 同名衝突時の優先（小さいほど優先）: 学説 > 用語、条文/判例は固有なので衝突しない想定
TYPE_RANK = {'statute': 0, 'case': 1, 'doctrine': 2, 'term': 3}

def build_alias_map(cards):
    alias_to = {}   # alias -> (id, rank)
    for c in cards:
        rank = TYPE_RANK[c['type']]
        for a in c['aliases']:
            if len(a) < 2:
                continue
            cur = alias_to.get(a)
            if cur is None or rank < cur[1]:
                alias_to[a] = (c['id'], rank)
    # 生成: 条文「N条」→「N条1項/2項/3項」（既存（用語等）を上書きしない）
    for c in cards:
        if c['type'] != 'statute':
            continue
        for a in list(c['aliases']):
            mm = re.fullmatch(r'(\d+条)', a)
            if mm:
                for k in ('1項', '2項', '3項'):
                    v = a + k
                    alias_to.setdefault(v, (c['id'], TYPE_RANK['statute']))
    items = [(a, t[0]) for a, t in alias_to.items()]
    items.sort(key=lambda x: -len(x[0]))   # 長い順（最長一致）
    return items

def split_text_tokens(chunk):
    """tag と text に分割。text トークンのインデックス配列も返す"""
    parts = re.split(r'(<[^>]*>)', chunk)
    text_idx = [i for i, p in enumerate(parts) if p and not p.startswith('<')]
    return parts, text_idx

def linkify_chunk(chunk, own_id, items):
    parts, text_idx = split_text_tokens(chunk)
    # 各 text トークンの前後隣接文字（タグをまたいだ境界判定用）
    before = {}
    after = {}
    prev_last = ''
    for i in text_idx:
        before[i] = prev_last
        prev_last = parts[i][-1] if parts[i] else prev_last
    nxt_first = ''
    for i in reversed(text_idx):
        after[i] = nxt_first
        nxt_first = parts[i][0] if parts[i] else nxt_first

    used = set()
    skip = 0
    out = []
    for i, p in enumerate(parts):
        if not p:
            out.append(p); continue
        if p.startswith('<'):
            if SKIP_OPEN.match(p) and not p.endswith('/>'):
                skip += 1
            elif SKIP_CLOSE.match(p):
                skip = max(0, skip - 1)
            out.append(p); continue
        if skip > 0:
            out.append(p); continue
        out.append(_link_text(p, own_id, items, used, before.get(i, ''), after.get(i, '')))
    return ''.join(out)

def _link_text(text, own_id, items, used, before_char, after_char):
    n = len(text)
    res = []
    i = 0
    while i < n:
        hit = None
        for alias, tid in items:          # 長い順
            if tid in used or tid == own_id:
                continue
            L = len(alias)
            if text[i:i+L] != alias:
                continue
            prev = text[i-1] if i > 0 else before_char
            nxt = text[i+L] if i+L < n else after_char
            if is_kanji(prev) or is_kanji(nxt):
                continue
            hit = (alias, tid, L); break
        if hit:
            alias, tid, L = hit
            res.append(f'<a class="xref auto" href="#{tid}">{alias}</a>')
            used.add(tid); i += L
        else:
            res.append(text[i]); i += 1
    return ''.join(res)

def process(html, report=False):
    cards = build_registry(html)
    items = build_alias_map(cards)
    counts = {'A_steps': 0, 'B_cards': 0}

    # ---- Zone A: 解法ナビの各 .step ----
    a_start = html.find('<!-- ===== 解法ナビ')
    a_end = html.find('How to Build the Outline')
    if a_start != -1 and a_end != -1:
        region = html[a_start:a_end]
        def repl_step(m):
            chunk = m.group(0)
            new = linkify_chunk(chunk, None, items)
            counts['A_steps'] += new.count('<a class="xref auto"')
            return new
        region2 = re.sub(r'<div class="step"[^>]*>.*?(?=\n  <!-- 手|\n  <!-- =====|\Z)',
                         repl_step, region, flags=re.S)
        html = html[:a_start] + region2 + html[a_end:]

    # ---- Zone B: 深層部 athena-graft 内の各カード ----
    b_start = html.find('<div class="athena-graft">')
    b_end = html.find('<a class="go-athena"')
    if b_start != -1 and b_end != -1:
        region = html[b_start:b_end]
        def repl_card(m):
            cid = m.group('id')
            chunk = m.group(0)
            new = linkify_chunk(chunk, cid, items)
            counts['B_cards'] += new.count('<a class="xref auto"')
            return new
        region2 = re.sub(
            r'<div class="basis-card [a-z]+-card" id="(?P<id>[^"]+)">.*?(?=\n<div class="basis-card |\n      <div class="graft-h|\Z)',
            repl_card, region, flags=re.S)
        html = html[:b_start] + region2 + html[b_end:]

    if report:
        sys.stderr.write('=== registry ===\n')
        for c in cards:
            sys.stderr.write(f"  [{c['type']:8}] {c['id']:30} :: {sorted(c['aliases'])}\n")
        sys.stderr.write(f"=== links: steps={counts['A_steps']} cards={counts['B_cards']} ===\n")
    return html

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args()
    with open(args.file, encoding='utf-8') as f:
        html = f.read()
    # 既存の自動リンク（再実行）を一旦剥がして冪等化。class="xref auto" のみ対象＝
    # 手書きの 論点マトリクス等 class="xref"（auto なし）は温存。
    html = re.sub(r'<a class="xref auto" href="#[^"]+">(.*?)</a>', r'\1', html)
    out = process(html, report=args.report)
    if args.dry_run:
        sys.stderr.write('(dry-run: not written)\n')
        return
    with open(args.file, 'w', encoding='utf-8') as f:
        f.write(out)
    sys.stderr.write(f'written: {args.file}\n')

if __name__ == '__main__':
    main()
