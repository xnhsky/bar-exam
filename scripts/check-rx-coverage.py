#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RX カバレッジ検査（ARIADNE 想起カードの data-rx ↔ RX 実ファイルの突き合わせ）

背景：
  Lexia は ARIADNE 解法ナビの想起カード（data-recall）に刻まれた data-rx を辿って、
  対応する RX 論証カードを復習プールへ注入する（scripts/ariadne-backfill-rx-link.py が
  data-recall タグに data-rx="{科目}RX{NNN}_{論点序号}" を刻む）。
  ところが 1 問の RX 枚数 > 想起カード数 のとき、どの想起にも紐づかない RX が生じ、
  それらは「どの想起の誤答でも引かれない」＝復習プールから取りこぼされる
  （例：刑JX008 は RX が _1〜_4 の 4 枚あるが ARIADNE は _1/_2/_4 しか参照せず _3 が孤児）。
  本スクリプトはこの取りこぼし（uncovered）と、逆に ARIADNE が実在しない RX を指す
  リンク切れ（dangling）を機械検出する。

仕組み（read-only・冪等）：
  各 outputs/ux/002_RX/{NNN_科目}/{科目JX NNN}/ について
    rx_present    = フォルダ内 RX ファイル名のコード集合（例 刑RX008_3）
    rx_referenced = 対応 outputs/ux/001_ARIADNE/{NNN_科目}/{科目JX NNN}_ARIADNE.html の
                    data-rx 値集合
  を集め、
    uncovered = present − referenced   （WARN・想起に未割当の RX＝復習プール取りこぼし）
    dangling  = referenced − present   （ERROR・ARIADNE が実在しない RX を参照＝リンク切れ）
  を科目別・JX 別に報告し、総計を出す。
  RX フォルダと ARIADNE ファイルの両側から JX を集合和して走査するため、
  「RX はあるが ARIADNE 不在」「ARIADNE はあるが RX フォルダ不在」も取りこぼさない。
  RX 未生成の科目（刑法以外＝RX フォルダが 1 つも無い）は graceful skip。

使い方：
  python scripts/check-rx-coverage.py            # 全科目
  python scripts/check-rx-coverage.py 刑          # 科目を絞る（ディレクトリ名の部分一致）
  python scripts/check-rx-coverage.py --summary   # OK の JX 行を省き WARN/ERROR と集計のみ

終了コード：
  0 = dangling 無し（uncovered は WARN で終了コードに影響しない）
  1 = dangling（リンク切れ）あり＝要修正
  3 = 構造異常・引数不正（基準ディレクトリ無し・科目フィルタ不一致 等）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RX_BASE = ROOT / "outputs" / "ux" / "002_RX"
ARI_BASE = ROOT / "outputs" / "ux" / "001_ARIADNE"

GREEN = "\033[32m"; YELLOW = "\033[33m"; RED = "\033[31m"
DIM = "\033[2m"; CYAN = "\033[36m"; RST = "\033[0m"

# ariadne-backfill-rx-link.py が刻む data-rx の値（例 data-rx="刑RX008_1"）。
DATA_RX_RE = re.compile(r'data-rx="([^"]+)"')
# RX コード／JX フォルダ名の番号（刑RX008_3 / 刑JX008 → 8）。並び順の安定化に使う。
JXNUM_RE = re.compile(r'JX0*(\d+)')
RXNUM_RE = re.compile(r'RX0*(\d+)_0*(\d+)')
ARI_SUFFIX = "_ARIADNE.html"


def jx_sort_key(code):
    m = JXNUM_RE.search(code)
    return (int(m.group(1)) if m else 10 ** 9, code)


def rx_sort_key(code):
    m = RXNUM_RE.search(code)
    return (int(m.group(1)), int(m.group(2)), code) if m else (10 ** 9, 0, code)


def rx_codes_in_folder(folder):
    """フォルダ内 RX ファイル名のコード集合（拡張子除く・'RX' を含む html のみ）。"""
    return {p.stem for p in folder.glob("*.html") if "RX" in p.stem}


