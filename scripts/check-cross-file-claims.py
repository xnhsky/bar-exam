#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
準用関係の corpus 横断矛盾ゲート（内容監査・2026-09-04）

コーパスを横断走査し、**同じ条文ペアについて「準用する」と「準用しない」が
別ファイルで書かれている**箇所を検出する。1 ファイル内の検証（validate-tx-core）は
その中の整合しか見ないため、「A というファイルでは準用すると書き、B というファイルでは
準用しないと書く」型の誤りは、どのゲートにも掛からず corpus に居座る。

実害（2026-09-04・§v13x 執筆中に精読して発覚）:
  刑訴TX118 記述2「捜査段階の差押え・捜索にも 222条1項が 113条を準用し、立会いの規律が働く」
  ⇄ 刑訴TX116 記述1「222条1項は 113条1項を準用しておらず、弁護人の立会権はない」
  正しいのは後者。222条1項の準用列挙に 113条は入っていない。
  この 2 本は同じ帯（弁護人の立会権）に並んでいたが、機械検査はどちらも PASS だった。

なぜ allowlist 方式か（check-citation-era.py と同じ思想）:
  「割れ＝即誤り」ではない。①条文が改正で準用関係を変えた（新旧で結論が違う）
  ②同じ条番号でも法律が違う（刑訴/民法/刑法）③一文に複数の条文が並び、抽出が
  取り違える、の 3 つがある。よって**割れを検出し、一次確認で正当と確定したペアは
  allowlist に登録して抑止**、未確認の新規の割れだけを gate（exit 1）で止める。

検出単位:
  (法域, 基準条, 対象条) でグルーピングし、ファイル単位の多数決で POS/NEG を決め、
  **ファイル間で結論が割れたペア**を報告する。同一ファイル内の POS/NEG 混在は
  「原則と例外を並べて説明している」正常な書き方なので割れとして扱わない。

法域の推定:
  ファイルの科目接頭辞（刑訴TX / 刑TX / 民TX …）から決める。異なる科目のファイルは
  同じ条番号でも別ペアとして扱う（民法 889条と刑訴 889条を混ぜない）。

使い方:
    python scripts/check-cross-file-claims.py                 # 既定 outputs/ux/000_TX を走査
    python scripts/check-cross-file-claims.py outputs         # ルート指定
    python scripts/check-cross-file-claims.py --list          # 全ペアの分布（棚卸し用）
    python scripts/check-cross-file-claims.py --warn-only     # 検出しても exit 0（可視化のみ）

allowlist:
    scripts/cross-file-claims-allowlist.txt
    1 行 = `科目|基準条|対象条  # 一次確認メモ`（# 以降は注記）。空行と # 始まりは無視。

