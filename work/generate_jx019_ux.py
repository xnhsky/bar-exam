#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from html import escape
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parents[1]
STAMP_ISO = "2026-06-28T22:10+09:00"
STAMP_TEXT = "2026-06-28 22:10"
SUBJECT_DIR = "001_刑法"
BASE_CODE = "刑JX019"
RX_BASE = "刑RX019"
TITLE = "早すぎた・遅すぎた構成要件の実現"
LONG_TITLE = "刑JX019　早すぎた・遅すぎた構成要件の実現 ― 殺人罪のシステマティック解法"


def e(value: str) -> str:
    return escape(value, quote=True)


RX_TOPICS = [
    {
        "name": "相続と「財産上……の利益」",
        "lead": "甲はAを殺害して相続により全財産を得ようとしているため、入口では2項強盗殺人罪が浮かぶ。しかし相続利益は財物の占有移転と同視できる具体的・直接的利益ではないため、強盗殺人を切って殺人罪へ進む。",
        "norm": "刑法236条2項の「財産上……の利益」は、1項強盗との均衡から、財物の占有移転と同視できる程度に具体的・直接的な利益を現実に取得したと評価できるものをいう。相続による財産承継は、死亡により直ちに事実上支配へ移る利益ではなく、法律上の承継手続・相続関係の確定を介するため、具体性・直接性を欠く。",
        "cite": "東京高判平成元年2月27日（相続と財産上の利益）",
        "reason": "2項強盗は財物移転がない場面を補充する規定であるから、抽象的・期待的な経済利益まで含めると処罰範囲が過度に広がる。殺害により相続が開始しても、利益取得の直接原因は相続法上の承継であり、暴行・脅迫による利益移転とはいえない。",
        "apply": [
            "甲はAの唯一の法定相続人であるが、相続による全財産取得は相続制度を介した包括承継である。",
            "A殺害行為から直ちに甲が具体的財産を直接取得するわけではなく、利益の具体性・直接性を欠く。",
            "よって2項強盗は成立せず、強盗殺人罪ではなく殺人罪を検討対象に据える。"
        ],
        "refs": "刑法236条2項、240条後段、199条",
        "case": "東京高判平成元年2月27日",
        "quizzes": [
            ("相続により全財産を得る目的で殺害した場合、相続利益は当然に2項強盗の財産上の利益となる。", "×", "相続は具体的・直接的な利益取得とはいえず、2項強盗は否定する。"),
            ("2項強盗の利益該当性では、1項強盗との均衡から具体性・直接性が問題になる。", "○", "財物の占有移転と同視できる程度の利益かを問う。"),
            ("強盗殺人を否定しても、殺意と死亡結果があるため殺人罪の検討は残る。", "○", "本問では強盗殺人を切った後、殺人既遂の成否へ進む。"),
        ],
    },
    {
        "name": "早すぎた構成要件の実現と実行の着手",
        "lead": "甲の計画では山中で刺殺する予定だったが、現実にはその前段階である強打・猿ぐつわ・トランク閉込めによりAが窒息死している。第1行為の時点で殺人の実行の着手を認められるかが核心である。",
        "norm": "実行の着手は、構成要件該当行為への密接性と、法益侵害ないし構成要件実現に至る現実的危険性から判断する。行為者の計画を踏まえ、準備的行為と構成要件該当行為との不可分性・必要不可欠性、時間的場所的接着性、準備的行為後に障害となる事情の有無を総合考慮する。",
        "cite": "最決平成16年3月22日（クロロホルム事件）",
        "reason": "未遂処罰の根拠は結果発生の現実的危険にある。計画上一連一体の行為で、前段階が後段階を確実かつ容易にするため不可欠であれば、後段階を待たずに構成要件実現への危険が顕在化している。",
        "apply": [
            "強打・猿ぐつわ・トランク閉込めは、山中でAを確実かつ容易に殺害するため必要不可欠である。",
            "移動距離は約5km、時間は約10分で、時間的場所的接着性がある。",
            "人気のない山中へ連れて行く計画であり、第1行為後に第2行為を妨げる特段の事情もない。",
            "したがって第1行為開始時点で殺人の実行の着手を肯定できる。"
        ],
        "refs": "刑法43条本文、199条",
        "case": "最決平成16年3月22日",
        "quizzes": [
            ("早すぎた構成要件の実現では、準備行為だからという理由だけで実行の着手を否定する。", "×", "計画上一連の行為で現実的危険があれば、前段階で着手を肯定し得る。"),
            ("着手判断では、不可分性・時間的場所的接着性・障害事情の有無が重要になる。", "○", "クロロホルム事件型の三つの認定軸である。"),
            ("甲の第1行為は第2行為を容易にするための行為で、A死亡の現実的危険も有する。", "○", "本問のあてはめでは密接性と危険性を肯定する。"),
        ],
    },
    {
        "name": "因果関係の錯誤と甲の故意",
        "lead": "甲は山中で刺殺するつもりだったが、現実にはトランク内で窒息死が生じた。この予見した因果経過と現実の因果経過の食い違いが、殺人の故意を阻却するかが問題となる。",
        "norm": "因果関係に錯誤があっても、行為者が認識した因果経過と現実の因果経過が構成要件の範囲内で符合し、同一の法益侵害へ向けられた危険の現実化と評価できる限り、故意は阻却されない。",
        "cite": "法定的符合説／クロロホルム事件",
        "reason": "故意責任の基礎は、構成要件的結果発生の危険を認識しながら行為し、規範に直面して反対動機を形成できた点にある。死因や経路の細部が予見と違っても、人の死亡という構成要件的結果の範囲で符合していれば責任非難は失われない。",
        "apply": [
            "甲はAを殺害する一連の計画を認識し、その実現に向け第1行為を開始している。",
            "予見は刺殺による死亡、現実は窒息死だが、いずれもA死亡という同一構成要件内の危険である。",
            "したがって因果関係の錯誤は殺人の故意を阻却せず、殺人既遂罪が成立する。"
        ],
        "refs": "刑法38条1項、199条",
        "case": "最決平成16年3月22日",
        "quizzes": [
            ("予見した死因と現実の死因が異なれば、因果関係の錯誤により故意は常に阻却される。", "×", "構成要件の範囲内で符合すれば故意は阻却されない。"),
            ("甲については、着手肯定により一連の殺人行為への認識を故意の基礎にできる。", "○", "第1行為単体の死の認識ではなく、一連の行為への認識が橋渡しになる。"),
            ("刺殺予定と窒息死の差は、A死亡という構成要件的結果の範囲内で処理する。", "○", "答案では法定的符合説の理由付けまで書くと安定する。"),
        ],
    },
    {
        "name": "遅すぎた構成要件の実現と危険の現実化",
        "lead": "乙はBを絞首して死んだと思い、発覚防止のため砂上に放置したが、実際にはその後の砂末吸引で死亡した。乙自身の投棄行為が介在しても、絞首行為と死亡結果の因果関係を肯定できるかが核心である。",
        "norm": "因果関係は、当該行為が内包する危険が結果として現実化したかにより判断する。介在事情がある場合には、実行行為の危険性、介在事情の異常性、介在事情の結果への寄与度を総合考慮する。",
        "cite": "大判大正12年4月30日（砂末吸引事件）／危険の現実化",
        "reason": "因果関係は単なる自然的条件関係ではなく、結果を行為に帰責できるほどの法的評価である。殺意ある絞首の直後に発覚防止として身体を放置することは、殺害行為に通常随伴しうる事後処分であり、異常な外部事情とはいえない。",
        "apply": [
            "麻縄で力いっぱい首を絞める行為は、それ自体B死亡の高度の危険を有する。",
            "発覚防止のため砂上へ運び放置することは、殺害を企てた者の行動として偶発的・異常とはいえない。",
            "砂末吸引死は投棄を介したものだが、第1行為の危険の延長線上にあるため因果関係を肯定する。"
        ],
        "refs": "刑法199条",
        "case": "大判大正12年4月30日、最決平成2年11月20日",
        "quizzes": [
            ("乙の第2行為が介在した以上、絞首行為と死亡結果の因果関係は必ず切断される。", "×", "介在が非異常で、行為の危険が結果に現実化したと評価できれば因果関係を肯定する。"),
            ("危険の現実化では、実行行為の危険性と介在事情の異常性を検討する。", "○", "本問では絞首の危険性が高く、投棄の異常性は低い。"),
            ("砂末吸引事件は、本問乙とほぼ同型の遅すぎた構成要件の実現である。", "○", "判例対応を示すと答案の説得力が増す。"),
        ],
    },
    {
        "name": "因果関係の錯誤と概括的故意",
        "lead": "乙は頸部圧迫によりBが死亡したと認識していたが、現実には砂末吸引で死亡している。客観面で因果関係を肯定した後、この因果経過のズレが殺人故意を阻却するかを処理する。",
        "norm": "行為者が認識した因果経過と現実の因果経過に食い違いがあっても、構成要件の範囲内で符合し、行為の危険が結果へ現実化している限り、因果関係の錯誤は故意を阻却しない。遅すぎた構成要件の実現では、客観面の因果関係を肯定したうえで主観面をこの規範で処理する。",
        "cite": "大判大正12年4月30日／法定的符合説",
        "reason": "乙は殺意をもってBの首を絞めており、人の死亡という構成要件的結果に向けられた危険を認識している。現実の死亡経路が砂末吸引であっても、同一被害者の死亡に向かう危険が一連の行為を通じて実現した以上、反対動機形成の機会は失われない。",
        "apply": [
            "乙の認識は頸部圧迫死、現実は砂末吸引死である。",
            "しかし絞首行為と投棄行為は一連の流れで、B死亡という同一構成要件的結果に向かう。",
            "よって因果関係の錯誤は故意を阻却せず、殺人既遂罪を肯定する。"
        ],
        "refs": "刑法38条1項、199条",
        "case": "大判大正12年4月30日",
        "quizzes": [
            ("乙がBは既に死亡したと思って投棄しているため、絞首時の殺意は既遂責任に使えない。", "×", "絞首時の殺意と、危険の現実化を介して殺人既遂の故意責任を肯定する。"),
            ("遅すぎた構成要件の実現では、客観面の因果関係を先に処理する。", "○", "因果関係を肯定してから、因果経過の錯誤が故意を阻却しないと述べる。"),
            ("因果経過の細部のズレは、構成要件の範囲内で符合すれば故意を妨げない。", "○", "法定的符合説の基本処理である。"),
        ],
    },
    {
        "name": "過失致死罪の吸収と死の二重評価回避",
        "lead": "乙の投棄行為だけを切り出すと、Bを生存中に砂上へ放置した点で過失致死罪が見える。しかし、殺人既遂を肯定するなら同じ死亡結果を二重に評価しないよう整理する必要がある。",
        "norm": "一個の死亡結果について殺人既遂罪の成立を肯定する場合、同じ死亡結果を基礎に投棄行為を別途過失致死罪として処罰すると、結果の二重評価となる。したがって、投棄行為の過失致死的評価は殺人既遂罪に吸収される。",
        "cite": "罪数処理・結果の二重評価回避",
        "reason": "刑法上の評価は結果を重ねて数えるものではない。乙の行為全体を殺人既遂として把握できるなら、投棄行為は因果経過の一部または事後処分として殺人既遂の評価に取り込まれる。",
        "apply": [
            "投棄時にBがなお生存していた以上、外形的には過失致死の構成要件が問題になり得る。",
            "しかしB死亡という一つの結果は、絞首から投棄までの一連の危険の現実化として殺人既遂に評価済みである。",
            "したがって過失致死罪を別途成立させず、殺人既遂罪に吸収させる。"
        ],
        "refs": "刑法199条、210条",
        "case": "砂末吸引事件の答案処理",
        "quizzes": [
            ("乙について殺人既遂を認める場合でも、同一死亡結果につき過失致死罪を必ず併合する。", "×", "死の結果の二重評価を避け、過失致死は殺人既遂に吸収させる。"),
            ("答案では、投棄行為の過失致死該当性に一言触れて吸収処理を示すと丁寧である。", "○", "小さな論点だが落とすと締まりが悪くなる。"),
            ("吸収処理は、殺人既遂の因果関係を肯定したことと整合する。", "○", "一連の危険の現実化として一罪処理する。"),
        ],
    },
]


