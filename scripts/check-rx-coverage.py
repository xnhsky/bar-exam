#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RX カバレッジ検査（ARIADNE 想起カードの data-rx ↔ RX 実ファイルの突き合わせ）

背景：
  Lexia は ARIADNE 解法ナビの想起カード（data-recall）に刻まれた data-rx を辿って、
  対応する RX 論証カードを復習プールへ注入する（scripts/ariadne-backfill-rx-link.py が
  data-recall タグに data-rx="{科目}RX{NNN}_{論点序号}" を刻む）。
  1 問の RX 枚数 > data-rx 参照数 のとき、どの想起にも直接紐づかない RX（孤児）が生じる。

  ただし Lexia には安全網がある（lexia/src/App.jsx）：
    - recordQuizAttempt（App.jsx:3509-3517）が想起カードを「書けなかった」時、その data-rx を起点に
    - supplementJxRx（App.jsx:3562-3571）が同 JX の RX を _1.._8 と順に手繰り（連続2miss で打切）
      injectRxCardForRecall で復習プールへまとめ補充する（＝論点まるごと取りこぼし回収）。
  従って「data-rx で参照されない孤児 RX」も、その JX に **data-rx が 1 つでも在れば**
  （＝失敗を起点にできれば）安全網で復習プールに入る＝取りこぼされない（遅延注入）。

  本当に取りこぼされるのは次の 2 つ：
    (A) その JX の ARIADNE に data-rx が **1 つも無い**（referenced==0）。起点が無く
        supplementJxRx が発火しない＝孤児 RX が永久に復習プールへ入らない。← 要対応
    (B) RX 連番が supplementJxRx の上限 _8 を超える（index>8）。手繰りが届かない。← 将来対策
  これらを uncovered の中で UNREACHABLE として切り分け、安全網で届くものを SAFETY-NET と
  区別して報告する（孤児の総数だけ見て過大に騒がないため）。

仕組み（read-only・冪等）：
  各 outputs/ux/002_RX/{NNN_科目}/{科目JX NNN}/ について
    rx_present    = フォルダ内 RX ファイル名のコード集合（例 刑RX008_3）
    rx_referenced = 対応 001_ARIADNE/{NNN_科目}/{科目JX NNN}_ARIADNE.html の data-rx 値集合
  を集め、
    uncovered = present − referenced
        ├ UNREACHABLE … referenced==0（起点無し）または index>_8 上限 → 真の取りこぼし
        └ SAFETY-NET  … 上記以外 → supplementJxRx が想起失敗時に回収（遅延注入・実害小）
    dangling  = referenced − present   → ARIADNE が実在しない RX を参照（リンク切れ・ERROR）
  を科目別・JX 別に報告し、総計を出す。RX フォルダと ARIADNE ファイルの両側から JX を集合和。
  RX 未生成の科目（刑法以外＝RX フォルダが 1 つも無い）は graceful skip。

使い方：
  python scripts/check-rx-coverage.py            # 全科目
  python scripts/check-rx-coverage.py 刑          # 科目を絞る（ディレクトリ名の部分一致）
  python scripts/check-rx-coverage.py --summary   # OK の JX 行を省き 問題のある JX と集計のみ
  python scripts/check-rx-coverage.py --strict     # UNREACHABLE があっても終了コード 1（CI ゲート用）

終了コード：
  0 = dangling 無し（uncovered は WARN・終了コードに影響しない）
  1 = dangling（リンク切れ）あり。--strict 指定時は UNREACHABLE があっても 1
  3 = 構造異常・引数不正（基準ディレクトリ無し・科目フィルタ不一致 等）
