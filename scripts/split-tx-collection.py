# -*- coding: utf-8 -*-
"""短答過去問パーフェクト（一括スキャン PDF）を 1 問 = 1 PDF に分割する。

判定ロジック（画像スキャン PDF・テキストなし前提）：
  - 問題ページ＝書籍の右ページかつヘッダー帯（y3〜12%）に幅広グレー帯
    （暗画素率 >=0.55 の行が 2 行以上）を持つページ。
    右ページの PDF 上の偶奇は --start-page の偶奇から決まる
    （--start-page には最初の問題ページを指定する）
  - 解説は問題直後のページから次の問題開始の直前まで
  - 問題 No は左上箱（民法/No.NN）を 400dpi OCR して取得し連番検証

使い方:
  python split-tx-collection.py --probe                                # 全ページ走査して問題候補帯を一覧
  python split-tx-collection.py --start-page 13 --end-page 650          # dry-run（一覧のみ）
  python split-tx-collection.py --start-page 13 --end-page 650 --write  # 分割 PDF を書き出し
"""
import argparse
import os
import re
import subprocess
import tempfile

import fitz

SRC_DIR = r"D:\OneDrive-archive\デスクトップ\TX作成用\民法"
OUT_DIR = SRC_DIR  # 生成物も同じフォルダへ（ユーザー指示）
TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = r"C:\Users\OWNER\bar-exam\_tessdata"


def find_src():
    pdfs = [n for n in os.listdir(SRC_DIR)
            if n.lower().endswith(".pdf") and not re.fullmatch(r"\d+\.pdf", n)]
    assert len(pdfs) == 1, f"source PDF ambiguous: {pdfs}"
    return os.path.join(SRC_DIR, pdfs[0])


def wide_band_rows(page, thresh=0.55):
    """ヘッダー帯（y3〜12%）の幅広暗帯行数"""
    r = page.rect
    clip = fitz.Rect(0, r.height * 0.03, r.width, r.height * 0.12)
    pix = page.get_pixmap(dpi=150, clip=clip, colorspace=fitz.csGRAY)
    w, h = pix.width, pix.height
    buf = pix.samples
    n = 0
    for y in range(h):
        row = buf[y * w:(y + 1) * w]
        if sum(1 for b in row if b < 180) / w >= thresh:
            n += 1
    return n


def ocr_no(page, tmpdir, idx):
    """左上箱（民法 / No.NN）から問題番号を OCR"""
    r = page.rect
    clip = fitz.Rect(r.width * 0.01, r.height * 0.040,
                     r.width * 0.17, r.height * 0.095)
    pix = page.get_pixmap(dpi=400, clip=clip, colorspace=fitz.csGRAY)
    png = os.path.join(tmpdir, f"no{idx}.png")
    pix.save(png)
    env = dict(os.environ, TESSDATA_PREFIX=TESSDATA)
    res = subprocess.run([TESSERACT, png, "stdout", "-l", "jpn+eng", "--psm", "6"],
                         capture_output=True, env=env)
    os.remove(png)
    text = res.stdout.decode("utf-8", errors="replace")
    flat = re.sub(r"\s+", "", text)
    m = re.search(r"[NnＮ][oOｏＯ0]\.?(\d{1,3})", flat)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true",
                    help="全ページの帯行数を一覧表示（範囲決定用・分割なし）")
    ap.add_argument("--end-page", type=int,
                    help="最終解説ページ（索引・広告の直前）")
    ap.add_argument("--start-page", type=int, default=1,
                    help="最初の問題ページ（この偶奇を右ページと見なす）")
    ap.add_argument("--extra-starts", type=str, default="",
                    help="帯検出をすり抜けた問題ページをカンマ区切りで強制追加")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    src = find_src()
    doc = fitz.open(src)

    if args.probe:
        end = args.end_page or doc.page_count
        print(f"probe: {os.path.basename(src)} p{args.start_page}-p{end}")
        for i in range(args.start_page - 1, end):
            n = wide_band_rows(doc[i])
            if n >= 2:
                print(f"  p{i+1:4d} ({'odd' if (i+1) % 2 else 'even'}) rows={n}")
        return

    assert args.end_page, "--end-page を指定してください"
    print(f"source: {os.path.basename(src)} ({doc.page_count} pages), "
          f"range p{args.start_page}-p{args.end_page}")

    # 1) 問題開始ページ検出（編扉バーで帯が縮むケースがあるため >=2 行で判定）
    right_parity = args.start_page % 2  # 右ページの偶奇
    starts = []
    for i in range(args.start_page - 1, args.end_page):
        p = i + 1
        if p % 2 != right_parity:
            continue
        if wide_band_rows(doc[i]) >= 2:
            starts.append(i)
        if p % 100 == 1 and p > 1:
            print(f"  ... scanned to p{p}, starts so far {len(starts)}")
    if args.extra_starts:
        extra = [int(x) - 1 for x in args.extra_starts.split(",")]
        starts = sorted(set(starts) | set(extra))
    print(f"problem starts: {len(starts)}")

    # 2) グループ化＋No OCR
    groups = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for k, first in enumerate(starts):
            last = starts[k + 1] - 1 if k + 1 < len(starts) else args.end_page - 1
            no = ocr_no(doc[first], tmpdir, k)
            groups.append({"seq": k + 1, "first": first, "last": last, "no": no})

    # 3) 検証＋一覧
    warns = []
    prev = None
    for g in groups:
        npg = g["last"] - g["first"] + 1
        if npg < 2 or npg > 8:
            warns.append(f"seq {g['seq']} (p{g['first']+1}): ページ数異常 {npg}")
        if g["no"] is None:
            warns.append(f"seq {g['seq']} (p{g['first']+1}): No 読取不能")
        elif prev is not None and int(g["no"]) != prev + 1:
            warns.append(f"seq {g['seq']} (p{g['first']+1}): No非連続 "
                         f"{prev} → {g['no']}")
        if g["no"]:
            prev = int(g["no"])

    first_no = int(groups[0]["no"]) if groups[0]["no"] else None
    report = [f"# 分割一覧（{os.path.basename(src)}）", "",
              f"対象 p{args.start_page}–p{args.end_page} → {len(groups)} 問",
              f"書籍No範囲: No.{groups[0]['no']} 〜 No.{groups[-1]['no']}",
              "推定No = 先頭No + 連番（OCR 不読・誤読の補完用）", "",
              "| 出力 | 推定No | OCR読取No | 元ページ | ページ数 |",
              "|---|---|---|---|---|"]
    for g in groups:
        est = first_no + g["seq"] - 1 if first_no else "?"
        report.append(f"| {g['seq']}.pdf | No.{est} | {g['no'] or '?'} "
                      f"| p{g['first']+1}–p{g['last']+1} | {g['last']-g['first']+1} |")
    if warns:
        report += ["", "## 要確認", ""] + [f"- {w}" for w in warns]
    rpt = os.path.join(OUT_DIR, "_分割一覧.md")
    with open(rpt, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"groups={len(groups)} warnings={len(warns)} -> {rpt}")
    for w in warns:
        print("  [WARN]", w)

    # 4) 書き出し
    if args.write:
        for g in groups:
            out = fitz.open()
            out.insert_pdf(doc, from_page=g["first"], to_page=g["last"])
            path = os.path.join(OUT_DIR, f"{g['seq']}.pdf")
            out.save(path, garbage=3, deflate=True)
            out.close()
            if g["seq"] % 50 == 0:
                print(f"  wrote {g['seq']}.pdf ...")
        print(f"done: {len(groups)} files -> {OUT_DIR}")


if __name__ == "__main__":
    main()
