# ARIADNE v0.1 — JX 解法ナビ＋周回 正典（骨子）

> 初学者（白紙で論文に手が付かない）向けの「解法ナビ＋周回」専用 JX 正典。
> 現 JX 正典 **ATHENA**（百科事典型）はそのまま。ARIADNE はそれと**役割分担**する別系統。
> コードネーム＝アリアドネの糸（白紙の迷宮を抜ける解法導線）。

---

## 0. 役割分担

| | ATHENA（既存） | ARIADNE（本spec） |
|---|---|---|
| 目的 | 知識の事典（条文/判例/学説/論証の網羅） | **「次に何をするか」の解法手順＋答案構成までの高速周回** |
| 起点 | `canonical/ATHENA.html` | `canonical/ARIADNE.html`（v0.3 誌面風・刑JX001 で実証） |
| 生成元 | 問題PDF＋逐語 | **検証済み JX（ATHENA HTML）から蒸留**（RX/TREE と同じ副産物パターン） |
| Lexia | 問題本体 | 別ID の周回教材（メイン JX と衝突しない） |

---

## 1. 配置・命名（2026-06-18 確定）

```
outputs/ux/000_ARIADNE/{00N_科目}/{科目}JX{NNN}_ARIADNE.html
```
- 科目フォルダは jx-deploy の `$Map` と同名：`001_刑法 / 002_刑事訴訟法 / 003_民法 / 004_商法 / 005_民事訴訟法 / 006_行政法 / 007_憲法`。
- 命名は TREE（`{科目}JX{NNN}_TREE.html`）に倣い **`{元問題ID}_ARIADNE`**＝例 `刑JX001_ARIADNE.html`。
- メイン `刑JX001.html` と**別ファイル名**＝Lexia 上で別 question（questionId はファイル名由来）。

---

## 2. 構造（誌面・上から下が学習導線）

1. **マストヘッド**（難易度別ベースカラー・§5）：キッカー＋大明朝タイトル＋シール＋虹罫。
2. **問題文**（`.problem`）＋登場人物（`.cast`・被害者/救助者は対象外マーク）＋講師プルクオート（`.pull`）。
3. **解法ナビ**（`.steps-rail` ＋ `.step`×7）＝後述の7手。各手「▶自分で一手→開いて確認（`details.peek`）」＋周回ドリル○×。
4. **骨子**（`.skeleton > .bone`）＝ゴール（答案構成）。**1周目はここを白紙再現できればクリア**。
5. **照合・自己採点**（`.collate > .rubric`）＝採点講評由来の減点ポイントを☐で自己採点（**AI採点に非依存**）。
6. **模範答案**（`details.reveal-answer > .model-answer`）＝既定クローズ。書き切ってから開く。
7. **深掘り層**（`details#deep-dive`）＝規範の中身・判例射程・条文（薄く）。1周目は開かない。百科事典版は ATHENA へ誘導。

---

## 3. 解法7手の型（刑法「罪責を論ぜよ」型・全問共通の転用可能スパイン）

| 手 | コード | 中身 |
|---|---|---|
| 手1 | **SCAN** | 登場人物を全員出し、各人の「引っかかる行為」を時系列で拾い、作為/不作為タグ。被害者・救助者は対象外に切る |
| 手2 | **AIM** | 各行為に罪名のアタリ。手がかり＝①結果（生命/身体…）②主観の文言（殺意の有無 等） |
| 手3 | **ORDER** | 重い罪・事案の中核を負う者から。理由を一言 |
| 手4 | **MARCH** | 犯罪論で流す（構成要件該当性→違法性→責任→未遂なら着手）。**素直に通す石**は一文／**立ち止まる石＝論点**だけ厚く |
| 手5 | **BREAK** | 各論点を ①問題の所在 ②規範（名前）③あてはめ（効く事実＋評価語）④結論 の4点セットで。複数人物は `手5′` で再演 |
| 手6 | **BRIDGE** | 複数人なら共犯（60条等）へ一言 |
| 手7 | **BUILD** | 番号＋見出し＋結論一行の骨子に落とす＝答案構成（GOAL🏁） |

