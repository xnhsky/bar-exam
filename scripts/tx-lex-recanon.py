#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX360 inline _lex 正典化（接ぎ木修復・内容保持）。

codex 等が「既存 _lex を v12 インラインへ手で更新」した結果生じる接ぎ木
（旧 Annex C JS 流用＋後付けパッチ `tx-inline-v1211-upgrade-js`＋不足 CSS）を、
本文（問題固有内容）を温存したまま土台だけ canonical/GENESIS-CORE.html へ載せ替える。
RX の rx-recanon.py / rx-restyle.py と同じ「内容不変・構造正典化」の一族。

やること（決定論的・冪等）:
  1. <style> を canonical のものへ差し替え。ただし AI 選定パレット（2つ目の :root{}）は元のまま。
     → 不足していた toast / result / inline 系 CSS が canonical 品質で揃う。
  2. <script> を「canonical 単一エンジン ＋ 元の解法ナビ(solve-nav)」の最大 2 本へ再構成。
     → 旧 Annex C JS と band-aid を物理削除し、inline カードを正典エンジンが自前配線する。
  3. v12 inline 表示面を正規化する。
     - `.tx-inline-explain` に初期 hidden を付与（canonical 契約・G40）。
     - `.tx-inline-card` と重複する旧 `.problem-text` 記述一覧は物理削除する。
     - 物語解説の段落にラベルが無い場合は、最低限の「ラベル＋題名」を補う。
  本文（HEADER / PART A / ox-grid / inline カード本文 / PART B / 参考条文判例 / SVG /
  物語解説本文 / 解法ナビの問題固有データ）は保つ。

対象は `.tx-inline-card` を持つ v12 inline _lex のうち G41 接ぎ木を含むファイルのみ。
既に正典（360-365 等）や旧デザイン _lex はスキップ（冪等）。

  python scripts/tx-lex-recanon.py outputs/ux/000_TX/001_刑法/刑TX366_lex.html   # dry-run（既定）
  python scripts/tx-lex-recanon.py outputs/ux/000_TX --apply                      # 配下を一括修復
  python scripts/tx-lex-recanon.py outputs/ux --apply

検証は呼び出し側で `validate-tx-core.py` ＋ `check-tx-lex-engine.py` を必ず通すこと。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "canonical" / "GENESIS-CORE.html"
SOLVE_NAV_CANON = ROOT / "canonical" / "SOLVE-NAV.html"

BAND_AID = "tx-inline-v1211-upgrade-js"
ENGINE_SIG = "hydrateInlinePartBDetails"  # canonical 単一エンジンの固有関数

LEGACY_INLINE_STATEMENTS_RE = re.compile(
    r'\n<h3\b[^>]*>【記述】.*?</h3>\s*'
    r'(?:<div class="problem-text"><span class="choice-num-inline">(?:\d+|[アイウエオア-ン])</span>'
    r'.*?</div>\s*)+'
    r'(?=<div class="solve-nav"|<div class="tx-inline-list"|<div class="tx-inline-judge-list")',
    re.S,
)


def solve_nav_css() -> str:
    """canonical/SOLVE-NAV.html の <style id="solve-nav-style"> 内 CSS を返す。

    解法ナビの CSS は GENESIS-CORE 本体には無く、各 _lex の <style> 末尾に追記されて
    いる（生成時に SOLVE-NAV.html から注入）。restyle は <style> を GENESIS-CORE で
    丸ごと載せ替えるため、この CSS をここで SOLVE-NAV 正典から再注入しないと
    解法ナビが無装飾化する（過去 restyle で 366-385 の .solve-nav CSS が剥落した実害）。
    SOLVE-NAV.html を単一情報源にすることで solve-nav 意匠も canonical 一元管理になる。"""
    try:
        t = SOLVE_NAV_CANON.read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(r'<style id="solve-nav-style">(.*?)</style>', t, re.S)
    return m.group(1).strip() if m else ""


def split_style(text: str):
    """(pre[..<style>], style_inner, after[</style>..]) を返す。"""
    s_open = text.index("<style>") + len("<style>")
    s_close = text.index("</style>")
    return text[:s_open], text[s_open:s_close], text[s_close:]


