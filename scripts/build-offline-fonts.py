#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lexia オフライン用フォント同梱バンドルを作る（2026-08-26・LEX-443）。

**なぜ必要か**：TX/JX/RX/ARIADNE/TREE は 12 役割・11 書体すべてを Google Fonts から読む。
iPad がオフラインだと 1 書体も取得できず、全役割が端末のフォールバック（ヒラギノ 3 書体）へ
潰れる＝「フォントの割り当てがめちゃくちゃ」に見える（LEX-442 の真因。CSS は健全）。
恒久対処は **Lexia アプリ側に woff2 を同梱して `@font-face` を定義する**こと。
そうすれば HTML 2,700 本は無改修（`font-family` の名前を参照しているだけ）で全書体が
オフラインでも正しく当たる。

**やること**：
  1. corpus（outputs/references）の `<link href="https://fonts.googleapis.com/css2?...">` を
     全部読み、必要な (書体, italic, ウェイト) を単一情報源として集める。
  2. 各 face を Google Fonts から**フル版 1 ファイル**で取得する（旧 UA を送ると unicode-range
     分割ではなく単一 woff が返る。新 UA だと 120 分割になり、法律日本語は ほぼ全分割に
     跨るため合計 2.5MB/face と逆に太る＝実測）。
  3. `lexia-font-charset.py` が出した文字集合だけへサブセット化し woff2 で保存。
  4. `lexia-offline-fonts.css`（@font-face 一式）を書き出す。Lexia はこの CSS と woff2 を
     アプリに同梱し、問題 HTML を表示する文書へ読ませるだけでよい。

**ライセンス**：同梱する 11 書体はすべて SIL Open Font License 1.1 または Apache License 2.0
（Kosugi Maru）。サブセット化・再配布・アプリ同梱はいずれも許諾範囲内。生成物には
OFL.txt を必ず添える（`--licenses` が出力先へ一覧を書く）。

  python scripts/build-offline-fonts.py --list                 # 必要 face の一覧だけ
  python scripts/build-offline-fonts.py --out dist/lexia-fonts # 取得→サブセット→CSS 生成
  python scripts/build-offline-fonts.py --out dist/lexia-fonts --latin-only  # 欧文だけ試す
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = ("canonical", "outputs/000_TX", "outputs/001_JX", "outputs/ux", "references")
CHARSET = ROOT / "docs" / "data" / "lexia-offline-charset.txt"

# 旧 UA ＝ unicode-range 分割なしの単一フォントが返る（woff）。新 UA だと 120 分割 woff2。
UA_LEGACY = "Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20110814 Firefox/6.0"

LINK_RE = re.compile(r"https://fonts\.googleapis\.com/css2\?([^\"'>]+)")


def fetch(url: str, ua: str = UA_LEGACY) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    return urllib.request.urlopen(req, timeout=120).read()


def collect_faces() -> dict[str, set[tuple[int, int]]]:
    """corpus の Google Fonts リンクから {family: {(italic, weight), ...}} を作る。"""
    faces: dict[str, set[tuple[int, int]]] = {}
    for r in SCAN_ROOTS:
        base = ROOT / r
        if not base.exists():
            continue
        for f in base.rglob("*.html"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            for q in LINK_RE.findall(text):
                q = q.replace("&amp;", "&")
                for key, val in urllib.parse.parse_qsl(q, keep_blank_values=True):
                    if key != "family":
                        continue
                    _parse_family(val, faces)
    return faces


def _parse_family(spec: str, faces: dict[str, set[tuple[int, int]]]) -> None:
    if ":" in spec:
        name, axes = spec.split(":", 1)
    else:
        name, axes = spec, ""
    name = name.replace("+", " ").strip()
    if not name:
        return
    got = faces.setdefault(name, set())
    if "@" not in axes:
        got.add((0, 400))
        return
    keys, values = axes.split("@", 1)
    keys = keys.split(",")
    for tup in values.split(";"):
        parts = tup.split(",")
        if len(parts) != len(keys):
            continue
        d = dict(zip(keys, parts))
        try:
            ital = int(d.get("ital", 0))
            wght = int(float(d.get("wght", 400)))
        except ValueError:
            continue
        got.add((ital, wght))


def slug(name: str, ital: int, wght: int) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return f"{base}-{wght}{'i' if ital else ''}"


def face_url(name: str, ital: int, wght: int) -> str:
    fam = urllib.parse.quote_plus(name)
    axis = f"ital,wght@{ital},{wght}" if ital else f"wght@{wght}"
    return f"https://fonts.googleapis.com/css2?family={fam}:{axis}"


def download_face(name: str, ital: int, wght: int) -> bytes:
    css = fetch(face_url(name, ital, wght)).decode("utf-8", "replace")
    m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)
    if not m:
        raise RuntimeError(f"font url が取れない: {name} {wght}{'i' if ital else ''}")
    return fetch(m.group(1))


