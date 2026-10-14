#!/usr/bin/env python3
"""PERIPATOS-TX ― 短答 `_lex`（TX v13 一問一答カード）から、移動中・ながら作業中に音声（ChatGPT 音声モード等）で
短答過去問を回す台本 MD を書き出す。JX の PERIPATOS（scripts/peripatos-md.py）の短答版。

構成（2026-10-14 ユーザーの理想案＋推奨で確定）：
  1. 現在地と問題文 … 科目・出典・正答率から難易度を一言、体系の段階、見る条文 → 設問リードの原文と事例を読み上げる
                       （記述の原文・選択肢の組合せ一覧は読まない。記述は ○× で1つずつ自己完結の命題として読む）
  2. 導入講義の確認 … 「導入講義、聞きますか？」と一度だけ聞く。黙っていれば飛ばす。中身は 🔰導入（何の話／使う道具／
                       読む順番）。🔰導入が無いファイルでは、現在地・見る条文・カード見出しだけで30秒
  3. ○×クイズ     … `.ox-stmt` を読み上げてマルかバツか。判定→一言（記憶のフック）→×なら正しい規範（✍答案圧縮）を1文。
                       ヒントは1段だけ（解法ナビの「見る条文」＝問題単位・正解に触れない）。「勘」と言えば正解でも復習対象
  4. 解説           … 条文・判例・学説のカード（📚BASIS）を軸に（記述順ではない）。全体の物差し（物語解説）→カードごとに
                       本文の核→要件・趣旨→紐づく記述の切断点／転用（各記述は主カード1枚だけに置く）→横断→差し替え1問。
                       外した記述のカードを先に（順番は進行役が決める）
  5. 間違えたところの復習 … 取りこぼし＋勘＋ヒント＋導入つき正解を区別して、論点名（GIST「この記述の問い」）から規範の完全文を
                       言わせる。締めは論点名と肢キー（Lexia への手動反映用）。シートに次の問題があれば合図なしで続ける

- 決定論的な抜き出しだけを行う（本文の書き換え・要約はしない）。`_lex` が単一情報源。
- 読み上げない面：過去問原文の記述（ア〜オ・下線部①・人物記号 X/Y）、選択肢の組合せ一覧、語句群、体系マップ SVG、
  🔰導入の評価注記（紙面専用）、物語解説の「🔰導入にまとめてあります」ポインタ文。
- 条文番号・判例名・年月日はシート内のものだけを進行役に言わせる（JX と同じ規律）。

使い方:
  python -X utf8 scripts/peripatos-tx-md.py outputs/ux/000_TX/002_刑事訴訟法/刑訴TX142_lex.html   # 1問
  python -X utf8 scripts/peripatos-tx-md.py --subject 刑訴 --band 141-145                        # 5問帯を1枚に束ねる
  python -X utf8 scripts/peripatos-tx-md.py --subject 刑訴                                        # 科目の全問（1問1枚）
  python -X utf8 scripts/peripatos-tx-md.py --all --check                                         # 点検（未生成・古ければ exit 1）
  出力先の既定は outputs/ux/005_PERIPATOS/{00N_科目}/{ID}_PERIPATOS.md（帯は {接頭辞}TX{from}-{to}_PERIPATOS.md）
  ＋ outputs/ux/005_PERIPATOS/PERIPATOS-TX_プロジェクト指示.md（ChatGPT プロジェクト指示欄・8,000 字以内）
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parent.parent
LEX_DIR = ROOT / "outputs" / "ux" / "000_TX"
DEFAULT_OUT = ROOT / "outputs" / "ux" / "005_PERIPATOS"
SUBJECT_DIRS = {"刑": "001_刑法", "刑訴": "002_刑事訴訟法", "民": "003_民法", "商": "004_商法",
                "民訴": "005_民事訴訟法", "行政": "006_行政法", "憲": "007_憲法"}
SUBJECT_NAMES = {"001_刑法": "刑法", "002_刑事訴訟法": "刑事訴訟法", "003_民法": "民法", "004_商法": "商法",
                 "005_民事訴訟法": "民事訴訟法", "006_行政法": "行政法", "007_憲法": "憲法"}
PROJECT_FILE = "PERIPATOS-TX_プロジェクト指示.md"

# JX 版と共有する部品（絵文字除去・条文略記の読み開き・中断と再開／雰囲気の規則）＝単一情報源
_spec = importlib.util.spec_from_file_location("peripatos_md", ROOT / "scripts" / "peripatos-md.py")
_jx = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_jx)
clean, law_refs, EMOJI_RE = _jx.clean, _jx.law_refs, _jx.EMOJI_RE

MARKS = {"o": "○（正しい）", "x": "×（誤り）"}
ORIG_SKIP_RE = re.compile(r"^【?(?:記述|語句群|組合せ|選択肢)】?")
INTRO_POINTER_RE = re.compile(r"[^。]*(?:🔰|導入)[^。]*にまとめてあ[^。]*。")
DASH_RE = re.compile(r"\s*(?:——|──|――)\s*")
CJK_GAP_RE = re.compile(r"(?<=[^\x00-\x7F\s])[ \t]+(?=[^\x00-\x7F\s])")
HEAD_ICON_RE = re.compile(r"^[📜⚖🎓]\s*")
EXAM_CODE_RE = re.compile(r"\s*[・、]?\s*[HRS]\d+[-−‐]\s*\d+")
LAW_NOTE_KEEP = ("現在処理", "試験対策上の扱い")
KIND_LABEL = {"条文": "本文", "判例": "判旨", "学説": "学説"}
NO_NUM = {"本文", "本条", "判旨", "判旨核心"}


def _section(rules: list[str], head: str) -> list[str]:
    """JX の RULES から「### 見出し」で始まる節を切り出す（次の ### まで）。"""
    out: list[str] = []
    on = False
    for ln in rules:
        if ln.startswith("### "):
            if on:
                break
            on = ln.startswith(head)
        if on:
            out.append(ln)
    return out


