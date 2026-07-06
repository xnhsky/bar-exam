# -*- coding: utf-8 -*-
"""柱スキャン: 本文の各ページ上部ストリップをOCRし、編/章/印刷ページ/問題No/出典を拾う。
問題は No.N が通し番号なので、章境界と各章のNo範囲から問題数を後段で算出する。
出力: toc_ocr/<name>_headers.jsonl (1行=1ページ), 進捗は toc_ocr/_scan_progress.log
使い方: python scan_headers.py <name> <from> <to>   (省略時は全ページ)
"""
import sys, io, re, json, time
import fitz, pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DPI = 260
STRIP = 0.15

# 番号非依存(番号が「ら」等に誤OCRされても章/編名を捕捉する)。group(1)=名前。
reHEN = re.compile(r'第[^\s編]{0,3}編([^\d\s（(]{1,24})')
reSHO = re.compile(r'第[^\s章]{0,3}章([^\d\s（(]{1,24})')
reNO  = re.compile(r'(?:No|N[o0]|Ne|Mo|Mg|Ma|Na)\.?\s*([0-9]{1,3})')
rePP  = re.compile(r'(?:画|回|墨|盟|副|田|闘|國|品|串|早|嘆|時|置|闇)\s*([0-9]{1,4})')
reLEAD_PP = re.compile(r'^\s*([0-9]{1,4})\s*(?:画|回|墨|盟|副|田|闘|國|品|正)')
reSRC = re.compile(r'(予備[^\s]{0,4}|司法[^\s]{0,4}|[RHrh]\s?[0-9]{1,2}\s?[-ー―]\s?[0-9]{1,3})')

Z2H = str.maketrans("０１２３４５６７８９", "0123456789")
KAN = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}

def num(s):
    s = s.translate(Z2H)
    if s.isdigit(): return int(s)
    return KAN.get(s)

def clean_name(s):
    # 柱の末尾ページマーカー以降を落とす
    s = re.split(r'[画回墨盟副田闘國品串早嘆時置闇\d]', s)[0]
    return s.strip()

def run(name, f, t):
    doc = fitz.open(name + ".pdf")
    mat = fitz.Matrix(DPI/72.0, DPI/72.0)
    hi = min(t, doc.page_count)
    out = f"toc_ocr/{name}_headers.jsonl"
    t0 = time.time()
    with open(out, "w", encoding="utf-8") as w:
        for p in range(f, hi+1):
            pix = doc[p-1].get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ww, hh = img.size
            strip = img.crop((0, 0, ww, int(hh*STRIP)))
            txt = pytesseract.image_to_string(strip, lang="jpn", config="--psm 6")
            flat = txt.replace(" ", "")
            rec = {"p": p}
            mh = reHEN.search(flat)
            if mh: rec["hen"] = [None, clean_name(mh.group(1))]
            ms = reSHO.search(flat)
            if ms: rec["sho"] = [None, clean_name(ms.group(1))]
            mp = rePP.search(flat) or reLEAD_PP.search(txt.strip())
            if mp:
                try: rec["pp"] = int(mp.group(1))
                except: pass
            nos = sorted(set(int(x) for x in reNO.findall(flat)))
            if nos: rec["no"] = nos
            src = [s.strip() for s in reSRC.findall(txt)]
            if src: rec["src"] = src[:2]
            w.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if p % 50 == 0:
                with open("toc_ocr/_scan_progress.log", "a", encoding="utf-8") as lg:
                    lg.write(f"[{int(time.time())}] {name} P{p}/{hi} ({(time.time()-t0)/(p-f+1):.2f}s/p)\n")
    doc.close()
    with open("toc_ocr/_scan_progress.log", "a", encoding="utf-8") as lg:
        lg.write(f"[{int(time.time())}] {name} DONE P{f}-{hi} total {(time.time()-t0):.0f}s\n")

if __name__ == "__main__":
    name = sys.argv[1]
    f = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    t = int(sys.argv[3]) if len(sys.argv) > 3 else 99999
    run(name, f, t)
