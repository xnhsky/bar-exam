# -*- coding: utf-8 -*-
"""柱スキャン結果(<name>_headers.jsonl)から章別カバレッジ topic-map を作る。
方式:
- 柱の 編/章 は「名前」でツリーにマッチ(番号はOCR誤読が多いため不使用)。編indexは前進のみ許可。
- 各ページを (編,章) ノードへ割当て。No.通し番号の (page,No) を単調補間(外れ値 no>page は除外)。
- 各ページの No 増分をそのページのノードに積算 → 章ごと問題数(近似)。合計は総No数に一致。
- ツリーの全最下位ノード(章 or 編止まり)を coverage に載せ、0件の章も「穴」として明示。
出力: references/topic-map/<subject>.json
"""
import json, os, re
from difflib import SequenceMatcher
from collections import defaultdict

# ★ 柱スキャン結果 toc_ocr/*_headers.jsonl がある作業ディレクトリ(run_all_scans.py の DATA_DIR と一致)
SCRATCH = r"C:\Users\xnrg2.DESKTOP-5664QR6\AppData\Local\Temp\claude\C--Users-xnrg2-DESKTOP-5664QR6\7d7b8729-a15f-47d6-ae1e-017a26b3e582\scratchpad"
TOPICS  = r"C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\references\topics"
OUTDIR  = r"C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam\references\topic-map"

# subject -> [(jsonl名, その巻の開始編番号)]。民法は2巻(minpo1=第1編〜, minpo2=第4編〜)。
BOOKS = {
    "刑事訴訟法": [("keiso", 1)],
    "憲法":       [("kenpo", 1)],
    "民法":       [("minpo1", 1), ("minpo2", 4)],
    "民事訴訟法": [("minso", 1)],
    "商法":       [("shoho", 1)],
}

def norm(s):
    return re.sub(r'[\s（）\(\)・,、。／/]', '', s or '')