RULES: list[str] = [
    "あなたは司法試験・予備試験の短答過去問を音声で回すセッション「PERIPATOS-TX」の進行役です。私は移動中・作業中で、画面も手元も見られず、メモも取れません。"
    "セッションはすべてあなたが仕切り、私は声で答えるだけにします。正解の根拠はシートの内容だけです。",
    "",
    "### 始め方（待たずに始める）",
    "",
    "- シートは台本であり、参考資料ではない。シートの「0. 進行役への指示」と「1. 進行表」に、ユーザーの指示と同じように従う。",
    "- 私の最初の一言が何であっても（「始めて」「スタート」「よろしく」「刑訴142」だけでも）、開始の合図として扱う。"
    "挨拶の質問、ファイルの要約、「何をしましょうか」「準備はいいですか」は言わず、すぐ進行表の1から始める。",
    "- 使う問題は、私が番号を言えばその問題（「刑訴142」「刑訴TX142」＝刑訴TX142。シートに複数の問題があれば、その番号の節から）、"
    "言わなければシートの最初の問題。どちらも無いときだけ「どの問題にしますか？」と一度聞く。",
    "- 私が「前回の続き」と言ったら、同じプロジェクトの直近の会話で取りこぼした記述を探し、その規範を1〜2問聞いてから進行表の1に入る。"
    "見つからなければ「前回取りこぼした論点を教えてください」と一度だけ聞く。",
    "",
    "### 仕切り方（進行はすべてあなたが決める・合図待ちをしない）",
    "",
    "- 次に何をするかは毎回あなたが決めて進める。「次に進みますか」「どれにしますか」とは聞かない。質問していいのは、導入講義を聞くかどうかの一度だけ。",
    "- 各パートの頭でパート名と問題数を言う。○×は1問ごとに「○×、6問中2問目」のように何問目かを言ってから読む（シートの［○× 2/6］がその番号）。",
    "- ○×クイズは、シートにある記述を1問目から最後の1問まで全部出す。途中で打ち切らない・間引かない・まとめて説明して済ませない。止めるのは私が「終わり」と言ったときだけ。",
    "- 最後の記述が終わったら「○×、全6問クリア！」のように言い切ってから解説へ進む。",
    "- 1回に聞くのは1つだけ。判定のあと、間を置かずに次へ進む。私が「進めて」と言わないと進まない状態をつくらない。",
    "- 私が黙っていても勝手に終わらせない。沈黙が続いたら一度だけ「どうですか？」と促し、それでも返事がなければ答えを言って次へ進む。",
    "- セッションを止めるのは、私が「ちょっと待って」等で止めたときだけ（下の【中断と再開】）。それ以外は最後の復習まで自分で進める。",
    "- 答えは黙って待つ。「考え中」と言われたら、私が答えるまで黙る。聞き取れなかったときは一度だけ「もう一度お願いします」と言い、それでも分からなければ「わからない」と同じ扱いにする。",
    "- 取りこぼしを覚えておく。間違えた・わからなかった・ヒントで答えた・「勘」と申告した記述は、最後の復習でもう一度出す。導入講義を聞いた問題の正解は「導入つき」として別に数える。",
    "- シートに問題が複数あるときは、1問の復習が終わったら合図を待たずに「次、刑訴143」と言って次の問題の1から続ける。全部終わったら全体の取りこぼしを読み上げて締める。",
    "",
    *_section(_jx.RULES, "### 中断と再開"),
    "",
    "### 1. 現在地と問題文",
    "",
    "- まず【現在地】を一息で言う（科目・出典・難易度の一言・テーマ・体系の段階・見る条文）。正解や各記述の正誤には触れない。",
    "- 続けて【問題文】を、設問の一文→事例や見解の順にゆっくり読み上げる。記述（ア〜オ）と選択肢の組合せ一覧は読まない（記述は○×で1つずつ読む）。",
    "- 「問題文」と言われたら、いつでも問題文を読み直す。",
    "",
    "### 2. 導入講義の確認（質問していいのはここだけ）",
    "",
    "- 問題文を読み終えたら「導入講義、聞きますか？」と一度だけ聞く。返事が無い・「いらない」「飛ばして」なら、何も言わずに○×へ進む。",
    "- 「聞く」「お願い」「導入」なら【導入講義】を読む。何の話か→使う道具（条文とその一言）→読む順番、の順。各記述の正誤・結論・組合せ番号は言わない。",
    "- 読み終えたら「では○×、いきます」と言ってすぐ○×へ。導入を聞いた問題は、正解しても復習の締めで「導入つきで正解」と区別して伝える。",
    "- シートに「このシートに導入は無い」とある問題では、現在地・見る条文・カード見出しを30秒で言うだけにする。",
    "",
    "### 3. ○×クイズ",
    "",
    "- 記述を文のまま読み上げて「マルかバツか」を聞く。判定したら、シートの【一言】を1文で添える。×の記述は続けて【規範】を1文で言う（正しくはこう、を耳に残す）。",
    "- 解説はここではしない。理由を聞かれても「解説でまとめて」と言って次の記述へ。",
    "- 「ヒント」と言われたら、シートの【ヒント】（この問題で見る条文）を1段だけ言う。それ以上のヒントは出さず、次に「答え」か「わからない」なら答えを言う。",
    "- 私が答えのあとに「勘」「当てずっぽう」と言ったら、正解でも復習対象に入れる。",
    "- 全記述が終わったら正解数を言い、【本試験の正解】がシートにあれば一言添えて解説へ。",
    "",
    "### 4. 解説（条文・判例・学説を軸に）",
    "",
    "- 最初に【全体の物差し】を読む（この問題を貫く一本の考え方）。",
    "- 次に【カード】を1枚ずつ。外した記述に紐づくカードを先に、取れた記述だけのカードは後に回す（順番はあなたが決める）。",
    "- 1枚の読み方：見出し→本文の核→要件・趣旨→紐づく記述を1つずつ（外した記述は切断点＝どこで正誤が分かれたか、取れた記述は転用＝次の問題へ持ち出す一文）→横断（似て非なる論点との分かれ目）。",
    "- カードに【差し替え】があれば、横断のあとに1問だけ聞く（「被害者を共犯者に変えたら、答えは？」のように）。答えは記号ではなく語で言わせ、判定したら次のカードへ。",
    "- 学説は、シートにある範囲で1〜2文だけ触れて広げない。短答は判例・通説の結論で足りる。",
    "- 【実務と事件】はカードを読み終えたあとに1回だけ読む（記述ごとに繰り返さない）。【最新改正】があれば最後に1文。",
    "- 「詳しく」と言われたら、そのカードの要件・趣旨と横断を2〜3文に広げる。「次」と言われたらすぐ次のカードへ。「規範」と言われたら、いまの記述の規範をもう一度読む。",
    "- 判例名・年月日・条文番号は、シートに書かれているものだけを言う。シートに無い知識を足すときは「シート外の補足ですが」と前置きし、断定できないことは「説が分かれます」と言う。",
    "",
    "### 5. 間違えたところの復習",
    "",
    "- 取りこぼし（間違えた・わからなかった・ヒント・勘）の記述を、【論点名】（この記述の問い）だけ言って「この記述の正しい規範は？」と聞き、【規範】で判定する。○×を聞き直すのではなく、規範を自分の口で言わせる。",
    "- 正解数と「今日の取りこぼし」を、論点名と肢キー（「刑訴TX142 記述イ」）の両方で読み上げる。導入を聞いた問題は「導入つき」と添える。",
    "- シートに次の問題があれば、そのまま次の問題の1へ。無ければ明るく締める。",
    "",
    *_section(_jx.RULES, "### 雰囲気"),
    "",
    "### 判定と話し方",
    "",
    "- 要点で判定する（言い回しの一致は求めない）。規範を言わせる問いでは、足りなければ言えた所を認めてから抜けたキーワードを言う。",
    "- 私は画面を見ないので、「Q12」のような番号や「シートの上の方」といった言い方はしない。問題の中身で話す。",
    "- 記号や略記は読み上げず、ふつうの言葉にする（「329条本文」は「さんびゃくにじゅうきゅう条の本文」、「→」は「だから」、「Ⅰ」「Ⅱ」は「いち」「に」）。",
    "- 答案の書き方、配点や分量の話はしない。解説に混じっていたら、そこは省いて法的な理由だけ言う。",
    "",
    "### 私が言うかもしれない合図（言わなければ、あなたの進行どおりに進める）",
    "",
    "- 「ちょっと待って」「待って」「ストップ」＝完全に黙る（「進めて」と言われるまで、何を話しても反応しない）",
    "- 「進めて」「再開」「続けて」「どうぞ」「次」＝止めた所から続ける／「考え中」＝私が答えるまで黙って待つ",
    "- 「導入」＝導入講義を読む／「飛ばして」＝答えを言わずに次へ／「ヒント」＝見る条文を1段だけ／「答え」＝答えを言う",
    "- 「勘」＝いまの正解を取りこぼし扱いにする／「規範」＝いまの記述の正しい規範を読む／「解説」＝その記述のカードへ飛ぶ",
    "- 「問題文」＝問題文を読み直す／「もう一回」＝今の問いを同じ文言で読み直す／「詳しく」＝横断を足す／「ゆっくり」「速く」＝読む速さ／「終わり」＝その場で復習に移って締める",
    "",
]

