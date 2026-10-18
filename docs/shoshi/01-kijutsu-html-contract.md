# 記述式 HTML 契約（HX ひな形カード／KX 記述式過去問）v0.1

> 確定日 2026-10-18。`00-master-plan.md` §3 の正典順位 2 位。
> **この文書を変えるときは、shoshi-exam 側 validator（`validate-hx.py`／`validate-kx.py`）と Lexia 側
> 抽出器・トラッカー枝を同じ PR 群で変える**（検出ゲートと生成ツールは同一式）。

---

## 0. 前提＝Lexia がどう読むか（変えない部分）

Lexia（SCRIBA ビルドも同じコア）は問題 HTML を `srcDoc` iframe で表示し、**親が注入するトラッカー**
（`QUIZ_TRACKER_SCRIPT`）が DOM の既知セレクタを監視して `postMessage({source:'lexia-quiz', type:'lexia:quiz',
kind, quizId, isCorrect, userAnswer, prompt})` を送る。親 `recordQuizAttempt` は `kind ∈ {comp, arena, stmt, card}`
だけを復習プール対象にし、**誤答だけ** を `questionId + '#' + quizId` で SM-2 に載せる。

| 既存契約 | DOM | kind / quizId | 司法書士版での使い方 |
|---|---|---|---|
| TX `_lex` 肢単位 | `.answer-area[data-answer-type="ox-grid"] .ox-row[data-stmt]`＋正誤表 `[data-answer-key]` | `stmt` / `stmt-{記述}` | **TX にそのまま流用**（変更なし） |
| ARIADNE 想起カード | `.self-check-quiz.recall[data-arena="1"][data-recall="1"][data-correct-value="○"]`＋`.quiz-question`＋`button.recall-reveal`＋`.quiz-answer`＋`.quiz-btns.recall-grade > .quiz-btn[data-value="○|×"]` | `arena` / `sc_{位置}` | **HX ひな形カードの本体**（§1） |
| （新設） | `.kx-app .kx-field` | `kxfield` / `kx-{申請番号}-{欄キー}` | **KX 申請書フォームの欄**（§2-5・§2-9） |

共通規律（bar-exam から継承・そのまま適用）：

- 一問一答の面は **自己完結**（原文ポインタ・裸の見解ラベル・事例が身分を与えた記号の禁止＝G79/G80 の趣旨）。
- 設問・別紙は **原文不可侵**（要約・言い換え・編集注記混入の禁止＝§v13r/§v13s）。解答前に見える場所へ正解を書かない。
- 折りたたみは **display のみで DOM 温存**（Lexia 抽出・validate の DOM 走査を壊さない）。
- `<script>` 内に `</body>` リテラルを書かない。`<table>` を一問一答の面に使わない。
- フォント 12 変数・配色 5 役割は TX と共通（`check-font-vars.py` を流用）。

---

## 1. HX ひな形カード（記述式の部品層）

### 1-1. 単位と命名

- **1 ファイル＝1 登記類型**（例：所有権移転（売買）／所有権移転（相続）／抵当権設定／役員変更／本店移転）。
- ファイル名 `{科目接頭辞}HX{NNN}.html`、出力先 `outputs/001_HX/{00N_科目}/`（科目は 010_不動産登記法／011_商業登記法。供託は後日）。
- 複製起点＝**`canonical/STYLUS.html`**（GENESIS-CARD の誌面＋ARIADNE 想起エンジンを逐語継承）。問題固有スロット以外は編集しない（placeholder 契約を別途置く）。

### 1-2. 構成

```
<header>  登記類型名・科目・ID（表紙）
<section id="hx-form">        ひな形本文（申請書全文＝読む用・プール対象外）
  .hx-form-sheet  欄ごとの表組みを div グリッドで（登記の目的／原因日付／申請人／添付情報／課税価格・登録免許税）
  .hx-form-note   注記（省略可の添付・記載の揺れ・先例の根拠）
<section id="hx-cards">       想起カード（プール対象・2〜5枚・効くものだけ）
  .self-check-quiz.recall[data-arena="1"][data-recall="1"][data-correct-value="○"][data-qid="hx-01"]
    .quiz-question   【想起】…を挙げよ／…はどう書くか／…はいくらか
    button.recall-reveal
    .quiz-answer     模範（欄の完全文）＋根拠（条文・先例）
    .quiz-btns.recall-grade > .quiz-btn[data-value="○"]書けた / [data-value="×"]書けなかった
<details id="deep-dive">      深掘り（なぜその添付か・似た類型との差・先例）
<footer>  lexia-genmeta（生成日時・版）
```