割れ（allowlist 未登録）を検出すると exit 1 を返す。
"""
import sys
import os
import re
import html
import glob
import collections

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWLIST = os.path.join(REPO, "scripts", "cross-file-claims-allowlist.txt")
DEFAULT_ROOTS = [os.path.join("outputs", "ux", "000_TX")]

# 「準用しない」側を示す語（準用の直後 14 字以内に出るもの）
NEG_TOKENS = (
    "準用せず", "準用しな", "準用していな", "準用されず", "準用されな", "準用されていな",
    "準用の対象外", "準用対象外", "準用外", "準用がな", "準用はな", "準用する余地はな",
    "準用を外", "準用を除外", "準用から除外", "準用しておらず", "準用されておらず",
    "準用の対象から除外", "準用対象から除外", "準用の対象外", "準用対象に含まれな",
)
# 条番号（項は落として正規化する＝「113条」と「113条1項」を同じ対象として扱う）
ART = re.compile(r"(\d+条(?:の\d+)?)(第?\d+項)?")
RANGE = re.compile(r"(\d+)条(?:の\d+)?から(\d+)条(?:の\d+)?まで")
SUBJECT = re.compile(r"^(刑訴|民訴|行政|刑|民|商|憲)TX")


def subject_of(path):
    name = os.path.basename(path)
    m = SUBJECT.match(name)
    return m.group(1) if m else "?"


def load_allowlist():
    ok = set()
    if not os.path.exists(ALLOWLIST):
        return ok
    with open(ALLOWLIST, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 3:
                ok.add(tuple(parts))
    return ok


def plain_text(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    # <script>/<style> の中身は本文ではないので落とす（JS のヒント文字列は本文と重複する）
    raw = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.S | re.I)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


EXCLUDE = ("含まれていな", "含めていな", "入っていな", "挙がっていな", "列挙にな",
           "リストにな", "準用の列挙にな", "対象に含まれ",
           "含まれな", "含まな", "入らな", "除外されて", "除外して")
# 対象条の**直後**に来る否定（「準用リストに113条はない」「113条を引かない」型）
POST_NEG = ("はない", "は無い", "は入って", "は入らな", "は含まれ", "を引かな", "は及ばな", "は挙がって")


def claims_in_sentence(sent, carried=None):
    """1 文から (基準条, 対象条, 極性) を取り出す。

    一文に準用の肯否が同居する形（「222条1項は110条から112条は準用しながら、113条は準用しない」）と、
    肯定文＋除外文の形（「222条1項が準用する条文の列挙に113条は含まれていない」）の両方を割るため、
    **読点で節に切り、節ごとに判定**する。基準条はその節の先頭の条（無ければ直前の節から引き継ぐ）、
    対象条は準用（又は除外表現）の直前にある最も近い条。列挙範囲（110条から112条まで）は展開する。
    """
    out = []
    base = carried
    # 読点に加えて空白でも切る（図解・体系マップの断片は句読点なしで連結されるため）
    for clause in re.split(r"[、，\s]+", sent):
        has_jun = "準用" in clause
        exc_at = -1
        for e in EXCLUDE:
            i = clause.find(e)
            if i >= 0 and (exc_at < 0 or i < exc_at):
                exc_at = i
        if not has_jun and exc_at < 0:
            continue
        arts = [(m.start(), m.group(1), (m.group(2) or "").replace("第", "")) for m in ART.finditer(clause)]
        if not arts:
            continue
        if len(arts) >= 2:
            base = arts[0][1]
        elif base is None:
            base = arts[0][1]
        pol = "POS"
        marker = clause.find("準用") if has_jun else exc_at
        if has_jun:
            for t in NEG_TOKENS:
                if t in clause[clause.find("準用"):clause.find("準用") + 16]:
                    pol = "NEG"
                    break
        if exc_at >= 0:
            pol = "NEG"
            marker = exc_at
        # 対象条＝マーカー直前で最も近い条（無ければ直後）。基準条そのものは対象にしない。
        before = [a for a in arts if a[0] < marker and a[1] != base]
        after = [a for a in arts if a[0] >= marker and a[1] != base]
        hit = before[-1] if before else (after[0] if after else None)
        target, tkou = (hit[1], hit[2]) if hit else (None, "")
        # 「（225条・168条）」「139条・172条の準用がない」のような**併記の引用**は準用関係ではない。
        # 基準条と対象条の間が中黒・読点・及び等だけなら、列挙として扱い claim にしない
        # （これを拾うと「225条は168条を準用しない」等の偽の割れが量産される）。
        if target:
            bi = next((a[0] for a in arts if a[1] == base), None)
            ti = next((a[0] for a in arts if a[1] == target), None)
            if bi is not None and ti is not None:
                lo, hi = (bi, ti) if bi < ti else (ti, bi)
                span = clause[lo:hi]
                span = re.sub(r"\d+条(?:の\d+)?(?:第?\d+項)?", "", span)
                if re.fullmatch(r"[\s・･、，及びならびに並]*", span):
                    target = None
        if target:
            ti = next((a[0] for a in arts if a[1] == target), None)
            tail = clause[ti + len(target):ti + len(target) + 14] if ti is not None else ""
            if any(n in tail for n in POST_NEG):
                pol = "NEG"
        targets = [(target, tkou)] if target else []
        for r in RANGE.finditer(clause):
            lo, hi = int(r.group(1)), int(r.group(2))
            if 0 < hi - lo <= 12:
                targets += [(f"{n}条", "") for n in range(lo, hi + 1)]
        for t, k in dict.fromkeys(targets):
            if t and t != base:
                out.append((base, t, pol, k))
    return out


def scan(roots):
    files = []
    for root in roots:
        if os.path.isfile(root):
            files.append(root)
        else:
            files += glob.glob(os.path.join(root, "**", "*.html"), recursive=True)
    files = sorted(set(files))
    # pair -> file -> Counter(pol)
    per = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    examples = collections.defaultdict(dict)
    kous = collections.defaultdict(lambda: collections.defaultdict(set))   # pair -> (file,pol) -> 項
    for f in files:
        subj = subject_of(f)
        name = os.path.basename(f)
        for sent in re.split(r"[。\n]", plain_text(f)):
            if "準用" not in sent or len(sent) > 220:
                continue
            for base, target, pol, kou in claims_in_sentence(sent):
                key = (subj, base, target)
                per[key][name][pol] += 1
                kous[key][(name, pol)].add(kou)
                examples[key].setdefault((name, pol), " ".join(sent.split())[:110])
    return files, per, examples, kous


def main():
    args = sys.argv[1:]
    warn_only = "--warn-only" in args
    listing = "--list" in args
    roots = [a for a in args if not a.startswith("--")] or DEFAULT_ROOTS
    allow = load_allowlist()

    files, per, examples, kous = scan(roots)
    conflicts = []
    for key, byfile in per.items():
        verdict = {}
        for fn, c in byfile.items():
            # ファイル内は多数決（原則と例外を並べる書き方を割れとしない）
            verdict[fn] = "NEG" if c["NEG"] >= c["POS"] else "POS"
        if len(verdict) > 1 and len(set(verdict.values())) > 1:
            # 「準用する」と言っている側と「しない」と言っている側が、対象条の**別の項**を
            # 指しているだけなら割れではない（例：223条2項は198条1項ただし書を準用し、198条2項は
            # 準用しない／889条2項は887条2項を準用し、887条3項は準用しない）。
            pos_k, neg_k = set(), set()
            for fn, pol in verdict.items():
                (pos_k if pol == "POS" else neg_k).update(kous[key].get((fn, pol), {""}))
            if "" not in pos_k and "" not in neg_k and not (pos_k & neg_k):
                continue
            conflicts.append((key, verdict))

    print(f"=== 準用の corpus 横断矛盾ゲート (check-cross-file-claims) ===")
    print(f"走査 {len(files)} ファイル / 準用ペア {len(per)} 種")

    if listing:
        for key, byfile in sorted(per.items()):
            pos = sum(c["POS"] for c in byfile.values())
            neg = sum(c["NEG"] for c in byfile.values())
            print(f"  {key[0]}|{key[1]}|{key[2]}  files={len(byfile)} POS={pos} NEG={neg}")
        return 0

    unreviewed = [(k, v) for k, v in conflicts if k not in allow]
    suppressed = len(conflicts) - len(unreviewed)
    if suppressed:
        print(f"[INFO] allowlist で抑止した確認済みの割れ: {suppressed} 件")
    if not unreviewed:
        print(f"[OK] 未確認の準用の割れなし（割れ {len(conflicts)} 件はすべて allowlist 済み）")
        return 0

    print(f"\n--- 未確認の割れ {len(unreviewed)} 件（ファイル間で結論が逆） ---")
    for key, verdict in sorted(unreviewed, key=lambda x: -len(x[1])):
        subj, base, target = key
        print(f"\n[{subj}] {base} → {target} を準用するか")
        for fn, pol in sorted(verdict.items()):
            mark = "準用する" if pol == "POS" else "準用しない"
            print(f"   {mark:<6} {fn}: {examples[key].get((fn, pol), '')}")
    print(f"\n一次確認（条文の準用列挙）で正しい側を確定し、誤っているファイルを直すか、"
          f"\n正当な割れ（改正前後・別法域）なら {os.path.relpath(ALLOWLIST, REPO)} に登録して抑止する。")
    return 0 if warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