def _find_root(style_inner: str, var_re: str):
    """style 内で `var_re`（例 r"--accent\\s*:"）を含む最初の :root ブロックの Match を返す。
    無ければ None。基底 :root（fonts のみ）や canonical のコメント内リテラル
    `:root{}` には誤マッチしない（内容で同定）。"""
    for m in re.finditer(r":root\s*\{[^}]*\}", style_inner, re.S):
        if re.search(var_re, m.group(0)):
            return m
    return None


# per-file で AI 選定される「本物のパレット」:root は 2 ブロックある：
#   block#2  --accent:        … メインパレット（5 役割 + freq/recall）
#   block#3  --accent-light:  … 派生パレット identity（--accent-darker/--mid-* 等）
# block#1（fonts/scale）と block#4（--ed-* editorial）は canonical 固定で per-file ではない。
# 旧実装は block#2 しか保存せず、restyle 時に block#3 が canonical（既定 Twilight Violet）で
# 上書きされ、--accent と --accent-darker の hue が割れる事故（header/SVG グラデ破綻）を招いた。
PALETTE_ROOT_SIGNATURES = (r"--accent\s*:", r"--accent-light\s*:")


def palette_match(style_inner: str):
    """互換: メインパレット（--accent: を持つ）:root の Match を返す（必須・無ければ ValueError）。"""
    m = _find_root(style_inner, r"--accent\s*:")
    if m is None:
        raise ValueError("パレット :root（--accent を含む）が見つからない")
    return m


def extract_scripts(text: str):
    return [m.group(0) for m in re.finditer(r"<script\b.*?</script>", text, re.S)]


def drop_legacy_inline_statement_list(body: str) -> str:
    """v12 inline カードと重複する旧い問題文一覧をHTMLから落とす。

    CSS/JSで隠すだけだと端末や配信キャッシュの条件で旧一覧が見えることがあるため、
    `tx-inline-card` がある画面では「問題文＋○×」カードを唯一の表示面にする。
    裏の `.answer-ox-grid` は記録源なので残す。
    """
    if "tx-inline-card" not in body:
        return body
    if "tx-inline-list" not in body and "tx-inline-judge-list" not in body:
        return body
    return LEGACY_INLINE_STATEMENTS_RE.sub("\n", body, count=1)


def generic_narrative_label(index: int, total: int, content: str = "") -> str:
    plain = re.sub(r"<.*?>", "", content)
    if index == 1:
        if "放火" in plain:
            return "導入：燃やした客体と入口"
        return "導入：問題の見取り図"
    if index == total:
        if "読み方" in plain or "番号" in plain:
            return "まとめ：判断順を固定する"
        return "まとめ：持ち帰る判断順"
    if "延焼罪" in plain:
        return "論点1：延焼罪の起点"
    if "108条の「人」" in plain or "共犯者" in plain or "共謀" in plain:
        return "論点3：108条の「人」"
    if "38条2項" in plain or "空き家" in plain or "非現住" in plain:
        return "論点2：現住と非現住の錯誤"
    if "外出" in plain or "現住性" in plain or "現在性" in plain:
        return "論点4：現住性と現在性"
    if "殺人罪" in plain or "吸収" in plain or "観念的競合" in plain:
        return "論点5：放火と殺人の罪数"
    return f"論点{index - 1}：記述{index - 1}の判断軸"


def add_default_narrative_labels(body: str) -> str:
    """ラベル未指定の物語解説段落へ、最低限の「ラベル＋題名」を補う。"""
    def label_block(match: re.Match) -> str:
        block = match.group(0)
        paras = list(re.finditer(r'<p(?![^>]*class="fa-narrative-title")(?![^>]*data-fa-label=)([^>]*)>(.*?)</p>', block, re.S))
        total = len(paras)
        if total == 0:
            return block
        out = []
        last = 0
        for i, pm in enumerate(paras, start=1):
            out.append(block[last:pm.start()])
            out.append(f'<p data-fa-label="{generic_narrative_label(i, total, pm.group(2))}"{pm.group(1)}>{pm.group(2)}</p>')
            last = pm.end()
        out.append(block[last:])
        return "".join(out)

    return re.sub(r'<div class="fa-narrative">.*?</div>', label_block, body, flags=re.S)