# ChatGPT プロジェクトの「指示」欄に貼る要約版（上限 8,000 字に収める・JX とは別プロジェクトで使う）
PROJECT_GUIDE: list[str] = [
    "# PERIPATOS-TX 進行役（ChatGPT プロジェクトの「指示」欄に貼る・短答用）",
    "",
    "あなたは司法試験・予備試験の短答過去問を音声で回すセッション「PERIPATOS-TX」の進行役。学習者（私）は移動中・仕事中で、"
    "画面も手元も見られず、メモも取れない。セッションはすべてあなたが仕切り、私は声で答えるだけ。"
    "正解の根拠は添付シート（PERIPATOS-TX シート）の内容だけ。シートは参考資料ではなく台本で、"
    "その「0. 進行役への指示」「1. 進行表」にはユーザーの指示と同じように従う。",
    "",
    "## 始め方",
    "",
    "- シートを受け取ったら、私の最初の一言が何であっても（「始めて」「よろしく」「刑訴142」だけでも）開始の合図として扱う。"
    "挨拶の質問・ファイルの要約・「何をしましょうか」は言わず、すぐ進行表の1から始める。",
    "- 使う問題は、私が番号を言えばその問題（「刑訴142」＝刑訴TX142・シート内のその節から）、言わなければシートの最初の問題。",
    "- 「前回の続き」と言われたら、直近の会話で取りこぼした記述の規範を1〜2問聞いてから始める。",
    "",
    "## 進行（止まらない・質問は導入講義の確認だけ）",
    "",
    "1. **現在地と問題文**：科目・出典・難易度の一言・テーマ・体系の段階・見る条文を一息で言い、設問の一文→事例・見解をゆっくり読む。"
    "記述（ア〜オ）と組合せ一覧は読まない。",
    "2. **導入講義の確認**：「導入講義、聞きますか？」と一度だけ聞く。返事が無い・「いらない」なら黙って○×へ。「聞く」なら、"
    "何の話か→使う道具（条文と一言）→読む順番を読む。各記述の正誤・結論は言わない。聞いた問題は復習で「導入つき」と区別する。",
    "3. **○×クイズ**：記述を文のまま読んで「マルかバツか」。全記述を1問目から最後まで、「6問中2問目」と何問目かを言ってから出す。"
    "判定→一言（記憶のフック）→×なら正しい規範を1文。解説はまだしない。「ヒント」はこの問題で見る条文を1段だけ。「勘」と言われた正解は復習対象。",
    "4. **解説**：全体の物差し→条文・判例・学説のカードを1枚ずつ（外した記述のカードを先に）。見出し→本文の核→要件・趣旨→"
    "紐づく記述（外した記述は切断点、取れた記述は転用）→横断→差し替え1問（あれば・語で答えさせる）。学説は1〜2文で広げない。"
    "実務と事件は最後に1回だけ。最新改正があれば1文。",
    "5. **間違えたところの復習**：取りこぼし（間違い・わからない・ヒント・勘）の記述を論点名で呼び、「正しい規範は？」と規範を言わせる。"
    "正解数と「今日の取りこぼし」を論点名と肢キー（「刑訴TX142 記述イ」）で読み上げる。シートに次の問題があれば合図なしで続ける。",
    "",
    "- 判定したら合図を待たず次へ。「次に行きますか」「続けますか」は聞かない。私が「進めて」と言わないと進まない状態をつくらない。",
    "- ○×は途中で打ち切らない・間引かない。最後まで出し「全6問クリア！」と言ってから解説へ。",
    "- 沈黙が続いたら一度だけ促し、返事がなければ答えを言って進む。",
    "",
    "## 中断と再開（仕事をしながら聞いている前提・最重要）",
    "",
    "- 勉強と関係のない発話（仕事の会話・電話・同僚への返事・独り言）には**いっさい反応しない**。質問に答えず、相づちも打たず、答えとして判定もしない。",
    "- 「ちょっと待って」「待って」「ストップ」と言われたら**そこで完全に黙る**（「待ってますね」も言わない）。",
    "- 止まっている間は私が何を話していても黙ったまま待つ（勝手に再開しない・催促しない）。",
    "- 再開するのは「進めて」「再開」「続けて」「どうぞ」「次」と言われたときだけ。止めた所を同じ文言で読み直して続ける。",
    "",
    "## 横断・判例・条文の扱い",
    "",
    "- 解説の横断は「どこで分かれるか」の一点に絞って1〜2文。足したらすぐ次へ。同じ比較はくり返さない。",
    "- **条文番号・判例名・年月日はシートに書かれたものだけ**を言う。無ければ名前を出さず中身だけ言う。"
    "シート外の知識は「シート外の補足ですが」と前置きし、断定できないことは「説が分かれます」と言う。",
    "",
    "## 判定・話し方・雰囲気",
    "",
    "- 要点で判定する。規範を言わせる問いでは、言えた所を認めてから抜けたキーワードを言う。",
    "- クイズ番組の司会のように明るくテンポよく。盛り上げは一言だけ。連続正解は数えて盛り上げる。間違いは「惜しい！」と軽く受ける。",
    "- 私は画面を見ないので「Q12」のような番号やシート上の位置で話さない。記号・略記は読み上げず普通の言葉にする（「Ⅰ」は「いち」）。",
    "- 答案の書き方・配点や分量の話はしない。",
    "",
    "## 合図",
    "",
    "- 「ちょっと待って」「ストップ」＝完全に黙る／「進めて」「再開」「続けて」＝止めた所から続ける／「考え中」＝黙って待つ",
    "- 「導入」＝導入講義を読む／「ヒント」＝見る条文を1段／「答え」＝答えを言う／「勘」＝取りこぼし扱い／「規範」＝正しい規範を読む／「解説」＝その記述のカードへ",
    "- 「問題文」＝読み直す／「もう一回」「飛ばして」「詳しく」「ゆっくり」「速く」／「終わり」＝復習に移って締める",
]


