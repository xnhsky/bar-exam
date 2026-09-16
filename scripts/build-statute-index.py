#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
条文インデックスの構築＋引用本文の corpus 横断不一致ゲート（内容監査・2026-09-04）

コーパスの 📚BASIS 条文カード（.tx-basis-item の .tx-basis-honbun）から
**条文の引用本文**を吸い出して法域ごとのインデックス（references/statutes/{法域}.md）を作り、
同時に**同じ条・項を引いているのに本文が食い違うファイル**を検出する。

なぜ要るか（2026-09-04・§v13x 執筆中に発覚した内容誤りの再発防止）:
  刑訴TX094 記述4「167条5項本文は勾留の執行が停止されたものとする」（正しくは 167条の2第1項）
  刑訴TX095 記述3「167条2項は期間を定めることを求め、3項は延長・短縮」（正しくは 1項と4項）
  条番号は実在し、ファイル内の整合も取れているため、既存のどのゲートにも掛からない。
  この型を潰すには**条文本文と突き合わせる**しかないが、当環境からは e-Gov に到達できない。
  そこで「コーパスが自分で持っている条文引用」を単一情報源に束ね、
    ①相互に矛盾する引用を機械検出する（下のゲート）
    ②執筆・監査時に引ける索引を作る（references/）
  の 2 つで、条文本文を手元に確保する。

検出単位:
  (法域, 条, 項) ごとに引用本文を正規化（記号・空白・強調を落とす）して比較し、
  **正規化後の本文が食い違うファイル**があれば報告する。短い引用（20字未満）と
  「本文」「本条」など項を特定できないラベルは比較対象から外す（誤検出を避ける）。

使い方:
    python scripts/build-statute-index.py --check          # 不一致だけ報告（既定・非ブロッキング）
    python scripts/build-statute-index.py --write          # references/statutes-*.md を生成
    python scripts/build-statute-index.py --strict         # 不一致があれば exit 1