def find_div_block(html: str, start: int) -> tuple[int, int]:
    """`start` 位置の <div> から対応する閉じ </div> 直後までを返す。"""
    depth = 0
    for m in re.finditer(r'<(/?)div\b', html[start:], re.I):
        if m.group(1) == "":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                gt = html.find(">", start + m.end())
                if gt < 0:
                    break
                return start, gt + 1
    raise ValueError("対応する </div> が見つからない")


def move_solve_nav_below_inline_cards(body: str) -> str:
    """解法ナビを問題文カード一覧の直後へ置く。

    旧生成物には「問題文 paragraph → solve-nav → inline cards」という順序が残るものがある。
    v12 inline では、まず問題文カードを読み、その下でナビを使う。
    """
    nav_m = re.search(r'<div class="solve-nav"\s+id="solve-nav">', body)
    list_m = re.search(r'<div class="tx-inline-(?:judge-)?list">', body)
    if not nav_m or not list_m:
        return body
    if nav_m.start() > list_m.start():
        return body

    nav_start, nav_end = find_div_block(body, nav_m.start())
    nav = body[nav_start:nav_end].strip()
    body = body[:nav_start] + body[nav_end:]

    list_m = re.search(r'<div class="tx-inline-(?:judge-)?list">', body)
    if not list_m:
        return body
    _, list_end = find_div_block(body, list_m.start())
    return body[:list_end].rstrip() + "\n" + nav + "\n" + body[list_end:].lstrip()


def _strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value or "")
    return re.sub(r"\s+", " ", value).strip()


def auto_solve_hint(step: dict) -> str:
    """採点前に結論を漏らさず、見るべき軸を具体化したヒントを作る。"""
    tip = str(step.get("tip") or "")
    q = str(step.get("q") or "")
    focus = ""
    m = re.search(r"<b>(.*?)</b>", tip, re.S | re.I)
    if m:
        focus = _strip_tags(m.group(1))
    if not focus:
        for kw in (
            "公共の危険", "建造物の一部", "毀損", "焼損", "一体性",
            "現住", "現在", "犯人以外", "延焼罪", "未遂", "失火",
            "艦船", "媒介物", "独立燃焼", "建造物",
        ):
            if kw in tip or kw in q:
                focus = kw
                break
    if focus:
        return f"まず「{focus}」が、どの条文要件・判例基準なのかを確認し、問題文の具体的事実を一つ対応させる。結論は採点後に確認する。"
    return "設問の中で条文要件・判例基準に対応する具体的事実を一つ選ぶ。どの限定・例外・時点で結論が分かれるかを先に決める。結論は採点後に確認する。"


