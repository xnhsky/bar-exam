#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-tx-v13m-depth.py ── TX _lex v13 解説の「深さ」助言リンター（§v13m A/③・2026-07-09 恒久対策）。

監査（2026-07-09）で判明した薄さ＝「①THE GIST がやさしい版でなく要点羅列」「②⚠️罠が結論言い換えで
横串を欠く」は、既存ゲート（G50 構造／G51 BASIS 存在／G52 罠が非空か）の外にあり機械では素通りする
（spec 第v13m項＝GIST の質は機械化困難）。本リンターは失敗シグネチャだけを高精度で拾い、著者の
自己照合1回の worklist にする。判定ロジックは validate-tx-core.py の gist_depth_flag/trap_depth_flag が
単一情報源（validate-tx-core の G56/G57 WARNING と本スクリプトが共有）。

使い方:
  python -X utf8 scripts/check-tx-v13m-depth.py                        # 既定=outputs/ux/000_TX 全科目
  python -X utf8 scripts/check-tx-v13m-depth.py outputs/ux/000_TX/001_刑法
  python -X utf8 scripts/check-tx-v13m-depth.py <file_lex.html> --detail
  python -X utf8 scripts/check-tx-v13m-depth.py <dir> --strict         # 候補があれば exit 1（任意ゲート用）

助言（WARNING 相当）につき既定は常に exit 0。ERROR にしないのは、良質だが簡潔な版（ます形やさしい版）を
誤爆させないため。gold 見本＝刑TX362 / 409-425 / 436-445。
"""
from __future__ import annotations
import sys, re, argparse, importlib.util
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # cp932 パイプ/headless での UnicodeEncodeError 回避
except Exception:
    pass

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent


def _load_core():
    spec = importlib.util.spec_from_file_location("validate_tx_core", SCRIPTS / "validate-tx-core.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CORE = _load_core()
gist_depth_flag = CORE.gist_depth_flag
trap_depth_flag = CORE.trap_depth_flag
BeautifulSoup = CORE.BeautifulSoup


def _clean(el, tag_re):
    if el is None:
        return None
    return re.sub(tag_re, "", el.get_text(" ", strip=True)).strip()


def scan_file(path: Path):
    """1 ファイルを走査し (thin_gist, thin_trap) を返す。各要素は (card_no, reason, snippet)。v13 でなければ None。"""
    html = path.read_bytes().decode("utf-8", "replace")
    soup = BeautifulSoup(html, "html.parser")
    if not (soup.select_one(".tx-inline-card .tx-v13-verdict") or "tx-v13-verdict" in html):
        return None
    thin_gist, thin_trap = [], []
    for i, card in enumerate(soup.select(".tx-inline-card"), start=1):
        ex = card.select_one(".tx-inline-explain") or card
        g = _clean(ex.select_one(".syn-lead"), r"^\s*💡\s*THE GIST\s*")
        if g is not None:
            r = gist_depth_flag(g)
            if r:
                thin_gist.append((i, r, g[:78]))
        trap = ex.select_one(".tx-v13-trap")
        tb = (trap.select_one(".tx-v13-trap-body") if trap else None) or trap
        t = _clean(tb, r"^\s*⚠️?\s*間違いやすいポイント\s*")
        if t is not None:
            r = trap_depth_flag(t)
            if r:
                thin_trap.append((i, r, t[:78]))
    return thin_gist, thin_trap


def collect(targets):
    files = []
    for tg in targets:
        p = Path(tg)
        if p.is_dir():
            files += sorted(p.rglob("*_lex.html"))
        elif p.is_file():
            files.append(p)
    # 公式版（ux 以外）と重複ミラーは _lex のみ対象なので rglob で十分
    return files


def main():
    ap = argparse.ArgumentParser(description="TX _lex v13 解説の深さ（やさしい版GIST/横串trap）助言リンター")
    ap.add_argument("targets", nargs="*", default=["outputs/ux/000_TX"],
                    help="ファイル or ディレクトリ（既定 outputs/ux/000_TX）")
    ap.add_argument("--detail", action="store_true", help="候補カードの本文抜粋も表示")
    ap.add_argument("--strict", action="store_true", help="候補があれば exit 1（任意ゲート用）")
    a = ap.parse_args()

    files = collect(a.targets)
    rows = []  # (path, thin_gist, thin_trap)
    for f in files:
        try:
            res = scan_file(f)
        except Exception as e:
            print(f"  読込スキップ: {f} ({e})")
            continue
        if res is None:
            continue
        tg, tt = res
        if tg or tt:
            rows.append((f, tg, tt))

    scanned_v13 = sum(1 for f in files if _is_v13(f))
    print("=== TX _lex v13m 深さ助言（薄い GIST / 横串を欠く罠） ===")
    print(f"走査 _lex={len(files)} / v13={scanned_v13} / 候補あり={len(rows)} ファイル\n")
    if not rows:
        print("候補なし（やさしい版GIST・横串trap のシグネチャ充足）。")
        return 0

    rows.sort(key=lambda r: -(len(r[1]) + len(r[2])))
    tot_g = tot_t = 0
    print(f"{'FILE':<22}{'薄GIST':>7}{'薄罠':>6}")
    print("-" * 40)
    for f, tg, tt in rows:
        tot_g += len(tg); tot_t += len(tt)
        gcards = ",".join(str(i) for i, _, _ in tg) or "-"
        tcards = ",".join(str(i) for i, _, _ in tt) or "-"
        print(f"{f.stem:<22}{len(tg):>7}{len(tt):>6}   GIST[{gcards}] 罠[{tcards}]")
        if a.detail:
            for i, r, s in tg:
                print(f"      GIST 記述{i}: {r}\n        « {s} »")
            for i, r, s in tt:
                print(f"      罠  記述{i}: {r}\n        « {s} »")
    print("-" * 40)
    print(f"合計 薄GIST={tot_g} 枚 / 薄罠={tot_t} 枚（{len(rows)} ファイル）")
    print("\n注: 助言（機械化困難ゆえ WARNING）。候補＝著者の自己照合1回の worklist。"
          "gold 見本＝刑TX362 / 409-425 / 436-445。誤爆（良質な簡潔版）は著者判断で除外可。")
    return 1 if a.strict else 0


def _is_v13(f: Path) -> bool:
    try:
        return "tx-v13-verdict" in f.read_bytes().decode("utf-8", "replace")
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
