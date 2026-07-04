#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARIADNE のセクション見出し(.sec-h)・導入文(.lead)がクリーム背景に溶けて見づらい問題を改善。

見出し＝左アクセントバー＋淡い帯＋濃色文字(--li-deep)で背景から分離。
導入文＝白カード＋左罫＋影で浮かせる（強調 .emb は保持）。ACTIVE難易度色(--li-*/--a-head)を使うので
EASY/STD/HARD いずれの配色でも自動整合。CSS marker ブロックを <style> 末尾へ注入（冪等・本文不変・LF保持）。

usage: python scripts/ariadne-sechead-contrast.py [--apply] [files...]
"""
import re, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "/* === ARIADNE-SECHEAD-CONTRAST v1 (auto) BEGIN === */"
END = "/* === ARIADNE-SECHEAD-CONTRAST v1 (auto) END === */"

CSS = BEGIN + r"""
/* セクション見出し(.sec-h)＝淡い帯＋左アクセントバー＋濃色文字で背景から分離 */
.sec-h{position:relative; margin:40px 0 13px; padding:11px 18px 12px; background:linear-gradient(100deg,var(--li-soft) 0%,rgba(255,255,255,.55) 86%); border:1px solid var(--li-line); border-left:5px solid var(--a-head); border-radius:12px; box-shadow:0 5px 14px -8px rgba(70,58,80,.3)}
.sec-h .kick{color:var(--li-deep) !important}
.sec-h .ttl{color:var(--li-deep) !important; margin-top:4px; text-shadow:0 1px 0 rgba(255,255,255,.6)}
.sec-h .ico{box-shadow:0 2px 6px -1px rgba(70,58,80,.28)}
/* 導入文(.lead)＝白カード＋左罫＋影でクリーム背景から浮かせる */
.lead{color:var(--ink); background:#fff; border:1px solid var(--line-2); border-left:3px solid var(--a-head-lt); border-radius:11px; padding:12px 18px; margin:3px 0 16px; box-shadow:0 3px 10px -4px rgba(70,58,80,.16)}
""" + END

def inject_css(html):
    if BEGIN in html and END in html:
        return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: CSS, html, flags=re.S)
    i = html.rfind("</style>")
    return html if i < 0 else html[:i] + CSS + "\n" + html[i:]

def process(path, apply):
    raw = Path(path).read_bytes().decode("utf-8")
    new = inject_css(raw)
    changed = new != raw
    if changed and apply:
        Path(path).write_bytes(new.encode("utf-8"))
    return changed

def main():
    apply = "--apply" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        files = [str(ROOT / "canonical/ARIADNE.html")]
        files += sorted(glob.glob(str(ROOT / "outputs/ux/001_ARIADNE/**/*_ARIADNE.html"), recursive=True))
    ch = 0
    for f in files:
        if not Path(f).exists():
            continue
        if process(f, apply):
            ch += 1
            print(f"  {'[WROTE]' if apply else '[DIFF]'} {Path(f).name}")
    print(f"\n{ch} files {'updated' if apply else 'would change'} ({'APPLY' if apply else 'DRY-RUN'})")

if __name__ == "__main__":
    main()