"""
import sys
import os
import re
import html
import glob
import collections
import difflib

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = [os.path.join(REPO, "outputs", "ux", "000_TX")]
OUTDIR = os.path.join(REPO, "references", "statutes")
SUBJECT = re.compile(r"^(刑訴|民訴|行政|刑|民|商|憲)TX")
SUBJECT_LAW = {"刑訴": "刑事訴訟法", "民訴": "民事訴訟法", "行政": "行政法", "刑": "刑法",
               "民": "民法", "商": "商法", "憲": "憲法"}
# head の例：「📜 刑法171条 虚偽鑑定罪（本問の核心条文）」「📜 刑訴225条 鑑定受託者の処分」
HEAD_LAW = re.compile(r"(刑事訴訟法|刑訴法|刑訴|刑法|民法|民訴法|民訴|商法|会社法|憲法|行政事件訴訟法|行政手続法|警察官職務執行法|警職法|刑事訴訟規則|刑訴規則|規則|通信傍受法|裁判員法)")
HEAD_ART = re.compile(r"(\d+条(?:の\d+)?)")
# 項ラベル：「223①」「167④」「166」「2項」「①」「本文」「本条」
LABEL = re.compile(r"^(?:(\d+条?(?:の\d+)?))?\s*([①-⑩]|\d+項)?")
CIRCLE = {c: i + 1 for i, c in enumerate("①②③④⑤⑥⑦⑧⑨⑩")}


def subject_of(path):
    m = SUBJECT.match(os.path.basename(path))
    return m.group(1) if m else "?"


def text_of(frag):
    t = html.unescape(re.sub(r"<[^>]+>", "", frag))
    return " ".join(t.split())


def norm(s):
    """比較用の正規化：記号・空白・括弧書きの読点差を吸収する。"""
    s = re.sub(r"[\s　]", "", s)
    s = s.translate(str.maketrans("，．（）［］｛｝「」", "、。()[]{}｢｣"))
    s = re.sub(r"[、。・,.]", "", s)
    return s


def parse_file(path):
    """1 ファイルから (法域, 条, 項, 本文) を取り出す。"""
    raw = open(path, encoding="utf-8").read()
    body = raw.split("</style>")[-1]
    subj = subject_of(path)
    out = []
    for item in re.finditer(
        r'<div [^>]*class="tx-basis-item(?![^"]*is-case)(?![^"]*is-theory)[^"]*"[^>]*>(.*?)(?=<div [^>]*class="tx-basis-item|</div></div>\s*<div class="tx-v13-trap|$)',
        body, re.S,
    ):
        chunk = item.group(1)
        mh = re.search(r'<div class="tx-basis-head">(.*?)</div>', chunk, re.S)
        if not mh:
            continue
        head = text_of(mh.group(1))
        law = HEAD_LAW.search(head)
        law = law.group(1) if law else SUBJECT_LAW.get(subj, subj)
        law = {"刑訴法": "刑事訴訟法", "刑訴": "刑事訴訟法", "民訴法": "民事訴訟法",
               "民訴": "民事訴訟法"}.get(law, law)
        head_arts = list(dict.fromkeys(HEAD_ART.findall(head)))
        # head に条が複数並ぶ複合カード（「刑訴218条1項・憲法35条1項」等）は、
        # どの本文がどの条のものか機械では割れないので既定の条を置かない
        default_art = head_arts[0] if len(head_arts) == 1 else None
        # 「108〜110条」「99・102条」のような範囲・併記 head も複合として扱う
        compound = bool(re.search(r"\d+\s*[〜～～\-－・､、]\s*\d+\s*条", head))
        multi_head = len(head_arts) > 1 or compound
        if compound:
            default_art = None
        multi_law = len(set(HEAD_LAW.findall(head))) > 1
        mb = re.search(r'<div class="tx-basis-honbun">(.*?)</div>\s*(?:<details|</div>)', chunk, re.S)
        if not mb:
            continue
        for p in re.finditer(
            r'<span class="para-num">(.*?)</span>\s*<span class="hang-body[^"]*">(.*?)</span>\s*</p>',
            mb.group(1), re.S,
        ):
            label, text = text_of(p.group(1)), text_of(p.group(2))
            if len(text) < 20:
                continue
            m = LABEL.match(label)
            art, kou = (m.group(1), m.group(2)) if m else (None, None)
            # 素の数字ラベルは、条か項・号かが曖昧（「166」＝166条／「2」＝2項・2号）。
            # head に同じ条が挙がっているか、3 桁以上のときだけ条として扱い、
            # それ以外は head の条の項として読む（誤って 207条1項の本文を「1条」に登録しない）。
            if art and not art.endswith("条"):
                if f"{art}条" in head_arts or len(art) >= 3:
                    art = art + "条"
                else:
                    kou = kou or f"{art}項"
                    art = None
            art = art or default_art
            if not art:
                continue
            # 条の確度：head が挙げた条か、ラベル自体が「◯条」形のときだけ索引に載せる
            # （素の数字ラベルを条と誤読して、別条の本文を登録しないための最終ガード）
            if art not in head_arts and not (m.group(1) or "").endswith("条"):
                continue
            if (multi_head or multi_law) and not m.group(1):
                continue      # 複合 head ＋ 項だけのラベル＝条の帰属が確定しない
            if kou in CIRCLE:
                kou = f"{CIRCLE[kou]}項"
            if not kou:
                # 「223①」型は条ラベルに丸数字が続く。ラベル全体から拾い直す
                mc = re.search(r"([①-⑩])", label)
                kou = f"{CIRCLE[mc.group(1)]}項" if mc else ""
            out.append((law, art, kou, text))
    return out


def main():
    args = sys.argv[1:]
    write = "--write" in args
    strict = "--strict" in args
    files = []
    for r in ROOTS:
        files += glob.glob(os.path.join(r, "**", "*_lex.html"), recursive=True)
    files = sorted(files)

    idx = collections.defaultdict(lambda: collections.defaultdict(list))  # law -> (art,kou) -> [(file,text)]
    for f in files:
        for law, art, kou, text in parse_file(f):
            idx[law][(art, kou)].append((os.path.basename(f), text))

    total = sum(len(v) for v in idx.values())
    print("=== 条文インデックス／引用本文の横断不一致 (build-statute-index) ===")
    print(f"走査 {len(files)} ファイル / 法域 {len(idx)} / 条項 {total} 種")

    mismatches = []
    for law, per in idx.items():
        for key, entries in per.items():
            if not key[1]:          # 項が特定できない引用（「本文」「本条」）は比較しない
                continue
            groups = []
            for fn, t in entries:
                n = norm(t)
                core = n.split("…")[0][:40]      # 省略引用は先頭で比べる
                for g in groups:
                    gn = g[0]
                    same = (
                        difflib.SequenceMatcher(None, gn, n).ratio() >= 0.80
                        or n in gn or gn in n                      # 部分引用（ただし書だけ等）
                        or (core and (core in gn or gn[:40] in n))  # 省略・付記の差
                    )
                    if same:
                        g[1].append((fn, t))
                        break
                else:
                    groups.append((n, [(fn, t)]))
            if len(groups) > 1:
                mismatches.append((law, key, groups))

    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for law, per in sorted(idx.items()):
            safe = law.replace("/", "_")
            path = os.path.join(OUTDIR, f"{safe}.md")
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(f"# {law} 条文インデックス（コーパス自動生成）\n\n")
                fh.write("`scripts/build-statute-index.py --write` が outputs の 📚BASIS 条文カードから\n"
                         "抽出した引用本文の索引。**一次資料ではない**（e-Gov に到達できない環境で、\n"
                         "執筆・監査のときに条文本文を手元で引くための作業用）。引用の食い違いは\n"
                         "同スクリプトの `--check` が検出する。\n\n"
                         "**帰属のノイズが残る**：カードの見出しが条を明示しない場合や、法令名を書かずに\n"
                         "他法令（警察法・犯罪捜査規範等）を引く場合、条・法域の推定を誤ることがある。\n"
                         "各行の末尾に出典ファイルを付けてあるので、疑わしい行は必ず出典で裏を取る。\n\n")
                def sortkey(k):
                    m = re.match(r"(\d+)条(?:の(\d+))?", k[0])
                    return (int(m.group(1)), int(m.group(2) or 0), k[1]) if m else (9999, 0, "")
                for key in sorted(per, key=sortkey):
                    entries = per[key]
                    art, kou = key
                    best = max(set(t for _, t in entries), key=lambda t: sum(1 for _, x in entries if x == t))
                    fh.write(f"- **{art}{kou}**　{best}　`{entries[0][0]}` ほか{len(entries)}件\n")
            print(f"[write] {os.path.relpath(path, REPO)}  ({len(per)} 条項)")

    if not mismatches:
        print("[OK] 同一条項の引用本文の食い違いなし")
        return 0
    print(f"\n--- 引用本文が食い違う条項 {len(mismatches)} 件 ---")
    for law, key, groups in mismatches[:40]:
        print(f"\n[{law}] {key[0]}{key[1]}")
        for n, ents in groups:
            fn, t = ents[0]
            print(f"   ({len(ents)}件) {fn}: {t[:90]}")
    print("\n条文本文を一次確認し、誤って引いているファイルを直す。"
          "\n（同じ条項でも改正前後で本文が違う場合は、現行法へそろえて現行法ノートに旧文を残す）")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main())