### 1-3. 想起カードの規律

- **問いの型は 5 種に限定**：①添付情報を全部挙げよ ②登記の目的・登記原因及びその日付の書き方 ③登録免許税（課税価格→税額） ④申請人欄の書き方（権利者・義務者・申請人・代理人） ⑤登記すべき事項（商登）。1 類型で **効く問いだけ** を置く（偽ドリル禁止）。
- `.quiz-question` に答えを含めない（添付情報の列挙・税額は `.quiz-answer` にだけ書く）。
- `.quiz-answer` は **欄の完全文**で書く（略記禁止・そのまま答案に書ける形）。根拠は末尾に 1 行（法令名＋条・先例の年月日と番号）。
- **安定キー `data-qid="hx-NN"`**（ファイル内で一意・連番・**追記のみ／並べ替え禁止**）。Lexia Phase 1 で `data-qid` を quizId に採用する（無ければ従来の位置キー＝互換）。
- 1 枚に 1 問い。複数欄をまとめて問わない（部分点の単位＝SM-2 の単位）。
- `data-rx` は使わない（RX は司法書士版に無い）。代わりに KX からの逆参照 `data-hx="{HX ID}#hx-NN"` を受ける（§2-7）。

### 1-4. validator `validate-hx.py`（H1〜H9・すべて ERROR）

| ID | 検査 |
|---|---|
| H1 | §1-2 の構造（`#hx-form`／`#hx-cards`／`#deep-dive`／footer）が揃う |
| H2 | 想起カードの DOM 契約（§0 表）が逐語で揃い、`data-correct-value="○"` |
| H3 | `data-qid` が `hx-NN` 形式・一意・文書順に連番 |
| H4 | `.quiz-answer` 非空・`.quiz-question` 非空・問いが 5 型のいずれか（先頭語で判定） |
| H5 | ネタバレ禁止＝`.quiz-question` の本文に `.quiz-answer` の添付情報名・税額が現れない |
| H6 | `#hx-form` の欄見出しが規定集合（不登／商登で別表） |
| H7 | 根拠の法令名明記（「不動産登記法」「不動産登記令」「不動産登記規則」「商業登記法」「商業登記規則」「会社法」「登録免許税法」または先例の「昭和/平成/令和 n.n.n 民三/民商 第n号」形式） |
| H8 | フォント 12 変数・配色（`check-font-vars.py` 流用） |
| H9 | `<script>` 内 `</body>` リテラル禁止・`<table>` 禁止（カード面） |

---

## 2. KX 記述式過去問（1問1HTML・前半コア／後半 deep）

### 2-1. 単位と命名

- **1 ファイル＝記述式 1 問**（年度×科目）。ファイル名 `{科目接頭辞}KX{NNN}.html`、出力先 `outputs/002_KX/{010_不動産登記法|011_商業登記法}/`。番号↔年度の対応表＝`docs/kx-index.md`（shoshi-exam 側）。
- 複製起点＝**`canonical/THOTH.html`**。HTML は手で書かず **`scripts/kx-build.py apply <file> --spec <json>`** が問題固有スロットを JSON 仕様から組む（§2-10）。

### 2-2. 構成（物理順序＝固定）

```
<header>                 年度・科目・ID・目安時間（data-minutes）
<section id="kx-problem">        問題文・別紙＝原文不可侵
  .kx-original-lead               設問文（逐語）
  .kx-exhibit[data-exhibit="別紙1"]  登記記録／議事録／事実関係／聴取記録（逐語・div グリッド。登記記録の甲区乙区は .kx-reg-row）
  .kx-instruction                  操作指示（編集注記＝原文と混ぜない別段落）
<details class="tx-intro">       解く前の🔰導入（任意・§v16 同型・既定閉）
<section id="kx-draft">          下書き（ARIADNE .drafting 同型）
  .rel-map（当事者図）／.timeline（時系列）／.facts（拾う事実：引用＋なぜ拾うか）
  ＝ネタバレ禁止（申請名・添付情報・結論を書かない。「生の事実抽出」まで）
<section id="kx-plan">           申請一覧パズル（§2-4）
<section id="kx-forms">          申請書フォーム採点（§2-5）＝申請ごとに 1 フォーム
<section id="kx-verdict">        採点表（§2-6）
<details class="reveal-answer">  模範答案（申請書の完成形・全申請）＋出題の要点
<details id="deep-dive">         深掘り：論点解説・先例・条文・似た類型との差・HX リンク（§2-7）
<footer>                         lexia-genmeta
```

