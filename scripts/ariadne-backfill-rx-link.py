#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ariadne-backfill-rx-link.py — 既存 ARIADNE の想起カードに対応RX論証カードの data-rx を刻む。

Lexia LXA_FEAT_008（spec §9-5 / validate-ariadne A29）。想起カード（data-recall）に
`data-rx="{科目}RX{NNN}_{論点序号}"` を付与し、Lexia が想起の誤答時に対応RXを復習プールへ
注入できるようにする。想起カードとRXは多対一・順序非対応のため、機械ヒューリスティックでは
誤リンクする。よって各カード→RXの対応は人手判定（MAP）で確定し、本スクリプトは

  ① 配列長 == そのファイルの想起カード数（document順）
  ② 参照先RXファイルが outputs/ux/002_RX/.../{科目}JX{NNN}/ に実在

を全件検査してからのみ書き込む（不一致は全体を中止）。冪等（既に data-rx があるカードは skip）。
None は総論／解法の型（「4点セット」「犯罪論3段階」）や対応RX無しの汎用想起＝意図的に刻まない。

使い方:
  python scripts/ariadne-backfill-rx-link.py            # dry-run（既定・書き込まない）
  python scripts/ariadne-backfill-rx-link.py --apply    # 書き込み
"""
import os, re, sys, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARI_DIR = os.path.join(REPO, "outputs", "ux", "001_ARIADNE", "001_刑法")
RX_BASE = os.path.join(REPO, "outputs", "ux", "002_RX", "001_刑法")
APPLY = "--apply" in sys.argv

# 想起カード（document順）→ 対応RXコード。None = 刻まない（総論/解法の型/対応RX無し）。
# 2026-06-25 初版（刑法 001-070・全64問・手判定）。新規生成は new-ariadne 側で data-rx を直接付与する。
# 2026-06-25 追補：data-rx 起点が皆無で Lexia supplementJxRx が発火しなかった 刑JX006/011/018/058 に
#   「論点まるごと想起」ブロック（各 RX 論点に対応する想起カード＋data-rx）を追加し起点を確保（取りこぼし解消）。
#   これらの想起カードは生成時に data-rx を直接刻んであるため、本バックフィルでは skip 扱い（冪等）。
MAP = {
 "刑JX001_ARIADNE.html": ["刑RX001_1", "刑RX001_1", None],
 "刑JX002_ARIADNE.html": ["刑RX002_2", "刑RX002_1", None],
 "刑JX003_ARIADNE.html": ["刑RX003_1", "刑RX003_1"],
 "刑JX004_ARIADNE.html": ["刑RX004_2", "刑RX004_1", "刑RX004_1"],
 "刑JX005_ARIADNE.html": ["刑RX005_1", "刑RX005_2", "刑RX005_1"],
 "刑JX006_ARIADNE.html": ["刑RX006_1", "刑RX006_2", "刑RX006_3"],
 "刑JX007_ARIADNE.html": [None, "刑RX007_1", "刑RX007_2"],
 "刑JX008_ARIADNE.html": ["刑RX008_1", "刑RX008_2", "刑RX008_4"],
 "刑JX009_ARIADNE.html": ["刑RX009_1", "刑RX009_3"],
 "刑JX010_ARIADNE.html": ["刑RX010_1", "刑RX010_2"],
 "刑JX011_ARIADNE.html": [None, None, "刑RX011_1", "刑RX011_2"],
 "刑JX012_ARIADNE.html": ["刑RX012_1", "刑RX012_3"],
 "刑JX013_ARIADNE.html": [None, None, "刑RX013_2"],
 "刑JX014_ARIADNE.html": ["刑RX014_1", "刑RX014_1", "刑RX014_2"],
 "刑JX015_ARIADNE.html": ["刑RX015_1", "刑RX015_1", "刑RX015_2"],
 "刑JX016_ARIADNE.html": ["刑RX016_1", "刑RX016_3", "刑RX016_2", "刑RX016_4"],
 "刑JX017_ARIADNE.html": ["刑RX017_1", "刑RX017_2", "刑RX017_4", "刑RX017_3"],
 "刑JX018_ARIADNE.html": ["刑RX018_1", "刑RX018_2", "刑RX018_3", "刑RX018_4"],
 "刑JX019_ARIADNE.html": ["刑RX019_1", "刑RX019_2", "刑RX019_3", "刑RX019_4", "刑RX019_5", "刑RX019_6", "刑RX019_7", "刑RX019_8"],
 "刑JX025_ARIADNE.html": ["刑RX025_2", "刑RX025_1", "刑RX025_3"],
 "刑JX026_ARIADNE.html": [None, "刑RX026_1", "刑RX026_4"],
 "刑JX027_ARIADNE.html": ["刑RX027_1", "刑RX027_2", "刑RX027_3"],
 "刑JX028_ARIADNE.html": [None, None, "刑RX028_2"],
 "刑JX029_ARIADNE.html": ["刑RX029_1", "刑RX029_2", "刑RX029_3"],
 "刑JX030_ARIADNE.html": ["刑RX030_2"],
 "刑JX031_ARIADNE.html": [None, "刑RX031_1", "刑RX031_2"],
 "刑JX032_ARIADNE.html": [None, "刑RX032_1", "刑RX032_2"],
 "刑JX033_ARIADNE.html": ["刑RX033_2", "刑RX033_1", "刑RX033_2"],
 "刑JX034_ARIADNE.html": ["刑RX034_1", "刑RX034_1", "刑RX034_3"],
 "刑JX035_ARIADNE.html": ["刑RX035_2", "刑RX035_1", "刑RX035_3"],
 "刑JX036_ARIADNE.html": ["刑RX036_1", "刑RX036_2", "刑RX036_3"],
 "刑JX037_ARIADNE.html": ["刑RX037_1", "刑RX037_1", "刑RX037_2"],
 "刑JX038_ARIADNE.html": ["刑RX038_1", "刑RX038_1"],
 "刑JX039_ARIADNE.html": ["刑RX039_2", "刑RX039_1", "刑RX039_2"],
 "刑JX040_ARIADNE.html": ["刑RX040_1", "刑RX040_2"],
 "刑JX041_ARIADNE.html": ["刑RX041_1", "刑RX041_2", "刑RX041_4"],
 "刑JX042_ARIADNE.html": ["刑RX042_1", "刑RX042_1", "刑RX042_2"],
 "刑JX043_ARIADNE.html": ["刑RX043_1", "刑RX043_2"],
 "刑JX044_ARIADNE.html": ["刑RX044_1", "刑RX044_2", "刑RX044_3"],
 "刑JX045_ARIADNE.html": ["刑RX045_1", "刑RX045_2", "刑RX045_3"],
 "刑JX046_ARIADNE.html": ["刑RX046_1", "刑RX046_3", "刑RX046_3"],
 "刑JX047_ARIADNE.html": ["刑RX047_1", "刑RX047_2", "刑RX047_1"],
 "刑JX048_ARIADNE.html": ["刑RX048_1", "刑RX048_2", "刑RX048_4"],
 "刑JX049_ARIADNE.html": ["刑RX049_1", "刑RX049_2", "刑RX049_3"],
 "刑JX050_ARIADNE.html": ["刑RX050_1", "刑RX050_2"],
 "刑JX051_ARIADNE.html": ["刑RX051_1", "刑RX051_2"],
 "刑JX052_ARIADNE.html": ["刑RX052_1", "刑RX052_3", "刑RX052_2"],
 "刑JX053_ARIADNE.html": ["刑RX053_2", "刑RX053_3", "刑RX053_4"],
 "刑JX054_ARIADNE.html": ["刑RX054_1", "刑RX054_3", "刑RX054_3"],
 "刑JX055_ARIADNE.html": ["刑RX055_1", "刑RX055_1"],
 "刑JX056_ARIADNE.html": ["刑RX056_1", "刑RX056_2", "刑RX056_2"],
 "刑JX057_ARIADNE.html": [None, "刑RX057_1", "刑RX057_2"],
 "刑JX058_ARIADNE.html": ["刑RX058_1", "刑RX058_2", "刑RX058_3", "刑RX058_4", "刑RX058_5", "刑RX058_6"],
 "刑JX059_ARIADNE.html": [None, None, "刑RX059_1"],
 "刑JX060_ARIADNE.html": [None, "刑RX060_1"],
 "刑JX061_ARIADNE.html": ["刑RX061_1", "刑RX061_3"],
 "刑JX062_ARIADNE.html": ["刑RX062_1", "刑RX062_2", None],
 "刑JX063_ARIADNE.html": ["刑RX063_2", "刑RX063_3"],
 "刑JX064_ARIADNE.html": ["刑RX064_3", "刑RX064_1", "刑RX064_1"],
 "刑JX065_ARIADNE.html": ["刑RX065_1", "刑RX065_2", None],
 "刑JX066_ARIADNE.html": ["刑RX066_1", None, "刑RX066_2"],
 "刑JX067_ARIADNE.html": ["刑RX067_1", "刑RX067_1", None],
 "刑JX068_ARIADNE.html": ["刑RX068_1", "刑RX068_4", None],
 "刑JX069_ARIADNE.html": ["刑RX069_1", "刑RX069_1", "刑RX069_2"],
 "刑JX070_ARIADNE.html": ["刑RX070_2", "刑RX070_1", None],
}

OPEN_RE = re.compile(r'<div\b[^>]*\bclass="[^"]*\bself-check-quiz\b[^"]*"[^>]*>', re.I)


def rx_exists(num, code):
    return os.path.isfile(os.path.join(RX_BASE, f"刑JX{num}", code + ".html"))


def main():
    files_on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(ARI_DIR, "*_ARIADNE.html"))}
    errors = []
    unmapped = files_on_disk - set(MAP)
    if unmapped:
        errors.append(f"MAP未登録のARIADNE: {sorted(unmapped)}")

    plans = []  # (path, new_html, nstamp, nnull, nskip)
    tot_recall = 0
    for fname, codes in MAP.items():
        path = os.path.join(ARI_DIR, fname)
        if not os.path.isfile(path):
            errors.append(f"{fname}: ファイル無し"); continue
        num = re.match(r'^刑JX(\d{3})_', fname).group(1)
        html = open(path, encoding="utf-8", newline="").read()
        recall_tags = [m.group(0) for m in OPEN_RE.finditer(html) if "data-recall" in m.group(0)]
        tot_recall += len(recall_tags)
        if len(recall_tags) != len(codes):
            errors.append(f"{fname}: 想起カード数 {len(recall_tags)} != MAP長 {len(codes)}"); continue
        for c in codes:
            if c and not rx_exists(num, c):
                errors.append(f"{fname}: 参照先RX不在 {c}")
        idx = [0]; n = {"stamp": 0, "null": 0, "skip": 0}

        def repl(m):
            tag = m.group(0)
            if "data-recall" not in tag:
                return tag
            i = idx[0]; idx[0] += 1
            code = codes[i] if i < len(codes) else None
            if not code:
                n["null"] += 1; return tag
            if "data-rx=" in tag:
                n["skip"] += 1; return tag
            n["stamp"] += 1
            return re.sub(r'(data-recall="1")', r'\1 data-rx="' + code + '"', tag, count=1)

        new_html = OPEN_RE.sub(repl, html)
        plans.append((path, new_html, n["stamp"], n["null"], n["skip"]))

    tot_stamp = sum(p[2] for p in plans)
    tot_null = sum(p[3] for p in plans)
    tot_skip = sum(p[4] for p in plans)
    mode = "APPLY" if APPLY else "DRY-RUN"
    print(f"=== {mode} === 対象 {len(plans)}/{len(MAP)} ファイル・想起カード {tot_recall} / "
          f"新規刻む {tot_stamp} / 既存 data-rx skip {tot_skip} / null(省略) {tot_null}")
    if errors:
        print(f"!!! 安全検査 NG（{len(errors)}件）→ 一切書き込まず中止 !!!")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    if APPLY:
        for path, new_html, nstamp, _nn, _ns in plans:
            if nstamp:
                open(path, "w", encoding="utf-8", newline="").write(new_html)
        print("→ 書き込み完了（冪等）")
    else:
        print("→ dry-run（--apply で書き込み）")


if __name__ == "__main__":
    main()