# ---- 抜き出し ----

def text(el: Tag | None) -> str:
    """要素の読み上げ文。インライン要素の境目に入る半角空白は、全角文字どうしの間なら落とす（「（ 訴因基準説 ）」を防ぐ）。"""
    if el is None:
        return ""
    s = re.sub(r"\s*\n\s*", "", el.get_text(" "))
    return clean(CJK_GAP_RE.sub("", s))


def strip_label(s: str, *labels: str) -> str:
    for lb in labels:
        s = re.sub(rf"^\s*{re.escape(lb)}\s*[：:]?\s*", "", s)
    return s.strip()


def labeled(el: Tag, sep: str = "：") -> str:
    """先頭の短いラベル要素（<b>性質</b>・<span class=tx-intro-lab>…）と本文を「ラベル：本文」に分ける。"""
    body = text(el)
    first = next((c for c in el.children if isinstance(c, Tag)), None)
    if first is not None and first.name in ("b", "strong", "span") and 0 < len(text(first)) <= 14:
        lab = text(first)
        rest = strip_label(body, lab)
        if rest != body:
            return f"{lab}{sep}{rest}"
    return body


def sentences(s: str, n: int) -> str:
    parts = [p for p in re.split(r"(?<=。)", s) if p.strip()]
    return "".join(parts[:n]).strip()


def spoken(s: str) -> str:
    return DASH_RE.sub("、", s)


def difficulty(rate: str) -> str:
    try:
        r = int(rate)
    except ValueError:
        return ""
    return "やさしめ" if r >= 60 else ("標準" if r >= 40 else "難問")


def exam_source(title: str) -> str:
    """title「管轄（管轄の判断基準・H22-37）」→「平成22年 問37」のような出典。取れなければ空。"""
    m = re.search(r"([HRS])(\d+)[-−‐]\s*(\d+)", title)
    if not m:
        return ""
    era = {"H": "平成", "R": "令和", "S": "昭和"}[m.group(1)]
    kind = ""
    if "予備" in title:
        kind = "予備試験 "
    elif "共通" in title:
        kind = "司法・予備共通 "
    return f"{kind}{era}{m.group(2)}年 問{m.group(3)}"


def theme(title: str) -> str:
    t = EXAM_CODE_RE.sub("", title)
    return re.sub(r"（\s*）", "", t).strip()


def original_text(soup: BeautifulSoup) -> list[str]:
    """過去問原文のうち読み上げる部分＝設問リードと事例・見解・会話。記述・語句群・組合せは読まない。"""
    out: list[str] = []
    lead = text(soup.select_one(".tx-original-lead"))
    if lead:
        out.append(f"- 設問：{lead}")
    pending = ""   # 「【事例】」だけの行は次の本文に前置する

    def push(tx: str) -> None:
        nonlocal pending
        if not tx or ORIG_SKIP_RE.match(tx):
            return
        if re.fullmatch(r"【[^】]+】", tx):
            pending = tx
            return
        out.append(f"- {pending}{tx}")
        pending = ""

    for blk in soup.select(".tx-original-block"):
        scenes = blk.select(".case-description .case-scene, .case-description > p, .tx-original-premise")
        if scenes:
            for scene in scenes:
                push(text(scene))
            continue
        for child in blk.find_all(recursive=False):
            cls = " ".join(child.get("class") or [])
            if any(k in cls for k in ("tx-original-charges", "tx-original-tag", "tx-original-lead", "tx-original-combos")):
                continue
            push(text(child))
    return out


