# -*- coding: utf-8 -*-
"""
build-topic-map.py  ─  過去問(TX) → 論点ノード の対応表を生成する。

論点習熟度マップ(Topic Mastery Map)の P1。
経路2「タイトル・ファジー一致」で TX_lex の <title> の論点名を
references/topics/<科目>.json の論点ツリー節名へ照合し、
references/topic-map/<科目>.json を起こす。

- 素材は TX タイトル(論点名＋過去問ID)のみ。問題本文・解説は読まない。
- 出力: { meta, map: { "刑TX001": {node, secondary, conf, review, topic, qid_raw} } }
- 併せて coverage(各ノードの TX 本数・未収録リーフ)を stdout に出す。

使い方:
    python scripts/build-topic-map.py 刑法
    python scripts/build-topic-map.py 刑法 --check   # 書き込まず REVIEW/未マップだけ表示
"""
import sys, os, re, json, glob, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 科目 → TX_lex 出力ディレクトリ
SUBJECT_DIR = {
    "刑法":   "001_刑法",
    "刑事訴訟法": "002_刑事訴訟法",
    "民法":   "003_民法",
    "商法":   "004_商法",
    "民事訴訟法": "005_民事訴訟法",
    "行政法": "006_行政法",
    "憲法":   "007_憲法",
}

# ── 明示オーバーライド(コード指定・横断/紛らわしいものを手当て) ──────────
# キーワード規則では拾いきれない or 誤爆する問題を code で直接固定する。
OVERRIDE = {
    "刑法": {
        "刑TX076": "4.1.1",   # 自殺関与罪と殺人罪の区別 → 殺人の罪
        "刑TX143": "2.6.1",   # 正犯・共犯の区別 → 共犯総論
        "刑TX158": "4.1.2",   # 同時傷害の特例と傷害致死 → 傷害の罪
        "刑TX185": "2.6.5",   # 共犯関係からの離脱と中止犯 → 共犯の諸問題
        "刑TX220": "4.1.2",   # 胎児傷害と業務上過失致死 → 傷害の罪
        "刑TX331": "4.4.9",   # 公用文書毀棄罪・公務執行妨害罪 → 毀棄及び隠匿
        "刑TX349": "4.4.2",   # 親族相盗例の射程と事後強盗罪 → 窃盗(244条)
        "刑TX401": "7",       # 国家的法益に対する罪の成否(総合) → 総合問題
        "刑TX437": "7",       # 故意の総合問題(未必・錯誤・共犯) → 総合問題
        "刑TX334": "7",       # 各種の犯罪の成否(甲の罪責) → 総合問題
        "刑TX337": "7",       # 犯罪の成立①(甲の各行為) → 総合問題
        "刑TX339": "7",       # 犯罪の成立②(強盗致死・証拠隠滅・放火) → 総合問題
        "刑TX434": "7",       # 偽札詐取殺害事件(総合問題) → 総合問題(偽札→通貨誤爆の是正)
        "刑TX177": "2.6.1",   # 共犯一般の区別 → 共犯総論
        "刑TX436": "7",       # 横領と賄賂の交錯 → 総合問題
        "刑TX442": "7",       # 総合事例:略取・傷害・電計詐欺・犯人隠避 → 総合問題
        "刑TX443": "7",       # 居直り強盗・共犯の錯誤・盗品関与の総合事例 → 総合問題
        "刑TX444": "7",       # 強盗殺人・死体遺棄・放火・公用文書毀棄・死者名誉 → 総合問題
        "刑TX445": "7",       # 詐欺・賭博・電計詐欺・犯人隠避の総合事例 → 総合問題
    },
}

