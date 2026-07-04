# -*- coding: utf-8 -*-
# 百選仕様の case-card 本文を primary occurrence（最高 freq、同点は最小JX）へ適用。
# 開始タグ/header/card-return を温存し、body 内容だけ差替。bytes I/O(LF保持)。冪等。
import re, sys, glob
from pathlib import Path

ROOT = Path("C:/Users/xnrg2.DESKTOP-5664QR6/bar-exam/.claude/worktrees/elated-nobel-00af23")
ADIR = ROOT / "outputs/ux/001_ARIADNE/001_刑法"
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRAFT_FILES = [Path(a) for a in _args] if _args else [Path(__file__).with_name("drafts_batch1.txt")]
APPLY = "--apply" in sys.argv

# 1) drafts パース（複数ファイル連結・サブエージェントが HTML エスケープしていれば復号）
import html as _html
txt = "\n\n".join(p.read_text(encoding="utf-8") for p in DRAFT_FILES)
blocks = {}
for m in re.finditer(r"=== 刑法百選(I{1,2}-\d+) ===\n(.*?)(?=\n=== |\Z)", txt, re.S):
    body = m.group(2).strip()
    if "&lt;" in body or "&gt;" in body:
        body = _html.unescape(body)
    blocks[m.group(1)] = body
print(f"drafts: {len(blocks)}判例 {sorted(blocks)}")

# 2) 出現＋freq マップ
FR = {"freq-high": 3, "freq-mid": 2, "freq-low": 1}
occ = {}  # num -> [(jx, file, freq)]
for f in sorted(glob.glob(str(ADIR / "*.html"))):
    html = Path(f).read_text(encoding="utf-8")
    for m in re.finditer(r'data-hyakusen="刑法百選(I{1,2}-\d+)"', html):
        num = m.group(1)
        # そのカードの header の freq を取る（open タグ直後の header 行）
        seg = html[m.end():m.end()+400]
        fm = re.search(r"freq-(high|mid|low)", seg)
        fr = FR.get("freq-" + fm.group(1), 0) if fm else 0
        jx = int(re.search(r"刑JX(\d+)", Path(f).stem).group(1))
        occ.setdefault(num, []).append((jx, f, fr))

def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()

def extract_honmon(old_body):
    """元カードから本問固有のコーチング（答案での使い方＋本問/本件/設問を含む段落）を抽出。"""
    parts, seen = [], set()
    # (a) r-ate（答案での使い方）セクションの <p>
    m = re.search(r'<h5[^>]*r-ate[^>]*>.*?</h5>(.*?)(?=<h5|<div class="card-return"|$)', old_body, re.S)
    if m:
        for pm in re.finditer(r"<p[^>]*>(.*?)</p>", m.group(1), re.S):
            t = plain(pm.group(1))
            if t and t not in seen:
                seen.add(t); parts.append(t)
    # (b) 本問/本件/設問 を含む <p>（射程の当てはめ等）
    for pm in re.finditer(r"<p[^>]*>(.*?)</p>", old_body, re.S):
        t = plain(pm.group(1))
        if t and t not in seen and re.search(r"本問|本件|設問", t):
            seen.add(t); parts.append(t)
    return " ".join(parts).strip()

def find_body_close(html, bo_end):
    """basis-card-body 開始直後(bo_end)から div 深さを数え、body を閉じる </div> 位置を返す。"""
    depth, i = 1, bo_end
    while depth > 0:
        nd = html.find("<div", i)
        nc = html.find("</div>", i)
        if nc < 0:
            return -1
        if 0 <= nd < nc:
            depth += 1; i = nd + 4
        else:
            depth -= 1
            if depth == 0:
                return nc
            i = nc + 6
    return -1

def apply_card(html, num, body):
    # data-hyakusen=num の case-card を探し、body を「百選プロファイル＋本問での使い方」に差替
    m = re.search(r'(<div class="basis-card case-card"[^>]*data-hyakusen="刑法百選' + re.escape(num) + r'"[^>]*>)', html)
    if not m:
        return html, "open tag 不明"
    start = m.end()
    bo, bo_tag = -1, None
    for tag in ('<div class="basis-card-body">', '<div class="bc-b">'):
        p = html.find(tag, start)
        if p >= 0 and (bo < 0 or p < bo):
            bo, bo_tag = p, tag
    if bo < 0 or bo - start > 600:
        return html, "basis-card-body 不明"
    bo_end = bo + len(bo_tag)
    cr = html.find('<div class="card-return">', bo_end)
    nextcard = html.find('<div class="basis-card ', bo_end)
    if cr >= 0 and (nextcard < 0 or cr < nextcard):
        end = cr  # card-return を温存し、その手前まで差替
    else:
        end = find_body_close(html, bo_end)  # card-return 無し＝body 閉じまで差替
        if end < 0:
            return html, "body close 不明（手動）"
    honmon = extract_honmon(html[bo_end:end])
    content = body
    if honmon:
        content += ('\n<p class="hanging"><strong>【本問での使い方】</strong>'
                    '<span class="hang-body">' + honmon + "</span></p>")
    new = html[:bo_end] + "\n" + content + "\n" + html[end:]
    return new, ("OK" + ("＋本問" if honmon else "（本問なし）"))

ONLY = None
for a in sys.argv[1:]:
    if a.startswith("--only="):
        ONLY = set(a.split("=", 1)[1].split(","))

applied = 0
report = []
for num, body in sorted(blocks.items()):
    if ONLY and num not in ONLY:
        continue
    cand = occ.get(num, [])
    if not cand:
        report.append(f"  {num}: 出現なし"); continue
    cand.sort(key=lambda t: (-t[2], t[0]))  # freq降順, jx昇順
    jx, f, fr = cand[0]
    html = Path(f).read_bytes().decode("utf-8")
    new, st = apply_card(html, num, body)
    frn = {3:"high",2:"mid",1:"low",0:"-"}[fr]
    report.append(f"  {num} → 刑JX{jx:03d}(freq {frn}) : {st}  [他 {len(cand)-1}問]")
    if st.startswith("OK") and APPLY and new != html:
        Path(f).write_bytes(new.encode("utf-8"))
        applied += 1

print("\n".join(report))
print(f"\n{'[APPLIED] ' + str(applied) + '件書込' if APPLY else '[DRY-RUN] --apply で適用'}")
