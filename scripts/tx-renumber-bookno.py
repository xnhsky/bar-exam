# -*- coding: utf-8 -*-
"""file->書籍No 確定。方針:
 - 確信読取 = バンド内(0<=read-pos<=maxdrift)の多桁読取（桁落ち/ゴミ除外）。箱を信頼＝順序外もそのまま。
 - パッチ(手動確定) を最優先で上書き。
 - 非確信ファイルは drift=No-pos を左右の確信値から補間（同一driftなら確定／段差跨ぎはAMBIGUOUS）。
 - 重複No・非単調(順序外以外)・AMBIGUOUS を列挙 → 目視確定へ。
 - 全解消かつ重複0で --apply。
使い方: python renumber2.py <folder> <ocr.txt> [--first-no N] [--patch p.tsv] [--max-drift M] [--apply]
"""
import sys, os, re, glob, collections
folder, ocrfile = sys.argv[1], sys.argv[2]
first_no=None; patch={}; maxdrift=15; apply="--apply" in sys.argv
for i,a in enumerate(sys.argv):
    if a=="--first-no": first_no=int(sys.argv[i+1])
    if a=="--max-drift": maxdrift=int(sys.argv[i+1])
    if a=="--patch":
        for ln in open(sys.argv[i+1],encoding="utf-8"):
            m=re.match(r'^(\d+)\s+(\d+)',ln.strip())
            if m: patch[int(m.group(1))]=int(m.group(2))
raw={}
for ln in open(ocrfile,encoding="utf-8"):
    m=re.match(r'^(\d+)\t(\d+|None)$',ln.strip())
    if m: raw[int(m.group(1))]=None if m.group(2)=="None" else int(m.group(2))
files=sorted(raw); base=files[0]-1
if first_no is not None: patch.setdefault(files[0], first_no)

# 確信読取
conf={}
for f in files:
    if f in patch: conf[f]=patch[f]; continue
    r=raw[f]
    if r is not None and r>=10 and 0<=(r-(f-base))<=maxdrift: conf[f]=r
# 補間: 各非確信fに対し左右の確信を探し drift 補間
cf=sorted(conf)
assign=dict(conf); amb=[]
import bisect
for f in files:
    if f in conf: continue
    j=bisect.bisect_left(cf,f)
    L=cf[j-1] if j>0 else None; R=cf[j] if j<len(cf) else None
    dL=conf[L]-L if L else None; dR=conf[R]-R if R else None
    if dL is not None and dR is not None:
        if dL==dR: assign[f]=f+dL
        else: assign[f]=f+dL; amb.append((f,L,conf[L],R,conf[R]))
    elif dL is not None: assign[f]=f+dL
    elif dR is not None: assign[f]=f+dR
vals=[assign[f] for f in files]
dup=collections.Counter(vals); dups={v:[f for f in files if assign[f]==v] for v,c in dup.items() if c>1}
# 非単調（順序外の可能性）: assign[f]<=assign[prev]
nonmono=[files[i] for i in range(1,len(files)) if assign[files[i]]<=assign[files[i-1]]]
print(f"files={len(files)} 確信={len(conf)} パッチ={len(patch)} 補間={len(files)-len(conf)}")
print(f"file{files[0]}->{assign[files[0]]}  file{files[-1]}->{assign[files[-1]]}")
print(f"重複No={len(dups)}  AMBIGUOUS補間={len(amb)}  非単調点={len(nonmono)}")
for v,fs in list(dups.items())[:30]: print(f"  重複 No.{v} <- files {fs}")
for a in amb[:30]: print(f"  AMB file{a[0]}: L=file{a[1]}(No{a[2]}) R=file{a[3]}(No{a[4]})")
for f in nonmono[:30]: print(f"  非単調 file{f}=No{assign[f]} (前file No{assign[f-1] if f-1 in assign else '?'})")
mapfile=ocrfile.replace(".txt","_map2.tsv")
open(mapfile,"w",encoding="utf-8").write("\n".join(f"{f}\t{assign[f]}" for f in files))
print("map ->",mapfile)
if apply:
    if dups or amb:
        print("！重複/AMBIGUOUS 未解消のため apply 中止"); sys.exit(1)
    for f in files: os.rename(os.path.join(folder,f"{f}.pdf"),os.path.join(folder,f"tmp_{f}.pdf"))
    for f in files: os.rename(os.path.join(folder,f"tmp_{f}.pdf"),os.path.join(folder,f"{assign[f]}.pdf"))
    print(f"renamed {len(files)} files")