# ── キーワード規則(順序＝最初にマッチした規則を採用・特殊→一般) ──────────
# (正規表現, ノードID, conf) ; conf: high / med(要確認寄り)
RULES = {
    "刑法": [
        # 総論・基礎
        (r"刑罰論|応報刑|目的刑|犯罪と刑罰", "1.1", "high"),
        (r"罪刑法定", "1.2", "high"),
        (r"場所的適用|時間的適用|国外犯|刑法の適用範囲", "1.3", "high"),
        # 構成要件
        (r"不作為犯", "2.2.2", "high"),
        (r"結果的加重犯の共同正犯", "2.6.2", "high"),
        (r"結果的加重犯", "2.2.2", "med"),
        (r"因果関係", "2.2.3", "high"),
        (r"方法の錯誤|客体の錯誤|事実の錯誤|構成要件的故意", "2.2.4", "high"),
        (r"過失", "2.2.5", "high"),
        # 違法性
        (r"自殺関与", "4.1.1", "high"),                       # 殺人章へ(違法性ではない)
        (r"被害者の同意|被害者の承諾|同意傷害|承諾と錯誤", "2.3.2", "med"),
        (r"違法性阻却.*正当行為|正当行為", "2.3.2", "high"),
        (r"緊急避難|過剰避難|対物防衛|第三者に対する防衛", "2.3.4", "high"),
        (r"正当防衛|偶然防衛|過剰防衛|防衛の意思|量的過剰|防衛の共同", "2.3.3", "high"),
        (r"自救行為", "2.3.5", "high"),
        (r"違法性阻却|違法性の本質|可罰的違法", "2.3.1", "med"),
        # 責任
        (r"原因において自由な行為", "2.4.3", "high"),
        (r"責任能力|心神喪失|心神耗弱|責任年齢", "2.4.2", "high"),
        (r"誤想防衛|違法性の意識|法律の錯誤|禁止の錯誤", "2.4.4", "high"),
        (r"期待可能性", "2.4.5", "high"),
        (r"責任の本質|責任主義", "2.4.1", "high"),
        # 未遂
        (r"中止犯|中止未遂", "2.5.2", "high"),
        (r"不能犯", "2.5.3", "high"),
        (r"実行の着手|既遂|未遂罪|未遂犯|犯罪の成立時期", "2.5.1", "high"),
        # 共犯
        (r"共犯と身分|身分犯の共犯|65条", "2.6.4", "high"),
        (r"共謀共同正犯|承継的共同正犯|承継的共犯|同時傷害の特例|傷害罪の承継", "2.6.2", "high"),
        (r"教唆犯と錯誤|共犯と錯誤|共同正犯と間接正犯|間接正犯と教唆|共犯の諸問題", "2.6.5", "high"),
        (r"間接幇助|間接従犯|幇助犯|教唆犯", "2.6.3", "high"),
        (r"共犯の従属性|要素従属性|共同正犯の本質|共同正犯の主観|正犯・共犯|共同正犯と幇助犯の区別|従犯と共同正犯|共犯総論", "2.6.1", "high"),
        (r"共同正犯", "2.6.2", "med"),
        # 罪数(「罪数論の総合」も罪数。総合規則より前に置く)
        (r"罪数|観念的競合|牽連犯|併合罪|かすがい|科刑上一罪|包括一罪|不可罰的事後行為", "2.7", "high"),
        # 刑罰
        (r"没収|追徴", "3.1", "high"),
        (r"執行猶予|量刑|刑の適用|処断刑|自首|刑の減軽|仮釈放", "3.2", "high"),
        (r"刑罰の意義|刑罰の種類|刑罰の根拠|刑罰論", "3.1", "high"),
        # 個人法益 - 生命身体
        (r"殺人", "4.1.1", "high"),
        (r"傷害|暴行|凶器準備集合|危険運転", "4.1.2", "high"),
        (r"遺棄", "4.1.5", "high"),
        # 自由・私生活
        (r"監禁|逮捕監禁", "4.2.1", "high"),
        (r"脅迫", "4.2.2", "high"),
        (r"略取|誘拐|人身売買", "4.2.3", "high"),
        (r"不同意性交|不同意わいせつ|監護者|性的自由", "4.2.4", "high"),
        (r"住居侵入|建造物侵入|住居を侵す|住居侵入等", "4.2.5", "high"),
        (r"業務妨害|業務に対する罪|信用及び業務", "4.2.6", "high"),
        (r"秘密漏示|秘密を侵す", "4.2.7", "high"),
        # 名誉信用
        (r"名誉毀損|侮辱|名誉に対する|真実性の証明", "4.3.1", "high"),
        (r"信用毀損|信用に対する", "4.3.2", "high"),
        # 財産
        (r"詐欺", "4.4.4", "high"),
        (r"恐喝", "4.4.5", "high"),
        (r"横領|不法原因給付", "4.4.6", "high"),
        (r"背任", "4.4.7", "high"),
        (r"盗品", "4.4.8", "high"),
        (r"毀棄|損壊|器物損壊|信書隠匿|文書毀棄|隠匿の罪", "4.4.9", "high"),
        (r"事後強盗|強盗殺人|強盗致傷|強盗致死|強盗利得|2項強盗|昏酔強盗|ひったくりと強盗|居直り強盗|強盗予備|強盗", "4.4.3", "high"),
        (r"窃盗", "4.4.2", "high"),
        (r"不法領得の意思|死者の占有|本権説|所持説|財産罪の客体|親族相盗|親族間の犯罪", "4.4.1", "high"),
        (r"財産犯総合|財産罪の成否|財産犯の成否|奪取罪と交付罪|共犯と財産犯", "4.4.10", "med"),
        # 社会法益
        (r"放火|焼損|失火|延焼|公共の危険", "5.1.2", "high"),
        (r"通貨偽造|偽札", "5.3.1", "med"),
        (r"有価証券偽造", "5.3.3", "med"),
        (r"文書偽造|公文書偽造|私文書偽造|有形偽造|無形偽造|偽造罪|各種偽造|偽造公文書", "5.3.2", "high"),
        (r"わいせつ物|わいせつの罪|わいせつ罪|頒布|賭博|風俗", "5.4", "high"),
        # 国家法益
        (r"公務執行妨害", "6.2.1", "high"),
        (r"逃走", "6.2.2", "high"),
        (r"犯人蔵匿|犯人隠避|証拠隠滅|証拠偽造", "6.2.3", "high"),
        (r"偽証", "6.2.4", "high"),
        (r"虚偽告訴", "6.2.5", "high"),
        (r"収賄|賄賂|汚職|職権濫用", "6.2.6", "high"),
        # 総合(最後の受け皿)
        (r"総合事例|各論横断|各種の?犯罪|犯罪の成[立否]|故意の総合", "7", "med"),
    ],
}


