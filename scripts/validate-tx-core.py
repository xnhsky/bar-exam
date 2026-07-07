#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v11/v12 LOOP-CORE 自己検証スクリプト（コア＝メイン HTML 用）

spec: spec/tx-v11.0.0-core.md 第7項

検証範囲（v10 GOLD の validate-tx-gold.py から派生）：
  継承：G1〜G3（構造）／G5〜G8（footer・配色）／G12〜G14（独立性・命名）／G16（SVG class）／
        G19（解答前ネタバレ）
  改定：
    G4  → コア構造（記述単位 PART B 5本＋参考条文判例＋体系/放射マップ。PART C/D は無い）
    G9  → SVG はコアに体系ツリー＋放射マップの2枚。フローチャートは別冊専用＝不在を要求
    G10 → AABB 衝突（tree+radial の2枚）
    G11 → viewBox 余白（tree+radial の2枚）
    G15 → feature-tag 先頭が "TX v11.x.x LOOP-CORE" または "TX v12.x.x LOOP-CORE"
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
  G32 復習プール本文の記号フリー化：_lex の .syn-lead / .choice-points li に
  G33 TX-LEX最終表5点セット：_lex の .statement-verdict-table 最終列に
      文言・趣旨・射程・切断点・転用の reflex core を要求（移行期 WARNING）。
        問題ローカル記号（A説・①・記述ア・事例Ⅰ等）が残らない
  G34 TX360 SM2 payload 契約：inline _lex の .ox-row 直下に .ox-pool-explain があり、
      通常 SM2 カード本文へ fa-narrative / 詳説 / 問題ローカル記号を混ぜない
  G35 物語解説タイポグラフィ：.fa-narrative の強調太字を過剰に太くしない
  G36 TX360テンプレート固定：本文ラベルは 文言/趣旨/射程/転用（字間スペースなし）
  G37 canonicalテンプレート固定：5点ラベルは楕円ピルCSS(v12.2.0)、H1は No.NNN ── 形式
  G38 正典プレースホルダー契約：生成済み _lex に {{...}} を残さない
  G39 記憶フック/答案圧縮：2カラム中央寄せのTX360テンプレートCSSを要求
  G45 v12.2.1 表示LOCK：条文/判例の題名・法理テーマ、条文本文2カラム、物語ラベル非重畳、解説役割の混入禁止を要求
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