def build_one(out_dir: Path, name: str, ital: int, wght: int, text: str) -> tuple[str, int]:
    from fontTools import subset
    from fontTools.ttLib import TTFont
    import io

    raw = download_face(name, ital, wght)
    font = TTFont(io.BytesIO(raw))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.notdef_outline = True
    opts.drop_tables += ["DSIG"]
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.recalc_bounds = False
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = "woff2"
    fname = slug(name, ital, wght) + ".woff2"
    path = out_dir / fname
    font.save(str(path))
    font.close()
    return fname, path.stat().st_size


CSS_HEAD = """/* Lexia オフライン用フォント（自動生成・scripts/build-offline-fonts.py）
 *
 * 問題 HTML（TX/JX/RX/ARIADNE/TREE）は 12 役割・11 書体を Google Fonts から読むため、
 * オフラインの iPad では全役割が端末フォントへ潰れる。この CSS と同階層の woff2 を
 * Lexia アプリに同梱し、問題 HTML を表示する文書へ読ませると、ネット回線なしでも
 * 12 役割がすべて正しい書体で描かれる（HTML 側は無改修）。
 *
 * 収録字数: {chars} 字（corpus 実使用 + JIS 第1水準ほかの安全網）
 * 収録 face: {faces} / 合計 {mb} MB
 * ライセンス: SIL Open Font License 1.1（Kosugi Maru のみ Apache License 2.0）。
 *             同梱時は各書体の OFL.txt / LICENSE.txt を添付すること。
 */
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist/lexia-offline-fonts")
    ap.add_argument("--charset", default=str(CHARSET))
    ap.add_argument("--list", action="store_true", help="必要 face を数えるだけ")
    ap.add_argument("--only", default="", help="書体名の部分一致でしぼる（検証用）")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()

    faces = collect_faces()
    if a.only:
        faces = {k: v for k, v in faces.items() if a.only.lower() in k.lower()}
    flat = sorted((n, i, w) for n, s in faces.items() for (i, w) in s)
    print(f"=== corpus が要求する face: {len(faces)} 書体 / {len(flat)} face ===")
    for n in sorted(faces):
        ws = ",".join(f"{w}{'i' if i else ''}" for i, w in sorted(faces[n]))
        print(f"  {n}: {ws}")
    if a.list:
        return 0

    cs = Path(a.charset)
    if not cs.is_absolute():
        cs = ROOT / cs
    if not cs.exists():
        print(f"[ERROR] 文字集合が無い: {cs}\n  先に python scripts/lexia-font-charset.py を実行する")
        return 2
    text = cs.read_text(encoding="utf-8").strip("\n")
    print(f"サブセット文字数: {len(text)}")

    out_dir = Path(a.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, int, int, str, int]] = []
    errors: list[str] = []

    def work(item):
        n, i, w = item
        try:
            fname, size = build_one(out_dir, n, i, w, text)
            print(f"  [OK] {n} {w}{'i' if i else ''} -> {fname} ({size//1024} KB)")
            return (n, i, w, fname, size)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{n} {w}{'i' if i else ''}: {e}")
            print(f"  [NG] {n} {w}{'i' if i else ''}: {e}")
            return None

    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(work, flat):
            if r:
                results.append(r)

    total = sum(r[4] for r in results)
    lines = [CSS_HEAD.format(chars=len(text), faces=len(results),
                             mb=round(total / 1024 / 1024, 2))]
    for n, i, w, fname, _ in sorted(results):
        lines.append("@font-face{")
        lines.append(f"  font-family:'{n}';")
        lines.append(f"  font-style:{'italic' if i else 'normal'};")
        lines.append(f"  font-weight:{w};")
        lines.append("  font-display:swap;")
        lines.append(f"  src:url('./{fname}') format('woff2');")
        lines.append("}")
    (out_dir / "lexia-offline-fonts.css").write_text("\n".join(lines) + "\n",
                                                     encoding="utf-8", newline="\n")

    print(f"\n==== {len(results)} face / 合計 {total/1024/1024:.2f} MB → {out_dir} ====")
    if errors:
        print(f"[WARN] 失敗 {len(errors)} 件")
        for e in errors:
            print("   ", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
