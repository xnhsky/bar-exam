# -*- coding: utf-8 -*-
"""指定fileのNo箱を縦に並べたモンタージュ画像を作る（目視確定用）。"""
import fitz, os, sys, glob, re
from PIL import Image, ImageDraw
folder = sys.argv[1]
nums = []
for part in sys.argv[2].split(","):
    if "-" in part:
        a,b=part.split("-"); nums+=list(range(int(a),int(b)+1))
    else: nums.append(int(part))
out = sys.argv[3]
tiles=[]
for fn in nums:
    p=os.path.join(folder,f"{fn}.pdf")
    if not os.path.exists(p): continue
    d=fitz.open(p); pg=d[0]; r=pg.rect
    clip=fitz.Rect(0, r.height*0.03, r.width*0.30, r.height*0.16)
    pix=pg.get_pixmap(dpi=130, clip=clip)
    img=Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
    # ラベル帯
    lab=Image.new("RGB",(90,img.height),(240,240,240))
    dr=ImageDraw.Draw(lab); dr.text((5,img.height//2-6), f"file{fn}", fill=(200,0,0))
    row=Image.new("RGB",(lab.width+img.width, img.height),(255,255,255))
    row.paste(lab,(0,0)); row.paste(img,(lab.width,0))
    tiles.append(row); d.close()
W=max(t.width for t in tiles); H=sum(t.height for t in tiles)
mont=Image.new("RGB",(W,H),(255,255,255)); y=0
for t in tiles: mont.paste(t,(0,y)); y+=t.height
mont.save(out); print("saved",out,mont.size)