- 科目で型は変わるが「人物→行為→罪名→体系で流す→論点を割る→横断→骨子」の骨格は共通。
- 用語（不真正不作為犯・排他的支配・移置・未必の故意 等）は**コア層に1行の超短定義**を併記（初学者が deep を開かず1周できるよう二重定義可）。

---

## 4. 周回○×（Lexia 復習プール契約・最重要）

各「周回ドリル ○×」は **`.self-check-quiz`** で実装し、Lexia の SM-2 復習プールに乗せる。

- **`data-arena="1"` 必須**：App.jsx:2803 で復習プール投入は `kind∈{comp,arena,stmt}` のみ。素の self-check は除外＝周回不能。`data-arena` で `kind=arena`。
- **`data-correct-value="○"` or `"×"`**：正解（Lexia が抽出）。
- **`.quiz-question`**（設問）／**`.quiz-answer`**（解説・非空）。
- **`.quiz-btn[data-value="○"/"×"]`** 2個。クリックで正解ボタンに `correct-mark`／他に `incorrect-mark`（末尾JS）。正誤は **data-correct-value 一本**で判定（button の data-correct は使わない）。
- **自己完結が鉄則**：設問は**本問の前提なしで解ける一般原則／【例題】**にする（復習プールで孤立表示されても解ける）。本問固有の状況依存設問にしない。
- **卒業＝別日2回正解**（correctSessions≥2）・誤答で巻き戻し。
- **件数 10〜15枚**／手ごとに 1〜複数。能動想起（▶問い→自力→開く）も併用。
- **禁止**：設問文を Lexia のメタ除去 regex `(本問|本設問)[0-20字]正解｜正解は肢｜正解はどれ｜正解の組` に当てない（当たると削除）。

---

## 5. 配色・フォント（誌面・2026-06-18 改訂：TX v11 を見本に統一・恒久）

> **【最重要・恒久】配色とフォントは TX v11 GENESIS（V3 Twilight Violet・刑TX327）を見本に統一**した
> （旧 ATHENA プラム＋マイルドライナー固定配色は廃止）。`canonical/ARIADNE.html` に実装済みで、
> 複製（§6）すれば自動継承する。設計の元ファイル＝`outputs/ux/000_ARIADNE/001_刑法/刑JX001_ARIADNE.html`。
> 既存生成物への一括反映は `scripts/ariadne-restyle-backfill.py`（冪等）。

- **フォント＝TX 12 役割と同ファミリー**（`canonical/GENESIS-CORE.html` と同系）：
  - `--f-disp`＝**Shippori Mincho B1**（大見出し・問題文・模範・規範＝法律文）
  - `--f-body`＝**Zen Kaku Gothic Antique**（本文・解説・UI／字間 .04em・line-height 1.9）
  - `--f-soft`＝**Zen Maru Gothic**（ナビ・ラベル・小見出し・バッジ・サマリー）
  - `--f-code`＝**Source Code Pro**（英コードネーム SCAN〜BUILD・キッカー）／`--f-mono`＝Source Code Pro（骨子）
- **★ ベースカラー＝難易度別に染色選定（TX P1/P2/P3 と同方針）。** `:root` の「▼ ACTIVE」プリセット
  （フレーム `--a-base/--a-head/--a-head-lt/--a-foot` ＋ ナビ・解法 chrome `--li` 系が連動）を**問題の難易度で1つ選ぶ**：

  | 難易度 | 系統 | 対応 TX | 目安 |
  |---|---|---|---|
  | **EASY 易** | ローズ | P1 Sweet Berry/Rose | 基礎・典型（1周で取りたい） |
  | **STD 標準** | クリスタルブルー | P2 Crystal Blue | 中堅・応用・頻出（例：正当防衛/過失共犯） |
  | **HARD 難** | バイオレット | P3 Twilight Violet | 重論点・罠多・錯誤/不作為/原自行為等の難所 |

  3案の hex は `canonical/ARIADNE.html` の `:root` コメントに常時カタログ記載。切替は「▼ ACTIVE」直下の
  **ラベル＋値2行**を差し替えるだけ（残り2案はコメントのまま）。
