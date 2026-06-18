#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学説・見解適用型 TX に「前提見解の原文再掲ブロック（.choice-premise）」を各記述の冒頭へ挿入。
PART A の見解定義を要約せず原文どおり複製し、記述に入った瞬間に前提を確認できるようにする（遡読防止）。

使い方：
  python scripts/add-choice-premise.py                 # dry-run（全候補レポート・書換なし）
  python scripts/add-choice-premise.py --apply          # CONFIDENT を一括挿入
  python scripts/add-choice-premise.py <file> [--apply] # 単一ファイル
要件： pip install beautifulsoup4
"""
import re, sys, glob, os
from bs4 import BeautifulSoup, NavigableString

CSS_BLOCK = """
/* === choice-premise（学説問題：各記述が前提とする見解を冒頭に原文再掲＝遡読防止）=== */
.choice-premise{ background:var(--accent-3); border:1px solid var(--border-mid); border-left:5px solid var(--accent);
  border-radius:8px; padding:14px 18px 13px 20px; margin:0 0 20px; line-height:1.9;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.choice-premise .cp-head{ display:inline-block; font-family:var(--font-mono); font-size:.72rem; font-weight:700;
  letter-spacing:.12em; color:#fff; background:linear-gradient(135deg,var(--accent),var(--accent-darker));
  padding:3px 10px 2px; border-radius:3px; margin-bottom:9px; box-shadow:0 1px 2px rgba(var(--accent-rgb),.25); }
.choice-premise .cp-title{ font-family:var(--font-soft); font-weight:700; color:var(--bg-dark); font-size:1.0em;
  letter-spacing:.02em; margin:0 0 6px; }
.choice-premise .cp-title + .cp-title, .choice-premise .cp-body + .cp-title{ margin-top:12px; }
.choice-premise .cp-body{ margin:0; font-family:var(--font-quote); font-weight:500; font-size:.95em; color:var(--text); }
"""

# 全角英大文字→半角（ラベル正規化）
FW = {chr(0xFF21+i): chr(0x41+i) for i in range(26)}
def half(s):
    return "".join(FW.get(c, c) for c in (s or ""))
def norm(s):
    return half(re.sub(r"\s+", "", s or ""))

LABEL_CHARS = "A-Za-zＡ-Ｚａ-ｚ甲乙丙丁"
# 見解見出しの先頭パターン（label を group 'lbl' で）
LEAD = re.compile(rf"^\s*(?:【?\s*見解\s*([{LABEL_CHARS}])\s*】?|【?\s*([{LABEL_CHARS}])\s*説)")

def view_label_from_text(t):
    m = LEAD.match(t)
    if not m:
        return ""
    return half(m.group(1) or m.group(2) or "")

def extract_views(soup):
    """PART A から {label: {'title','body'}} を抽出（複数レイアウト対応）。"""
    pa = soup.find(id="part-a")
    if not pa:
        return {}
    views = {}

    def add(lbl, title, body):
        lbl = norm(lbl)
        if not lbl or len(lbl) > 2:
            return
        if lbl in views:
            return
        views[lbl] = {"title": (title or "").strip(), "body": (body or "").strip()}

    # 共有ガード：【記述】見出し位置 rec_idx より前のみ見解候補／記述本文と一致するものは除外
    order = pa.find_all(True)
    rec_idx = len(order)
    for i, el in enumerate(order):
        if el.name in ("h2", "h3", "h4") and re.search(r"【?\s*記述", el.get_text()):
            rec_idx = i
            break
    pos = {id(el): i for i, el in enumerate(order)}
    rec_texts = set()
    for s in soup.find_all("section", class_="choice-section"):
        so = s.find(class_="syn-orig")
        if so:
            rec_texts.add(norm(re.sub(r"^📜\s*記述原文\s*", "", so.get_text(" ", strip=True))))

    def is_record(el):
        if pos.get(id(el), 0) >= rec_idx:
            return True
        n = norm(el.get_text(" ", strip=True))
        return any(n == rt or (len(rt) > 12 and rt in n) for rt in rec_texts)

    # title = ラベル見出し（【見解X】/X説）＋（説名）または ── 説名（説名は空白・句読点で打ち切り）
    HEAD_RE = rf"((?:【?\s*見解\s*[{LABEL_CHARS}]\s*】?|【?\s*[{LABEL_CHARS}]\s*説\s*】?)(?:[（(][^）)]*[）)]|\s*[─――—-]+\s*[^\s「。、（(]{{0,14}})?)\s*(.*)"

    # 1) case-scene 型
    scenes = pa.select(".case-scene")
    for sc in scenes:
        paras = sc.find_all(class_="case-paragraph")
        title_el = sc.find(class_="case-scene-title")
        # 1a) 1 scene 内に複数 case-paragraph で各説（X説：… / 【見解X】… ）
        per_para = [(view_label_from_text(p.get_text(" ", strip=True)), p) for p in paras]
        labeled = [(l, p) for l, p in per_para if l]
        if len(labeled) >= 2:
            for l, p in labeled:
                add(l, "", p.get_text(" ", strip=True))
            continue
        # 1b) scene 全体が 1 説（case-scene-num or title 先頭がラベル）
        num = sc.find(class_="case-scene-num")
        body = "\n".join(p.get_text(" ", strip=True) for p in paras)
        ttxt = (title_el.get_text(" ", strip=True) if title_el else "")
        if not re.search(r"説|見解", ttxt + body):
            continue
        lbl = view_label_from_text(ttxt) or (norm(num.get_text()) if num else "") or view_label_from_text(body)
        if lbl:
            add(lbl, ttxt, body)

    # 1c〜2) 統合フォールバック：case-paragraph / problem-text / 直下 <p> を走査。
    #   1 要素に複数見解（【見解】A説…【見解】B説…）が同居する場合は見出し境界で分割。
    if len(views) < 2:
        # 見出し境界（新しい見解の開始位置・label を group で）
        HEAD_FIND = re.compile(
            rf"(?:【\s*見解\s*】\s*)?(?:【\s*見解\s*([{LABEL_CHARS}])\s*】|【?\s*([{LABEL_CHARS}])\s*説|見解\s*([{LABEL_CHARS}])\s*[（(])")

        def reg_seg(lbl, seg):
            seg = seg.strip()
            if not lbl or not re.search(r"説|見解", seg):
                return
            mm = re.match(HEAD_RE, seg, re.S)
            if mm and mm.group(2).strip():
                add(lbl, mm.group(1).strip(), mm.group(2).strip())
            else:
                add(lbl, "", seg)

        def register_from_text(text, forced_label=None):
            text = text.strip()
            if forced_label:
                reg_seg(forced_label, text)
                return
            ms = list(HEAD_FIND.finditer(text))
            if not ms or ms[0].start() > 2:   # 先頭が見出しで始まるもののみ（記述の途中一致を除外）
                return
            for i, mo in enumerate(ms):
                seg = text[mo.start(): ms[i + 1].start() if i + 1 < len(ms) else len(text)]
                lbl = half(mo.group(1) or mo.group(2) or mo.group(3) or "")
                reg_seg(lbl, seg)

        seen = set()
        cands = pa.select(".case-paragraph") + pa.select(".problem-text") + pa.find_all("p", recursive=True)
        for el in cands:
            if is_record(el):
                continue
            t = el.get_text(" ", strip=True)
            key = norm(t)
            if not key or key in seen:
                continue
            seen.add(key)
            # 先頭ラベル span（A/B 等）がある型（例：「A 見解A（原因行為説）…」「A 【A説】──…」）
            span = el.find(class_="choice-num-inline") if el.name != "p" else None
            sp = norm(span.get_text()) if span else ""
            if sp and len(sp) <= 2 and re.match(rf"[{LABEL_CHARS}]", sp) and t.startswith(sp):
                register_from_text(t[len(sp):].strip(), forced_label=sp)
            else:
                register_from_text(t)
    return views

def label_variants(lbl):
    return [f"{lbl}説", f"{lbl}の見解", f"{lbl}の立場", f"見解{lbl}", f"{lbl}の考え"]

def referenced_labels(sec, views):
    so = sec.find(class_="syn-orig")
    text = half(so.get_text(" ", strip=True)) if so else ""
    if not text:
        return []
    hits = []
    for lbl in views:
        pos = min([text.find(v) for v in label_variants(lbl) if text.find(v) >= 0] or [10**9])
        if pos < 10**9:
            hits.append((pos, lbl))
    # 「いずれの見解／両説／両見解」型は全見解を前提として再掲
    if re.search(r"いずれの(見解|説)|両(説|見解)|双方の(見解|説)", text):
        return sorted(views)
    return [l for _, l in sorted(hits)]

def build_premise(labels, views, soup):
    wrap = soup.new_tag("div", **{"class": "choice-premise"})
    head = soup.new_tag("span", **{"class": "cp-head"}); head.string = "🔎 この記述が前提とする見解"
    wrap.append(head)
    for lbl in labels:
        v = views[lbl]
        if v["title"]:
            t = soup.new_tag("p", **{"class": "cp-title"}); t.string = v["title"]; wrap.append(t)
        for para in (v["body"].split("\n") if v["body"] else []):
            if para.strip():
                b = soup.new_tag("p", **{"class": "cp-body"}); b.string = para.strip(); wrap.append(b)
    return wrap

def process(path, apply=False):
    soup = BeautifulSoup(open(path, encoding="utf-8").read(), "html.parser")
    views = extract_views(soup)
    secs = soup.find_all("section", class_="choice-section")
    already = sum(1 for s in secs if s.find(class_="choice-premise"))
    ref = {}
    for s in secs:
        if s.find(class_="choice-premise"):
            continue
        ref[s.get("id")] = referenced_labels(s, views)
    n_ref = sum(1 for v in ref.values() if v)
    confident = len(views) >= 2 and n_ref >= max(2, len(secs) - already - 1)
    status = "DONE" if (already and not ref) else ("CONFIDENT" if confident else ("REVIEW" if (views and n_ref) else "SKIP"))
    print(f"  views={len(views)}{sorted(views)} secs={len(secs)} done={already} ref={n_ref} -> {status}")
    if not apply or status != "CONFIDENT":
        return status, 0
    inserted = 0
    for s in secs:
        if s.find(class_="choice-premise"):
            continue
        labels = ref.get(s.get("id")) or []
        if not labels:
            continue
        hb = s.find(class_="choice-header-block")
        if not hb:
            continue
        hb.insert_after(build_premise(labels, views, soup))
        hb.insert_after(NavigableString("\n\n    "))
        inserted += 1
    out = str(soup)
    if ".choice-premise{" not in out:
        out = out.replace("</style>", CSS_BLOCK + "\n</style>", 1)
    open(path, "w", encoding="utf-8").write(out)
    return status, inserted

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    files = args or [f for sub in ["刑TX","憲TX","民TX","商TX","民訴TX","刑訴TX","行政TX"]
                     for f in sorted(glob.glob(f"outputs/000_TX/{sub}/*.html"))]
    STRONG = re.compile(r"の見解によれば|の見解に立|の見解から|説によれば|説に立[つっ]|説からは|説の立場|この見解")
    conf = []; total = 0; review = []
    for f in files:
        if "_failed" in f or "-deep" in f:
            continue
        if not STRONG.search(open(f, encoding="utf-8").read()):
            continue
        print(f"{os.path.basename(f)}:")
        st, ins = process(f, apply=apply)
        if st == "CONFIDENT": conf.append(os.path.basename(f))
        elif st == "REVIEW": review.append(os.path.basename(f))
        total += ins
    print(f"\nCONFIDENT {len(conf)}: {conf}")
    print(f"REVIEW {len(review)}: {review}")
    if apply: print(f"挿入合計 {total} ブロック")

if __name__ == "__main__":
    main()
