#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-iss-denumber-backfill.py  （冪等）

骨子パズル（ARIADNE）の論点チップから冠番号を除去する一括バックフィル。

なぜ：本物の論点チップ `<span class="iss">【論点①】…</span>` が番号付きで、
おとり `data-kp-decoys="iss:【論点】…"` が番号なしだと、学習者が
「番号の有無＝本物／おとり」「①→第1・②→第2＝配置順」を見分けられ、
論点抽出＋並べ替えの能動想起（パズルの核心）が成立しない＝ネタバレになる。
仕様 jx-ariadne-v1.2.0-core.md 9-3 のおとり例も `iss:【論点】…`（番号なし）で、
本物側も番号を焼き込まない想定。よって本物 .iss・おとり双方を `【論点】…` へ統一する。

対象（安全＝この2コンテキストのみ。本文 `論点①`・表 `核心論点①` は無冠括弧で不変）：
  1) チップ:  class="iss">【論点①】 → class="iss">【論点】
  2) おとり:  iss:【論点①】        → iss:【論点】
番号は 半角0-9 / 全角０-９ / 丸数字①-⑳ に対応。

使い方:
  python scripts/ariadne-iss-denumber-backfill.py            # dry-run（差分表示のみ）
  python scripts/ariadne-iss-denumber-backfill.py --apply    # 実書き込み
  python scripts/ariadne-iss-denumber-backfill.py --apply path1 path2 ...  # 個別指定
"""
import re
import sys
import glob

NUM = r'[0-9０-９①-⑳]+'  # 半角/全角/丸数字①-⑳
RE_CHIP  = re.compile(r'(class="iss">【論点)' + NUM + r'(】)')
RE_DECOY = re.compile(r'(iss:【論点)' + NUM + r'(】)')

# 検証用：denumber 後に本物 iss とおとりが完全一致＝チップ重複しないか確認
RE_ISS_TEXT   = re.compile(r'class="iss">(【論点】[^<]*)</span>')
RE_DECOY_TEXT = re.compile(r'iss:(【論点】[^|"]*)')


def process(text):
    new = RE_CHIP.sub(r'\1\2', text)
    new = RE_DECOY.sub(r'\1\2', new)
    return new


def main():
    args = [a for a in sys.argv[1:] if a != '--apply']
    apply = '--apply' in sys.argv
    files = args or glob.glob('outputs/ux/001_ARIADNE/**/*ARIADNE.html', recursive=True)
    files = sorted(files)

    changed = 0
    total_chip = 0
    total_decoy = 0
    dup_warn = []
    for f in files:
        s = open(f, encoding='utf-8').read()
        nchip = len(RE_CHIP.findall(s))
        ndecoy = len(RE_DECOY.findall(s))
        if nchip == 0 and ndecoy == 0:
            continue
        out = process(s)
        if out == s:
            continue
        changed += 1
        total_chip += nchip
        total_decoy += ndecoy
        # チップ重複チェック（denumber 後に本物=おとりで同一文言になっていないか）
        iss_set = set(RE_ISS_TEXT.findall(out))
        decoy_set = set(RE_DECOY_TEXT.findall(out))
        dup = iss_set & decoy_set
        if dup:
            dup_warn.append((f, dup))
        print(f"{'[apply]' if apply else '[dry] '} {f}  iss:{nchip} decoy:{ndecoy}")
        if apply:
            open(f, 'w', encoding='utf-8').write(out)

    print(f"\n--- {'適用' if apply else 'ドライラン'} 完了 ---")
    print(f"変更ファイル: {changed} / 走査 {len(files)}")
    print(f"除番号 チップ: {total_chip}  おとり: {total_decoy}")
    if dup_warn:
        print("\n[WARN] denumber 後に本物チップとおとりが同一文言（重複チップ）になるファイル:")
        for f, d in dup_warn:
            print(f"   {f}: {sorted(d)}")
        print("   → 該当おとりを別文言へ手当て推奨")
    return 0


if __name__ == '__main__':
    sys.exit(main())
