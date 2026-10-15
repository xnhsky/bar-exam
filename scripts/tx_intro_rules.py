#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tx_intro_rules.py ── §v16 INTRO（解く前の🔰導入）の組版と判定式（単一情報源）。

scripts/tx-intro.py（組み込み・検査ツール）と scripts/validate-tx-core.py G84 が同じ式を使う
（「直したのに ERROR」「ERROR は出ないのに壊れている」を構造的に起こさない）。

導入＝初見で見当がつかないときだけ開く、問題単位の案内（既定は閉じた details）。
  置き場所＝#part-a の直下。不可侵原文ブロック（.tx-original-block）があればその直後、
           無ければ体系マップ／最初の記述カードの直前（＝原文の下・記述カードの上）。
  中身＝何の話？（土俵）／使う道具（記述を読むための用語・制度の定義・0〜4 件）／読む順番（記述が分かれる軸）。
  書かないもの＝記述ごとの結論・正誤・組合せ番号・答案圧縮と同じ文・解答技術。
  物語解説（.fa-narrative）には手を付けない＝Lexia が復習カードに使う一連の読み物なので、
  導入へ段落を移すと復習カード側で前提が抜ける（gold 刑訴TX142 で一度移して戻した）。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from tx_v15_rules import read, write, strip_tags, block_end  # noqa: F401  （IO・タグ除去・div の入れ子）

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "canonical" / "GENESIS-CARD.html"

CSS_BEGIN = "/* TX-INTRO:BEGIN"
CSS_END = "/* TX-INTRO:END */"
STYLE_OPEN = '<style id="tx-intro-style">'

TAG = "🔰 導入"
CUE = "30秒考えて見当がつかないときだけ開く ── 答え・正誤は書いていません"
NOTE = "開いた回は、全部当たっても評価は3まで（知識を借りて解いたため・導き書§3-7）。"
LAB_WHAT, LAB_TOOLS, LAB_ORDER = "何の話？", "使う道具", "読む順番"

ALLOWED_TAGS = {"b", "strong", "em"}
MAX_TOOLS = 4
BODY_MIN, BODY_MAX = 120, 700      # 何の話＋道具＋読む順番の本文字数（空白・タグ・ラベル除く）
ANSCOMP_SHARE = 20                 # 答案圧縮と共有する連続文字数がこれ以上なら「同じ文」の助言

# 導入の本文に置いてはならない語（解く前に見える面＝答えの先出し・解答技術を締め出す）
FORBIDDEN = [
    (r"[○×〇✕◯]", "○×記号（掛け算は「と」で書く）"),
    (r"正解", "「正解」"),
    (r"正しい", "「正しい」（正誤の断定）"),
    (r"誤り|誤って?いる", "「誤り」（正誤の断定）"),
    (r"肢\s*[0-9０-９]", "肢N"),
    (r"記述\s*[0-9０-９ア-コ]", "記述N の参照"),
    (r"組合せ\s*[0-9０-９]|後記\s*[0-9０-９]", "選択肢番号"),
    (r"素直に|疑いすぎ|思い込みの罠|先入観|[ひ引]っかけ|言い切り", "解答技術語"),
]

# 解法ナビ（STEP の hint）が結論を言っている型（導入を持つファイルだけ ERROR で見る）
HINT_VERDICT = re.compile(r"(?:正しい|誤り)[。）」]|(?:正しい|誤り)$|[＝=]\s*[○×]|正解")


# ---------------------------------------------------------------- 組版
def render(spec: dict) -> str:
    """仕様 → 導入 HTML（LF 改行）。"""
    lines = [
        '<details class="tx-intro" id="tx-intro">',
        f'<summary><span class="tx-intro-tag">{TAG}</span><span class="tx-intro-cue">{CUE}</span></summary>',
        '<div class="tx-intro-body">',
        f'<p class="tx-intro-line"><span class="tx-intro-lab">{LAB_WHAT}</span>{spec["what"]}</p>',
    ]
    tools = spec.get("tools") or []
    if tools:
        lines += [f'<div class="tx-intro-line"><span class="tx-intro-lab">{LAB_TOOLS}</span>',
                  '<ul class="tx-intro-tools">']
        for t in tools:
            ref = f'（{t["ref"]}）' if (t.get("ref") or "").strip() else ""
            lines.append(f'<li><b>{t["term"]}</b>{ref}── {t["def"]}</li>')
        lines += ["</ul>", "</div>"]
    lines += [
        f'<p class="tx-intro-line"><span class="tx-intro-lab">{LAB_ORDER}</span>{spec["order"]}</p>',
        f'<p class="tx-intro-note">{NOTE}</p>',
        "</div>",
        "</details>",
    ]
    return "\n".join(lines)


