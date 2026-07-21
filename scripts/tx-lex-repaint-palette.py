#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TX（公式＋_lex）の難易度帯パレット一括再選定（決定論・冪等・本文不変）。2026-07-21・LEX-403。

対象（いずれか）:
  A. パレット未選定＝palette :root（--accent ブロック）が歴代正典の既定ブロックの
     バイトコピーのままで、§5 選定宣言（非 baseline）が無い（G71 の ERROR 条件と同一）
  B. 宣言未適用＝§5 で選定を宣言しているのに実効 --accent が正典既定 hex のまま
     （実害＝刑TX359/286 型・G72 の ERROR 条件と同一）
  C. 帯外カスタム＝FORCED_CODES（監査 2026-07-21 で確定した green-on-P1 の 5 問）

処理（<style> 内の palette ブロックと §5 コメントだけを差し替え・本文/DOM/JS 不変）:
  1. パレット決定（問題コード単位＝公式と _lex は必ず同色）
     - 兄弟いずれかに §5 宣言があればその宣言パレット（B 型は宣言を尊重）
     - なければ正答率帯 → REPAINT_ROTATION[band][問題番号 % N]（決定論）
  2. §5 コメントを「帯別再選定」宣言へ差し替え（G72 が読む）
  3. block#2（--accent :root）／block#3（--accent-light :root）を corpus 実証済み
     逐語テンプレ（scripts/tx-palette-templates.json）へ差し替え
  4. 移行ツールの末尾上書き :root（AI選定パレット保全）があれば、テンプレ変数だけ同色へ更新
  5. CRLF ファイルは CRLF を保存

使い方:
  python scripts/tx-lex-repaint-palette.py                 # dry-run（全 TX を走査し計画表示）
  python scripts/tx-lex-repaint-palette.py --apply         # 反映
  python scripts/tx-lex-repaint-palette.py <file...> --apply
検証: validate-tx-core G71/G72 が 0 になること（単一情報源 scripts/tx_palette_rules.py）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tx_palette_rules as rules  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

# 監査 2026-07-21 で確定した帯外カスタム（緑系 accent を P1 問題に使用・宣言なし）。
# 宣言が無いため機械では「意図した選定」と区別できず、ここに明示列挙して P1 帯へ寄せる。
FORCED_CODES = {"刑TX133", "刑TX134", "刑訴TX028", "刑訴TX039", "刑訴TX048"}

VAR_LINE_RE = re.compile(r"(--[a-z0-9-]+)(\s*:\s*)([^;]+);")


def read_raw(f: Path) -> str:
    """改行を変換せず読む（corpus は CRLF/LF 混在＝read_text の universal newlines は
    CRLF ファイルを全行 LF 化して全行 diff を生むため禁止・LEX-403 実地で確認）。"""
    return f.read_bytes().decode("utf-8", errors="replace")