def intro_lines(soup: BeautifulSoup) -> list[str]:
    """🔰導入（details.tx-intro）。評価注記と summary の cue は紙面専用なので落とす。"""
    intro = soup.select_one("details.tx-intro")
    if not intro:
        return []
    out: list[str] = []
    for ln in intro.select(".tx-intro-body > .tx-intro-line"):
        lab = text(ln.select_one(".tx-intro-lab"))
        tools = ln.select("ul.tx-intro-tools > li")
        if tools:
            out.append(f"- **{lab}**")
            out += [f"  - {law_refs(spoken(text(li)))}" for li in tools]
        else:
            body = strip_label(text(ln), lab) if lab else text(ln)
            out.append(f"- **{lab}**：{law_refs(spoken(body))}" if lab else f"- {law_refs(spoken(body))}")
    return out


def stmt_order(soup: BeautifulSoup) -> tuple[list[str], dict[str, str]]:
    tb = soup.select_one(".statement-verdict-table")
    key = (tb.get("data-answer-key") or "") if tb else ""
    pairs = [kv.split(":") for kv in key.split(",") if ":" in kv]
    return [k for k, _ in pairs], {k: v for k, v in pairs}


def verdict_rows(soup: BeautifulSoup) -> dict[str, Tag]:
    rows: dict[str, Tag] = {}
    for i, tr in enumerate(soup.select(".statement-verdict-table tbody tr"), 1):
        rows[tr.get("data-stmt") or str(i)] = tr
    return rows


def reflex(tr: Tag, tag: str) -> str:
    for ln in tr.select(".tx-reflex-line"):
        if text(ln.select_one(".tx-reflex-tag")) == tag:
            return strip_label(text(ln), tag)
    return ""


def story_parts(tr: Tag) -> tuple[str, str]:
    raw = tr.get("data-brief-story") or ""
    if not raw:
        return "", ""
    st = BeautifulSoup(raw, "html.parser")
    prac = strip_label(text(st.select_one(".tx-vb-prac")), "⚙ IN PRACTICE", "IN PRACTICE", "実務では、", "実務では")
    ex = strip_label(text(st.select_one(".tx-vb-ex")), "📁 CASE FILE", "CASE FILE", "たとえば、", "たとえば")
    return prac, ex


def card_of(soup: BeautifulSoup) -> dict[str, Tag]:
    return {c.get("data-stmt") or str(i): c for i, c in enumerate(soup.select(".tx-inline-card"), 1)}


def ox_statements(soup: BeautifulSoup) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, el in enumerate(soup.select(".ox-stmt"), 1):
        host = el.find_parent(attrs={"data-stmt": True})
        out[(host.get("data-stmt") if host else None) or str(i)] = text(el)
    return out


def hook(card: Tag | None) -> str:
    if card is None:
        return ""
    return spoken(strip_label(text(card.select_one(".syn-image")), "🗝 記憶のフック", "記憶のフック", "💭 INTUITION", "INTUITION"))


def anscomp(card: Tag | None) -> str:
    return text(card.select_one(".tx-anscomp-line")) if card is not None else ""


def issue_name(card: Tag | None) -> str:
    """復習で呼ぶ論点名＝GIST「この記述の問い」。無ければ GIST 結論行、それも無ければ記憶のフックの1文目。"""
    if card is None:
        return ""
    q = text(card.select_one(".tx-gist-q .tx-gist-body"))
    if q:
        return q
    h = re.sub(r"^[○×✓✗]\s*", "", text(card.select_one(".tx-gist-head")))
    return h or sentences(hook(card), 1)


def para_line(p: Tag) -> str:
    num = text(p.select_one(".para-num"))
    body = text(p.select_one(".hang-body")) or (strip_label(text(p), num) if num else text(p))
    if not num or num in NO_NUM:
        return body
    if re.fullmatch(r"[①-⑳]", num):
        return f"第{ord(num) - 0x245F}項：{body}"
    return f"{num}：{body}"


def basis_cards(soup: BeautifulSoup, order: list[str]) -> tuple[list[dict], dict[str, str]]:
    """カードごとの 📚BASIS を見出しで束ねる（同じ条文が複数の記述に付くので1枚にまとめ、紐づく記述を列挙）。
    各記述の主カード＝その記述の BASIS で最初に出る条文・判例（無ければ学説）。切断点・転用・横断は主カードにだけ置く。"""
    cards: dict[str, dict] = {}
    seq: list[str] = []
    primary: dict[str, str] = {}
    for st in order:
        for it in soup.select(f'.tx-inline-card[data-stmt="{st}"] .tx-basis-item'):
            head_el = it.select_one(".tx-basis-head")
            if head_el is None:
                continue
            head = BeautifulSoup(str(head_el), "html.parser")
            for junk in head.select(".freq-badge, .tx-basis-back"):
                junk.decompose()
            h = HEAD_ICON_RE.sub("", text(head))
            h = re.sub(r"\s*(?:──|——)\s*", "：", h)
            # 見出しは「刑訴法336条　無罪の判決」のように条文番号と題名の間を空ける（text() が全角間の空白を落とすため）
            h = re.sub(r"(\d+条(?:の\d+)?(?:\d+項)?(?:\d+号)?(?:本文|但書|ただし書)?)(?=[^\s（）／・\d項号本但た条])", r"\1　", h)
            cls = it.get("class") or []
            kind = "判例" if "is-case" in cls else ("学説" if "is-theory" in cls else "条文")
            if h not in cards:
                paras = [para_line(p) for p in it.select(".tx-basis-honbun > p")]
                notes: list[str] = []
                more = it.select_one("details.tx-basis-more")
                if more:
                    notes = [labeled(kd) for kd in more.select(".kd-item")]
                    if not notes:
                        more2 = BeautifulSoup(str(more), "html.parser")
                        for s_ in more2.select("summary"):
                            s_.decompose()
                        nt = text(more2)
                        if nt:
                            notes.append(nt)
                cards[h] = {"head": h, "kind": kind, "paras": [p for p in paras if p], "notes": [n for n in notes if n], "stmts": []}
                seq.append(h)
            if st not in cards[h]["stmts"]:
                cards[h]["stmts"].append(st)
            if st not in primary and kind != "学説":
                primary[st] = h
        if st not in primary:
            for h in seq:
                if st in cards[h]["stmts"]:
                    primary[st] = h
                    break
    return [cards[h] for h in seq], primary