def referenced_in_ariadne(path):
    """ARIADNE HTML の data-rx 値集合（空白除去・空値は除外）。"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {m.group(1).strip() for m in DATA_RX_RE.finditer(text) if m.group(1).strip()}


def subject_dirs(filter_token):
    """002_RX 配下の科目ディレクトリ（フィルタがあれば名前の部分一致で絞る）。"""
    if not RX_BASE.is_dir():
        print(f"{RED}[FATAL]{RST} RX 基準ディレクトリが無い: {RX_BASE}")
        sys.exit(3)
    dirs = sorted([d for d in RX_BASE.iterdir() if d.is_dir()])
    if filter_token:
        dirs = [d for d in dirs if filter_token in d.name]
        if not dirs:
            print(f"{RED}[FATAL]{RST} 科目フィルタ '{filter_token}' に一致するディレクトリが "
                  f"002_RX 下に無い")
            sys.exit(3)
    return dirs


def check_subject(subj_dir, summary):
    """1 科目を検査。戻り: stats dict、または RX 未生成なら None（graceful skip）。"""
    subj = subj_dir.name
    rx_folders = [d for d in subj_dir.iterdir() if d.is_dir() and "JX" in d.name]
    if not rx_folders:
        print(f"{CYAN}## {subj}{RST}  {YELLOW}[SKIP]{RST} RX 未生成 → スキップ")
        return None

    ari_dir = ARI_BASE / subj
    # JX コードを RX フォルダ ∪ ARIADNE ファイルで集合和（両方向の取りこぼしを捕捉）。
    jx_codes = {d.name for d in rx_folders}
    ari_files = {}  # jxcode -> Path
    if ari_dir.is_dir():
        for p in ari_dir.glob("*" + ARI_SUFFIX):
            ari_files[p.name[: -len(ARI_SUFFIX)]] = p
            jx_codes.add(p.name[: -len(ARI_SUFFIX)])

    print(f"{CYAN}## {subj}{RST}")
    s = dict(jx=0, present=0, referenced=0, uncovered=0, dangling=0,
             ok=0, warn=0, err=0, ari_missing=0)
    dangling_detail = []  # (jxcode, [rx, ...])

    for code in sorted(jx_codes, key=jx_sort_key):
        folder = subj_dir / code
        present = rx_codes_in_folder(folder) if folder.is_dir() else set()
        ari_path = ari_files.get(code)
        referenced = referenced_in_ariadne(ari_path) if ari_path else set()
        uncovered = present - referenced
        dangling = referenced - present

        s["jx"] += 1
        s["present"] += len(present)
        s["referenced"] += len(referenced)
        s["uncovered"] += len(uncovered)
        s["dangling"] += len(dangling)

        notes = []
        if folder.is_dir() and ari_path is None:
            s["ari_missing"] += 1
            notes.append("ARIADNE 不在")
        if not folder.is_dir() and ari_path is not None:
            notes.append("RX フォルダ不在")
        note_s = f"  {DIM}({'; '.join(notes)}){RST}" if notes else ""

        stat = f"present {len(present)} / ref {len(referenced)}"
        if dangling:
            s["err"] += 1
            dangling_detail.append((code, sorted(dangling, key=rx_sort_key)))
            print(f"  {RED}[ERROR]{RST} {code}  {stat}  "
                  f"dangling(参照先RX不在): {', '.join(sorted(dangling, key=rx_sort_key))}{note_s}")
        elif uncovered:
            s["warn"] += 1
            print(f"  {YELLOW}[WARN]{RST}  {code}  {stat}  "
                  f"uncovered(想起未割当): {', '.join(sorted(uncovered, key=rx_sort_key))}{note_s}")
        else:
            s["ok"] += 1
            if not summary:
                print(f"  {GREEN}[OK]{RST}    {code}  {stat}{note_s}")

    print(f"  {DIM}── {subj} 計: JX {s['jx']} / present {s['present']} / referenced "
          f"{s['referenced']} / OK {s['ok']} · WARN {s['warn']} · ERROR {s['err']}"
          f" → uncovered {s['uncovered']} 件 · dangling {s['dangling']} 件{RST}")
    s["dangling_detail"] = dangling_detail
    s["subject"] = subj
    return s


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(0)
    summary = "--summary" in args
    pos = [a for a in args if not a.startswith("-")]
    filter_token = pos[0] if pos else None

    print("=== RX カバレッジ検査（ARIADNE 想起 data-rx ↔ RX 実ファイル）===")
    if not ARI_BASE.is_dir():
        print(f"{YELLOW}[WARN]{RST} ARIADNE 基準ディレクトリが無い: {ARI_BASE}"
              f"（全 RX が uncovered 扱いになる）")
    print()

    grand = dict(jx=0, present=0, referenced=0, uncovered=0, dangling=0,
                 ok=0, warn=0, err=0, ari_missing=0)
    checked = []
    skipped = []
    for d in subject_dirs(filter_token):
        st = check_subject(d, summary)
        print()
        if st is None:
            skipped.append(d.name)
            continue
        checked.append(st)
        for k in grand:
            grand[k] += st.get(k, 0)

    print("=== 総計 ===")
    print(f"  対象科目 {len(checked)}（{', '.join(s['subject'] for s in checked) or '—'}）"
          f" ／ スキップ {len(skipped)}（{', '.join(skipped) or '—'}）")
    print(f"  JX {grand['jx']} ／ RX present {grand['present']} ／ referenced "
          f"{grand['referenced']} ／ ARIADNE 不在 {grand['ari_missing']} 問")
    print(f"  {YELLOW}uncovered{RST}（WARN・想起カードに未割当の RX＝復習プール取りこぼし）"
          f": {grand['uncovered']} 件 / {grand['warn']} 問")
    print(f"  {RED}dangling{RST} （ERROR・ARIADNE が参照する RX が実在しない）"
          f": {grand['dangling']} 件 / {grand['err']} 問")

    if grand["dangling"]:
        print(f"\n  {RED}リンク切れ詳細：{RST}")
        for st in checked:
            for code, rxs in st["dangling_detail"]:
                print(f"    {st['subject']}/{code}: {', '.join(rxs)}")
        print(f"\n→ {RED}dangling あり＝終了コード 1（要修正）{RST}")
        sys.exit(1)
    print(f"\n→ {GREEN}dangling 無し＝終了コード 0{RST}"
          + (f"（uncovered {grand['uncovered']} 件は想起カード増設で解消可・WARN）"
             if grand["uncovered"] else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