- **機能色（意味で固定・難易度で変えない｜soft=塗り / line=罫・蛍光 / deep=文字）**：規範=ティール(`--ai`)／
  効く事実・OK=グリーン(`--gr`＝TX `recall-correct`)／罠・注意=コーラル(`--shu`)／ヒント・ゴール=ゴールド(`--gd`)。
  副アクセント＝ダスティティール `--a-mid #79a6a6`（TX `--mid`）。淡背景＋濃文字（WCAG AA）。蛍光下線 `.emb`（`.c/.g/.b`）。
- カード＝純白／誌面シート＝暖オフホワイト `--sheet #fbf7f0`／大背景＝難易度別ベース。本文・解説・模範に字下げ（text-indent:1em）。
- **周回ドリル○×ボタンはコンパクト固定（48×40px・左寄せ）**＝横幅いっぱいにしない（`flex:1` 禁止）。

---

## 6. 生成手順（蒸留方式）

1. 入力＝**検証済み JX（ATHENA）HTML**：`outputs/001_JX/{科目}JX/{科目}JX{NNN}.html`（問題文・論点抽出・模範答案・採点講評・規範・判例を一次情報源にする）。
2. **複製＋空化**：`canonical/ARIADNE.html` を出力先へ複製→本文を空化→各部を JX 内容から鋳造（content independence・ATHENA 本文の逐語転載はしない）。
3. **7手・骨子・15例題**を JX の論点構造から起こす。○×は**自己完結の一般原則／例題**に変換（§4）。
4. **検証**：`python scripts/validate-ariadne.py <出力>` で **A1〜A21 ERROR 0**。
5. **配置・同期**：`outputs/ux/000_ARIADNE/{00N_科目}/` に置き、**master に commit/push**（Lexia は `barExamSync.js` で outputs/ を自動スキャン＝push で自動同期）。

---

## 7. パイプライン連携（2026-06-18 ②-ariadne 実装済み）

- **バッチ（実装済み）**：`jx-batch-runner.ps1` の ②-rx / ②-arb と並ぶ **②-ariadne 段**（検証 PASS 済み
  JX から蒸留・非致命＝失敗しても JX/TTS 本流は止めない）。**既定 ON**・`-SkipAriadne` で抑止。
  sentinel は `BATCH_ITEM_COMPLETED:{ID}-ARIADNE`（プロンプト `prompts/new-ariadne-headless.md`）。
  検証は `validate-ariadne.py`、ログは `logs/rx-arb-summary.csv` に kind=`ARIADNE` で追記。