def load_tree(subject):
    p = os.path.join(ROOT, "references", "topics", subject + ".json")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    # node id → name, leaf 判定
    nodes, leaves = {}, set()
    def walk(n):
        nodes[n["id"]] = n["name"]
        ch = n.get("children")
        if ch:
            for c in ch:
                walk(c)
        else:
            leaves.add(n["id"])
    for n in data["tree"]:
        walk(n)
    return data, nodes, leaves


def parse_title(raw):
    """<title> 文字列 → (code, topic, qid_raw)"""
    raw = raw.strip()
    m = re.match(r"^(\S+?TX\d+)\s*(?:[-–｜:：]|\s)\s*(.*)$", raw)
    if not m:
        return None, raw, ""
    code, rest = m.group(1), m.group(2).strip()
    # 末尾の （…過去問ID…） を qid_raw として剥がす
    qid_raw = ""
    qm = re.search(r"[（(]([^（）()]*(?:H|R|平成|令和|司法|予備|共通)[^（）()]*)[)）]\s*$", rest)
    if qm:
        qid_raw = qm.group(1)
    topic = re.sub(r"[（(][^（）()]*[)）]\s*$", "", rest).strip()
    return code, (topic or rest), qid_raw


def map_title(subject, code, raw_title):
    ov = OVERRIDE.get(subject, {})
    if code in ov:
        return ov[code], "high", True   # override は review 済みとして true フラグ
    for pat, node, conf in RULES.get(subject, []):
        if re.search(pat, raw_title):
            return node, conf, False
    return None, None, False


def build(subject, check=False):
    subdir = SUBJECT_DIR[subject]
    lex_glob = os.path.join(ROOT, "outputs", "ux", "000_TX", subdir, "*_lex.html")
    files = sorted(glob.glob(lex_glob))
    if not files:
        print("!! _lex ファイルが見つからない: " + lex_glob)
        return

    data, nodes, leaves = load_tree(subject)

    mp = {}
    review, unmapped = [], []
    for f in files:
        with open(f, encoding="utf-8", errors="ignore") as fh:
            head = fh.read(4000)
        tm = re.search(r"<title>([^<]*)</title>", head)
        if not tm:
            continue
        code, topic, qid_raw = parse_title(tm.group(1))
        if not code:
            continue
        node, conf, forced = map_title(subject, code, tm.group(1))
        if node is None:
            unmapped.append((code, topic))
            continue
        entry = {"node": node, "topic": topic, "qid_raw": qid_raw,
                 "src": "title-fuzzy", "conf": conf}
        if forced:
            entry["conf"] = "high"
            entry["src"] = "override"
        mp[code] = entry
        if conf == "med" and not forced:
            review.append((code, topic, node, nodes.get(node, "?")))

    # ── coverage 集計 ──
    per_node = {}
    for code, e in mp.items():
        per_node.setdefault(e["node"], []).append(code)
    empty_leaves = [lid for lid in sorted(leaves) if lid not in per_node]

    # ── レポート ──
    print("=== topic-map build: {} ===".format(subject))
    print("TX total mapped : {} / files {}".format(len(mp), len(files)))
    print("unmapped        : {}".format(len(unmapped)))
    print("review(med conf): {}".format(len(review)))
    print("leaves total    : {}   未収録(0本) : {}".format(len(leaves), len(empty_leaves)))
    print()
    print("--- 未収録リーフ(TX 0本 = カバレッジの穴 = 発注書) ---")
    for lid in empty_leaves:
        print("  {:<8} {}".format(lid, nodes.get(lid, "?")))
    if unmapped:
        print("\n--- UNMAPPED(規則に載らず・要ルール追加) ---")
        for code, topic in unmapped:
            print("  {}  {}".format(code, topic))
    if review:
        print("\n--- REVIEW(med conf・人手確認推奨) ---")
        for code, topic, node, nm in review:
            print("  {}  {} -> {} {}".format(code, topic, node, nm))

    if check:
        print("\n[--check] 書き込みなし")
        return

    out = {
        "meta": {
            "subject": subject,
            "generatedBy": "scripts/build-topic-map.py (経路2 title-fuzzy)",
            "sourceTitles": "outputs/ux/000_TX/{}/*_lex.html の <title>".format(subdir),
            "treeVersion": data.get("meta", {}).get("version", "?"),
            "note": "過去問ID→ノードではなく TX code→ノード(Lexia の安定キー=問題コード)。"
                    "conf=med と override は人手確認対象。年度別索引(経路1)取得後に精緻化する。",
        },
        "map": mp,
    }
    outdir = os.path.join(ROOT, "references", "topic-map")
    os.makedirs(outdir, exist_ok=True)
    outp = os.path.join(outdir, subject + ".json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n[written] " + os.path.relpath(outp, ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.subject not in SUBJECT_DIR:
        print("unknown subject: " + a.subject); sys.exit(1)
    build(a.subject, a.check)
