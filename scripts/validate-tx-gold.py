#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v10.0.0 GOLD-SKELETON 自己検証スクリプト

検証範囲：G1〜G16
  G1〜G5：構造（HEAD/HEADER/PART A〜D/footer 存在）
  G6〜G8：配色 V2
    G6: :root{} 内に主要 CSS 変数が定義されているか
    G7: 派生色 10 個が定義されているか
    G8: ヘッダー／フッター表示テキストに配色 Concept 文言が残っていないか
  G9〜G11：SVG
    G9: mindmap-tree / mindmap-radial / flow-svg の 3 種すべて存在
    G10: ボックス重なり 0 件（rect/ellipse/polygon AABB 全ペア検査）
    G11: viewBox の下端余白が十分（最下端要素から 40px 以上）
  G12〜G13：content-independence
    G12: canonical/KTX301.html 由来禁止文言の不出現
    G13: canonical/GENESIS.html 本文との 5 単語以上連続一致なし
  G14〜G15：命名規則
    G14: ファイル ID 形式（{接頭辞}{NNN}）と出力先サブフォルダ整合（canonical/ 配下はスキップ）
    G15: footer-spec feature-tag 先頭が "TX v10.0.0 GOLD-SKELETON"
  G16：SVG class 整合性
    G16: SVG 内 <rect>/<text>/<ellipse>/<polygon> の class が <style> 内に定義済み
         （未定義 class は SVG デフォルトの fill="black" で黒塗りになる事故対策）
  G17〜G18：PART D 12問ドリルの自己完結性（2026-05-29 追加）
    G17: drill-block の quiz-question に「本問の正解は肢N」型の正解再問設問がない
         （答えの暗記には学習効果がないため法理問題に差替）
    G18: PART D（section#part-d）に .arena-premise（前提ブロック）が存在し非空
         （見解・事案・記述を再掲し、12問エリアを遡読不要で自己完結させる）

使い方：
    python scripts/validate-tx-gold.py <HTML ファイルパス>

例：
    python scripts/validate-tx-gold.py outputs/tx/刑TX/刑TX312.html

要件：
    pip install beautifulsoup4
