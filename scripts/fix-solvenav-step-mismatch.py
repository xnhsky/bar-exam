#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-solvenav-step-mismatch.py ── 解法ナビ STEP/ORDER の gold 混入を本問固有データへ復元。

背景（LEX388）: tx-lex-v11-to-v13.py の engine swap が gold（canonical/GENESIS-CARD.html＝
刑TX359）の <script> を逐語移植するため、移植先の解法ナビ問題固有データ（var STEP / var ORDER）
まで刑TX359 の放火問題の内容で上書きされていた。同型の混入が 59 ファイル
（刑TX066/074/089・刑TX386-445 帯、刑TX089 のみ刑TX356 由来）に存在する。

本ツールは scripts/lex/ 配下のスペック（build-ox-lex.py / lite_specs.py / specs_*.py）を
AST で安全に読み出し（import 実行なし）、各問の order と step/stmt（q・tip）から v13 エンジン
互換の STEP（label/q/tip/hint）を再構成して該当行だけを書き換える。決定論・冪等・CRLF 保持。

  python -X utf8 scripts/fix-solvenav-step-mismatch.py --check   # 検出のみ（終了コード1=混入あり）
  python -X utf8 scripts/fix-solvenav-step-mismatch.py --apply   # 復元を書き込み
"""
from __future__ import annotations

import ast
import glob
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEX_GLOB = str(ROOT / "outputs" / "ux" / "000_TX" / "*" / "*_lex.html")
SPEC_GLOB = str(ROOT / "scripts" / "lex" / "*.py")

# 正当な持ち主（gold 供給元）。この2ファイルの STEP は本問データそのもの。
LEGIT_OWNERS = {"刑TX359_lex.html", "刑TX356_lex.html"}

# スペックと現行 ox-grid の記述数・文言が一致しない問題（組合せ当否判定型の再生成で
# 記述自体が書き直されたもの）。自ファイルの ox-stmt 原文から STEP を導出する。
OWN_ROWS_FALLBACK = {"089"}

# ラベル体系を序数へ正規化（1始まり）。
_LABEL_SEQS = [
    [str(i) for i in range(1, 11)],
    list("①②③④⑤⑥⑦⑧⑨⑩"),
    list("アイウエオカキクケコ"),
    list("ABCDEFGHIJ"),
    list("ＡＢＣＤＥＦＧＨＩＪ"),
]


def label_ordinal(label: str) -> int | None:
    for seq in _LABEL_SEQS:
        if label in seq:
            return seq.index(label) + 1
    return None


def read(p) -> str:
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, t) -> None:
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def load_specs() -> dict[str, dict]:
    """scripts/lex/*.py から 3桁キーのスペック dict を AST 抽出（コード実行なし）。"""
    specs: dict[str, list] = {}
    for path in sorted(glob.glob(SPEC_GLOB)):
        try:
            tree = ast.parse(read(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for k, v in zip(node.keys, node.values):
                if (isinstance(k, ast.Constant) and isinstance(k.value, str)
                        and re.fullmatch(r"\d{3}", k.value) and isinstance(v, ast.Dict)):
                    try:
                        d = ast.literal_eval(v)
                    except Exception:
                        continue
                    if isinstance(d, dict) and "order" in d and ("step" in d or "stmt" in d):
                        specs.setdefault(k.value, []).append((path, d))
    out = {}
    for num, cands in specs.items():
        # 同一番号の重複定義はここでは解決せず、利用時に単一であることを要求する。
        out[num] = cands
    return out


def strip_tags(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", t)).strip()


def derive_hint(tip: str) -> str:
    """build-ox-lex.py の safeHint と同一規則で tip から誘導ヒントを生成する。"""
    m = re.search(r"<b>(.*?)</b>", tip or "", re.S | re.I)
    focus = strip_tags(m.group(1)) if m else ""
    if focus:
        return ("まず「" + focus + "」が、どの条文要件・判例基準なのかを確認し、"
                "問題文の具体的事実を一つ対応させる。結論は採点後に確認する。")
    return ("設問の中で条文要件・判例基準に対応する具体的事実を一つ選ぶ。"
            "どの限定・例外・時点で結論が分かれるかを先に決める。結論は採点後に確認する。")


def own_rows(html: str) -> list[str]:
    return re.findall(r'<div class="ox-row" data-stmt="([^"]+)"', html)


def own_row_texts(html: str) -> dict[str, str]:
    """ox-row の data-stmt → ox-stmt 原文（タグ除去済み）"""
    out = {}
    for m in re.finditer(
            r'<div class="ox-row" data-stmt="([^"]+)".*?class="ox-stmt"[^>]*>(.*?)</(?:span|div)>',
            html, re.S):
        out[m.group(1)] = strip_tags(m.group(2))
    return out


def build_step_from_rows(html: str, rows: list[str]):
    """スペックが現行記述と一致しない問題用：自ファイルの記述原文から STEP を導出。"""
    texts = own_row_texts(html)
    step = {}
    for lbl in rows:
        t = texts.get(lbl, "")
        if not t:
            raise ValueError("no ox-stmt text for row %r" % lbl)
        # 記述末尾の句点を落として設問形へ
        q = "『" + t.rstrip("。") + "』──正しい（○）か誤り（×）か？"
        step[lbl] = {"label": lbl, "q": q, "hint": derive_hint("")}
    return step, list(rows)


def step_block(html: str):
    """var STEP = {...}; の行内 JSON 部分を返す（行単位マッチ＝末尾コメント温存）。"""
    m = re.search(r"^([ \t]*var STEP\s*=\s*)(\{.*\})(;.*)$", html, re.M)
    return m


def order_block(html: str):
    m = re.search(r"^([ \t]*var ORDER\s*=\s*)(\[[^\]]*\])(;.*)$", html, re.M)
    return m


def build_step(spec: dict, rows: list[str]):
    """スペック order/step(stmt) をファイル実ラベル（rows）へ写像し STEP/ORDER を構成。"""
    order = list(spec["order"])
    src = spec.get("step") or spec.get("stmt")
    if len(order) != len(rows):
        raise ValueError("row count mismatch: spec=%d file=%d" % (len(order), len(rows)))
    if set(order) == set(rows):
        pairs = [(lbl, lbl) for lbl in order]
    else:
        # ラベル体系が違う場合は序数対応（① ↔ 1 ↔ ア）で写像する。
        row_by_ord = {}
        for r in rows:
            o = label_ordinal(r)
            if o is None:
                raise ValueError("unknown row label: %r" % r)
            row_by_ord[o] = r
        pairs = []
        for lbl in order:
            o = label_ordinal(lbl)
            if o is None or o not in row_by_ord:
                raise ValueError("cannot map spec label %r to rows %r" % (lbl, rows))
            pairs.append((lbl, row_by_ord[o]))
    step = {}
    new_order = []
    for spec_lbl, row_lbl in pairs:
        s = src[spec_lbl]
        if not s.get("q"):
            raise ValueError("spec %r lacks q" % spec_lbl)
        entry = {"label": row_lbl, "q": s["q"]}
        if s.get("tip"):
            entry["tip"] = s["tip"]
        entry["hint"] = s.get("hint") or derive_hint(s.get("tip", ""))
        step[row_lbl] = entry
        new_order.append(row_lbl)
    return step, new_order


def find_contaminated() -> list[tuple[Path, str]]:
    """複製 STEP（同一 JSON が複数ファイルに存在）を持つファイルを検出し、
    正当な持ち主（LEGIT_OWNERS）以外を返す。"""
    by_sig: dict[str, list[Path]] = {}
    for f in sorted(glob.glob(LEX_GLOB)):
        p = Path(f)
        m = step_block(read(p))
        if not m:
            continue
        by_sig.setdefault(m.group(2), []).append(p)
    bad = []
    for sig, files in by_sig.items():
        if len(files) < 2:
            continue
        owners = [p for p in files if p.name in LEGIT_OWNERS]
        if len(owners) != 1:
            raise SystemExit("[FATAL] duplicated STEP group without single legit owner: %s"
                             % [p.name for p in files])
        for p in files:
            if p.name not in LEGIT_OWNERS:
                bad.append((p, owners[0].name))
    return sorted(bad)


def main() -> int:
    apply = "--apply" in sys.argv
    check = "--check" in sys.argv or not apply
    bad = find_contaminated()
    if not bad:
        print("[OK] no duplicated solve-nav STEP found")
        return 0
    print("[FOUND] %d files carry another question's solve-nav STEP:" % len(bad))
    specs = load_specs()
    failures = 0
    for p, owner in bad:
        num = re.search(r"TX(\d{3})", p.name).group(1)
        subj = p.name.split("TX")[0]
        html = read(p)
        rows = own_rows(html)
        try:
            # scripts/lex/ のスペックは刑法（build-ox-lex 系）由来で 3 桁番号キー＝科目を持たない。
            # 刑訴TX075 のような他科目ファイルに同番号の刑法スペックを写像すると別科目の
            # 中身が混入するため、刑法以外は常に自ファイルの ox-stmt から導出する（2026-07-21）。
            if num in OWN_ROWS_FALLBACK or subj != "刑":
                spec_path = "(own ox-stmt)"
                step, new_order = build_step_from_rows(html, rows)
            else:
                cands = specs.get(num, [])
                if len(cands) != 1:
                    raise ValueError("spec candidates=%d" % len(cands))
                spec_path, spec = cands[0]
                step, new_order = build_step(spec, rows)
        except ValueError as e:
            print("  [FAIL] %s (from %s): %s" % (p.name, owner, e))
            failures += 1
            continue
        if not apply:
            print("  [BAD ] %s (STEP from %s; fix source: %s)"
                  % (p.name, owner, Path(spec_path).name))
            continue
        sm, om = step_block(html), order_block(html)
        if not sm or not om:
            print("  [FAIL] %s: STEP/ORDER line not found" % p.name)
            failures += 1
            continue
        html = html[:sm.start(2)] + json.dumps(step, ensure_ascii=False) + html[sm.end(2):]
        om = order_block(html)
        html = html[:om.start(2)] + json.dumps(new_order, ensure_ascii=False) + html[om.end(2):]
        write(p, html)
        print("  [FIX ] %s (own STEP restored from %s)" % (p.name, Path(spec_path).name))
    if apply and not failures:
        rest = find_contaminated()
        if rest:
            print("[FATAL] contamination remains after apply: %d" % len(rest))
            return 1
        print("[OK] all files restored; no duplicated STEP remains")
    if check and not apply:
        return 1 if bad else 0
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
