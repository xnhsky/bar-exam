from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(r"C:\Users\xnrg2.DESKTOP-5664QR6\bar-exam")
ARI_DIR = ROOT / "outputs" / "ux" / "001_ARIADNE" / "001_刑法"
RX_DIR = ROOT / "outputs" / "ux" / "002_RX" / "001_刑法"


RX_SPECS = {
    "刑RX001_4": {
        "jx": "刑JX001",
        "title": "不真正不作為犯における作為義務の発生根拠",
        "issue": "不作為犯では、単に結果を防げたというだけで処罰できない。法令上の義務がない場合に、どの事情から作為義務を基礎づけるかが答案の入口になる。",
        "norm": "作為義務は、法令・契約・事務管理・先行行為・排他的支配の設定などから、結果回避を期待できる法的地位があるかを総合して判断する。法令上の義務がなくても、被害者の生命身体を事実上排他的に支配し、保護が容易である場合には、条理上の作為義務を肯定しうる。",
        "reason": "作為義務を広げすぎると不作為犯の処罰範囲が不明確になる。他方で、現実に救える者が一人しかいない場面で形式的義務だけを要求すると、生命保護を空洞化させる。そこで排他的支配と作為容易性で限定する。",
        "apply": "本問では、Yに親権はない。しかし、生後3か月のAが道路から見えないY宅勝手口付近に置かれ、Yがすぐに気付いた以上、保護できるのは事実上Yだけである。病院搬送も容易だから、作為義務を肯定する。",
    },
    "刑RX003_4": {
        "jx": "刑JX003",
        "title": "具体的事実の錯誤における法定的符合説",
        "issue": "認識した客体・結果と現実に発生した客体・結果がずれたとき、故意をどこまで認めるかが問題となる。",
        "norm": "判例・通説は法定的符合説に立ち、認識事実と発生事実が同一構成要件の範囲内で符合すれば、故意を阻却しないと解する。構成要件をまたぐ場合には抽象的事実の錯誤として別途処理する。",
        "reason": "故意責任は、行為者が当該構成要件的事実を認識して危険を引き受けたことに基礎を置く。同一構成要件内の客体差・方法差まで故意を否定すると、故意責任の範囲を不当に狭める。",
        "apply": "答案では、まず同一構成要件内のずれかを確認する。人を殺す意思で別人を死亡させた場合には、殺人罪の構成要件内で符合するから、殺人の故意は残る。",
    },
    "刑RX004_4": {
        "jx": "刑JX004",
        "title": "故意の定義と構成要件該当事実の認識",
        "issue": "故意の有無は、行為者が何を知っていたかを構成要件単位で確認する作業である。",
        "norm": "故意とは、構成要件に該当する事実の認識・認容をいう。重い罪の構成要件事実を認識していない場合、重い罪の故意は認められず、刑法38条2項により重い罪として処断することはできない。",
        "reason": "故意犯として重く処罰するには、行為者がその重い構成要件的危険を認識していたことが必要である。知らない重い事実について故意責任を負わせるのは責任主義に反する。",
        "apply": "答案では、客観的に重い罪が実現していても、主観面でその重い構成要件事実を認識していたかを先に見る。認識が軽い罪にとどまるなら、38条2項の処理へ進む。",
    },
    "刑RX005_4": {
        "jx": "刑JX005",
        "title": "介在事情判例の対比と危険の現実化",
        "issue": "行為後に被害者や第三者の行為が介在したとき、最初の行為と結果との因果関係をどこまで肯定するかが問題となる。",
        "norm": "介在事情がある場合でも、実行行為に含まれる危険が、介在事情を経てもなお結果へ現実化したといえるときは因果関係を肯定する。判断では、介在事情の異常性、結果への寄与度、行為時に内在していた危険との関係を比較する。",
        "reason": "条件関係だけでは広すぎ、予見可能性だけでは答案が抽象化しやすい。危険の現実化という軸で、行為が作り出した危険が結果へどうつながったかを評価する。",
        "apply": "本問では、介在事情の有無だけで切らず、最初の危険が結果へ流れ込んだかを判例と対比して示す。対比判例は、異常な介在か、危険の延長かを説明する材料になる。",
    },
    "刑RX014_4": {
        "jx": "刑JX014",
        "title": "結果的加重犯における基本犯と重い結果の結び付き",
        "issue": "結果的加重犯では、基本犯があるだけで重い結果まで当然に帰責できるわけではない。",
        "norm": "結果的加重犯が成立するには、基本犯の実行行為に内在する危険が重い結果として現実化したことが必要である。基本犯と重い結果との間には、危険の現実化として説明できる因果的結び付きが要る。",
        "reason": "重い結果について過失まで常に要するかは争いがあるが、少なくとも基本犯の危険と無関係な結果まで加重処罰することはできない。",
        "apply": "答案では、傷害行為の危険が死亡結果へどう流れたかを、介在事情の性質とあわせて評価する。単に傷害後に死亡した、という時系列だけでは足りない。",
    },
    "刑RX019_7": {
        "jx": "刑JX019",
        "title": "相続目的の前提検討と強盗殺人の入口処理",
        "issue": "相続目的が問題文に出ているとき、強盗殺人を立てるか、入口で否定して殺人へ進むかが答案構成を分ける。",
        "norm": "2項強盗の「財産上不法の利益」は、具体的・直接的な財産上の利益であることを要する。相続期待のような抽象的・間接的利益は、原則としてこれに当たらない。",
        "reason": "強盗罪は財産犯であり、暴行脅迫によって直接取得される財産的利益を処罰対象にする。相続のような将来・不確定の利益まで広げると処罰範囲が不明確になる。",
        "apply": "答案では、相続目的を見た瞬間に強盗殺人を検討し、相続利益の具体性・直接性を否定して殺人罪へ切り替える。ここを飛ばすと、出題意図を拾っていない答案に見える。",
    },
    "刑RX019_8": {
        "jx": "刑JX019",
        "title": "乙の答案配列と因果関係・錯誤・罪数の処理順",
        "issue": "乙の答案では、因果関係、因果関係の錯誤、過失致死の吸収をどの順番で置くかが読みやすさを左右する。",
        "norm": "まず客観面として因果関係を危険の現実化で検討し、その後、認識した因果経過と現実の因果経過のずれを因果関係の錯誤として処理する。最後に、同一死亡結果の二重評価を避けるため罪数処理を一文で締める。",
        "reason": "主観面の錯誤から入ると、そもそも客観的帰責があるのかが不明になる。客観面、主観面、罪数の順に並べると、採点者が追いやすい。",
        "apply": "乙では、投棄行為を介した死亡について危険の現実化を先に肯定し、死因のずれが故意を阻却しないことを述べ、過失致死は殺人既遂に吸収されると締める。",
    },
    "刑RX033_4": {
        "jx": "刑JX033",
        "title": "名誉毀損罪における公然性",
        "issue": "名誉毀損罪の公然性は、多数人が現に認識したかではなく、認識し得る状態に置かれたかで判断する。",
        "norm": "230条1項の「公然」とは、不特定または多数人が認識し得る状態をいう。特定少数者への伝達でも、そこから不特定または多数人へ伝播する可能性がある場合には、公然性を肯定し得る。",
        "reason": "名誉は社会的評価であり、評価低下の危険が社会へ広がり得る状態に置かれれば保護法益への危険が生じる。",
        "apply": "答案では、伝達相手の人数だけでなく、不特定多数へ広がる可能性を具体的事情から評価する。秘密保持が期待できる関係かどうかも重要な切断点になる。",
    },
    "刑RX034_5": {
        "jx": "刑JX034",
        "title": "偽計と隠避の基本定義",
        "issue": "偽計業務妨害罪と犯人隠避罪は、条文上の行為概念を短く正確に置けるかが入口になる。",
        "norm": "偽計とは、人を欺罔し、誘惑し、または錯誤・不知を利用するなど、人の判断を誤らせる不正な計略をいう。隠避とは、蔵匿以外の方法により、官憲による犯人の発見・逮捕を困難にする一切の行為をいう。",
        "reason": "両罪とも抽象的な保護法益を持つため、定義を置かずにあてはめると、どの行為を処罰しているのかがぼやける。",
        "apply": "答案では、まず偽計と隠避の定義を短く示し、そのうえで、公務・業務該当性や犯人自身による教唆の可罰性などの論点へ進む。",
    },
    "刑RX037_3": {
        "jx": "刑JX037",
        "title": "防衛行為の一体性判断",
        "issue": "複数の反撃行為があるとき、一個の防衛行為としてまとめて評価するか、別個の行為として分けるかが問題となる。",
        "norm": "複数の行為が時間的・場所的に接着し、侵害の継続性や行為者の防衛意思の連続性が認められる場合には、一個の防衛行為として評価し得る。反対に、侵害が終了し、攻撃意思へ転化している場合は分断する。",
        "reason": "正当防衛は急迫不正の侵害に対する反撃を許す制度であり、侵害と防衛の対応関係が失われた後の加害行為まで正当化できない。",
        "apply": "答案では、時間・場所・侵害継続・意思の連続性を並べる。単に複数回殴ったという回数ではなく、侵害に対応する一連の行為かを評価する。",
    },
    "刑RX038_5": {
        "jx": "刑JX038",
        "title": "事後強盗罪の三目的",
        "issue": "事後強盗罪は、窃盗後の暴行脅迫なら常に成立するわけではなく、条文上の目的が必要である。",
        "norm": "238条の事後強盗罪は、窃盗犯人が、財物を得てこれを取り返されることを防ぎ、逮捕を免れ、または罪跡を隠滅する目的で、暴行又は脅迫をした場合に成立する。",
        "reason": "事後強盗罪は、窃盗後の暴行脅迫を強盗と同視する重い犯罪であるため、窃盗と暴行脅迫を結び付ける目的によって処罰範囲を限定する。",
        "apply": "答案では、目的を三つ列挙したうえで、本問の暴行脅迫がどの目的に向けられているかを具体的事実から一つに絞る。",
    },
    "刑RX039_3": {
        "jx": "刑JX039",
        "title": "窃盗罪の主観的要件としての不法領得の意思",
        "issue": "窃盗罪では、故意だけで足りるか、それとも不法領得の意思が必要かが問題となる。",
        "norm": "判例・通説は、窃盗罪の成立に故意のほか不法領得の意思を必要とする。不法領得の意思とは、権利者を排除して他人の物を自己の所有物と同様に利用・処分する意思をいう。",
        "reason": "不法領得の意思は、一時使用や毀棄・隠匿目的の取得と窃盗を区別する機能を持つ。財物奪取を財産犯として処罰するための主観的限定である。",
        "apply": "答案では、権利者排除意思と利用処分意思の二要素に分けて、単なる一時使用にとどまるか、所有者の支配を排除する意思があるかを評価する。",
    },
    "刑RX042_4": {
        "jx": "刑JX042",
        "title": "強盗罪の暴行・脅迫の程度",
        "issue": "強盗罪の暴行・脅迫は、財物交付に影響しただけでは足りず、反抗抑圧に足りる程度であることを要する。",
        "norm": "強盗罪の暴行又は脅迫は、相手方の反抗を抑圧するに足りる程度のものであることを要する。その程度は、暴行脅迫の態様、被害者の年齢・性別・状況、周囲の事情を総合して客観的に判断する。",
        "reason": "強盗罪は恐喝罪より重く処罰される。両者を区別するため、単なる畏怖ではなく反抗抑圧という強度が必要になる。",
        "apply": "答案では、まず反抗抑圧基準を置き、被害者が実際に反抗できなかったかだけでなく、客観的にその程度に達していたかを評価する。",
    },
    "刑RX046_4": {
        "jx": "刑JX046",
        "title": "事後強盗予備と条件付き犯意",
        "issue": "逃走時に発見されたら脅そうという条件付きの意思で、事後強盗予備が成立するかが問題となる。",
        "norm": "予備罪に必要な犯意は、犯罪実行の現実的準備行為を基礎づける程度に具体化していれば足りる。条件付きの意思であっても、条件成就時に実行する意思が具体的で、準備行為がその実行に向けられていれば予備を肯定し得る。",
        "reason": "予備罪は実行着手前の危険を処罰する犯罪であり、確定的な実行意思だけに限ると予備処罰の趣旨を狭めすぎる。他方で、漠然とした可能性では足りない。",
        "apply": "答案では、凶器準備や逃走計画などの客観的準備と、発見時に脅す具体的意思を結び付ける。単なる心配や抽象的予定にとどまれば否定する。",
    },
    "刑RX047_4": {
        "jx": "刑JX047",
        "title": "事後強盗罪の成立要件",
        "issue": "事後強盗罪は、窃盗後の暴行脅迫を強盗として重く扱うため、主体・目的・行為・時的場所的関連を整理して書く必要がある。",
        "norm": "事後強盗罪は、窃盗犯人が、財物奪還防止・逮捕免脱・罪跡隠滅の目的で、窃盗の機会に暴行又は脅迫をした場合に成立する。暴行脅迫は反抗抑圧に足りる程度を要する。",
        "reason": "窃盗後の暴行脅迫をすべて強盗化すると重すぎるため、窃盗との密接な関連と条文上の目的で限定する。",
        "apply": "答案では、主体が窃盗犯人か、目的が三目的のどれか、暴行脅迫の程度、窃盗の機会性を順に確認する。共犯・身分論へ入る前の土台である。",
    },
    "刑RX054_5": {
        "jx": "刑JX054",
        "title": "盗品等関与罪における親族特例",
        "issue": "盗品等関与罪では、親族間の特例を誰と誰の関係で見るかが答案の切断点になる。",
        "norm": "盗品等関与罪について257条1項の親族特例を考える場合、親族関係は本犯者と被害者との間ではなく、盗品等関与行為者と被害者との間で問題となる。親族関係がなければ特例は及ばない。",
        "reason": "盗品等関与罪は、本犯後に盗品の流通・保持を助長して被害回復を困難にする独立の犯罪である。特例の主体を本犯中心に広げると、本罪の独立性が崩れる。",
        "apply": "答案では、まず盗品性を肯定し、その後、257条1項の親族関係を関与者と被害者の関係で確認する。親族関係がないなら一文で否定する。",
    },
    "刑RX055_4": {
        "jx": "刑JX055",
        "title": "横領後の横領",
        "issue": "一度横領した後、同じ物をさらに処分した場合に、後行行為を別個の横領として評価できるかが問題となる。",
        "norm": "先行行為により委託信任関係に基づく占有が完全に失われていない限り、後行の処分行為が新たに所有者の権利を侵害する場合には、別個の横領罪を認め得る。",
        "reason": "横領罪は委託信任関係を裏切って所有者の財産権を侵害する犯罪である。先行横領後も所有者に対する侵害が別個に拡大する場合、後行行為を不可罰的事後行為に吸収するだけでは評価不足になる。",
        "apply": "不動産では、抵当権設定後の売却など、処分の法的意味が異なる場合がある。答案では、既遂時期と後行処分の新たな侵害性を分けて書く。",
    },
    "刑RX056_4": {
        "jx": "刑JX056",
        "title": "業務上横領の非身分者共犯と科刑",
        "issue": "業務上占有者に非身分者が共謀加担した場合、罪名と科刑をどう分けるかが問題となる。",
        "norm": "業務上横領罪への非身分者の関与では、真正身分によって犯罪成立を連帯させる場面は65条1項で処理し、加重身分による刑の個別化は65条2項で処理する。非身分者にも横領罪の共犯成立を認めつつ、業務上身分による加重は及ばない。",
        "reason": "65条1項は身分による犯罪成立の連帯、2項は身分による科刑の個別化を定める。両者を混同すると、非身分者に過重な刑を及ぼすことになる。",
        "apply": "答案では、罪名レベルでは横領罪の共同正犯・共犯を認め、科刑レベルでは非身分者を単純横領の刑で処理する、という二段階で書く。",
    },
    "刑RX064_4": {
        "jx": "刑JX064",
        "title": "公共の危険と財産危険の限定",
        "issue": "建造物等以外放火罪では、公共の危険をどの範囲の危険として捉えるかが問題となる。",
        "norm": "公共の危険とは、不特定または多数人の生命・身体・財産に対する危険をいう。ただし危険が財産のみに及ぶ場合には、単なる個別財産の危険では足りず、不特定または多数の財産に対する危険であることを要する。",
        "reason": "放火罪は公共危険犯であり、個人の財産侵害に尽きる危険を公共の危険として扱うと、器物損壊等との区別が曖昧になる。",
        "apply": "答案では、まず危険が生命身体に及ぶか、財産にとどまるかを分ける。財産危険だけなら、不特定多数性を具体的事情で示す必要がある。",
    },
    "刑RX067_3": {
        "jx": "刑JX067",
        "title": "写真コピーの名義人確定",
        "issue": "写真コピーが文書に当たる場合、その名義人を原本作成者と見るか、コピー作成者と見るかが問題となる。",
        "norm": "写真コピーが原本と同一内容を示し、社会生活上原本と同様の信用を持つ場合、文書性を肯定し得る。その名義人は、文書の内容から表示される作成名義を基準に判断し、単なるコピー作成者ではなく原本上の作成名義人となり得る。",
        "reason": "文書偽造罪が保護するのは文書の真正に対する公共の信用である。社会が誰の意思・観念表示として受け取るかを基準にしなければ、信用侵害の実体を捉えられない。",
        "apply": "答案では、コピーの外観・用途・原本同様の信用性を確認し、そのうえで名義人を内容表示から確定する。電子データ化など後の利用態様だけで遡って決めない。",
    },
    "刑RX069_4": {
        "jx": "刑JX069",
        "title": "犯人隠避罪における隠避の意義と危険犯性",
        "issue": "犯人隠避罪では、どのような行為が隠避に当たり、現実に捜査が妨害されたことまで必要かが問題となる。",
        "norm": "隠避とは、蔵匿以外の方法により、官憲による犯人の発見・逮捕を困難にする一切の行為をいう。本罪は国家の刑事司法作用を保護する抽象的危険犯であり、現実に逮捕が不能になったことまでは要しない。",
        "reason": "刑事司法作用は、犯人の発見・逮捕が困難にされる危険が生じた時点で害される。現実の捜査失敗まで要求すると、保護が遅すぎる。",
        "apply": "答案では、身代わり出頭、虚偽説明、所在秘匿などが官憲の発見・逮捕を困難にする方向へ働くかを評価する。実際に逮捕されたかどうかだけで切らない。",
    },
}