def intro_span(s: str) -> tuple[int, int] | None:
    i = s.find('<details class="tx-intro"')
    if i < 0:
        return None
    j = s.find("</details>", i)
    return None if j < 0 else (i, j + len("</details>"))


def parse(intro_html: str) -> dict | None:
    """導入 HTML → 仕様（render の逆）。構造が崩れていれば None。"""
    m_what = re.search(r'<p class="tx-intro-line"><span class="tx-intro-lab">' + re.escape(LAB_WHAT)
                       + r'</span>(.*?)</p>', intro_html, re.S)
    m_order = re.search(r'<p class="tx-intro-line"><span class="tx-intro-lab">' + re.escape(LAB_ORDER)
                        + r'</span>(.*?)</p>', intro_html, re.S)
    if not (m_what and m_order):
        return None
    tools = []
    for m in re.finditer(r"<li><b>(.*?)</b>(?:（(.*?)）)?── (.*?)</li>", intro_html, re.S):
        tools.append({"term": m.group(1), "ref": m.group(2) or "", "def": m.group(3)})
    return {"what": m_what.group(1), "tools": tools, "order": m_order.group(1)}


def part_a_span(s: str) -> tuple[int, int] | None:
    m = re.search(r'<section class="section" id="part-a">', s)
    if not m:
        return None
    depth = 0
    for t in re.finditer(r"<section\b|</section>", s[m.start():]):
        depth += 1 if t.group(0) == "<section" else -1
        if depth == 0:
            return m.start(), m.start() + t.end()
    return None


def anchor(s: str) -> tuple[int, str] | None:
    """導入を差し込む位置と、差し込み方（'after'＝原文ブロック直後／'before'＝その行の頭）。"""
    pa = part_a_span(s)
    if pa is None:
        return None
    ob = s.find('<div class="tx-original-block"', pa[0], pa[1])
    if ob >= 0:
        return block_end(s, ob), "after"
    cands = [i for i in (s.find('<div class="tx-sysmap"', pa[0], pa[1]),
                         s.find('<article class="tx-inline-card"', pa[0], pa[1])) if i >= 0]
    if not cands:
        return None
    i = min(cands)
    ls = s.rfind("\n", 0, i) + 1
    # ヘッダー〜#part-a〜体系マップが改行なしの 1 物理行に詰まった旧世代（刑訴TX252）では、行頭が
    # #part-a の外になる。そのときは要素の直前に差し込む（#part-a の中に必ず入る）。
    pa_open = s.find(">", pa[0]) + 1
    return (ls if ls >= pa_open else i), "before"


def remove_intro(s: str) -> str:
    sp = intro_span(s)
    if sp is None:
        return s
    i, j = sp
    if s[i - 2:i] == "\n\n":          # 原文ブロック直後型（"\n\n<details…</details>"）
        return s[:i - 2] + s[j:]
    if s[j:j + 2] == "\n\n":          # 行頭差し込み型（"<details…</details>\n\n"）
        return s[:i] + s[j + 2:]
    return s[:i] + s[j:]


def place_intro(s: str, html: str) -> str:
    s = remove_intro(s)
    a = anchor(s)
    if a is None:
        raise ValueError("差し込み位置（#part-a・原文ブロック・体系マップ・記述カード）が見つからない")
    pos, how = a
    if how == "after":
        return s[:pos] + "\n\n" + html + s[pos:]
    return s[:pos] + html + "\n\n" + s[pos:]


# ---------------------------------------------------------------- CSS（独立 <style> 区画）
def css_region(text: str) -> tuple[int, int] | None:
    i = text.find(CSS_BEGIN)
    if i < 0:
        return None
    j = text.find(CSS_END, i)
    return None if j < 0 else (i, j + len(CSS_END))


def canonical_css() -> str:
    s = CANONICAL.read_bytes().decode("utf-8").replace("\r\n", "\n")
    r = css_region(s)
    if r is None:
        raise SystemExit(f"正典 {CANONICAL} に TX-INTRO 区画が無い")
    return s[r[0]:r[1]]


