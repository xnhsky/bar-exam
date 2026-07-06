# -*- coding: utf-8 -*-
"""目次から 編/章/節 行の『右端ページ番号』を image_to_data で抽出。
リーダー線(………)対策として、行を語トークンに分解し、行末に近い純数字トークンをページ番号として拾う。
出力: UTF-8 で toc_ocr/<name>_pages.tsv  (level<TAB>name_raw<TAB>page)
"""
import sys, io, re, json
import fitz, pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DPI = 450
# name -> 目次ページ範囲(PDFページ, 1始まり)
TOC = {
    "keiso":  (10, 13),
    "kenpo":  (10, 11),
    "minpo1": (10, 11),
    "minpo2": (10, 12),
    "minso":  (10, 13),
    "shoho":  (10, 12),
}

HEAD = re.compile(r'第\s*([0-9０-９一二三四五六七八九十]+)\s*(編|章|節)')

def z2h(s):
    return s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

def extract(name, f, t):
    doc = fitz.open(name + ".pdf")
    mat = fitz.Matrix(DPI/72.0, DPI/72.0)
    rows = []
    for p in range(f, t+1):
        pix = doc[p-1].get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        data = pytesseract.image_to_data(img, lang="jpn", config="--psm 6",
                                         output_type=pytesseract.Output.DICT)
        # group tokens by (block,par,line)
        lines = {}
        n = len(data["text"])
        for i in range(n):
            txt = data["text"][i]
            if txt is None or txt.strip() == "":
                continue
            key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            lines.setdefault(key, []).append((data["left"][i], z2h(txt.strip())))
        for key, toks in lines.items():
            toks.sort(key=lambda x: x[0])
            joined = " ".join(w for _, w in toks)
            m = HEAD.search(joined.replace(" ", ""))
            if not m:
                continue
            # 行末に近い純数字トークン(1-4桁)をページ番号候補に
            page = None
            for _, w in reversed(toks):
                d = re.sub(r"[^0-9]", "", w)
                if re.fullmatch(r"[0-9]{1,4}", w) and 1 <= int(w) <= 2000:
                    page = int(w); break
            rows.append((p, m.group(2), joined, page))
    doc.close()
    return rows

if __name__ == "__main__":
    books = sys.argv[1:] if len(sys.argv) > 1 else list(TOC.keys())
    for b in books:
        f, t = TOC[b]
        rows = extract(b, f, t)
        out = f"toc_ocr/{b}_pages.tsv"
        with open(out, "w", encoding="utf-8") as w:
            for pg, kind, joined, page in rows:
                w.write(f"P{pg}\t{kind}\t{page}\t{joined}\n")
        print(f"{b}: {len(rows)} lines -> {out}")