- 前半コア（problem〜verdict）は **周回の主戦場**。deep と模範答案は既定で閉じる（DOM 温存）。
- 周回モード `.wrap[data-loop="1|2|3"]`（ARIADNE v1.5.0 の 3 ブロックを逐語継承）：1周目＝フル／2周目＝下書き・導入を伏せる／3周目＝問題＋パズル＋フォームだけ。

### 2-3. 原文不可侵（別紙）

- `#kx-problem` 配下は PDF 原文の逐語。登記記録・議事録の表は **div グリッド**で再現（`<table>` 禁止）。
- 編集語（「ここでは」「本問は」「を素材に」等）は bar-exam G19 の語彙をそのまま流用して ERROR。
- 解答前に見える領域（problem／intro／draft／plan のチップ面）に正解（申請の件数・順序・添付情報・税額）を書かない。

### 2-4. 申請一覧パズル（`#kx-plan`）

判断の型＝「どの登記を何件、どの順で申請するか」を能動想起で組む。ARIADNE 骨子パズル（`.bone`＋`data-kp-decoys`＋3段階 Lv）のエンジンを **逐語継承**し、タグの意味だけ次のとおり写像する：

| ARIADNE | KX での意味 | 例 |
|---|---|---|
| `.b1`（見出し） | 申請の順序 | `1件目`／`2件目`／`申請できない` |
| `.iss`（論点） | 登記の目的 | `所有権移転`／`抵当権抹消`／`役員変更` |
| `.krule`（規範） | 登記原因 | `売買`／`相続`／`辞任` |
| `.kfact`（事実） | 申請人の型 | `権利者乙・義務者甲`／`申請人 株式会社A` |
| `<u>`（結論） | 可否・特記 | `申請できない（理由：…）` |

- おとり `data-kp-decoys` は **似て非なる申請**（所有権移転↔所有権更正、抹消↔変更、就任↔重任 等）を 4〜6 枚。
- Lv1＝目的だけ／Lv2＝＋原因＋申請人／Lv3＝＋順序＋可否。
- 申請の件数＝`#kx-forms` のフォーム数と一致（K2）。

### 2-5. 申請書フォーム採点（`#kx-forms`）

申請 1 件＝`form.kx-app[data-app="N"][data-kind="不登|商登"]`。欄＝`fieldset.kx-field`。**正解は欄ごとに属性で持ち、採点は HTML 内エンジンが決定論で行う**（LLM 不使用）。

```html
<form class="kx-app" data-app="2" data-kind="不登">
  <fieldset class="kx-field" data-qid="kx-2-mokuteki" data-field="目的"
            data-norm="exact" data-answer="所有権移転" data-points="4">
  <fieldset class="kx-field" data-qid="kx-2-genin" data-field="原因日付"
            data-norm="date-cause" data-answer="令和6年4月1日売買" data-points="4">
  <fieldset class="kx-field" data-qid="kx-2-shinseinin" data-field="申請人"
            data-norm="set" data-answer-json='{"権利者":["乙"],"義務者":["甲"]}' data-points="4">
  <fieldset class="kx-field" data-qid="kx-2-tempu" data-field="添付情報"
            data-norm="set" data-answer-json='["登記識別情報","登記原因証明情報","印鑑証明情報","住所証明情報","代理権限証明情報"]'
            data-decoys-json='["戸籍謄本","評価証明書"]' data-points="6">
  <fieldset class="kx-field" data-qid="kx-2-zei" data-field="登録免許税"
            data-norm="number" data-answer="200000" data-formula="課税価格1,000万円×20/1000" data-points="3">
</form>
```

欄キー（`data-qid` の末尾・ASCII 固定）：

| 欄キー | 欄 | 不登 | 商登 | 既定 norm |
|---|---|---|---|---|
| `mokuteki` | 登記の目的／登記の事由 | ◯ | ◯ | exact |
| `genin` | 登記原因及びその日付 | ◯ | — | date-cause |
| `shinseinin` | 申請人（権利者・義務者・申請人・代理人） | ◯ | — | set |
| `tempu` | 添付情報／添付書面 | ◯ | ◯ | set |
| `zei` | 登録免許税（課税価格を含む） | ◯ | ◯ | number |
| `jiko` | 登記すべき事項 | — | ◯ | lines |
| `fuka` | 登記できない事項とその理由 | （申請できない登記で使用） | ◯ | self |

`data-norm`（採点規則・単一情報源は Lexia 側 `src/lib/kxNormalize.js` と shoshi-exam 側 `scripts/kx_norm.py` の **同一仕様・同一テストベクタ**）：

