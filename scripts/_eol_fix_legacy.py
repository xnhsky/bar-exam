# -*- coding: utf-8 -*-
import os
base = r"C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\outputs\tx"
files = [
    r"刑訴TX\刑訴TX001.html",
    r"商TX\商TX001.html",
    r"憲TX\憲TX001.html",
    r"民TX\民TX001.html",
    r"民訴TX\民訴TX001.html",
    r"行政TX\行政TX001.html",
]
for f in files:
    p = os.path.join(base, f)
    data = open(p, "rb").read()
    fixed = data.replace(b"\r\n", b"\n")
    if fixed != data:
        open(p, "wb").write(fixed)
        print("LF normalized:", f)
    else:
        print("already LF:", f)
