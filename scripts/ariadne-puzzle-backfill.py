# -*- coding: utf-8 -*-
"""ARIADNE 答案構成パズル backfill（冪等）

刑JX001_ARIADNE.html（手作業で完成した設計ソース）から
  ① パズル/想起/下書き CSS（3領域）
  ② パズル JS（boot IIFE・レベル/チップ/想起/フォールバック）
を抽出し、既存 ARIADNE 生成物へ注入する。

注入する汎用部分のみで Lv1（論点 .iss）・Lv3（＋結論 <u>＋見出し .b1）のパズルが
即動く（骨子の .iss/<u>/.b1 は全 ARIADNE 共通）。
**問題固有部分（おとり data-kp-decoys／規範.krule・あてはめ.kfact＝Lv2／下書き本文／
想起カード化）は本スクリプトの対象外**＝各問の手執筆で後追いする。

冪等：マーカー KP-PUZZLE-BACKFILL があるファイルはスキップ。
使い方：
  python scripts/ariadne-puzzle-backfill.py                # 全 ARIADNE に適用
  python scripts/ariadne-puzzle-backfill.py <file> [...]   # 指定ファイルのみ
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs/ux/000_ARIADNE/001_刑法/刑JX001_ARIADNE.html"
ARIADNE_DIR = ROOT / "outputs/ux/000_ARIADNE"

MARKER = "KP-PUZZLE-BACKFILL"

# 骨子の上に出す静的マークアップ（ヒント＋JS無効時フォールバック注記）
KP_BAR = (
    '    <div class="kp-bar">\n'
    '      <span class="kp-hint">穴（論点・結論）を埋めて答案構成を完成させよう ─ 移動中の能動周回・自動採点。答えは「📖 答えを見る」で確認。</span>\n'
    '    </div>\n'
    '    <div class="kp-fallback">⚠ 穴埋めパズルは <b>ブラウザ（Safari/Chrome）か Lexia</b> で開くと起動します。いまは JavaScript が動かない表示（ファイルのプレビュー等）なので、下に<b>完成形の骨子</b>を表示しています。</div>\n'
)


def extract_blocks(src_html):
    """設計ソースから CSS（3領域連結）と JS（パズルIIFE）を抽出する。"""
    recall = re.search(r'\.self-check-quiz\.recall::before\{.*?\.recall \.quiz-btn\{[^\n]*\}', src_html, re.S)
    draft = re.search(r'/\* ===== 試験会場での下書き.*?(?=\n/\* ===== 骨子)', src_html, re.S)
    puzzle = re.search(r'/\* ===== 答案構成パズル（.*?(?=\n</style>)', src_html, re.S)
    js = re.search(r'/\* ===== 答案構成パズル v2.*?(?=\n</script>)', src_html, re.S)
    if not (recall and draft and puzzle and js):
        miss = [n for n, m in [('recall', recall), ('draft', draft), ('puzzle', puzzle), ('js', js)] if not m]
        raise SystemExit(f"[FATAL] 設計ソースから抽出失敗: {miss}（{SRC} を確認）")
    css = (f"\n/* ==== {MARKER} (css) ==== */\n"
           + recall.group(0).strip() + "\n"
           + draft.group(0).strip() + "\n"
           + puzzle.group(0).strip() + "\n")
    js_block = (f"\n/* ==== {MARKER} (js) ==== */\n" + js.group(0).strip() + "\n")
    return css, js_block


def apply_to(path, css, js_block):
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return "skip(適用済)"
    if not all(t in html for t in ('</style>', '</script>', 'class="skeleton"', 'class="bone"')):
        return "skip(構造不一致)"

    # ① CSS を </style> 直前へ
    html = html.replace('</style>', css + '</style>', 1)

    # ② ヒント＋フォールバックを b-goal バッジ直後へ
    html, n = re.subn(
        r'(<div class="skeleton">\s*<span class="badge b-goal">[^<]*</span>)',
        lambda m: m.group(1) + "\n" + KP_BAR.rstrip("\n"),
        html, count=1)
    if n == 0:
        return "skip(skeletonバッジ不一致)"

    # ③ パズル JS を </script> 直前へ
    html = html.replace('</script>', js_block + '</script>', 1)

    path.write_text(html, encoding="utf-8")
    return "applied"


def main():
    src_html = SRC.read_text(encoding="utf-8")
    css, js_block = extract_blocks(src_html)

    args = [pathlib.Path(a) for a in sys.argv[1:]]
    if args:
        targets = args
    else:
        targets = sorted(ARIADNE_DIR.glob("*/*_ARIADNE.html"))

    for p in targets:
        if p.resolve() == SRC.resolve():
            print(f"  {p.name}: skip(設計ソース)")
            continue
        try:
            print(f"  {p.name}: {apply_to(p, css, js_block)}")
        except Exception as e:
            print(f"  {p.name}: ERROR {e}")


if __name__ == "__main__":
    main()