| norm | 入力 UI | 正規化と判定 |
|---|---|---|
| `exact` | テキスト | 全角半角・空白・括弧種を正規化して完全一致。別名表（§2-5-bis）で同義を吸収 |
| `date-cause` | 日付（年号/年/月/日）＋原因語 | 和暦を正規化（令和6年4月1日＝R6.4.1）して「日付＋原因語」の一致。原因語は別名表 |
| `set` | チップ複数選択（候補＝正解∪おとり∪共通候補） | 順不同の集合一致。過不足は欄ごと不正解（部分点はつけない＝記述式の採点実務に合わせる） |
| `number` | 数値 | 円・カンマ・全角を除いて整数一致 |
| `lines` | 複数行テキスト | 行ごとに exact を適用し、全行一致で正解（登記すべき事項） |
| `self` | 自由記述＋模範表示＋チェックリスト `.kx-rubric li` | 決定論採点しない。利用者が rubric を見て「書けた／書けなかった」を押す（想起カードと同じ自己採点） |

採点後、エンジンは **DOM に状態を書く**（トラッカーが読む単一情報源）：

- `form.kx-app` に `graded`
- 各 `fieldset.kx-field` に `is-correct` または `is-incorrect`、`data-user="<利用者入力の正規化文字列>"`
- `.kx-field` 内 `.kx-field-prompt`（問いの自己完結文＝「甲から乙への売買による所有権移転登記。添付情報を全部挙げよ」）と `.kx-field-answer`（模範の完全文）を **常に DOM に持つ**（採点前は display で伏せる）。プールの復習カードはこの 2 つから組む（§2-9）。

#### 2-5-bis. 別名表（`references/kx-aliases.json`）

同義表記の吸収（例：「登記識別情報」＝「登記識別情報（甲のもの）」／「印鑑証明書」＝「印鑑証明情報」／「住所証明情報」＝「住民票の写し」）。**別名表は shoshi-exam が単一情報源**で、Lexia は取込時に `references/kx-aliases.json` を読む（`references/` は既に同期対象）。

### 2-6. 採点表（`#kx-verdict`）

TX 正誤表と同型の役割：フォームごとに **欄・配点・あなた・正解・ズレの一言** を div グリッドで出す。配点 `data-points` の合計＝70（K9・不登／商登とも）。配点は公表されないため **目安**として付け、`.kx-verdict-note` に「配点は目安」を固定文で出す。

### 2-7. deep と HX リンク

- `#deep-dive` に論点解説・先例・条文・似た類型との差。**先例の新規引用は一次確認済みのものだけ**（年月日・番号を書く）。
- 各フォームの欄から対応ひな形へ `data-hx="{HX ID}#hx-NN"` を貼る（任意・K10 で corpus 内の存在を検査）。外した欄の復習は HX の想起カードへ誘導する。

### 2-8. タイマー

`header .kx-timer[data-minutes="35"]`（目安時間＝問題固有スロット）。経過表示だけで評価に使わない。

### 2-9. SM-2 キーとトラッカー枝（Lexia 側 Phase 2b）

- 新 kind **`kxfield`**。quizId＝`fieldset.kx-field[data-qid]`（例 `kx-2-tempu`）。親のキー＝`{問題ID}#kx-2-tempu`。
- トラッカー枝：`.kx-app` を監視し、`graded` が付いた時点で各 `.kx-field` の `is-correct|is-incorrect` を読んで送る（ox-grid 枝と同じ「answered で一括送信・二重送信防止」）。`__lexiaPeek`／`__lexiaRestoring` のゲートは `send()` が共通で効く。
- `recordQuizAttempt` の対象 kind に `kxfield` を追加（誤答だけプール）。
- **プールのカード面**＝想起型 UI（答えを見る→書けた／書けなかった）。`prompt`＝`.kx-field-prompt`、`answer`＝`.kx-field-answer`。`norm=self` の欄は rubric も添える。
- 回答履歴の復元（LXA_FEAT_014）は **Phase 2b では対象外**（KX はフォーム入力なので○×スナップショットの型が合わない。後日 `data-user` を保存する別型で検討）。

### 2-10. JSON 仕様（`kx-build.py` の入力・問題固有スロットだけ）