"""
import re
import sys
from pathlib import Path

# Windows の headless／パイプ実行は stdout が cp932 になり、↔(U+2194)・絵文字・中点(·)など
# cp932 外の文字を print した瞬間に UnicodeEncodeError でクラッシュ→exit 1 する（＝gate に
# 組み込むとクリーンでも"空振りブロック"になる）。caller 依存を無くすため出力を UTF-8 に固定。
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass  # Python<3.7 等 reconfigure 不可環境では従来どおり

ROOT = Path(__file__).resolve().parents[1]
RX_BASE = ROOT / "outputs" / "ux" / "002_RX"
ARI_BASE = ROOT / "outputs" / "ux" / "001_ARIADNE"

# Lexia supplementJxRx（App.jsx:3567）の手繰り上限。i <= 8 で打ち切るため _9 以降は届かない。
SUPPLEMENT_CAP = 8

GREEN = "\033[32m"; YELLOW = "\033[33m"; RED = "\033[31m"
MAGENTA = "\033[35m"; DIM = "\033[2m"; CYAN = "\033[36m"; RST = "\033[0m"

# ariadne-backfill-rx-link.py が刻む data-rx の値（例 data-rx="刑RX008_1"）。
DATA_RX_RE = re.compile(r'data-rx="([^"]+)"')
# RX コード／JX フォルダ名の番号（刑RX008_3 / 刑JX008 → 8）。並び順の安定化と連番抽出に使う。
JXNUM_RE = re.compile(r'JX0*(\d+)')
RXNUM_RE = re.compile(r'RX0*(\d+)_0*(\d+)')
ARI_SUFFIX = "_ARIADNE.html"


def jx_sort_key(code):
    m = JXNUM_RE.search(code)
    return (int(m.group(1)) if m else 10 ** 9, code)


def rx_sort_key(code):
    m = RXNUM_RE.search(code)
    return (int(m.group(1)), int(m.group(2)), code) if m else (10 ** 9, 0, code)


def rx_suffix_index(code):
    """RX コード末尾の論点序号（刑RX008_3 → 3）。取れなければ None。"""
    m = RXNUM_RE.search(code)
    return int(m.group(2)) if m else None


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


def classify_uncovered(uncovered, has_anchor):
    """uncovered RX を UNREACHABLE / SAFETY-NET に層別。
    戻り: (unreachable[(code, reason)], safetynet[code])。
    UNREACHABLE = supplementJxRx が届かない＝真の取りこぼし：
      - has_anchor False（その JX に data-rx 起点が無い → 発火しない）
      - index > _8 上限（手繰りが届かない）
    """
    unreachable, safetynet = [], []
    for code in sorted(uncovered, key=rx_sort_key):
        idx = rx_suffix_index(code)
        if not has_anchor:
            unreachable.append((code, "data-rx 起点なし"))
        elif idx is not None and idx > SUPPLEMENT_CAP:
            unreachable.append((code, f"_{idx} > 手繰り上限 _{SUPPLEMENT_CAP}"))
        else:
            safetynet.append(code)
    return unreachable, safetynet


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
    s = dict(jx=0, present=0, referenced=0, uncovered=0, unreachable=0, safetynet=0,
             dangling=0, ok=0, ari_missing=0)
    dangling_detail = []      # (jxcode, [rx, ...])
    unreachable_detail = []   # (jxcode, [(rx, reason), ...])

    for code in sorted(jx_codes, key=jx_sort_key):
        folder = subj_dir / code
        present = rx_codes_in_folder(folder) if folder.is_dir() else set()
        ari_path = ari_files.get(code)
        referenced = referenced_in_ariadne(ari_path) if ari_path else set()
        uncovered = present - referenced
        dangling = referenced - present
        has_anchor = len(referenced) >= 1
        unreachable, safetynet = classify_uncovered(uncovered, has_anchor)

        s["jx"] += 1
        s["present"] += len(present)
        s["referenced"] += len(referenced)
        s["uncovered"] += len(uncovered)
        s["unreachable"] += len(unreachable)
        s["safetynet"] += len(safetynet)
        s["dangling"] += len(dangling)

        notes = []
        if folder.is_dir() and ari_path is None:
            s["ari_missing"] += 1
            notes.append("ARIADNE 不在")
        if not folder.is_dir() and ari_path is not None:
            notes.append("RX フォルダ不在")
        note_s = f"  {DIM}({'; '.join(notes)}){RST}" if notes else ""
        stat = f"present {len(present)} / ref {len(referenced)}"

        printed = False
        if dangling:
            dangling_detail.append((code, sorted(dangling, key=rx_sort_key)))
            print(f"  {RED}[ERROR]{RST}       {code}  {stat}  "
                  f"dangling(参照先RX不在): {', '.join(sorted(dangling, key=rx_sort_key))}{note_s}")
            printed = True
        if unreachable:
            unreachable_detail.append((code, unreachable))
            rxs = ", ".join(f"{c}〔{why}〕" for c, why in unreachable)
            print(f"  {MAGENTA}[UNREACHABLE]{RST} {code}  {stat}  "
                  f"取りこぼし(安全網外): {rxs}{note_s if not dangling else ''}")
            printed = True
        if safetynet and not summary:
            print(f"  {YELLOW}[SAFETY-NET]{RST}  {code}  {stat}  "
                  f"孤児だが supplementJxRx 回収: {', '.join(sorted(safetynet, key=rx_sort_key))}")
            printed = True
        if not printed:
            s["ok"] += 1
            if not summary:
                print(f"  {GREEN}[OK]{RST}          {code}  {stat}{note_s}")

    print(f"  {DIM}── {subj} 計: JX {s['jx']} / present {s['present']} / referenced "
          f"{s['referenced']} → uncovered {s['uncovered']}"
          f"（{MAGENTA}UNREACHABLE {s['unreachable']}{RST}{DIM} / SAFETY-NET {s['safetynet']}）"
          f" / dangling {s['dangling']}{RST}")
    s["subject"] = subj
    s["dangling_detail"] = dangling_detail
    s["unreachable_detail"] = unreachable_detail
    return s


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(0)
    summary = "--summary" in args
    strict = "--strict" in args
    pos = [a for a in args if not a.startswith("-")]
    filter_token = pos[0] if pos else None

    print("=== RX カバレッジ検査（ARIADNE 想起 data-rx ↔ RX 実ファイル）===")
    if not ARI_BASE.is_dir():
        print(f"{YELLOW}[WARN]{RST} ARIADNE 基準ディレクトリが無い: {ARI_BASE}"
              f"（全 RX が起点無し＝UNREACHABLE 扱いになる）")
    print()

    grand = dict(jx=0, present=0, referenced=0, uncovered=0, unreachable=0,
                 safetynet=0, dangling=0, ok=0, ari_missing=0)
    checked, skipped = [], []
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
    print(f"  uncovered（想起 data-rx に未参照の RX）: {grand['uncovered']} 件　内訳↓")
    print(f"    {MAGENTA}UNREACHABLE{RST}（{RED}真の取りこぼし{RST}・data-rx 起点なし/上限超で "
          f"supplementJxRx が届かない）: {grand['unreachable']} 件")
    print(f"    {YELLOW}SAFETY-NET{RST} （孤児だが想起失敗時に supplementJxRx が回収＝遅延注入・実害小）"
          f": {grand['safetynet']} 件")
    print(f"  {RED}dangling{RST}（ARIADNE が参照する RX が実在しない＝リンク切れ）: {grand['dangling']} 件")

    if grand["unreachable"]:
        print(f"\n  {MAGENTA}■ UNREACHABLE 詳細（要対応＝この JX の ARIADNE は data-rx 起点を持たない）：{RST}")
        for st in checked:
            for code, rxs in st["unreachable_detail"]:
                joined = ", ".join(f"{c}〔{why}〕" for c, why in rxs)
                print(f"    {st['subject']}/{code}: {joined}")
        print(f"  {DIM}→ 対応案：当該 JX の ARIADNE を data-rx 起点（想起カード＋リンク）付きで再生成すると、"
              f"Lexia supplementJxRx が _1.._{SUPPLEMENT_CAP} を一括回収する。{RST}")
    if grand["dangling"]:
        print(f"\n  {RED}■ dangling 詳細（リンク切れ＝ARIADNE 側 data-rx の誤り or RX 欠落）：{RST}")
        for st in checked:
            for code, rxs in st["dangling_detail"]:
                print(f"    {st['subject']}/{code}: {', '.join(rxs)}")

    fail = grand["dangling"] > 0 or (strict and grand["unreachable"] > 0)
    if fail:
        why = []
        if grand["dangling"]:
            why.append(f"dangling {grand['dangling']}")
        if strict and grand["unreachable"]:
            why.append(f"UNREACHABLE {grand['unreachable']}（--strict）")
        print(f"\n→ {RED}終了コード 1（{', '.join(why)}）{RST}")
        sys.exit(1)
    tail = ""
    if grand["unreachable"]:
        tail = (f"（{MAGENTA}UNREACHABLE {grand['unreachable']} 件は要対応{RST}"
                f"・--strict で exit 1 にできる）")
    elif grand["uncovered"]:
        tail = f"（SAFETY-NET {grand['safetynet']} 件は Lexia が回収・実害小）"
    print(f"\n→ {GREEN}dangling 無し＝終了コード 0{RST}{tail}")
    sys.exit(0)


if __name__ == "__main__":
    main()