REASSIGNMENTS = [
    ("刑JX001", "法令上の作為義務が無くても", "刑RX001_1", "刑RX001_4"),
    ("刑JX003", "法定の範囲内", "刑RX003_1", "刑RX003_4"),
    ("刑JX004", "故意（38条1項）の定義", "刑RX004_1", "刑RX004_4"),
    ("刑JX005", "対比すべき判例", "刑RX005_1", "刑RX005_4"),
    ("刑JX014", "結果的加重犯", "刑RX014_1", "刑RX014_4"),
    ("刑JX015", "偽装心中", "刑RX015_1", "刑RX015_3"),
    ("刑JX019", "強盗殺人の前提検討を飛ばしても", "刑RX019_1", "刑RX019_7"),
    ("刑JX019", "乙の答案は、因果関係", "刑RX019_4", "刑RX019_8"),
    ("刑JX033", "「公然」の定義", "刑RX033_2", "刑RX033_4"),
    ("刑JX034", "「偽計」の意義", "刑RX034_1", "刑RX034_5"),
    ("刑JX037", "防衛行為とみるか", "刑RX037_1", "刑RX037_3"),
    ("刑JX038", "3つの目的", "刑RX038_1", "刑RX038_5"),
    ("刑JX039", "明文なき要件", "刑RX039_2", "刑RX039_3"),
    ("刑JX042", "暴行又は脅迫", "刑RX042_1", "刑RX042_4"),
    ("刑JX046", "条件付きの意思", "刑RX046_3", "刑RX046_4"),
    ("刑JX047", "成立要件を、主体", "刑RX047_1", "刑RX047_4"),
    ("刑JX054", "257条1項", "刑RX054_3", "刑RX054_5"),
    ("刑JX055", "更に売却した行為", "刑RX055_1", "刑RX055_4"),
    ("刑JX056", "罪名」と「科刑", "刑RX056_2", "刑RX056_4"),
    ("刑JX064", "危険が財産のみに及ぶ", "刑RX064_1", "刑RX064_4"),
    ("刑JX067", "名義人は誰か", "刑RX067_1", "刑RX067_3"),
    ("刑JX069", "「隠避」の定義", "刑RX069_1", "刑RX069_4"),
]


