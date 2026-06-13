#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v11.0.0 LOOP-CORE 深掘り別冊（-deep.html）検証スクリプト

spec: spec/tx-v11.0.0-core.md 第5項・第7項

別冊（-deep.html）の構成：
  D-1 記述別補講（教授③イメージ・④あてはめ＋誤読パターン・他肢対比）
  D-2 参考条文・判例 完全プロファイル（【事案】【審級経過】【判旨原文】【補足・反対意見】）
  D-3 総合フローチャート（flow-svg）  D-4 PART C（c-1〜c-7）
  ※ PART D（12問ドリル）は v11 で廃止＝存在してはならない

検証（D1〜D13）：
  D1  head/style 存在
  D2  構造：#d-1（補講）・#basis（完全プロファイル）・#c-1〜#c-7（PART C）存在
  D3  SVG：flow-svg 存在／tree-svg・radial-svg は core 専用＝不在
  D4  flow-svg ボックス AABB 衝突 0（G10 継承）
  D5  flow-svg viewBox 下端余白（G11 継承）
  D6  SVG class 整合（G16 継承）
  D7  完全プロファイル存在：判例カードに <strong>【事案/判旨/補足】 がある（core と逆＝別冊必須）
  D8  PART D 不在：drill-block / recall-arena / #part-d が body に無い
  D9  禁止句（G21 継承）
  D10 feature-tag 先頭が "TX v11.0.0 LOOP-CORE DEEP"
  D11 KTX301 由来禁止文言の不出現（G12 継承）
  D12 コアファイル存在：{ID}-deep.html に対し {ID}.html が同階層に存在（単独生成の禁止）
  D13 教授③④存在：prof-num 3 と 4 が body にある

使い方：
    python scripts/validate-tx-deep.py <HTML ファイルパス>
例：
    python scripts/validate-tx-deep.py canonical/GENESIS-DEEP.html
要件：
    pip install beautifulsoup4
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。pip install beautifulsoup4")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_DEEP = REPO_ROOT / "canonical" / "GENESIS-DEEP.html"

FORBIDDEN_PHRASES = [
    "正解は肢", "組合せ全体", "組合せ不成立",
    "消去法", "絞り込", "分かれば正解", "切れれば", "判断できれば肢",
]
CANONICAL_301_LEAKAGE = [
    "詐欺罪と他罪の成否", "背任行為が同時に詐欺の欺罔行為に当たる", "畏怖の一材料",
    "集金業務を委託", "偽造通貨行使罪に包含", "最判昭28.5.8", "東京高判昭28.6.12",
]


# --- bbox helpers（validate-tx-gold.py と同一）---

def parse_translate(s):
    if not s:
        return (0.0, 0.0)
    m = re.search(r"translate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*\)", s)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def get_rect_bbox(el, t=(0.0, 0.0)):
    try:
        x = float(el.get("x", 0)); y = float(el.get("y", 0))
        w = float(el.get("width", 0)); h = float(el.get("height", 0))
    except (TypeError, ValueError):
        return None
    return (x + t[0], x + t[0] + w, y + t[1], y + t[1] + h)


def get_ellipse_bbox(el, t=(0.0, 0.0)):
    try:
        cx = float(el.get("cx", 0)); cy = float(el.get("cy", 0))
        rx = float(el.get("rx", 0)); ry = float(el.get("ry", 0))
    except (TypeError, ValueError):
        return None
    return (cx + t[0] - rx, cx + t[0] + rx, cy + t[1] - ry, cy + t[1] + ry)


def collect_svg_boxes(svg):
    boxes = []
    for sh in svg.find_all(["rect", "ellipse"]):
        tx, ty = 0.0, 0.0
        cur = sh.parent
        while cur is not None and cur.name == "g":
            ax, ay = parse_translate(cur.get("transform", ""))
            tx += ax; ty += ay; cur = cur.parent
        bbox = get_rect_bbox(sh, (tx, ty)) if sh.name == "rect" else get_ellipse_bbox(sh, (tx, ty))
        if bbox:
            cls = " ".join(sh.get("class", []))
            boxes.append((f"{sh.name}.{cls}" if cls else sh.name, bbox))
    return boxes


