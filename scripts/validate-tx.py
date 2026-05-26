#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX 自己検証スクリプト（v8.11.7 / v9.0.0-genkei / v9.1.0-mindmap / v9.2.0-deepdive 4 バージョン対応）

検証範囲: S1〜S91（仕様書 §31 準拠・主要なものを実装）
  S82: PDF 番号抽出整合（ファイル名 NNN と HTML 内 ID 数字部分の照合）
  S83: placeholder 残存検査（[...] / <!-- 指示: ... --> 検出）
  S84: mindmap section 構造検査（v9.1.0-mindmap 専用 / version-aware）
  S85: ツリー型体系図 section 構造検査（v9.2.0 専用 / mindmap-tree）
  S86: 放射状マインドマップ section 構造検査（v9.2.0 専用 / mindmap-radial・旧 S84 後継）
  S87: 分岐型フローチャート構造検査（v9.2.0 専用 / c-5 内 flow-svg）
  S88: 派生色変数存在検査（v9.2.0 専用 / :root 内 10 派生色 hex 定義）
  S89: §17-ter 学説対立 deep-dive 構造検査（v9.2.0 専用 / theory-detail-grid）
  S90: メタ説明違反検査（v9.2.0 専用 / §0-quad-2-bis ブラックリスト 15 語句）
  S91: 教授解説密度検査（v9.2.0 専用 / prof-heading 150/400/300/300 字）

version-aware ロジック:
  footer-spec の feature-tag から版を判定。各 S 検査は適用版が一致した場合のみ実行。
  - S84: "TX v9.1.0 MINDMAP" 含む場合のみ
  - S85-S91: "TX v9.2.0 DEEP-DIVE" 含む場合のみ（うち S85/S86/S87/S89 は対応 feature-tag も要求）

使い方:
    python scripts/validate-tx.py <HTML ファイルパス>

例:
    python scripts/validate-tx.py outputs/tx/刑TX/刑TX299.html

要件:
    pip install beautifulsoup4

注：Windows PowerShell では既定 cp932 で絵文字 (✅❌⚠️) が出力できない。
    スクリプト先頭で stdout/stderr を utf-8 に reconfigure するため、
    PYTHONIOENCODING=utf-8 環境変数を毎回付与する必要はない。