STYLE = r"""
<style>
:root{--font-body:"Zen Kaku Gothic Antique","Yu Gothic",sans-serif;--font-display:"Shippori Mincho B1","Noto Serif JP",serif;--font-soft:"Zen Maru Gothic","Yu Gothic",sans-serif;--font-mono:"Source Code Pro",Consolas,monospace;--base:#FAF6EF;--paper:#fff;--text:#3a3340;--accent:#7E5F9C;--line:#e7dff0;--norm-bg:#fff7a8;--norm-border:#e8c400;--ok:#4E7536;--ng:#A84E74}
*{box-sizing:border-box}body{margin:0;padding:20px 12px 56px;background:var(--base);color:var(--text);font-family:var(--font-body);font-size:16px;line-height:1.92;letter-spacing:.02em}.card{max-width:920px;margin:0 auto;background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:34px 30px 38px;box-shadow:0 12px 34px rgba(106,77,134,.13)}h1{font-family:var(--font-display);font-size:1.62rem;line-height:1.48;color:var(--accent);margin:.1em 0 .5em;border-bottom:3px solid #C7B4E2;padding-bottom:.4em}.src{font-family:var(--font-mono);font-size:.78rem;color:#6d6478;margin:0 0 16px}.lead,.reason,.apply,.refs,.quiz-group{border-radius:12px;padding:18px 19px;margin:14px 0;border:1px solid var(--line);box-shadow:inset 0 1px 0 rgba(255,255,255,.65)}.lead{background:#DFEFF7}.reason{background:#E7F4D9}.apply{background:#EDE6F6}.refs{background:#FCEBD3}.norm-group{background:#FCF3C5;border:1.5px solid #EAD879;border-radius:12px;padding:18px 19px;margin:14px 0}.norm-box{background:var(--norm-bg);border:2px solid var(--norm-border);border-radius:11px;padding:18px 20px;font-family:var(--font-display);font-weight:700;line-height:2.02;color:#5a4012;box-shadow:inset 0 0 0 1px #fff}h2{display:inline-block;font-family:var(--font-soft);font-size:.84rem;letter-spacing:.08em;background:#C7B4E2;color:#4d3868;border-radius:7px;padding:4px 13px;margin:22px 0 2px}p{margin:.45em 0;text-indent:1em}b,strong{font-weight:800;background:linear-gradient(transparent 58%,rgba(255,226,77,.48) 58%)}.quiz-group{background:#FBE5EE;border-color:#F3B0CA}.self-check-quiz{background:#fff;border:1px solid #F3B0CA;border-radius:11px;padding:14px 15px;margin:12px 0}.quiz-question{text-indent:0;font-weight:700}.quiz-buttons{display:flex;gap:10px}.quiz-btn{flex:1;border:2px solid #A8D6E8;background:#DFEFF7;border-radius:10px;padding:11px 0;font-family:var(--font-mono);font-weight:800;cursor:pointer}.quiz-result{display:none;margin-top:10px;padding:11px 13px;border-radius:9px}.quiz-result.correct{display:block;background:#E7F4D9;border:1px solid #BFE09C}.quiz-result.wrong{display:block;background:#FBE5EE;border:1px solid #F3B0CA}.footer-date{font-family:var(--font-mono);font-size:.78rem;text-align:center;color:#6d6478;margin-top:26px}@media(max-width:640px){.card{padding:24px 16px}}
</style>
"""