# G30：プール対象テキスト（ox-stmt・verdict 論点コア）の自己完結ルール。
# Lexia は誤答した記述を「肢キー」で単独追跡し（{問題ID}#stmt-ラベル）、間隔反復の
# 一問一答カードとして問題本体から切り離して提示する。そのカード本文に「その回の問題
# レイアウト固有のラベル」が残ると、知識ではなく記号対応の暗記になり転用できない
# （A説/B説は実体の学説名が来年は別ラベルで呼ばれ、プール内で偽の関連を量産する）。
# よってプール対象テキストは①見解を実体名で主語化し②空欄記号/選択肢記号/他記述・他肢
# 参照/「本問」「上記見解」依存を残さないこと。検出は当面 WARNING（既存コーパスの
# 後追い書き直しの worklist にする・安定後 ERROR 化）。
POOL_LABEL_PATTERNS = [
    (r"[A-EＡ-Ｅ]\s*説", "問題ローカルの見解ラベル『A説』＝実体の学説名で主語化する"),
    (r"[A-EＡ-Ｅ]の見解", "問題ローカルの見解ラベル『Aの見解』＝実体の学説名で主語化する"),
    (r"[甲乙丙丁]\s*説", "甲乙説ラベル＝実体の学説名で主語化する"),
    (r"第\s*[1-5１-５一二三四五]\s*説", "第N説ラベル＝実体の学説名で主語化する"),
    (r"[①-⑩]", "空欄記号（丸数字）の残留＝命題本文に置換する"),
    (r"[（(][a-jａ-ｊ][）)]", "選択肢記号（a〜j）の残留＝語句本文に置換する"),
    (r"記述[アイウエオ1-9１-９]", "他記述の相互参照＝各記述を自己完結させる"),
    (r"肢[アイウエオ1-5１-５]", "肢番号への参照＝命題本文で書く"),
    (r"上記(?:の)?見解", "『上記見解』依存＝前提を命題内に含めて自己完結させる"),
    (r"本問", "『本問』依存＝問題非依存の命題として書く"),
    # 2026-06-25 拡張：283/310型（bare見解letter・事例・学生ラベル）を捕捉。WARNING（worklist）。
    (r"学生[A-EＡ-Ｅ]", "問題ローカルの学生ラベル『学生A』＝実体の学説名で主語化する"),
    (r"[A-EＡ-Ｅ]\s*[・／]\s*[A-EＡ-Ｅ]", "見解letterの連結『A・B』＝実体の学説名に展開する"),
    (r"[A-EＡ-Ｅ]（[^）]{1,12}）", "見解letter＋注釈『A（…）』＝実体の学説名で主語化する"),
    (r"事例[ⅠⅡⅢⅣⅤ]", "事例ローマ数字ラベル＝事案の実体内容で表す"),
]

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
        # v13 LOOP-CARD 新設計は PART B（choice-section）を各カードへ昇格し廃止する。
        is_v13 = self.soup.select_one(".tx-inline-card .tx-v13-verdict") is not None
        choice_sections = self.soup.find_all("section", class_="choice-section")
        if not is_v13 and len(choice_sections) < 2:
            self.err("G4", f"記述別 choice-section が {len(choice_sections)} 個（記述ア〜オで通常 5 を期待）")
        if not self.soup.find(id="basis"):
            self.err("G4", "参考条文・判例セクション（#basis）が存在しない")
        # 体系マップ内に SVG ツリー（ハイブリッド新設計）があれば、下部の体系ツリー／
        # 放射マップセクションは不要（廃止）。旧設計は従来どおり両セクションを要求する。
        hybrid_sysmap = self.soup.select_one(".tx-sysmap svg.tree-svg") is not None
        if not hybrid_sysmap:
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
        # ハイブリッド新設計（体系マップ内 SVG ツリー）では放射マップは廃止。
        hybrid_sysmap = self.soup.select_one(".tx-sysmap svg.tree-svg") is not None
        if not self.tree_svg:
            self.err("G9", "tree-svg（体系ツリー）が存在しない")
        if not self.radial_svg and not hybrid_sysmap:
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
        "back-to-top",
    )
    _G13_SHELL_SELECTORS = (
        ".statement-verdict-table thead",
    )
    _G13_LEAK_THRESHOLD = 20

    @staticmethod
    def _g13_content_tokens(html_str):
        soup = BeautifulSoup(html_str, "html.parser")
        body = soup.find("body") or soup
        for cls in Validator._G13_SHELL_CLASSES:
            for el in body.select("." + cls):
                el.decompose()
        for selector in Validator._G13_SHELL_SELECTORS:
            for el in body.select(selector):
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
        # v11/v12.x.x LOOP-CORE または v13.x.x LOOP-CARD（active）を許容。
        # v12.1.1 は v12.1.0 inline canon に narrative typography patch を重ねた版。
        # v13.x LOOP-CARD（v13.0.0 基盤＋v13.1.0 正誤表リデザイン）は「読む解説」再編（gold=刑TX359・lineage active）。
        ok_core = first.startswith(("TX v11.", "TX v12.")) and "LOOP-CORE" in first
        ok_card = first.startswith("TX v13.") and "LOOP-CARD" in first
        if not (ok_core or ok_card):
            self.err("G15", f"feature-tag 先頭が 'TX v11/v12.x.x LOOP-CORE' または 'TX v13.x.x LOOP-CARD' でない: '{first}'")

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
        # 二系統化：記述○×一覧表（data-answer-key）は ox-grid／Lexia 用 _lex の肢データ源。
        # 公式（outputs/000_TX/...）が real-exam 5択（single/multi）の場合は対象外（過去問そのまま）。
        area = self.soup.find(class_="answer-area")
        is_lex = self.html_path.stem.endswith("_lex")
        atype = area.get("data-answer-type", "") if area else ""
        if not is_lex and atype in ("single", "multi"):
            return  # 公式 real-exam 版は ○×一覧表 任意
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
        # 二系統化（v11.1.0 継承／v12.1.1 active）：Lexia 用 _lex（outputs/ux/000_TX/..._lex.html）は ox-grid 必須
        # ＝記述単位○×が Lexia 復習プールの肢データ源。一方、公式（outputs/000_TX/...）は
        # 過去問そのままの「本物の5択」＝ single / multi を許容する（解法ナビは _lex のみ）。
        is_lex = self.html_path.stem.endswith("_lex")
        if not is_lex and atype in ("single", "multi"):
            return  # 公式（real-exam 5択）＝ ox-grid 固有検査は対象外
        if atype != "ox-grid":
            who = "Lexia 用 _lex は" if is_lex else "ox-grid でない公式は single/multi のみ可。"
            self.err("G25", f"PART A の data-answer-type が '{atype}'（ox-grid を期待）。{who}"
                            "5記述の○×収集が肢データ源・spec 第2項/第9項")
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
            raw = cv[i] if i < len(cv) else ""
            # 行の選択肢（.ox-btn の data-value）。○× 型は ○/×、多肢選択型は a/b/c… 。
            valid = [(b.get("data-value") or "") for b in row.find_all(class_="ox-btn")]
            valid = [v for v in valid if v]
            # ① data-correct-value の i 文字目が、その行の選択肢のどれかと一致するか
            #    （○× 型の半角 x/o 混入も、選択肢に無い＝ここで検出される）
            if valid and raw not in valid:
                self.err("G29", f"記述{label or i+1} の data-correct-value 文字 '{raw}' が "
                                f"その行の選択肢 {valid} に無い（半角混入／正解不整合＝Lexia で判定不能）")
                continue
            pos_v = norm(raw)
            # ② ○× 型のみ：位置文字列とラベル対応正誤表（data-answer-key）が一致するか
            #    （多肢選択型は norm が None になり、この照合はスキップされる）
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

    def g30_pool_self_contained(self):
        # [G31] プール対象テキスト＝(1) 各 .ox-stmt（カード見出し命題）と
        # (2) reveal 正誤表 .statement-verdict-table の論点コア列（最終 td）。
        # POOL_LABEL_PATTERNS にマッチする「問題ローカルのラベル／他記述・本問依存」を
        # 自己完結阻害として WARNING する（記号フリー・実体名主語化・spec 第3-bis項）。
        targets = []
        for el in self.soup.find_all(class_="ox-stmt"):
            targets.append(("ox-stmt", el.get_text(" ", strip=True)))
        tbl = self.soup.find("table", class_="statement-verdict-table")
        if tbl:
            for tr in tbl.find_all("tr"):
                tds = tr.find_all("td")
                if tds:
                    targets.append(("論点コア", tds[-1].get_text(" ", strip=True)))

        # 座談会型の例外（2026-06-25）：学生A/B/C 等の話者ラベルが 3 つ以上の ox-stmt の
        # 対応主語に現れる問題（話者↔見解の総当たり対応＝刑TX090型）では、学生ラベルは
        # 甲乙丙の登場人物と同じく問題内在の話者識別子であり、転用可能な見解ラベルではない。
        # 除去すると命題が成立せず answer-key を壊すため、この型に限り学生ラベル
        # （STUDENT_LABEL_PAT）だけを G31 の対象から外す（擬陽性・spec 第3-bis項の例外）。
        STUDENT_LABEL_PAT = r"学生[A-EＡ-Ｅ]"
        student_ox = sum(1 for w, t in targets
                         if w == "ox-stmt" and re.search(STUDENT_LABEL_PAT, t))
        zadankai = student_ox >= 3

        hits = []
        for where, txt in targets:
            if not txt:
                continue
            for pat, reason in POOL_LABEL_PATTERNS:
                if zadankai and pat == STUDENT_LABEL_PAT:
                    continue  # 座談会型：話者ラベルは内在識別子（擬陽性）
                m = re.search(pat, txt)
                if m:
                    hits.append((where, m.group(0).strip(), reason, txt[:46]))
                    break  # 1テキスト1指摘
        if hits:
            head = "; ".join(f"[{w}]『{frag}…』←{why}({tok})" for w, tok, why, frag in hits[:4])
            more = f" 他 {len(hits)-4} 件" if len(hits) > 4 else ""
            self.warn("G31", f"プール対象テキスト {len(hits)} 件が一問一答として自己完結していない: "
                             f"{head}{more}（記号フリー・見解は実体名で主語化・spec 第3-bis項）")

    def g32_pool_review_text_symbol_free(self):
        # Lexia 復習プールは肢キーカードに PART B の THE GIST(.syn-lead) と
        # POINT(.choice-points li) を併載する。ここに空欄番号・選択肢記号・
        # A説/B説・記述参照・事例番号などが残ると、問題ローカル記号の暗記に
        # 退化するため _lex では ERROR として止める。
        if not self.html_path.stem.endswith("_lex"):
            return

        targets = []
        for idx, el in enumerate(self.soup.select(".syn-lead"), 1):
            targets.append((f"syn-lead#{idx}", el.get_text(" ", strip=True)))
        for cp_idx, cp in enumerate(self.soup.select(".choice-points"), 1):
            for li_idx, li in enumerate(cp.find_all("li"), 1):
                targets.append((f"choice-points#{cp_idx} li#{li_idx}",
                                li.get_text(" ", strip=True)))

        hits = []
        for where, txt in targets:
            if not txt:
                continue
            for pat, reason in POOL_LABEL_PATTERNS:
                m = re.search(pat, txt)
                if m:
                    hits.append((where, m.group(0).strip(), reason, txt[:60]))
                    break

        if hits:
            head = "; ".join(f"[{w}]『{frag}…』←{why}({tok})"
                             for w, tok, why, frag in hits[:5])
            more = f" 他 {len(hits)-5} 件" if len(hits) > 5 else ""
            self.err("G32", f"復習プール併載テキスト {len(hits)} 件に問題ローカル記号が残留: "
                            f"{head}{more}（.syn-lead / .choice-points li は実体名・概念名で自己完結させる）")

    def g33_tx_lex_reflex_core_five_tags(self):
        # TX-LEX の reveal 最終表は Lexia/SM2 で単独カード化されるため、単なる長文説明ではなく
        # 文言・趣旨・射程・切断点・転用の5点セットを要求する。既存在庫の移行期なので WARNING。
        if not self.html_path.stem.endswith("_lex"):
            return
        tbl = self.soup.find("table", class_="statement-verdict-table")
        if not tbl:
            return

        required = {"文言", "趣旨", "射程", "切断点", "転用"}
        misses = []
        ths = tbl.find_all("th")
        header_text = ths[-1].get_text(" ", strip=True) if ths else ""
        if "文言・趣旨・射程・切断点・転用" not in header_text:
            misses.append("見出し")

        for idx, tr in enumerate(tbl.find_all("tr"), 1):
            tds = tr.find_all("td")
            if not tds:
                continue
            cell = tds[-1]
            tags = {el.get_text(" ", strip=True) for el in cell.select(".tx-reflex-tag")}
            if not required.issubset(tags):
                label = tds[0].get_text(" ", strip=True) if tds else str(idx)
                lacks = "・".join(tag for tag in ("文言", "趣旨", "射程", "切断点", "転用") if tag not in tags)
                misses.append(f"{label}:{lacks}")

        if misses:
            head = " / ".join(misses[:8])
            more = f" 他 {len(misses)-8} 件" if len(misses) > 8 else ""
            self.warn("G33", f"_lex 最終表の論点コアが5点セット化されていない: {head}{more}。"
                             "各行を .tx-reflex-core 内の 文言・趣旨・射程・切断点・転用 に分解する。")

    def g34_tx360_sm2_payload_contract(self):
        # TX360 inline 正典では、Lexia の通常 SM2 カード本文は `.ox-stmt` と
        # `.ox-pool-explain`（= tx-reflex-core + cycle aids）で自己完結させる。
        # `.fa-narrative` は初回理解用の読み物、`.tx-inline-detail` / PART B は詳説アーカイブなので、
        # 通常カード本文へ混ぜない。
        if not self.html_path.stem.endswith("_lex"):
            return
        area = self.soup.select_one('.answer-area.inline-prototype-mode[data-answer-type="ox-grid"]')
        cards = self.soup.select(".tx-inline-card[data-stmt]")
        if not area or not cards:
            return

        missing = []
        polluted = []
        label_hits = []
        for row in area.select(".answer-ox-grid .ox-row"):
            stmt = (row.get("data-stmt") or "").strip() or "?"
            pe = row.select_one(".ox-pool-explain")
            if not pe:
                missing.append(stmt)
                continue
            if pe.select_one(".fa-narrative, .tx-inline-detail, .sub-card.synthesis, .sub-card.explanation"):
                polluted.append(stmt)
            txt = pe.get_text(" ", strip=True)
            for pat, reason in POOL_LABEL_PATTERNS:
                m = re.search(pat, txt)
                if m:
                    label_hits.append((stmt, m.group(0).strip(), reason))
                    break

        if missing:
            self.err("G34", f"TX360 inline _lex の ox-row に .ox-pool-explain が無い: {missing[:8]}"
                            f"{' 他 '+str(len(missing)-8)+' 件' if len(missing)>8 else ''}。"
                            "Lexia の SM2 GIST/POINT が PART B 長文へフォールバックする。"
                            "scripts/tx-sm2-payload-backfill.py で tx-reflex-core を注入する。")
        if polluted:
            self.err("G34", f".ox-pool-explain に fa-narrative / 詳説カードが混入: {polluted[:8]}。"
                            "SM2 は読む場所ではなく誤答肢を再判定する場所なので、"
                            "tx-reflex-core と短い cycle aids だけにする。")
        if label_hits:
            head = "; ".join(f"stmt{stmt}:{tok}({why})" for stmt, tok, why in label_hits[:5])
            more = f" 他 {len(label_hits)-5} 件" if len(label_hits) > 5 else ""
            self.err("G34", f".ox-pool-explain に問題都合ラベルが残留: {head}{more}。"
                            "SM2 payload は論点コア・テーゼへ置換する。")

    def g35_fa_narrative_emphasis_weight(self):
        # v12.1.1 typography patch: story explanation is a rescue reading text.
        # Bold terms should guide the eye, not become black chunks on iPhone.
        css = "\n".join(style.get_text() for style in self.soup.find_all("style"))
        m = re.search(r"\.fa-narrative\s+b\s*\{(?P<body>[^}]*)\}", css, re.S)
        if not m:
            return
        body = m.group("body")
        w = re.search(r"font-weight\s*:\s*(?P<weight>\d+)", body)
        if not w:
            return
        weight = int(w.group("weight"))
        if weight > 560:
            self.err("G35", f".fa-narrative b の font-weight が {weight}。"
                            "v12.1.1 では物語解説の強調は 560 以下にして、"
                            "モバイルで潰れる太字へ戻さない。")

    def g36_tx360_template_flow_label_text(self):
        # TX360 is the concrete template source for inline-card flow labels.
        # The label text itself must stay compact; spacing is handled by CSS.
        if not self.html_path.stem.endswith("_lex"):
            return
        bad = []
        allowed = {"文言", "趣旨", "射程", "切断点", "転用"}
        compact = {"文　言": "文言", "趣　旨": "趣旨", "射　程": "射程", "転　用": "転用"}
        for el in self.soup.select(".tx-article-flow .tx-flow-label"):
            txt = el.get_text("", strip=True)
            if txt in compact:
                bad.append(f"{txt}→{compact[txt]}")
            elif txt not in allowed:
                bad.append(txt)

        if bad:
            head = " / ".join(bad[:8])
            more = f" 他 {len(bad)-8} 件" if len(bad) > 8 else ""
            self.err("G36", f"TX360テンプレート外の本文ラベル: {head}{more}。"
                            ".tx-flow-label は 文言/趣旨/射程/切断点/転用 に固定し、"
                            "字間スペースはCSS側に任せる。")

    def g37_tx360_template_visual_contract(self):
        # TX360 is also the visual source of truth: compact flow-label badges
        # and a title beginning with "No.NNN ──".
        if not self.html_path.stem.endswith("_lex"):
            return

        code_m = re.match(r"(.+?)(\d+)_lex$", self.html_path.stem)
        expected_no = code_m.group(2) if code_m else None
        h1 = self.soup.find("h1")
        h1_text = h1.get_text(" ", strip=True) if h1 else ""
        if expected_no and not h1_text.startswith(f"No.{expected_no} ──"):
            self.err("G37", f"H1 が TX360テンプレート形式ではない: {h1_text!r}。"
                            f"`No.{expected_no} ── ...` で始める。")

        css = "\n".join(style.get_text() for style in self.soup.find_all("style"))
        matches = list(re.finditer(r"\.tx-article-flow\s+\.tx-flow-label\s*\{(?P<body>[^}]*)\}", css, re.S))
        if not matches:
            self.err("G37", ".tx-article-flow .tx-flow-label の楕円ピルテンプレートCSSが無い。"
                            "canonical の実物テンプレートを流し込む。")
            return
        # v12.2.0：5点ラベルは固定幅タブではなく、文字幅に縮むバッジ。
        required = {
            "width": r"width\s*:\s*auto",
            "min-width": r"min-width\s*:\s*0",
            "justify-self": r"justify-self\s*:\s*start",
            "border-radius": r"border-radius\s*:\s*999px",
            "padding": r"padding\s*:\s*3px\s+9px\s+4px",
        }
        ok = False
        best_lacks = list(required)
        for m in matches:
            body = m.group("body")
            lacks = [name for name, pat in required.items() if not re.search(pat, body)]
            if len(lacks) < len(best_lacks):
                best_lacks = lacks
            if not lacks:
                ok = True
                break
        if not ok:
            self.err("G37", f"5点ラベルCSSがTX360バッジテンプレート(v12.2.0)からずれている: {', '.join(best_lacks)}。"
                            "長方形・固定幅へ戻さず、canonical の `.tx-article-flow .tx-flow-label`"
                            "(width:auto / min-width:0 / justify-self:start / 999px / 3px 9px 4px) を使う。")

    def g38_placeholder_contract(self):
        unresolved = re.findall(r"\{\{[^{}]{1,120}\}\}", self.html)
        if self.html_path.stem.endswith("_lex") and unresolved:
            sample = " / ".join(unresolved[:8])
            more = f" 他 {len(unresolved)-8} 件" if len(unresolved) > 8 else ""
            self.err("G38", f"未置換プレースホルダーが残っている: {sample}{more}。"
                            "正典HTMLは {{...}} 部分だけを置換し、生成済み _lex には残さない。")

        if self.html_path.name == "GENESIS-CORE.html":
            required = [
                "{{問題コード}}", "{{問題番号}}", "{{テーマ}}", "{{出典}}",
                "{{記述1本文}}", "{{記述1文言本文}}", "{{記述1切断点本文}}",
                "{{記述1記憶フック本文}}", "{{記述1答案圧縮本文}}",
                "{{記述1処理マトリクス題名}}", "{{記述1処理結論軸}}",
                "{{記述2記憶フック本文}}", "{{記述2答案圧縮本文}}",
                "{{記述2処理マトリクス題名}}", "{{記述2処理結論軸}}",
                "{{記述3記憶フック本文}}", "{{記述3答案圧縮本文}}",
                "{{記述3処理マトリクス題名}}", "{{記述3処理結論軸}}",
                "{{記述4記憶フック本文}}", "{{記述4答案圧縮本文}}",
                "{{記述4処理マトリクス題名}}", "{{記述4処理結論軸}}",
            ]
            missing = [token for token in required if token not in self.html]
            if missing:
                self.err("G38", f"正典プレースホルダー契約の必須変数が無い: {', '.join(missing)}")
            if "TX360 PLACEHOLDER TEMPLATE CONTRACT" not in self.html:
                self.err("G38", "正典HTMLにプレースホルダー運用契約コメントが無い。")
            if "配色パレット選定はAI判断" not in self.html:
                self.err("G38", "正典HTMLに配色パレット選定はAI判断とする例外契約が無い。")

    def g39_tx360_cycle_aids_center_contract(self):
        if not self.html_path.stem.endswith("_lex"):
            return

        css = "\n".join(style.get_text() for style in self.soup.find_all("style"))
        matches = list(re.finditer(r"\.tx-cycle-aids\s*\{(?P<body>[^}]*)\}", css, re.S))
        if not matches:
            self.err("G39", ".tx-cycle-aids のCSSが無い。記憶フック/答案圧縮の2カラム中央寄せテンプレートを入れる。")
            return

        required = {
            "2-column": r"grid-template-columns\s*:\s*repeat\(2\s*,\s*minmax\(0\s*,\s*1fr\)\)",
            "center-width": r"width\s*:\s*min\(92%\s*,\s*1120px\)",
            "center-margin": r"margin\s*:\s*24px\s+auto\s+0",
        }
        ok = False
        best_lacks = list(required)
        for m in matches:
            body = m.group("body")
            lacks = [name for name, pat in required.items() if not re.search(pat, body)]
            if len(lacks) < len(best_lacks):
                best_lacks = lacks
            if not lacks:
                ok = True
                break
        if not ok:
            self.err("G39", f"記憶フック/答案圧縮CSSがTX360中央寄せテンプレートからずれている: {', '.join(best_lacks)}。"
                            "`width:min(92%,1120px); margin:24px auto 0;` を持つ .tx-cycle-aids を正典にする。")

        # The actual TX360 badge/card design is not just the two-column
        # container.  Generated batches may emit either the placeholder shape
        # (`p > .tx-cycle-label`) or an intermediate generated shape
        # (`.tx-cycle-aid > .tx-cycle-title`).  Both must resolve to the same
        # TX360 pill-tab box, otherwise a later compatibility block can silently
        # repaint the badges with palette `--accent` and break the canonical
        # placeholder design.
        strict_needles = {
            "generated-card-selector": ".tx-cycle-aids>.tx-cycle-aid",
            "generated-title-selector": ".tx-cycle-title",
            "pill-top": "top:-13px",
            "pill-left": "left:18px",
            "pill-min-width": "min-width:8.2em",
            "pill-padding": "padding:4px 10px 5px 38px",
            "memory-dot": "content:'記'",
            "compress-dot": "content:'答'",
            "compress-selector": ".tx-cycle-aid.compress .tx-cycle-title",
        }
        compact_css = re.sub(r"\s+", "", css)
        missing = [name for name, needle in strict_needles.items()
                   if re.sub(r"\s+", "", needle) not in compact_css]
        if missing:
            self.err("G39", f"TX360バッジ/ボックス構造CSSが不足: {', '.join(missing)}。"
                            "`.tx-cycle-label` と `.tx-cycle-title` の双方をTX360の"
                            " top:-13px / min-width:8.2em / 記・答丸バッジに固定する。")

    def g40_tx360_inline_initial_state_contract(self):
        if not self.html_path.stem.endswith("_lex"):
            return
        if not self.soup.select_one(".answer-area.inline-prototype-mode[data-answer-type='ox-grid']"):
            return

        css = "\n".join(style.get_text() for style in self.soup.find_all("style"))
        compact_css = re.sub(r"\s+", "", css)
        has_hidden_attr = bool(self.soup.select_one(".tx-inline-explain[hidden]"))
        has_initial_hide_css = ".tx-inline-explain{display:none" in compact_css
        has_reveal_css = ".tx-inline-card.revealed.tx-inline-explain" in compact_css
        if not (has_hidden_attr or has_initial_hide_css):
            self.err("G40", "TX-LEX inline 解説が初期表示される。"
                            "`.tx-inline-explain[hidden]` または `.tx-inline-explain{display:none}` を要求する。")
        if has_initial_hide_css and not has_reveal_css:
            self.err("G40", "TX-LEX inline 解説の reveal CSS が無い。"
                            "○×選択・解説閲覧時だけ `.tx-inline-card.revealed .tx-inline-explain` で表示する。")

        if "根拠条文・判例は、このカード下部の詳説および共通根拠セクションで確認する。" in self.html:
            self.err("G40", "TX360に無い汎用文言が inline カードへ混入している。"
                            "実条文ボックスが無い場合は `.tx-mini-law` ごと出さない。")

        # v13 LOOP-CARD 新設計（カードに旧正典プロースを昇格）では SYNTHESIS 混入を許容する。
        is_v13 = self.soup.select_one(".tx-inline-card .tx-v13-verdict") is not None
        if not is_v13 and self.soup.select_one(".tx-inline-explain .sub-card.synthesis, .tx-inline-explain .sub-card.explanation, .tx-inline-detail .sub-card"):
            self.err("G40", "inline カード内に PART B/SYNTHESIS 長文が混入している。"
                            "通常周回カードは5点フロー＋記憶フック/答案圧縮までに固定する。")

        for title in self.soup.select(".part-title"):
            text = title.get_text(" ", strip=True)
            if text.startswith("PART B ──") and "PART B+" not in text:
                if not title.has_attr("hidden"):
                    self.err("G40", "PART B 詳説タイトルが通常フローに露出している。"
                                    "TX360同様 `.partb-source-title[hidden]` にする。")
                nxt = title.find_next_sibling()
                if not (nxt and nxt.name == "details" and "partb-source" in nxt.get("class", []) and nxt.has_attr("hidden")):
                    self.err("G40", "PART B 詳説本体が通常フローに露出している。"
                                    "TX360同様 `details.partb-source[hidden][aria-hidden=true]` に格納する。")

    def g41_tx360_canonical_engine_integrity(self):
        # TX360 インライン正典は canonical/GENESIS-CORE.html の単一 JS エンジンが
        # `.tx-inline-card` を完全自前で配線する（reveal / browse / toast / PART B 自動注入）。
        # 旧 _lex ベース（旧 Annex C JS）を流用して後付けパッチ script で接ぎ木すると、
        # G1〜G40 は構造要素の「存在」しか見ないため PASS してしまうが、デザイン崩れ・
        # 機能不全・本文肥大（+30〜70K）を招く（§7「保守的書き換え」禁止）。G41 はこの
        # 接ぎ木クラスを機械検出し、canonical エンジンから作り直させるための整合ガード。
        if not self.html_path.stem.endswith("_lex"):
            return
        # v12 インライン正典を名乗るファイル（.tx-inline-card を持つ）だけを対象にする。
        # 旧デザイン _lex（インラインカード無し）は対象外＝温存。
        if not self.soup.select_one(".tx-inline-card"):
            return

        scripts = self.soup.find_all("script")
        joined = "\n".join(s.get_text() for s in scripts)

        # (1) 後付けパッチ script の禁止。canonical エンジンに同等機能が内蔵されており、
        #     band-aid を足すこと自体が「旧エンジン流用」の動かぬ証拠。
        if self.soup.find("script", id="tx-inline-v1211-upgrade-js") or "tx-inline-v1211-upgrade-js" in self.html:
            self.err("G41", "後付けパッチ `tx-inline-v1211-upgrade-js` が存在する。"
                            "canonical/GENESIS-CORE.html の単一エンジンが inline カードを自前配線するので、"
                            "band-aid を足さず canonical からエンジンごと作り直す（§7 保守的書き換え禁止）。")

        # (2) canonical エンジン固有関数の必須化。これらが無い＝旧 Annex C JS を流用している。
        ENGINE_SIGNATURES = [
            "hydrateInlinePartBDetails",  # PART B → 詳説パネル自動注入
            "syncStatementVerdictTable",  # 正誤表へユーザー回答を同期
            "setInlineBrowseState",       # 「解説だけ閲覧」状態管理
            "closeInlineBrowse",
        ]
        missing_sig = [fn for fn in ENGINE_SIGNATURES if fn not in joined]
        if missing_sig:
            self.err("G41", f"canonical inline エンジンの必須関数が欠落: {', '.join(missing_sig)}。"
                            "旧 _lex ベース（旧 Annex C JS）の流用＝接ぎ木の疑い。"
                            "canonical/GENESIS-CORE.html の単一 <script> を逐語コピーで載せ直す。")

        # (3) author script 本数の上限。canonical エンジン 1 本＋解法ナビ(SOLVE-NAV)1 本＝最大 2 本。
        #     3 本以上＝余分なパッチ script が混入している（正実装 360〜365 は 1〜2 本）。
        if len(scripts) > 2:
            self.err("G41", f"<script> が {len(scripts)} 本ある（canonical エンジン＋解法ナビの最大 2 本を想定）。"
                            "余分なパッチ script を除去し、canonical エンジンに統合する。")

    def g42_no_combination_verdict_stmt(self):
        # 組合せ問題の _lex グリッドは「答え選択肢（組合せ1〜5）の当否」を ox-stmt にしてはならない。
        # ox-row/ox-stmt は空欄・記述・事例・論点など「単独で○×判定できる最小学習単位」にし、
        # correct-value はその単位の○×にする（正しい組合せを1つだけ選ぶ5択の○×化＝○1個 は禁止）。
        # 「…とする組合せは正しい/誤り」で終わる ox-stmt は正解番号の暗記でしかなく転用できない。
        # 良い例＝刑TX350（blank モード・各空欄を独立命題化・correct-value 全○）。
        # 悪い例＝刑TX089/174/218/220/256/368（組合せ当否判定）。G30 は「記号のみ肢」を見るが、
        # 本ゲートは「記号を消しても組合せ全体の当否を問うている」構造欠陥を検出する（G30 は素通り）。
        if not self.html_path.stem.endswith("_lex"):
            return
        area = None
        for a in self.soup.find_all(class_="answer-area"):
            if a.get("data-answer-type", "") == "ox-grid":
                area = a
                break
        if area is None:
            return
        combo_re = re.compile(r"組合せ(?:は|として|を|が)?.{0,8}(?:正しい|誤り|誤っ)")
        bad = []
        for row in area.find_all(class_="ox-row"):
            el = row.find(class_="ox-stmt")
            if el and combo_re.search(el.get_text(" ", strip=True)):
                bad.append(row.get("data-stmt") or "?")
        if not bad:
            return
        cv = area.get("data-correct-value", "")
        o_count = sum(1 for c in cv if c in "○◯")
        self.err("G42", f"ox-stmt が組合せ全体の当否を判定している記述: {bad}"
                        f"（correct-value='{cv}' ○={o_count}個）。"
                        "答え選択肢（組合せ1〜5）を ox-row にしない＝組合せ当否判定は正解の暗記で転用不能。"
                        "空欄/記述/事例単位の独立命題へ分解する（見本 刑TX350・blank モードは correct-value 全○）。")

    def g46_no_self_verdict_stmt(self):
        # ox-stmt は「○×判定の対象になる素の命題」であり、命題自身の当否評価
        # （「…は誤り」「…は正しい」、括弧内の（…誤り）、前段/後段の当否メタ言及）を
        # 含んではならない。含めると、正しい命題を述べているのに answer-key が × 等になり、
        # 肢文の字義上の真偽と正解番号が矛盾して学習者を混乱させる。
        #   実害：刑TX363 記述3・記述5 で「（判例の）正しい命題＋『（…は誤り）』注記」が
        #   × 判定と噛み合わず、「合っている命題なのに×？」という誤解を生んだ（2026-07-07）。
        # 原因：ox-stmt の記号フリー正規化時に、元の誤った命題を書く代わりに「正しい見解＋
        # 誤りである旨の解説」を肢文へ書いてしまう癖（LLM の“親切な補足”）。
        # 対処：評価語は解説（.ox-pool-explain）に置き、ox-stmt は元の（＝×になる）素の主張だけにする。
        if not self.html_path.stem.endswith("_lex"):
            return
        area = None
        for a in self.soup.find_all(class_="answer-area"):
            if a.get("data-answer-type", "") == "ox-grid":
                area = a
                break
        if area is None:
            return
        # 括弧内で「別案は誤り／正しい」と編集的に訂正する注記：（…は誤り）（…は正しい）等。
        #   判定語が括弧の末尾（は/が/も＋誤り/正しい…で閉じる）にある場合だけを見る。
        #   これで「（正しい語句はc）」＝先頭が形容詞の空欄補充（刑TX405 型）は除外できる。
        paren_verdict = re.compile(
            r"[（(][^）)]*(?:は|が|も)(?:誤り|誤って(?:いる)?|正しい|妥当でない|妥当でなく|"
            r"判例に反する|判例と矛盾する|判旨に反する)(?:である)?[）)]")
        # 前段/後段など自らの節の当否をメタ言及（複合肢を「片方は誤り」と自己解説する癖）。
        clause_verdict = re.compile(
            r"(?:前段|後段|前半|後半)(?:は|が|の\S{0,10})?(?:誤り|正しい|矛盾|齟齬|反する|妥当でない)")
        # 注：文末の裸の「…は正しい／…は妥当でない」は、座談会型・空欄補充型・見解評価型の
        #   正当な素命題（刑TX090/010/290）なので検出対象にしない（擬陽性回避）。判定語が
        #   「別案への編集的訂正」として括弧内 or 前段/後段に付く形だけを 363 型欠陥として弾く。
        bad = []
        for row in area.find_all(class_="ox-row"):
            el = row.find(class_="ox-stmt")
            if not el:
                continue
            t = el.get_text(" ", strip=True)
            why = None
            if paren_verdict.search(t):
                why = "括弧内で別案の当否を編集的に評価"
            elif clause_verdict.search(t):
                why = "前段/後段の当否をメタ言及"
            if why:
                bad.append((row.get("data-stmt") or "?", why, t[:52]))
        if bad:
            head = "; ".join(f"記述{s}（{why}）『{frag}…』" for s, why, frag in bad[:4])
            more = f" 他 {len(bad)-4} 件" if len(bad) > 4 else ""
            self.err("G46", f"ox-stmt に命題自身の当否評価が混入: {head}{more}。"
                            "ox-stmt は○×の対象になる素の命題だけにし、評価語（誤り/正しい・"
                            "前段後段の当否・括弧注記）は .ox-pool-explain へ移す。"
                            "正しい命題を述べつつ×判定＝字義と正解の矛盾（実害 刑TX363）。")

    def g44_tx_inline_answer_controls_contract(self):
        if not self.html_path.stem.endswith("_lex"):
            return
        if not self.soup.select_one(".tx-inline-card"):
            return

        if self.soup.select_one(".tx-explain-only"):
            self.err("G44", "古い単独の `tx-explain-only` ボタンが残っている。"
                            "`.tx-inline-reveal-panel` 内の `tx-inline-browse-btn` に統一する。")

        if self.soup.select_one(".tx-inline-stmt .tx-inline-label"):
            self.err("G44", "inline 記述に旧 `tx-inline-label` が残っている。"
                            "`choice-num-inline` + `tx-inline-stmt-text` に統一し、番号の二重表示を防ぐ。")

        if self.soup.select_one(".tx-inline-stmt .tx-inline-verdict"):
            self.err("G44", "判定表示 `tx-inline-verdict` が本文内に混入している。"
                            "正典通り `.tx-inline-actions` の末尾へ置く。")

        panel = self.soup.select_one(".tx-inline-reveal-panel")
        if panel is None:
            self.err("G44", "inline 回答操作パネル `.tx-inline-reveal-panel` が無い。"
                            "`解説だけ閲覧` と `解答を表示` を同じパネルに置く。")
        else:
            if panel.select_one(".tx-inline-browse-btn") is None:
                self.err("G44", "`.tx-inline-reveal-panel` 内に `解説だけ閲覧` ボタンが無い。")
            if panel.select_one(".tx-inline-reveal-btn") is None:
                self.err("G44", "`.tx-inline-reveal-panel` 内に `解答を表示` ボタンが無い。")

        if self.soup.select_one(".solve-nav .sn-body") and self.soup.select_one("#sn-combos") is None:
            self.err("G44", "解法ナビに `#sn-combos` が無い。"
                            "候補・進捗表示の受け皿を `.sn-body` 先頭に置く。")
        if self.soup.select_one(".solve-nav"):
            if "sn-answer-choices" not in self.html or "sn-nav-ox" not in self.html:
                self.err("G44", "解法ナビ内に回答用○×ボタンが無い。"
                                "現在STEPの `.sn-answer-choices` / `.sn-nav-ox` を表示し、裏の ox-grid と同期する。")
            if "下の一問一答" in self.html and "このナビ内" not in self.html:
                self.err("G44", "解法ナビが下の一問一答へ誘導するだけになっている。"
                                "ナビ内でその場回答できる導線にする。")

    def g45_tx_v1221_presentation_lock(self):
        # v12.2.1（2026-07-01 実地合意）：
        # 条文/判例の上段ラベルは「題名：」「テーマ：」という説明語を出さず、
        # 下部 basis-card 由来の題名＋法理的テーマだけを表示する。
        # また、ストーリー解説のラベルは本文に重ならない通常フロー配置、
        # 条文/判例本文はラベル列＋本文列の2カラムを正典とする。
        target = self.html_path.stem.endswith("_lex") or self.html_path.name == "GENESIS-CORE.html"
        if not target:
            return
        if self.html_path.stem.endswith("_lex") and not self.soup.select_one(".tx-inline-card"):
            return

        css = "\n".join(style.get_text() for style in self.soup.find_all("style"))
        compact_css = re.sub(r"\s+", "", css)
        scripts = "\n".join(s.get_text() for s in self.soup.find_all("script"))

        legend = self.soup.select_one(".marker-legend")
        if legend:
            legend_text = legend.get_text(" ", strip=True)
            if "論文と重複" not in legend_text or re.search(r"\b論\s*論点\b|論点", legend_text):
                self.err("G45", "マーカー凡例の `論` が `論点` 表記になっている。"
                                "`論` は論文試験と短答試験が重複する箇所のロンマークであり、凡例は `論文と重複` に固定する。")
            if "条文" in legend_text or "裁判例" in legend_text:
                self.err("G45", "マーカー凡例に旧 `条/判` が残っている。"
                                "v12.2 系の凡例は `論＝論文と重複` と頻度（高/中/低）だけにする。")

        if "題名：" in self.html or "テーマ：" in self.html:
            self.err("G45", "条文/判例チップに `題名：` / `テーマ：` の説明文字が残っている。"
                            "表示は basis 由来の題名と法理テーマだけにする。")

        required_script = [
            "findMiniLawBasisCard",
            "extractMiniLawBasisHeading",
            "deriveMiniLawHeading",
            "deriveMiniLawTheme",
            "headingSpan.textContent = heading",
            "span.textContent = theme",
        ]
        missing_script = [sig for sig in required_script if sig not in scripts]
        if missing_script:
            self.err("G45", f"条文/判例チップの v12.2.1 JS が不足: {', '.join(missing_script)}。"
                            "basis-card 見出しから題名を取り、テーマは法理名として出す canonical エンジンを使う。")

        if ".tx-mini-law-title{" not in compact_css or "flex-wrap:wrap" not in compact_css:
            self.err("G45", "`.tx-mini-law-title` が折返し可能な wrap 構造ではない。"
                            "条文/判例/題名/法理テーマのチップ列は横幅に応じて折り返す。")

        for selector in (".tx-mini-law-heading", ".tx-mini-law-theme"):
            if selector not in css:
                self.err("G45", f"{selector} のCSSが無い。"
                                "条文・判例カード上段に題名チップと法理テーマチップを出す。")

        if not re.search(r"\.tx-mini-law-text(?:\.has-label|:has\(\.tx-mini-law-para\))[^{}]*\{[^}]*grid-template-columns\s*:\s*max-content\s+minmax\(0\s*,\s*1fr\)", css, re.S):
            self.err("G45", "条文/判例本文ラベル付き行が2カラムではない。"
                            "`tx-mini-law-para` 列と `tx-mini-law-body` 本文列を分ける。")

        if not re.search(r"\.tx-mini-law-body\s*\{[^}]*text-indent\s*:\s*1em", css, re.S):
            self.err("G45", "`.tx-mini-law-body` の1字下げが無い。"
                            "本文の先頭だけ1字分空け、折返しは本文列に揃える。")

        story_label_blocks = list(re.finditer(r"\.fa-narrative\s*>\s*p\[data-fa-label\]::before\s*\{(?P<body>[^}]*)\}", css, re.S))
        if not story_label_blocks:
            self.err("G45", "物語解説ラベル `.fa-narrative > p[data-fa-label]::before` のCSSが無い。")
        else:
            body = story_label_blocks[-1].group("body")
            if not re.search(r"position\s*:\s*static", body):
                self.err("G45", "物語解説ラベルが `position:static` ではない。"
                                "絶対配置へ戻すと本文に被るため、通常フロー内の左寄せラベルに固定する。")
            if not re.search(r"text-align\s*:\s*left", body):
                self.err("G45", "物語解説ラベルが左寄せではない。")
            if re.search(r"position\s*:\s*absolute", body) or re.search(r"\bleft\s*:", body):
                self.err("G45", "物語解説ラベルに absolute/left 指定が残っている。"
                                "右寄り・本文被りの再発を防ぐため禁止。")

        if not re.search(r"\.fa-narrative-body\s*\{[^}]*text-indent\s*:\s*1em", css, re.S):
            self.err("G45", "物語解説本文 `.fa-narrative-body` の1字下げCSSが無い。"
                            "ラベルではなく本文側だけを包み、段落先頭を1字分空ける。")

        for i, p in enumerate(self.soup.select(".fa-narrative > p[data-fa-label]"), start=1):
            if not p.select_one(".fa-narrative-body"):
                self.err("G45", f"物語解説ラベル付き段落 {i} に `.fa-narrative-body` が無い。"
                                "本文を直書きせず、本文側だけを包んで1字下げにする。")

        onepoint_blocks = list(re.finditer(r"\.tx-onepoint\s+\.tx-op-body\s*\{(?P<body>[^}]*)\}", css, re.S))
        if not onepoint_blocks:
            self.err("G45", "記憶フック本文 `.tx-onepoint .tx-op-body` のCSSが無い。")
        else:
            body = onepoint_blocks[-1].group("body")
            if not re.search(r"text-indent\s*:\s*1em", body):
                self.err("G45", "記憶フック本文 `.tx-op-body` の1字下げが無い。"
                                "本文列全体ではなく、本文先頭だけ1字分空ける。")
            if re.search(r"padding-left\s*:\s*1em", body):
                self.err("G45", "記憶フック本文 `.tx-op-body` に `padding-left:1em` が残っている。"
                                "予約スペースではなく `text-indent:1em` で本文先頭だけ字下げする。")

        answer_review_required = [
            "buildAnswerReview",
            "compactAnswerComparison",
            "formatInlineVerdict",
            "setInlineVerdict",
            "compactReviewTableClone",
            "extractReviewCoreSummary",
            "tx-user-answer-cell",
            "tx-inline-answer-table-panel",
            "tx-review-core-summary",
            "setInlineResult(area, ok, correct)",
        ]
        missing_review = [sig for sig in answer_review_required if sig not in scripts and sig not in self.html]
        if missing_review:
            self.err("G45", f"回答後レビュー/正誤表同期の正典JS/CSSが不足: {', '.join(missing_review)}。"
                            "回答後は解説冒頭の正誤表にユーザー回答を追加し、カード内判定はボタン下2行で表示する。")
        if "tx-inline-toast" in self.html or "tx-toast" in self.html or "showInlineToast" in scripts:
            self.err("G45", "トースト実装が残っている。"
                            "回答後フィードバックは解説冒頭の正誤表とカード内2行判定に集約する。")
        if "あなたの答え" in self.html or re.search(r"function\s+setInlineResult\s*\([^)]*\)\s*\{.*?tx-result-miss", scripts, re.S):
            self.err("G45", "回答操作パネル内の大きな回答サマリー箱が残っている。"
                            "`setInlineResult` はサマリーを描画せず、正誤表同期だけを行う。")
        bad_hint_phrases = [
            "問題文のキーワードを拾い、条文・判例の要件",
            "客体・危険・焼損・故意",
            "結論と個別のコアは採点後に確認できます",
        ]
        leaked_hints = [p for p in bad_hint_phrases if p in self.html]
        if leaked_hints:
            self.err("G45", "解法ナビに汎用・分野ズレのヒント文が残っている: "
                            + " / ".join(leaked_hints)
                            + "。ヒントは具体的な条文要件・判例基準・例外規定へ誘導する。")

        flow_blocks = list(re.finditer(r"\.tx-article-flow\s*>\s*p\s*\{(?P<body>[^}]*)\}", css, re.S))
        if flow_blocks:
            last = flow_blocks[-1].group("body")
            if not re.search(r"grid-template-columns\s*:\s*max-content\s+minmax\(0\s*,\s*1fr\)", last):
                self.err("G45", "5点フローの実効CSSがラベル列＋本文列の2カラムではない。"
                                "モバイルでもラベル下へ本文をぶら下げない。")

        flow_exists = bool(self.soup.select_one(".tx-inline-card .tx-article-flow"))
        has_sysmap = bool(self.soup.select_one(".tx-sysmap"))
        # 整理図は「各肢の論点処理マトリクス」か「問題単位の体系マップ(.tx-sysmap)」のどちらかでよい（v12.2.2）
        matrix_required = flow_exists and not has_sysmap
        if flow_exists and self.soup.select_one(".tx-inline-card .tx-logic-matrix"):
            if ".tx-logic-matrix{" not in compact_css:
                self.err("G45", "論点処理マトリクス `.tx-logic-matrix` のCSSが無い。")
            if not re.search(r"\.tx-matrix-grid\s*\{[^}]*display\s*:\s*grid", css, re.S):
                self.err("G45", "論点処理マトリクス `.tx-matrix-grid` がgrid表示ではない。")
            if ".tx-matrix-verdict{" not in compact_css:
                self.err("G45", "論点処理マトリクスの判断式 `.tx-matrix-verdict` のCSSが無い。")
        if has_sysmap:
            if ".tx-sysmap{" not in compact_css:
                self.err("G45", "体系マップ `.tx-sysmap` のCSSが無い。")
            if not re.search(r"#part-a:has\([^)]*\)\s*\.tx-sysmap", css):
                self.err("G45", "体系マップの表示フック `#part-a:has(...) .tx-sysmap` が無い。"
                                "解説表示（解答を表示／解説だけ閲覧）で現れるようにする。")

        def _norm45(s):
            return re.sub(r"\s+", "", s or "")

        def _lcs45(a, b):
            if not a or not b:
                return 0
            prev = [0] * (len(b) + 1)
            best = 0
            for ca in a:
                cur = [0] * (len(b) + 1)
                for j, cb in enumerate(b, 1):
                    if ca == cb:
                        cur[j] = prev[j - 1] + 1
                        if cur[j] > best:
                            best = cur[j]
                prev = cur
            return best

        def _dupnorm(s):
            # 重複判定用の正規化：正誤プレフィックス・フローラベル・記号/空白を除去して
            # 「実体の言い回し」だけを残す。記憶フックが ANSWER の言い換えかを見るため。
            s = re.sub(r"^\s*[アイウエオカキクケコサシスセソタチツテトナ\dA-Za-z①-⑳（(]{1,6}は[○×]。?\s*", "", s or "")
            s = re.sub(r"^(文言|趣旨|射程|切断点|転用|本質|原則|定義)\s*", "", s)
            return re.sub(r"[\s。、「」『』（）()・：:；;／/…\.\,]", "", s)

        # 条番号チップは ASCII 短縮形（例 112条 / 109条1項・2項）。エンジンの題名・法理テーマ
        # 導出は ASCII 条番号前提で、漢数字（第百十二条）だと導出が全滅し本文16字切りのゴミが出る。
        for _art in self.soup.select(".tx-inline-card .tx-mini-law-article"):
            _at = _art.get_text(strip=True)
            if "{{" in _at:
                continue
            if re.search(r"第[一二三四五六七八九十百千]", _at):
                self.err("G45", f"条番号チップ『{_at}』が漢数字。ASCII短縮形（例 112条 / 109条1項・2項）にする。"
                                "エンジンの題名・法理テーマ導出は ASCII 条番号前提。")

        for i, ex in enumerate(self.soup.select(".tx-inline-card .tx-inline-explain"), start=1):
            if ex.select_one(".tx-answer-box") and not ex.select_one(".tx-mini-law"):
                self.err("G45", f"inlineカード {i} に `tx-mini-law` が無い。"
                                "ANSWER直後に条文/判例ボックスを置き、文言/趣旨/射程だけで根拠を代用しない。")
            answer_text = ""
            answer = ex.select_one(".tx-answer-box .tx-answer-body")
            if answer:
                answer_text = answer.get_text(" ", strip=True)
                # 正誤プレフィックス（例「アは×。」「1は○。」）を剥がしてからラベル漏れを見る。
                # プレフィックス裏に隠れた「アは×。文言 …」型のフロー行丸写しも検出する。
                answer_head = re.sub(
                    r"^\s*[アイウエオカキクケコサシスセソタチツテトナ\dA-Za-z①-⑳（(]{1,6}は[○×]。?\s*",
                    "", answer_text)
                if "{{" in answer_text:
                    pass
                elif re.match(r"^(文言|趣旨|射程|切断点|転用|本質|原則|定義)\b", answer_head):
                    self.err("G45", f"inlineカード {i} の ANSWER が分析ラベル始まり。"
                                    "ANSWER は `条文・判例 → 本件事実 → 成否` の到達形にし、文言/趣旨等の役割名を入れない。")
                elif not re.search(r"(成立|不成立|当たる|当たらない|肯定|否定|可罰|不可罰|既遂|未遂|客体外|含まれない|含む|足りる|足りない|阻却|処罰|非ず|ではない|なし|あり|○|×)", answer_text):
                    self.err("G45", f"inlineカード {i} の ANSWER に結論語が不足。"
                                    "短答周回で使うため、成否・該当性・限界を必ず明示する。")
            hook = ex.select_one(".tx-onepoint .tx-op-body")
            if hook:
                hook_text = hook.get_text(" ", strip=True)
                if re.search(r"(成立するか|当たるか|どれか|正しいか|誤りか)\s*$", hook_text):
                    self.err("G45", f"inlineカード {i} の記憶フックが問題文の焼き直し。"
                                    "1秒で思い出す要件・条文列挙・分岐の合図にする。")
                if len(hook_text) > 55:
                    self.err("G45", f"inlineカード {i} の記憶フックが長すぎる。"
                                    "論点のコア・テーゼを一言の記憶標語にする。")
                if "／" in hook_text and len(hook_text) > 40:
                    self.err("G45", f"inlineカード {i} の記憶フックが説明の連結になっている。"
                                    "判例名・要件・結論を並べるのではなく、1秒で思い出す言葉に圧縮する。")
                # 記憶フックが ANSWER の言い換え（重複）になっていないか（LCS 被覆率で判定）。
                # 較正: 重複問(357/358/359)は 0.85〜1.0、健全な標語は ≤0.48。閾値 0.65 で分離。
                if answer_text:
                    hn, an = _dupnorm(hook_text), _dupnorm(answer_text)
                    if hn and _lcs45(hn, an) / len(hn) >= 0.65:
                        self.err("G45", f"inlineカード {i} の記憶フックが ANSWER の言い換え（重複）。"
                                        "ANSWER とは別の言葉で、短く・イメージしやすく・記憶に刺さる標語にする"
                                        "（結論の再掲でなく、想起の引き金にする）。")
                if re.search(r"→\s*.*成立しない", hook_text) and re.search(r"(成立する|成立し得る|当たる|偽造となる)", answer_text):
                    self.err("G45", f"inlineカード {i} の記憶フックが ANSWER と逆結論に読める。"
                                    "正誤結論は ANSWER・フロー・記憶フックで必ず一致させる。")
                if re.search(r"→\s*.*成立する", hook_text) and re.search(r"(成立しない|客体外|当たらない|含まれない)", answer_text):
                    self.err("G45", f"inlineカード {i} の記憶フックが ANSWER と逆結論に読める。"
                                    "正誤結論は ANSWER・フロー・記憶フックで必ず一致させる。")
            mini = ex.select_one(".tx-mini-law")
            if mini:
                mini_text = mini.get_text(" ", strip=True)
                if re.search(r"\bBASIS\b", mini_text):
                    self.err("G45", f"inlineカード {i} の条文/判例ボックスに BASIS 要約が混入。"
                                    "選択肢判断に実際に使う条文・項・判例だけを載せる。")
                for code in mini.select(".tx-mini-law-code, .tx-mini-law-article"):
                    code_text = code.get_text(" ", strip=True)
                    if code_text in {"根拠", "条文・判例"}:
                        self.err("G45", f"inlineカード {i} の条文/判例チップが汎用名 `{code_text}`。"
                                        "`刑法 / 112条`、`判例 / 最決...` のように根拠そのものを表示する。")
            for text in ex.select(".tx-mini-law-text.has-label, .tx-mini-law-text"):
                if text.select_one(".tx-mini-law-para") and not text.select_one(".tx-mini-law-body"):
                    self.err("G45", f"inlineカード {i} の条文/判例本文に `tx-mini-law-body` が無い。"
                                    "ラベル横本文を包んで2カラム字下げにする。")
            matrix = ex.select_one(".tx-logic-matrix")
            if matrix_required and not matrix:
                self.err("G45", f"inlineカード {i} に整理図が無い。各肢の論点処理マトリクス、"
                                "または問題単位の体系マップ `.tx-sysmap` を置く。")
            if matrix:
                cells = matrix.select(".tx-matrix-cell")
                if len(cells) < 4:
                    self.err("G45", f"inlineカード {i} の論点処理マトリクスが4セル未満。"
                                    "体系的処理手順を01〜04で図解する。")
                verdict_el = matrix.select_one(".tx-matrix-verdict")
                if not verdict_el or len(verdict_el.get_text(" ", strip=True)) < 8:
                    self.err("G45", f"inlineカード {i} の論点処理マトリクスに判断式が不足。"
                                    "最後に結論到達の式を置く。")
                flow = ex.select_one(".tx-article-flow")
                direct = list(ex.find_all(recursive=False))
                if mini and flow and matrix in direct and mini in direct and flow in direct:
                    if not (direct.index(mini) < direct.index(matrix) < direct.index(flow)):
                        self.err("G45", f"inlineカード {i} の論点処理マトリクスの配置順が違う。"
                                        "条文判例の下、5点フローの上に置く。")
                else:
                    self.err("G45", f"inlineカード {i} の論点処理マトリクスが条文判例と5点フローの間にない。"
                                    "同じ階層の直列要素として配置する。")
                # 逐語コピー禁止（spec 58行）：マトリクスは5点フロー/記憶フックの焼き直しにしない
                flow_bodies = [_norm45(b.get_text(" ", strip=True))
                               for b in (flow.select(".tx-flow-body") if flow else [])]
                rehashed = 0
                for cell in cells:
                    be = cell.select_one(".tx-matrix-body")
                    if not be:
                        continue
                    bt = _norm45(be.get_text(" ", strip=True))
                    if not bt or "{{" in bt:
                        continue
                    if any(_lcs45(bt, fb) >= 24 for fb in flow_bodies):
                        rehashed += 1
                if rehashed:
                    self.err("G45", f"inlineカード {i} のマトリクスが5点フローの焼き直し"
                                    f"（{rehashed}セルが本文逐語重複）。マトリクスは"
                                    "『見る軸→確認事実→切る場所→結論到達』の上位地図にし、"
                                    "文言/趣旨/射程/切断点の文をコピーしない。")
                hook_el = ex.select_one(".tx-onepoint .tx-op-body")
                if verdict_el and hook_el:
                    vt = re.sub(r"^判断式", "", _norm45(verdict_el.get_text(" ", strip=True)))
                    ht = _norm45(hook_el.get_text(" ", strip=True))
                    if vt and ht and vt == ht and "{{" not in vt:
                        self.err("G45", f"inlineカード {i} の判断式が記憶フックと同一。"
                                        "判断式は結論到達の決定式、記憶フックは1秒で思い出す標語に役割分離する。")

    def g50_v13_loopcard_structure(self):
        """v13.x LOOP-CARD 構造検証（.tx-v13-verdict 検出時のみ・spec tx-v13.1.0-loopcard-core.md）。"""
        if not self.html_path.stem.endswith("_lex"):
            return
        if not self.soup.select_one(".tx-inline-card .tx-v13-verdict"):
            return  # v13 でなければスキップ（v12 は非退行）
        for i, card in enumerate(self.soup.select(".tx-inline-card"), start=1):
            ex = card.select_one(".tx-inline-explain")
            if not ex:
                continue
            if not ex.select_one(".sub-card.synthesis"):
                self.err("G50", f"v13 カード{i}に統合解説（.sub-card.synthesis）が無い。旧PART Bプロースを本文位置へ昇格する。")
            if not ex.select_one(".choice-points"):
                self.err("G50", f"v13 カード{i}に📌POINT（.choice-points）が無い。")
            basis = ex.select_one(".sub-card.basis-link")
            if not basis:
                self.err("G50", f"v13 カード{i}に📚BASIS（.sub-card.basis-link）が無い。条文/判例を箱内トグルで置く。")
            elif not basis.select_one(".tx-basis-item"):
                # 箱シェルだけで条文/判例が空＝合意（各カードに BASIS）に反する。中身が正典（第6項）。
                self.err("G51", f"v13 カード{i}の📚BASIS（.sub-card.basis-link）に条文/判例（.tx-basis-item）が"
                                "1件も無い＝空箱。旧#basis の ref-backlinks 配分に従い条文/判例を鋳造する（spec 第6項）。")
            # 各記述に⚠️間違いやすいポイント（.tx-v13-trap）＝横串・誤解の罠を積極投入（spec 第5項5・§v13m③）。
            #     trap 無し記述は同型で1枠新設する規約。刑法v13 corpus＋canonical 全充足につき 2026-07-07 ERROR 化。
            trap = ex.select_one(".tx-v13-trap")
            if not trap or not trap.get_text(strip=True):
                self.err("G52", f"v13 カード{i}に⚠️間違いやすいポイント（.tx-v13-trap＝横串解説）が無い/空。"
                                "似た論点の混同・差がつくひっかけを先回りする横串を1枠置く（spec 第5項5・§v13m③）。")
            # v13m規約B（§v13m B）：.syn-image は💭INTUITION（2〜3文の比喩）→🗝記憶のフック（締めの一行標語）へ。
            #     corpus＋canonical 全変換完了につき 2026-07-07 ERROR 化（新規生成で💭のまま出せば弾く）。
            si = ex.select_one(".syn-image .syn-tag")
            if si and ("INTUITION" in si.get_text() or "💭" in si.get_text()):
                self.err("G54", f"v13 カード{i}の.syn-imageが旧『💭 INTUITION』のまま（🗝記憶のフック未変換）。"
                                "2〜3文の比喩を締めの一行標語（鉤括弧の一言）へ圧縮しラベルを🗝記憶のフックにする（§v13m B）。")
            if not ex.select_one(".tx-sysmap-back"):
                self.err("G50", f"v13 カード{i}に体系マップ復路リンク .tx-sysmap-back（↑体系マップに戻る・"
                                "href=#tx-sysmap）が無い。解説末尾に置いてハブ往復させる（第5項7・往路 #stmt-N と対）。")
            for cls, label in ((".tx-answer-box", "ANSWER箱"), (".tx-onepoint", "記憶フック"),
                               (".tx-article-flow", "5点フロー"), (".tx-mini-law", "条文判例チップ")):
                if ex.select_one(cls):
                    self.err("G50", f"v13 カード{i}に廃止要素 {label}（{cls}）が残っている。v13 では削除する。")
        if not self.soup.select_one(".tx-sysmap svg.tree-svg"):
            self.err("G50", "v13 の体系マップ SVG（.tx-sysmap svg.tree-svg）が無い。")
        if self.soup.find(id="mindmap-radial"):
            self.err("G50", "v13 で廃止のはずの #mindmap-radial（放射マップ）が残っている。")
        if self.soup.select_one(".tx-sysmap-back") and not self.soup.find(id="tx-sysmap"):
            self.err("G50", "体系マップ復路リンク（.tx-sysmap-back）の戻り先 id=tx-sysmap が .tx-sysmap に無い（往復が切れる）。")
        # --- v13.1.0 正誤表リデザイン（体系マップ規範核バッジ／正誤表 印付き原文＋成績／重厚感）。
        #     既存 v13 は未移行のため当面 WARNING（tx-lex-verdict-redesign.py＋data-brief-mark/規範核の鋳造で移行後 ERROR 化）。
        if "本問の帰結" in self.html:
            self.warn("G50", "体系マップに旧『本問の帰結（○×）』ネタバレ箱が残っている（答え先出し。v13 リデザインで廃止）。")
        if not self.soup.select_one(".tx-sysmap-svg .nb-badge"):
            self.warn("G50", "体系マップ各札の✍規範核バッジ（.nb-badge）が無い（v13 リデザインの転用可能な規範核）。")
        if "function computeInlineScore(" not in self.html:
            self.warn("G50", "正誤表の成績エンジン computeInlineScore が未導入（tx-lex-verdict-redesign.py で土台注入する）。")
        if not self.soup.select_one("[data-brief-mark]"):
            self.warn("G50", "正誤表行に印付き原文スロット data-brief-mark が無い（v13 リデザイン＝誤り箇所に下線＋正解）。")
        # 第7項 相互リンク往復＝解説内 a.ref-stat[href="#bref-…"] は同カードの BASIS 条文 id に解決する。
        #     配線切れ（存在しない bref-… を指す）は往復ハブが黙って壊れる（174/218 で実害）。当面 WARNING。
        _ids = {e.get("id") for e in self.soup.select("[id]")}
        _broken = [a.get("href") for a in self.soup.select('a.ref-stat[href^="#bref-"]')
                   if a.get("href", "")[1:] not in _ids]
        if _broken:
            self.err("G53", f"相互リンク（a.ref-stat）が存在しない条文 id を指す配線切れ {len(_broken)}件"
                            f"（例 {_broken[0]}）。同カード BASIS の #bref-{{記述}}-{{条番号}} へ配線する（第7項）。")
        # Lexia 復習プールは v13 の THE GIST/POINT と同期する（旧5点フローラベルを残さない・第5-bis項）。
        _old5 = ("文言", "趣旨", "射程", "切断点", "転用")
        for li in self.soup.select(".ox-pool-points li"):
            lt = li.get_text(" ", strip=True)
            head = re.split(r"[：:]", lt, 1)[0].strip()
            if head in _old5:
                self.err("G50", "v13 の Lexia プール（.ox-pool-points）に旧5点フローラベル"
                                f"『{head}：』が残っている。💡THE GIST→gist・📌POINT→points へ再配線する（第5-bis項）。")
                break

    def g55_basis_article_number_label(self):
        """G55 参考条文カードの条番号ラベル整合（2026-07-07・刑TX365/351 の①誤ラベル恒久対策）。

        BASIS 条文カード（.tx-basis-honbun）で、見出しが複数の別条を列挙し各条を1行で並べる型は、
        各行の `.para-num` を条番号（110/112/113…）で揃える。ある条を条番号ではなく項マーカー
        （①〜⑳）でラベルすると、兄弟行（112・113 等）と不整合になり、その条が「前条の一項」に
        見えてしまう（実害：刑TX365/351 の 111条＝延焼罪が①表示）。
        検出条件（誤検出ゼロで真の誤りだけを弾く精密条件）：
          同一 honbun 内に **別条の条番号行が2つ以上** あり、かつ **本文が「第<数字>条」で始まる
          （＝別条を主語にした条文丸ごとの書き出し＝独立の条）行が項マーカーでラベルされている。
        単独条カード（見出しが1条のみで①②が正規の項＝刑TX355/360/364 等）は兄弟条番号が無いので
        非該当＝温存する。
        """
        maru = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
        lead = re.compile(r"^第[0-9０-９]+条")
        for honbun in self.soup.select(".tx-basis-honbun"):
            rows = honbun.select("p.hanging")
            jouban = set()
            for p in rows:
                pn = p.select_one(".para-num")
                if pn and re.match(r"^\s*\d+\s*$", pn.get_text(strip=True)):
                    jouban.add(pn.get_text(strip=True))
            if len(jouban) < 2:
                continue  # 別条を並べる列挙型カードでなければ対象外（単独条の項①②は正規）
            for p in rows:
                pn = p.select_one(".para-num")
                body = p.select_one(".hang-body")
                if not pn or not body:
                    continue
                if pn.get_text(strip=True) in maru and lead.match(body.get_text(strip=True)):
                    self.err("G55", "参考条文カードで別条を列挙しているのに、条『"
                                    f"{body.get_text(strip=True)[:14]}…』の行が条番号ではなく項マーカー"
                                    f"『{pn.get_text(strip=True)}』でラベルされている。兄弟行（"
                                    f"{'・'.join(sorted(jouban))}）と揃えて条番号にする（刑TX365/351 の"
                                    "111条＝延焼罪 ①誤ラベル恒久対策）。")

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
        self.g30_pool_self_contained()
        self.g32_pool_review_text_symbol_free()
        self.g33_tx_lex_reflex_core_five_tags()
        self.g34_tx360_sm2_payload_contract()
        self.g35_fa_narrative_emphasis_weight()
        self.g36_tx360_template_flow_label_text()
        self.g37_tx360_template_visual_contract()
        self.g38_placeholder_contract()
        self.g39_tx360_cycle_aids_center_contract()
        self.g40_tx360_inline_initial_state_contract()
        self.g41_tx360_canonical_engine_integrity()
        self.g42_no_combination_verdict_stmt()
        self.g46_no_self_verdict_stmt()
        self.g44_tx_inline_answer_controls_contract()
        self.g45_tx_v1221_presentation_lock()
        self.g50_v13_loopcard_structure()
        self.g55_basis_article_number_label()


def main():
    if len(sys.argv) != 2:
        print("使い方: python scripts/validate-tx-core.py <HTML ファイルパス>")
        sys.exit(2)
    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"❌ ファイルが見つからない: {html_path}")
        sys.exit(2)

    print(f"\n=== TX v11/v12 LOOP-CORE 検証: {html_path.name} ===\n")
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
        print("✅ ALL (G1〜G45, G17/G18 廃止) PASS")
        sys.exit(0)
    else:
        print("❌ FAIL — ERROR を修正してから再検証してください")
        sys.exit(1)


if __name__ == "__main__":
    main()