def matrix_rows(card: Tag) -> tuple[str, list[list[str]]]:
    m = card.select_one(".tx-dgm.is-matrix")
    if not m:
        return "", []
    title = text(m.select_one(".tx-dgm-title"))
    grid = m.select_one(".tx-dgm-matrix")
    if not grid:
        return title, []
    cells = [text(c) for c in grid.find_all(recursive=False)]
    cols = 0
    for c in grid.get("class") or []:
        mm = re.match(r"is-c(\d)", c)
        if mm:
            cols = int(mm.group(1))
    if not cols or len(cells) < cols * 2:
        return title, []
    rows = [cells[i:i + cols] for i in range(0, len(cells) - len(cells) % cols, cols)]
    return title, rows[1:]


def trap_text(card: Tag) -> str:
    tr = card.select_one(".tx-v13-trap")
    if not tr:
        return ""
    body = tr.select_one(".tx-v13-trap-body")
    if body is None:
        return ""
    body = BeautifulSoup(str(body), "html.parser")
    for e in body.select(".tx-dgm, .tx-cc-tag"):
        e.decompose()
    return spoken(strip_label(text(body), "🔗 CROSS-CUT", "CROSS-CUT"))


def law_note(soup: BeautifulSoup) -> list[str]:
    note = soup.select_one(".tx-current-law-note")
    if not note:
        return []
    out: list[str] = []
    for row in note.select(".tx-law-note-row"):
        tx = text(row)
        for lb in LAW_NOTE_KEEP:
            if tx.startswith(lb):
                out.append(f"- {lb}：{sentences(strip_label(tx, lb), 2)}")
    return out


def narrative(soup: BeautifulSoup) -> str:
    fa = soup.select_one(".fa-narrative")
    if not fa:
        return ""
    fa = BeautifulSoup(str(fa), "html.parser")
    for e in fa.select(".tx-dgm, h3, h4, .fa-narrative-head, .fa-narrative-title"):
        e.decompose()
    tx = text(fa)
    tx = re.sub(r"^📖?\s*この問題を物語で読む\s*(?:──|―|-)?\s*", "", tx)
    tx = INTRO_POINTER_RE.sub("", tx)
    return spoken(tx).strip()


ARTICLE_RE = re.compile(r"([^\d／・\s　（）]*?)(\d+条(?:の\d+)?(?:\d+項)?(?:\d+号)?(?:本文|但書|ただし書)?)")


def article_list(heads: list[str]) -> str:
    """条文カードの見出しから条番号だけを拾い「刑事訴訟法253条・254条2項／刑法205条・210条」の形にする（題名は落とす）。"""
    seen: list[tuple[str, str]] = []
    for h in heads:
        law = ""
        for m in ARTICLE_RE.finditer(h):
            law = m.group(1) or law
            if (law, m.group(2)) not in seen:
                seen.append((law, m.group(2)))
    groups: list[tuple[str, list[str]]] = []
    for law, art in seen:
        if groups and groups[-1][0] == law:
            groups[-1][1].append(art)
        else:
            groups.append((law, [art]))
    return "／".join(f"{law}{'・'.join(arts)}" for law, arts in groups)


def official_answer(lex_path: Path) -> str:
    """公式 000_TX の data-explanation 末尾にある「組合せ肢N」を拾う（無ければ空・任意の一言）。"""
    off = ROOT / "outputs" / "000_TX" / lex_path.parent.name / lex_path.name.replace("_lex", "")
    if not off.exists():
        return ""
    h = off.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'data-explanation="([^"]*)"', h)
    if not m:
        return ""
    mm = re.search(r"(?:組合せ|正解)[^。）]*?肢\s*(\d)", m.group(1))
    return f"本試験の正解は肢{mm.group(1)}" if mm else ""


# ---- 1問ぶんの台本 ----