def overlap(b1, b2):
    return b1[0] < b2[1] and b1[1] > b2[0] and b1[2] < b2[3] and b1[3] > b2[2]


def contained(s, b):
    return s[0] >= b[0] and s[1] <= b[1] and s[2] >= b[2] and s[3] <= b[3]


class Validator:
    def __init__(self, p):
        self.path = Path(p)
        self.html = self.path.read_text(encoding="utf-8")
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.errors = []
        self.warnings = []

    def err(self, c, m):
        self.errors.append((c, m))

    def warn(self, c, m):
        self.warnings.append((c, m))

    def _body_text(self):
        b = self.soup.find("body")
        return b.get_text() if b else ""

    def d1_head(self):
        if not self.soup.find("head"):
            self.err("D1", "<head> が無い")
        if not self.soup.find("style"):
            self.err("D1", "<style> が無い")

    def d2_structure(self):
        if not self.soup.find(id="d-1"):
            self.err("D2", "D-1 記述別補講（#d-1）が無い")
        if not self.soup.find(id="basis"):
            self.err("D2", "D-2 参考条文・判例 完全プロファイル（#basis）が無い")
        missing = [c for c in ["c-1", "c-2", "c-3", "c-4", "c-5", "c-6", "c-7"] if not self.soup.find(id=c)]
        if missing:
            self.err("D2", f"PART C のセクションが不足: {missing}")

    def d3_svg(self):
        self.flow = self.soup.find("svg", class_="flow-svg")
        if not self.flow:
            self.err("D3", "flow-svg（総合フローチャート）が無い")
        if self.soup.find("svg", class_="tree-svg"):
            self.err("D3", "tree-svg が別冊に存在する（体系ツリーは core 専用）")
        if self.soup.find("svg", class_="radial-svg"):
            self.err("D3", "radial-svg が別冊に存在する（放射マップは core 専用）")

    def d4_overlap(self):
        if not getattr(self, "flow", None):
            return
        boxes = collect_svg_boxes(self.flow)
        n = len(boxes)
        for i in range(n):
            for j in range(i + 1, n):
                la, ba = boxes[i]; lb, bb = boxes[j]
                if overlap(ba, bb) and not (contained(ba, bb) or contained(bb, ba)):
                    self.err("D4", f"[flow] {la} と {lb} が重なる (bbox {ba} vs {bb})")

    def d5_viewbox(self):
        if not getattr(self, "flow", None):
            return
        vb = self.flow.get("viewbox") or self.flow.get("viewBox") or ""
        parts = vb.split()
        if len(parts) != 4:
            self.warn("D5", f"flow-svg viewBox 解析不可: {vb}")
            return
        try:
            vb_h = float(parts[3])
        except ValueError:
            return
        boxes = collect_svg_boxes(self.flow)
        if not boxes:
            return
        margin = vb_h - max(b[1][3] for b in boxes)
        if margin < 20:
            self.err("D5", f"flow-svg viewBox 下端余白 {margin:.0f}px（20px 未満）")
        elif margin < 40:
            self.warn("D5", f"flow-svg viewBox 下端余白 {margin:.0f}px（推奨 40px 以上）")

    def d6_svg_class(self):
        defined = set()
        for st in self.soup.find_all("style"):
            for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_-]*)", st.get_text()):
                defined.add(m.group(1))
        tags = {"rect", "text", "ellipse", "polygon", "circle", "line", "path", "g"}
        undef = set()
        for svg in self.soup.find_all("svg"):
            for el in svg.find_all(True):
                if el.name not in tags:
                    continue
                for c in (el.get("class") or []):
                    if c and c not in defined:
                        undef.add((el.name, c))
        if undef:
            self.err("D6", f"SVG 内に未定義 class {len(undef)} 種（黒塗りリスク）: {list(undef)[:5]}")

    def d7_full_profile(self):
        # 別冊 D-2 は完全プロファイル必須（core と逆）
        if not any(f"<strong>{lbl}" in self.html for lbl in ("【事案】", "【判旨】")):
            self.err("D7", "判例の完全プロファイル（<strong>【事案】/【判旨】）が D-2 に無い"
                          "（別冊は完全プロファイルを収める・spec D-2）")

    def d8_no_part_d(self):
        body = self.soup.find("body")
        if not body:
            return
        if body.find(id="part-d"):
            self.err("D8", "#part-d が存在する（PART D は廃止・spec 原理3）")
        if body.find(class_="recall-arena"):
            self.err("D8", ".recall-arena が存在する（PART D 廃止）")
        if body.find(class_="drill-block"):
            self.err("D8", "drill-block が存在する（12問クイズ廃止）")

    def d9_forbidden(self):
        text = self._body_text()
        for ph in FORBIDDEN_PHRASES:
            if ph in text:
                self.err("D9", f"禁止句が出現: '{ph}'")

    def d10_version_tag(self):
        footer = self.soup.find("div", class_="footer-spec")
        if not footer:
            self.err("D10", ".footer-spec が無い")
            return
        tags = footer.find_all(class_="feature-tag")
        if not tags:
            self.err("D10", "feature-tag が無い")
            return
        first = tags[0].get_text().strip()
        if not first.startswith("TX v11.0.0 LOOP-CORE DEEP"):
            self.err("D10", f"feature-tag 先頭が 'TX v11.0.0 LOOP-CORE DEEP' でない: '{first}'")

    def d11_no_301(self):
        text = self._body_text()
        for ph in CANONICAL_301_LEAKAGE:
            if ph in text:
                self.err("D11", f"KTX301 由来禁止文言が残存: '{ph}'")

    def d12_core_exists(self):
        if self.path.parent.name == "canonical":
            return
        stem = self.path.stem
        if not stem.endswith("-deep"):
            self.err("D12", f"別冊ファイル名は '{{ID}}-deep' であるべき: '{stem}'")
            return
        core = self.path.with_name(stem[:-5] + ".html")
        if not core.exists():
            self.err("D12", f"対応するコアファイルが無い: {core.name}（別冊の単独生成は禁止・spec 第7項）")

    def d13_prof_34(self):
        if "prof-num\">3" not in self.html or "prof-num\">4" not in self.html:
            self.warn("D13", "教授③④（prof-num 3/4）が D-1 に見当たらない")

    def run(self):
        self.d1_head()
        self.d2_structure()
        self.d3_svg()
        self.d4_overlap()
        self.d5_viewbox()
        self.d6_svg_class()
        self.d7_full_profile()
        self.d8_no_part_d()
        self.d9_forbidden()
        self.d10_version_tag()
        self.d11_no_301()
        self.d12_core_exists()
        self.d13_prof_34()


def main():
    if len(sys.argv) != 2:
        print("使い方: python scripts/validate-tx-deep.py <HTML ファイルパス>")
        sys.exit(2)
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"❌ ファイルが見つからない: {p}")
        sys.exit(2)

    print(f"\n=== TX v11.0.0 LOOP-CORE DEEP 検証: {p.name} ===\n")
    v = Validator(p)
    v.run()

    print(f"File size: {p.stat().st_size:,} bytes")
    print(f"Errors:    {len(v.errors)}")
    print(f"Warnings:  {len(v.warnings)}\n")

    if v.errors:
        print("--- ERRORS ---")
        for c, m in v.errors:
            print(f"  ❌ [{c}] {m}")
        print()
    if v.warnings:
        print("--- WARNINGS ---")
        for c, m in v.warnings:
            print(f"  ⚠️  [{c}] {m}")
        print()

    if not v.errors:
        print("✅ ALL D1〜D13 PASS")
        sys.exit(0)
    else:
        print("❌ FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