def sync_css(s: str, css: str) -> str:
    """TX-INTRO 区画を正典へそろえ、</head> 直前の独立 <style id="tx-intro-style"> に置く（冪等）。
    他ストリーム（S/D/G）が同期する第1 <style> の区画と行が隣接しないよう、独立ブロックにしている。"""
    block = f"{STYLE_OPEN}\n{css}\n</style>\n"
    cur = re.search(re.escape(STYLE_OPEN) + r"\n.*?\n</style>\n", s, re.S)
    if cur and cur.group(0) == block and s.count(CSS_BEGIN) == 1:
        return s
    if cur:
        s = s[:cur.start()] + s[cur.end():]
    r = css_region(s)
    while r is not None:                       # 旧配置（第1 <style> 内など）の区画を取り除く
        end = r[1] + (1 if s[r[1]:r[1] + 1] == "\n" else 0)
        s = s[:r[0]] + s[end:]
        r = css_region(s)
    k = s.find("</head>")
    if k < 0:
        raise ValueError("</head> が見つからない")
    return s[:k] + block + s[k:]


# ---------------------------------------------------------------- 解法ナビ（STEP の hint）
STEP_RE = re.compile(r"(var STEP\s*=\s*)(\{.*?\})(;)")


def step_data(s: str) -> tuple[dict, tuple[int, int]] | None:
    m = STEP_RE.search(s)
    if not m:
        return None
    try:
        return json.loads(m.group(2)), (m.start(2), m.end(2))
    except Exception:
        return None


def set_hints(s: str, hints: dict) -> str:
    sd = step_data(s)
    if sd is None:
        raise ValueError("解法ナビの STEP データが読めない")
    data, (a, b) = sd
    for k, v in hints.items():
        if k not in data:
            raise ValueError(f"解法ナビに記述 {k} の STEP が無い")
        data[k]["hint"] = v
    return s[:a] + json.dumps(data, ensure_ascii=False) + s[b:]


def blank_hints(s: str) -> str:
    sd = step_data(s)
    if sd is None:
        return s
    data, (a, b) = sd
    for v in data.values():
        if isinstance(v, dict) and "hint" in v:
            v["hint"] = ""
    return s[:a] + json.dumps(data, ensure_ascii=False) + s[b:]


# ---------------------------------------------------------------- 文の検査
def text_problems(t: str, where: str) -> list[str]:
    errs = []
    if "\n" in t:
        errs.append(f"{where}: 改行を含む")
    for tag in re.findall(r"</?\s*([a-zA-Z0-9]+)", t):
        if tag.lower() not in ALLOWED_TAGS:
            errs.append(f"{where}: 許可外のタグ <{tag}>（b・strong・em のみ）")
            break
    plain = strip_tags(t)
    for pat, label in FORBIDDEN:
        m = re.search(pat, plain)
        if m:
            errs.append(f"{where}: {label}（'{m.group(0)}'）")
    return errs


def spec_problems(spec: dict, step_keys: list[str] | None = None) -> list[str]:
    errs = []
    for key in ("what", "order"):
        v = spec.get(key)
        if not isinstance(v, str) or not v.strip():
            errs.append(f"{key} が空")
        else:
            errs.extend(text_problems(v, key))
    tools = spec.get("tools") or []
    if not isinstance(tools, list):
        errs.append("tools は配列")
        tools = []
    if len(tools) > MAX_TOOLS:
        errs.append(f"tools が {len(tools)} 件（上限 {MAX_TOOLS}）")
    for i, t in enumerate(tools, 1):
        if not isinstance(t, dict) or not (t.get("term") or "").strip() or not (t.get("def") or "").strip():
            errs.append(f"tools[{i}]: term と def が要る")
            continue
        for k in ("term", "ref", "def"):
            errs.extend(text_problems(t.get(k) or "", f"tools[{i}].{k}"))
        if "（" in (t.get("ref") or "") or "）" in (t.get("ref") or ""):
            errs.append(f"tools[{i}].ref: 全角括弧を入れない（括弧はツールが付ける）")
        if "── " in t["def"] or "──" in t["term"]:
            errs.append(f"tools[{i}]: 区切り「──」を本文に入れない")
    hints = spec.get("hints") or {}
    for k, v in hints.items():
        if step_keys is not None and k not in step_keys:
            errs.append(f"hints: 記述 {k} は解法ナビの STEP に無い")
        if not isinstance(v, str) or not v.strip():
            errs.append(f"hints[{k}] が空")
        elif HINT_VERDICT.search(v):
            errs.append(f"hints[{k}]: 結論を言っている（'{HINT_VERDICT.search(v).group(0)}'）")
    return errs


