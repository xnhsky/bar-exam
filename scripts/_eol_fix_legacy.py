# -*- coding: utf-8 -*-
import os
base = r"C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\outputs\000_TX"
files = [
    r"002_刑事訴訟法\刑訴TX001.html",
    r"004_商法\商TX001.html",
    r"007_憲法\憲TX001.html",
    r"003_民法\民TX001.html",
    r"005_民事訴訟法\民訴TX001.html",
    r"006_行政法\行政TX001.html",
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
