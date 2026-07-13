#!/usr/bin/env python3
"""tx-dgm ブロックを _lex の指定アンカー行直後へ挿入する（TX-DGM 後付け改訂用）

usage: python scripts/tx-dgm-insert.py <対象_lex.html> <spec.json>

spec.json は挿入指示の配列：
  [{"after": "ファイル内で一意な生の部分文字列（アンカー）",
    "block": "<div class=\"tx-dgm\" data-dgm=\"NNN-01\">…（1行・改行禁止）"}, ...]

規約（docs/tx-dgm-retrofit-handoff.md・spec §v13p）：
- block は G67 の許可クラスのみ／inline style 禁止／1行で書く（機械検査して違反は挿入前に止める）
- アンカーは出現数1の生文字列。行末が挿入点になるので、
  物語側＝段落 </p> を含む末尾、カード側＝syn-path の閉じ </div> を含む末尾を使う
- アンカー内の改行は常に \n で書く（CRLF ファイルへ970は自動変換）
- 同一アンカーに複数ブロックを積む場合、spec の並び順と逆の視覚順になる
  （後から挿入した方が上に入る）＝視覚順 A,B にしたければ spec は B,A の順に書く
- 挿入後は必ず validate-tx-core.py（G67）を通す
"""
import json, re, sys

ALLOWED = {
    'tx-dgm', 'tx-dgm-tag', 'tx-dgm-title', 'tx-dgm-lanes', 'is-3',
    'dgm-lane', 'dgm-lane-head', 'dgm-lane-obj', 'dgm-lane-law', 'dgm-lane-body',
    'dgm-rule', 'dgm-src', 'dgm-case', 'dgm-verdict',
    'is-ok', 'is-ng', 'is-acc', 'is-teal', 'is-flat',
    'tx-dgm-steps', 'dgm-step', 'dgm-step-no', 'dgm-next', 'tx-dgm-fork',
}

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    path, specpath = sys.argv[1], sys.argv[2]
    src = open(path, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in src[:4000] else '\n'
    specs = json.load(open(specpath, encoding='utf-8'))

    for sp in specs:
        # アンカー内の \n はファイルの改行コードへ正規化（JSON では常に \n で書く）
        if '\n' in sp['after'] and nl != '\n':
            sp['after'] = sp['after'].replace('\n', nl)

    errors = []
    for i, sp in enumerate(specs):
        blk = sp['block']
        for cm in re.finditer(r'class="([^"]*)"', blk):
            for cls in cm.group(1).split():
                if cls not in ALLOWED:
                    errors.append(f"spec#{i}: 不許可クラス {cls}")
        if 'style=' in blk:
            errors.append(f"spec#{i}: inline style 禁止")
        if '\n' in blk or '\r' in blk:
            errors.append(f"spec#{i}: ブロックは1行で書く")
        n = src.count(sp['after'])
        if n != 1:
            errors.append(f"spec#{i}: アンカー出現数 {n} (要1): {sp['after'][:60]}...")
    if errors:
        print("[ERROR]")
        for e in errors:
            print(" ", e)
        sys.exit(1)

    for sp in specs:
        pos = src.index(sp['after']) + len(sp['after'])
        eol = src.find(nl, pos)
        if eol == -1:
            print("[ERROR] 行末が見つからない:", sp['after'][:60])
            sys.exit(1)
        insert_at = eol + len(nl)
        src = src[:insert_at] + sp['block'] + nl + src[insert_at:]

    open(path, 'w', encoding='utf-8', newline='').write(src)
    print(f"[OK] {len(specs)} blocks inserted into {path} "
          f"(newline={'CRLF' if nl == chr(13) + chr(10) else 'LF'})")

if __name__ == '__main__':
    main()