def body_chars(spec: dict) -> int:
    parts = [spec.get("what", ""), spec.get("order", "")]
    for t in spec.get("tools") or []:
        parts += [t.get("term", ""), t.get("ref", ""), t.get("def", "")]
    return len(re.sub(r"\s+", "", strip_tags("".join(parts))))


def check_text(s: str, name: str = "", require: bool = False) -> list[str]:
    """導入を持つファイルの契約検査。戻り値は "ERROR …" / "WARN …" の配列（空＝OK）。
    導入が無いファイルは require=False なら検査対象外（[]）。"""
    out: list[str] = []
    n = s.count('<details class="tx-intro"')
    if n == 0:
        return ["ERROR 🔰導入（details.tx-intro）が無い"] if require else []
    if n > 1:
        out.append(f"ERROR 🔰導入が {n} 個ある（1 問 1 個）")
    sp = intro_span(s)
    if sp is None:
        return out + ["ERROR 🔰導入の </details> が無い"]
    intro = s[sp[0]:sp[1]]
    head = intro[:intro.find(">") + 1]
    if re.search(r"\bopen\b", head):
        out.append("ERROR 🔰導入が既定で開いている（open を付けない）")
    pa = part_a_span(s)
    if pa is None or not (pa[0] < sp[0] < pa[1]):
        out.append("ERROR 🔰導入が #part-a の外にある")
    else:
        ob = s.find('<div class="tx-original-block"', pa[0], pa[1])
        if ob >= 0:
            obe = block_end(s, ob)
            if ob < sp[0] < obe:
                out.append("ERROR 🔰導入が原文ブロックの中にある（原文は不可侵＝§v13r）")
            elif sp[0] < ob:
                out.append("ERROR 🔰導入が原文ブロックより上にある（原文の直後に置く）")
        fc = s.find('<article class="tx-inline-card"', pa[0], pa[1])
        if fc >= 0 and sp[0] > fc:
            out.append("ERROR 🔰導入が記述カードより下にある（記述カードの上に置く）")
    spec = parse(intro)
    if spec is None or render(spec) != intro.replace("\r\n", "\n"):
        out.append("ERROR 🔰導入の構造が正典の組版と違う（手書き・追記・壊れたタグ。tx-intro.py apply で組む）")
    else:
        out += ["ERROR " + e for e in spec_problems(spec)]
        bc = body_chars(spec)
        if not (BODY_MIN <= bc <= BODY_MAX):
            out.append(f"WARN 🔰導入の本文が {bc} 字（目安 {BODY_MIN}〜{BODY_MAX} 字＝30秒〜1分で読める量）")
        plain = re.sub(r"\s+", "", strip_tags(spec["what"] + spec["order"]
                                             + "".join(t["def"] for t in spec["tools"])))
        for m in re.finditer(r'<span class="tx-anscomp-line">(.*?)</span>', s, re.S):
            a = re.sub(r"\s+", "", strip_tags(m.group(1)))
            hit = next((a[i:i + ANSCOMP_SHARE] for i in range(0, max(0, len(a) - ANSCOMP_SHARE) + 1)
                        if a[i:i + ANSCOMP_SHARE] in plain), None)
            if hit:
                out.append(f"WARN 🔰導入に答案圧縮と同じ文がある（'{hit}'…＝答えになる命題を書かない）")
                break
    if css_region(s) is None:
        out.append("ERROR TX-INTRO の CSS 区画が無い（tx-intro.py css）")
    sd = step_data(s)
    if sd is not None:
        for k, v in sd[0].items():
            h = (v or {}).get("hint", "") if isinstance(v, dict) else ""
            m = HINT_VERDICT.search(h or "")
            if m:
                out.append(f"ERROR 解法ナビの記述{k}のヒントが結論を言っている（'{m.group(0)}'・解く前に見える面）")
    return out
