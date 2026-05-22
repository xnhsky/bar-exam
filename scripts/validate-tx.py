#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TX v8.11.7 自己検証スクリプト

検証範囲: S1〜S84（仕様書 §31 準拠・主要なものを実装）
  S82: PDF 番号抽出整合（ファイル名 NNN と HTML 内 ID 数字部分の照合）
  S83: v9.0.0-genkei placeholder 残存検査（[...] / <!-- 指示: ... --> 検出）
  S84: mindmap section 構造検査（v9.1.0-mindmap 専用）
    footer-spec の feature-tag に "TX v9.1.0 MINDMAP" を含むファイルのみ
    厳格適用（version-aware）。8 検査項目 (a)〜(h) を順次確認。

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
        print(f"\nTX v8.11.7 検証結果: {target}")
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
    """S78〜S69: v8.11.7 コンテンツ独立性"""

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
                f"レガシー命名形式: {filename}（v8.11.7 形式 {{日本語接頭辞}}TX{{3桁}}.html に更新必要）",
            )
        else:
            rep.error(
                "S80",
                f"ファイル名が v8.11.7 形式に非該当: {filename}",
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

    # v8.11.7 必須 feature-tag
    # 注：canonical/KTX301.html は v8.11.0 ベースの構造参考なので
    # v8.11.7 専用タグの検査対象外とする（編集を誘発しないため）
    if not is_canonical_reference:
        required_tags = ["TX v8.11.7", "ktx301-canon", "jp-prefix-naming", "content-independence"]
        footer_el = soup.find(class_="footer-spec")
        if footer_el:
            footer_text = footer_el.get_text()
            for tag in required_tags:
                if tag not in footer_text:
                    rep.warn("S51", f"footer-spec に feature-tag '{tag}' が含まれない")
        else:
            rep.error("S51", "footer-spec が存在しない")

    # AP-24: P2/P3 override が単一 :root{} ブロックのみであること
    # （複雑な解析が必要なので簡易チェック）
    root_blocks = re.findall(r":root\s*\{", style_text)
    if len(root_blocks) > 2:
        rep.warn(
            "S60/AP-24",
            f":root{{}} ブロックが {len(root_blocks)} 個存在（P2/P3 override の場合は 2 個まで）",
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

    check_structure(target, soup, html, rep)
    check_v8110_layers(html, style_text, rep)
    check_content_independence(soup, rep)
    check_naming(target, soup, rep)
    check_misc(target, soup, html, style_text, rep)
    check_number_integrity(target, soup, rep)
    check_placeholder_residue(target, soup, html, rep)
    check_mindmap_structure(soup, rep)

    sys.exit(rep.summary(target))


if __name__ == "__main__":
    main()
