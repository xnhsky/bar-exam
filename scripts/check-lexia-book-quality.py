#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TXLEX / ARIADNE 横断品質ゲート。

単体 validator では拾いにくい「本文の役割崩れ」を、書物全体の観点で検査する。
ERROR が 1 件でもあれば exit 1。対象を絞って実行する場合はファイル/ディレクトリを引数に渡す。

例:
  python scripts/check-lexia-book-quality.py outputs/ux/000_TX/001_刑法/刑TX370_lex.html
  python scripts/check-lexia-book-quality.py outputs/ux/000_TX outputs/001_JX outputs/ux/001_ARIADNE outputs/ux/002_RX outputs/ux/003_TREE
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。pip install beautifulsoup4", file=sys.stderr)
    sys.exit(2)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


BAD_HINT_PHRASES = (
    "問題文のキーワードを拾い、条文・判例の要件",
    "客体・危険・焼損・故意",
    "結論と個別のコアは採点後に確認できます",
)

ANSWER_LABEL_RE = re.compile(r"^(文言|趣旨|射程|切断点|転用)\b")
CONCLUSION_RE = re.compile(
    r"(成立|不成立|当たる|当たらない|肯定|否定|可罰|不可罰|既遂|未遂|"
    r"客体外|含まれない|含む|足りる|足りない|阻却|処罰|偽造|行使|"
    r"非ず|ではない|なし|あり|○|×)"
)
REASON_RE = re.compile(
    r"(から|ため|ので|要件|条|判例|規範|結論|成立|不成立|故意|違法|責任|因果|"
    r"客体|射程|区別|限ら|目的|危険|名義|文書|錯誤|正当防衛|緊急避難|"
    r"阻却|否定|肯定|対象外|無効|有効|減点|条文|主体|過失|未遂|既遂|"
    r"法益|補充性|相当性|公共|評価|検討対象|実益|配点|自殺|承諾|共犯|"
    r"急迫|不正|侵害|継続|終了|加害|意思|可能性|時間的|場所的|接着|"
    r"総合|判断|失点|罪名|行為|検討|漏れ|起動|詐欺|傷害|殺人)"
    r"|正犯|道具|利用|定義|形態"
)

PLACEHOLDER_RE = re.compile(r"(TODO|未置換|\{\{[^}]+\}\}|\bPLACEHOLDER\b)")
MOJIBAKE_RE = re.compile(r"(?:ã|ä¸|å|è|é|æ|ç|ï¼|ï½)")


@dataclass
class Issue:
    file: Path
    code: str
    message: str


def text_of(node) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip() if node else ""