SCRIPT = r"""
<script>
function lexiaAnswer(btn,val){
  var q=btn.closest('.self-check-quiz');
  var correct=q.getAttribute('data-correct-value');
  var exp=q.getAttribute('data-explanation')||'';
  q.querySelectorAll('.quiz-btn').forEach(function(b){b.disabled=true;});
  var r=q.querySelector('.quiz-result');
  var ok=val===correct;
  r.className='quiz-result '+(ok?'correct':'wrong');
  r.innerHTML='<b>'+(ok?'◎ 正解':'× 不正解')+'（正答：'+correct+'）</b><br>'+exp;
}
</script>
"""


def rx_num(code: str) -> str:
    return code.replace("刑RX", "刑JX").split("_")[0]


def render_rx(code: str, spec: dict[str, str]) -> str:
    title = html.escape(spec["title"])
    jx = spec["jx"]
    q1 = f"{spec['title']}では、まず問題の所在を示してから規範を置くべきである。"
    q2 = f"{spec['title']}は、条文・保護法益から処罰範囲を限定するための論点である。"
    q3 = "答案では、規範を長く読むより、効く事実を評価語へ変換して短く当てはめる方が重要である。"
    exp1 = "正しい。論証RXは、問題提起、規範、理由、あてはめタグを短く再装填するためのカードである。"
    exp2 = "正しい。条文文言と保護法益に戻ることで、暗記した規範を本問の事実へ接続できる。"
    exp3 = "正しい。ARIADNEへ戻って答案構成を再現するため、RXでは規範確認で止まらない。"
    return f"""<!DOCTYPE html>
<!-- AXIOM-RECANON v1.0 / data-rx duplicate split -->
<html lang="ja">
<head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@400;500;700;800&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Serif+JP:wght@400;500;700&family=Source+Code+Pro:wght@400;600;700&display=swap" rel="stylesheet">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{STYLE}
</head>
<body>
<div class="card">
<h1>{title}</h1>
<p class="src">出典: {jx} / data-rx 重複解消用 RX 論証カード</p>

<h2>問題の所在</h2>
<div class="lead"><p>{html.escape(spec["issue"])}</p></div>

<h2>規範（暗記対象）</h2>
<div class="norm-group"><div class="norm-box">{html.escape(spec["norm"])}</div></div>

<h2>理由づけ</h2>
<div class="reason"><p>{html.escape(spec["reason"])}</p></div>

<h2>あてはめタグ</h2>
<div class="apply"><p>{html.escape(spec["apply"])}</p></div>

<h2>答案フレーズ</h2>
<div class="refs"><p>答案では、<b>条文文言</b>、<b>保護法益</b>、<b>規範</b>、<b>効く事実</b>、<b>結論</b>の順に短く接続する。詰まったらこのカードで再装填し、必ず ARIADNE の答案構成へ戻る。</p></div>

<h2>規範チェック</h2>
<div class="quiz-group">
<div class="self-check-quiz" data-correct-value="○" data-explanation="{html.escape(exp1)}">
<div class="quiz-question">Q1. {html.escape(q1)}</div>
<div class="quiz-buttons"><button class="quiz-btn" data-value="○" onclick="lexiaAnswer(this,'○')">○</button><button class="quiz-btn" data-value="×" onclick="lexiaAnswer(this,'×')">×</button></div>
<div class="quiz-result"></div>
</div>
<div class="self-check-quiz" data-correct-value="○" data-explanation="{html.escape(exp2)}">
<div class="quiz-question">Q2. {html.escape(q2)}</div>
<div class="quiz-buttons"><button class="quiz-btn" data-value="○" onclick="lexiaAnswer(this,'○')">○</button><button class="quiz-btn" data-value="×" onclick="lexiaAnswer(this,'×')">×</button></div>
<div class="quiz-result"></div>
</div>
<div class="self-check-quiz" data-correct-value="○" data-explanation="{html.escape(exp3)}">
<div class="quiz-question">Q3. {html.escape(q3)}</div>
<div class="quiz-buttons"><button class="quiz-btn" data-value="○" onclick="lexiaAnswer(this,'○')">○</button><button class="quiz-btn" data-value="×" onclick="lexiaAnswer(this,'×')">×</button></div>
<div class="quiz-result"></div>
</div>
</div>
</div>
{SCRIPT}
<p class="footer-date lexia-genmeta" style="text-align:center" data-generated="2026-06-29T00:00+09:00">Generated: 2026-06-29 00:00 / RX AXIOM v1.0</p>
</body>
</html>
"""