def _json_block_after(text: str, start: int) -> tuple[int, int] | None:
    i = start
    while i < len(text) and text[i].isspace():
        i += 1
    if i >= len(text) or text[i] != "{":
        return None
    depth = 0
    in_str = False
    esc = False
    quote = ""
    for j in range(i, len(text)):
        ch = text[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                in_str = False
            continue
        if ch in ("'", '"'):
            in_str = True
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i, j + 1
    return None


def ensure_solve_nav_hints(script: str) -> str:
    """solve-nav の STEP/STMT に採点前ヒントを補う。既存 hint は尊重する。"""
    out = script
    for var_name in ("STEP", "STMT"):
        m = re.search(rf"var\s+{var_name}\s*=\s*", out)
        if not m:
            continue
        span = _json_block_after(out, m.end())
        if not span:
            continue
        start, end = span
        try:
            data = json.loads(out[start:end])
        except json.JSONDecodeError:
            continue
        changed = False
        for value in data.values():
            if isinstance(value, dict) and not value.get("hint"):
                value["hint"] = auto_solve_hint(value)
                changed = True
        if changed:
            out = out[:start] + json.dumps(data, ensure_ascii=False) + out[end:]
    return out


def is_target(text: str) -> bool:
    """v12 inline かつ接ぎ木（band-aid or 旧エンジン）を含むファイルだけ対象。"""
    if 'class="tx-inline-card' not in text and "class='tx-inline-card" not in text:
        return False
    grafted = (BAND_AID in text) or (ENGINE_SIG not in text) or (len(extract_scripts(text)) > 2)
    return grafted


def recanon(text: str, canon: str) -> str:
    pre, style_src, _ = split_style(text)
    _, style_canon, _ = split_style(canon)

    # 1) style を canonical へ。per-file パレット :root（block#2 --accent: と
    #    block#3 --accent-light:）だけ元のものを保存する。canonical の各パレット
    #    ブロックを、元ファイルの対応ブロックで丸ごと差し替える（コメント内リテラル
    #    :root{} や fonts/--ed-* ブロックは対象外＝誤上書きしない）。block#2 は必須、
    #    block#3 は無ければ canonical のまま（旧式 _lex への graceful degrade）。
    style_new = style_canon
    palette_match(style_src)  # block#2 必須チェック（無ければ ValueError）
    for sig in PALETTE_ROOT_SIGNATURES:
        src_m = _find_root(style_src, sig)
        can_m = _find_root(style_new, sig)
        if src_m and can_m:
            style_new = style_new.replace(can_m.group(0), src_m.group(0), 1)

    # 1-bis) 解法ナビ CSS を SOLVE-NAV 正典から注入（GENESIS-CORE 本体に無いため）。
    #    解法ナビを持つ _lex のみ。冪等（既に注入済みなら重複させない）。
    if 'class="solve-nav"' in text or "class='solve-nav" in text:
        sn_css = solve_nav_css()
        if sn_css and ".solve-nav{" not in style_new:
            style_new = (
                style_new.rstrip()
                + "\n\n/* === 解法ナビ CSS（canonical/SOLVE-NAV.html 正典より注入） === */\n"
                + sn_css
                + "\n"
            )

    # 本文 = </style> 〜 最初の <script> 直前
    s_close = text.index("</style>")
    first_script = text.index("<script", s_close)
    body = text[s_close:first_script]
    tail = text[text.rindex("</script>") + len("</script>"):]

    # 2) scripts 再構成: canonical エンジン ＋ 元の解法ナビ
    engine = extract_scripts(canon)[0]
    src_scripts = extract_scripts(text)
    solvenav = [s for s in src_scripts if "solve-nav" in s and ENGINE_SIG not in s]

    # 3) 本文契約: v12 inline 表示面を正規化（冪等）
    body = drop_legacy_inline_statement_list(body)
    body = add_default_narrative_labels(body)
    body = move_solve_nav_below_inline_cards(body)
    body = re.sub(r'<div class="tx-inline-explain">',
                  '<div class="tx-inline-explain" hidden>', body)

    new = pre + style_new + body + engine
    for sn in solvenav:
        new += "\n" + ensure_solve_nav_hints(sn)
    return new + tail


def collect(paths):
    files = []
    for p in paths:
        ap = Path(p)
        ap = ap if ap.is_absolute() else ROOT / ap
        if ap.is_file() and ap.suffix == ".html":
            files.append(ap)
        elif ap.is_dir():
            files.extend(sorted(ap.rglob("*_lex.html")))
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="_lex.html ファイル or ディレクトリ")
    ap.add_argument("--apply", action="store_true", help="実際に上書きする（既定 dry-run）")
    args = ap.parse_args()

    canon = CANON.read_text(encoding="utf-8")
    files = collect(args.paths)
    targeted = skipped = fixed = errors = 0

    for f in files:
        text = f.read_text(encoding="utf-8")
        if not is_target(text):
            skipped += 1
            continue
        targeted += 1
        try:
            new = recanon(text, canon)
        except Exception as e:
            errors += 1
            print(f"  ❌ {f.name}: {e}")
            continue
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        if args.apply:
            f.write_text(new, encoding="utf-8")
            fixed += 1
            print(f"  ✏️  修復: {rel}  ({len(text):,} → {len(new):,} bytes)")
        else:
            print(f"  • 対象: {rel}  ({len(text):,} → {len(new):,} bytes 予定)")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] 接ぎ木対象={targeted} / 修復={fixed} / 非対象スキップ={skipped} / エラー={errors}")
    if not args.apply and targeted:
        print("→ 上書きするには --apply。修復後は validate-tx-core.py と check-tx-lex-engine.py を通すこと。")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
