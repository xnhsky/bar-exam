#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v11.0.0 LOOP-CORE 自己検証スクリプト（コア＝メイン HTML 用）

spec: spec/tx-v11.0.0-core.md 第7項

検証範囲（v10 GOLD の validate-tx-gold.py から派生）：
  継承：G1〜G3（構造）／G5〜G8（footer・配色）／G12〜G14（独立性・命名）／G16（SVG class）／
        G19（解答前ネタバレ）
  改定：
    G4  → コア構造（記述単位 PART B 5本＋参考条文判例＋体系/放射マップ。PART C/D は無い）
    G9  → SVG はコアに体系ツリー＋放射マップの2枚。フローチャートは別冊専用＝不在を要求
    G10 → AABB 衝突（tree+radial の2枚）
    G11 → viewBox 余白（tree+radial の2枚）
    G15 → feature-tag 先頭が "TX v11.x.x LOOP-CORE"（v11.0.0／v11.1.0 等）
  新設（v11 中核）：
    G20 記述単位検査：choice-section の見出しバッジが単一記述（ア〜オ）。組合せ見出しを禁止
    G21 禁止句検査：組合せ導出・選択戦略語彙が body に出現しない
    G22 choice-points 規律：論点コアに「本記述は誤り/正しい」「記述[ア-オ]は」「正解は肢」が無い
    G23 reveal 記述○×一覧表：.final-answer 内に data-answer-key 付き表が存在（肢データ源）
    G24 参考条文判例の深度：ラベル付き完全プロファイル（<strong>【事案/判旨/補足】）が無い
    G25 PART A ox-grid：data-answer-type="ox-grid" で 5 記述の○×を収集
    G26 PART D 不在：drill-block / recall-arena / #part-d / flow-svg が無い
    G29 答え整合：data-correct-value（位置）と data-answer-key（ラベル）が記述ごとに一致し、
        各文字が全角○/×（半角 x/o 混入＝Lexia で判定不能を検出）
  廃止：G17・G18（PART D 関連）

使い方：
    python scripts/validate-tx-core.py <HTML ファイルパス>
例：
    python scripts/validate-tx-core.py canonical/GENESIS-CORE.html
要件：
    pip install beautifulsoup4