- **永続化（実装済み）**：`jx-finalize.ps1` ⑦ が `{ID}_ARIADNE.html` を RX/TREE と同コミットで git add→push
  ＝GitHub 経由で Lexia 自動同期に乗る。`jx-deploy.ps1` ⑥ が Drive `2 JX_論 文\D_ARIADNE\00N_科目\` へも配置。
- **後追い（未実装・任意）**：`scripts/ariadne-backfill.ps1`（既存 JX 群へ一括後追い）は未作成。
  当面は既存 JX 1 問ずつ `.claude/commands/new-ariadne.md` か headless プロンプトで生成する。
- 生成器の実体は LLM プロンプト（`prompts/new-ariadne-headless.md`）。①-rx/arb と同様「論点ごと」でなく「1問1枚」。

---

## 8. 検証（validate-ariadne.py）

- 構造 A1〜A11：lang/title/マストヘッド/フッター/問題文/手7個/ステッパー/骨子/自己採点/模範reveal/深掘り。
- Lexia 周回契約 A12〜A18：○×枚数／全カード `data-arena="1"`／`data-correct-value`／設問／解説／○×ボタン整合／メタregex非該当。
- Lexia 安全 A19〜A20：`<script>`内 `</body>` リテラル無し／○×採点JS。
- 命名 A21：`{科目}JX{NNN}_ARIADNE.html`。

---

## 9. 答案構成パズル＋想起カード＋試験下書き（2026-06-19 追加・周回の主役）

> 初学者の最重要スキル＝**論点抽出と答案構成**を能動想起で鍛えるため、骨子を
> 「穴埋めパズル」化する。エンジン（CSS/JS）は `canonical/ARIADNE.html` に実装済みで、
> **複製すれば自動継承**する（既存物への後追いは `scripts/ariadne-puzzle-backfill.py`・冪等）。

### 9-1. エンジン（canonical 継承・汎用・削除禁止）
- 読込時に JS が `.bone` の伏せ字対象をスロット化＋チップ配置で自動採点。クリックは
  **document 委譲**（Lexia の srcDoc iframe でも動く）。JS 無効環境（ファイルプレビュー等）は
  `.kp-fallback` 注記が出て**完成形の骨子がそのまま見える**安全フォールバック。
- 既定でパズル表示＝**答えは隠す**。模範は「答えを見る」で開閉。

### 9-2. 骨子タグ規律（生成時に問題固有で付与）
`.bone` 内に、伏せ字対象を次の class で必ずマークする：
- **論点＝`<span class="iss">…</span>`**／**結論＝`<u>…</u>`**／**見出し＝`<span class="b1">第1…</span>`**（既存）。
- **規範名＝`<span class="krule">三要件 等</span>`**／**あてはめキー事実＝`<span class="kfact">排他的支配 等</span>`**（Lv2 用に新規付与）。
- 3 段階：**Lv1=論点(.iss)** ／ **Lv2=論点+規範+あてはめ** ／ **Lv3=+結論<u>+見出し.b1**（順序・誰からも再現）。

### 9-3. おとりチップ（`.bone` の `data-kp-decoys`）
`type:text` を `|` 区切りで列挙（**type∈{iss,u,rule,fact}**・各レベルに出る型のみ採用・最大6枚提示）。
近い誤り（広義説↔狭義説、未遂↔既遂、遺棄↔遺棄致死 等）を 4〜6 個。例：
`data-kp-decoys="iss:【論点】正当防衛|u:殺人既遂罪 成立|rule:狭義説|fact:先行行為"`

### 9-4. 試験会場の下書き（`.drafting`・骨子の直前）
本番の紙上整理を再現。`まず下書き用紙にこう整理する` 見出し＋：
- `.draft-problem`＝問題文原文（再掲）。
- `.draft-grid` 内に **①人物関係図 `.rel-map`**（`.p`人物/`.ob`客体/`.out`対象外）**②時系列 `.timeline>li`** **③拾う文言 `.facts>li`（`.ph`引用＋`.cue`なぜ拾うか）**。
- **ネタバレ防止＝「生の事実抽出」までに限定**し、論点名・規範（排他的支配/未必の故意/三要件 等）は書かない（それはパズルの想起対象）。

### 9-5. 想起カード（○×の一部を格上げ・Lexia 連携）
○×は **10 枚前後**に整理し、**うち数枚を想起（1問1答）化**する：
`<div class="self-check-quiz recall" data-arena="1" data-recall="1" data-correct-value="○">`
＋`.quiz-question`（【想起】…を挙げよ）＋`<button class="recall-reveal" onclick="…答えを開示">`＋
`.quiz-answer`（模範）＋`.quiz-btns.recall-grade` に `.quiz-btn[data-value="○"]`書けた/`[data-value="×"]`書けなかった。
Lexia は `data-recall` を読み復習プールで「答えを見る→自己採点」UIに分岐（○=書けた=正解＝SM-2 卒業に前進）。

### 9-6. 検証
`validate-ariadne.py` A22：パズルエンジン（`KP-PUZZLE-BACKFILL` マーカー or `kp-levels`＋boot JS）の存在を確認（当面 WARNING）。
Lv2タグ/おとり/下書き/想起は**推奨**（機械必須にはしない＝後追い可）。
