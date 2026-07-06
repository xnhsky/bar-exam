# -*- coding: utf-8 -*-
"""本文の上部ストリップだけOCRして、各ページの 柱(編/章/印刷ページ) と
問題マーカー(No.N + 出典 + タイトル) を拾い、問題→章 の対応表(JSONL)を作る。
使い方: python extract_problems.py <name> <from_page> <to_page>
出力: toc_ocr/<name>_probs.jsonl  (1行=1ページの解析結果)
"""
import sys, io, re, json
import fitz, pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DPI = 300
STRIP = 0.16   # 上部16%

reHEN  = re.compile(r'第\s*([0-9０-９一二三四五六七八九十]+)\s*編\s*([^\d\s].{0,20})')
reSHO  = re.compile(r'第\s*([0-9０-９一二三四五六七八九十]+)\s*章\s*([^\d\s].{0,20})')
reNO   = re.compile(r'(?:No|Ne|Mo|Mg|Ma|Na|N[o0])\.?\s*([0-9]{1,3})')
rePAGE = re.compile(r'(?:画|回|墨|盟|副|田|闘|國|品|正)\s*([0-9]{1,4})')
# 出典: 予備R1-14 / 司法H30-10 / 予備独自 / R\d / H\d\d
reSRC  = re.compile(r'(予備[^\s]{0,6}|司法[^\s]{0,6}|[RHrh]\s*[0-9]{1,2}\s*[-ー―]\s*[0-9]{1,3})')

Z2H = str.maketrans("０１２３４５６７８９", "0123456789")
KANJI = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}

def num(s):
    s = s.translate(Z2H)
    if s.isdigit(): return int(s)
    return KANJI.get(s)

def run(name, f, t):
    doc = fitz.open(name + ".pdf")
    mat = fitz.Matrix(DPI/72.0, DPI/72.0)
    out = f"toc_ocr/{name}_probs.jsonl"
    hi = min(t, doc.page_count)
    with open(out, "w", encoding="utf-8") as w:
        for p in range(f, hi+1):
            page = doc[p-1]
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ww, hh = img.size
            strip = img.crop((0, 0, ww, int(hh*STRIP)))
            txt = pytesseract.image_to_string(strip, lang="jpn", config="--psm 6")
            flat = txt.replace(" ", "")
            rec = {"p": p}
            mh = reHEN.search(flat)
            if mh: rec["hen"] = [num(mh.group(1)), mh.group(2).strip()]
            ms = reSHO.search(flat)
            if ms: rec["sho"] = [num(ms.group(1)), ms.group(2).strip()]
            mp = rePAGE.search(flat)
            if mp: rec["pp"] = int(mp.group(1))
            nos = [int(x) for x in reNO.findall(flat)]
            if nos: rec["no"] = sorted(set(nos))
            src = reSRC.findall(txt)
            if src: rec["src"] = [s.strip() for s in src][:3]
            # タイトル候補: No行の後続テキスト(生txtの最初の非空行でNoを含む行)
            for line in txt.splitlines():
                if reNO.search(line.replace(" ", "")):
                    rec["noline"] = line.strip()[:60]
                    break
            w.write(json.dumps(rec, ensure_ascii=False) + "\n")
    doc.close()
    print(f"{name}: P{f}-{hi} -> {out}")

if __name__ == "__main__":
    name = sys.argv[1]
    f = int(sys.argv[2]); t = int(sys.argv[3])
    run(name, f, t)