"""

import copy
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


# ============================================================
# 定数
# ============================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_CORE = REPO_ROOT / "canonical" / "GENESIS-CORE.html"
BASELINE_301 = REPO_ROOT / "canonical" / "KTX301.html"

JP_PREFIX_TO_DIR = {
    # 2026-06-20: 出力フォルダ 00N_科目 統一（commit 368759b refactor）に追従。
    # 旧マッピング（刑TX→"刑TX" 等）は stale で正しく配置した全ファイルが G14 で誤 ERROR になっていた。
    "刑TX": "001_刑法", "憲TX": "007_憲法", "民TX": "003_民法", "商TX": "004_商法",
    "民訴TX": "005_民事訴訟法", "刑訴TX": "002_刑事訴訟法", "行政TX": "006_行政法",
}

REQUIRED_CSS_VARS_MAIN = ["--accent", "--mid", "--light", "--base", "--soft", "--bg-dark"]
REQUIRED_CSS_VARS_DERIVATIVES = ["--accent-darker", "--accent-soft", "--accent-3", "--border-mid", "--kp-text-color"]

PALETTE_LEAKAGE_PATTERNS_HEADER = [
    r"配色\s*[:：]", r"P[123][\s　]*[「『]", r"AI\s*自由選定",
    r"Sweet\s*Berry", r"Fresh\s*Citrus", r"Rose\s*Mist", r"Antique\s*Pearl",
    r"Maison\s*Blanche", r"Crystal\s*Blue", r"Dusty\s*Sage", r"Mint\s*Tea",
    r"Fresh\s*Mint", r"Twilight\s*Violet", r"Sunset\s*Harmony",
    r"ベース\s*70\s*%", r"メイン\s*25\s*%", r"アクセント\s*5\s*%",
]

# G21：組合せ導出・選択戦略語彙（第一原理＝解説の対象は記述であって肢ではない・spec 第4項）
FORBIDDEN_PHRASES = [
    "正解は肢", "組合せ全体", "組合せ不成立",
    "消去法", "絞り込", "分かれば正解", "切れれば", "判断できれば肢",
]
# G22：choice-points 内で禁止（論点コアに混ぜてはならない）
CHOICE_POINTS_FORBIDDEN = [r"本記述は誤り", r"本記述は正しい", r"記述[アイウエオ]は", r"正解は肢"]

# G19：解答前ネタバレ
ANSWER_SPOILER_VISIBLE_PATTERNS = [
    r"正解は[肢記述]?[0-9０-９]", r"正しいのは[肢記述]*[0-9０-９]",
    r"誤っているのは[肢記述]*[0-9０-９]", r"誤りは[肢記述]*[0-9０-９]",
    r"答え?は[肢記述][0-9０-９]",
]

CANONICAL_301_LEAKAGE = [
    "詐欺罪と他罪の成否", "詐欺罪のみが成立し得る", "背任行為が同時に詐欺の欺罔行為に当たる",
    "畏怖の一材料", "集金業務を委託", "偽造通貨行使罪に包含", "最判昭28.5.8",
    "東京高判昭28.6.12", "大判明43.6.30", "新聞販売店から集金業務を委託",
]


# ============================================================
# ヘルパー：bounding box（validate-tx-gold.py と同一）
# ============================================================

def parse_translate(transform_str):
    if not transform_str:
        return (0.0, 0.0)
    m = re.search(r"translate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*\)", transform_str)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def get_rect_bbox(rect_el, parent_translate=(0.0, 0.0)):
    try:
        x = float(rect_el.get("x", 0)); y = float(rect_el.get("y", 0))
        w = float(rect_el.get("width", 0)); h = float(rect_el.get("height", 0))
    except (TypeError, ValueError):
        return None
    tx, ty = parent_translate
    return (x + tx, x + tx + w, y + ty, y + ty + h)


def get_ellipse_bbox(el_el, parent_translate=(0.0, 0.0)):
    try:
        cx = float(el_el.get("cx", 0)); cy = float(el_el.get("cy", 0))
        rx = float(el_el.get("rx", 0)); ry = float(el_el.get("ry", 0))
    except (TypeError, ValueError):
        return None
    tx, ty = parent_translate
    return (cx + tx - rx, cx + tx + rx, cy + ty - ry, cy + ty + ry)


def get_polygon_bbox(poly_el, parent_translate=(0.0, 0.0)):
    coords = re.findall(r"(-?[\d.]+)[,\s]+(-?[\d.]+)", poly_el.get("points", ""))
    if not coords:
        return None
    xs = [float(p[0]) for p in coords]; ys = [float(p[1]) for p in coords]
    tx, ty = parent_translate
    return (min(xs) + tx, max(xs) + tx, min(ys) + ty, max(ys) + ty)


def collect_svg_boxes(svg_el):
    boxes = []
    for shape in svg_el.find_all(["rect", "ellipse", "polygon"]):
        tx, ty = 0.0, 0.0
        cur = shape.parent
        while cur is not None and cur.name == "g":
            ax, ay = parse_translate(cur.get("transform", ""))
            tx += ax; ty += ay; cur = cur.parent
        parent_t = (tx, ty)
        if shape.name == "rect":
            bbox = get_rect_bbox(shape, parent_t)
        elif shape.name == "ellipse":
            bbox = get_ellipse_bbox(shape, parent_t)
        else:
            bbox = get_polygon_bbox(shape, parent_t)
        if bbox is None:
            continue
        cls = " ".join(shape.get("class", []))
        boxes.append((f"{shape.name}.{cls}" if cls else shape.name, bbox))
    return boxes


def boxes_overlap(b1, b2):
    x1n, x1x, y1n, y1x = b1; x2n, x2x, y2n, y2x = b2
    return x1n < x2x and x1x > x2n and y1n < y2x and y1x > y2n


# ============================================================
# 検証本体
# ============================================================

class Validator:
    def __init__(self, html_path):
        self.html_path = Path(html_path)
        self.html = self.html_path.read_text(encoding="utf-8")
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.errors = []
        self.warnings = []

    def err(self, code, msg):
        self.errors.append((code, msg))

    def warn(self, code, msg):
        self.warnings.append((code, msg))

    # --- G1〜G3：構造 ---

    def g1_head(self):
        if not self.soup.find("head"):
            self.err("G1", "<head> が存在しない")
        if not self.soup.find("style"):
            self.err("G1", "<style> ブロックが存在しない")

    def g2_header(self):
        header = self.soup.find("header", class_="header")
        if not header:
            self.err("G2", "<header class='header'> が存在しない")
            return
        if not header.find("div", class_="doc-header"):
            self.err("G2", ".doc-header が <header> 内にない")
        if not header.find("h1"):
            self.err("G2", "<h1> が <header> 内にない")

    def g3_part_a(self):
        if not self.soup.find(id="part-a"):
            self.err("G3", "section#part-a が存在しない")
        if not self.soup.find(class_="answer-area"):
            self.err("G3", ".answer-area が存在しない")
        if not self.soup.find("button", class_="reveal-answer-btn"):
            self.err("G3", ".reveal-answer-btn が存在しない")

    # --- G4：コア構造（記述単位 PART B＋参考条文判例＋2 マインドマップ）---

    def g4_core_structure(self):
        choice_sections = self.soup.find_all("section", class_="choice-section")
        if len(choice_sections) < 2:
            self.err("G4", f"記述別 choice-section が {len(choice_sections)} 個（記述ア〜オで通常 5 を期待）")
        if not self.soup.find(id="basis"):
            self.err("G4", "参考条文・判例セクション（#basis）が存在しない")
        if not self.soup.find(id="mindmap-tree"):
            self.err("G4", "体系ツリー（#mindmap-tree）が存在しない")
        if not self.soup.find(id="mindmap-radial"):
            self.err("G4", "放射マップ（#mindmap-radial）が存在しない")

    def g5_footer(self):
        footer = self.soup.find("div", class_="footer-spec")
        if not footer:
            self.err("G5", ".footer-spec が存在しない")
            return
        if not footer.find(class_="footer-problem"):
            self.err("G5", ".footer-problem が存在しない")
        if not footer.find(class_="footer-meta-hidden"):
            self.err("G5", ".footer-meta-hidden（feature-tag コンテナ）が存在しない")

    # --- G6〜G8：配色 ---

    def _root_block(self):
        chunks = []
        for style in self.soup.find_all("style"):
            css = style.get_text()
            i = 0
            while True:
                m = re.search(r":root\s*\{", css[i:])
                if not m:
                    break
                start = i + m.end(); depth = 1; j = start
                while j < len(css) and depth > 0:
                    if css[j] == "{":
                        depth += 1
                    elif css[j] == "}":
                        depth -= 1
                    j += 1
                if depth == 0:
                    chunks.append(css[start:j - 1]); i = j
                else:
                    break
        return "\n".join(chunks)

    def g6_main_vars(self):
        root = self._root_block()
        if not root:
            self.err("G6", ":root{} ブロックが <style> 内に見つからない")
            return
        for v in REQUIRED_CSS_VARS_MAIN:
            if v + ":" not in root and v + " :" not in root:
                self.err("G6", f"主要 CSS 変数 {v} が :root に定義されていない")

    def g7_derivatives(self):
        root = self._root_block()
        if not root:
            return
        found = sum(1 for v in REQUIRED_CSS_VARS_DERIVATIVES if v + ":" in root or v + " :" in root)
        if found < 3:
            self.err("G7", f"派生色変数が {found} 個しか定義されていない（最低 3 個期待）")
        elif found < len(REQUIRED_CSS_VARS_DERIVATIVES):
            self.warn("G7", f"派生色変数が {found}/{len(REQUIRED_CSS_VARS_DERIVATIVES)} のみ定義")

    def g8_no_palette_in_header_footer(self):
        for cls in ("exam-meta", "footer-meta-info"):
            el = self.soup.find(class_=cls)
            if not el:
                continue
            txt = el.get_text()
            for pat in PALETTE_LEAKAGE_PATTERNS_HEADER:
                if re.search(pat, txt):
                    self.err("G8", f".{cls} に配色情報 '{pat}' が残存")

    # --- G9〜G11：SVG（コアは体系ツリー＋放射マップの2枚）---

    def g9_core_svgs(self):
        self.tree_svg = self.soup.find("svg", class_="tree-svg")
        self.radial_svg = self.soup.find("svg", class_="radial-svg")
        self.flow_svg = self.soup.find("svg", class_="flow-svg")
        if not self.tree_svg:
            self.err("G9", "tree-svg（体系ツリー）が存在しない")
        if not self.radial_svg:
            self.err("G9", "radial-svg（放射マップ）が存在しない")
        if self.flow_svg:
            self.err("G9", "flow-svg（フローチャート）が core に存在する（別冊 -deep 専用・spec 第2項）")

    def g10_no_overlap(self):
        for svg_name, svg in [("tree", self.tree_svg), ("radial", self.radial_svg)]:
            if svg is None:
                continue
            boxes = [b for b in collect_svg_boxes(svg) if not b[0].startswith("polygon")]
            n = len(boxes)
            for i in range(n):
                for j in range(i + 1, n):
                    la, ba = boxes[i]; lb, bb = boxes[j]
                    if boxes_overlap(ba, bb):
                        if self._fully_contained(ba, bb) or self._fully_contained(bb, ba):
                            continue
                        self.err("G10", f"[{svg_name}] {la} と {lb} が重なる (bbox: {ba} vs {bb})")

    @staticmethod
    def _fully_contained(small, big):
        return small[0] >= big[0] and small[1] <= big[1] and small[2] >= big[2] and small[3] <= big[3]

    def g11_viewbox_margin(self):
        for svg_name, svg in [("tree", self.tree_svg), ("radial", self.radial_svg)]:
            if svg is None:
                continue
            vb = svg.get("viewbox") or svg.get("viewBox") or ""
            parts = vb.split()
            if len(parts) != 4:
                self.warn("G11", f"[{svg_name}] viewBox が解析できない: {vb}")
                continue
            try:
                _, _, _, vb_h = (float(p) for p in parts)
            except ValueError:
                continue
            boxes = collect_svg_boxes(svg)
            if not boxes:
                continue
            margin = vb_h - max(b[1][3] for b in boxes)
            if margin < 20:
                self.err("G11", f"[{svg_name}] viewBox 下端余白が {margin:.0f}px（20px 未満）")
            elif margin < 40:
                self.warn("G11", f"[{svg_name}] viewBox 下端余白が {margin:.0f}px（推奨 40px 以上）")

    # --- G12〜G13：content-independence ---

    def _body_text(self):
        body = self.soup.find("body")
        return body.get_text() if body else ""

    def g12_no_301_leakage(self):
        text = self._body_text()
        for phrase in CANONICAL_301_LEAKAGE:
            if phrase in text:
                self.err("G12", f"KTX301 由来禁止文言が残存: '{phrase}'")

    _G13_SHELL_CLASSES = (
        "sec-nav", "sec-icon", "marker-legend", "part-title",
        "answer-instruction", "reveal-answer-btn", "ox-btn", "footer-spec",
    )
    _G13_LEAK_THRESHOLD = 20

    @staticmethod
    def _g13_content_tokens(html_str):
        soup = BeautifulSoup(html_str, "html.parser")
        body = soup.find("body") or soup
        for cls in Validator._G13_SHELL_CLASSES:
            for el in body.select("." + cls):
                el.decompose()
        return re.findall(r"\S+", body.get_text())

    def g13_no_baseline_copy(self):
        if self.html_path.parent.name == "canonical":
            return
        if "311" in self.html_path.stem:
            return
        if not BASELINE_CORE.exists():
            self.warn("G13", f"baseline {BASELINE_CORE.name} が見つからずスキップ")
            return
        baseline_tokens = self._g13_content_tokens(BASELINE_CORE.read_text(encoding="utf-8"))
        baseline_5grams = set()
        for k in range(0, len(baseline_tokens) - 4, 3):
            baseline_5grams.add(" ".join(baseline_tokens[k:k + 5]))
        cur_tokens = self._g13_content_tokens(self.html)
        hits = 0; sample = []
        for k in range(len(cur_tokens) - 4):
            g = " ".join(cur_tokens[k:k + 5])
            if g in baseline_5grams:
                hits += 1
                if len(sample) < 3:
                    sample.append(g)
        if hits >= self._G13_LEAK_THRESHOLD:
            self.err("G13", f"baseline GENESIS-CORE と本文 5-gram が {hits} 件一致"
                            f"（閾値 {self._G13_LEAK_THRESHOLD}・content leakage 疑い）: 例 {sample}")

    # --- G14〜G15：命名・version-tag ---

    def g14_filename_dir(self):
        if self.html_path.parent.name == "canonical":
            return
        stem = self.html_path.stem
        # 別冊は対象外（validate-tx-deep.py が担当）
        if stem.endswith("-deep"):
            return
        # Lexia 用 TX（outputs/ux/000_TX/...）は公式と区別するため末尾 _lex を付ける
        # （刑TX350_lex.html）。ID 形式判定では _lex を正規化して落とす。
        stem = re.sub(r"_lex$", "", stem, flags=re.IGNORECASE)
        m = re.match(r"(刑TX|憲TX|民訴TX|刑訴TX|行政TX|民TX|商TX)(\d{3,})$", stem)
        if not m:
            self.err("G14", f"ファイル名 ID 形式違反: '{stem}'")
            return
        expected_dir = JP_PREFIX_TO_DIR.get(m.group(1))
        if not expected_dir:
            self.err("G14", f"未知の接頭辞: '{m.group(1)}'")
            return
        if self.html_path.parent.name != expected_dir:
            self.err("G14", f"出力先サブフォルダ不整合: 期待 '{expected_dir}'、実際 '{self.html_path.parent.name}'")

    def g15_version_tag(self):
        footer = self.soup.find("div", class_="footer-spec")
        if not footer:
            return
        tags = footer.find_all(class_="feature-tag")
        if not tags:
            self.err("G15", "footer-spec に feature-tag が一つもない")
            return
        first = tags[0].get_text().strip()
        # v11.x.x LOOP-CORE を許容（v11.0.0 既存／v11.1.0 誌面・配色進化版・後方互換）
        if not (first.startswith("TX v11.") and "LOOP-CORE" in first):
            self.err("G15", f"feature-tag 先頭が 'TX v11.x.x LOOP-CORE' でない: '{first}'")

    # --- G16：SVG class 整合性 ---

    def g16_svg_class_defined(self):
        defined = set()
        for style in self.soup.find_all("style"):
            for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_-]*)", style.get_text()):
                defined.add(m.group(1))
        SVG_SHAPE_TAGS = {"rect", "text", "ellipse", "polygon", "circle", "line", "path", "g"}
        undefined = []
        for svg in self.soup.find_all("svg"):
            for el in svg.find_all(True):
                if el.name not in SVG_SHAPE_TAGS:
                    continue
                for c in (el.get("class") or []):
                    if c and c not in defined:
                        undefined.append((el.name, c))
        if undefined:
            unique = set(undefined)
            self.err("G16", f"SVG 内に未定義 class が {len(unique)} 種類あり（黒塗りリスク）: {list(unique)[:5]}")

    # --- G19：解答前ネタバレ ---

    def g19_no_answer_spoiler(self):
        for st in self.soup.find_all(class_="section-title"):
            txt = st.get_text()
            for pat in ANSWER_SPOILER_VISIBLE_PATTERNS:
                if re.search(pat, txt):
                    self.err("G19", f"section-title「{txt.strip()[:40]}」が正解を開示している（'{pat}'）")
                    break
        part_a = self.soup.find(id="part-a")
        if not part_a:
            return
        visible = copy.copy(part_a)
        for el in visible.find_all(attrs={"hidden": True}):
            el.decompose()
        for el in visible.find_all(class_="final-answer"):
            el.decompose()
        for el in visible.find_all(class_="section-title"):
            el.decompose()
        for el in visible.find_all(["script", "style"]):
            el.decompose()
        txt = visible.get_text()
        for pat in ANSWER_SPOILER_VISIBLE_PATTERNS:
            m = re.search(pat, txt)
            if m:
                self.err("G19", f"PART A の可視テキストが正解を開示している（'{m.group(0)}'）")
                break

    # --- G20：記述単位検査 ---

    def g20_statement_unit(self):
        """choice-section の見出しバッジ（.choice-big-badge）が単一記述（ア〜オ）であること。
        組合せ見出し（「ア・イ」「アエ」「1」等）を検出したら ERROR（肢単位への退化）。"""
        for sec in self.soup.find_all("section", class_="choice-section"):
            badge = sec.find(class_="choice-big-badge")
            if not badge:
                self.err("G20", f"choice-section#{sec.get('id')} に .choice-big-badge が無い")
                continue
            label = badge.get_text().strip()
            # 記述ア〜オ（組合せ型）／肢1〜5（単純5択型）の単一記述ラベルを許可。
            # 組合せ見出し（「ア・イ」「アエ」等の複合）は不可（spec 原理1）。
            if not re.fullmatch(r"[アイウエオ1-5１-５]", label):
                self.err("G20", f"choice-section#{sec.get('id')} のバッジ '{label}' が単一記述でない"
                                "（組合せ単位は禁止＝記述ア〜オ／肢1〜5 各1セクション・spec 原理1）")

    # --- G21：禁止句 ---

    def g21_forbidden_phrases(self):
        text = self._body_text()
        for ph in FORBIDDEN_PHRASES:
            if ph in text:
                self.err("G21", f"組合せ導出・選択戦略の禁止句が出現: '{ph}'（spec 第4項）")

    # --- G22：choice-points 規律 ---

    def g22_choice_points(self):
        for cp in self.soup.find_all(class_="choice-points"):
            txt = cp.get_text()
            for pat in CHOICE_POINTS_FORBIDDEN:
                m = re.search(pat, txt)
                if m:
                    self.err("G22", f"choice-points に論点コア外の文言 '{m.group(0)}' が混入"
                                    "（他記述参照・結論再掲・組合せ判定は禁止）")
                    break

    # --- G23：reveal 記述○×一覧表 ---

    def g23_verdict_table(self):
        fa = self.soup.find(class_="final-answer")
        if not fa:
            self.err("G23", ".final-answer（記述○×一覧表のコンテナ）が存在しない")
            return
        table = fa.find("table", attrs={"data-answer-key": True})
        if not table:
            self.err("G23", "記述○×一覧表に data-answer-key（機械可読な答えの鍵）が無い"
                            "（Lexia 肢キー記録の一次情報源・spec 第9項）")
            return
        key = table.get("data-answer-key", "")
        if not re.search(r"[アイウエオ1-5１-５]\s*[:：]\s*[ox]", key):
            self.warn("G23", f"data-answer-key の書式が想定外: '{key}'（例 'ア:x,...' / '1:x,2:o,...'）")

    # --- G24：参考条文判例に完全プロファイル無し ---

    def g24_no_full_profile(self):
        for label in ("【事案】", "【判旨】", "【補足】", "【審級経過】"):
            if f"<strong>{label}" in self.html:
                self.err("G24", f"ラベル付き完全プロファイル '<strong>{label}' が core に存在する"
                                "（事案・判旨原文・補足は別冊 -deep 専用・spec 第2項/D-2）")

    # --- G25：PART A ox-grid ---

    def g25_part_a_oxgrid(self):
        area = self.soup.find(class_="answer-area")
        if not area:
            return  # G3 で報告済
        atype = area.get("data-answer-type", "")
        if atype != "ox-grid":
            self.err("G25", f"PART A の data-answer-type が '{atype}'（ox-grid を期待）"
                            "＝5記述の○×収集が肢データ源・spec 第2項/第9項")
            return
        rows = area.find_all(class_="ox-row")
        if len(rows) < 2:
            self.err("G25", f"ox-row が {len(rows)} 個（記述ア〜オで通常 5 を期待）")
        # data-correct-value が ○× の連結で row 数と一致するか
        cv = area.get("data-correct-value", "")
        if rows and cv and len(cv) != len(rows):
            self.warn("G25", f"data-correct-value 長 {len(cv)} と ox-row 数 {len(rows)} が不一致")

    # --- G26：PART D 不在 ---

    def g26_no_part_d(self):
        if self.soup.find(id="part-d"):
            self.err("G26", "section#part-d が存在する（PART D は v11 で廃止・spec 原理3）")
        if self.soup.find(class_="recall-arena"):
            self.err("G26", ".recall-arena が存在する（PART D は廃止）")
        drills = self.soup.find_all(class_="drill-block")
        if drills:
            self.err("G26", f"drill-block が {len(drills)} 個存在する（12問クイズは廃止・spec 原理3）")

    def g28_choice_premise(self):
        # 学説・見解適用問題のみ対象（WARNING）。PART A に見解定義（【見解X】/X説：等）が複数あり、
        # 記述原文（syn-orig）が見解を名指し参照しているのに .choice-premise（前提見解の原文再掲）が
        # 無いセクションを警告。遡読防止のため各記述冒頭に PART A の見解定義を要約せず再掲する。
        pa = self.soup.find(id="part-a")
        if not pa:
            return
        pa_text = pa.get_text()
        has_defs = len(re.findall(r"【\s*見解\s*[A-ZＡ-Ｚ甲乙丙]|[A-ZＡ-Ｚ甲乙丙]\s*説\s*[（(：:─―—-]", pa_text)) >= 2
        if not has_defs:
            return
        ref = re.compile(r"[A-ZＡ-Ｚ甲乙丙]の見解|[A-ZＡ-Ｚ甲乙丙]\s*説|いずれの見解|両(?:説|見解)")
        missing = []
        for sec in self.soup.find_all("section", class_="choice-section"):
            so = sec.find(class_="syn-orig")
            t = so.get_text() if so else ""
            if ref.search(t) and not sec.find(class_="choice-premise"):
                missing.append(sec.get("id"))
        if len(missing) >= 2:
            self.warn("G28", f"学説・見解問題と推定（PART A に見解定義あり）だが {len(missing)} 記述に "
                             f"前提見解の原文再掲（.choice-premise）が無い: {missing}。"
                             "各記述冒頭に PART A の見解定義を要約せず再掲して遡読を防ぐ"
                             "（scripts/add-choice-premise.py で自動挿入可）")

    def g27_part_a_statute_ref(self):
        # §4c: PART A の参照条文 blockquote.statute は、PDF問題文原文に条文が印字されている場合のみ残す。
        # baseline(GENESIS-CORE)は 0 個。在れば WARNING で要確認を促す（無ければ削除＝A-3共通根拠で足りる・二重掲載しない）。
        # A-3 共通根拠は .basis-card.statute-card（div）で別物なので対象外。
        refs = self.soup.find_all("blockquote", class_="statute")
        if refs:
            self.warn("G27", f"PART A に参照条文 blockquote.statute が {len(refs)} 個あり。PDF問題文原文に条文が印字されている場合のみ残す（§4c）。無ければ削除すること（A-3共通根拠で足りる・二重掲載しない）")

    def g29_answer_value_consistency(self):
        # PART A ox-grid の data-correct-value（位置文字列）と reveal 正誤表の
        # data-answer-key（記述ラベル対応）が記述ごとに一致するかを照合する。
        # 両者がズレると Lexia 肢キー pool で○×判定が反転し、正答が誤答扱いになる
        # （刑TX332/382/355/402/384 で実在・○位置のズレ／刑TX079 で半角 x 混入）。
        area = self.soup.find(class_="answer-area")
        if not area or area.get("data-answer-type", "") != "ox-grid":
            return
        rows = area.find_all(class_="ox-row")
        cv = area.get("data-correct-value", "")
        if not rows or not cv:
            return

        def norm(ch):
            s = (ch or "").strip().lower()
            if s in ("o", "○", "◯"):
                return "o"
            if s in ("x", "×", "✕", "✗"):
                return "x"
            return None

        # reveal 正誤表のラベル→○× マップ
        keymap = {}
        table = self.soup.find("table", attrs={"data-answer-key": True})
        if table:
            for pair in (table.get("data-answer-key", "") or "").split(","):
                pair = pair.strip()
                mm = re.match(r"^\s*([アイウエオ1-5１-５])\s*[:：]\s*([oxOX○×])\s*$", pair)
                if mm:
                    keymap[mm.group(1)] = norm(mm.group(2))

        for i, row in enumerate(rows):
            label = (row.get("data-stmt") or "").strip()
            # ① data-correct-value の i 文字目が正規の全角 ○/× か（半角 x/o 混入検出）
            raw = cv[i] if i < len(cv) else ""
            if raw not in ("○", "×"):
                self.err("G29", f"記述{label or i+1} の data-correct-value 文字 '{raw}' が "
                                "全角 ○/× でない（半角 x/o 等の混入＝Lexia で判定不能）")
                continue
            pos_v = norm(raw)
            # ② 位置文字列とラベル対応正誤表が一致するか
            key_v = keymap.get(label)
            if key_v is not None and pos_v is not None and pos_v != key_v:
                self.err("G29", f"記述{label} で data-correct-value（位置）='{raw}' と "
                                f"正誤表 data-answer-key='{ '○' if key_v=='o' else '×' }' が不一致"
                                "（○位置のズレ＝Lexia で正答が誤答扱いになる）")

    def g30_no_symbol_only_stmt(self):
        # ox-stmt（一問一答の文言）が「①b ②c ③e…」のような記号のみの組合せ肢でないか。
        # Lexia は記号のみ肢を復習プールから恒久除外する（src/App.jsx isSymbolOnlyStmt /
        # commit 2ebbe70）。記号列の暗記には転用可能な学習価値が無いため、生成側でも
        # 一問一答に記号のみ肢を作らない。組合せ問題は空欄ごとの実質命題へ分解する
        # （良い例：刑TX350「公共の危険の内容＝b（限定せず…）が正しい」）。
        # 判定は Lexia と同一：丸数字 3 つ以上 かつ 実質日本語（漢字・かな）2 文字以下。
        area = self.soup.find(class_="answer-area")
        if not area or area.get("data-answer-type", "") != "ox-grid":
            return

        def is_symbol_only(t):
            circled = sub = 0
            for ch in (t or ""):
                c = ord(ch)
                if (0x2460 <= c <= 0x2473) or (0x3251 <= c <= 0x32BF) or \
                   (0x2776 <= c <= 0x277F) or (0x2780 <= c <= 0x2789):
                    circled += 1
                    continue
                if (0x3040 <= c <= 0x30FF) or (0x4E00 <= c <= 0x9FFF) or (0x3400 <= c <= 0x4DBF):
                    sub += 1
            return circled >= 3 and sub <= 2

        bad = []
        for row in area.find_all(class_="ox-row"):
            el = row.find(class_="ox-stmt")
            if el and is_symbol_only(el.get_text()):
                bad.append((row.get("data-stmt") or "?"))
        if bad:
            self.err("G30", f"ox-stmt が記号のみ（①b②c…）の記述: {bad}。"
                            "Lexia の復習プールから除外され一問一答にならない。"
                            "組合せは空欄ごとの実質命題へ分解する（例：刑TX350）")

    def run(self):
        self.g1_head()
        self.g2_header()
        self.g3_part_a()
        self.g4_core_structure()
        self.g5_footer()
        self.g6_main_vars()
        self.g7_derivatives()
        self.g8_no_palette_in_header_footer()
        self.g9_core_svgs()
        self.g10_no_overlap()
        self.g11_viewbox_margin()
        self.g12_no_301_leakage()
        self.g13_no_baseline_copy()
        self.g14_filename_dir()
        self.g15_version_tag()
        self.g16_svg_class_defined()
        self.g19_no_answer_spoiler()
        self.g20_statement_unit()
        self.g21_forbidden_phrases()
        self.g22_choice_points()
        self.g23_verdict_table()
        self.g24_no_full_profile()
        self.g25_part_a_oxgrid()
        self.g26_no_part_d()
        self.g27_part_a_statute_ref()
        self.g28_choice_premise()
        self.g29_answer_value_consistency()
        self.g30_no_symbol_only_stmt()


def main():
    if len(sys.argv) != 2:
        print("使い方: python scripts/validate-tx-core.py <HTML ファイルパス>")
        sys.exit(2)
    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"❌ ファイルが見つからない: {html_path}")
        sys.exit(2)

    print(f"\n=== TX v11.0.0 LOOP-CORE 検証: {html_path.name} ===\n")
    v = Validator(html_path)
    v.run()

    print(f"File size: {html_path.stat().st_size:,} bytes")
    print(f"Errors:    {len(v.errors)}")
    print(f"Warnings:  {len(v.warnings)}\n")

    if v.errors:
        print("--- ERRORS ---")
        for code, msg in v.errors:
            print(f"  ❌ [{code}] {msg}")
        print()
    if v.warnings:
        print("--- WARNINGS ---")
        for code, msg in v.warnings:
            print(f"  ⚠️  [{code}] {msg}")
        print()

    if not v.errors:
        print("✅ ALL (G1〜G28, G17/G18 廃止) PASS")
        sys.exit(0)
    else:
        print("❌ FAIL — ERROR を修正してから再検証してください")
        sys.exit(1)


if __name__ == "__main__":
    main()