```json
{
  "id": "不登KX001", "subject": "010_不動産登記法", "year": "R06", "minutes": 35,
  "problem": { "lead": "…逐語…", "exhibits": [{"title":"別紙1","kind":"登記記録","rows":[…]}], "instruction": "…" },
  "draft": { "parties": [...], "timeline": [...], "facts": [{"quote":"…","why":"…"}] },
  "plan": { "items": [{"order":1,"mokuteki":"所有権移転","genin":"売買","party":"権利者乙・義務者甲"}, …],
            "decoys": ["所有権更正", "抵当権変更"] , "cannot": [{"mokuteki":"…","reason":"…"}] },
  "apps": [ { "n":1, "kind":"不登", "fields":[ {"key":"mokuteki","norm":"exact","answer":"所有権移転","points":4,
              "prompt":"…自己完結の問い…","hx":"不登HX003#hx-02"}, … ] } ],
  "verdict_note": "配点は目安",
  "deep": { "sections": [...], "precedents": [{"date":"昭和39.4.6","no":"民三第1291号","gist":"…","verified":"2026-10-18 裁判所/法務局資料"}] },
  "current_law_note": { "checked":"2026-10-18", "old":"…", "now":"…", "exam_note":"…" }
}
```

`kx-build.py` は **全スロット被覆・配点合計 70・plan 件数＝apps 件数・qid 一意** を満たさないと 1 字も書かない（bar-exam `tx-gist-story.py` と同じ流儀）。`extract` で生成済み HTML→JSON、`check` で構造検査。

### 2-11. validator `validate-kx.py`（K1〜K12）

| ID | 検査 | 重さ |
|---|---|---|
| K1 | §2-2 の物理順序と必須 id が揃う／deep・模範答案が `details` で既定閉 | ERROR |
| K2 | `#kx-plan` の申請件数（`.b1` の件数見出し）＝`form.kx-app` の数 | ERROR |
| K3 | 各 `.kx-field` に `data-qid`/`data-field`/`data-norm`/正解属性/`data-points`/`.kx-field-prompt`/`.kx-field-answer` が揃い、norm が既知集合 | ERROR |
| K4 | `set` の JSON 妥当・おとりと正解の非重複・候補 3 枚以上 | ERROR |
| K5 | `data-qid` が `kx-{n}-{欄キー}` 形式で一意、n がフォーム番号と一致 | ERROR |
| K6 | 原文不可侵：`#kx-problem` に編集語（G19 語彙）なし・解答前領域に正解語（申請名・添付情報名・税額）なし | ERROR |
| K7 | 周回モード 3 ブロック（CSS 区画・UI・JS）が正典と一致・`data-loop="1"` 既定 | ERROR |
| K8 | 現行法ノート：年度が直近の大改正（相続登記義務化 2024-04／住所等変更登記義務化 2026-04／会社法改正）より前の問題は `.kx-current-law-note` 必須 | ERROR |
| K9 | `data-points` 合計＝70 | ERROR |
| K10 | `data-hx` の参照先が corpus に存在（横断） | WARNING |
| K11 | 下書き `#kx-draft` に申請名・添付情報名・結論が現れない（ネタバレ） | ERROR |
| K12 | フォント 12 変数・`</body>` リテラル・`<table>` | ERROR |

---

## 3. Lexia 側の変更一覧（コアに入れる・bar ビルドでは不活性）

| Phase | 変更 | 影響 |
|---|---|---|
| 1 | `data-qid` を `extractQuizzesFromHtml` の id と トラッカー `ensureQuizId` の両方で最優先（無ければ従来の位置キー） | bar の既存 HTML は `data-qid` を持たないので挙動不変 |
| 1 | 試験プロファイル（`src/lib/examProfile.js`）＝科目表・接頭辞正規表現・取込元・カテゴリ・機能フラグ・保存域名 | bar の値は現状と同一 |
| 2b | トラッカー `kx` 枝＋`recordQuizAttempt` の `kxfield`＋プールの想起型カード面（prompt/answer を DOM から） | shoshi のみ有効（`features.kx`） |
| 2b | `src/lib/kxNormalize.js`（§2-5 の norm・別名表読込・テストベクタ）＝HTML 内エンジンと同一仕様 | shoshi のみ |
| 2b | カテゴリ `HX`/`KX` の検出・ライブラリ表示・科目カード | shoshi のみ |

---

## 4. 禁止事項（この契約に固有）

- ひな形カードの `.quiz-question` に答え（添付情報の列挙・税額）を書くこと。
- `set` 欄に部分点をつけること（過不足＝不正解で固定。採点実務に合わせる）。
- 別紙を `<table>` で組むこと／要約すること。
- `self` 以外の欄を LLM で採点すること。
- `data-qid` の振り直し・並べ替え（SM-2 キーの孤児化＝bar-exam `docs/lexia-tx-statement-tracking.md` と同じ事故）。
- 先例を一次確認なしに引くこと（年月日・番号を欠く先例は K 系では書けない＝JSON の `verified` 必須）。