"""

import colorsys
import json
import sys
import re
from pathlib import Path

# Windows cp932 で絵文字出力時の UnicodeEncodeError 対策
# Python 3.7+ なら stdout/stderr を utf-8 に再構成できる
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。以下を実行してインストールしてください：")
    print("  pip install beautifulsoup4")
    sys.exit(1)


# ============================================================
# §0-quad-2 KTX301 由来の禁止文言ブラックリスト（S78）
# ============================================================

CANONICAL_LEAKAGE_BLACKLIST = [
    # 論点・キーワード系
    "詐欺罪と他罪の成否",
    "詐欺罪のみが成立し得る",
    "詐欺罪と他の罪の双方が成立し得る",
    # 注: 「詐欺罪は成立しない」は一般的な法律述語であり、
    # 詐欺罪論点を扱う任意の問題（例: 刑TX304 予備H25-8）で
    # PDF 原文に出現するため、ブラックリストから除外。
    # 他 4 項目（論点見出し・複合表現）で KTX301 固有検出は維持される。
    "背任行為が同時に詐欺の欺罔行為に当たる",
    "背任罪を別個に構成せず",
    "畏怖の一材料",
    "業務上横領罪",
    "集金業務を委託",
    "偽造通貨行使罪に包含",
    "放火だけでは詐欺の実行着手",
    # 判例引用系（KTX301 で参照される特定の最判・大判）
    "最判昭28.5.8",
    "最判昭24.2.8",
    "東京高判昭28.6.12",
    "大判明5.12.12",
    "大判明43.6.30",
    # KTX301 専用の選択肢例（記述ア〜オの原文をそのまま流用するな）
    "他人のためにその事務を処理する者が、任務に背いて",
    "脅迫文言の中に虚偽の部分があり",
    "新聞販売店から集金業務を委託",
    "保険金を詐取する目的で、火災保険",
    "他人に売買代金として偽造通貨を行使",
]


# ============================================================
# §1-bis 命名規則：科目接頭辞 → 出力先サブフォルダ対応表（S80/S81）
# ============================================================

JP_PREFIX_TO_DIR = {
    "刑TX": "刑TX",
    "憲TX": "憲TX",
    "民TX": "民TX",
    "商TX": "商TX",
    "民訴TX": "民訴TX",
    "刑訴TX": "刑訴TX",
    "行政TX": "行政TX",
}

LEGACY_PREFIXES = ["K", "KEN", "MIN", "SYO", "MINS", "KEIS", "GSE"]


# ============================================================
# S12: instruction_type → 期待 choice-section 件数（slotmap §5.1〜§6.7）
# ============================================================

EXPECTED_CHOICE_COUNT = {
    "ox-grid-5": 5,
    "ox-grid-4": 4,
    "multi-select-5": 5,
    "single-choice-5": 5,
    "combination-5": 5,
    "fill-in": 5,
    "ox-grid-3-combination-8": 3,   # 記述ア〜ウ 3 件 + 組合せ 1〜8
    "fillin8": 5,
}

# HTML 出力ディレクトリ名 → JSON 命名規則用 subject 接頭辞
JP_DIR_TO_SUBJECT = {
    "刑TX": "KEI",   # KEI: problems/{NNN}.json（接頭辞なし）
    "憲TX": "KEN",
    "民TX": "MIN",
    "商TX": "SYO",
    "民訴TX": "MINS",
    "刑訴TX": "KEIS",
    "行政TX": "GSE",
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = PROJECT_ROOT / "problems"


# ============================================================
# spec バージョン判定（v9.2.0 Task 10 § 3）
# ============================================================

SPEC_VERSION_PATTERNS = [
    ("v9.3.0", re.compile(r"TX\s+v9\.3\.0\s+PALETTE-MULTI-VARIANT")),
    ("v9.2.0", re.compile(r"TX\s+v9\.2\.0\s+DEEP-DIVE")),
    ("v9.1.0", re.compile(r"TX\s+v9\.1\.0\s+MINDMAP")),
    ("v9.0.0", re.compile(r"TX\s+v9\.0\.0\s+GENKEI")),
    ("v8.11.7", re.compile(r"TX\s+v8\.11\.7")),
]


def detect_spec_version(soup):
    """footer-spec の feature-tag から spec バージョンを判定。

    判定優先順：v9.2.0 → v9.1.0 → v9.0.0 → v8.11.7 → "unknown"
    """
    footer = soup.find(class_="footer-spec")
    if footer is None:
        return "unknown"
    feature_text = " ".join(
        tag.get_text(strip=True) for tag in footer.find_all(class_="feature-tag")
    )
    for version, pattern in SPEC_VERSION_PATTERNS:
        if pattern.search(feature_text):
            return version
    return "unknown"


def footer_has_tag(soup, tag_text):
    """footer-spec の feature-tag に当該文字列を含むか。"""
    footer = soup.find(class_="footer-spec")
    if footer is None:
        return False
    for tag in footer.find_all(class_="feature-tag"):
        if tag_text in tag.get_text(strip=True):
            return True
    return False


# ============================================================
# v9.2.0 派生色 10 個（S88）
# ============================================================

V92_DERIVATIVE_COLORS = [
    "--accent-light",
    "--accent-darker",
    "--mid-warm",
    "--mid-cool",
    "--accent-soft-2",
    "--mid-soft",
    "--surface-tint",
    "--neutral-cream",
    "--contrast-warm",
    "--contrast-cool",
]


# ============================================================
# v9.3.0 PALETTE-MULTI-VARIANT 検査定数（S88 改訂 / S92 新規 / AP-47）
# ============================================================

# 27 サブパレット ID（flat 構造・S92 ID 整合性検査用）
SUBPALETTES_V93_FLAT: dict = {
    # P1 桜彩
    "sakura-haze":         {"category": "P1", "label_ja": "桜霞"},
    "spring-twilight":     {"category": "P1", "label_ja": "春薄明"},
    "peony-glow":          {"category": "P1", "label_ja": "牡丹陽"},
    "hydrangea-dusk":      {"category": "P1", "label_ja": "紫陽花宵"},
    "wisteria-moon":       {"category": "P1", "label_ja": "藤霞月"},
    "kerria-bloom":        {"category": "P1", "label_ja": "山吹陽"},
    "crimson-camellia":    {"category": "P1", "label_ja": "鮮椿青"},
    "hydrangea-morn":      {"category": "P1", "label_ja": "紫陽朝"},
    "spring-aureate":      {"category": "P1", "label_ja": "春金苑"},
    # P2 翠彩
    "verdant-rose":        {"category": "P2", "label_ja": "翠紅園"},
    "golden-verdant":      {"category": "P2", "label_ja": "山吹翠苑"},
    "young-sprout":        {"category": "P2", "label_ja": "若苗野"},
    "moss-blossom":        {"category": "P2", "label_ja": "苔月華"},
    "azure-orchid":        {"category": "P2", "label_ja": "群青蘭"},
    "early-jade":          {"category": "P2", "label_ja": "早春翠"},
    "vermilion-garden":    {"category": "P2", "label_ja": "朱檀苑"},
    "crimson-jade":        {"category": "P2", "label_ja": "朱赭翠"},
    "golden-harvest":      {"category": "P2", "label_ja": "黄金穂"},
    # P3 玄彩
    "moonfrost-violet":    {"category": "P3", "label_ja": "月霜紫"},
    "starlit-amethyst":    {"category": "P3", "label_ja": "星辰深紫"},
    "wine-galaxy":         {"category": "P3", "label_ja": "葡萄銀河"},
    "dusk-violet":         {"category": "P3", "label_ja": "黄昏菫"},
    "hydrangea-afterglow": {"category": "P3", "label_ja": "紫陽花残光"},
    "sapphire-moon":       {"category": "P3", "label_ja": "紺碧月華"},
    "dawn-nebula":         {"category": "P3", "label_ja": "暁星雲"},
    "violet-firework":     {"category": "P3", "label_ja": "紫煙花火"},
    "emerald-violet":      {"category": "P3", "label_ja": "青翠菫光"},
}


# v9.3.0 派生色変数（14 個・S88 検査対象）
DERIVED_COLOR_VARS_V93 = [
    "--accent", "--mid", "--base",
    "--accent-light", "--accent-darker", "--accent-soft", "--accent-soft-2",
    "--mid-warm", "--mid-cool", "--mid-soft", "--surface-tint",
    "--neutral-cream", "--contrast-warm", "--contrast-cool",
]

# 絶対派生 3 個（S88 で固定値検査）
ABSOLUTE_DERIVATIVES_V93 = {
    "--neutral-cream": "#F4EDE0",
    "--contrast-warm": "#D97A4F",
    "--contrast-cool": "#6A8AA8",
}

# HSL 派生パラメータ（spec §32-5-2）
HSL_DERIVATIONS_V93 = {
    "--accent-light":   ("--accent",   0,  -8, +13),
    "--accent-darker":  ("--accent",   0,  +5,  -4),
    "--accent-soft":    ("--accent",   0, -25, +18),
    "--accent-soft-2":  ("--accent",   0, -15, +25),
    "--mid-warm":       ("--mid",     +8,  +5,  +6),
    "--mid-cool":       ("--mid",     -8,  -5,  +0),
    "--mid-soft":       ("--mid",      0, -10, +20),
    "--surface-tint":   ("--accent",   0, -20, +30),
}


def _v93_hex_to_hsl(hex_str: str) -> tuple:
    hex_clean = hex_str.lstrip("#")
    if len(hex_clean) != 6:
        raise ValueError(f"invalid hex: {hex_str}")
    r, g, b = (int(hex_clean[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s * 100, l * 100)


def _v93_hsl_to_hex(h: float, s: float, l: float) -> str:
    h_norm = (h % 360) / 360.0
    s_norm = max(0.0, min(100.0, s)) / 100.0
    l_norm = max(0.0, min(100.0, l)) / 100.0
    r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)
    return "#" + "".join(f"{int(round(c * 255)):02X}" for c in (r, g, b))


def _v93_hex_distance(hex_a: str, hex_b: str) -> int:
    a = hex_a.lstrip("#").upper()
    b = hex_b.lstrip("#").upper()
    if len(a) != 6 or len(b) != 6:
        return 999
    return sum(abs(int(a[i:i+2], 16) - int(b[i:i+2], 16)) for i in (0, 2, 4))


# ============================================================
# v9.2.0 メタ説明禁止カテゴリ（S90 / §0-quad-2-bis）
# ============================================================

META_EXPLANATION_PATTERNS = [
    # 肢系
    re.compile(r"肢[\d１-５ア-オ]\s*を選[ぶびうい]"),
    re.compile(r"肢[\d１-５ア-オ]\s*を選択"),
    re.compile(r"肢[\d１-５ア-オ]\s*が正解"),
    re.compile(r"正解の肢は"),
    re.compile(r"本問の正解は"),
    # 記号系
    re.compile(r"記号[ア-オ]\s*を選[ぶびうい]"),
    re.compile(r"記号[ア-オ]\s*を選択"),
    re.compile(r"[ア-オ]の組合せが正解"),
    # 手順系
    re.compile(r"解答の手順"),
    re.compile(r"解答プロセス"),
    re.compile(r"正解を選ぶプロセス"),
    re.compile(r"解答に至る手順"),
    # メタ説明系
    re.compile(r"本問では.+を選[べびう]"),
    re.compile(r"選び方の説明"),
]

META_CHECK_SELECTORS = [
    ".basis-card-body",
    ".sub-card.professor",
    ".sub-card.explanation",
    "section#c-4",
    "section#mindmap-tree",
    "section#mindmap-radial",
    "section#c-5",
    ".key-phrase-box",
]


# ============================================================
# v9.2.0 教授解説密度規律（S91 / §0-quad-3 STEP IQ-5 強化版）
# ============================================================

PROF_DENSITY_REQUIREMENTS = [
    (".prof-heading.prof-point", 150),
    (".prof-heading.prof-process", 400),
    (".prof-heading.prof-image", 300),
    (".prof-heading.prof-application", 300),
]

PROF_IMAGE_SUBELEMENTS = [".image-scene", ".image-bridge", ".image-contrast"]
PROF_SYLLOGISM_SUBELEMENTS = [".syl-major", ".syl-minor", ".syl-conclusion"]


def derive_problem_json_path(html_path):
    """HTML ファイルパスから対応する problems/{ID}.json を逆引きする。
    例:
      outputs/tx/刑TX/刑TX327.html   → problems/327.json
      outputs/tx/行政TX/行政TX001.html → problems/GSE001.json
    決定できない場合は None。
    """
    p = Path(html_path)
    parent_jp = p.parent.name
    stem = p.stem
    subject = JP_DIR_TO_SUBJECT.get(parent_jp)
    if subject is None or not stem.startswith(parent_jp):
        return None
    num = stem[len(parent_jp):]
    if subject == "KEI":
        return PROBLEMS_DIR / f"{num}.json"
    return PROBLEMS_DIR / f"{subject}{num}.json"


def get_expected_choice_count(html_path):
    """problems/{ID}.json の instruction_type から期待 choice-section 数を返す。
    取得できなければ 5（ox-grid-5 既定）にフォールバック。
    Returns: (expected_n, instruction_type_or_None)
    """
    jp = derive_problem_json_path(html_path)
    if jp is None or not jp.exists():
        return 5, None
    try:
        data = json.loads(jp.read_text(encoding="utf-8"))
    except Exception:
        return 5, None
    itype = data.get("instruction_type")
    if itype is None:
        return 5, None
    return EXPECTED_CHOICE_COUNT.get(itype, 5), itype


# ============================================================
# レポート用ヘルパー
# ============================================================

class Reporter:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, check_id, msg):
        self.errors.append(f"[{check_id}] {msg}")

    def warn(self, check_id, msg):
        self.warnings.append(f"[{check_id}] {msg}")

    def summary(self, target):
        print(f"\nTX 検証結果: {target}")
        if self.errors:
            print(f"\n❌ ERROR ({len(self.errors)} 件):")
            for e in self.errors:
                print(f"  {e}")
        if self.warnings:
            print(f"\n⚠️  WARNING ({len(self.warnings)} 件):")
            for w in self.warnings:
                print(f"  {w}")
        if not self.errors and not self.warnings:
            print("\n✅ 配信可能（ERROR 0 / WARNING 0）")
        elif not self.errors:
            print(f"\n✅ 配信可能（ERROR 0 / WARNING {len(self.warnings)} ※必要に応じて修正）")
        else:
            print(f"\n❌ 配信不可（ERROR {len(self.errors)} を修正してください）")
        return 0 if not self.errors else 1


# ============================================================
# 検証本体
# ============================================================

def get_style_text(soup):
    return "\n".join(s.get_text() for s in soup.find_all("style"))


def get_script_text(soup):
    return "\n".join(s.get_text() for s in soup.find_all("script"))


def get_visible_text(soup):
    """スクリプト・スタイル・コメントを除いた可視テキスト"""
    for s in soup(["script", "style"]):
        s.extract()
    return soup.get_text(" ", strip=True)


def check_structure(target_path, soup, html, rep):
    """S1〜S51: 構造系基本検査"""

    # S1-S6: タグ開閉バランス
    for tag in ["div", "section", "a", "span", "p"]:
        opens = len(re.findall(rf"<{tag}[\s>]", html))
        closes = len(re.findall(rf"</{tag}>", html))
        if opens != closes:
            rep.error(f"S1-{tag}", f"<{tag}> 開閉数不一致: open={opens}, close={closes}")

    # S7: id 重複
    ids = [el.get("id") for el in soup.find_all(id=True)]
    dup_ids = [i for i in set(ids) if ids.count(i) > 1]
    if dup_ids:
        rep.error("S7", f"id 重複: {dup_ids}")

    # S8: href="#X" の X が id で実在
    anchor_links = [a.get("href")[1:] for a in soup.find_all("a", href=True)
                    if a.get("href", "").startswith("#") and len(a.get("href", "")) > 1]
    missing = [h for h in set(anchor_links) if h not in ids]
    if missing:
        rep.warn("S8", f"未解決アンカー: {missing[:5]}{'...' if len(missing)>5 else ''}")

    # S9: marker-legend が </header> 直後
    if not soup.find("div", class_="marker-legend"):
        rep.error("S9", "marker-legend が存在しない")

    # S10: 4 PART タイトル存在
    part_titles = [pt.get_text() for pt in soup.find_all("div", class_="part-title")]
    needed = ["PART A", "PART B", "PART C", "PART D"]
    for p in needed:
        if not any(p in t for t in part_titles):
            rep.error("S10", f"{p} part-title が欠落")

    # S11: PART A に 2 section（A-1, A-2）
    if not soup.find("section", id="part-a"):
        rep.error("S11", "section#part-a 欠落")
    if not soup.find("section", id="answer-area"):
        rep.error("S11", "section#answer-area 欠落")

    # S12: PART B に N choice-section（N は instruction_type ベースで決定）
    # ox-grid-4 → 4, ox-grid-3-combination-8 → 3, それ以外 → 5
    choice_sections = soup.find_all("section", class_="choice-section")
    expected_n, itype = get_expected_choice_count(target_path)
    if len(choice_sections) != expected_n:
        rep.error(
            "S12",
            f"choice-section: instruction_type={itype or 'unset'} は期待 {expected_n} 件, "
            f"実際 {len(choice_sections)} 件",
        )

    # S13: PART C に 7 section（c-1〜c-7）
    for i in range(1, 8):
        if not soup.find("section", id=f"c-{i}"):
            rep.warn("S13", f"section#c-{i} 欠落")

    # S14: PART D に drill-block が複数
    drill_blocks = soup.find_all("div", class_="drill-block")
    if len(drill_blocks) < 1:
        rep.error("S14", "drill-block が存在しない")
    elif len(drill_blocks) < 12:
        rep.warn("S14", f"drill-block: 期待 12 件, 実際 {len(drill_blocks)} 件")

    # S15-S16: data-correct-value / data-explanation
    ans = soup.find(class_="answer-area")
    if ans:
        if not ans.get("data-correct-value"):
            rep.error("S15", "answer-area の data-correct-value 未設定")
        if not ans.get("data-explanation"):
            rep.error("S16", "answer-area の data-explanation 未設定")

    # S17: 各 choice-section に 4 sub-card（original/explanation/basis-link/professor）
    required_cards = ["original", "explanation", "basis-link", "professor"]
    for cs in choice_sections:
        cs_id = cs.get("id", "?")
        # sub-card は <div class="sub-card original"> 等の複合 class なので class 含有でマッチ
        found_cards = set()
        for div in cs.find_all("div", class_="sub-card"):
            div_classes = div.get("class", [])
            for r in required_cards:
                if r in div_classes:
                    found_cards.add(r)
        missing = [r for r in required_cards if r not in found_cards]
        if missing:
            rep.warn("S17", f"{cs_id}: sub-card 欠落 {missing}")


def check_v8110_layers(html, style_text, rep):
    """S64〜S67: v8.11.0 で追加された層"""

    # S64: §24 readability layer
    if not re.search(r"\.section\s+h3\s*\{", style_text):
        rep.warn("S64-1", "§24-1 (.section h3) 規則が見つからない")
    if not re.search(r"\.cross-grid\s+\.cross-card:nth-child", style_text):
        rep.warn("S64-2", "§24-2 (.cross-card 奇偶交互背景) 規則が見つからない")
    if not re.search(r"\.memory-list\s+\.memory-item\.priority-a", style_text):
        rep.warn("S64-3", "§24-3 (.memory-item priority-a) 規則が見つからない")
    if not re.search(r"\.lead-list\s*>\s*li\s*\{", style_text):
        rep.warn("S64-4", "§24-4 (.lead-list > li) 規則が見つからない")
    if not re.search(r"\.basis-card-body\s*>\s*p\.hanging\s*\{", style_text):
        rep.warn("S64-6", "§24-6 (.basis-card-body > p.hanging) 規則が見つからない")

    # S65: hanging 構造
    # <p class="..." includes "hanging"> をすべてカウント（"judgment-text hanging" 等の複合 class 対応）
    hanging_p_count = len(re.findall(r'<p\s+[^>]*\bclass="[^"]*\bhanging\b[^"]*"', html))
    hang_body_count = len(re.findall(r'<span\s+[^>]*\bclass="[^"]*\bhang-body\b[^"]*"', html))
    if hanging_p_count > 0 and hanging_p_count != hang_body_count:
        rep.error(
            "S65",
            f"<p class='hanging'> 数 ({hanging_p_count}) と "
            f"<span class='hang-body'> 数 ({hang_body_count}) が不一致",
        )

    # S66: PART 順序（A-3 が PART B の後・PART C の前）
    basis_pos = html.find('id="basis"')
    choice5_pos = html.find('id="choice-5"')
    c1_pos = html.find('id="c-1"')
    if basis_pos != -1 and choice5_pos != -1 and basis_pos < choice5_pos:
        rep.error("S66", "<section id='basis'> が PART B の前にある（PART B の後ろに移動必要）")
    if basis_pos != -1 and c1_pos != -1 and basis_pos > c1_pos:
        rep.error("S66", "<section id='basis'> が PART C の後ろにある（PART C の前に移動必要）")

    # S67: font-weight + AP-26/27/28 検出
    m = re.search(r"\.basis-card-body\s*\{[^}]*font-weight\s*:\s*(\d+)", style_text)
    if m:
        if int(m.group(1)) < 600:
            rep.error("S67", f".basis-card-body の font-weight が 600 未満: {m.group(1)}")
    else:
        rep.warn("S67", ".basis-card-body の font-weight 未指定（600 が canonical）")

    m = re.search(r"a\.ref-stat[^{]*\{[^}]*font-weight\s*:\s*(\d+)", style_text)
    if m and int(m.group(1)) < 700:
        rep.error("S67", f"a.ref-stat の font-weight が 700 未満: {m.group(1)}")

    # AP-28: .ron-mark に display:inline-block
    m = re.search(r"\.ron-mark\s*\{([^}]*)\}", style_text)
    if m and "inline-block" in m.group(1) and "display" in m.group(1):
        rep.error("S67/AP-28", ".ron-mark に display:inline-block が指定されている（AP-28 違反）")

    # AP-27: .basis-card-body > p に display:flex/grid 直当て
    if re.search(r"\.basis-card-body\s*>\s*p\s*\{[^}]*display\s*:\s*(flex|grid)\b", style_text):
        rep.error("S67/AP-27", ".basis-card-body > p に display:flex/grid 直当て（AP-27 違反）")

    # AP-26: 負 text-indent
    if re.search(r"\.basis-card-body\s*>\s*p\s*[^{]*\{[^}]*text-indent\s*:\s*-\d", style_text):
        rep.error("S67/AP-26", ".basis-card-body > p に負の text-indent（AP-26 違反）")


def check_content_independence(soup, rep):
    """S78〜S69: コンテンツ独立性"""

    visible = get_visible_text(soup)

    # S68: KTX301 由来文言ブラックリスト
    title_text = soup.title.get_text() if soup.title else ""
    doc_header_el = soup.find(class_="doc-header")
    doc_header_text = doc_header_el.get_text() if doc_header_el else ""

    # 本問が KTX301 と同じ問題（KTX301 / 刑TX301）かどうかを判定
    is_ktx301_itself = bool(
        re.search(r"\bKTX301\b", title_text + doc_header_text)
        or re.search(r"刑TX301", title_text + doc_header_text)
    )

    hits = []
    for phrase in CANONICAL_LEAKAGE_BLACKLIST:
        if phrase in visible:
            hits.append(phrase)

    if hits and not is_ktx301_itself:
        rep.error(
            "S78/AP-42",
            f"canonical text leakage 検出（KTX301 由来文言が本問に出現）: "
            f"{hits[:3]}{'... 他 '+str(len(hits)-3)+' 件' if len(hits)>3 else ''}",
        )
        rep.error(
            "S78/AP-42",
            "本問が真にこの論点を扱う場合のみ許容。そうでなければ §0-quad-3 IQ-2 から再執筆",
        )
    elif hits and is_ktx301_itself:
        # 自分自身が KTX301 なら検査をスキップ
        pass

    # S69: structural shell only 原則違反（簡易版）
    # ※完全な §Annex B 元テキストとの比較は実装が重いため、
    #   よく流用される代表 4 文字列の出現で代用検出する
    ktx301_signature_fragments = [
        "他人のためにその事務を処理する者",
        "脅迫文言の中に虚偽の部分",
        "新聞販売店から集金業務",
        "保険金を詐取する目的で",
    ]
    sig_hits = [s for s in ktx301_signature_fragments if s in visible]
    if sig_hits and not is_ktx301_itself:
        rep.error(
            "S79",
            f"§Annex B 元テキストとの長文一致を検出: {sig_hits}",
        )


def check_naming(target_path, soup, rep):
    """S80〜S72: 命名規則"""

    filename = Path(target_path).name
    parent_dir = Path(target_path).parent.name

    # canonical/KTX301.html は構造参考ファイルであり命名規則検証の対象外
    if filename == "KTX301.html" and parent_dir == "canonical":
        return

    # S70: ファイル名形式 = "{日本語接頭辞}TX{3桁0埋め数字}.html"
    pattern_jp = (
        r"^(刑TX|憲TX|民TX|商TX|民訴TX|刑訴TX|行政TX)(\d{3,})\.html$"
    )
    m = re.match(pattern_jp, filename)
    if not m:
        # レガシー形式チェック
        if re.match(r"^(K|KEN|MIN|SYO|MINS|KEIS|GSE)\d+\.html$", filename):
            rep.error(
                "S80",
                f"レガシー命名形式: {filename}（現行形式 {{日本語接頭辞}}TX{{3桁}}.html に更新必要）",
            )
        else:
            rep.error(
                "S80",
                f"ファイル名が現行形式に非該当: {filename}",
            )
        return

    prefix = m.group(1)
    number = m.group(2)

    # S70: ファイル ID が <title>/<div class="doc-header">/footer-spec 3 箇所一致
    file_id = f"{prefix}{number}"
    title_text = soup.title.get_text() if soup.title else ""
    doc_header_el = soup.find(class_="doc-header")
    doc_header_text = doc_header_el.get_text() if doc_header_el else ""
    footer_el = soup.find(class_="footer-spec")
    footer_text = footer_el.get_text() if footer_el else ""

    if file_id not in title_text:
        rep.error("S80", f"<title> にファイル ID '{file_id}' が含まれない: '{title_text}'")
    if file_id not in doc_header_text:
        rep.error("S80", f".doc-header にファイル ID '{file_id}' が含まれない: '{doc_header_text}'")
    if file_id not in footer_text:
        rep.error("S80", f"footer-spec にファイル ID '{file_id}' が含まれない")

    # レガシー形式が混在していないかチェック
    for legacy in LEGACY_PREFIXES:
        if re.search(rf"\b{legacy}\d{{2,}}\b", title_text + doc_header_text):
            rep.warn("S80", f"レガシー接頭辞 '{legacy}' がメタ情報に残存している可能性")
            break

    # S71: 出力先サブフォルダが §1-bis-3 対応表通り
    expected_dir = JP_PREFIX_TO_DIR.get(prefix)
    if parent_dir != expected_dir:
        rep.error(
            "S81",
            f"出力先サブフォルダ不整合: 接頭辞 {prefix} は outputs/tx/{expected_dir}/ 配下のはずだが、"
            f"実際は .../{parent_dir}/",
        )


def check_misc(target_path, soup, html, style_text, rep):
    """その他の重要チェック"""

    filename = Path(target_path).name
    parent_dir = Path(target_path).parent.name
    is_canonical_reference = (filename == "KTX301.html" and parent_dir == "canonical")

    # AP-41 / S77: <script> 内に </body> リテラル禁止
    script_text = get_script_text(soup)
    if "</body>" in script_text:
        rep.error(
            "AP-41",
            "<script>...</script> 内に </body> リテラル文字列を検出（Lexia 致命的バグ・"
            "代替表記『</`+`body>』等を使用）",
        )

    # K302-16: #answer-feedback strong{color:#fff !important}
    if re.search(
        r"#answer-feedback\s+strong\s*\{[^}]*color\s*:\s*#fff[^}]*!important", style_text
    ):
        rep.error(
            "S62/K302-16",
            "#answer-feedback strong{color:#fff !important} が CSS に残存（旧 v8.6 バグ）",
        )

    # 必須 feature-tag
    # 注：canonical/KTX301.html は v8.11.0 ベースの構造参考なので
    # spec バージョン専用タグの検査対象外とする（編集を誘発しないため）
    if not is_canonical_reference:
        # spec バージョン feature-tag（v8.11.7 / v9.0.0-genkei / v9.1.0-mindmap / v9.2.0-deepdive いずれか必須）
        spec_version_tags = ["TX v8.11.7", "TX v9.0.0 GENKEI", "TX v9.1.0 MINDMAP", "TX v9.2.0 DEEP-DIVE"]
        # 共通必須 feature-tag
        common_required_tags = ["ktx301-canon", "jp-prefix-naming", "content-independence"]
        footer_el = soup.find(class_="footer-spec")
        if footer_el:
            footer_text = footer_el.get_text()
            # spec バージョンタグ：OR 条件（いずれか 1 つあれば PASS）
            if not any(tag in footer_text for tag in spec_version_tags):
                rep.warn("S51", "footer-spec に spec バージョン feature-tag が含まれない（'TX v8.11.7' / 'TX v9.0.0 GENKEI' / 'TX v9.1.0 MINDMAP' / 'TX v9.2.0 DEEP-DIVE' のいずれか必須）")
            # 共通必須タグ：AND 条件（全て必須）
            for tag in common_required_tags:
                if tag not in footer_text:
                    rep.warn("S51", f"footer-spec に feature-tag '{tag}' が含まれない")
        else:
            rep.error("S51", "footer-spec が存在しない")

    # AP-24: P2/P3 override が単一 :root{} ブロックのみであること
    # （複雑な解析が必要なので簡易チェック）
    # v9.2.0 では §Annex A-z-1 派生色 :root が追加で 1 ブロック許容（合計 3 まで）
    root_blocks = re.findall(r":root\s*\{", style_text)
    spec_version = detect_spec_version(soup)
    max_allowed = 3 if spec_version == "v9.2.0" else 2
    if len(root_blocks) > max_allowed:
        rep.warn(
            "S60/AP-24",
            f":root{{}} ブロックが {len(root_blocks)} 個存在（{spec_version} では {max_allowed} 個まで）",
        )


# ============================================================
# S82: PDF 番号抽出整合（ファイル名 NNN と HTML 内 ID 数字部分の照合）
# ============================================================

def check_number_integrity(target_path, soup, rep):
    """S82: ファイル名から抽出した NNN と
    <title> / .doc-header / .footer-spec 内の ID 数字部分が全て一致することを確認"""

    filename = Path(target_path).name
    parent_dir = Path(target_path).parent.name

    # canonical/KTX301.html は対象外
    if filename == "KTX301.html" and parent_dir == "canonical":
        return

    m = re.match(r"^(刑|憲|民|商|民訴|刑訴|行政)(TX|JX)(\d{3,})\.html$", filename)
    if not m:
        # 非該当ファイル名は S80 が捕捉済み。S82 は対象外
        return

    prefix, series, nnn = m.group(1), m.group(2), m.group(3)
    file_id = f"{prefix}{series}{nnn}"
    id_pattern = rf"{re.escape(prefix)}{re.escape(series)}(\d{{3,}})"

    title_text = soup.title.get_text() if soup.title else ""
    doc_header_el = soup.find(class_="doc-header")
    doc_header_text = doc_header_el.get_text() if doc_header_el else ""
    footer_el = soup.find(class_="footer-spec")
    footer_text = footer_el.get_text() if footer_el else ""

    def extract_nnn(text):
        m2 = re.search(id_pattern, text)
        return m2.group(1) if m2 else None

    found = {
        "title": extract_nnn(title_text),
        "doc-header": extract_nnn(doc_header_text),
        "footer-spec": extract_nnn(footer_text),
    }

    bad_locations = [name for name, num in found.items() if num != nnn]
    if bad_locations:
        details = []
        for name, num in found.items():
            if num is None:
                details.append(f"{name}: ({prefix}{series}NNN not found)")
            elif num != nnn:
                details.append(f"{name}: {prefix}{series}{num}（不一致）")
            else:
                details.append(f"{name}: {prefix}{series}{num}")
        rep.error(
            "S82",
            f"ファイル名 NNN={nnn} と HTML 内 ID 不整合: filename={file_id}; "
            + "; ".join(details),
        )


# ============================================================
# S83: v9.0.0-genkei placeholder 残存検査
# ============================================================

def check_placeholder_residue(target_path, soup, html, rep):
    """S83: 未差替 placeholder（[...] / <!-- 指示: ... -->）の残存を検出

    パターン A: 可視テキスト内の [...]（<a> タグ・<script>・<style> 内を除外）
    パターン B: <!-- 指示: ... --> 指示コメント残存
    法令引用（第XX条 / 最判昭○○ 等）は誤検出回避のため除外
    """

    filename = Path(target_path).name
    parent_dir = Path(target_path).parent.name
    if filename == "KTX301.html" and parent_dir == "canonical":
        return

    # パターン B: <!-- 指示: ... --> 残存
    instruction_comments = re.findall(r"<!--\s*指示:.*?-->", html, re.DOTALL)

    # パターン A: 可視テキスト内の [...]
    # <a> / <script> / <style> 内テキストおよび属性値を除外したテキストを抽出
    soup_copy = BeautifulSoup(html, "html.parser")
    for tag in soup_copy(["script", "style", "a"]):
        tag.extract()
    visible_text = soup_copy.get_text(" ", strip=False)

    # 元仕様は {0,50} だが genkei の長い placeholder を見逃すため {1,200} に拡張
    bracket_pattern = re.compile(r"\[([^\[\]]{1,200})\]")
    raw_brackets = bracket_pattern.findall(visible_text)

    # 法令引用・判例引用の誤検出を除外
    def is_legal_citation(content):
        s = content.strip()
        if re.match(r"^第[〇一二三四五六七八九十百千\d]+条", s):
            return True
        if re.match(r"^(最|大)(判|決|大判)?(昭|平|令|明|大)", s):
            return True
        if re.match(r"^\d{1,4}年", s):
            return True
        return False

    placeholders = [b for b in raw_brackets if not is_legal_citation(b)]

    total = len(instruction_comments) + len(placeholders)
    if total == 0:
        return

    details = []
    for inst in instruction_comments[:5]:
        pos = html.find(inst)
        line_no = (html[:pos].count("\n") + 1) if pos >= 0 else "?"
        snippet = inst.replace("\n", " ")
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        details.append(f"L{line_no}: {snippet}")
    for ph in placeholders[:5]:
        search_str = f"[{ph}]"
        pos = html.find(search_str)
        line_no = (html[:pos].count("\n") + 1) if pos >= 0 else "?"
        snippet = search_str.replace("\n", " ")
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        details.append(f"L{line_no}: {snippet}")

    extra = total - len(details)
    msg = f"未差替 placeholder を {total} 件検出: " + "; ".join(details)
    if extra > 0:
        msg += f"; ... 他 {extra} 件"
    rep.error("S83", msg)


# ============================================================
# S84: mindmap section 構造検査（v9.1.0-mindmap 専用 / version-aware）
# ============================================================

def check_mindmap_structure(soup, rep):
    """S84: mindmap section 構造検査（v9.1.0-mindmap 専用）

    対象判定：
      footer-spec の feature-tag 列に "TX v9.1.0 MINDMAP" を含む
      ファイルのみ厳格適用。それ以外は早期 return（version-aware）。

    検査項目（spec §31 S84 (a)〜(h)）：
      a) <section id="mindmap"> の存在
      b) 内部に <svg viewBox="0 0 1100 900"> 必須
      c) SVG の親に <div class="figure-wrap"> 必須（§17-bis-2 K302-10）
      d) <p class="figure-caption"> 必須（figure-wrap 内）
      e) SVG 内に <ellipse>（中心ノード）1 個以上必須
      f) SVG 内に <rect>（4 体系層含む）≥ 4 個必須
      g) SVG に role="img" + aria-label 属性必須
      h) <script>/<style> タグ禁止（host-injection-safe / AP-41）
    """

    # === version-aware 判定 ===
    footer = soup.find(class_="footer-spec")
    if footer is None:
        return  # footer-spec なし → 検査対象外（他検査で別途検出）

    feature_tags = footer.find_all(class_="feature-tag")
    feature_text = " ".join(tag.get_text(strip=True) for tag in feature_tags)

    if "TX v9.1.0 MINDMAP" not in feature_text:
        return  # 対象外：早期 return（version-aware）

    # === ここから v9.1.0-mindmap ファイルのみ実行 ===

    # (a) <section id="mindmap"> の存在
    mindmap_section = soup.find("section", id="mindmap")
    if mindmap_section is None:
        rep.error("S84", '<section id="mindmap"> が見つかりません')
        return  # これがないと後続検査が無意味なので早期 return

    # (b) 内部に <svg viewBox="0 0 1100 900"> 必須
    svg = mindmap_section.find("svg")
    if svg is None:
        rep.error("S84", "mindmap section 内に <svg> が見つかりません")
        return

    # BS4 html.parser は SVG 属性名を小文字化するため、両方確認
    viewbox = svg.get("viewBox") or svg.get("viewbox") or ""
    if viewbox.strip() != "0 0 1100 900":
        rep.error(
            "S84",
            f"SVG viewBox は '0 0 1100 900' 必須・実値='{viewbox}'",
        )

    # (c) SVG の親に <div class="figure-wrap"> 必須
    svg_parent = svg.parent
    if svg_parent is None or "figure-wrap" not in (svg_parent.get("class") or []):
        rep.error(
            "S84",
            'SVG の親要素に class="figure-wrap" 必須（§17-bis-2 K302-10）',
        )

    # (d) <p class="figure-caption"> 必須（figure-wrap 内）
    if svg_parent is not None:
        caption = svg_parent.find("p", class_="figure-caption")
        if caption is None:
            rep.error(
                "S84",
                'figure-wrap 内に <p class="figure-caption"> 必須',
            )

    # (e) SVG 内に <ellipse>（中心ノード）1 個以上必須
    ellipses = svg.find_all("ellipse")
    if len(ellipses) < 1:
        rep.error(
            "S84",
            f"SVG 内に <ellipse>（中心ノード）必須・実検出数={len(ellipses)}",
        )

    # (f) SVG 内に <rect>（4 体系層含む）≥ 4 個必須
    rects = svg.find_all("rect")
    if len(rects) < 4:
        rep.error(
            "S84",
            f"SVG 内に <rect>（4 体系層）≥ 4 個必須・実検出数={len(rects)}",
        )

    # (g) SVG に role="img" + aria-label 属性必須
    if svg.get("role") != "img":
        rep.error("S84", 'SVG に role="img" 必須（K302 アクセシビリティ）')

    if not svg.get("aria-label"):
        rep.error("S84", "SVG に aria-label 属性必須")

    # (h) <script>/<style> タグ禁止（host-injection-safe / AP-41）
    scripts_in_mindmap = mindmap_section.find_all("script")
    styles_in_mindmap = mindmap_section.find_all("style")
    if scripts_in_mindmap or styles_in_mindmap:
        rep.error(
            "S84",
            f"mindmap section 内に <script>/<style> タグ禁止・"
            f"script={len(scripts_in_mindmap)}個 / style={len(styles_in_mindmap)}個"
            f"（AP-41 host-injection-safe）",
        )


# ============================================================
# S85: ツリー型体系図 section 構造検査（v9.2.0 DEEP-DIVE 専用）
# ============================================================

def check_tree_structure(soup, rep):
    """S85: <section id="mindmap-tree"> 構造検査

    判定条件：feature-tag に "TX v9.2.0 DEEP-DIVE" と "tree-mindmap" を含む場合のみ実行
    """
    if detect_spec_version(soup) != "v9.2.0":
        return
    if not footer_has_tag(soup, "tree-mindmap"):
        return

    # (a) <section id="mindmap-tree"> の存在
    section = soup.find("section", id="mindmap-tree")
    if section is None:
        rep.error("S85", '<section id="mindmap-tree"> が見つかりません')
        return

    # (b) sec-nav "↑参考" / "↓マインドマップ放射" 存在
    nav = section.find("nav", class_="sec-nav")
    if nav is None or "↑参考" not in nav.get_text() or "↓マインドマップ放射" not in nav.get_text():
        rep.error("S85", 'mindmap-tree sec-nav に "↑参考" / "↓マインドマップ放射" 必須')

    # (c) <h2 class="section-title"> 内 sec-icon=🌳 + "体系ツリー"
    title = section.find("h2", class_="section-title")
    if title is None or "体系ツリー" not in title.get_text() or "🌳" not in title.get_text():
        rep.error("S85", '<h2 class="section-title"> に 🌳 + "体系ツリー" 必須')

    # (d) <div class="figure-wrap"> 直下に <svg viewBox="0 0 [1100|1300] [600|700|800]">
    figure_wrap = section.find("div", class_="figure-wrap")
    if figure_wrap is None:
        rep.error("S85", "mindmap-tree section 内に <div class=\"figure-wrap\"> 必須")
        return
    svg = figure_wrap.find("svg")
    if svg is None:
        rep.error("S85", "figure-wrap 内に <svg> が見つかりません")
        return

    viewbox = (svg.get("viewBox") or svg.get("viewbox") or "").strip()
    valid_viewboxes = {"0 0 1100 600", "0 0 1100 700", "0 0 1100 800", "0 0 1300 600", "0 0 1300 700"}
    if viewbox not in valid_viewboxes:
        rep.error(
            "S85",
            f"tree-svg viewBox は 4 パターン (1100×600/700/800・1300×600) 必須・実値='{viewbox}'",
        )

    # (e) SVG 内に role="img" + aria-label 属性
    if svg.get("role") != "img":
        rep.error("S85", 'tree-svg に role="img" 必須')
    if not svg.get("aria-label"):
        rep.error("S85", "tree-svg に aria-label 属性必須")

    # (f) SVG class="tree-svg" 付与
    svg_classes = svg.get("class") or []
    if "tree-svg" not in svg_classes:
        rep.error("S85", 'SVG に class="tree-svg" 必須')

    # (g) <defs><marker id="issueArr">...</marker></defs> 存在
    defs = svg.find("defs")
    if defs is None or defs.find("marker", id="issueArr") is None:
        rep.error("S85", '<defs><marker id="issueArr"> 必須')

    # (h) L0/L1/L2/L3 各層のノードが各 1 個以上（class="l0-fill" 等）
    for level in ("l0-fill", "l1-fill", "l2-fill", "l3-fill"):
        nodes = svg.find_all(class_=level)
        if len(nodes) < 1:
            rep.error("S85", f'SVG 内に class="{level}" のノード必須・実検出数={len(nodes)}')

    # (i) issue-fill（本問の論点枠）1 個存在
    issue_nodes = svg.find_all(class_="issue-fill")
    if len(issue_nodes) < 1:
        rep.error("S85", f'SVG 内に class="issue-fill"（本問の論点枠）1 個必須・実検出数={len(issue_nodes)}')

    # (j) issue-arrow（破線矢印）1 個存在
    arrow_nodes = svg.find_all(class_="issue-arrow")
    if len(arrow_nodes) < 1:
        rep.error("S85", f'SVG 内に class="issue-arrow"（破線矢印）1 個必須・実検出数={len(arrow_nodes)}')

    # (k) <p class="figure-caption"> 存在
    if figure_wrap.find("p", class_="figure-caption") is None:
        rep.error("S85", 'figure-wrap 内に <p class="figure-caption"> 必須')

    # (l) <script>/<style> タグ禁止（host-injection-safe）
    if section.find_all(["script", "style"]):
        rep.error("S85", "mindmap-tree section 内に <script>/<style> タグ禁止（AP-41）")


# ============================================================
# S86: 放射状マインドマップ section 構造検査（v9.2.0 専用・旧 S84 後継）
# ============================================================

def check_radial_structure(soup, rep):
    """S86: <section id="mindmap-radial"> 構造検査

    判定条件：feature-tag に "TX v9.2.0 DEEP-DIVE" と "radial-mindmap" を含む場合のみ実行
    """
    if detect_spec_version(soup) != "v9.2.0":
        return
    if not footer_has_tag(soup, "radial-mindmap"):
        return

    # (a) <section id="mindmap-radial"> の存在
    section = soup.find("section", id="mindmap-radial")
    if section is None:
        rep.error("S86", '<section id="mindmap-radial"> が見つかりません')
        return

    # (b) sec-nav "↑マインドマップツリー" / "↓C-1"
    nav = section.find("nav", class_="sec-nav")
    if nav is None or "↑マインドマップツリー" not in nav.get_text() or "↓C-1" not in nav.get_text():
        rep.error("S86", 'mindmap-radial sec-nav に "↑マインドマップツリー" / "↓C-1" 必須')

    # (c) <h2 class="section-title"> 内 sec-icon=🧭 + "論点マインドマップ"
    title = section.find("h2", class_="section-title")
    if title is None or "論点マインドマップ" not in title.get_text() or "🧭" not in title.get_text():
        rep.error("S86", '<h2 class="section-title"> に 🧭 + "論点マインドマップ" 必須')

    # (d) <div class="figure-wrap"> 直下に <svg viewBox="0 0 1200 1000">
    figure_wrap = section.find("div", class_="figure-wrap")
    if figure_wrap is None:
        rep.error("S86", 'mindmap-radial section 内に <div class="figure-wrap"> 必須')
        return
    svg = figure_wrap.find("svg")
    if svg is None:
        rep.error("S86", "figure-wrap 内に <svg> が見つかりません")
        return

    viewbox = (svg.get("viewBox") or svg.get("viewbox") or "").strip()
    if viewbox != "0 0 1200 1000":
        rep.error("S86", f"radial-svg viewBox は '0 0 1200 1000' 必須・実値='{viewbox}'")

    # (e) SVG 内 role="img" + aria-label 属性
    if svg.get("role") != "img":
        rep.error("S86", 'radial-svg に role="img" 必須')
    if not svg.get("aria-label"):
        rep.error("S86", "radial-svg に aria-label 属性必須")

    # (f) SVG class="radial-svg" 付与
    svg_classes = svg.get("class") or []
    if "radial-svg" not in svg_classes:
        rep.error("S86", 'SVG に class="radial-svg" 必須')

    # (g) <defs><linearGradient id="centerGrad"> 存在
    defs = svg.find("defs")
    if defs is None or (
        defs.find("linearGradient", id="centerGrad") is None
        and defs.find("lineargradient", id="centerGrad") is None
    ):
        rep.error("S86", '<defs><linearGradient id="centerGrad"> 必須')

    # (h) 中心 <ellipse fill="url(#centerGrad)"> が 1 個存在
    center_ellipses = [
        e for e in svg.find_all("ellipse")
        if (e.get("fill") or "").strip() == "url(#centerGrad)"
    ]
    if len(center_ellipses) < 1:
        rep.error("S86", '中心 <ellipse fill="url(#centerGrad)"> 1 個必須')

    # (i) branch-fill（主要枝）が 6-7 個存在
    branch_nodes = svg.find_all(class_="branch-fill")
    if not (6 <= len(branch_nodes) <= 7):
        rep.error("S86", f'class="branch-fill"（主要枝）は 6-7 個必須・実検出数={len(branch_nodes)}')

    # (j) issue-branch-fill（本問の論点枝）が 1 個存在
    issue_branch = svg.find_all(class_="issue-branch-fill")
    if len(issue_branch) < 1:
        rep.error("S86", f'class="issue-branch-fill"（本問の論点枝）1 個必須・実検出数={len(issue_branch)}')

    # (k) sub-statute / sub-case が各 1 個以上
    if len(svg.find_all(class_="sub-statute")) < 1:
        rep.error("S86", 'class="sub-statute" 1 個以上必須')
    if len(svg.find_all(class_="sub-case")) < 1:
        rep.error("S86", 'class="sub-case" 1 個以上必須')

    # (l) line-main / line-issue / line-sub の使い分け
    if len(svg.find_all(class_="line-main")) < 1:
        rep.error("S86", 'class="line-main" 1 個以上必須')
    if len(svg.find_all(class_="line-issue")) < 1:
        rep.error("S86", 'class="line-issue" 1 個以上必須')

    # (m) <p class="figure-caption"> 存在
    if figure_wrap.find("p", class_="figure-caption") is None:
        rep.error("S86", 'figure-wrap 内に <p class="figure-caption"> 必須')

    # (n) <script>/<style> タグ禁止
    if section.find_all(["script", "style"]):
        rep.error("S86", "mindmap-radial section 内に <script>/<style> タグ禁止（AP-41）")


# ============================================================
# S87: 分岐型フローチャート構造検査（v9.2.0 専用 / c-5 内 flow-svg）
# ============================================================

def check_flowchart_structure(soup, rep):
    """S87: <section id="c-5"> 内の SVG 分岐型フローチャート構造検査

    判定条件：feature-tag に "TX v9.2.0 DEEP-DIVE" と "branching-flowchart" を含む場合のみ実行
    """
    if detect_spec_version(soup) != "v9.2.0":
        return
    if not footer_has_tag(soup, "branching-flowchart"):
        return

    section = soup.find("section", id="c-5")
    if section is None:
        rep.error("S87", '<section id="c-5"> が見つかりません')
        return

    svg = section.find("svg")
    if svg is None:
        rep.error("S87", "c-5 section 内に <svg> が見つかりません")
        return

    # (a) SVG class="flow-svg" 付与
    svg_classes = svg.get("class") or []
    if "flow-svg" not in svg_classes:
        rep.error("S87", 'c-5 内 SVG に class="flow-svg" 必須')

    # (b) viewBox が "0 0 900 [600|800|1000]" のいずれか
    viewbox = (svg.get("viewBox") or svg.get("viewbox") or "").strip()
    if viewbox not in {"0 0 900 600", "0 0 900 800", "0 0 900 1000"}:
        rep.error(
            "S87",
            f"flow-svg viewBox は '0 0 900 [600|800|1000]' 必須・実値='{viewbox}'",
        )

    # (c) <defs><marker id="flowArr"> 存在
    defs = svg.find("defs")
    if defs is None or defs.find("marker", id="flowArr") is None:
        rep.error("S87", '<defs><marker id="flowArr"> 必須')

    # (d) flow-start ノードが 1 個存在
    starts = svg.find_all(class_="flow-start")
    if len(starts) != 1:
        rep.error("S87", f'class="flow-start" は 1 個必須・実検出数={len(starts)}')

    # (e) flow-decision の polygon が 1 個以上
    decisions = svg.find_all(class_="flow-decision")
    if len(decisions) < 1:
        rep.error("S87", f'class="flow-decision"（polygon）1 個以上必須・実検出数={len(decisions)}')

    # (f) flow-end-success / flow-end-fail の rect が各 1 個以上
    if len(svg.find_all(class_="flow-end-success")) < 1:
        rep.error("S87", 'class="flow-end-success" 1 個以上必須')
    if len(svg.find_all(class_="flow-end-fail")) < 1:
        rep.error("S87", 'class="flow-end-fail" 1 個以上必須')

    # (g) flow-chip（肢マーカー）が 1 個以上
    chips = svg.find_all(class_="flow-chip")
    if len(chips) < 1:
        rep.error("S87", f'class="flow-chip"（肢マーカー）1 個以上必須・実検出数={len(chips)}')

    # (h) 旧形式（stepbox / stepnum）の混在禁止
    if svg.find_all(class_="stepbox") or svg.find_all(class_="stepnum"):
        rep.error("S87", "旧形式（stepbox / stepnum）の混在禁止（v9.2.0 では flow-svg のみ）")

    # (i) <p class="figure-caption"> 存在
    figure_wrap = svg.parent
    if figure_wrap is None or figure_wrap.find("p", class_="figure-caption") is None:
        rep.error("S87", 'flow-svg の figure-wrap 内に <p class="figure-caption"> 必須')

    # (j) <script> 禁止（host-injection-safe）
    if section.find_all("script"):
        rep.error("S87", "c-5 section 内に <script> タグ禁止（AP-41）")


# ============================================================
# S88: 派生色変数存在検査（v9.2.0 専用・AP-45）
# ============================================================

def check_palette_derivatives(style_text, rep):
    """S88: <style> 内 :root{} ブロックに v9.2.0 派生色 10 個の hex 形式定義検査

    判定条件：呼び出し側で v9.2.0 判定済前提
    """
    # :root ブロックを抽出（複数 :root を許容・S60 連動は別途）
    root_blocks = re.findall(r":root\s*\{([^}]*)\}", style_text)
    if not root_blocks:
        rep.error("S88", ":root{} ブロックが見つかりません（AP-45）")
        return

    all_root_content = "\n".join(root_blocks)

    missing = []
    for var in V92_DERIVATIVE_COLORS:
        # hex 形式（#RGB / #RRGGBB）を許容
        pattern = re.escape(var) + r"\s*:\s*#[0-9a-fA-F]{3,8}"
        if not re.search(pattern, all_root_content):
            missing.append(var)

    if missing:
        rep.error(
            "S88",
            f"派生色変数の hex 形式定義が欠落（AP-45）：{', '.join(missing)}",
        )


# ============================================================
# S88 改訂: v9.3.0 派生色変数検査（HSL 派生妥当性含む・AP-45/AP-47）
# ============================================================

def check_s88_v93(style_text, rep):
    """S88 (v9.3.0): :root{} 内 14 派生色変数の存在 + 絶対派生固定値 + HSL 派生妥当性検査。"""
    m = re.search(r":root\s*\{([^}]*)\}", style_text, re.DOTALL)
    if not m:
        rep.error("S88/AP-45", ":root{} ブロックが見つかりません（v9.3.0）")
        return
    root_body = m.group(1)

    var_values: dict = {}
    for var in DERIVED_COLOR_VARS_V93:
        pattern = re.escape(var) + r"\s*:\s*(#[0-9A-Fa-f]{6})"
        vm = re.search(pattern, root_body)
        if not vm:
            rep.error(
                "S88/AP-45",
                f"派生色変数 {var} が :root 内に定義されていません（v9.3.0）"
            )
        else:
            var_values[var] = vm.group(1).upper()

    # 絶対派生 3 個の固定値検査
    for var, expected in ABSOLUTE_DERIVATIVES_V93.items():
        if var in var_values:
            actual = var_values[var]
            if _v93_hex_distance(actual, expected) > 0:
                rep.error(
                    "S88/AP-47",
                    f"絶対派生 {var} の値 {actual} が期待値 {expected} と一致しません"
                )

    # HSL 派生 8 個の妥当性検査（許容誤差: R/G/B 差分合計 ≤6）
    for derived, (src_var, dh, ds, dl) in HSL_DERIVATIONS_V93.items():
        if derived not in var_values or src_var not in var_values:
            continue
        src_hex = var_values[src_var]
        derived_actual = var_values[derived]
        try:
            h, s, l = _v93_hex_to_hsl(src_hex)
            expected_hex = _v93_hsl_to_hex(h + dh, s + ds, l + dl)
        except ValueError:
            continue
        dist = _v93_hex_distance(derived_actual, expected_hex)
        if dist > 6:
            rep.error(
                "S88/AP-47",
                f"HSL 派生 {derived}={derived_actual} が期待値 {expected_hex} "
                f"（{src_var}={src_hex} から dH={dh}/dS={ds}/dL={dl}）と乖離 (距離={dist})"
            )


# ============================================================
# S92 新規: サブパレット ID 整合性検査（v9.3.0 専用・AP-47）
# ============================================================

def check_s92(html_content, problem_json, rep):
    """S92: :root コメントと footer feature-tag の sub-palette 整合性、
    JSON correct_rate からのカテゴリ判定整合性検査。"""
    root_m = re.search(r":root\s*\{([^}]*)\}", html_content, re.DOTALL)
    if not root_m:
        return  # S88 で別途検出
    root_body = root_m.group(1)

    root_comment_m = re.search(
        r"sub-palette:\s*([^\s/]+(?:\s+[^\s/]+)*)\s*\(([\w\-]+)\)\s*/\s*category:\s*(P[123])",
        root_body
    )
    if not root_comment_m:
        rep.error(
            "S92/AP-47",
            ':root{} 内に "sub-palette: [名前] ([英語コード]) / category: P[123]" コメントが見つかりません'
        )
        return
    root_id = root_comment_m.group(2)
    root_category = root_comment_m.group(3)

    tag_pattern = r'<span class="feature-tag">sub-palette:\s*([^\s<]+(?:\s+[^\s<]+)*)\s*\(([\w\-]+)\)</span>'
    tag_m = re.search(tag_pattern, html_content)
    if not tag_m:
        rep.error(
            "S92/AP-47",
            'footer feature-tag に "sub-palette: [名前] ([英語コード])" が見つかりません'
        )
        return
    tag_id = tag_m.group(2)

    if root_id != tag_id:
        rep.error(
            "S92/AP-47",
            f":root sub-palette ID ({root_id}) と footer tag ID ({tag_id}) が不一致"
        )

    if root_id not in SUBPALETTES_V93_FLAT:
        rep.error(
            "S92/AP-47",
            f'サブパレット ID "{root_id}" が登録カラーパレットに存在しません'
        )
        return

    expected_meta = SUBPALETTES_V93_FLAT[root_id]
    if expected_meta["category"] != root_category:
        rep.error(
            "S92/AP-47",
            f"サブパレット {root_id} の登録 category={expected_meta['category']} と "
            f":root 内 category={root_category} が不一致"
        )

    # JSON correct_rate との整合性（override_reason 未記載時のみ）
    if problem_json is not None:
        override_reason = problem_json.get("palette_override_reason")
        if not override_reason:
            correct_rate_str = problem_json.get("correct_rate", "")
            rate_m = re.search(r"(\d+)", str(correct_rate_str))
            if rate_m:
                rate = int(rate_m.group(1))
                if rate >= 70:
                    expected_cat = "P1"
                elif rate >= 40:
                    expected_cat = "P2"
                else:
                    expected_cat = "P3"
                if expected_cat != root_category:
                    rep.error(
                        "S92/AP-47",
                        f"correct_rate={rate}% から導出されるカテゴリ {expected_cat} と "
                        f"使用サブパレット category={root_category} が不一致。"
                        f"意図的なら JSON に palette_override_reason を記載してください"
                    )


# ============================================================
# S89: §17-ter 学説対立 deep-dive 構造検査（v9.2.0 専用・AP-46）
# ============================================================

def check_theory_deep_dive(target, soup, rep):
    """S89: <section id="c-4"> 内の §17-ter theory-detail-grid 構造検査

    判定条件：feature-tag に "TX v9.2.0 DEEP-DIVE" と "theory-deep-dive" を含み、
              かつ theory-detail-grid が出現する場合のみ実行

    罠 9 検出: JSON 側に theory_deep_dive 定義あり、HTML 側 feature-tag 不在は
    claude -p 不完全出力（Phase 13B step 2 v1 で実観測）→ ERROR で再生成促す
    """
    if detect_spec_version(soup) != "v9.2.0":
        return

    # 罠 9 検出: JSON 側 theory_deep_dive フィールド存在チェック
    json_path = derive_problem_json_path(target)
    json_has_theory = False
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            json_has_theory = "theory_deep_dive" in data
        except (json.JSONDecodeError, OSError):
            pass

    html_has_tag = footer_has_tag(soup, "theory-deep-dive")

    # 偽 PASS 検出: JSON あり・HTML 不在
    if json_has_theory and not html_has_tag:
        rep.error(
            "S89",
            'JSON に "theory_deep_dive" 定義あるが HTML 出力に "theory-deep-dive" feature-tag 不在'
            '（罠 9・claude -p 不完全出力の可能性・要再生成）',
        )
        return

    if not html_has_tag:
        return  # 正常 skip（JSON にも HTML にもない）

    section_c4 = soup.find("section", id="c-4")
    if section_c4 is None:
        return  # c-4 自体が無い問題（学説対立なし）はスキップ

    # 学説対立がある問題（theory-detail-grid が存在）の場合のみ厳格適用
    grid = section_c4.find("div", class_="theory-detail-grid")
    if grid is None:
        return  # 学説対立 deep-dive が出題されない問題はスキップ

    # data-question-type="theory-selection" 時の 200 字規律フラグ
    is_theory_selection = section_c4.get("data-question-type") == "theory-selection"

    # (a) theory-detail-grid 存在（上で確認済）

    # (b) sub-card theory-major が 1 個
    majors = grid.find_all(class_="theory-major")
    if len(majors) != 1:
        rep.error("S89", f'class="theory-major" は 1 個必須・実検出数={len(majors)}（AP-46）')

    # (c) sub-card theory-minor が 1 個
    minors = grid.find_all(class_="theory-minor")
    if len(minors) != 1:
        rep.error("S89", f'class="theory-minor" は 1 個必須・実検出数={len(minors)}（AP-46）')

    # (d) why-adopted dt 存在 + (e) why-not-adopted dt 存在
    for major in majors:
        if major.find("dt", class_="why-adopted") is None:
            rep.error("S89", 'theory-major 内 <dt class="why-adopted"> 必須（AP-46）')
    for minor in minors:
        if minor.find("dt", class_="why-not-adopted") is None:
            rep.error("S89", 'theory-minor 内 <dt class="why-not-adopted"> 必須（AP-46）')

    # (f) statute-interpretation blockquote 存在
    if section_c4.find("blockquote", class_="statute-interpretation") is None:
        rep.error("S89", '<blockquote class="statute-interpretation"> 必須（AP-46）')

    # (g) data-question-type="theory-selection" 時：dd 本文 200 字以上必須
    if is_theory_selection:
        for major in majors:
            adopted_dt = major.find("dt", class_="why-adopted")
            if adopted_dt is not None:
                dd = adopted_dt.find_next_sibling("dd")
                if dd is None or len(dd.get_text(strip=True)) < 200:
                    rep.error(
                        "S89",
                        f"theory-selection: why-adopted の dd 本文 200 字以上必須・実={len(dd.get_text(strip=True)) if dd else 0}（AP-46）",
                    )
        for minor in minors:
            not_adopted_dt = minor.find("dt", class_="why-not-adopted")
            if not_adopted_dt is not None:
                dd = not_adopted_dt.find_next_sibling("dd")
                if dd is None or len(dd.get_text(strip=True)) < 200:
                    rep.error(
                        "S89",
                        f"theory-selection: why-not-adopted の dd 本文 200 字以上必須・実={len(dd.get_text(strip=True)) if dd else 0}（AP-46）",
                    )

    # (h) theory-heading 内 theory-badge 存在
    for sub in majors + minors:
        heading = sub.find(class_="theory-heading")
        if heading is None or heading.find(class_="theory-badge") is None:
            rep.error("S89", "theory-heading 内 theory-badge 必須（AP-46）")

    # (i) <script>/<style> 禁止
    if section_c4.find_all(["script", "style"]):
        rep.error("S89", "c-4 section 内に <script>/<style> タグ禁止（AP-41）")


# ============================================================
# S90: メタ説明違反検査（v9.2.0 専用・AP-43 / §0-quad-2-bis）
# ============================================================

def check_meta_explanation(soup, rep):
    """S90: メタ説明禁止カテゴリ 15 語句の検出

    判定条件：feature-tag に "TX v9.2.0 DEEP-DIVE" と "meta-explanation-blocked" を含む場合のみ実行
    """
    if detect_spec_version(soup) != "v9.2.0":
        return
    if not footer_has_tag(soup, "meta-explanation-blocked"):
        return

    violations = []
    for selector in META_CHECK_SELECTORS:
        # BeautifulSoup の select はクラス selector を順次解釈
        elements = soup.select(selector)
        for elem in elements:
            # 例外 1：data-question-type="theory-selection" 配下は学説名「ア/イ」許容
            parent_c4 = elem.find_parent("section", id="c-4")
            is_theory_selection = (
                parent_c4 is not None
                and parent_c4.get("data-question-type") == "theory-selection"
            )

            # 例外 2/3：fa-summary / answer-instruction はスキップ
            if elem.find_parent(class_="fa-summary") or elem.find_parent(class_="answer-instruction"):
                continue

            # 例外 4：mindmap-tree / mindmap-radial / c-5 の「本問の論点」枠（issue-fill / issue-branch-fill）はスキップ
            if (
                elem.find_parent(class_="issue-fill")
                or elem.find_parent(class_="issue-branch-fill")
            ):
                continue

            text = elem.get_text(" ", strip=True)
            for pat in META_EXPLANATION_PATTERNS:
                m = pat.search(text)
                if m:
                    # 例外 1 適用判定：学説名としての「ア/イ」のみのケースは許容
                    if is_theory_selection and m.group(0).startswith(("肢ア", "肢イ", "肢ウ", "肢エ", "肢オ", "記号ア", "記号イ", "記号ウ", "記号エ", "記号オ")):
                        continue
                    snippet = text[max(0, m.start() - 10):m.end() + 30]
                    violations.append(f"{selector}: 「{m.group(0)}」検出 [...{snippet}...]")

    if violations:
        joined = "\n  ".join(violations[:10])
        more = f"\n  …他 {len(violations) - 10} 件" if len(violations) > 10 else ""
        rep.error("S90", f"メタ説明違反検出（AP-43 / §0-quad-2-bis）：\n  {joined}{more}")


# ============================================================
# S91: 教授解説密度検査（v9.2.0 専用・AP-44 / §0-quad-3 STEP IQ-5 強化版）
# ============================================================

def check_professor_density(soup, rep):
    """S91: 各 prof-heading 配下のテキスト文字数検査

    判定条件：feature-tag に "TX v9.2.0 DEEP-DIVE" と "professor-density-v2" を含む場合のみ実行
    """
    if detect_spec_version(soup) != "v9.2.0":
        return
    if not footer_has_tag(soup, "professor-density-v2"):
        return

    profs = soup.select(".sub-card.professor")
    if not profs:
        return  # 教授カードが無い問題は対象外

    for idx, prof in enumerate(profs, start=1):
        total_chars = 0

        # (a)-(d) 各 prof-heading の文字数規律
        for selector, min_chars in PROF_DENSITY_REQUIREMENTS:
            heading = prof.select_one(selector)
            if heading is None:
                rep.error(
                    "S91",
                    f"professor #{idx}: {selector} が見つかりません（AP-44）",
                )
                continue
            text = heading.get_text(" ", strip=True)
            char_count = len(text)
            total_chars += char_count
            if char_count < min_chars:
                rep.error(
                    "S91",
                    f"professor #{idx}: {selector} は最低 {min_chars} 字必須・実={char_count} 字（AP-44）",
                )

        # (e) prof-image 内 3 要素必須
        prof_image = prof.select_one(".prof-heading.prof-image")
        if prof_image is not None:
            for sub_sel in PROF_IMAGE_SUBELEMENTS:
                if prof_image.select_one(sub_sel) is None:
                    rep.error(
                        "S91",
                        f"professor #{idx}: prof-image 内 {sub_sel} 必須（AP-44）",
                    )

        # (f) prof-application 内 syllogism 3 要素必須
        prof_app = prof.select_one(".prof-heading.prof-application")
        if prof_app is not None:
            syllogism = prof_app.select_one(".syllogism")
            if syllogism is None:
                rep.error(
                    "S91",
                    f"professor #{idx}: prof-application 内 .syllogism 必須（AP-44）",
                )
            else:
                for sub_sel in PROF_SYLLOGISM_SUBELEMENTS:
                    if syllogism.select_one(sub_sel) is None:
                        rep.error(
                            "S91",
                            f"professor #{idx}: syllogism 内 {sub_sel} 必須（AP-44）",
                        )

        # (g) 全 prof-heading 合計 ≥ 1150 字
        if total_chars < 1150:
            rep.error(
                "S91",
                f"professor #{idx}: 全 prof-heading 合計 1150 字以上必須・実={total_chars} 字（AP-44）",
            )


# ============================================================
# main
# ============================================================

def main():
    if len(sys.argv) != 2:
        print("使い方: python scripts/validate-tx.py <HTMLファイルパス>")
        sys.exit(1)

    target = sys.argv[1]
    p = Path(target)
    if not p.exists():
        print(f"ERROR: ファイルが存在しない: {target}")
        sys.exit(1)

    html = p.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    style_text = get_style_text(soup)

    rep = Reporter()

    # S1〜S82: バージョン非依存（全 spec 共通）
    check_structure(target, soup, html, rep)
    check_v8110_layers(html, style_text, rep)
    check_content_independence(soup, rep)
    check_naming(target, soup, rep)
    check_misc(target, soup, html, style_text, rep)
    check_number_integrity(target, soup, rep)

    # S83: placeholder 残存検査（v8.11.x 以降全般）
    check_placeholder_residue(target, soup, html, rep)

    # S84: v9.1.0-mindmap 専用（version-aware は関数内で判定）
    check_mindmap_structure(soup, rep)

    # S85〜S91: v9.2.0 DEEP-DIVE 専用（version-aware は各関数内で判定）
    check_tree_structure(soup, rep)
    check_radial_structure(soup, rep)
    check_flowchart_structure(soup, rep)
    # S88 (派生色) / S92 (サブパレット ID 整合性) は spec_version で経路分岐
    spec_version = detect_spec_version(soup)
    if spec_version == "v9.3.0":
        # v9.3.0 PALETTE-MULTI-VARIANT: S88 改訂 + S92 新規
        check_s88_v93(style_text, rep)
        # S92 は problem.json を必要とする（JSON 未在時は None で内部スキップ）
        json_path = derive_problem_json_path(target)
        problem_json = None
        if json_path.exists():
            try:
                problem_json = json.loads(json_path.read_text(encoding="utf-8"))
            except Exception:
                problem_json = None
        check_s92(html, problem_json, rep)
    elif spec_version == "v9.2.0":
        check_palette_derivatives(style_text, rep)
    check_theory_deep_dive(target, soup, rep)
    check_meta_explanation(soup, rep)
    check_professor_density(soup, rep)

    sys.exit(rep.summary(target))


if __name__ == "__main__":
    main()