def ratio(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()

def interp(anchors):
    """(page,No) を no<=page で粗く外れ値除去→最長非減少部分列(LNDS)で整形→線形補間関数。
    LNDSにより単一の外れ値(例 130の列に紛れた186)が長い正しい列を殺すのを防ぐ。"""
    pts = sorted((p, n) for p, n in anchors if n <= p)
    if not pts:
        return (lambda page: 0), []
    nos = [n for _, n in pts]
    N = len(nos); dp = [1]*N; par = [-1]*N
    for i in range(N):
        for j in range(i):
            if nos[j] <= nos[i] and dp[j]+1 > dp[i]:
                dp[i] = dp[j]+1; par[i] = j
    i = max(range(N), key=lambda k: dp[k]); idx = []
    while i != -1:
        idx.append(i); i = par[i]
    idx.reverse()
    clean = [pts[k] for k in idx]
    def f(page):
        if not clean: return 0
        if page <= clean[0][0]: return clean[0][1]
        if page >= clean[-1][0]: return clean[-1][1]
        for i in range(1, len(clean)):
            if clean[i][0] >= page:
                (p0, n0), (p1, n1) = clean[i-1], clean[i]
                return n0 + (n1-n0)*(page-p0)/(p1-p0) if p1 != p0 else n1
        return clean[-1][1]
    return f, clean

def load_tree(subject):
    tree = json.load(open(os.path.join(TOPICS, subject+".json"), encoding="utf-8"))["tree"]
    # グローバル・リーフ順序(章、章なし編は編自身)。柱の編番号はOCR誤読が多いため使わない。
    leaves = []
    for i, top in enumerate(tree):
        chapters = [c for c in top.get("children", []) if c.get("kind") == "章"]
        if chapters:
            for c in chapters:
                leaves.append({"id": c["id"], "name": c["name"], "hen": i+1, "hleaf": False})
        else:
            # 章なし編は編自身がリーフ。柱の編名(hen)でのみ検出する。
            leaves.append({"id": top["id"], "name": top["name"], "hen": i+1, "hleaf": True})
    return tree, leaves

WINDOW = 11   # 現在位置から前方何リーフまで一致を探すか(最大章数=商法機関11節に対応)

def assign_pages(vol, leaves, start_pos=0):
    """章名/編名の観測をグローバル・リーフ順序へ前進のみで整列し {page: node_id} を返す。
    start_pos: この巻が始まるリーフindex(民法2巻目は第4編先頭から)。"""
    page_node = {}
    pos = start_pos
    started = False
    for r in vol:
        p = r["p"]
        sho_raw = r["sho"][1] if ("sho" in r and r["sho"][1]) else None
        hen_nm = r["hen"][1] if ("hen" in r and r["hen"][1]) else None
        # 柱の章名は「章名/節名…」形式。/前の章名部分でもマッチさせる(節サフィックスで薄まるのを防ぐ)
        sho_cands = None
        if sho_raw:
            sho_cands = [sho_raw, sho_raw.split("/")[0]]
        if sho_cands or hen_nm:
            best_j = None; best_r = 0.0
            hi = min(len(leaves), pos + 1 + WINDOW)
            for j in range(pos, hi):
                lf = leaves[j]
                # 章名は章リーフのみ、編名は章なし編リーフのみに一致させる(部分一致の誤ジャンプ防止)
                cands = [hen_nm] if lf["hleaf"] else sho_cands
                cands = [c for c in (cands or []) if c]
                if not cands:
                    continue
                lr = max(ratio(nm, lf["name"]) for nm in cands)
                # 編リーフ(総合問題/裁判の執行等)への編名マッチは高閾値。
                # 非リーフ編名の部分一致(例「裁判」→「裁判の執行」0.57)による誤ジャンプを防ぐ。
                thr = 0.72 if lf["hleaf"] else 0.5
                if lr >= thr and lr > best_r:
                    best_r = lr; best_j = j
            if best_j is not None:
                pos = best_j; started = True
        if started:
            page_node[p] = leaves[pos]["id"]
    return page_node

def build(subject, names):
    tree, leaves = load_tree(subject)
    # 全リーフの下地(0件)
    leaf_meta = {lf["id"]: {"node": lf["id"], "name": lf["name"], "hen": lf["hen"]}
                 for lf in leaves}
    est = defaultdict(float)
    src_by = defaultdict(list)
    total = 0
    for nm, start_hen in names:
        start_pos = next((i for i, lf in enumerate(leaves) if lf["hen"] == start_hen), 0)
        vol = [json.loads(l) for l in open(os.path.join(SCRATCH, "toc_ocr", f"{nm}_headers.jsonl"), encoding="utf-8")]
        anchors = [(r["p"], no) for r in vol if "no" in r for no in r["no"]]
        # 先頭合成アンカー: 本文冒頭付近に No.1 があるとみなし、最初のアンカー前の
        # フラット化(序論等がest=0になる)を防ぐ。
        if vol:
            anchors.append((min(r["p"] for r in vol), 1))
        f, clean = interp(anchors)
        total += clean[-1][1] if clean else 0
        page_node = assign_pages(vol, leaves, start_pos)
        # No増分をページのノードへ積算
        prev = None
        for r in vol:
            p = r["p"]; cur = f(p)
            if prev is not None:
                nid = page_node.get(p)
                if nid is not None:
                    est[nid] += max(0.0, cur - prev)
            prev = cur
        # src をノードへ
        for r in vol:
            if "src" in r:
                nid = page_node.get(r["p"])
                if nid:
                    for s in r["src"]:
                        if s not in src_by[nid] and len(src_by[nid]) < 6:
                            src_by[nid].append(s)
    coverage = {}
    for nid, meta in leaf_meta.items():
        coverage[nid] = {**meta,
                         "problems_est": round(est.get(nid, 0)),
                         "src_samples": src_by.get(nid, [])}
    out = {
        "meta": {
            "subject": subject,
            "generatedBy": "scan_headers.py 柱スキャン + 編/章名マッチ + No(page)単調補間",
            "treeVersion": "v0-draft",
            "note": "TX素材が無いため過去問IDではなく短パフェ本文の章別問題数(概算)でカバレッジを表す。problems_est は No.通し番号のpage補間による近似値。src_samples は柱OCRで拾えた出典のみ。problems_est=0 は出題の薄い(または柱OCR未捕捉の)章。",
            "totalProblems_est": total,
        },
        "coverage": coverage,
    }
    json.dump(out, open(os.path.join(OUTDIR, subject+".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    psum = sum(c["problems_est"] for c in coverage.values())
    zero = sum(1 for c in coverage.values() if c["problems_est"] == 0)
    print(f"{subject}: leaf={len(coverage)} est合計={psum} total~{total} 0件章={zero}")

if __name__ == "__main__":
    import sys
    for sub in (sys.argv[1:] or list(BOOKS.keys())):
        try:
            build(sub, BOOKS[sub])
        except Exception:
            import traceback; print(f"{sub}: ERROR"); traceback.print_exc()
