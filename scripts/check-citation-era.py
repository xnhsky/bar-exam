#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
判例引用・元号の割れ検出ゲート（恒久対策・2026-07-09）

コーパスを横断走査し、**同一の裁判所種別＋数値の年月日が、異なる元号で
引かれている**箇所を検出する。OCR/転記で 大↔昭↔明↔平 が入れ替わる誤記
（例：大判大9.5.8 が別ファイルで 大判昭9.5.8）を機械的にあぶり出す。

なぜ WARNING/allowlist 方式か（179 の教訓）:
  同一日付でも「別論点の別判例」が実在しうる。
  実例：大判大10.10.24（業務妨害「業務」の定義）と
        大判昭10.10.24（従犯の共同正犯・刑集14輯1267頁）は別事件。
  よって割れ＝即誤記ではない。**割れを検出し、一次確認で「正当な別判例」と
  確定したペアは allowlist に登録して抑止**、未確認の新規の割れだけを
  gate（exit 1）で止める。確定はあくまで判例百選・刑録/刑集・裁判所検索で行う。
  （CLAUDE.md §省エネ規律(c)「的絞りWeb一次確認」の機械的入口）

検出単位:
  (裁判所トークン, 数値年, 月, 日) でグルーピングし、元号（明/大/昭/平/令）の
  集合サイズが 2 以上のクラスタを「割れ」とする。allowlist 済みは抑止。

対応表記:
  短縮形  … 大判昭9.5.8 / 最決平29.5.27 / 最判昭23.10.23
  完全形  … 大判大正9年3月16日 / 最決昭和29年5月27日
  裁判所トークン … 最大判/最大決/最判/最決/大判/大決/大連判/大連決/
                    高判/高決/地判/地決/家審/簡判（前方一致で貪欲一致）

使い方:
    python scripts/check-citation-era.py                    # 既定 outputs/ を走査
    python scripts/check-citation-era.py outputs deploy     # 複数ルート
    python scripts/check-citation-era.py --list             # 全引用の分布を出力（棚卸し用）

allowlist:
    scripts/citation-era-allowlist.txt
    1 行 = `裁判所|年|月|日  # 一次確認メモ`（# 以降は注記）。空行と # 始まりは無視。

割れ（allowlist 未登録）を検出すると exit 1 を返す。push 前ゲートや
check-tx-lex-engine の後段に噛ませられる。
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

# --- 元号正規化（完全形→単字） ---
ERA_FULL = {"明治": "明", "大正": "大", "昭和": "昭", "平成": "平", "令和": "令"}
ERA_ONE = set("明大昭平令")

# 裁判所トークン（長いものを先に＝貪欲一致）
COURTS = [
    "最大判", "最大決", "大連判", "大連決",
    "最判", "最決", "大判", "大決",
    "東京高判", "東京高決", "大阪高判", "大阪高決",
    "高判", "高決", "地判", "地決", "家審", "簡判", "簡決",
]
_COURT_ALT = "|".join(COURTS)

# 短縮形: <court><era1><y>.<m>.<d>
RE_SHORT = re.compile(
    rf"(?P<court>{_COURT_ALT})(?P<era>[明大昭平令])(?P<y>\d{{1,2}})[.．](?P<m>\d{{1,2}})[.．](?P<d>\d{{1,2}})"
)
# 完全形: <court><era-word><y>年<m>月<d>日
RE_FULL = re.compile(
    rf"(?P<court>{_COURT_ALT})(?P<eraw>明治|大正|昭和|平成|令和)(?P<y>\d{{1,2}})年(?P<m>\d{{1,2}})月(?P<d>\d{{1,2}})日"
)

Z2H = str.maketrans("０１２３４５６７８９", "0123456789")


def load_allowlist(script_dir: Path):
    """確認済み『正当な別判例』ペア。key=(court,y,m,d) の集合を返す。"""
    allow = {}
    f = script_dir / "citation-era-allowlist.txt"
    if not f.exists():
        return allow
    for raw in f.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        body, _, note = line.partition("#")
        parts = [p.strip() for p in body.strip().split("|")]
        if len(parts) == 4:
            court, y, m, d = parts
            allow[(court, int(y), int(m), int(d))] = note.strip()
    return allow


def scan_file(path: Path, clusters):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return
    lines = text.split("\n")
    for lineno, line in enumerate(lines, 1):
        s = line.translate(Z2H)
        for mo in RE_SHORT.finditer(s):
            _add(clusters, path, lineno, mo.group("court"), mo.group("era"),
                 mo.group("y"), mo.group("m"), mo.group("d"), mo.group(0))
        for mo in RE_FULL.finditer(s):
            _add(clusters, path, lineno, mo.group("court"), ERA_FULL[mo.group("eraw")],
                 mo.group("y"), mo.group("m"), mo.group("d"), mo.group(0))


def _add(clusters, path, lineno, court, era, y, m, d, raw):
    key = (court, int(y), int(m), int(d))
    clusters[key].setdefault(era, []).append((path, lineno, raw))


def collect(roots):
    clusters = defaultdict(dict)  # key -> {era: [(path,line,raw),...]}
    seen = set()
    for root in roots:
        rp = Path(root)
        if not rp.exists():
            continue
        for html in rp.rglob("*.html"):
            rk = html.resolve()
            if rk in seen:
                continue
            seen.add(rk)
            scan_file(html, clusters)
    return clusters


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    roots = args if args else ["outputs"]
    script_dir = Path(__file__).resolve().parent
    allow = load_allowlist(script_dir)
    clusters = collect(roots)

    if "--list" in flags:
        for key in sorted(clusters):
            court, y, m, d = key
            eras = clusters[key]
            n = sum(len(v) for v in eras.values())
            era_s = "".join(sorted(eras))
            print(f"{court}{era_s}{y}.{m}.{d}  ({n}件 / 元号{len(eras)}種)")
        return 0

    conflicts = {k: v for k, v in clusters.items() if len(v) >= 2}
    new_conf = {k: v for k, v in conflicts.items() if k not in allow}
    allowed = {k: v for k, v in conflicts.items() if k in allow}

    if allowed:
        print(f"[INFO] allowlist で抑止した確認済みの割れ: {len(allowed)} 件")
        for key in sorted(allowed):
            court, y, m, d = key
            print(f"   ・{court}{y}.{m}.{d}（{''.join(sorted(allowed[key]))}）— {allow[key]}")

    total_cites = sum(len(occ) for eras in clusters.values() for occ in eras.values())
    if not new_conf:
        print(f"[OK] 未確認の元号割れなし（走査 {total_cites} 引用 / {len(clusters)} 日付 / ルート {roots}）")
        return 0

    print(f"\n[ERROR] 未確認の元号割れ {len(new_conf)} 件（一次確認して是正 or allowlist へ登録）:")
    for key in sorted(new_conf):
        court, y, m, d = key
        eras = new_conf[key]
        print(f"\n  ■ {court}〔{'/'.join(sorted(eras))}〕{y}.{m}.{d}")
        for era in sorted(eras):
            for path, lineno, raw in eras[era]:
                print(f"      {era}: {path}:{lineno}  …{raw}")
    print("\n  → 判例百選/刑録刑集/裁判所裁判例検索で正しい元号を確定。")
    print("     誤記なら可視ラベルを是正（アンカーidは不変）。正当な別判例なら")
    print("     scripts/citation-era-allowlist.txt に `裁判所|年|月|日  # メモ` を追記。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