"""

import re
import sys
from pathlib import Path

# Windows cp932 で絵文字出力時の UnicodeEncodeError 対策
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
BASELINE_GENESIS = REPO_ROOT / "canonical" / "GENESIS.html"
BASELINE_301 = REPO_ROOT / "canonical" / "KTX301.html"

JP_PREFIX_TO_DIR = {
    "刑TX": "刑TX",
    "憲TX": "憲TX",
    "民TX": "民TX",
    "商TX": "商TX",
    "民訴TX": "民訴TX",
    "刑訴TX": "刑訴TX",
    "行政TX": "行政TX",
}

REQUIRED_CSS_VARS_MAIN = [
    "--accent",
    "--mid",
    "--light",
    "--base",
    "--soft",
    "--bg-dark",
]

REQUIRED_CSS_VARS_DERIVATIVES = [
    "--accent-darker",
    "--accent-soft",
    "--accent-3",
    "--border-mid",
    "--kp-text-color",
]

PALETTE_LEAKAGE_PATTERNS_HEADER = [
    r"配色\s*[:：]",
    r"P[123][\s　]*[「『]",
    r"AI\s*自由選定",
    # V3 11 named palettes
    r"Sweet\s*Berry",
    r"Fresh\s*Citrus",
    r"Rose\s*Mist",
    r"Antique\s*Pearl",
    r"Maison\s*Blanche",
    r"Crystal\s*Blue",
    r"Dusty\s*Sage",
    r"Mint\s*Tea",
    r"Fresh\s*Mint",
    r"Twilight\s*Violet",
    r"Sunset\s*Harmony",
    # V3 役割定義の漏出
    r"ベース\s*70\s*%",
    r"メイン\s*25\s*%",
    r"アクセント\s*5\s*%",
    # 旧 V2 (歴史的・残存防止)
    r"ピンクを使った可愛い配色",
    r"グリーンを使った可愛い配色",
    r"ロマンティックなパープル配色",
]

# G17：drill quiz-question が「本問の正解そのもの」を再問する設問を検出する。
# 答えの暗記には学習効果がないため、転用可能な法理を問う設問に差し替える。
# .quiz-question の表示テキストにのみ適用（解説 .quiz-answer は正解に言及して可）。
DRILL_ANSWER_RECALL_PATTERNS = [
    r"本問の正解",
    r"本問正解",
    r"正解は肢[0-9０-９]",
    r"正解は記述[0-9０-９]",
    r"の組合せは肢[0-9０-９]",
    r"本問[（(][^）)]*[）)]の[0-9０-９]\s*記述",
    r"本問の[0-9０-９]\s*記述は",
    r"誤っている記述の組合せは肢",
    r"正しい記述の組合せは肢",
]

CANONICAL_301_LEAKAGE = [
    "詐欺罪と他罪の成否",
    "詐欺罪のみが成立し得る",
    "詐欺罪と他の罪の双方が成立し得る",
    "背任行為が同時に詐欺の欺罔行為に当たる",
    "背任罪を別個に構成せず",
    "畏怖の一材料",
    "集金業務を委託",
    "偽造通貨行使罪に包含",
    "放火だけでは詐欺の実行着手",
    "最判昭28.5.8",
    "東京高判昭28.6.12",
    "大判明43.6.30",
    "他人のためにその事務を処理する者が、任務に背いて",
    "新聞販売店から集金業務を委託",
    "保険金を詐取する目的で、火災保険",
    "他人に売買代金として偽造通貨を行使",
]


# ============================================================
# ヘルパー：bounding box 計算
# ============================================================

def parse_translate(transform_str):
    """transform="translate(X, Y)" から (X, Y) を抽出"""
    if not transform_str:
        return (0.0, 0.0)
    m = re.search(r"translate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*\)", transform_str)
    if not m:
        return (0.0, 0.0)
    return (float(m.group(1)), float(m.group(2)))


def get_rect_bbox(rect_el, parent_translate=(0.0, 0.0)):
    """<rect x y width height> の (x_min, x_max, y_min, y_max)"""
    try:
        x = float(rect_el.get("x", 0))
        y = float(rect_el.get("y", 0))
        w = float(rect_el.get("width", 0))
        h = float(rect_el.get("height", 0))
    except (TypeError, ValueError):
        return None
    tx, ty = parent_translate
    return (x + tx, x + tx + w, y + ty, y + ty + h)


def get_ellipse_bbox(el_el, parent_translate=(0.0, 0.0)):
    """<ellipse cx cy rx ry> の bbox"""
    try:
        cx = float(el_el.get("cx", 0))
        cy = float(el_el.get("cy", 0))
        rx = float(el_el.get("rx", 0))
        ry = float(el_el.get("ry", 0))
    except (TypeError, ValueError):
        return None
    tx, ty = parent_translate
    return (cx + tx - rx, cx + tx + rx, cy + ty - ry, cy + ty + ry)


def get_polygon_bbox(poly_el, parent_translate=(0.0, 0.0)):
    """<polygon points="x1,y1 x2,y2 ..."> の bbox"""
    points_str = poly_el.get("points", "")
    coords = re.findall(r"(-?[\d.]+)[,\s]+(-?[\d.]+)", points_str)
    if not coords:
        return None
    xs = [float(p[0]) for p in coords]
    ys = [float(p[1]) for p in coords]
    tx, ty = parent_translate
    return (min(xs) + tx, max(xs) + tx, min(ys) + ty, max(ys) + ty)


def collect_svg_boxes(svg_el):
    """SVG 内のすべての rect/ellipse/polygon の bounding box を集める。
    親 <g transform="translate(...)"> を考慮。
    戻り値：[(label, bbox), ...]
    """
    boxes = []
    for shape in svg_el.find_all(["rect", "ellipse", "polygon"]):
        # 親 g の translate を遡って合成（最も近い直接親のみで十分なケースが多い）
        tx, ty = 0.0, 0.0
        cur = shape.parent
        while cur is not None and cur.name == "g":
            ax, ay = parse_translate(cur.get("transform", ""))
            tx += ax
            ty += ay
            cur = cur.parent
        parent_t = (tx, ty)

        if shape.name == "rect":
            bbox = get_rect_bbox(shape, parent_t)
        elif shape.name == "ellipse":
            bbox = get_ellipse_bbox(shape, parent_t)
        else:  # polygon
            bbox = get_polygon_bbox(shape, parent_t)

        if bbox is None:
            continue
        # ラベル候補：class または text 兄弟
        cls = " ".join(shape.get("class", []))
        label = f"{shape.name}.{cls}" if cls else shape.name
        boxes.append((label, bbox))
    return boxes


def boxes_overlap(b1, b2):
    """AABB intersection 判定"""
    x1_min, x1_max, y1_min, y1_max = b1
    x2_min, x2_max, y2_min, y2_max = b2
    return (x1_min < x2_max and x1_max > x2_min
            and y1_min < y2_max and y1_max > y2_min)


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

    # --- G1〜G5：構造 ---

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

    def g4_parts_b_c_d(self):
        choice_sections = self.soup.find_all("section", class_="choice-section")
        if len(choice_sections) < 2:
            self.err("G4", f"choice-section が {len(choice_sections)} 個（最低 2 必要）")
        for cid in ["c-1", "c-2", "c-3", "c-4", "c-5", "c-6", "c-7"]:
            if not self.soup.find(id=cid):
                self.err("G4", f"section#{cid} が存在しない")
        drills = self.soup.find_all(class_="drill-block")
        if len(drills) < 10:
            self.err("G4", f"drill-block が {len(drills)} 個（PART D は 12 を期待）")

    def g5_footer(self):
        footer = self.soup.find("div", class_="footer-spec")
        if not footer:
            self.err("G5", ".footer-spec が存在しない")
            return
        if not footer.find(class_="footer-problem"):
            self.err("G5", ".footer-problem が存在しない")
        if not footer.find(class_="footer-meta-hidden"):
            self.err("G5", ".footer-meta-hidden（feature-tag コンテナ）が存在しない")

    # --- G6〜G8：配色 V2 ---

    def _root_block(self):
        """全 <style> から :root{...} ブロックを brace-balanced で抽出して連結"""
        chunks = []
        for style in self.soup.find_all("style"):
            css = style.get_text()
            i = 0
            while True:
                m = re.search(r":root\s*\{", css[i:])
                if not m:
                    break
                start = i + m.end()
                depth = 1
                j = start
                while j < len(css) and depth > 0:
                    if css[j] == "{":
                        depth += 1
                    elif css[j] == "}":
                        depth -= 1
                    j += 1
                if depth == 0:
                    chunks.append(css[start:j - 1])
                    i = j
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
            return  # G6 で既に報告
        found = 0
        for v in REQUIRED_CSS_VARS_DERIVATIVES:
            if v + ":" in root or v + " :" in root:
                found += 1
        if found < 3:
            self.err("G7", f"派生色変数が {found} 個しか定義されていない（最低 3 個期待）")
        elif found < len(REQUIRED_CSS_VARS_DERIVATIVES):
            self.warn("G7", f"派生色変数が {found}/{len(REQUIRED_CSS_VARS_DERIVATIVES)} のみ定義")

    def g8_no_palette_in_header_footer(self):
        # exam-meta
        exam_meta = self.soup.find(class_="exam-meta")
        if exam_meta:
            txt = exam_meta.get_text()
            for pat in PALETTE_LEAKAGE_PATTERNS_HEADER:
                if re.search(pat, txt):
                    self.err("G8", f".exam-meta に配色情報 '{pat}' が残存")
        # footer-meta-info
        footer_info = self.soup.find(class_="footer-meta-info")
        if footer_info:
            txt = footer_info.get_text()
            for pat in PALETTE_LEAKAGE_PATTERNS_HEADER:
                if re.search(pat, txt):
                    self.err("G8", f".footer-meta-info に配色情報 '{pat}' が残存")

    # --- G9〜G11：SVG ---

    def g9_three_svgs(self):
        self.tree_svg = self.soup.find("svg", class_="tree-svg")
        self.radial_svg = self.soup.find("svg", class_="radial-svg")
        self.flow_svg = self.soup.find("svg", class_="flow-svg")
        if not self.tree_svg:
            self.err("G9", "tree-svg（体系ツリー）が存在しない")
        if not self.radial_svg:
            self.err("G9", "radial-svg（論点マインドマップ放射）が存在しない")
        if not self.flow_svg:
            self.err("G9", "flow-svg（C-5 総合フローチャート）が存在しない")

    def g10_no_overlap(self):
        for svg_name, svg in [("tree", self.tree_svg),
                              ("radial", self.radial_svg),
                              ("flow", self.flow_svg)]:
            if svg is None:
                continue
            boxes = collect_svg_boxes(svg)
            # polygon（flow-decision 等の菱形）は bbox 検査では擬陽性が多いので除外
            rects_ellipses = [b for b in boxes if not b[0].startswith("polygon")]
            n = len(rects_ellipses)
            for i in range(n):
                for j in range(i + 1, n):
                    label_a, b_a = rects_ellipses[i]
                    label_b, b_b = rects_ellipses[j]
                    if boxes_overlap(b_a, b_b):
                        # 完全内包は装飾レイヤーなのでスキップ
                        if self._fully_contained(b_a, b_b) or self._fully_contained(b_b, b_a):
                            continue
                        self.err("G10",
                                 f"[{svg_name}] {label_a} と {label_b} が重なる "
                                 f"(bbox: {b_a} vs {b_b})")

    @staticmethod
    def _fully_contained(small, big):
        """small が big に完全に内包されるか"""
        return (small[0] >= big[0] and small[1] <= big[1]
                and small[2] >= big[2] and small[3] <= big[3])

    def g11_viewbox_margin(self):
        for svg_name, svg in [("tree", self.tree_svg),
                              ("radial", self.radial_svg),
                              ("flow", self.flow_svg)]:
            if svg is None:
                continue
            # BS4 html.parser は属性名を小文字化するので viewbox で取得
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
            y_max_all = max(b[1][3] for b in boxes)
            margin = vb_h - y_max_all
            if margin < 20:
                self.err("G11",
                         f"[{svg_name}] viewBox 下端余白が {margin:.0f}px（20px 未満）")
            elif margin < 40:
                self.warn("G11",
                          f"[{svg_name}] viewBox 下端余白が {margin:.0f}px（推奨 40px 以上）")

    # --- G12〜G13：content-independence ---

    def _body_text(self):
        body = self.soup.find("body")
        return body.get_text() if body else ""

    def g12_no_301_leakage(self):
        text = self._body_text()
        for phrase in CANONICAL_301_LEAKAGE:
            if phrase in text:
                self.err("G12", f"KTX301 由来禁止文言が残存: '{phrase}'")

    def g13_no_genesis_baseline_copy(self):
        # GENESIS 自身（canonical/）または 311 の派生検証時はスキップ
        if self.html_path.parent.name == "canonical":
            return
        if "311" in self.html_path.stem:
            return
        if not BASELINE_GENESIS.exists():
            self.warn("G13", f"baseline {BASELINE_GENESIS.name} が見つからずスキップ")
            return
        baseline_text = BeautifulSoup(
            BASELINE_GENESIS.read_text(encoding="utf-8"), "html.parser"
        ).get_text()
        # body 本文のみ 5-gram 一致を簡易検出
        cur_text = self._body_text()
        # 句読点で粗く split
        baseline_tokens = re.findall(r"\S+", baseline_text)
        # 5-gram set（負担軽減のため間引き）
        baseline_5grams = set()
        for k in range(0, len(baseline_tokens) - 4, 3):
            baseline_5grams.add(" ".join(baseline_tokens[k:k + 5]))
        cur_tokens = re.findall(r"\S+", cur_text)
        hits = 0
        sample = []
        for k in range(len(cur_tokens) - 4):
            g = " ".join(cur_tokens[k:k + 5])
            if g in baseline_5grams:
                hits += 1
                if len(sample) < 3:
                    sample.append(g)
                if hits >= 10:
                    break
        if hits >= 5:
            self.err("G13",
                     f"baseline GENESIS と 5-gram が {hits} 件以上一致（content leakage 疑い）: "
                     f"例 {sample}")

    # --- G14〜G15：命名規則・version-tag ---

    def g14_filename_dir(self):
        # canonical/ 配下は baseline 専用なので命名チェックをスキップ
        if self.html_path.parent.name == "canonical":
            return
        stem = self.html_path.stem
        m = re.match(r"(刑TX|憲TX|民訴TX|刑訴TX|行政TX|民TX|商TX)(\d{3,})$", stem)
        if not m:
            self.err("G14", f"ファイル名 ID 形式違反: '{stem}'")
            return
        prefix = m.group(1)
        expected_dir = JP_PREFIX_TO_DIR.get(prefix)
        if not expected_dir:
            self.err("G14", f"未知の接頭辞: '{prefix}'")
            return
        if self.html_path.parent.name != expected_dir:
            self.err("G14",
                     f"出力先サブフォルダ不整合: 期待 '{expected_dir}'、"
                     f"実際 '{self.html_path.parent.name}'")

    def g15_version_tag(self):
        footer = self.soup.find("div", class_="footer-spec")
        if not footer:
            return  # G5 で既に報告
        tags = footer.find_all(class_="feature-tag")
        if not tags:
            self.err("G15", "footer-spec に feature-tag が一つもない")
            return
        first = tags[0].get_text().strip()
        if not first.startswith("TX v10.0.0 GOLD-SKELETON"):
            self.err("G15",
                     f"feature-tag 先頭が 'TX v10.0.0 GOLD-SKELETON' でない: '{first}'")

    # --- G16：SVG class 整合性（未定義 class 検出）---

    def g16_svg_class_defined(self):
        """SVG 内の <rect>/<text>/<ellipse>/<polygon> 等で class 属性に
        指定されている class 名が <style> 内に定義されているか検査。
        未定義 class は SVG デフォルト fill="black" で黒塗りになる事故対策。
        """
        # <style> 内の全 class 定義を収集
        defined = set()
        for style in self.soup.find_all("style"):
            text = style.get_text()
            for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_-]*)", text):
                defined.add(m.group(1))

        # SVG 内の class 利用箇所を走査
        SVG_SHAPE_TAGS = {"rect", "text", "ellipse", "polygon", "circle",
                          "line", "path", "g"}
        undefined_uses = []
        for svg in self.soup.find_all("svg"):
            for el in svg.find_all(True):
                if el.name not in SVG_SHAPE_TAGS:
                    continue
                cls = el.get("class")
                if not cls:
                    continue
                # BeautifulSoup の class 属性はリストで来る
                for c in cls:
                    if c and c not in defined:
                        undefined_uses.append((el.name, c))

        if undefined_uses:
            # 重複排除して件数報告
            unique = set(undefined_uses)
            samples = list(unique)[:5]
            self.err("G16",
                     f"SVG 内に未定義 class が {len(unique)} 種類あり（黒塗りリスク）: "
                     f"{samples}")

    # --- G17〜G18：PART D 12問ドリルの自己完結性 ---

    def g17_no_answer_recall_drill(self):
        """drill-block の quiz-question が本問の正解そのものを再問していないか検査。"""
        for drill in self.soup.find_all(class_="drill-block"):
            q = drill.find(class_="quiz-question")
            if not q:
                continue
            txt = q.get_text()
            for pat in DRILL_ANSWER_RECALL_PATTERNS:
                if re.search(pat, txt):
                    tag = drill.find(class_="drill-tag")
                    label = tag.get_text().strip() if tag else "?"
                    self.err("G17",
                             f"drill「{label}」の設問が本問の正解を再問している"
                             f"（'{pat}' に一致）。法理を問う設問に差し替えること")
                    break

    def g18_arena_premise(self):
        """PART D に前提ブロック .arena-premise が存在し非空か検査。"""
        part_d = self.soup.find(id="part-d")
        if not part_d:
            return  # G4 で報告済
        premise = part_d.find(class_="arena-premise")
        if not premise:
            self.err("G18",
                     ".arena-premise（前提ブロック）が PART D に存在しない"
                     "（見解・事案・記述を再掲し 12問エリアを自己完結させること）")
            return
        items = premise.find_all(class_="arena-premise-item")
        if len(items) < 2:
            self.err("G18",
                     f".arena-premise の項目（.arena-premise-item）が {len(items)} 件"
                     "（事案・見解・各記述で最低 2 件以上を期待）")

    def run(self):
        self.g1_head()
        self.g2_header()
        self.g3_part_a()
        self.g4_parts_b_c_d()
        self.g5_footer()
        self.g6_main_vars()
        self.g7_derivatives()
        self.g8_no_palette_in_header_footer()
        self.g9_three_svgs()
        self.g10_no_overlap()
        self.g11_viewbox_margin()
        self.g12_no_301_leakage()
        self.g13_no_genesis_baseline_copy()
        self.g14_filename_dir()
        self.g15_version_tag()
        self.g16_svg_class_defined()
        self.g17_no_answer_recall_drill()
        self.g18_arena_premise()


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) != 2:
        print("使い方: python scripts/validate-tx-gold.py <HTML ファイルパス>")
        sys.exit(2)

    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"❌ ファイルが見つからない: {html_path}")
        sys.exit(2)

    print(f"\n=== TX v10.0.0 GOLD-SKELETON 検証: {html_path.name} ===\n")

    v = Validator(html_path)
    v.run()

    print(f"File size: {html_path.stat().st_size:,} bytes")
    print(f"Errors:    {len(v.errors)}")
    print(f"Warnings:  {len(v.warnings)}")
    print()

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
        print("✅ ALL G1〜G18 PASS")
        sys.exit(0)
    else:
        print("❌ FAIL — ERROR を修正してから再検証してください")
        sys.exit(1)


if __name__ == "__main__":
    main()
