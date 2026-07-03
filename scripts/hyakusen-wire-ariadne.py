#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyakusen-wire-ariadne.py — 刑法 ARIADNE の case-card へ data-hyakusen を配線する決定論ツール。

二系統の信号で百選番号を確定する：
  (A) カード見出し/出典に author が明記した百選番号（例「百選I42」「百選II（各論）2事件」）。
  (B) 判決日＋裁判所種別 → 索引 references/hyakusen/_index-刑法.md の逆引き。
(A)がある場合は索引の同番号エントリの日付と突合して検証（不一致=CONFLICT）。
(A)が無い場合は日付が索引で一意（かつ裁判所種別が整合）なら確定。多義・court不一致は REVIEW。

方針（lean・安全側）：
  - CONFIDENT のみ --apply で data-hyakusen を書く（冪等・既存属性は温存）。
  - CONFLICT / REVIEW / (EXPLICIT 番号が索引に無い) は書かず、レポートで目視に回す。
  - 一次資料（百選PDF）での引用是正は本ツールの対象外（別タスク）。

使い方：
  python scripts/hyakusen-wire-ariadne.py                 # 全 刑法ARIADNE をドライラン（レポートのみ）
  python scripts/hyakusen-wire-ariadne.py --apply          # CONFIDENT を書き込む
  python scripts/hyakusen-wire-ariadne.py --file 刑JX003   # 1問だけ
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "hyakusen" / "_index-刑法.md"
ARIADNE_DIR = ROOT / "outputs" / "ux" / "001_ARIADNE" / "001_刑法"

ERA = {"明治": "M", "大正": "T", "昭和": "S", "平成": "H", "令和": "R",
       "m": "M", "t": "T", "s": "S", "h": "H", "r": "R"}
ZEN2HAN = str.maketrans("０１２３４５６７８９", "0123456789")
ROMAN = {"Ⅰ": "I", "Ⅱ": "II", "Ⅲ": "III", "Ⅰ".lower(): "I"}


def norm_num(s):
    return (s or "").translate(ZEN2HAN)


def norm_vol(v):
    v = (v or "").strip()
    v = "".join(ROMAN.get(c, c) for c in v)
    v = v.upper().replace("Ｉ", "I").replace("Ⅰ", "I").replace("Ⅱ", "II")
    return v


def date_key(era_letter, y, m, d):
    if not (era_letter and y and m and d):
        return None
    y = 1 if str(y) in ("元", "1") else int(norm_num(str(y)))
    return f"{era_letter}{y}.{int(norm_num(str(m)))}.{int(norm_num(str(d)))}"


def wareki_to_key(text):
    """本文中の「平成17年7月4日」「昭和63年2月29日」「平成元年…」を date_key へ。"""
    m = re.search(r"(明治|大正|昭和|平成|令和)\s*(元|[0-9０-９]+)\s*年\s*([0-9０-９]+)\s*月\s*([0-9０-９]+)\s*日", text)
    if not m:
        return None
    return date_key(ERA[m.group(1)], m.group(2), m.group(3), m.group(4))


def id_to_key(card_id):
    """id 末尾の -h17-7-4 / -s63-2-29 / -t4-5-21 を date_key へ（最後の一致を採用）。"""
    ms = list(re.finditer(r"-([hstrm])(\d+)-(\d+)-(\d+)(?:$|-)", card_id))
    if not ms:
        return None
    m = ms[-1]
    return date_key(ERA[m.group(1)], m.group(2), m.group(3), m.group(4))


def court_class_from_text(text):
    """見出し等のテキストから裁判所クラス（最/大審/高/地）を粗く判定。"""
    if re.search(r"最(?:高裁)?大(?:法廷)?(?:判|決)", text) or "最大判" in text or "最大決" in text:
        return "最"
    if re.search(r"最(?:高裁)?[一二三]?小?(?:法廷)?(?:判|決)", text) or "最判" in text or "最決" in text:
        return "最"
    if "大判" in text or "大決" in text or "大審院" in text:
        return "大審"
    if re.search(r"高(?:等裁判所)?(?:判|決)", text) or "高判" in text or "高決" in text:
        return "高"
    if re.search(r"地(?:方裁判所)?(?:判|決)", text) or "地判" in text or "地決" in text:
        return "地"
    return None


def court_class_from_id(card_id):
    if "saidaihan" in card_id:
        return "最"
    if "saihan" in card_id or "saiketsu" in card_id or "saidai" in card_id:
        return "最"
    if "daihan" in card_id or "daiketsu" in card_id:
        return "大審"
    if "koso" in card_id:
        return "高"
    # 地裁は place 名のみで曖昧。text 側に委ねる。
    return None


def court_class_index(court):
    if court.startswith("最"):
        return "最"
    if court.startswith("大判") or court.startswith("大決"):
        return "大審"
    if "高判" in court or "高決" in court:
        return "高"
    if "地判" in court or "地決" in court:
        return "地"
    return None