TAG_RE = re.compile(r'<div\b[^>]*\bclass="[^"]*\bself-check-quiz\b[^"]*"[^>]*>', re.I)


def patch_ariadne(code: str, question_key: str, old_rx: str, new_rx: str) -> None:
    path = ARI_DIR / f"{code}_ARIADNE.html"
    text = path.read_text(encoding="utf-8")
    patched = False
    for m in list(TAG_RE.finditer(text)):
        tag = m.group(0)
        if f'data-rx="{old_rx}"' not in tag:
            continue
        qstart = text.find('<p class="quiz-question">', m.end())
        qend = text.find("</p>", qstart)
        if qstart == -1 or qend == -1:
            continue
        qhtml = text[qstart:qend]
        qtext = re.sub(r"<[^>]+>", "", qhtml)
        if question_key not in qtext:
            continue
        new_tag = tag.replace(f'data-rx="{old_rx}"', f'data-rx="{new_rx}"')
        text = text[:m.start()] + new_tag + text[m.end():]
        patched = True
        break
    if not patched:
        raise RuntimeError(f"対象タグが見つかりません: {code} {question_key} {old_rx}->{new_rx}")
    path.write_text(text, encoding="utf-8", newline="")


def write_rx_files() -> None:
    for code, spec in RX_SPECS.items():
        jx = spec["jx"]
        out_dir = RX_DIR / jx
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{code}.html"
        path.write_text(render_rx(code, spec), encoding="utf-8", newline="")


def main() -> None:
    write_rx_files()
    for args in REASSIGNMENTS:
        patch_ariadne(*args)
    print(f"created_rx={len(RX_SPECS)} reassigned={len(REASSIGNMENTS)}")


if __name__ == "__main__":
    main()
