#!/usr/bin/env python3
"""PERIPATOS（ペリパトス）― ARIADNE 解法ナビ HTML から、移動中・ながら作業中に音声（ChatGPT 音声モード等）で
論文事例問題を回す台本 MD を書き出す。

名前はアリストテレスが歩きながら弟子と問答して教えた学園（逍遥学派）から。先生役の AI が問答をリードし、
学習者は画面も手元も見ずに、声で答えるだけ、という使い方をそのまま表す。

構成（2026-09-17 ユーザーと確定・以後固定）：
  1. 答案構成 … 問題文 → 事実の要点 → 入口の問い（事案の整理・見当づけ・論点）→ 組み立ての順序
                 （順番・項目ごとの論点名・順番の理由）→ 骨子を第1から、論点名を言ってから規範・使う事実、
                 項目の最後に結論（段階ヒント・項目ごとの復唱・最後に通しで口頭構成）
  2. 規範クイズ … 規範・定義を口で再生（＋ひっかけ）。全問を最後まで・［規範クイズ 2/6］で何問目かを明示
  3. ○×クイズ  … 周辺知識と誤り命題を再認で拾う。同じく全問・番号つき・パート末に終わりの目印
  4. 間違えたところの復習 … 取りこぼしを再出題し、今日の取りこぼしを論点名で読み上げて締める
順番の理由：クイズの解説は「本問では〜」と結論を含むので、先にやると答案構成が思い出すだけになる／
一番価値が高く集中力の要る答案構成を頭が新鮮な冒頭に置く（途中で降りても主役は終わっている）／
生成 → 再生 → 再認の順が記憶に残る／問題文を聞いた直後に組み立てられる。

- 決定論的な抜き出しだけを行う（本文の書き換え・要約はしない）。ARIADNE が単一情報源。
- 入れないもの：答案の書き方の一般論・論じる順番の一般論・配点や分量（「〜のコツ」等のボックス、
  bc-wrap の作法ドリル、それを問う○×）／採点チェック／模範答案／深掘り層。ORDER ステップは
  「この問題の順番の理由」（p.do の一文）だけを組み立ての順序に使う（2026-09-19 ユーザー指示）。

JX の副産物（RX/TREE/ARIADNE に続く4つ目・2026-09-17 配線）。ARIADNE から決定論で作るので LLM 不要。
jx-batch-runner（②-peripatos／②-verify）・rx-arb-backfill・rx-arb-autofill（毎スイープ同期）・jx-finalize・
jx-deploy（Drive の ux/005_PERIPATOS へ配置）・/new-jx Phase 9・/new-ariadne から呼ばれる。
書き込みは中身が変わったときだけ（冪等）なので、何度流しても差分は出ない。

使い方:
  python -X utf8 scripts/peripatos-md.py outputs/ux/001_ARIADNE/001_刑法/刑JX020_ARIADNE.html  # 1問
  python -X utf8 scripts/peripatos-md.py --subject 刑        # 科目ごと（刑/刑訴/民/商/民訴/行政/憲 か 00N_科目）
  python -X utf8 scripts/peripatos-md.py --all               # 全 ARIADNE と同期
  python -X utf8 scripts/peripatos-md.py --all --check       # 書き込まず、未生成・古いシートがあれば exit 1
  出力先の既定は outputs/ux/005_PERIPATOS/{00N_科目}/{ID}_PERIPATOS.md（＋PERIPATOS_プロジェクト指示.md）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parent.parent
ARIADNE_DIR = ROOT / "outputs" / "ux" / "001_ARIADNE"
DEFAULT_OUT = ROOT / "outputs" / "ux" / "005_PERIPATOS"
SUBJECT_DIRS = {"刑": "001_刑法", "刑訴": "002_刑事訴訟法", "民": "003_民法", "商": "004_商法",
                "民訴": "005_民事訴訟法", "行政": "006_行政法", "憲": "007_憲法"}
PROJECT_FILE = "PERIPATOS_プロジェクト指示.md"

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿️‍✓§]")
MARKS = {"○": "○（正しい）", "×": "×（誤り）"}

# 書き方・順番・配分の一般論＝入れないボックス見出し
METHOD_BADGE_RE = re.compile(r"コツ|棚卸しの型|配分|配点|分量|順番|順序|並べる|本丸|割り方|減点")
# 一行要約から落とす「書く順」の文
ORDER_SENTENCE_RE = re.compile(r"書く順[^。]*(?:。|$)")
# 論じる順番・分量・答案での扱いを問う出題。「〜罪を疑うのが筋」（罪名の見分け＝中身）や「答案の一文で規範を」は残す
METHOD_QUESTION_RE = re.compile(
    r"答案(?!の(?:一文|規範))|先に(?:論|確定|検討|固め)|から(?:先に)?論じ|後に(?:論じ|回す)|論じる(?:順|対象|際、最初|前に)"
    r"|論じるのが(?:筋|セオリー|よい)|論じると|論じてよい|論じておくべき|論じる必要がある|論じるべき|論じるには、まず"
    r"|順に検討|順序|確定してから|確定し、(?:次に|その後に)|検討した後に論じ|論述|配点|分量|配分|厚く|書き直|書けば足り|書くべき"
    r"|長く書く|セオリー|鉄則|論理的に明快|登場順|検討を飛ばし|列挙してから|説得力|摘示|並べられるか|入口処理"
    r"|アピール|高評価|減点|検討対象|丁寧|時系列で切り出"
)
# 解説に混じる短い書き方の一言（この長さ以下の文だけ落とす＝法的な理由を巻き込まない）
METHOD_SENTENCE_RE = re.compile(r"厚く|一段落で|深入り|一文で通|一言で|筆を(?:集|残|割|止)|配点|答案|評価語|減点|鉄則|高評価|アピール")
METHOD_SENTENCE_MAX = 32
# 骨子に付いた書き方の括弧書き
METHOD_PAREN_RE = re.compile(r"（[^（）]*(?:一段落|深入り|省略可|厚く|一言で)[^（）]*）")
# 骨子パズルのダミー選択肢の種別
DECOY_KIND = {"iss": "論点", "rule": "規範", "fact": "事実", "u": "結論"}


# 進行役への指示（シート §0 とプロジェクト指示で共有する単一情報源）
RULES: list[str] = [
    "あなたは司法試験論文式の事例問題を音声で回すセッション「PERIPATOS」の進行役です。私は移動中・作業中で、画面も手元も見られず、メモも取れません。"
    "セッションはすべてあなたが仕切り、私は声で答えるだけにします。正解の根拠はシートの内容だけです。",
    "",
    "### 始め方（待たずに始める）",
    "",
    "- シートは台本であり、参考資料ではない。シートの「0. 進行役への指示」と「1. 進行表」に、ユーザーの指示と同じように従う。",
    "- 私の最初の一言が何であっても（「始めて」「スタート」「よろしく」「刑法42」だけでも）、開始の合図として扱う。"
    "挨拶の質問、ファイルの要約、「何をしましょうか」「準備はいいですか」は言わず、すぐ進行表の1から始める。",
    "- 使うシートは、私が番号を言えばそのシート（「刑法42」「刑JX42」＝刑JX042）、言わなければこの会話で最後に添付されたシート。"
    "どちらも無いときだけ「どの問題にしますか？」と一度聞く。",
    "- 私が「前回の続き」と言ったら、同じプロジェクトの直近の会話から私が言えなかった論点を探し、その規範を1〜2問聞いてから進行表の1に入る。"
    "見つからなければ「前回言えなかった論点を教えてください」と一度だけ聞く。",
    "",
    "### 仕切り方",
    "",
    "- 次に何をするかは毎回あなたが決めて進める。「次に進みますか」「どれにしますか」とは聞かない。",
    "- 各パートの頭でパート名と問題数を言う。クイズは1問ごとに「規範クイズ、6問中2問目」のように何問目かを言ってから読む（シートの［規範クイズ 2/6］の表示がその番号）。",
    "- 規範クイズと○×クイズは、シートにある問題を1問目から最後の1問まで全部出す。途中で打ち切らない・間引かない・まとめて説明して済ませない・時間を理由に省かない。止めるのは私が「終わり」と言ったときだけ。",
    "- パートの最後の問題が終わったら「規範クイズ、全6問クリア！」のように言い切ってから次のパートへ進む。まだ残りがあるのに次へ行かない。",
    "- 1回に聞くのは1つだけ。判定のあと、間を置かずに次の問いへ進む。",
    "- 答えは黙って待つ。「考え中」「待って」と言われたら、私が次に話すまで黙る。",
    "- 聞き取れなかったときは一度だけ「もう一度お願いします」と言い、それでも分からなければ「わからない」と同じ扱いにする。",
    "- 正解数を数えておく。間違えた・わからなかった・ヒントで答えた問いは覚えておき、最後の復習でもう一度出す。",
    "",
    "### 答案構成のサポート（いちばん大事。画面を見られない前提で徹底的に支える）",
    "",
    "- 私はメモを取れないので、組み立て途中の骨子はあなたが覚えておく。「今どこ？」と言われたら、いまの項目と論点名、ここまでに言えた骨子、次に何を聞くかを短く伝える。",
    "- 問題文を読み上げたら、続けて「事実の要点」を読む。シートに無ければ、問題文から評価を入れずに3〜5行の要点を作って読む。"
    "「事実」と言われたら、問題文全部ではなく事実の要点だけを読み直す。",
    "- 入口の問いが終わったら、【組み立ての順序】を読み上げる。まず順番（第1 → 第2 → …）、次に項目ごとの論点名、最後にこの順番の理由を、結論に触れずに一言で言う。「順番」と言われたらいつでも読み直す。",
    "- 骨子は「第1」から順に、見出しを言ってから論点ごとに進める。論点に入るたびに「論点1つ目、『反抗を抑圧するに足りる程度か』」のように論点名を必ず言い、"
    "「規範は？」→「あてはめで使う事実は？」を1つずつ聞く。その項目の論点が終わったら「第1の結論は？」と聞く。論点の無い項目は結論だけ聞く。",
    "- 詰まったら、すぐに答えを言わず、段階ヒントを1段ずつ出す。",
    "  1. 事実を指す：「問題文の『〜』に注目すると？」（ヒントの【拾う事実】【効く事実】を使う）",
    "  2. 範囲を絞る：関係する条文の文言や、どの要件の話かを示す（答えそのものは言わない）",
    "  3. 2択にする：正解と【まぎらわしい選択肢】を並べて「AとBなら、どっち？」と聞く",
    "  4. 答えを言い、「では言ってみて」と一度だけ復唱してもらう",
    "- 「ヒント」と言われたら次の段へ進み、「答え」と言われたら4へ飛ぶ。「わからない」は1段目からヒントを出す。",
    "- 私が言えた部分は必ず拾って認め、足りない所だけを足す。言い回しが違っても、中身が合っていれば正解にする。",
    "- 骨子の規範は短く書いてあるので、判定と答えには、規範クイズの模範解答やヒントの【規範の要点】にある完全な規範も使う（ただし答案構成の途中で規範クイズの問題文は読まない）。",
    "- 各項目（第1、第2…）の終わりに、その項目の骨子を短く読み上げてから「第1を一息で言ってみて」と復唱してもらう。",
    "- 全項目が終わったら、見出しだけを順に言いながら全体を通しで口頭構成してもらい、最後に「流れのまとめ」を読んで答え合わせする。",
    "",
    "### 雰囲気（楽しく、テンポよく）",
    "",
    "- クイズ番組の司会のように、明るくテンポよく楽しく進める。ただし盛り上げは一言で済ませ、すぐ次の問いへ行く（雑談で進行を止めない）。",
    "- 正解したら「正解！」「いいですね」「さすが」「完璧です」など、短いひとことで反応する。同じ言葉を続けて使わない。",
    "- 連続で正解したら「3問連続！」のように数えて盛り上げる。答案構成で自力で言えたら特に大きくほめる。",
    "- 間違い・「わからない」のときは責めず、「惜しい！」「ここ、よく引っかかるところです」のように軽く受ける。",
    "- パートの切り替えでは「答案構成クリア！次は規範クイズ、4問いきます」のように区切りを作る。",
    "- 冗談や脱線はたまに一言だけ。法律の中身は茶化さず、説明は正確さを優先する。",
    "",
    "### 判定と話し方",
    "",
    "- 要点で判定する（言い回しの一致は求めない）。足りなければ、言えた所を認めてから抜けたキーワードを言う。間違いなら正解を1〜2文で言う。",
    "- 複数挙げる問い（論点を3つ等）は、言えた数と抜けたものを言う。",
    "- 規範クイズでは、わからなければ答えを言って次へ進む（段階ヒントは答案構成だけ）。",
    "- ○×は文をそのまま読み上げて「マルかバツか」を聞く。判定のあと理由を2文以内で言う。",
    "- 私は画面を見ないので、「Q12」のような番号や「シートの上の方」といった言い方はしない。問題の中身で話す。",
    "- 記号や略記は読み上げず、ふつうの言葉にする（「199条・203条」は「ひゃくきゅうじゅうきゅう条と、にひゃくさん条」、「→」は「だから」）。",
    "- 答案の書き方、論じる順番、配点や分量の話はしない。理由の中に書き方の話が混じっていたら、そこは省いて法的な理由だけ言う。",
    "- シートに無い知識を足すときは必ず「シート外の補足ですが」と前置きする。条文番号・判例名・年月日はシートに書かれたものしか言わない。",
    "",
    "### 私が言うかもしれない合図（言わなければ、あなたの進行どおりに進める）",
    "",
    "- 「考え中」「待って」＝私が次に話すまで黙って待つ／「再開」＝止めた所から続ける",
    "- 「ヒント」＝次の段のヒント／「答え」＝答えを言う／「今どこ？」＝ここまでの骨子と次の問い",
    "- 「事実」＝事実の要点を読み直す／「問題文」＝問題文を全部読み直す／「順番」＝組み立ての順序を読み直す",
    "- 「もう一回」＝今の問いを同じ文言で読み直す／「飛ばして」＝答えを言わずに次へ",
    "- 「ゆっくり」「速く」＝読む速さを変える／「終わり」＝その場で復習に移って締める",
    "",
]

# ChatGPT プロジェクトの「指示」欄に貼る共通文（上限 8,000 字）
PROJECT_FLOW: list[str] = [
    "### 進行（各シートの「1. 進行表」の順）",
    "",
    "1. 答案構成：問題文と事実の要点を読み、入口の問い（事案の整理・見当づけ・論点）のあと、組み立ての順序（順番・論点名・理由）を読み上げる。"
    "骨子を第1から、論点名を言ってから「規範は？」「あてはめで使う事実は？」、項目の最後に「結論は？」と1つずつ組み立てる。詰まったら段階ヒント。各項目の終わりに復唱、最後に通しで口頭構成して流れのまとめで答え合わせ",
    "2. 規範クイズ：全問を1問目から最後まで。何問目かを言ってから出し、キーワードの抜けを判定する",
    "3. ○×クイズ：全問を1問目から最後まで。何問目かを言ってから出す",
    "4. 間違えたところの復習：取りこぼしをもう一度出し、正解数・よくできた所を伝え、「今日の取りこぼし」を論点名で読み上げて明るく締める",
]


def clean(s: str) -> str:
    s = EMOJI_RE.sub("", s)
    s = re.sub(r"[ \t　]*\n[ \t　]*", "\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def text(el: Tag | None) -> str:
    if el is None:
        return ""
    return clean(re.sub(r"\s*\n\s*", "", el.get_text()))


def lines_text(el: Tag) -> list[str]:
    return [clean(x) for x in el.get_text().split("\n") if clean(x)]


def law_refs(s: str, header: bool = False) -> str:
    """骨子の条文略記を読み上げ向けに開く：「199/203」→「199条・203条」、「62Ⅰ」→「62条1項」、「220Ⅰ②」→「220条1項2号」。"""
    roman = {"Ⅰ": "1", "Ⅱ": "2", "Ⅲ": "3", "Ⅳ": "4", "Ⅴ": "5"}
    s = re.sub(
        r"(\d+(?:の\d+)?)([ⅠⅡⅢⅣⅤ])([①-⑳])?",
        lambda m: f"{m[1]}条{roman[m[2]]}項" + (f"{ord(m[3]) - 0x245F}号" if m[3] else ""),
        s,
    )
    s = re.sub(r"(\d+(?:の\d+)?)/(?=\d)", r"\1条・", s)
    s = re.sub(r"(?<=条・)(\d+(?:の\d+)?)(?![\d条の])", r"\1条", s)
    if header:
        s = re.sub(r"(?<=[・（])(\d+(?:の\d+)?)(?=[）・])", r"\1条", s)
    return s


def drop_method_sentences(s: str) -> str:
    sents = re.split(r"(?<=。)", s)
    keep = [x for x in sents if not (len(x.strip()) <= METHOD_SENTENCE_MAX and METHOD_SENTENCE_RE.search(x))]
    return "".join(keep).strip()


# ---- カード（出題）と、読み上げないヒント ----

def card(kind: str, prompt: str, answers: list[str], label: str = "答え", strip: bool = True) -> tuple[str, list[str]]:
    """strip=False は論点・事案の整理の答え（中身そのもの）に使い、書き方の一言を落とす処理をかけない。"""
    answers = [a for a in (map(drop_method_sentences, answers) if strip else answers) if a]
    if not answers:
        return kind, []
    return kind, [f"- **Q00［{kind}］** {prompt}", *[f"  - {label}：{a}" for a in answers]]


def hint(kind: str, prompt: str, answers: list[str]) -> tuple[str, list[str]]:
    answers = [a for a in map(drop_method_sentences, answers) if a]
    if not answers:
        return kind, []
    return kind, [f"- 【{kind}】{prompt}", *[f"  - {a}" for a in answers]]


def quiz(q: Tag) -> tuple[str, list[str]]:
    question = re.sub(r"^【例題】", "", text(q.select_one(".quiz-question")))
    if METHOD_QUESTION_RE.search(question):
        return "", []
    ans_el = q.select_one(".quiz-answer")
    mark_el = ans_el.select_one(".qa-mark") if ans_el else None
    mark = text(mark_el) if mark_el else q.get("data-correct-value", "")
    if mark_el:
        mark_el.extract()
    answer = text(ans_el)
    if q.get("data-recall") == "1" or "recall" in (q.get("class") or []):
        return card("規範", re.sub(r"^【想起】", "", question), [answer], "模範解答")
    return "○×", [
        f"- **Q00［○×］** {question}",
        f"  - 正解：{MARKS.get(mark, mark)}",
        f"  - 理由：{drop_method_sentences(answer)}",
    ]


def peek_parts(d: Tag) -> tuple[str, str, list[str]]:
    summ = d.select_one("summary")
    hint_el = summ.select_one(".hint") if summ else None
    hint_t = text(hint_el)
    if hint_el:
        hint_el.extract()
    body = d.select_one(".body")
    answers = [text(p) for p in body.find_all(["p", "li"])] if body else []
    return text(summ), hint_t, answers


def with_count(prompt: str, hint_t: str) -> str:
    m = None if "まず" in hint_t else re.search(r"\d+", hint_t)
    return f"{prompt}（{m.group(0)}つ）" if m else prompt


def scan_prompt(ttl: str) -> str:
    return re.sub(r"を(?:時系列で)?棚卸し$", "を挙げて", ttl)


def aim_prompt(ttl: str) -> str:
    p = re.sub(r"(?:の|を)?(?:GUESS|アタリ|当たり)を?(?:する|付ける|つける)$", "", ttl).strip()
    p = re.sub(r"をGUESSし、", "を挙げ、", p)
    p = re.sub(r"\s*(?:の|を|で)?\s*「?GUESS」?\s*を?(?:する|で並べる)?", "", p).strip()
    p = re.sub(r"を$", "", re.sub(r"^(各?[^「」]{1,4})に「", r"\1は「", p))
    return f"{p} ― 見当をつけて"


def march_prompt(summary: str) -> str:
    p = summary.replace("自分で", "")
    p = re.sub(r"から開く$", "", p)
    p = re.sub(r"「?チェックポイント(?:（論点）)?」?|「詰まる所（＝論点）」|「素直に進めない所」", "問題になる論点", p)
    return p.strip() or "問題になる論点を挙げて"


def step_topic(ttl: str) -> str:
    """BREAK 等のステップ見出しから論点名だけを取り出す（「4点セットで割る」等の手順語は捨てる）。"""
    if "―" in ttl:
        t = ttl.rsplit("―", 1)[1]
    else:
        quoted = [q for q in re.findall(r"「([^」]+)」", ttl) if "4点" not in q]
        t = quoted[0] if quoted else re.sub(r"CP[①-⑳]", "", ttl) if "CP" in ttl else ""
    t = re.sub(r"^「([^」]+)」の一点$", r"\1", t.strip())
    t = re.sub(r"(?:の一点|＝本問の主戦場|を4点(?:セット)?で割る|を割る)$", "", t)
    t = re.sub(r"(?:最大の)?山場|本丸|チェックポイント[①-⑳]?|論点\d|4点セット", "", t)
    return re.sub(r"[「」]", "", t).strip(" 　・")


def facts_prompt(badge: str, topic: str) -> str:
    p = re.sub(r"^本問で|の掴み方$", "", badge)
    if p != "効く事実":
        return p
    return f"「{topic}」のあてはめで使う事実" if topic else "あてはめで使う事実"


def norm_prompt(badge: str, topic: str) -> str:
    m = re.search(r"規範（([^）]+)）", badge)
    name = m.group(1) if m else ""
    if name and not re.search(r"一文|段で|立て|→", name):
        return f"{name}の規範"
    return f"「{topic}」の規範" if topic else "この論点の規範"


def trap_prompt(badge: str) -> str:
    rest = re.sub(r"^.*?罠(?:に注意)?[：:]?", "", badge).strip()
    return f"ひっかけ注意「{rest}」 ― どういうこと？" if rest else "この論点のひっかけポイントは？"


OUTSIDE_NAV_CLASSES = {"bc-wrap", "drafting", "skeleton", "bone", "collate", "reveal-answer", "model-answer"}


def is_outside_nav(tag: Tag) -> bool:
    return bool(OUTSIDE_NAV_CLASSES & set(tag.get("class") or [])) or tag.get("id") == "deep-dive"


def steps(soup: BeautifulSoup) -> list[tuple[str, list[str]]]:
    """解法ナビの各ステップを、出題カードとヒントに分ける（順番・コツ・やることは落とす）。"""
    items: list[tuple[str, list[str]]] = []
    for step in soup.select(".step[id^=step-]"):
        code = text(step.select_one(".hd .code"))
        ttl = text(step.select_one(".hd .ttl"))
        topic = step_topic(ttl)
        for el in step.find_all(True):
            # 閉じ忘れの div でステップが入れ子になっても、各要素は一番近いステップでだけ拾う。
            # 答案作法・下書き・骨子・深掘り・模範答案に入り込んだ要素は拾わない（民JX057 で実害）。
            if el.find_parent(class_="step") is not step or el.find_parent(is_outside_nav):
                continue
            cls = el.get("class") or []
            if "self-check-quiz" in cls:
                if el.get("data-arena") == "1":
                    items.append(quiz(el))
                continue
            if code in ("ORDER", "BUILD"):
                continue
            if el.name == "details" and "peek" in cls:
                summary, hint_t, answers = peek_parts(el)
                if code == "SCAN":
                    items.append(card("事案の整理", with_count(scan_prompt(ttl), hint_t), answers, strip=False))
                elif code == "AIM":
                    items.append(card("見当づけ", with_count(aim_prompt(ttl), hint_t), answers, strip=False))
                else:
                    items.append(card("論点", with_count(march_prompt(summary), hint_t), answers, strip=False))
            elif el.name == "div" and "box" in cls:
                badge = text(el.select_one(".badge"))
                body = " ".join(text(p) for p in el.find_all("p"))
                if not body or METHOD_BADGE_RE.search(badge):
                    continue
                if code == "SCAN":
                    items.append(hint("事案の整理", badge, [body]))
                elif code == "AIM":
                    items.append(card("見当づけ", aim_prompt(ttl), [body]))
                elif "効く事実" in badge:
                    items.append(hint("効く事実", facts_prompt(badge, topic), [body]))
                elif "規範" in badge:
                    items.append(hint("規範の要点", norm_prompt(badge, topic), [body]))
                elif "罠" in badge:
                    items.append(card("ひっかけ", trap_prompt(badge), [body]))
                elif "素直" in badge:
                    items.append(hint("争いのない要件", "論点にならず、あっさり認定する要件", [body]))
                elif code == "BRIDGE":
                    items.append(hint("論点どうしの関係", "罪数・共犯関係など、論点どうしのつながり", [body]))
                else:
                    items.append(hint("ポイント", badge, [body]))
    return [(k, lines) for k, lines in items if lines]


def issue_names(sec: Tag) -> list[str]:
    """骨子の【論点】チップ（.iss）から論点名を取る。直前が「「暴行又は脅迫」→」なら要件名を添える。"""
    names = []
    for iss in sec.select(".iss"):
        name = re.sub(r"^【論点】", "", text(iss))
        prev = iss.previous_sibling
        ctx = re.search(r"(「[^」]+」)\s*→\s*$", str(prev)) if isinstance(prev, str) else None
        names.append(f"{ctx.group(1)} ― {name}" if ctx else name)
    return names


def skeleton(soup: BeautifulSoup) -> tuple[list[str], int, list[tuple[str, list[str]]]]:
    out: list[str] = []
    road: list[tuple[str, list[str]]] = []
    blocks = 0
    bone = soup.select_one(".bone")
    if not bone:
        return out, 0, road
    for sec in bone.select(".bsec"):
        blocks += 1
        head = sec.select_one(".b1")
        # 見出しの括弧（「殺人未遂・199条・203条」等）は結論そのものなので、見出しから外して本文に置く
        h = law_refs(text(head), header=True)
        hm = re.match(r"^(.+?)（(.+)）$", h)
        road.append((hm.group(1) if hm else h, issue_names(sec)))
        out += [f"#### {hm.group(1) if hm else h}", ""]
        if hm:
            out.append(f"- 見出しの補足（結論を含む。項目の終わりに読む）：{hm.group(2)}")
        head.extract()
        for bn in sec.select(".bn"):
            bn.replace_with(f"\n@@{bn.get_text().strip()} ")
        for ln in (METHOD_PAREN_RE.sub("", law_refs(x)).strip() for x in lines_text(sec)):
            if not ln:
                continue
            m = re.match(r"@@(\d+)\s*(.*)", ln)
            if m:
                out.append(f"{m.group(1)}. {m.group(2)}")
            elif ln.startswith("└"):
                out.append(f"   - あてはめ：{re.sub(r'^あてはめ：', '', ln.lstrip('└ ').strip())}")
            elif ln.startswith("→"):
                out.append(f"- {ln.lstrip('→ ').strip()}")
            else:
                out.append(f"   {ln}")
        out.append("")
    return out, blocks, road


def roadmap(road: list[tuple[str, list[str]]], reason: str) -> list[str]:
    """組み立ての順序：順番 → 項目ごとの論点名 → 順番の理由（ARIADNE の ORDER ステップ）。"""
    if not road:
        return []
    out = ["### 組み立ての順序（入口の問いのあと、骨子に入る前に読み上げる）", "", "- 順番：" + " → ".join(h for h, _ in road)]
    for h, names in road:
        out.append(f"- {h}")
        if not names:
            out.append("  - 論点：なし（結論の確認だけ）")
        elif len(names) == 1:
            out.append(f"  - 論点：{names[0]}")
        else:
            out += [f"  - 論点{i}：{x}" for i, x in enumerate(names, 1)]
    if reason:
        out += ["", f"この順番の理由（参考。結論・配点には触れず、一言で言い直す）：{reason}"]
    return out + [""]


def label_cards(lines: list[str], section: str, default_kind: str = "") -> list[str]:
    """出題カードに「［規範クイズ 2/6］」のようなパート内の番号を付ける（進行役が何問目か・残りを見失わない）。"""
    n = count_cards(lines)
    i = 0
    out = []
    for ln in lines:
        m = re.match(r"- \*\*Q00［([^］]+)］\*\* (.*)", ln)
        if m:
            i += 1
            kind = "" if m.group(1) == default_kind else f"・{m.group(1)}"
            out.append(f"- **［{section} {i}/{n}{kind}］** {m.group(2)}")
        else:
            out.append(ln)
    return out


def decoys(soup: BeautifulSoup) -> list[str]:
    bone = soup.select_one(".bone")
    raw = bone.get("data-kp-decoys", "") if bone else ""
    groups: dict[str, list[str]] = {}
    for item in filter(None, raw.split("|")):
        kind, _, val = item.partition(":")
        if kind in DECOY_KIND and val.strip():
            groups.setdefault(DECOY_KIND[kind], []).append(re.sub(r"^【論点】", "", val.strip()))
    return [f"- 【まぎらわしい選択肢・{k}】" + "／".join(v) for k, v in groups.items()]


def build(path: Path) -> tuple[str, str]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for t in soup(["script", "style"]):
        t.decompose()

    pid = path.stem.replace("_ARIADNE", "")
    title = text(soup.select_one("h1"))
    items = steps(soup)

    entry = [x for k, c in items if k in ("事案の整理", "見当づけ", "論点") and c[0].startswith("- **") for x in c]
    norms = [x for k, c in items if k in ("規範", "ひっかけ") for x in c]
    if not count_cards(norms):
        # 想起カードが無い問題は、解法ナビの「規範で一文」ボックスから規範クイズを作る（規範クイズを空にしない）
        for k, c in items:
            if k == "規範の要点":
                prompt = re.sub(r"^- 【規範の要点】", "", c[0])
                norms += card("規範", f"{prompt}を一文で言うと？", [re.sub(r"^\s*- ", "", x) for x in c[1:]], "模範解答")[1]
    ox = [x for k, c in items if k == "○×" for x in c]
    hints = [x for k, c in items if c[0].startswith("- 【") for x in c]

    # 事案：問題文・事実の要点・参考（登場人物の札と一行要約は論点の答えを含むので読み上げない）
    prob = soup.select_one(".problem")
    problem = text(prob.select_one("p.pq") or prob.find("p")) if prob else ""
    timeline = [text(li) for li in soup.select(".drafting ul.timeline li")]
    ref: list[str] = []
    cast = [text(c) for c in prob.select(".cast .c")] if prob else []
    if cast:
        ref += ["登場人物："] + [f"- {c}" for c in cast] + [""]
    digest = soup.select_one(".draft-digest .ddbody")
    d = ORDER_SENTENCE_RE.sub("", text(digest)).strip() if digest else ""
    if d:
        ref += [f"一行要約：{d}", ""]

    facts = []
    for li in soup.select(".drafting ul.facts li"):
        ph, cue = text(li.select_one(".ph")), re.sub(r"^―\s*", "", text(li.select_one(".cue")))
        quoted = ph if ph.startswith("「") and ph.endswith("」") else f"『{ph}』"
        facts.append(f"- 【拾う事実】{quoted} → {cue}")

    bone_md, blocks, road = skeleton(soup)
    order_reason = ""
    for st in soup.select(".step[id^=step-]"):
        if text(st.select_one(".hd .code")) == "ORDER":
            order_reason = drop_method_sentences(re.sub(r"理由を一言(?:添える|で)?[。：:]?", "", text(st.select_one("p.do")))).strip()
            break
    rb = soup.select_one(".bc-rhythm .rb")
    flow_summary = law_refs(text(rb)) if rb else ""

    n_entry, n_norm, n_ox = count_cards(entry), count_cards(norms), count_cards(ox)
    total = n_entry + n_norm + n_ox
    minutes = max(20, 5 * round((3 + n_entry * 0.8 + blocks * 4 + 3 + n_norm * 0.8 + n_ox * 0.4 + 3) / 5))

    flow = [
        f"1. **答案構成（入口{n_entry}問＋骨子{blocks}項目）**：「{pid}、{title}。まずは答案構成から、いきましょう！」のように一言で始める。"
        "書き方の一般論ではなく、この問題の骨子を口で組み立てる。",
        "   1. 【2. 答案構成】の問題文をゆっくり読み上げ、続けて事実の要点を読む",
        "   2. 入口の問い（事案の整理・見当づけ・論点）を順に出題する",
        "   3. 【組み立ての順序】を読み上げる：順番（第1 → 第2 → …）→ 項目ごとの論点名 → この順番の理由（結論には触れず一言）",
        "   4. 骨子の「第1」から、見出し（「第1　甲の罪責」の部分だけ）を言い、論点ごとに論点名を言ってから「規範は？」「あてはめで使う事実は？」を1つずつ聞く。"
        "項目の論点が終わったら「第1の結論は？」と聞く。詰まったら段階ヒント（事実を指す → 範囲を絞る → 2択 → 答えと復唱）",
        "   5. 各項目の終わりに、見出しの補足とその項目の骨子を短く読み上げ、「第1を一息で言ってみて」と復唱してもらう",
        "   6. 全項目が終わったら、見出しだけを言いながら全体を通しで口頭構成してもらい、流れのまとめを読んで答え合わせする",
    ]
    n = 1
    if n_norm:
        n += 1
        flow.append(f"{n}. **規範クイズ（全{n_norm}問）**：【3. 規範クイズ】を1問目から{n_norm}問目まで全部出す。1問ごとに「{n_norm}問中◯問目」と言ってから読み、口で説明してもらってキーワードの抜けを判定する。最後に「規範クイズ、全{n_norm}問クリア！」と言ってから次へ。")
    if n_ox:
        n += 1
        flow.append(f"{n}. **○×クイズ（全{n_ox}問）**：【4. ○×クイズ】を1問目から{n_ox}問目まで全部出す。1問ごとに「{n_ox}問中◯問目」と言ってから読む。最後に「○×クイズ、全{n_ox}問クリア！」と言ってから次へ。")
    n += 1
    flow.append(
        f"{n}. **間違えたところの復習**：ここまでで間違えた・わからなかった・ヒントで答えた問いを、もう一度だけ出す"
        "（答案構成で詰まった所は「〇〇の規範は？」のように論点名で聞き直す）。"
        "最後に正解数と、よくできた所を伝え、「今日の取りこぼし：〇〇、〇〇」と論点名で読み上げて、明るく締める。"
    )

    md: list[str] = [
        f"# PERIPATOS　{pid}　{title}",
        "",
        f"出典：{path.parent.name}/{path.name}（ARIADNE 解法ナビから機械抽出・本文は無改変）",
        "",
        "> **進行役の AI へ**：このファイルは学習セッションの台本です（参考資料ではありません）。"
        "読み込んだら要約・感想・「何をしましょうか」は言わず、ユーザーの最初の一言が何であっても、ただちに「1. 進行表」の1から始めてください。",
        "",
        "## 0. 進行役への指示",
        "",
        *RULES,
        f"## 1. 進行表（骨子{blocks}項目＋全部で{total}問・目安{minutes}分）",
        "",
        *flow,
        "",
        "## 2. 答案構成",
        "",
        "### 問題文（最初にゆっくり読み上げる）",
        "",
        problem,
        "",
    ]
    if timeline:
        md += ["### 事実の要点（問題文の直後に読む。「事実」と言われたら読み直す）", "", *[f"- {x}" for x in timeline], ""]
    else:
        md += ["### 事実の要点", "", "（このシートには無い。問題文から、法的な評価を入れずに3〜5行の要点を作って読む）", ""]
    if ref:
        md += ["### 参考（読み上げない。入口の問いの答えを含むので判定にだけ使う）", "", *ref]
    if entry:
        md += [f"### 入口の問い（{n_entry}問）", "", *label_cards(entry, "入口"), ""]
    md += roadmap(road, order_reason)
    if bone_md:
        md += [f"### 骨子（{blocks}項目。第1から、論点名 → 規範 → あてはめで使う事実、項目の最後に結論）", "", *bone_md]
    hint_md = facts + hints + decoys(soup)
    if hint_md:
        md += ["### ヒント（読み上げない。段階ヒントと判定に使う）", "", *hint_md, ""]
    if flow_summary:
        md += ["### 流れのまとめ（通しの口頭構成のあと、答え合わせに読む）", "", flow_summary, ""]
    if n_norm:
        md += [f"## 3. 規範クイズ（全{n_norm}問・1問目から最後まで全部出す）", "", *label_cards(norms, "規範クイズ", "規範"), "",
               f"（規範クイズはここまで＝全{n_norm}問。最後の{n_norm}問目まで出したら「規範クイズ、全{n_norm}問クリア！」と言って次へ）", ""]
    if n_ox:
        md += [f"## 4. ○×クイズ（全{n_ox}問・1問目から最後まで全部出す）", "", *label_cards(ox, "○×クイズ", "○×"), "",
               f"（○×クイズはここまで＝全{n_ox}問。最後の{n_ox}問目まで出したら「○×クイズ、全{n_ox}問クリア！」と言って復習へ）", ""]
    md += [
        "## 5. 間違えたところの復習",
        "",
        "ここまでで間違えた・わからなかった・ヒントで答えた問いを、進行表のとおりもう一度だけ出し、「今日の取りこぼし」を論点名で読み上げて締める。",
        "",
    ]
    return path.parent.name, re.sub(r"\n{3,}", "\n\n", "\n".join(md)).rstrip() + "\n"


def count_cards(lines: list[str]) -> int:
    return sum(1 for x in lines if x.startswith("- **Q00［"))


def is_current(path: Path, body: str) -> bool:
    return path.exists() and path.read_text(encoding="utf-8") == body


def main() -> int:
    ap = argparse.ArgumentParser(description="ARIADNE から PERIPATOS（音声学習の台本 MD）を作る")
    ap.add_argument("files", nargs="*", help="ARIADNE HTML のパス")
    ap.add_argument("--all", action="store_true", help="全 ARIADNE を対象にする")
    ap.add_argument("--subject", help="科目を絞る（刑/刑訴/民/商/民訴/行政/憲 または 00N_科目）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--check", action="store_true", help="書き込まず、未生成・古いシートがあれば一覧を出して exit 1")
    ap.add_argument("--quiet", action="store_true", help="1ファイルごとの表示を省く")
    a = ap.parse_args()
    if a.files:
        files = [Path(f) for f in a.files]
    elif a.all or a.subject:
        subj = SUBJECT_DIRS.get(a.subject or "", a.subject or "*")
        files = sorted(ARIADNE_DIR.glob(f"{subj}/*_ARIADNE.html"))
    else:
        ap.error("ARIADNE のパスか、--subject / --all を指定してください")
    out_root = Path(a.out)

    stale: list[Path] = []
    written = same = failed = 0
    guide = "\n".join(["# PERIPATOS 進行役（ChatGPT プロジェクトの「指示」欄に貼る）", "", *RULES, *PROJECT_FLOW]) + "\n"
    jobs: list[tuple[Path, str]] = [(out_root / PROJECT_FILE, guide)]
    for f in files:
        if not f.exists():
            continue
        try:
            subject, body = build(f)
        except Exception as e:  # 1問の不備で全体を止めない（副産物は非致命）
            failed += 1
            print(f"[PERIPATOS][ERROR] {f.name}: {e}", file=sys.stderr)
            continue
        jobs.append((out_root / subject / (f.stem.replace("_ARIADNE", "") + "_PERIPATOS.md"), body))

    for dst, body in jobs:
        if is_current(dst, body):
            same += 1
            continue
        if a.check:
            stale.append(dst)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(body, encoding="utf-8", newline="\n")
        written += 1
        if not a.quiet:
            print(f"[PERIPATOS] 更新 {dst}  {len(body):,}字")

    if a.check:
        for x in stale:
            print(f"[PERIPATOS][要更新] {x}")
        print(f"[PERIPATOS] check: 対象 {len(jobs) - 1}本（＋指示文） / 最新 {same} / 要更新 {len(stale)} / 生成失敗 {failed}")
        return 1 if (stale or failed) else 0
    print(f"[PERIPATOS] 対象 {len(jobs) - 1}本（＋指示文） / 更新 {written} / 変更なし {same} / 生成失敗 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