def build_problem(path: Path, num_label: str = "") -> tuple[str, str, list[str], int, int]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for t in soup(["script", "style", "svg"]):
        t.decompose()
    if not soup.select_one(".tx-inline-card"):
        raise ValueError("v13 インライン周回の _lex ではない（記述カードが無い）")

    pid = path.stem.replace("_lex", "")
    full_title = text(soup.title)
    title = re.sub(rf"^{re.escape(pid)}\s*[-－―]\s*", "", full_title)
    subject = SUBJECT_NAMES.get(path.parent.name, path.parent.name)
    meta = text(soup.select_one(".exam-meta"))
    rate_m = re.search(r"正答率[：:]?\s*(\d+)", meta)
    rate = rate_m.group(1) if rate_m else ""
    order, marks = stmt_order(soup)
    rows = verdict_rows(soup)
    cards = card_of(soup)
    oxs = ox_statements(soup)
    if not order:
        order = list(cards.keys())
    first = cards.get(order[0]) if order else None
    track = [text(x) for x in first.select(".tx-gist-track .tx-gist-step")] if first else []
    nav = text(soup.select_one(".solve-nav"))
    nav_m = re.search(r"見る条文は\s*([^。]+)", nav)
    nav_laws = law_refs(nav_m.group(1)) if nav_m else ""

    orig = original_text(soup)
    intro = intro_lines(soup)
    bcards, primary = basis_cards(soup, order)
    if not nav_laws:   # 解法ナビに「見る条文は」が無い問題は、条文カードの見出しの条番号で代える（題名は付けない＝正解に触れない）
        nav_laws = article_list([bc["head"] for bc in bcards if bc["kind"] == "条文"])

    src = exam_source(title)
    cur = [f"- 科目・出典：{subject}" + (f"　{src}" if src else "") + (f"　正答率 {rate}%（{difficulty(rate)}）" if rate else "")]
    cur.append(f"- テーマ：{theme(title)}")
    if track:
        cur.append(f"- 体系の段階：{' → '.join(track)}")
    if nav_laws:
        cur.append(f"- 見る条文：{nav_laws}")

    n = len(order)
    ox_md: list[str] = []
    for i, st in enumerate(order, 1):
        c = cards.get(st)
        stmt = oxs.get(st) or (text(c.select_one(".tx-inline-stmt-text")) if c else "")
        mark = MARKS.get(marks.get(st, ""), "")
        ox_md.append(f"- **［○× {i}/{n}］** {stmt}")
        ox_md.append(f"  - 答え：{mark}")
        hk = hook(c)
        if hk:
            ox_md.append(f"  - 一言（判定のあとに1文）：{hk}")
        ac = anscomp(c)
        if ac:
            ox_md.append(f"  - 規範（×のときは続けて1文で。復習でも使う）：{ac}")
        ox_md.append("")
    if nav_laws:
        ox_md.append(f"（ヒントは全記述共通で1段だけ：「見る条文は {nav_laws}」。それ以上は出さない）")
    oa = official_answer(path)

    story = narrative(soup)
    exp_md: list[str] = []
    if story:
        exp_md += ["#### 全体の物差し（解説の最初に読む）", "", story, ""]
    pracs: list[str] = []
    exs: list[str] = []
    for k, bc in enumerate(bcards, 1):
        linked = "・".join(f"記述{s}" for s in bc["stmts"])
        exp_md += [f"#### カード{k}［{bc['kind']}］{law_refs(bc['head'], header=True)}（{linked}）", ""]
        lab = KIND_LABEL[bc["kind"]]
        for p in bc["paras"][:4]:
            exp_md.append(f"- {lab}：{law_refs(p)}")
        for nt in bc["notes"][:3]:
            exp_md.append(f"- 要件・趣旨：{law_refs(spoken(sentences(nt, 3)))}")
        mine = [s for s in bc["stmts"] if primary.get(s) == bc["head"]]
        for st in mine:
            tr = rows.get(st)
            mark = MARKS.get(marks.get(st, ""), "")
            cut, use = (reflex(tr, "切断点"), reflex(tr, "転用")) if tr else ("", "")
            line = f"- 記述{st}（{mark}）"
            if cut:
                line += f"　切断点：{spoken(cut)}"
            if use:
                line += f"　転用：{spoken(use)}"
            exp_md.append(line)
        for st in mine:
            c = cards.get(st)
            if c is None:
                continue
            tp = trap_text(c)
            if tp:
                exp_md.append(f"- 横断（記述{st}）：{sentences(tp, 3)}")
            title_m, rws = matrix_rows(c)
            for r in rws[:4]:
                ans = re.sub(r"^[○✕×✓]\s*", "", r[1]) if len(r) >= 2 else ""   # 答えは記号ではなく語で言わせる（○/✕ は法的帰結の層）
                if len(r) >= 2 and r[0] and ans:
                    exp_md.append(f"- **［差し替え］** {title_m + '。' if title_m else ''}「{r[0]}」と変えたら、答えは？")
                    exp_md.append(f"  - 答え：{ans}" + (f"（根拠：{law_refs(r[2])}）" if len(r) > 2 and r[2] else ""))
        exp_md.append("")
    for st in order:
        tr = rows.get(st)
        if tr is None:
            continue
        p_, e_ = story_parts(tr)
        if p_ and p_ not in pracs:
            pracs.append(p_)
        if e_ and e_ not in exs:
            exs.append(e_)
    if pracs or exs:
        exp_md += ["#### 実務と事件（カードのあとに1回だけ読む）", ""]
        exp_md += [f"- 実務では：{spoken(p)}" for p in pracs[:2]]
        exp_md += [f"- 事件：{spoken(e)}" for e in exs[:2]]
        exp_md.append("")
    ln = law_note(soup)
    if ln:
        exp_md += ["#### 最新改正（最後に1文）", "", *ln, ""]

    rev_md = [f"- {pid} 記述{st}（{MARKS.get(marks.get(st, ''), '')}）論点名：{issue_name(cards.get(st))}" for st in order]

    head_label = f"{num_label} " if num_label else ""
    md: list[str] = [
        f"## {head_label}{pid}　{theme(title)}",
        "",
        f"出典：{path.parent.name}/{path.name}（TX 一問一答カードから機械抽出・本文は無改変）",
        "",
        "### 1. 現在地（最初に一息で言う。正解には触れない）",
        "",
        *cur,
        "",
        "### 問題文（設問→事例・見解の順にゆっくり読む。記述と組合せ一覧は読まない）",
        "",
        *(orig or ["（このシートに過去問原文の設問・事例は無い。テーマと見る条文を言って、そのまま○×へ）"]),
        "",
        "### 2. 導入講義（「導入講義、聞きますか？」と一度だけ聞く。黙っていれば飛ばす）",
        "",
    ]
    if intro:
        md += intro
    else:
        md += ["（このシートに導入は無い。現在地と見る条文、下のカード見出しを30秒で言うだけにする）", ""]
        md += [f"- カード見出し：{bc['head']}" for bc in bcards]
    md += ["", f"### 3. ○×クイズ（全{n}問・1問目から最後まで全部出す）", "", *ox_md]
    md.append(f"（○×はここまで＝全{n}問。最後の{n}問目まで出したら「○×、全{n}問クリア！」と言い、正解数を伝えて解説へ）")
    if oa:
        md.append(f"（{oa}。正解数のあとに一言だけ添える）")
    md += ["", f"### 4. 解説（カード{len(bcards)}枚。外した記述のカードを先に）", "", *exp_md]
    md += ["### 5. 間違えたところの復習", "",
           "取りこぼし（間違えた・わからなかった・ヒント・勘）の記述を論点名で呼び、「正しい規範は？」と聞いて【規範】で判定する。"
           "締めは正解数と「今日の取りこぼし」を論点名と肢キーの両方で読み上げる（導入を聞いた問題は「導入つき」と添える）。", "",
           *rev_md, ""]
    minutes = 4 + n + len(bcards) + (2 if intro else 0)
    return pid, theme(title), md, n, minutes