def discover(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and (
            path.name.endswith("_lex.html")
            or path.name.endswith("_ARIADNE.html")
            or path.name.endswith("_TREE.html")
            or re.search(r"JX\d{3}\.html$", path.name)
            or re.search(r"RX\d{3}_\d+\.html$", path.name)
        ):
            files.append(path)
        elif path.is_dir():
            files.extend(path.rglob("*_lex.html"))
            files.extend(path.rglob("*_ARIADNE.html"))
            files.extend(path.rglob("*_TREE.html"))
            files.extend([p for p in path.rglob("*JX*.html") if re.search(r"JX\d{3}\.html$", p.name)])
            files.extend([p for p in path.rglob("*RX*.html") if re.search(r"RX\d{3}_\d+\.html$", p.name)])
    return sorted(set(files))


def check_tx(path: Path, soup: BeautifulSoup, html: str) -> list[Issue]:
    issues: list[Issue] = []
    if ".tx-inline-card" not in html:
        return issues

    for phrase in BAD_HINT_PHRASES:
        if phrase in html:
            issues.append(Issue(path, "TX-HINT", f"汎用・分野ズレの解法ナビヒントが残存: {phrase}"))

    for i, card in enumerate(soup.select(".tx-inline-card"), 1):
        explain = card.select_one(".tx-inline-explain")
        if not explain:
            continue

        answer = text_of(explain.select_one(".tx-answer-box .tx-answer-body"))
        if answer:
            if ANSWER_LABEL_RE.search(answer):
                issues.append(Issue(path, "TX-ANSWER", f"カード{i}: ANSWERが分析ラベル始まり"))
            if not CONCLUSION_RE.search(answer):
                issues.append(Issue(path, "TX-ANSWER", f"カード{i}: ANSWERに成否・該当性の結論語が不足"))
        elif explain.select_one(".tx-answer-box"):
            issues.append(Issue(path, "TX-ANSWER", f"カード{i}: ANSWER本文が空"))

        mini = explain.select_one(".tx-mini-law")
        if explain.select_one(".tx-answer-box") and not mini:
            issues.append(Issue(path, "TX-LAW", f"カード{i}: ANSWER直後の条文/判例ボックスがない"))
        if mini:
            mini_text = text_of(mini)
            if "BASIS" in mini_text:
                issues.append(Issue(path, "TX-LAW", f"カード{i}: 条文/判例ボックスにBASIS要約が混入"))
            for chip in mini.select(".tx-mini-law-code, .tx-mini-law-article"):
                chip_text = text_of(chip)
                if chip_text in {"根拠", "条文・判例"}:
                    issues.append(Issue(path, "TX-LAW", f"カード{i}: 汎用チップ `{chip_text}` が残存"))
            if mini.select_one(".tx-mini-law-para") and not mini.select_one(".tx-mini-law-body"):
                issues.append(Issue(path, "TX-LAW", f"カード{i}: 条文/判例本文に tx-mini-law-body がない"))

        flow_labels = [text_of(x) for x in explain.select(".tx-article-flow .tx-flow-label")]
        if flow_labels:
            required = ["文言", "趣旨", "射程", "切断点", "転用"]
            if flow_labels[:5] != required:
                issues.append(Issue(path, "TX-FLOW", f"カード{i}: 5点フローの役割順が崩れている"))
            for label, body in zip(flow_labels, explain.select(".tx-article-flow .tx-flow-body")):
                if len(text_of(body)) < 8:
                    issues.append(Issue(path, "TX-FLOW", f"カード{i}: `{label}` の本文が短すぎる"))

        hook = text_of(explain.select_one(".tx-onepoint .tx-op-body"))
        if hook:
            if re.search(r"(成立するか|当たるか|どれか|正しいか|誤りか)\s*$", hook):
                issues.append(Issue(path, "TX-HOOK", f"カード{i}: 記憶フックが問題文の焼き直し"))
            if len(hook) < 10:
                issues.append(Issue(path, "TX-HOOK", f"カード{i}: 記憶フックが短すぎる"))
            if len(hook) > 55:
                issues.append(Issue(path, "TX-HOOK", f"カード{i}: 記憶フックが長すぎる。論点のコア・テーゼを一言で残す"))
            if "／" in hook and len(hook) > 40:
                issues.append(Issue(path, "TX-HOOK", f"カード{i}: 記憶フックが説明の連結になっている"))
            if "→" in hook and "成立しない" in hook and re.search(r"(成立する|成立し得る|当たる|偽造となる)", answer):
                issues.append(Issue(path, "TX-HOOK", f"カード{i}: 記憶フックがANSWERと逆結論に読める"))
            if "→" in hook and "成立する" in hook and re.search(r"(成立しない|客体外|当たらない|含まれない)", answer):
                issues.append(Issue(path, "TX-HOOK", f"カード{i}: 記憶フックがANSWERと逆結論に読める"))

    return issues


def check_encoding(path: Path, html: str) -> list[Issue]:
    if MOJIBAKE_RE.search(html):
        return [Issue(path, "ENCODING", "文字化けらしき本文が残存")]
    return []


def check_ariadne(path: Path, soup: BeautifulSoup, html: str) -> list[Issue]:
    issues: list[Issue] = []
    if "_ARIADNE.html" not in path.name:
        return issues

    for phrase in ("問題文のキーワード", "まず考えよう", "確認しましょう。"):
        if phrase in html:
            issues.append(Issue(path, "AR-GENERIC", f"汎用誘導文が残存: {phrase}"))

    for i, step in enumerate(soup.select(".step"), 1):
        for j, do in enumerate(step.select(".do"), 1):
            dt = text_of(do)
            if len(dt) < 18:
                issues.append(Issue(path, "AR-STEP", f"STEP{i} .do {j}: 切断軸が短すぎる"))
            if re.fullmatch(r".*(確認する|考える|整理する)[。.]?", dt) and not REASON_RE.search(dt):
                issues.append(Issue(path, "AR-STEP", f"STEP{i} .do {j}: 汎用作業指示のみ"))

    for i, quiz in enumerate(soup.select(".self-check-quiz"), 1):
        q = text_of(quiz.select_one(".quiz-question"))
        a = text_of(quiz.select_one(".quiz-answer"))
        if re.search(r"正解はどれ|本問の正解|正解の組", q):
            issues.append(Issue(path, "AR-QUIZ", f"ドリル{i}: 正解再問型"))
        if len(a) < 18:
            issues.append(Issue(path, "AR-QUIZ", f"ドリル{i}: 解説が短すぎる"))
        elif not REASON_RE.search(a):
            issues.append(Issue(path, "AR-QUIZ", f"ドリル{i}: 理由・要件・結論の手掛かりが不足"))

    bone = soup.select_one(".bone.matrix-bone")
    if bone:
        bone_html = str(bone)
        for marker, label in [
            ('class="iss"', "論点"),
            ('class="krule"', "規範"),
            ('class="kfact"', "あてはめキー事実"),
            ("<u>", "結論"),
        ]:
            if marker not in bone_html:
                issues.append(Issue(path, "AR-BONE", f"答案構成骨子に{label}マーカーが不足"))

    model = soup.select_one(".model-answer")
    if model:
        if not model.select(".r-issue, .r-norm, .r-apply, .r-concl"):
            issues.append(Issue(path, "AR-MODEL", "模範答案に問規当結の役割クラスがない"))
        apply_blocks = model.select(".r-apply")
        if apply_blocks and all(not block.select_one(".fact, .eval") for block in apply_blocks):
            issues.append(Issue(path, "AR-MODEL", "あてはめ段落に fact/eval マーカーがない"))

    return issues


def check_jx(path: Path, soup: BeautifulSoup, html: str) -> list[Issue]:
    issues: list[Issue] = []
    if not re.search(r"JX\d{3}\.html$", path.name) or "_ARIADNE" in path.name or "_TREE" in path.name:
        return issues

    if PLACEHOLDER_RE.search(html):
        issues.append(Issue(path, "JX-PLACEHOLDER", "TODO/PLACEHOLDER/未置換スロットが残存"))
    issue_has_statute = re.search(r"(検討条文|適用条文|条\)|条）|条前段|条\d*項)", html)
    if "論点の自動抽出" not in html or not issue_has_statute:
        issues.append(Issue(path, "JX-ISSUE", "論点抽出に検討条文・論点候補が不足"))
    if "model-answer" not in html and "模範答案" not in html:
        issues.append(Issue(path, "JX-MODEL", "模範答案が確認できない"))
    else:
        model_text = text_of(soup.select_one(".model-answer")) or text_of(soup.find(id="answer-full"))
        if len(model_text) < 400:
            issues.append(Issue(path, "JX-MODEL", "模範答案本文が短すぎる"))
        if model_text and not re.search(r"罪|条|成立|不成立|阻却|故意|過失|因果|違法|責任", model_text):
            issues.append(Issue(path, "JX-MODEL", "模範答案に法律判断語が不足"))
    grading_text = text_of(soup.select_one(".grading")) or text_of(soup.find(id="grading-comment"))
    if len(grading_text) < 120:
        issues.append(Issue(path, "JX-GRADING", "採点講評が短すぎる、または欠落"))
    if "judgment-text" not in html:
        issues.append(Issue(path, "JX-CASE", "判旨核心 .judgment-text がない"))
    if "答案での使い方" not in html and "本問での意義" not in html:
        issues.append(Issue(path, "JX-USE", "条文・判例・論証の『答案での使い方』がない"))
    if html.count("rank-A") + html.count("rank-B") < 4:
        issues.append(Issue(path, "JX-RANK", "重要度ランクが不足し、優先順位が見えない"))
    return issues


def check_rx(path: Path, soup: BeautifulSoup, html: str) -> list[Issue]:
    issues: list[Issue] = []
    if not re.search(r"RX\d{3}_\d+\.html$", path.name):
        return issues

    if PLACEHOLDER_RE.search(html):
        issues.append(Issue(path, "RX-PLACEHOLDER", "TODO/PLACEHOLDER/未置換スロットが残存"))
    title = text_of(soup.find("title"))
    if not title or title.lower() in {"document", "untitled", "card"}:
        issues.append(Issue(path, "RX-TITLE", "タイトルが空またはプレースホルダ"))
    if "規範" not in html or not soup.select_one(".norm-box"):
        issues.append(Issue(path, "RX-NORM", "暗記対象の規範ボックスがない"))
    else:
        norm_text = text_of(soup.select_one(".norm-box"))
        if len(norm_text) < 80:
            issues.append(Issue(path, "RX-NORM", "規範本文が短すぎる"))
    if "理由づけ" not in html:
        issues.append(Issue(path, "RX-REASON", "理由づけセクションがない"))
    if (
        "答案での使い方" not in html
        and "答案上の使い方" not in html
        and "あてはめの型" not in html
        and "あてはめタグ" not in html
        and "答案フレーズ" not in html
    ):
        issues.append(Issue(path, "RX-USE", "答案での使い方がない"))
    quizzes = soup.select(".self-check-quiz")
    if len(quizzes) < 2:
        issues.append(Issue(path, "RX-QUIZ", "規範チェックが2問未満"))
    for i, quiz in enumerate(quizzes, 1):
        exp = quiz.get("data-explanation", "") or text_of(quiz.select_one(".quiz-answer"))
        if len(exp) < 24:
            issues.append(Issue(path, "RX-QUIZ", f"ドリル{i}: 解説が短すぎる"))
        elif not REASON_RE.search(exp):
            issues.append(Issue(path, "RX-QUIZ", f"ドリル{i}: 理由・要件・結論の手掛かりが不足"))
    return issues


def check_tree(path: Path, soup: BeautifulSoup, html: str) -> list[Issue]:
    issues: list[Issue] = []
    if not path.name.endswith("_TREE.html"):
        return issues

    if PLACEHOLDER_RE.search(html):
        issues.append(Issue(path, "TREE-PLACEHOLDER", "TODO/PLACEHOLDER/未置換スロットが残存"))
    branches = [text_of(x) for x in soup.select(".mm-name")]
    leaves = soup.select(".mm-leaf")
    questions = soup.select(".mm-q")
    if len(branches) < 10:
        issues.append(Issue(path, "TREE-BRANCH", f"分枝が少なすぎる: {len(branches)}"))
    if len(leaves) < 30:
        issues.append(Issue(path, "TREE-LEAF", f"葉が少なすぎる: {len(leaves)}"))
    if len(questions) < 8:
        issues.append(Issue(path, "TREE-RECALL", f"能動想起Qが少なすぎる: {len(questions)}"))
    required_roles = ["処理手順", "論証文言", "あてはめ事実", "失点パターン", "参照判例"]
    joined = " / ".join(branches)
    for role in required_roles:
        if role not in joined:
            issues.append(Issue(path, "TREE-ROLE", f"必須分枝 `{role}` がない"))
    for i, q in enumerate(questions, 1):
        answer = text_of(q.select_one(".mm-q-answer"))
        if len(answer) < 12:
            issues.append(Issue(path, "TREE-RECALL", f"Q{i}: 解答が短すぎる"))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="TXLEX / ARIADNE 横断品質ゲート")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[
            Path("outputs/ux/000_TX"),
            Path("outputs/001_JX"),
            Path("outputs/ux/001_ARIADNE"),
            Path("outputs/ux/002_RX"),
            Path("outputs/ux/003_TREE"),
        ],
    )
    parser.add_argument("--max-issues", type=int, default=200, help="表示する最大件数")
    args = parser.parse_args()

    files = discover(args.paths)
    issues: list[Issue] = []
    for path in files:
        html = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        issues.extend(check_encoding(path, html))
        issues.extend(check_tx(path, soup, html))
        issues.extend(check_jx(path, soup, html))
        issues.extend(check_ariadne(path, soup, html))
        issues.extend(check_rx(path, soup, html))
        issues.extend(check_tree(path, soup, html))

    for issue in issues[: args.max_issues]:
        print(f"[ERROR] {issue.code}: {issue.file}: {issue.message}")
    if len(issues) > args.max_issues:
        print(f"... and {len(issues) - args.max_issues} more")

    print(f"\n=== LEXIA BOOK QUALITY: files {len(files)} / ERROR {len(issues)} ===")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
