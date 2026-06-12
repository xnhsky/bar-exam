# -*- coding: utf-8 -*-
"""既存 TTS 台本の出だしに連番ラベル「{問題番号}の{連番}」を後付けする。

仕様（prompts/tts-jx-headless.md・c617bbc）:
  - 全 .txt の出だし最初の発話 = 「{N}の{k}」(N=問題IDの数字・先頭ゼロ除去)
  - 連番1: ラベル「Nの1」を言ってから冒頭スパルタへ
  - 連番2+: 「Nのk、続きから行くよ」型の冒頭接続文がラベルを兼ねる

使い方:
  python fix-tts-labels.py           # dry-run（変更予定の一覧）
  python fix-tts-labels.py --write   # 実際に書き換え
"""
import argparse
import os
import re

TTS_ROOT = r"C:\Users\OWNER\bar-exam\outputs\tts"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    fixed, skipped, errors = [], [], []
    for d in sorted(os.listdir(TTS_ROOT)):
        dpath = os.path.join(TTS_ROOT, d)
        if not os.path.isdir(dpath):
            continue
        m = re.search(r"(\d+)$", d)
        if not m:
            errors.append(f"{d}: 問題番号を抽出できない")
            continue
        n = int(m.group(1))  # 先頭ゼロ除去
        for fn in sorted(os.listdir(dpath)):
            fm = re.fullmatch(re.escape(d) + r"-(\d+)\.txt", fn)
            if not fm:
                continue
            k = int(fm.group(1))
            path = os.path.join(dpath, fn)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            label = f"{n}の{k}"
            # 既にラベル始まりなら skip
            if re.match(r"^\s*" + re.escape(label) + r"[、。]", text):
                skipped.append(fn)
                continue
            if k == 1:
                new = f"{label}。\n\n" + text.lstrip("\n")
                how = f"prepend「{label}。」(独立発話)"
            else:
                new = f"{label}、" + text.lstrip("\n")
                how = f"先頭文に「{label}、」前置"
            fixed.append((fn, how))
            if args.write:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new)

    print(f"対象: fix={len(fixed)} skip(ラベル済)={len(skipped)} err={len(errors)}")
    for fn, how in fixed:
        print(f"  FIX  {fn}: {how}")
    for e in errors:
        print(f"  ERR  {e}")
    if not args.write:
        print("\n(dry-run: --write で書き換え)")


if __name__ == "__main__":
    main()