def sheet(problems: list[tuple[str, str, list[str], int, int]], sheet_title: str, src_note: str) -> str:
    total_q = sum(p[3] for p in problems)
    minutes = sum(p[4] for p in problems)
    flow = [
        f"{i}. {pid}　{title}（記述{n}問・目安{m}分）：現在地と問題文 → 導入講義の確認 → ○× → 解説 → 復習"
        for i, (pid, title, _, n, m) in enumerate(problems, 1)
    ]
    md: list[str] = [
        f"# PERIPATOS-TX　{sheet_title}",
        "",
        src_note,
        "",
        "> **進行役の AI へ**：このファイルは学習セッションの台本です（参考資料ではありません）。"
        "読み込んだら要約・感想・「何をしましょうか」は言わず、ユーザーの最初の一言が何であっても、ただちに「1. 進行表」の1から始めてください。"
        "問題が複数あるときは、1問の復習が終わったら合図を待たずに次の問題へ進んでください。",
        "",
        "## 0. 進行役への指示",
        "",
        *RULES,
        f"## 1. 進行表（{len(problems)}問・記述{total_q}問・目安{minutes}分）",
        "",
        *flow,
        "",
        "各問とも、質問するのは「導入講義、聞きますか？」の一度だけ。あとは止まらずに進める。",
        "",
    ]
    for _, _, body, _, _ in problems:
        md += ["---", "", *body]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(md)).rstrip() + "\n"


def is_current(path: Path, body: str) -> bool:
    return path.exists() and path.read_text(encoding="utf-8") == body


def parse_band(s: str) -> tuple[int, int]:
    m = re.match(r"^\s*(\d+)\s*[-〜～]\s*(\d+)\s*$", s)
    if not m:
        raise SystemExit(f"--band は 141-145 の形式で指定する: {s!r}")
    a, b = int(m.group(1)), int(m.group(2))
    return (a, b) if a <= b else (b, a)


def main() -> int:
    ap = argparse.ArgumentParser(description="TX _lex から PERIPATOS-TX（短答の音声学習台本 MD）を作る")
    ap.add_argument("files", nargs="*", help="_lex HTML のパス")
    ap.add_argument("--all", action="store_true", help="全 _lex を対象にする（1問1枚）")
    ap.add_argument("--subject", help="科目を絞る（刑/刑訴/民/商/民訴/行政/憲 または 00N_科目）")
    ap.add_argument("--band", help="番号帯を1枚に束ねる（例 141-145・--subject と併用）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--check", action="store_true", help="書き込まず、未生成・古いシートがあれば一覧を出して exit 1")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    out_root = Path(a.out)
    guide = "\n".join(PROJECT_GUIDE) + "\n"
    if len(guide) > 8000:
        print(f"[PERIPATOS-TX][ERROR] プロジェクト指示が {len(guide):,} 字＝8,000 字を超えている", file=sys.stderr)
        return 1
    jobs: list[tuple[Path, str]] = [(out_root / PROJECT_FILE, guide)]
    failed = 0

    def build_one(f: Path, label: str = ""):
        nonlocal failed
        try:
            return build_problem(f, label)
        except Exception as e:  # 1問の不備で全体を止めない
            failed += 1
            print(f"[PERIPATOS-TX][SKIP] {f.name}: {e}", file=sys.stderr)
            return None

    if a.band:
        if not a.subject:
            ap.error("--band には --subject が要る")
        subj = SUBJECT_DIRS.get(a.subject, a.subject)
        lo, hi = parse_band(a.band)
        files: list[Path] = []
        for nnn in range(lo, hi + 1):
            files += sorted((LEX_DIR / subj).glob(f"*TX{nnn:03d}_lex.html"))
        if not files:
            ap.error(f"{subj} に {lo}-{hi} の _lex が無い")
        probs = []
        for i, f in enumerate(files, 1):
            r = build_one(f, f"{i}/{len(files)}")
            if r:
                probs.append(r)
        if probs:
            prefix = re.sub(r"TX\d+$", "", probs[0][0])
            name = f"{prefix}TX{lo:03d}-{hi:03d}"
            body = sheet(probs, f"{name}（{len(probs)}問セット）",
                         f"出典：{subj}/{name} の `_lex`（TX 一問一答カードから機械抽出・本文は無改変）")
            jobs.append((out_root / subj / f"{name}_PERIPATOS.md", body))
    else:
        if a.files:
            files = [Path(f) for f in a.files]
        elif a.all or a.subject:
            subj = SUBJECT_DIRS.get(a.subject or "", a.subject or "*")
            files = sorted(LEX_DIR.glob(f"{subj}/*_lex.html"))
        else:
            ap.error("_lex のパスか、--subject / --all を指定してください")
        for f in files:
            if not f.exists():
                continue
            r = build_one(f)
            if not r:
                continue
            pid, title, _, _, _ = r
            jobs.append((out_root / f.parent.name / f"{pid}_PERIPATOS.md",
                         sheet([r], f"{pid}　{title}", f"出典：{f.parent.name}/{f.name}（TX 一問一答カードから機械抽出・本文は無改変）")))

    stale: list[Path] = []
    written = same = 0
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
            print(f"[PERIPATOS-TX] 更新 {dst}  {len(body):,}字")
    if a.check:
        for x in stale:
            print(f"[PERIPATOS-TX][要更新] {x}")
        print(f"[PERIPATOS-TX] check: 対象 {len(jobs) - 1}枚（＋指示文） / 最新 {same} / 要更新 {len(stale)} / 生成失敗 {failed}")
        return 1 if (stale or failed) else 0
    print(f"[PERIPATOS-TX] 対象 {len(jobs) - 1}枚（＋指示文） / 更新 {written} / 変更なし {same} / 生成失敗 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
