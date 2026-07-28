#!/usr/bin/env python3
"""§v13q 改訂の決定論注入。usage: python3 v13q_inject.py <file.html> <payload.json>

payload 形式:
{
  "stmts": [
    {"n": "1",
     "anscomp": "…規範完全文（HTML可・二重引用符禁止）…",
     "gist": "…新GIST（syn-tag 後の中身・HTML可）…",      // 省略時は差し替えない
     "fix": "→ 最小訂正" | null                             // null/省略＝訂正チップは触らない
    }, ...
  ],
  "hide_basis": true|false      // true: 可視の空 #basis を hidden アンカーへ
}

保証: UTF-8 BOM / CRLF 保持・全置換に assert・冪等（既に anscomp が有る記述はエラー）。
CSS: TX-ANSCOMP 区画が無ければ canonical/GENESIS-CARD.html から逐語で移植。
"""
import io, json, re, sys

path, payload_path = sys.argv[1], sys.argv[2]
with io.open(path, encoding='utf-8', newline='') as f:
    html = f.read()
with io.open(payload_path, encoding='utf-8') as f:
    payload = json.load(f)

# --- CSS 区画（canonical から逐語移植・BEGIN/END マーカー込み） ---
if 'TX-ANSCOMP:BEGIN' not in html:
    can = io.open('canonical/GENESIS-CARD.html', encoding='utf-8', newline='').read()
    s = can.find('/* TX-ANSCOMP:BEGIN')
    e = can.find('/* TX-ANSCOMP:END */', s)
    assert s > 0 and e > s, 'canonical に TX-ANSCOMP 区画が無い'
    block = can[s:e + len('/* TX-ANSCOMP:END */')]
    i = html.find('</style>')
    assert i > 0
    html = html[:i] + block + '\r\n' + html[i:]

def sub_fix(seg, fix, quote):
    """seg 内の tx-stmt-fix チップ本文を fix に置換（1個のときだけ・複数は触らない）"""
    pat = re.compile(r'(<span class=' + quote + r'tx-stmt-fix' + quote + r'>)(.*?)(</span>)', re.S)
    hits = pat.findall(seg)
    if len(hits) != 1:
        return seg, False
    return pat.sub(lambda m: m.group(1) + fix + m.group(3), seg, count=1), True

for st in payload['stmts']:
    n = str(st['n'])
    ans = st['anscomp']
    assert '"' not in ans, f'記述{n}: anscomp に二重引用符'
    m = re.search(rf'(<article class="tx-inline-card" data-stmt="{re.escape(n)}".*?</article>)', html, re.S)
    assert m, f'記述{n}: article が見つからない'
    seg = m.group(1)
    new = seg

    # syn-orig: 訂正チップ短縮 → anscomp 追記
    om = re.search(r'<p class="syn-orig">.*?</p>', new, re.S)
    assert om, f'記述{n}: syn-orig 無し'
    orig = om.group(0)
    assert 'tx-anscomp-line' not in orig, f'記述{n}: syn-orig に anscomp 既存'
    new_orig = orig
    if st.get('fix'):
        new_orig, ok = sub_fix(new_orig, st['fix'], '"')
        assert ok, f'記述{n}: syn-orig の fix チップが1個でない'
    new_orig = new_orig[:-len('</p>')] + f'<span class="tx-anscomp-line">{ans}</span></p>'
    new = new.replace(orig, new_orig, 1)

    # GIST 差し替え
    if st.get('gist'):
        lm = re.search(r'(<p class="syn-lead"><span class="syn-tag">[^<]*</span>)(.*?)(</p>)', new, re.S)
        assert lm, f'記述{n}: syn-lead 無し'
        new = new.replace(lm.group(0), lm.group(1) + st['gist'] + lm.group(3), 1)

    html = html.replace(seg, new, 1)

    # 正誤表 brief-mark: 訂正チップ短縮 → 同一 anscomp 追記
    tm = re.search(rf'(<tr data-stmt="{re.escape(n)}" data-verdict="[xo]" data-brief-mark=")(.*?)(")', html, re.S)
    if not tm:
        print(f'NOTE: 記述{n} は正誤表 brief-mark 行なし（v13.0 表）→ カード側のみ注入')
        continue
    bm = tm.group(2)
    assert 'tx-anscomp-line' not in bm, f'記述{n}: brief-mark に anscomp 既存'
    if st.get('fix'):
        bm2, ok = sub_fix(bm, st['fix'], "'")
        if ok:
            bm = bm2
    bm = bm + f"<span class='tx-anscomp-line'>{ans}</span>"
    html = html.replace(tm.group(0), tm.group(1) + bm + tm.group(3), 1)

# --- 可視の空 #basis → hidden アンカー ---
if payload.get('hide_basis'):
    b = re.search(r'<section class="section" id="basis"[^>]*>(.*?)</section>', html, re.S)
    assert b, '#basis 無し'
    inner_txt = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', b.group(1)))
    assert inner_txt in ('', '↑ページ先頭へ'), '#basis に中身がある（hide 不可）'
    html = html.replace(b.group(0), '<section class="section" id="basis" hidden=""></section>', 1)

with io.open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(html)
print(f'OK: {len(payload["stmts"])} 記述へ注入完了 → {path}')
