# -*- coding: utf-8 -*-
"""各 N.pdf の No箱を堅牢OCR（多clip/多dpi/2値化/psm）。file->No 表を outfile に。"""
import fitz, os, sys, subprocess, re, tempfile, glob
from PIL import Image
folder, outfile = sys.argv[1], sys.argv[2]
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = r"C:\Users\OWNER\bar-exam\_tessdata"
env = dict(os.environ, TESSDATA_PREFIX=TESSDATA)

def tess(png, psm, whitelist=None):
    cmd = [TESS, png, "stdout", "-l", "jpn+eng", "--psm", psm]
    if whitelist: cmd += ["-c", f"tessedit_char_whitelist={whitelist}"]
    return subprocess.run(cmd, capture_output=True, env=env).stdout.decode("utf-8","replace")

def read_no(pg, tmp):
    r = pg.rect
    # 複数の縦位置（通常/編扉ずれ）×dpi
    for (yy0, yy1) in [(0.035,0.16),(0.07,0.185),(0.10,0.205)]:
        clip = fitz.Rect(r.width*0.015, r.height*yy0, r.width*0.165, r.height*yy1)
        for dpi in (450, 650):
            pix = pg.get_pixmap(dpi=dpi, clip=clip, colorspace=fitz.csGRAY)
            png = os.path.join(tmp, "n.png"); pix.save(png)
            for psm in ("6","11","4","7"):
                flat = re.sub(r"\s+","", tess(png, psm))
                m = re.search(r"[NnＮ][oOaＯ0O０-９0-9]\.?(\d{1,4})", flat)
                if m: return int(m.group(1))
            # 2値化して数字専用（下半分＝No行）
            im = Image.open(png).convert("L")
            w,h = im.size
            low = im.crop((0, int(h*0.4), w, h)).resize((w*2, int(h*1.2)))
            low = low.point(lambda x: 0 if x<150 else 255)
            bp = os.path.join(tmp, "b.png"); low.save(bp)
            for psm in ("7","8"):
                d = re.sub(r"\s+","", tess(bp, psm, whitelist="0123456789No."))
                m = re.search(r"[No]{1,2}\.?(\d{1,4})", d) or re.search(r"(\d{1,4})", d)
                if m and m.group(1): return int(m.group(1))
    return None

files = sorted(int(re.match(r'(\d+)\.pdf',os.path.basename(p)).group(1))
               for p in glob.glob(f"{folder}/*.pdf") if re.fullmatch(r'\d+\.pdf',os.path.basename(p)))
res=[]
with tempfile.TemporaryDirectory() as tmp:
    for i,fn in enumerate(files):
        d=fitz.open(os.path.join(folder,f"{fn}.pdf")); no=read_no(d[0],tmp); d.close()
        res.append((fn,no))
        if (i+1)%50==0: print(f"  ...{i+1}/{len(files)}", flush=True)
read=sum(1 for _,n in res if n)
lines=[f"# {folder}", f"files={len(files)} read={read} ({100*read//len(files)}%)"]
lines+=[f"{fn}\t{no}" for fn,no in res]
open(outfile,"w",encoding="utf-8").write("\n".join(lines))
print(f"done read={read}/{len(files)} -> {outfile}")