def collect(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    if not paths:
        paths = ["outputs/000_TX", "outputs/ux/000_TX"]
    for p in paths:
        ap = Path(p) if Path(p).is_absolute() else ROOT / p
        if ap.is_file() and ap.suffix == ".html":
            files.append(ap)
        elif ap.is_dir():
            files.extend(sorted(ap.rglob("*.html")))
    return [f for f in files if re.search(r"TX\d+(?:_lex)?$", f.stem)]


def code_of(f: Path) -> str:
    return f.stem[:-4] if f.stem.endswith("_lex") else f.stem


def number_of(code: str) -> int:
    m = re.search(r"(\d+)", code)
    return int(m.group(1)) if m else 0


def template_vars(tpl: dict) -> dict:
    out = {}
    for block in (tpl["b2"], tpl["b3"]):
        for m in VAR_LINE_RE.finditer(block):
            out[m.group(1)] = m.group(3).strip()
    return out


def chip1_of(tpl: dict) -> str:
    m = re.search(r"--accent-light:\s*(#[0-9A-Fa-f]{6})", tpl["b3"])
    return m.group(1).upper() if m else "#------"


def classify(html: str, code: str):
    """repaint 対象種別（'A'/'B'/'C'/None）と宣言パレット名を返す。"""
    decl = rules.last_selected_declaration(html)
    blocks = rules.palette_root_blocks(html)
    if not blocks:
        return None, None
    canon = rules.canonical_default_blocks()
    default_left = any(b == blocks[-1][2] for b in canon.values())
    eff = rules.effective_accent(html)
    if decl is None and default_left:
        kind = "A"
    elif decl is not None and eff in rules.DEFAULT_ACCENTS and \
            rules.template_accent(decl["name"]) not in (None, eff):
        kind = "B"
    elif code in FORCED_CODES and decl is None:
        kind = "C"
    else:
        kind = None
    return kind, (decl["name"] if decl else None)


def build_decl_comment(band: str, name: str, rate: int, chip1: str) -> str:
    pid = rules.PALETTE_IDS.get(name, "??")
    return (
        f"/* === §5 V3 {band} {name} (palette ID: {pid}) ─ 正答率{rate}%（{band}）帯別再選定 ===\n"
        "   役割割当て: ベース 70% / メイン 25% / アクセント 5% / サブ × 2\n"
        f"   palette identity chip 1 {chip1} は --accent-light で保存\n"
        "   正答率帯の帯内パレットへ決定論再選定（tx-lex-repaint-palette・LEX-403 2026-07-21）。\n"
        "   ※以後の更新で配色を変える場合もこの §5 宣言と palette :root を対で書き換える（G71/G72） */"
    )


def repaint_text(html: str, band: str, name: str, rate: int) -> str | None:
    """差し替え済みテキストを返す（変更不要なら None）。"""
    tpl = rules.load_templates().get(name)
    if not tpl:
        return None
    crlf = "\r\n" in html
    work = html.replace("\r\n", "\n") if crlf else html

    blocks = rules.palette_root_blocks(work)
    if not blocks:
        return None
    b2_start, b2_end, _ = blocks[0]

    # block#3（block#2 以降で最初の --accent-light :root）
    b3_span = None
    for m in rules.ROOT_BLOCK_RE.finditer(work, b2_end):
        if "--accent-light:" in m.group(0):
            b3_span = (m.start(), m.end())
            break

    # §5 コメント（block#2 の直前にある最後の /* === §5 V3 ... */）
    decl_span = None
    for m in re.finditer(r"/\*\s*===\s*§5 V3", work[:b2_start]):
        end = work.find("*/", m.start())
        if end != -1 and end < b2_start:
            decl_span = (m.start(), end + 2)

    edits: list[tuple[int, int, str]] = []
    new_comment = build_decl_comment(band, name, rate, chip1_of(tpl))
    if decl_span:
        edits.append((decl_span[0], decl_span[1], new_comment))
    else:
        edits.append((b2_start, b2_start, new_comment + "\n"))
    edits.append((b2_start, b2_end, tpl["b2"]))
    if b3_span:
        edits.append((b3_span[0], b3_span[1], tpl["b3"]))

    # 末尾上書き :root（移行ツールのパレット保全ブロック等）はテンプレ変数だけ同色へ
    tvars = template_vars(tpl)
    for start, end, text in blocks[1:]:
        new_text = VAR_LINE_RE.sub(
            lambda m: f"{m.group(1)}{m.group(2)}{tvars[m.group(1)]};" if m.group(1) in tvars else m.group(0),
            text,
        )
        if new_text != text:
            edits.append((start, end, new_text))

    out = work
    # 同一 start（コメント挿入と block#2 置換）が並ぶ場合は幅の広い置換を先に適用する
    for start, end, rep in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        out = out[:start] + rep + out[end:]
    if crlf:
        out = out.replace("\n", "\r\n")
    return None if out == html else out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply_mode = "--apply" in sys.argv
    files = collect(args)

    # 問題コード単位でグループ化（公式と _lex を同色にする）
    by_code: dict[str, list[Path]] = {}
    for f in files:
        by_code.setdefault(code_of(f), []).append(f)

    planned: list[tuple[Path, str, str, str, int]] = []  # (file, kind, band, palette, rate)
    skipped_no_rate = []
    for code, group in sorted(by_code.items()):
        infos = []
        for f in group:
            # 判定は LF 正規化テキストで（canonical 既定ブロックとのバイト比較を CRLF 差で
            # 取りこぼさない）。書き戻し側 repaint_text は raw を受けて元の改行を保存する。
            norm = read_raw(f).replace("\r\n", "\n")
            kind, decl_name = classify(norm, code)
            rate = rules.extract_rate(norm)
            infos.append((f, norm, kind, decl_name, rate))
        if not any(kind for _, _, kind, _, _ in infos):
            continue
        rate = next((r for _, _, _, _, r in infos if r is not None), None)
        if rate is None:
            skipped_no_rate.append(code)
            continue
        band = rules.band_of(rate)
        # 兄弟の §5 宣言（B 型）が最優先＝宣言パレットへ寄せる。無ければ決定論ローテーション
        decl_name = next((d for _, _, _, d, _ in infos
                          if d and d in rules.load_templates() and rules.PALETTE_BAND.get(d) == band), None)
        name = decl_name or rules.REPAINT_ROTATION[band][number_of(code) % len(rules.REPAINT_ROTATION[band])]
        for f, html, kind, _, frate in infos:
            if kind is None:
                continue
            planned.append((f, kind, band, name, frate if frate is not None else rate))

    print(f"=== TX 難易度帯パレット再選定 {'APPLY' if apply_mode else 'DRY-RUN'} ===")
    print(f"走査 {len(files)} ファイル / 対象 {len(planned)} ファイル"
          f"（A=未選定 {sum(1 for x in planned if x[1]=='A')} / B=宣言未適用 {sum(1 for x in planned if x[1]=='B')} / "
          f"C=帯外カスタム {sum(1 for x in planned if x[1]=='C')}）")
    if skipped_no_rate:
        print(f"[WARN] 正答率が読めずスキップ: {', '.join(skipped_no_rate)}")

    changed = 0
    for f, kind, band, name, rate in planned:
        rel = f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else str(f)
        new_html = repaint_text(read_raw(f), band, name, rate)
        if new_html is None:
            print(f"  [{kind}] {rel} → {name}（{band}）… 変更なし（冪等）")
            continue
        changed += 1
        if apply_mode:
            f.write_text(new_html, encoding="utf-8", newline="")
            print(f"  [{kind}] {rel} → {name}（{band}・正答率{rate}%）✔")
        else:
            print(f"  [{kind}] {rel} → {name}（{band}・正答率{rate}%）")
    print(f"{'反映' if apply_mode else '計画'}: {changed} ファイル")
    return 0


if __name__ == "__main__":
    sys.exit(main())