RX_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$code $name</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@500;600;700;800&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Serif+JP:wght@400;500;700&family=Source+Code+Pro:wght@500;600;700&family=M+PLUS+1p:wght@500;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --font-body:"Zen Kaku Gothic Antique","Hiragino Sans","Yu Gothic Medium","Noto Sans JP",sans-serif;
  --font-display:"Shippori Mincho B1","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif;
  --font-quote:"Noto Serif JP","Yu Mincho","Hiragino Mincho ProN",serif;
  --font-statute:"Noto Serif JP","Yu Mincho","Hiragino Mincho ProN",serif;
  --font-keyword:"M PLUS 1p","Yu Gothic",sans-serif;
  --font-judgment:"Noto Serif JP","Yu Mincho",serif;
  --font-note:"Zen Maru Gothic","Yu Gothic",sans-serif;
  --font-soft:"Zen Maru Gothic","Yu Gothic",sans-serif;
  --font-mono:"Source Code Pro","Consolas","Menlo",monospace;
  --accent:#6b4f78;--mid:#8f739b;--base:#f7f1e9;--paper:#fffdfb;--line:#d9c7d8;
  --text:#2f2933;--soft:#f0e5f1;--green:#e8f3df;--blue:#e3eff6;--pink:#f8e3ec;
  --norm-bg:#fff7a8;--norm-border:#e8c400;--norm-text:#5a4012;
}
*{box-sizing:border-box}
body{margin:0;padding:22px 12px 64px;background:var(--base);color:var(--text);font-family:var(--font-body);font-size:16px;font-weight:500;line-height:1.9;letter-spacing:.02em}
.card{max-width:920px;margin:0 auto;background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:34px 30px 38px;box-shadow:0 14px 34px rgba(80,55,90,.14)}
h1{font-family:var(--font-display);font-size:1.72rem;line-height:1.45;margin:0 0 8px;color:var(--accent);letter-spacing:.04em}
.src{font-family:var(--font-note);font-size:.82rem;color:#706879;margin:0 0 22px;letter-spacing:.06em}
h2{font-family:var(--font-keyword);font-size:.88rem;letter-spacing:.14em;width:fit-content;margin:28px 0 0 16px;padding:5px 14px;border-radius:7px;background:var(--mid);color:white;position:relative;z-index:2}
.lead,.norm-group,.reason,.refs,.quiz-group,ol.pattern{border-radius:12px;margin:0 0 12px;padding:25px 19px 16px;border:1px solid var(--line);box-shadow:inset 0 1px 0 rgba(255,255,255,.65)}
.lead{background:var(--blue);font-family:var(--font-quote)}
.reason{background:var(--green)}
.norm-group{background:#fffbe0;border-color:var(--norm-border)}
.norm-box{background:#fff7a8;border:2px solid var(--norm-border);color:var(--norm-text);border-radius:12px;padding:16px 18px;font-family:var(--font-statute)}
.norm-box span.head{display:inline-block;font-family:var(--font-mono);font-weight:700;background:#ffe66a;border-radius:999px;padding:2px 10px;margin-bottom:8px}
.norm-box .cite{display:block;margin-top:10px;font-family:var(--font-note);font-size:.84rem;color:#765918}
ol.pattern{background:#f1ebf6;counter-reset:item;list-style:none}
ol.pattern li{counter-increment:item;margin:.55em 0;padding-left:2.4em;position:relative}
ol.pattern li::before{content:counter(item);position:absolute;left:0;top:.2em;width:1.65em;height:1.65em;line-height:1.65em;text-align:center;border-radius:50%;background:var(--accent);color:#fff;font-family:var(--font-mono);font-weight:700}
.refs{background:#fff3df;font-family:var(--font-quote)}
.refs p{text-indent:0;margin:.4em 0}.refs b{display:inline-block;min-width:3.5em;color:#8b5a2b}
.quiz-group{background:var(--pink)}
.self-check-quiz{background:#fff;border:1px solid #e7b9cf;border-radius:11px;padding:15px 16px;margin:12px 0}
.quiz-question{font-weight:700;margin:.2em 0 12px;text-indent:0}
.quiz-buttons{display:flex;gap:10px}.quiz-btn{flex:1;border:2px solid #b9cee4;background:#e7f1fa;color:#385f83;border-radius:9px;padding:11px 0;font-family:var(--font-mono);font-weight:700;font-size:1.15rem;cursor:pointer}
.quiz-result{display:none;margin-top:12px;padding:10px 12px;border-radius:8px;background:#f7f2fb}
.footer-date{font-family:var(--font-mono);font-size:.78rem;color:#81748a;margin-top:26px}
@media(max-width:640px){.card{padding:24px 17px}h1{font-size:1.42rem}.quiz-buttons{gap:8px}}
</style>
</head>
<body>
<div class="card">
<h1>$name</h1>
<p class="src">出典: $long_title / $code</p>
<h2>問題の所在</h2>
<div class="lead"><p>$lead</p></div>
<h2>規範（暗記対象）</h2>
<div class="norm-group"><div class="norm-box"><span class="head">Rule</span><p>$norm</p><span class="cite">$cite</span></div></div>
<h2>理由づけ</h2>
<div class="reason"><p>$reason</p></div>
<h2>あてはめの型</h2>
<ol class="pattern">
$apply
</ol>
<h2>関連判例・条文</h2>
<div class="refs">
<p><b>条文</b><span>$refs</span></p>
<p><b>判例</b><span>$case</span></p>
</div>
<h2>規範チェック</h2>
<div class="quiz-group">
$quizzes
</div>
<p class="footer-date lexia-genmeta" style="text-align:center" data-generated="$stamp_iso">Generated: $stamp_text / RX AXIOM v2.8</p>
</div>
<script>
function lexiaAnswer(btn,val){
  var quiz=btn.closest('.self-check-quiz');
  var correct=quiz.getAttribute('data-correct-value');
  var expl=quiz.getAttribute('data-explanation')||'';
  var res=quiz.querySelector('.quiz-result');
  var ok=(val===correct);
  quiz.querySelectorAll('.quiz-btn').forEach(function(b){b.disabled=true;});
  btn.classList.add('sel');
  res.style.display='block';
  res.textContent=(ok?'◎ 正解':'× 不正解')+'（正答：'+correct+'） '+expl;
}
</script>
</body>
</html>
""")


def render_quiz(question: str, correct: str, explanation: str, recall: bool = False, rx: str = "") -> str:
    attrs = 'class="self-check-quiz"'
    if recall:
        attrs = 'class="self-check-quiz recall ex" data-arena="1" data-recall="1"'
        if rx:
            attrs += f' data-rx="{e(rx)}"'
    else:
        attrs = 'class="self-check-quiz" data-arena="1"'
    attrs += f' data-correct-value="{e(correct)}" data-explanation="{e(explanation)}"'
    return f"""<div {attrs}>
  <p class="quiz-question">{e(question)}</p>
  <div class="quiz-buttons">
    <button class="quiz-btn" data-value="○" onclick="lexiaAnswer(this,'○')">○</button>
    <button class="quiz-btn" data-value="×" onclick="lexiaAnswer(this,'×')">×</button>
  </div>
  <div class="quiz-answer">{e(explanation)}</div>
  <div class="quiz-result"></div>
</div>"""


def render_rx_files() -> None:
    out_dir = ROOT / "outputs" / "ux" / "002_RX" / SUBJECT_DIR / BASE_CODE
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, topic in enumerate(RX_TOPICS, 1):
        code = f"{RX_BASE}_{idx}"
        apply_items = "\n".join(f"<li>{e(item)}</li>" for item in topic["apply"])
        quizzes = "\n".join(render_quiz(q, c, a) for q, c, a in topic["quizzes"])
        html = RX_TEMPLATE.substitute(
            code=e(code),
            name=e(topic["name"]),
            long_title=e(LONG_TITLE),
            lead=e(topic["lead"]),
            norm=e(topic["norm"]),
            cite=e(topic["cite"]),
            reason=e(topic["reason"]),
            apply=apply_items,
            refs=e(topic["refs"]),
            case=e(topic["case"]),
            quizzes=quizzes,
            stamp_iso=STAMP_ISO,
            stamp_text=STAMP_TEXT,
        )
        (out_dir / f"{code}.html").write_text(html, encoding="utf-8", newline="\n")


TREE_CSS = """
:root{--paper:#f4edd8;--ink:#1f1b16;--soft:#4a4338;--rule:#c8b894;--ox:#6b2436;--sage:#5a6b4a;--clay:#8b5a3c;--gold:#9c7c2d;--leaf:#f9f4e8;--f-jp:'Noto Serif JP','Yu Mincho',serif;--f-body:'Crimson Pro','Noto Serif JP',serif;--f-it:'Cormorant Garamond','Noto Serif JP',serif}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--f-body);font-size:14.5px;line-height:1.85;letter-spacing:.03em}
.topbar{position:sticky;top:0;z-index:4;background:rgba(244,237,216,.94);border-bottom:1px solid var(--rule);padding:14px 26px;display:flex;gap:18px;align-items:baseline;flex-wrap:wrap}.topbar-vol{font-family:var(--f-it);font-style:italic;color:var(--ox);letter-spacing:.12em}.topbar-title{font-family:var(--f-jp);font-weight:700;font-size:18px}.topbar-stats{margin-left:auto;color:var(--soft);font-style:italic}
.mm-canvas{width:100%;overflow-x:auto;padding:48px 0 80px}.mindmap{display:flex;align-items:flex-start;width:max-content;min-width:100%;padding:0 30px}.mm-root{position:sticky;left:22px;top:86px;flex:0 0 250px;background:var(--ox);color:#f4edd8;border-radius:8px;padding:28px 24px;box-shadow:0 16px 38px rgba(80,30,45,.28)}.mm-root-title{font-family:var(--f-jp);font-size:25px;line-height:1.22;font-weight:700}.mm-root-en{font-family:var(--f-it);font-style:italic;opacity:.72;margin-top:10px}
.mm-trunk{display:flex;gap:0;align-items:flex-start}.mm-branch{display:grid;grid-template-columns:230px 360px;gap:34px;min-height:160px;margin:0 0 16px 52px;position:relative}.mm-branch::before{content:'';position:absolute;left:-52px;top:31px;width:52px;height:1px;background:var(--rule)}.mm-trunk-node{height:max-content;border-radius:7px;padding:13px 15px;background:#e8d4d8;color:var(--ox);box-shadow:0 3px 12px rgba(31,27,22,.08)}.mm-name{font-family:var(--f-jp);font-weight:700;font-size:14.5px;letter-spacing:.08em}.mm-name-en{display:block;font-family:var(--f-it);font-style:italic;font-size:11px;opacity:.68;margin-top:2px}.mm-leaves{display:flex;flex-direction:column;gap:8px;position:relative}.mm-leaves::before{content:'';position:absolute;left:-17px;top:18px;bottom:18px;width:1px;background:var(--rule)}
.mm-leaf{position:relative}.mm-leaf::before{content:'';position:absolute;left:-17px;top:18px;width:17px;height:1px;background:var(--rule)}.mm-leaf>summary{list-style:none;cursor:pointer;background:var(--leaf);border:1px solid rgba(31,27,22,.13);border-radius:6px;padding:9px 12px;display:flex;align-items:center;gap:8px}.mm-leaf>summary::-webkit-details-marker{display:none}.mm-leaf-name{font-family:var(--f-jp);font-weight:700}.mm-leaf-sub{display:block;color:var(--soft);font-size:12px}.mm-leaf-chev{margin-left:auto;color:var(--ox)}.mm-leaf-chev::before{content:'+'}.mm-leaf[open] .mm-leaf-chev{transform:rotate(45deg)}.mm-leaf-body{background:rgba(255,253,247,.75);border-left:3px solid var(--ox);border-radius:0 0 6px 6px;margin:0 8px 4px;padding:10px 13px;color:var(--soft)}.mm-leaf-body .norm{background:#fff7d0;border:1px solid #d9c274;border-radius:5px;padding:8px 10px;color:#5f4615}.mm-q{margin-top:8px;background:#eef5e8;border:1px solid #b8caa6;border-radius:5px;padding:6px 9px;color:#3d4a30;font-family:var(--f-jp);font-size:12.5px}
.mm-c2 .mm-trunk-node,.mm-c5 .mm-trunk-node,.mm-c10 .mm-trunk-node{background:#e0cbb8;color:var(--clay)}.mm-c3 .mm-trunk-node,.mm-c8 .mm-trunk-node,.mm-c13 .mm-trunk-node{background:#c5cfb4;color:#3d4a30}.mm-c4 .mm-trunk-node,.mm-c9 .mm-trunk-node{background:#d4b0b8;color:var(--ox)}.mm-c6 .mm-trunk-node,.mm-c11 .mm-trunk-node,.mm-c12 .mm-trunk-node{background:#e8dcb4;color:#6b5530}.foot{max-width:980px;margin:18px auto 42px;color:var(--soft);padding:0 24px}.lexia-genmeta{text-align:center;font-family:monospace;font-size:12px;color:#756b60}
@media(max-width:760px){.mm-root{position:relative;left:auto;top:auto}.mindmap{padding:0 16px}.mm-branch{grid-template-columns:210px 330px;margin-left:34px}.topbar-stats{margin-left:0}}
"""


TREE_BRANCHES = [
    ("事案構造", "case architecture", ["二段階行為", "計画と現実", "甲乙の鏡像", "設問順序"]),
    ("小問(1)入口", "first count", ["強盗殺人の誘い", "相続目的", "殺人罪への切替", "客観構成要件"]),
    ("財産上の利益", "benefit", ["具体性", "直接性", "相続手続", "結論否定"]),
    ("実行の着手", "attempt threshold", ["密接性", "危険性", "三要素", "クロロホルム射程"]),
    ("甲の故意", "mens rea", ["一連の認識", "因果関係の錯誤", "法定的符合", "殺人既遂"]),
    ("甲の結論", "conclusion A", ["強盗殺人なし", "殺人既遂", "未遂過失説排斥", "答案配点"]),
    ("小問(2)入口", "second count", ["絞首行為", "投棄行為", "客観面先行", "砂末吸引"]),
    ("因果関係", "causation", ["危険の現実化", "介在事情", "非異常性", "寄与度"]),
    ("概括的故意", "dolus generalis", ["認識と現実", "因果経過のズレ", "故意阻却なし", "同一結果"]),
    ("過失致死吸収", "absorption", ["投棄の評価", "一個の死", "二重評価回避", "殺人一罪"]),
    ("判例対応", "authorities", ["クロロホルム", "砂末吸引", "大阪南港", "相続利益"]),
    ("答案順序", "writing order", ["甲から乙へ", "規範短く", "あてはめ厚く", "結論明示"]),
    ("失点回避", "risk control", ["相続を成立させない", "因果と故意を分ける", "吸収を忘れない", "判例名を添える"]),
]


def render_tree() -> None:
    branch_html = []
    for bi, (name, en, leaves) in enumerate(TREE_BRANCHES, 1):
        leaf_html = []
        for li, leaf in enumerate(leaves, 1):
            point = (
                f"{name}の枝では「{leaf}」を、答案上の処理順序と結論に結び付けて確認する。"
                "本問は二段階行為と因果経過の食い違いを扱うため、客観面と主観面を混ぜずに配置することが重要である。"
            )
            norm = (
                "規範は短く、あてはめは事実語で厚く書く。甲では着手の三要素、乙では危険の現実化の三視点を使い、"
                "最後に因果関係の錯誤が故意を阻却しないと結論へ接続する。"
            )
            q = f"Q. {leaf}を答案で落とすと、どの構成要件要素または罪数処理が不安定になるか。"
            leaf_html.append(f"""<details class="mm-leaf">
  <summary><span><span class="mm-leaf-name">{e(leaf)}</span><span class="mm-leaf-sub">{e(name)} / node {bi}-{li}</span></span><span class="mm-leaf-chev"></span></summary>
  <div class="mm-leaf-body"><p>{e(point)}</p><p class="norm">{e(norm)}</p><div class="mm-q">{e(q)}</div></div>
</details>""")
        branch_html.append(f"""<section class="mm-branch mm-c{bi}">
  <div class="mm-trunk-node"><span class="mm-name">{e(name)}</span><span class="mm-name-en">{e(en)}</span></div>
  <div class="mm-leaves">
{chr(10).join(leaf_html)}
  </div>
</section>""")
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>刑JX019 早すぎた・遅すぎた構成要件の実現 — 横向き樹形図 / ARBOR v5.0</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=Crimson+Pro:wght@400;500;600&family=Noto+Serif+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>{TREE_CSS}</style>
</head>
<body>
<div class="topbar"><div class="topbar-vol">刑JX019 <em>ARBOR</em></div><div class="topbar-title">早すぎた・遅すぎた構成要件の実現</div><div class="topbar-stats">13 branches / 52 leaves / 52 questions</div></div>
<main class="mm-canvas">
<div class="mindmap">
<section class="mm-root"><div class="mm-root-title">刑JX019<br>因果経過の食い違い</div><div class="mm-root-en">early and late realization of actus reus</div></section>
<div class="mm-trunk">
<div>
{chr(10).join(branch_html)}
</div>
</div>
</div>
</main>
<div class="foot">
<p>甲は「予定より前」に結果が発生したため、実行の着手を前倒しして一連の殺人行為と評価する。乙は「予定より後」に結果が発生したため、危険の現実化で因果関係を肯定し、因果関係の錯誤を故意阻却なしで処理する。</p>
<p class="lexia-genmeta" data-generated="{STAMP_ISO}">Generated: {STAMP_TEXT} / ARBOR v5.0</p>
</div>
</body>
</html>
"""
    out = ROOT / "outputs" / "ux" / "003_TREE" / SUBJECT_DIR / f"{BASE_CODE}_TREE.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")


ARIADNE_CSS = """
/* ARIADNE JX019 / MA-ROLE-RESTYLE / KP-PUZZLE-BACKFILL */
:root{--a-base:#f7f1e9;--a-head:#7d607f;--a-foot:#463a50;--li:#7d607f;--line:rgba(70,58,80,.18);--paper:#fffdfb;--card:#fff;--ink:#2b2330;--soft:#6e6370;--shu:#b44f3b;--ai:#5e8e91;--gr:#5fa565;--gd:#a17a1c;--f-disp:"Shippori Mincho B1","Noto Serif JP",serif;--f-body:"Zen Kaku Gothic Antique","Yu Gothic",sans-serif;--f-soft:"Zen Maru Gothic","Yu Gothic",sans-serif;--f-code:"Source Code Pro",monospace;--maxw:1040px}
*{box-sizing:border-box}body{margin:0;background:var(--a-base);color:var(--ink);font-family:var(--f-body);font-size:16px;line-height:1.9;font-weight:500;letter-spacing:.03em}.wrap{max-width:var(--maxw);margin:0 auto;padding:0 12px 76px}.masthead{background:linear-gradient(135deg,#a387a8,var(--a-head),var(--a-foot));color:#fff;border-radius:0 0 18px 18px;padding:23px 24px 18px;margin:0 -12px 24px;box-shadow:0 7px 20px rgba(70,58,80,.25)}.kicker{font-family:var(--f-code);font-size:.72rem;letter-spacing:.2em;opacity:.8}.masthead h1{font-family:var(--f-disp);font-size:1.5rem;margin:.2em 0;line-height:1.42}.sheet,.problem,.step,.bone,.rubric,.drill,.bc-wrap,.deep-body,.model-answer{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:16px 0;box-shadow:0 3px 12px rgba(80,60,80,.07)}.sec-h{margin:32px 0 12px}.sec-h .kick{font-family:var(--f-code);font-size:.72rem;letter-spacing:.16em;color:var(--a-head)}.sec-h .ttl{font-family:var(--f-disp);font-size:1.28rem;color:var(--a-head);font-weight:800}.problem{border-left:6px solid var(--shu)}.problem .pq{font-family:var(--f-disp);line-height:2.05;text-indent:1em}.steps-rail{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 16px}.steps-rail span{border:1px solid #c7aed1;background:#fff;border-radius:9px;padding:4px 10px;font-family:var(--f-soft);font-weight:700;color:#534260}.step{position:relative;overflow:hidden}.step::before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;background:var(--li)}.step .hd{display:flex;gap:12px;align-items:center}.step .num{font-family:var(--f-code);font-weight:700;color:var(--a-head);border:1px solid #c7aed1;border-radius:9px;padding:7px 10px;background:#f0e5f1}.step .ttl{font-family:var(--f-disp);font-weight:800;color:var(--a-head)}.step .do{text-indent:1em}.peek{background:#fffdf6;border:1px solid #ecd99a;border-radius:10px;padding:9px 12px}.peek summary{cursor:pointer;font-weight:800;color:#6d5314}.bone{background:#fbf7ef}.bone .iss{display:inline-block;border:1px solid #c7aed1;border-radius:999px;padding:3px 10px;margin:3px;background:#efe3f0;color:#534260;font-weight:700}.self-check-quiz{background:#fff;border:1px solid #e6c1d1;border-radius:11px;padding:14px 15px;margin:12px 0}.quiz-question{font-weight:700;margin:.1em 0 10px;text-indent:0}.quiz-buttons{display:flex;gap:10px}.quiz-btn{flex:1;border:2px solid #aecadd;background:#eef7fb;border-radius:9px;padding:10px 0;font-family:var(--f-code);font-weight:700;cursor:pointer}.quiz-answer{margin-top:10px;background:#f7f2fb;border-radius:8px;padding:8px 10px;color:#51465b}.quiz-result{display:none;margin-top:10px}.bc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}.bc-col{background:#f8f2fb;border:1px solid #d8c9df;border-radius:10px;padding:12px}.bc-col h4{margin:.1em 0;color:var(--a-head)}.reveal-answer summary,#deep-dive summary{cursor:pointer;font-family:var(--f-soft);font-weight:800;color:var(--a-head);background:#efe3f0;border-radius:10px;padding:11px 14px}.model-answer{font-family:var(--f-disp);font-size:.97rem}.model-answer .ma-h{font-weight:800;color:#fff;background:linear-gradient(135deg,var(--a-head),var(--a-foot));border-radius:8px;padding:5px 12px;display:inline-block}.model-answer p.role{position:relative;border:1px solid #e2d5e7;border-left:6px solid var(--cd,#7d607f);border-radius:10px;padding:10px 12px 10px 42px;background:#fff;margin:10px 0}.model-answer p.role::before{content:attr(data-role);position:absolute;left:9px;top:10px;font-family:var(--f-code);font-size:.7rem;color:var(--cd,#7d607f);font-weight:800}.r-issue{--cd:#b44f3b}.r-norm{--cd:#a17a1c}.r-apply{--cd:#5e8e91}.r-concl{--cd:#5b6fa8}.fact{background:linear-gradient(transparent 56%,#f2cfc8 56%);font-weight:700}.eval{background:linear-gradient(transparent 56%,#d6e8bf 56%);font-weight:700}.deep-body{background:#fffdf8}.statute-card,.case-card{border:1px solid #d9c274;border-radius:10px;background:#fff8d8;padding:12px 14px;margin:10px 0}.case-card{background:#eef5e8;border-color:#b8caa6}.go-athena{display:inline-block;background:linear-gradient(135deg,var(--a-head),var(--a-foot));color:#fff;text-decoration:none;border-radius:999px;padding:9px 18px;font-weight:800}.foot{color:#fff;background:var(--a-foot);border-radius:14px;padding:16px 18px;margin:20px 0}.footer-date{font-family:var(--f-code);font-size:.78rem;text-align:center;opacity:.78}.rubric table{width:100%;border-collapse:collapse}.rubric td,.rubric th{border:1px solid #ddd0e2;padding:8px;vertical-align:top}.rubric th{background:#efe3f0;color:#534260}
@media(max-width:640px){.masthead h1{font-size:1.24rem}.sheet,.problem,.step,.bone,.rubric,.drill,.bc-wrap,.deep-body,.model-answer{padding:14px 13px}.quiz-buttons{gap:7px}}
"""


RECALLS = [
    ("相続利益が2項強盗の財産上の利益に当たるため、甲には強盗殺人罪が成立する。", "×", "相続は具体的・直接的な利益ではないため、強盗殺人を否定して殺人罪へ進む。", "刑RX019_1"),
    ("甲の第1行為は第2行為を確実かつ容易にするため必要不可欠であれば、実行の着手を肯定し得る。", "○", "密接性・危険性と三要素で着手を前倒しする。", "刑RX019_2"),
    ("甲について、刺殺予定と窒息死の違いは常に殺人故意を阻却する。", "×", "構成要件の範囲内で符合すれば因果関係の錯誤は故意を阻却しない。", "刑RX019_3"),
    ("乙では、自己の投棄行為が介在するため、まず危険の現実化による因果関係を検討する。", "○", "客観面を先に処理してから因果経過の錯誤へ進む。", "刑RX019_4"),
    ("乙の認識した死因と現実の死因が異なっても、同一被害者の死亡に向かう危険が現実化すれば故意は残る。", "○", "遅すぎた構成要件の実現は因果関係の錯誤として処理する。", "刑RX019_5"),
    ("殺人既遂を認める場合、投棄行為の過失致死は同一死亡結果の二重評価を避けるため吸収される。", "○", "罪数処理で一言添えると答案が締まる。", "刑RX019_6"),
    ("甲では強盗殺人の前提検討を飛ばしても、相続目的が問題文にある以上、答案上の失点はない。", "×", "相続利益の否定は入口の重要論点であり、短くても必ず処理する。", "刑RX019_1"),
    ("乙の答案は、因果関係、因果関係の錯誤、過失致死の吸収の順に並べると読みやすい。", "○", "客観面から主観面、最後に罪数処理へ流す。", "刑RX019_4"),
]


BC_QUIZZES = [
    ("甲の答案では、強盗殺人を成立させてから殺人罪も併記するのが安全である。", "×", "相続利益を否定し、強盗殺人は不成立として殺人罪へ切り替える。"),
    ("実行の着手は、密接性と危険性を立ててから事実を三つに分けて当てはめる。", "○", "不可分性・時間場所の近接・障害事情なしを使う。"),
    ("乙では、因果関係の錯誤だけを書けば危険の現実化の検討は不要である。", "×", "まず客観面の因果関係を肯定する必要がある。"),
    ("砂上放置は発覚防止の事後処分として非異常な介在と評価し得る。", "○", "投棄を含めて第1行為の危険の現実化を説明する。"),
    ("過失致死の吸収は、死の結果を二重評価しないための罪数処理である。", "○", "最後に一文で処理する。"),
]


def render_step(num: int, title: str, body: str, peek: str) -> str:
    return f"""<div class="step" id="step-{num}">
  <div class="hd"><div class="num">STEP {num}</div><div class="ttl">{e(title)}</div></div>
  <p class="do">{e(body)}</p>
  <details class="peek"><summary>能動想起の観点</summary><div class="body"><p>{e(peek)}</p></div></details>
</div>"""


def render_ariadne() -> None:
    steps = [
        ("設問を二つに割る", "小問(1)甲と小問(2)乙を混ぜず、甲は予定より前、乙は予定より後に結果が出た問題として整理する。", "時間軸のズレが逆向きであることを最初に固定する。"),
        ("甲の入口を処理する", "相続目的から2項強盗殺人を一応検討し、相続利益の具体性・直接性を否定して殺人罪へ切り替える。", "強盗殺人を長く書きすぎず、入口で確実に切る。"),
        ("甲の着手を前倒しする", "第1行為と第2行為の密接性・危険性を、必要不可欠性、時間的場所的接着性、障害事情なしで認定する。", "着手を故意の橋渡しに使うため、三要素を事実で埋める。"),
        ("甲の錯誤を故意へ接続する", "刺殺予定と窒息死のズレを因果関係の錯誤として、構成要件内の符合により故意阻却なしとまとめる。", "死因の違いを過大視せず、人の死亡という結果の符合を示す。"),
        ("乙は客観面から始める", "絞首後の投棄が介在しているため、まず危険の現実化で因果関係を肯定する。", "自己の事後行為が介在する点を主戦場にする。"),
        ("乙の錯誤と罪数を処理する", "頸部圧迫死の認識と砂末吸引死の現実を因果関係の錯誤で処理し、過失致死は殺人既遂に吸収させる。", "最後の吸収を落とさない。"),
        ("結論を対称に締める", "甲も乙も殺人既遂罪。ただし甲は着手、乙は因果関係が山であると答案上の厚みに差をつける。", "同じ結論でも理由付けの山を取り違えない。"),
    ]
    step_html = "\n".join(render_step(i, *step) for i, step in enumerate(steps, 1))
    recall_html = "\n".join(render_quiz(q, c, a, recall=True, rx=rx) for q, c, a, rx in RECALLS)
    bc_quiz_html = "\n".join(render_quiz(q, c, a, recall=False) for q, c, a in BC_QUIZZES)
    bc_cols = "\n".join(
        f'<div class="bc-col"><h4>{e(title)}</h4><p>{e(text)}</p></div>'
        for title, text in [
            ("入口", "強盗殺人の誘いを短く処理し、殺人罪へ進む道筋を作る。"),
            ("規範", "着手・危険の現実化・錯誤の規範を分けて立てる。"),
            ("事実", "距離、時間、投棄目的など評価を支える事実語を拾う。"),
            ("評価", "密接性、非異常性、符合という評価語へ変換する。"),
            ("結論", "甲乙とも殺人既遂、過失致死は吸収で締める。"),
        ]
    )
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>刑JX019 解法ナビ｜早すぎた・遅すぎた構成要件の実現 — ARIADNE</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@500;600;700;800&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Serif+JP:wght@400;500;700&family=Source+Code+Pro:wght@500;600;700&display=swap" rel="stylesheet">
<style>{ARIADNE_CSS}</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <div class="kicker">ARIADNE / {BASE_CODE}</div>
  <h1>早すぎた・遅すぎた構成要件の実現</h1>
  <p>殺人罪の答案で、甲の「着手」と乙の「因果関係」を取り違えないための解法ナビ。</p>
</header>

<section class="sheet">
  <div class="sec-h"><div class="kick">CASE</div><div class="ttl">問題文の骨格</div></div>
  <div class="problem">
    <p class="pq">甲はAを殺害して相続により全財産を得ようとし、Aを意識喪失させてトランクに閉じ込め、山中で殺害する計画を進めた。しかしAは予定現場到着前に、猿ぐつわ等により窒息死していた。</p>
    <p class="pq">乙はBを殺そうとして首を絞め、死亡したと誤信して発覚防止のため砂上に放置した。実際にはBはなお生存しており、その後砂末吸引で窒息死した。</p>
  </div>

  <div class="sec-h"><div class="kick">BONE</div><div class="ttl">答案骨子</div></div>
  <div class="bone" data-kp="KP-PUZZLE-BACKFILL">
    <p><span class="iss">【論点】相続利益</span><span class="iss">【論点】実行の着手</span><span class="iss">【論点】因果関係の錯誤</span><span class="iss">【論点】危険の現実化</span><span class="iss">【論点】過失致死の吸収</span></p>
    <ol>
      <li>甲は、2項強盗殺人を入口で否定し、殺人罪に進む。</li>
      <li>第1行為時点の実行の着手を、密接性・危険性で肯定する。</li>
      <li>甲の因果経過のズレは故意を阻却しない。</li>
      <li>乙は、自己の投棄行為の介在を危険の現実化で処理する。</li>
      <li>乙の因果関係の錯誤は故意を阻却せず、過失致死は吸収される。</li>
    </ol>
  </div>

  <div class="sec-h"><div class="kick">NAVIGATION</div><div class="ttl">解法ナビ</div></div>
  <div class="steps-rail"><span>1 分割</span><span>2 入口</span><span>3 着手</span><span>4 錯誤</span><span>5 因果</span><span>6 吸収</span><span class="goal">7 結論</span></div>
  {step_html}

  <div class="drill">
    <div class="sec-h"><div class="kick">RECALL</div><div class="ttl">周回ドリル</div></div>
    {recall_html}
  </div>

  <div class="bc-wrap">
    <div class="sec-h"><div class="kick">COMPOSITION</div><div class="ttl">答案構成の作法</div></div>
    <div class="bc-grid">{bc_cols}</div>
    {bc_quiz_html}
  </div>

  <div class="rubric">
    <div class="sec-h"><div class="kick">RUBRIC</div><div class="ttl">自己採点チェック</div></div>
    <table><tr><th>観点</th><th>A答案の目印</th></tr><tr><td>甲</td><td>相続利益否定、着手三要素、故意への橋渡しがある。</td></tr><tr><td>乙</td><td>危険の現実化、因果関係の錯誤、過失致死吸収が順に並ぶ。</td></tr></table>
  </div>

  <details class="reveal-answer">
    <summary>模範答案を開く</summary>
    <div class="model-answer">
      <p class="ma-h">第1　甲の罪責</p>
      <p class="role r-issue" data-role="問"><b>1</b>　甲は相続によりAの全財産を得る目的でAを殺害しようとしているため、まず2項強盗殺人罪の前提として、相続による利益が「財産上……の利益」に当たるかが問題となる。</p>
      <p class="role r-norm" data-role="規"><b>2</b>　同利益は、1項強盗との均衡から、財物の占有移転と同視できる程度に<span class="eval">具体的・直接的</span>な利益を現実に取得したといえるものを要する。</p>
      <p class="role r-apply" data-role="当"><b>3</b>　相続は死亡により当然に開始するとはいえ、権利関係の確定を介する包括承継であり、甲が暴行により<span class="fact">Aの個別財産を直接取得</span>するものではない。よって2項強盗は成立せず、強盗殺人罪は成立しない。</p>
      <p class="role r-issue" data-role="問"><b>4</b>　次に殺人罪について、甲は山中で殺害する予定であったのに、第1行為でAが死亡しているため、第1行為時点の実行の着手と故意が問題となる。</p>
      <p class="role r-norm" data-role="規"><b>5</b>　実行の着手は、構成要件該当行為への密接性と結果発生の現実的危険性から判断し、計画上の不可分性、時間的場所的接着性、障害事情の有無を考慮する。</p>
      <p class="role r-apply" data-role="当"><b>6</b>　強打、猿ぐつわ、トランク閉込めは山中での殺害を確実かつ容易にするため必要不可欠であり、移動は約5km・約10分で、特段の障害もない。したがって第1行為開始時点で殺人の実行の着手がある。</p>
      <p class="role r-concl" data-role="結"><b>7</b>　刺殺予定と窒息死のズレはあるが、A死亡という構成要件の範囲内で符合するため故意は阻却されず、甲には殺人既遂罪が成立する。</p>
      <p class="ma-h">第2　乙の罪責</p>
      <p class="role r-issue" data-role="問"><b>1</b>　乙は殺意をもってBの首を絞めており、絞首行為は殺人の実行行為である。もっとも死亡は砂上放置後の砂末吸引により生じているため、因果関係が問題となる。</p>
      <p class="role r-norm" data-role="規"><b>2</b>　因果関係は、行為が内包する危険が結果として現実化したかにより判断し、介在事情の異常性や寄与度を考慮する。</p>
      <p class="role r-apply" data-role="当"><b>3</b>　麻縄で力いっぱい首を絞める行為は死の高度の危険を有し、発覚防止のため砂上に放置することは殺害後の事後処分として異常とはいえない。よって絞首行為の危険が投棄を介して現実化した。</p>
      <p class="role r-concl" data-role="結"><b>4</b>　乙の認識した頸部圧迫死と現実の砂末吸引死の違いは因果関係の錯誤にとどまり、故意を阻却しない。投棄行為の過失致死的評価は死亡結果の二重評価を避けるため殺人既遂罪に吸収される。</p>
    </div>
  </details>

  <details id="deep-dive">
    <summary>深掘り層を開く</summary>
    <div class="deep-body">
      <div class="statute-card"><h4>条文</h4><p>刑法38条1項、43条本文、199条、210条、236条2項、240条後段。答案では、条文を羅列せず、どの構成要件要素で使うかを対応させる。</p></div>
      <div class="case-card"><h4>判例</h4><p>クロロホルム事件は甲の着手前倒し、砂末吸引事件は乙の遅すぎた構成要件の実現、東京高判平成元年2月27日は相続利益否定の支柱となる。</p></div>
      <a class="go-athena" role="button" tabindex="0" data-athena-code="刑JX019" data-athena-href="../../../001_JX/001_刑法/刑JX019.html">アテナで詳しく</a>
    </div>
  </details>
</section>

<div class="foot">
<p>甲は着手、乙は因果関係。鏡像の二問を同じ語で混ぜず、答案上の山を分ければ安定して書ける。</p>
<p class="footer-date lexia-genmeta" data-generated="{STAMP_ISO}">Generated: {STAMP_TEXT} / ARIADNE v0.3</p>
</div>
</div>
<script>
document.addEventListener('click',function(ev){{
  var btn=ev.target.closest('.quiz-btn');
  if(!btn){{return;}}
  var quiz=btn.closest('.self-check-quiz');
  var correct=quiz.getAttribute('data-correct-value');
  var ok=btn.getAttribute('data-value')===correct;
  var res=quiz.querySelector('.quiz-result');
  quiz.querySelectorAll('.quiz-btn').forEach(function(b){{b.disabled=true;}});
  res.style.display='block';
  res.textContent=(ok?'◎ 正解':'× 不正解')+'（正答：'+correct+'） '+(quiz.getAttribute('data-explanation')||'');
}});
document.querySelectorAll('.go-athena').forEach(function(ga){{
  ga.addEventListener('click',function(ev){{
    ev.preventDefault();
    var code=ga.getAttribute('data-athena-code')||'';
    var href=ga.getAttribute('data-athena-href')||'';
    if(window.parent){{window.parent.postMessage({{type:'lexia:navigate',code:code,href:href}},'*');}}
  }});
}});
</script>
</body>
</html>
"""
    out = ROOT / "outputs" / "ux" / "001_ARIADNE" / SUBJECT_DIR / f"{BASE_CODE}_ARIADNE.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")


def main() -> None:
    render_rx_files()
    render_tree()
    render_ariadne()


if __name__ == "__main__":
    main()
