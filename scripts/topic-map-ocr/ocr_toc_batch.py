# -*- coding: utf-8 -*-
"""前付けOCR: 各PDFの指定ページ範囲を rasterize -> tesseract(jpn) で読み、
UTF-8 で直接ファイル出力する(stdout経由の文字化けを回避)。
出力: toc_ocr/<name>_p{f}-{t}_{dpi}.txt  各ページ ===== P{n} ===== 区切り。
"""
import os, io, sys, time
import fitz
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "toc_ocr")
os.makedirs(OUT, exist_ok=True)

DPI = 350
FROM, TO = 6, 20
LANG = "jpn"
CFG = "--psm 6"

# name -> subject (民法は1・2巻)
BOOKS = ["keiso", "kenpo", "minpo1", "minpo2", "minso", "shoho"]

def ocr_book(name):
    pdf = os.path.join(BASE, name + ".pdf")
    if not os.path.exists(pdf):
        return f"{name}: PDF NOT FOUND"
    doc = fitz.open(pdf)
    zoom = DPI / 72.0
    mat = fitz.Matrix(zoom, zoom)
    out_path = os.path.join(OUT, f"{name}_p{FROM}-{TO}_{DPI}.txt")
    hi = min(TO, doc.page_count)
    with open(out_path, "w", encoding="utf-8") as w:
        for p in range(FROM, hi + 1):
            page = doc[p - 1]
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            txt = pytesseract.image_to_string(img, lang=LANG, config=CFG)
            w.write("===== P%d =====\n" % p)
            w.write(txt.strip() + "\n")
            w.flush()
    doc.close()
    return f"{name}: wrote {out_path} (P{FROM}-{hi})"

if __name__ == "__main__":
    books = sys.argv[1:] if len(sys.argv) > 1 else BOOKS
    log = os.path.join(OUT, "_progress.log")
    with open(log, "a", encoding="utf-8") as lg:
        for b in books:
            t0 = time.time()
            try:
                msg = ocr_book(b)
            except Exception as e:
                msg = f"{b}: ERROR {e!r}"
            line = f"[{int(time.time())}] {msg} ({time.time()-t0:.0f}s)\n"
            lg.write(line); lg.flush()
    with open(os.path.join(OUT, "_DONE"), "w", encoding="utf-8") as d:
        d.write("done\n")