def parse_index():
    entries = []          # {vol,num,court,cc,key,ronten}
    by_key = {}           # date_key -> [entry]
    by_volnum = {}        # (vol,num) -> entry
    vol = None
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if line.startswith("## 刑法I "):
            vol = "I"
        elif line.startswith("## 刑法II "):
            vol = "II"
        m = re.match(r"\|\s*(I{1,2})-(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(\d+)\s*\|", line)
        if not m:
            continue
        v, num, ronten, court, ymd, page = m.groups()
        # ymd 例: 平成17・7・4 / 大正12・4・30 / 平成元・12・15
        dm = re.match(r"(明治|大正|昭和|平成|令和)(元|\d+)・(\d+)・(\d+)", ymd)
        key = date_key(ERA[dm.group(1)], dm.group(2), dm.group(3), dm.group(4)) if dm else None
        e = {"vol": v, "num": int(num), "court": court, "cc": court_class_index(court),
             "key": key, "ronten": ronten, "page": int(page)}
        entries.append(e)
        by_volnum[(v, int(num))] = e
        if key:
            by_key.setdefault(key, []).append(e)
    return entries, by_key, by_volnum


# --- カード抽出 ---
CARD_OPEN = re.compile(r'<div class="basis-card case-card"([^>]*)>')


def extract_explicit(header, shutten):
    """見出し＋出典から百選番号を抽出（本文の先例参照は拾わない）。"""
    for src in (header, shutten):
        if not src:
            continue
        m = re.search(r"百選\s*([ⅠⅡⅢIVXivx]+)\s*[（(〔\[]?\s*各?\s*論?\s*[）)〕\]]?\s*([0-9０-９]+)", src)
        if m:
            return (norm_vol(m.group(1)), int(norm_num(m.group(2))))
    return None


def process(html, by_key, by_volnum):
    """1ファイル分。カードごとの判定リストと、apply 用の書換え済み html を返す。"""
    results = []
    edits = []  # (insert_pos, text)
    for mo in CARD_OPEN.finditer(html):
        attrs = mo.group(1)
        tag_end = mo.end()
        # このカードのブロック（次の case/statute カード直前まで、最大 4000 字）。
        # 空白付き 'basis-card ' で束ね、'basis-card-header/-body' の下位 div では切らない。
        nxt = html.find('<div class="basis-card ', tag_end)
        block = html[tag_end: nxt if 0 <= nxt <= tag_end + 4000 else tag_end + 4000]
        cid_m = re.search(r'id="([^"]*)"', attrs)
        cid = cid_m.group(1) if cid_m else ""
        has_hy = 'data-hyakusen=' in attrs
        # header / 出典（刑JX021 等は bc-h/bc-b 短縮クラスの異形）
        h_m = re.search(r'class="(?:basis-card-header|bc-h)">(.*?)</div>', block, re.S)
        header = re.sub(r"<[^>]+>", "", h_m.group(1)) if h_m else ""
        s_m = re.search(r'出典</strong>[：:]\s*([^<]*)', block)
        shutten = s_m.group(1) if s_m else ""
        # 日付：カード自身の事件を名指す「見出し」「判決日/決定日フィールド」からのみ採る。
        # id 末尾の日付は流用残りで陳腐化しうる（別事件の id 使い回し）ため、日付根拠の
        # 自動確定には使わず、text 日付が無い場合の弱シグナル(REVIEW送り)に留める。
        fld_m = re.search(r'(?:判決日|決定日|裁判(?:年月)?日|言渡日)</strong>[：:]?\s*([^<]{0,24})', block)
        text_key = wareki_to_key(header) or (wareki_to_key(fld_m.group(1)) if fld_m else None)
        id_key = id_to_key(cid)
        key = text_key or id_key           # 明記番号の日付照合はベストエフォートで id も使う
        cc = court_class_from_text(header) or court_class_from_id(cid)
        explicit = extract_explicit(header, shutten)

        rec = {"cid": cid, "header": header.strip()[:60], "key": key, "cc": cc,
               "explicit": explicit, "status": None, "hy": None, "note": ""}

        if has_hy:
            rec["status"] = "ALREADY"
        elif explicit:
            e = by_volnum.get(explicit)
            if e is None:
                rec["status"] = "REVIEW"
                rec["note"] = f"明記 {explicit[0]}-{explicit[1]} が索引に無い（要確認）"
            elif key is None or e["key"] is None:
                rec["status"] = "CONFIDENT"
                rec["hy"] = explicit
                rec["note"] = "明記番号（日付照合不可・author信頼）"
            elif e["key"] == key:
                rec["status"] = "CONFIDENT"
                rec["hy"] = explicit
                rec["note"] = "明記番号＝索引日付一致（検証済）"
            else:
                rec["status"] = "CONFLICT"
                rec["note"] = f"明記 {explicit[0]}-{explicit[1]}(索引日{e['key']}) vs カード日{key}"
        else:
            # 自動確定は text 由来の日付のみを根拠にする（id 由来は REVIEW 送り）。
            cands = by_key.get(text_key, []) if text_key else []
            if cc:
                filt = [e for e in cands if e["cc"] == cc] or cands
            else:
                filt = cands
            if len(filt) == 1:
                rec["status"] = "CONFIDENT"
                rec["hy"] = (filt[0]["vol"], filt[0]["num"])
                rec["note"] = f"日付一意→{filt[0]['ronten'][:16]}"
            elif len(filt) > 1:
                rec["status"] = "REVIEW"
                rec["note"] = "同日複数候補：" + " / ".join(f"{e['vol']}-{e['num']}{e['court']}" for e in filt)
            elif text_key is None and id_key and by_key.get(id_key):
                # 本文に日付が無く id 日付だけが索引に当たる＝流用残り id の疑い。目視へ。
                cand = by_key.get(id_key)
                rec["status"] = "REVIEW"
                rec["note"] = "id由来日付のみ(本文に日付なし・要目視)：" + \
                    " / ".join(f"{e['vol']}-{e['num']}{e['ronten'][:10]}" for e in cand)
            else:
                rec["status"] = "NONE"
                rec["note"] = "百選日付に不一致（未収録/下級審)" if text_key else "日付・明記なし"

        if rec["status"] == "CONFIDENT" and rec["hy"]:
            ins = f' data-hyakusen="刑法百選{rec["hy"][0]}-{rec["hy"][1]}"'
            edits.append((tag_end - 1, ins))  # '>' の直前へ
        results.append(rec)

    if edits:
        for pos, text in sorted(edits, reverse=True):
            html = html[:pos] + text + html[pos:]
    return results, html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="CONFIDENT を書き込む")
    ap.add_argument("--file", help="対象を1問に絞る（例 刑JX003）")
    ap.add_argument("--verbose", action="store_true", help="CONFIDENT の割当を全件表示")
    ap.add_argument("--date-only", action="store_true", help="日付根拠(明記なし)の CONFIDENT だけ表示")
    args = ap.parse_args()

    _, by_key, by_volnum = parse_index()
    files = sorted(ARIADNE_DIR.glob("刑JX*_ARIADNE.html"))
    if args.file:
        files = [f for f in files if args.file in f.name]

    tally = {"CONFIDENT": 0, "REVIEW": 0, "CONFLICT": 0, "NONE": 0, "ALREADY": 0}
    applied = 0
    review_lines, conflict_lines, confident_lines = [], [], []
    for f in files:
        # 改行はファイル原状を保つ（ARIADNE は LF・text mode 書込は CRLF 化する）ため bytes I/O。
        html = f.read_bytes().decode("utf-8")
        results, new_html = process(html, by_key, by_volnum)
        for r in results:
            tally[r["status"]] += 1
            if r["status"] == "REVIEW":
                review_lines.append(f"  [{f.stem[:6]}] {r['cid']}｜{r['header']}｜{r['note']}")
            elif r["status"] == "CONFLICT":
                conflict_lines.append(f"  [{f.stem[:6]}] {r['cid']}｜{r['header']}｜{r['note']}")
            elif r["status"] == "CONFIDENT" and r["hy"]:
                date_only = r["note"].startswith("日付一意")
                if (not args.date_only) or date_only:
                    confident_lines.append(
                        f"  [{f.stem[:6]}] 刑法百選{r['hy'][0]}-{r['hy'][1]}"
                        f"{'（日付）' if date_only else '（明記）'}｜{r['cid']}｜{r['header']}｜{r['note']}")
        if args.apply and new_html != html:
            f.write_bytes(new_html.encode("utf-8"))
            applied += sum(1 for r in results if r["status"] == "CONFIDENT" and r["hy"])

    print("=== 集計 ===")
    for k, v in tally.items():
        print(f"  {k:9}: {v}")
    if conflict_lines:
        print("\n=== CONFLICT（明記番号と索引日付が矛盾・要一次確認）===")
        print("\n".join(conflict_lines))
    if review_lines:
        print(f"\n=== REVIEW（{len(review_lines)}件・目視確定）===")
        print("\n".join(review_lines))
    if (args.verbose or args.date_only) and confident_lines:
        head = "日付根拠のみ" if args.date_only else "全"
        print(f"\n=== CONFIDENT 割当（{head} {len(confident_lines)}件）===")
        print("\n".join(confident_lines))
    if args.apply:
        print(f"\n[APPLIED] data-hyakusen を {applied} 件書き込み")
    else:
        would = tally["CONFIDENT"]
        print(f"\n[DRY-RUN] --apply で CONFIDENT {would} 件を書き込み")


if __name__ == "__main__":
    main()
