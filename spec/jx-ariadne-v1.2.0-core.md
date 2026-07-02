# ARIADNE v1.2.0 PLACEHOLDER-LOCK — JX 解法ナビ＋周回 正典

> 初学者（白紙で論文に手が付かない）向けの「解法ナビ＋周回」専用 JX 正典。
> 現 JX 正典 **ATHENA**（百科事典型）はそのまま。ARIADNE はそれと**役割分担**する別系統。
> コードネーム＝アリアドネの糸（白紙の迷宮を抜ける解法導線）。
> **ステータス：現行 active。** Claude正典の誌面・模範答案を維持し、答案構成だけを JX019 で確定した
> マトリクス型チップ訓練へ正典化する。v1.2.0 では HTML/CSS/JS の構造をプレースホルダー方式で固定し、
> AI は問題固有本文スロットと難易度別 ACTIVE ベースカラー選択だけを判断する。RX 配線・TTS/答案構成の作法・
> 下書き・拾う文言を一体で回す。

---

## 0-prime. バージョン系譜（2026-06-29 確定）

- **v0.1（prototype）**：ARIADNE を ATHENA から分離した初期正典。解法7手・周回○×・深掘り・ATHENAジャンプを定義。
- **v0.3（visual prototype）**：`canonical/ARIADNE.html` の誌面風スケルトン。TX v11系フォント・難易度別ベースカラー・マイルドライナー機能色を導入。
- **v1.0.0（major / MATRIX-THREAD）**：JX019 で合意した **マトリクス型答案構成**を正式正典へ昇格。
  旧来の `<pre>` 風・箇条書き風骨子は新規生成では使わない。模範答案は Claude 正典どおり問規当結カードを維持する。
- **v1.1.0（minor / historical baseline）**：v1.0.0 の実運用で出た誌面調整を恒久化。
  本文1字下げ、ラベル＋本文2カラム、拾う文言の近接2カラム、項目間点線、マイルドライナー系ラベル色、
  RX `data-rx` 配線、`validate-ariadne.py` A30/A31/A32 と preflight 組込みを含む。
- **v1.2.0（minor / active / PLACEHOLDER-LOCK）**：正典デザインを「固定テンプレート＋変数スロット」方式へ昇格。
  `canonical/ARIADNE.html` は DOM/CSS/JS の固定正典、`canonical/ARIADNE.placeholder.html` は AI が置換してよい
  `{{{...}}}` スロット一覧を示す契約ファイルとする。AI はスロット外の構造・余白・class・JS・機能色を変更しない。
  例外として、難易度に応じた既存 ACTIVE ベースカラー（EASY/STD/HARD）の選択だけは AI 判断可。
- **v1.2.1（patch / 2026-07-02・骨子 SIMPLE-BONE 差し戻し）**：答案構成（骨子）を `.bone.matrix-bone`
  （問規当結グリッド）から、元設計 `刑JX001_ARIADNE.html` の**シンプル型 `.bone`（1項目1行）へ差し戻す**。
  問規当結の色分けは模範答案側に集約。canonical / placeholder / 生成プロンプト / validator を更新（§17）。
  版文字列 `ARIADNE v1.2.0 PLACEHOLDER-LOCK` は据置（PLACEHOLDER-LOCK 体制内の書式パッチ）。

## 0. 役割分担

| | ATHENA（既存） | ARIADNE（本spec） |
|---|---|---|
| 目的 | 知識の事典（条文/判例/学説/論証の網羅） | **「次に何をするか」の解法手順＋答案構成までの高速周回** |
| 起点 | `canonical/ATHENA.html` | `canonical/ARIADNE.html`（v1.2.0 PLACEHOLDER-LOCK active）＋`canonical/ARIADNE.placeholder.html` |
| 生成元 | 問題PDF＋逐語 | **検証済み JX（ATHENA HTML）から蒸留**（RX/TREE と同じ副産物パターン） |
| Lexia | 問題本体 | 別ID の周回教材（メイン JX と衝突しない） |

---

## 1. 配置・命名（2026-06-18 確定）

```
outputs/ux/001_ARIADNE/{00N_科目}/{科目}JX{NNN}_ARIADNE.html
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
7. **深掘り層**（`details#deep-dive`）＝**アテナ級**の規範・学説・判例・条文（§11）。1周目は開かない。
   気になった所をその場でアテナ密度で確認でき、さらに網羅的事典が要るときだけ末尾の「アテナで詳しく」で
   本物の ATHENA 版へ飛ぶ（postMessage `lexia:navigate`・§11-2）。**旧版の「（薄く）・ATHENA へ誘導」は §11 で上書き**。

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

### 4-bis. 教示↔ドリル 非重複の原則（2026-06-22 確定・最重要・ユーザー指示）

> **症状（実害）：** 各手の **教示**（`.do`／`details.peek` 本文＝「次の一手」のナビ）と、その直下の
> **周回ドリル○×** の中身がほぼ同じで、**教示を読んだ直後にドリルを解くと答えが丸わかり**になっていた
> （例：刑JX003 手6 BRIDGE ─ 教示「本問は事実が乏しく教唆で足りる／共同正犯にすると共謀共同正犯の論点が増える」、
> ドリル「背後者は事実が乏しいとき教唆で足り共同正犯は不要」＝**同一命題の言い換え**）。これは TX の
> 「正解再問 DRILL 禁止」（G17・答えの暗記は学習効果ゼロ）と同根の問題。**トグルで隠すのは不可**（ユーザー指示）。

**設計原則（最強の周回＝能動想起の最大化）：教示とドリルは“認知の的”を分ける。**

| | 教示（`.do`／`.peek`） | 周回ドリル○×／想起 |
|---|---|---|
| 役割 | **手続的**（procedural）「**本問で**どう動くか」の次の一手 | **宣言的**（declarative）「**どこでも効く**規範・定義・区別・要件」の能動想起 |
| 文体 | 本問の事実・結論にアンカー（具体・戦術） | 本問抜きで解ける一般原則／【例題】（転用可能） |
| 重複判定 | — | **「直上の教示を読めば答えが割れるか？」→ 割れるなら不可** |

**書換ルール（既存・新規 共通）：** ドリルが教示の言い換え（＝教示が既にその命題を述べている）になっていたら、
**ドリル側を、その手が依拠する“一段深い転用知識”へ振り替える**（教示は本問ナビとして残す）：

- 教示が「**戦術的選択**」を述べている（例「教唆で足りる／重い罪から書く／規範は再掲せず接続」）なら、
  ドリルは**その選択を支える規範・要件・理由**を問う：
  - BRIDGE「教唆で足りる」→ ドリルは **共謀共同正犯の成立要件（練馬事件の規範）**／**教唆犯と共同正犯（正犯性）の区別基準**／**共犯従属性**。
  - ORDER「正犯から書く」→ ドリルは **なぜ正犯から書くのか＝共犯従属性の意義**／**間接正犯なら背後者から書く例外**。
  - 接続「規範を再掲しない」→ ドリルは **その規範の中身そのもの**（法定的符合説の定義・符合範囲）。
- ドリルは**判別（どっちか）／定義／要件列挙／2説の帰結の分岐**を問う形にすると、教示の戦術文と的が自然にずれる。
- **法的正確性は当該 ARIADNE / 元 JX の検証済み本文（deep-dive・`.box-norm`・模範答案）に厳密準拠**。
  ファイルに無い規範・判例を新たに創作しない（振替先は必ずファイル内に根拠がある知識に限る）。
- 1手に複数ドリルがあるなら、**少なくとも教示と被る1枚を上記へ書換**。残りは別ファセット（典型誤り・対立説・例題）で多様化。
- 既に転用知識を問えているドリル（例：刑JX003 の客体／方法の錯誤・法定的符合説 群）は**触らない**（過剰書換禁止）。

**検証：** 字面コピーは `validate-ariadne.py` A23（8-gram backstop）で再発検知。**意味の言い換えは字面検出不能**なので、
生成時・後追い時に上記ルーブリックで自己点検する（各手で「教示を隠さず読んでもドリルが解けてしまわないか」を必ず確認）。

---

### 4-ter. ARIADNE 役割別品質定義（2026-07-01・強制）

ARIADNE は「読んで分かった気になる資料」ではなく、**初見問題で次に何をするかを再現する教材**である。各欄は次の役割を外したら低品質として扱う。

- **SCAN**：登場人物・行為・結果を、検討対象に入れるか切るかの単位で棚卸しする。単なる時系列要約は禁止。
- **AIM**：罪名候補と分岐理由を出す。条文番号の羅列や「まず考えよう」だけは禁止。
- **ORDER**：答案の順番を、法定刑・体系順・前提関係・配点重心のどれで決めたか明示する。
- **MARCH**：構成要件→違法性→責任→罪数のどこで詰まるかを示す。全部を「論点」と呼ばない。
- **BREAK**：各論点を「問題の所在→規範→効く事実＋評価語→結論」に分解する。規範名だけ、結論だけ、事実だけの記載は禁止。
- **BRIDGE**：共犯・罪数・複数人・複数行為の横断処理を、答案で何行書くかまで決める。汎用の「整理する」で終えない。
- **BUILD**：骨子は答案にそのまま移せる順序・見出し・結論にする。単なる箇条書きメモや論点名の羅列は禁止。
- **周回ドリル**：本問抜きで解ける転用知識を問う。直前の教示を読めば答えが割れる確認問題、正解番号暗記、問題文再掲は禁止。
- **模範答案**：問規当結の役割を段落ごとに明確にし、あてはめでは事実と評価語を分ける。規範だけ厚く、事実評価が薄い答案は禁止。
- **深掘り**：条文・判例・学説は元JX/ATHENAの検証済み本文に根拠を持たせる。創作・出典不明の判例風説明は禁止。
- **教授のひとこと**：答案構成の手順原理を残す。「頑張ろう」「重要」など気分だけの励ましは禁止。

### 4-quater. ARIADNE 強制ゲート（抜け防止）

以下があるファイルは、ARIADNE 完了・配信可・push可にしない。

- `quiz-question` が「本問の正解」「正解はどれ」型、または直上教示の言い換えになっている。
- `quiz-answer` が「重要」「確認しよう」だけで、理由・要件・結論の少なくとも2つを含まない。
- `.do` / `.box-tip` が「問題文のキーワード」「まず考えよう」など汎用誘導だけで、本問の切断軸を示さない。
- `.model-answer` に問規当結の役割クラスがない、またはあてはめ段落に具体事実・評価語がない。
- `.bone.matrix-bone` に論点・規範・事実・結論のいずれかが欠ける。

機械ガードは `scripts/validate-ariadne.py` A23 / A24 / A33 に置く。生成・更新した ARIADNE は必ず対象ファイル単位で通す。

---

## 5. 配色・フォント（誌面・2026-06-18 改訂：TX v11 を見本に統一・恒久）

> **【最重要・恒久】配色とフォントは TX v11 GENESIS（V3 Twilight Violet・刑TX327）を見本に統一**した
> （旧 ATHENA プラム＋マイルドライナー固定配色は廃止）。`canonical/ARIADNE.html` に実装済みで、
> 複製（§6）すれば自動継承する。設計の元ファイル＝`outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html`。
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
  **ラベル＋値2行**を差し替えるだけ（残り2案はコメントのまま）。これは v1.2.0 でも AI 判断可の唯一の
  デザイン差分であり、EASY/STD/HARD の既存プリセット以外の新色創作は禁止。
- **機能色（意味で固定・難易度で変えない｜soft=塗り / line=罫・蛍光 / deep=文字）**：規範=ティール(`--ai`)／
  効く事実・OK=グリーン(`--gr`＝TX `recall-correct`)／罠・注意=コーラル(`--shu`)／ヒント・ゴール=ゴールド(`--gd`)。
  副アクセント＝ダスティティール `--a-mid #79a6a6`（TX `--mid`）。淡背景＋濃文字（WCAG AA）。蛍光下線 `.emb`（`.c/.g/.b`）。
- カード＝純白／誌面シート＝暖オフホワイト `--sheet #fbf7f0`／大背景＝難易度別ベース。本文・解説・模範に字下げ（text-indent:1em）。
- **周回ドリル○×ボタンはコンパクト固定（48×40px・左寄せ）**＝横幅いっぱいにしない（`flex:1` 禁止）。

---

## 6. 生成手順（蒸留方式）

1. 入力＝**検証済み JX（ATHENA）HTML**：`outputs/001_JX/{科目}JX/{科目}JX{NNN}.html`（問題文・論点抽出・模範答案・採点講評・規範・判例を一次情報源にする）。
2. **複製＋スロット置換**：`canonical/ARIADNE.html` を出力先へ複製し、`canonical/ARIADNE.placeholder.html` の
   `{{{...}}}` スロット契約に従って、問題固有本文・属性だけを置換する。スロット外のHTML/CSS/JS・class・section順・
   余白・機能色は編集しない（content independence・ATHENA 本文の逐語転載はしない）。
3. **7手・骨子・15例題**を JX の論点構造から起こす。○×は**自己完結の一般原則／例題**に変換（§4）。
   **深掘り層は §11 の TX 参考条文判例書式でアテナ級に鋳造**（規範＋学説対立＋判例完全プロファイル＋
   条文完全プロファイル）し、末尾に「アテナで詳しく」ボタン（`data-athena-code={元問題ID}`）を置く。
4. **検証**：`python scripts/validate-ariadne.py <出力>` で **A1〜A32 ERROR 0**。
5. **配置・同期**：`outputs/ux/001_ARIADNE/{00N_科目}/` に置き、**master に commit/push**（Lexia は `barExamSync.js` で outputs/ を自動スキャン＝push で自動同期）。

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
> **【2026-07-02・§17 で差し戻し】骨子は シンプル型 `.bone`（刑JX001 型）を正典とする。**
> `.bone.matrix-bone` の `.mrow/.mline/.mstage`（問規当結グリッド）は**新規生成では使わない旧型**にした
> （CSS は互換のため残置）。以下 §9-2 の「マトリクス構造」「色」記述は legacy 参照。シンプル型の書式は §17 を正典とする。

骨子は **シンプル型 `.bone`**（罪責ごとに `.bsec > span.b1` 見出し＋各項目 inline `.bn` 連番＋一行本文・`white-space:pre-wrap`）とする。伏せ字対象を次の class で必ずマークする：
- **論点＝`<span class="iss">…</span>`**／**結論＝`<u>…</u>`**／**見出し＝`<span class="b1">第1…</span>`**（既存）。
- **論点チップに冠番号を付けない（ネタバレ防止・2026-06-23 確定）**：`<span class="iss">【論点】…</span>`
  と書き、`【論点①】`/`【論点1】` のような番号は**禁止**。本物だけ番号付き・おとり（9-3）は無番号だと、
  学習者が「番号の有無＝本物／おとり」「①→第1＝配置順」を見分けられ、論点抽出＋並べ替えの能動想起が成立しない。
  配置順は `.b1`（第1/第2…見出し）側で担保する。検証は `validate-ariadne.py` A27 が ERROR で検出。
  既存物の一括除去は `scripts/ariadne-iss-denumber-backfill.py`（冪等）。
- **規範名＝`<span class="krule">三要件 等</span>`**／**あてはめキー事実＝`<span class="kfact">排他的支配 等</span>`**（Lv2 用に新規付与）。
- 3 段階：**Lv1=論点(.iss)** ／ **Lv2=論点+規範+あてはめ** ／ **Lv3=+結論<u>+見出し.b1**（順序・誰からも再現）。
- **マトリクス構造**：罪責・小問単位は `.bsec`。各番号行は `.mrow`、番号は `.bn`、本文側は `.mcell`。
  問規当結は `.mline` で縦に積み、ラベルは `.mstage q/r/a/c/cut`（問・論・規・当・結・削）、本文は `.mtext`。
  `.mline + .mline` には点線区切りを入れ、本文だけ `text-indent:1em`。論点だけの行（`.iss`単独）は字下げしない。
- **色**：`.mstage` は濃いベタ塗りではなく、`--ml-red/teal/green/gold/violet` のマイルドライナー系パステルを使う。
  文字色は各 `--ml-*-deep`。これにより「問・規・当・結」がチップとして見え、答案構成パズルの視線移動が安定する。

### 9-3. おとりチップ（`.bone` の `data-kp-decoys`）
`type:text` を `|` 区切りで列挙（**type∈{iss,u,rule,fact}**・各レベルに出る型のみ採用・最大6枚提示）。
近い誤り（広義説↔狭義説、未遂↔既遂、遺棄↔遺棄致死 等）を 4〜6 個。例：
`data-kp-decoys="iss:【論点】正当防衛|u:殺人既遂罪 成立|rule:狭義説|fact:先行行為"`

### 9-4. 試験会場の下書き（`.drafting`・骨子の直前）
本番の紙上整理を再現。`まず下書き用紙にこう整理する` 見出し＋：
- **`.draft-problem`＝問題文原文の再掲（最重要・2026-06-21 確定）**：上部 `.problem .pq` を**逐語コピー**して入れる。
  答案構成（骨子）の直前で**上の問題文まで遡らずに解ける**ための再掲なので、要約・圧縮した「メモ調」にしない（過去そうなっていた）。
- **`.draft-digest`＝骨子用に一行へ圧縮したメモ**（原文の直下に併存）：`<span class="ddl">骨子用に一行圧縮</span>` ラベル＋
  `<span class="ddbody">…</span>` 本文の2カラムにし、事実の骨子だけを一行圧縮。原文（読む用）＋圧縮（骨子へ落とす用）の**二段構成**にする。
- `.draft-grid` 内は **①人物関係図 `.rel-map`** と **②時系列 `.timeline>li`** を上段2カラム、**③拾う文言 `.facts>li`（`.ph`引用＋`.cue`なぜ拾うか）** を `.draft-card span2` の下段全幅に固定する。
- **余白・2カラム規律（JX019で確定）**：`.draft-card` は左右に十分な余白を取り、`.rel-map`/`.timeline` は左に寄りすぎないよう内側に少し逃がす。
  `.facts li` は引用 `.ph` と理由 `.cue` の2カラム（引用側をやや広め）にして、右側に大きな空白を残さない。`.cue` の先頭に `...` / `…` などの接続記号を本文として置かない。小画面は1カラムへ落とす。
- **ネタバレ防止＝「生の事実抽出」までに限定**し、論点名・規範（排他的支配/未必の故意/三要件 等）は書かない（それはパズルの想起対象）。
- **既存物への一括反映＝`scripts/ariadne-draftproblem-backfill.py`（冪等）**：`.draft-problem` を原文へ置換し旧・圧縮版を `.draft-digest` へ退避（`.draft-digest` CSS も追記）。`<p class="draft-problem">` の旧記法・下書き欠如ファイルも吸収。

### 9-5. 想起カード（○×の一部を格上げ・Lexia 連携）
○×は **10 枚前後**に整理し、**うち数枚を想起（1問1答）化**する：
`<div class="self-check-quiz recall" data-arena="1" data-recall="1" data-rx="{科目}RX{NNN}_{論点序号}" data-correct-value="○">`
＋`.quiz-question`（【想起】…を挙げよ）＋`<button class="recall-reveal" onclick="…答えを開示">`＋
`.quiz-answer`（模範）＋`.quiz-btns.recall-grade` に `.quiz-btn[data-value="○"]`書けた/`[data-value="×"]`書けなかった。
Lexia は `data-recall` を読み復習プールで「答えを見る→自己採点」UIに分岐（○=書けた=正解＝SM-2 卒業に前進）。

**`data-rx`＝対応 RX 論証カードのリンク（2026-06-25・Lexia LXA_FEAT_008）**：各想起カードに、その想起が問う論点に
対応する RX 論証カードのコードを `data-rx="{科目prefix}RX{NNN}_{論点序号}"`（科目prefix込み・拡張子なし、例 `刑RX004_2`）で持たせる。
`{論点序号}` は JX 論点①②③の順＝同JX配下 `outputs/ux/002_RX/{00N_科目}/{科目}JX{NNN}/` の `_1/_2/_3` に一致。
**1カード=1RX**（多対一可＝複数の想起カードが同一 RX を指してよい）。対応 RX の無い総論的カードは `data-rx` 省略可。
Lexia は想起の**誤答時にこの RX を復習プールへ注入**し、ARIADNE 周回がそのまま弱点 RX の失敗駆動レビューになる。
検証は `validate-ariadne.py` A29（欠落=移行期 WARN／科目JX不整合・参照先RX不在=ERROR）。

### 9-6. 検証
`validate-ariadne.py` A22：パズルエンジン（`KP-PUZZLE-BACKFILL` マーカー or `kp-levels`＋boot JS）の存在を確認（当面 WARNING）。
Lv2タグ/おとり/下書き/想起は**推奨**（機械必須にはしない＝後追い可）。

---

## 10. 模範答案の誌面リスキン＝問規当結カード（2026-06-22 確定・ユーザー指示）

> 模範答案（`.model-answer`）が「字ばかりで読みにくい」課題に対し、**答案を論証ブロック単位の
> カード**にし、各段落を **問規当結（問題提起／規範／あてはめ／結論）でマイルドライナー色分け**する。
> 配色は RX(AXIOM) と同一の `--ml-*` 5系統（AXIOM と統一）。CSS は `canonical/ARIADNE.html` に実装済み
> （複製で自動継承）。既存物への一括反映は **`scripts/ariadne-ma-restyle.py --all`**（CSS のみ・本文不変・冪等）。

### 10-1. 役割クラス（生成時に各 `<p>` へ付与）
模範答案の各段落 `<p>` に、論証上の役割を1つ付与する（`.ma-h` 見出しには付けない）：

| 役割 | クラス | マイルドライナー | 食い出しバッジ | 典型 |
|---|---|---|---|---|
| 問題提起 | `role r-issue` | Blue | ❓ 問題提起 | 「〜の成否を検討する」「〜が問題となる」 |
| 規範 | `role r-norm` | Yellow | 🔑 規範 | 規範定立（説の名前は `<b class="rule">` で強調） |
| あてはめ | `role r-apply` | Violet | ✍ あてはめ | 事実を規範に当てる段落 |
| 結論 | `role r-concl` | Green | ⮕ 結論 | 「以上より〜が成立する」 |

- バッジ（食い出しピル・縁なし）はカード背景(`--c`)より一段濃い `--cb`、一行ごとに点線ルール。
- 段落番号（`<b>1</b>` 等）は各カードの `> b:first-child` が役割色で太字になる。

### 10-2. 事実と評価語（あてはめカード内）
あてはめ段落で、答案技術を可視化するため2種をスパンで括る：
- **事実＝`<span class="fact">…</span>`**（ピンクマーカー）＝問題文から拾った生の事実。
- **評価語＝`<span class="eval">…</span>`**（橙マーカー）＝「現実的危険を有する」「範囲内で符合する」等、
  事実を規範へ橋渡しする評価表現。

### 10-3. 注意
- **CSS のみのリスキンは無害**（役割未タグ段落は従来表示）。役割タグ＋fact/eval は**段落ごとの内容判断**で付与する。
- `<details class="reveal-answer">` の折りたたみ・`<u>` 結論下線・印刷時展開は不変。

### 10-4. 検証
`validate-ariadne.py` A24：リスキンCSS（`MA-ROLE-RESTYLE` マーカー）の有無と、模範答案に役割クラス
（`r-issue/r-norm/r-apply/r-concl`）が付いているかを確認（当面 WARNING・fact/eval は推奨）。

---

## 11. 深掘り層をアテナ級に＋アテナへジャンプ（2026-06-22 確定・ユーザー指示）

> **狙い：** 今後の学習はほぼ ARIADNE が主軸になる。学習中に気になった箇所を、上部の問題まで戻らず
> **その場でアテナ（JX 百科事典版）レベル**で確認できるよう、深掘りトグル（`details#deep-dive`）に
> **アテナ密度の知識**を収める。さらに網羅的事典が要るときだけ、本物の ATHENA 版へ**ジャンプ**する二段構え。
> エンジン（CSS）は `canonical/ARIADNE.html` に実装済み＝**複製すれば自動継承**する。

### 11-1. 深掘り層の中身＝TX 参考条文判例書式（A の主軸）
判例・学説・条文の**書式は TX v11 GENESIS の「参考条文判例」をテンプレート**にする（ユーザー指示）。
深掘り層 `.deep-body` を次の順で鋳造する：

1. **規範**（既存どおり `.box-norm`＝答案に書く中身）。
2. **学説対立**（`.gakusetsu > .gk`）＝対立見解を並べ、本問の採用説に `.gk.adopt`（緑＝「◀ 本問の採用説」）。
3. **判例 完全プロファイル**（`.basis-card.case-card`）＝1判例1カード。ヘッダ `⚖ {判例名}`＋
   `.freq-badge`（★★★/★★/★ の重要度）。本文は **【事案】【判旨】【補足】** を `<p class="hanging">`＋
   `<strong>` バッジ（【判旨】は `.judgment-text`）。射程・対比を必ず一言添える。
4. **条文 完全プロファイル**（`.basis-card.statute-card`）＝中核条文はカード化。`.para-num`（項番号バッジ）＋
   条文文言、`.note > .note-body` に **制度趣旨・保護法益・要件・射程**を `.kd-label.r-shushi/r-hogo/r-youken/r-shatei/r-ate/r-chui`（役割固定色）で整理。周辺条文は `.kd-item` の一覧でよい。
5. 相互参照は `a.ref-stat`（条文）・`a.ref-case`（判例）。本文強調は `.case-emphasis`／`.ron-mark`。

**法的正確性は元 JX（ATHENA）の検証済み本文に厳密準拠**。ファイルに無い判例・規範を創作しない（§4 と同旨）。
旧版の `.cs` 段落羅列は本書式（カード）へ置き換える。

### 11-1-bis. 最新法令・判例・学説レビュー（ARIADNE）
ARIADNE も司法試験対策教材なので、生成・更新時点の最新法令、最新判例、主要学説の現状を必ず確認する。

- 法令は e-Gov 法令検索で現行条文、未施行改正、施行日、改正前後の文言を確認する。司法試験・予備試験の法令基準は、法務省の当該年度実施情報、Q&A、試験用法文登載法令に合わせる。
- 判例は裁判所の裁判例検索と最近の裁判例を一次確認先にし、裁判所サイトが全判決を網羅しない点は最高裁判例集、判例百選、重要判例解説、主要判例データベース等で補完する。
- 学説は最新版の基本書、判例百選、重要判例解説、法学教室・法学セミナー等で補完する。機械検索だけで有力説の現状を確定しない。
- レビュー対象は、問題文、解法ナビ、骨子、模範答案、深掘り層の `.box-norm`、`.basis-card.case-card`、`.basis-card.statute-card`、`.basis-card.doctrine-card`、`.term-card`、周回○×とする。
- 旧法・旧判例・旧説と現在法・最新判例・現在の有力説に差分がある場合は、本文を現在法・最新判例ベースへ更新し、旧処理は深掘り層の関連カード付近に `.ariadne-current-law-note` として補足する。
- `.ariadne-current-law-note` には、確認日、参照ソース、旧処理、現在の処理、立法経緯・改正経緯、改正趣旨、試験対策上の扱いを記載する。単なる「新旧あり」の一言で済ませず、なぜ改正されたか、旧法・旧判例がどの問題意識を持っていたかまで短く示す。
- 新判例や改正で結論・理由付け・用語が変わる場合は、どちらで答案を書くべきかを曖昧にしない。対象試験年度の基準日と生成・更新日現在の違いがあるときは、その扱いをコラム内で明示する。
- 最新確認が未了のファイルは、ARIADNE v1.2.0 完了・配信可・push可とは扱わない。

### 11-2. アテナへジャンプ（B・postMessage `lexia:navigate`）
深掘り層末尾に「アテナで詳しく」ボタンを置く：

```html
<a class="go-athena" role="button" tabindex="0"
   data-athena-code="刑JX001"
   data-athena-href="../../../001_JX/001_刑法/刑JX001.html">…</a>
```

- `data-athena-code`＝**元問題ID**（例 `刑JX001`。`_ARIADNE` は付けない）。Lexia の `extractCode('刑JX001.html')` と一致。
- クリック時、末尾 JS `gotoAthena()` が **iframe 内なら**親へ
  `postMessage({source:'lexia-quiz', type:'lexia:navigate', targetCode})` を送る（Lexia が該当 JX を開く＝
  lexia 側 `onMessage` 実装済み・`LXA_FEAT_ariadne-athena-jump`）。**単体ファイルで開いた場合**は
  `data-athena-href`（相対パス）を `window.open` するフォールバック。
- ボタン文言に Lexia メタ除去 regex（`本問|正解は肢` 等・§4）を**含めない**（`stripMetaArenaQuizzes` 回避）。

### 11-3. 既存物への後追い（mechanical backfill）
`scripts/ariadne-athena-deep-backfill.py`（冪等）が**既存 ARIADNE 群**へ ①TX書式CSS ②アテナジャンプボタン
③`gotoAthena` JS を注入する（B が即座に全 ARIADNE で効く）。**深掘り層の TX 書式カード中身（A）は問題固有＝
機械生成不可**なので、内容のアテナ級化は**再生成**（バッチ／`/new-ariadne`）で揃える。backfill は jump を先行配備する保険。

### 11-4. 検証
`validate-ariadne.py`：**A25**（深掘り層が `case-card`＋`statute-card` の TX 書式＝アテナ級か）／
**A26**（`.go-athena[data-athena-code]` ジャンプボタンの有無）を追加（当面 WARNING・安定後 ERROR 化）。

---

## 12. 答案構成の作法＝教授のひとこと＋ステップ別周回ドリル（2026-06-22 確定・ユーザー指示）

解法ナビ（論点を**見つける**）と骨子パズル（**組み立てを再現**）の間に、答案を**並べ・厚みを決め・締める**
段取りを置く。位置は **BRIDGE と 手7 BUILD（骨子）の間**。`canonical/ARIADNE.html`（§6 複製）すれば構造・CSS・
汎用文言が自動継承される。元設計＝`outputs/ux/001_ARIADNE/001_刑法/刑JX001_ARIADNE.html`。

### 12-1. 構造（`.bc-wrap`・5ステップ）
**予測 → 軸 → 骨 → 重心 → 締め**の5ステップ。各ステップ＝
①手順タイトル（`.cm`）②**🎓 教授のひとことコラム**（`.bc-col`・コツ／アドバイス調・violet系）③本問の具体（`.bc-inst`）
④**ステップ別 周回ドリル○×**（`.self-check-quiz` `data-arena="1"`・直後に能動確認）。
- ④重心は `.bc-weight`（配点％バー）＋`.bc-cap`（字数目安）、⑤締めは `.box-trap`（書かないことリスト）を持つ。
- 末尾に `.bc-rhythm`（3周目以降のリズム超簡略版・口頭構成用の一筆書き）。
- `.bc-inst` はラベルと本文を分ける2カラムを正典とする：
  `<div class="bc-inst"><span class="ji">本問</span><div class="bi">本文</div></div>`。
  ラベル・バッジ・見出しは字下げせず、本文側 `.bi` だけ `text-indent:1em`。ラベル横に長文を直置きして本文がぶら下がる形は禁止。

### 12-2. 汎用と問題固有の分離
- **汎用（流用可）**：5ステップの手順タイトル・🎓教授のひとことコラム5枚・5枚のドリル○×
  （＝答案構成の**転用可能な手順原理**：設計優先／重い罪先行／規範先出し／重心集中／実益薄論点の切捨て）。
- **問題固有（鋳造）**：各 `.bc-inst`（登場人物・罪名・順序）・`.bc-weight`/`.bc-cap`（配点・字数）・
  `.box-trap`（書かないこと）・`.bc-rhythm`。

### 12-3. 規律
- ドリルは**本問前提なしで解ける一般原則**（§4 と同旨）。**正解は○×を偏らせない**（当て勘封じ・例 ○○×○×）。
- コラムは「解説」でなく**短い一言アドバイス**（1〜2文）。**解法ナビと役割が被るので教授のひとことはここ専用**
  （ナビ側には足さない＝ナビは `.do`＋💡box-tip＋peek＋ドリルで既に十分）。
- ナビの `💡 box-tip`（コツ箱）は **要所主義（2026-07-02 確定）**：判断・戦術が要る手（**最低 ORDER・BRIDGE**）には必ず置く。他手（SCAN/AIM/MARCH/BREAK/BUILD）は任意で、全手に無理に付けて filler にしない（gold `刑JX001_ARIADNE.html` も4手のみ＝これを正典とする）。ゲートは ORDER/BRIDGE の box-tip 有無までを見れば足り、全手強制はしない。

### 12-4. 検証
`validate-ariadne.py` **A27**：`.bc-wrap` 内に 🎓教授のひとことコラム ≥5・周回ドリル ≥5 で PASS
（無い既存物は WARNING＝再生成で揃える・当面 WARNING）。

---

## §13. 体裁強化（2026-06-23・全件＋canonical 反映済み）

ARIADNE の閲覧性を上げる 4 点を後段スクリプトで**冪等付与**する（生成プロンプトの
finalize 工程に組込み済み・既存 57 枚＋`canonical/ARIADNE.html` 反映済み）。

| # | 内容 | 付与スクリプト |
|---|---|---|
| ① | 深層部 条文プロファイルの「N項」を**ピル型バッジ化**し、項どうしを**点線**で区切る（`.stat-para`/`.stat-pn`/`.stat-pt`） | `scripts/ariadne-enhance.py` |
| ② | **本文インライン相互リンク**：条文・判例・学説・用語を**その語のまま**控えめな下線リンク（`a.xref auto`）にし、解法ナビ→深層部・カード間を相互リンク（最長一致・初出のみ・自己リンク除外・漢字連結の部分一致回避・学説/用語同名は学説優先）。**帰り道**＝各深層部カード末尾に「↩ 解法ナビ STEP n へ戻る」（参照元の手・無ければ `#sec-nav`／`.card-return`）を付与し双方向化 | `scripts/ariadne-autolink.py`（＋step id は `ariadne-enhance.py`） |
| ③ | マストヘッドに**目次ジャンプ TOC**（`.toc-nav`・問題文/解法ナビ/作法/骨子/想起/照合/深掘り）。`#top`/各 sec へアンカー | `scripts/ariadne-enhance.py` |
| ④ | 各セクション区切り＋深掘り前に「**▲ 先頭へ戻る**」（`.to-top`→`#top`） | `scripts/ariadne-enhance.py` |

- 実行順：`ariadne-enhance.py`（①③④）→ `ariadne-autolink.py`（②）。両者冪等で再実行安全。
- 既存一括反映：`for f in outputs/ux/001_ARIADNE/**/*_ARIADNE.html canonical/ARIADNE.html; do python scripts/ariadne-enhance.py "$f"; python scripts/ariadne-autolink.py "$f"; done`

---

## §14. v1.0.0 major — JX019 マトリクス正典化（2026-06-29・ユーザー確定）

JX019で仕上げた表示を、今後の ARIADNE 正典に採用する。意味は「Claude正典の誌面・模範答案の書式は維持しつつ、
答案構成だけを、チップ配置で訓練しやすいマトリクス型にする」こと。

- **模範答案**：従来のClaude正典どおり。問規当結カード、明朝、字下げ、事実/評価語マーカーを維持する。
- **答案構成（骨子）**：**シンプル型 `.bone`（元設計 刑JX001 型・§17）を正典とする**（2026-07-02 差し戻し）。旧来の `<pre>` 風・箇条書き風の骨子も、`.bone.matrix-bone` の問規当結グリッドも新規生成では使わない（matrix-bone は legacy・既存は順次 simple へ移行）。
- **RX配線**：想起カードの `data-rx` は徹底する。ただし対応論点が明確なものだけ付け、RXファイルがあるだけで無理に紐づけない。
- **2カラム規律**：CASE、問題文、下書き問題文、下書き要約、拾う文言、答案構成の作法、骨子行は、ラベル列＋本文列を分ける。
  バッジ・ラベル・見出し以外の本文は本文カラム側で字下げする。
- **点線区切り**：骨子の `.mline + .mline` と、拾う文言の項目間には点線区切りを置き、視線が詰まらないようにする。
- **照合配置**：`.collate`、`details.reveal-answer`、`details#deep-dive` は骨子コンテナ `.skeleton` の内側に置く。背景上へ外置きしない。
- **バックアップ**：この正典化前の比較用として、`backups/ariadne-claude-canonical-20260629-154017` に
  `canonical/ARIADNE.html` のHEAD版と、刑JX001〜019の JX/ARIADNE/RX/TREE/TTS 存在分を退避済み。
- 閉じた深掘り層（`<details id="deep-dive">`）への TOC/相互リンクは末尾 JS が details を展開してからジャンプ。`@media print` で TOC/戻るは非表示。

---

## §15. v1.1.0 minor — 正典指定後の恒久対策（2026-06-29）

v1.0.0 の見た目合意を、生成・検証・同期前ゲートで戻らないように固定する。

- **正典スケルトン**：`canonical/ARIADNE.html` の版記載は当時 `ARIADNE v1.1.0 MATRIX-THREAD` とした。
  現行 active は §16 の `ARIADNE v1.2.0 PLACEHOLDER-LOCK`。
- **生成プロンプト**：`prompts/new-ariadne-headless.md` は本 spec を唯一の正典として参照する。
- **検証 A30**：`.problem .pq` は `text-indent:1em`。`text-indent:0` への退行は ERROR。
- **検証 A31**：`.facts li` を2カラムにする場合は
  `grid-template-columns:minmax(18em,32em) minmax(16em,28em); column-gap:18px; justify-content:start`
  の近接型を正典とする。旧ワイド2カラム
  `minmax(24em,1.35fr) minmax(18em,1fr); column-gap:24px` は ERROR。
  また、人物関係図が全幅 `span2` になる退行、拾う文言が下段全幅 `span2` でない退行、`.cue` 先頭に `...` / `…` が出る退行も ERROR。
- **検証 A32**：`.collate`、`details.reveal-answer`、`details#deep-dive` は骨子コンテナ `.skeleton` 内に固定する。
  旧来の `max-width:calc(var(--maxw) - 120px); width:100%` による外置き幅調整へ戻す退行は ERROR。
- **preflight**：`scripts/check-lexia-preflight.py` は `scripts/check-ariadne-canonical.py` を通じて
  `canonical/ARIADNE.html` と `outputs/ux/001_ARIADNE/**/*.html` を横断検証する。
- **RX 配線**：想起カードの `data-rx` は「対応論点が明確なものだけ」付ける。参照先不在・科目/JX不整合は ERROR。
  RX ファイルがあるだけで無理に紐づけることは禁止。
- **本文レイアウト**：バッジ・ラベル・見出し以外の本文は本文カラム側に置く。ラベル横へ長文を直置きして
  ぶら下がりを作らない。本文カラムは1字下げを標準にする。
- **役割分担の維持**：TREE は論点構造理解、RX は答案で吐き出す論証、ARIADNE は周回導線。
  三者を混同せず、ARIADNE は「JX → 答案構成 → 想起 → RX → TREE」へ自然に回る導線を担う。

---

## §16. v1.2.0 minor — PLACEHOLDER-LOCK（2026-06-29・ユーザー確定）

v1.1.0 で正典化した見た目を、AI生成時に揺らさないため、ARIADNE を **固定HTML＋変数スロット**方式へ移行する。
目的は「AIにデザイン判断の余白を渡さず、問題ごとに変わる文章・論点・事実・RX配線だけを判断させる」こと。

- **固定正典**：`canonical/ARIADNE.html`。HTML/CSS/JS、class名、セクション順、余白、字下げ、点線区切り、
  マイルドライナー機能色、パズルエンジン、Lexia連携JSは固定する。
- **スロット契約**：`canonical/ARIADNE.placeholder.html`。AIが置換してよい箇所を `{{{SLOT_NAME}}}` で列挙する。
  生成時はこのファイルを「編集可能箇所一覧」として読み、三重波括弧スロット外を変更しない。
- **AI判断可**：問題文、登場人物、解法ナビ本文、peek、ドリル、答案構成の作法本文、下書き、拾う文言、骨子の
  論点/規範/あてはめ/結論、模範答案本文、深掘り本文、`data-rx` の教育的に明確な配線。
- **AI判断可のデザイン例外**：難易度に応じた ACTIVE ベースカラー選択のみ許す。
  `canonical/ARIADNE.html` の既存プリセット **EASY / STD / HARD** から1つ選び、「▼ ACTIVE」直下のラベル＋値だけを
  差し替える。新しい色の創作、機能色（問/規/当/結、事実、罠、ヒント等）の変更は禁止。
- **AI判断不可**：カード構造、2カラム構造、下書きカードの `span2` 配置、ラベル/本文の配置、本文字下げ、`.facts li` のgrid値、`.mline` 構造、
  `.bc-wrap` 構造、`.model-answer` の問規当結カード構造、`details#deep-dive` の外枠、JS、CSSセレクタ。
- **生成プロンプト**：`prompts/new-ariadne-headless.md` は `{SKELETON}=canonical/ARIADNE.html` と
  `{SLOT_CONTRACT}=canonical/ARIADNE.placeholder.html` を読み、固定正典を複製してスロット相当箇所だけを置換する。
- **ガード**：`scripts/check-ariadne-canonical.py` は `canonical/ARIADNE.html` の
  `ARIADNE v1.2.0 PLACEHOLDER-LOCK` と、`canonical/ARIADNE.placeholder.html` の
  `ARIADNE_SLOT_CONTRACT v1.2.0 PLACEHOLDER-LOCK` を確認する。

---

## §17. v1.2.1 patch — 骨子はシンプル型 `.bone` へ差し戻し（2026-07-02・ユーザー確定）

**背景：** v1.0.0／§14 で骨子を `.bone.matrix-bone`（`.mrow/.mline/.mstage` の問規当結グリッド）へ正典化したが、
実運用で「骨子が模範答案とほぼ重複し、"先に答えを見ない・骨だけ再現" の周回原則を崩す／問規当結の色ラベルが
骨子には過剰でノイズ」という問題が出た。ユーザー確定により、**骨子は元設計 `刑JX001_ARIADNE.html` の
シンプル型 `.bone`（1項目1行）を正典に差し戻す**。問規当結の色分けは**模範答案（`r-issue/r-norm/r-apply/r-concl`）へ集約**する。

### 17-1. シンプル型 `.bone` の書式（正典）
- ラッパは `<div class="bone" data-kp-decoys="…">`（`matrix-bone` を付けない）。`white-space:pre-wrap` で改行・行頭空白がそのまま効く。
- 罪責・小問ごとに `<div class="bsec"><span class="b1">第1　…</span> … </div>` で束ねる。
- 各項目は **2 space ＋ `<span class="bn">N</span>` ＋一行本文**。見出し直後の第1項目は `.b1` と同じ行に続ける。
- 補足は行頭 `      └ `（6 space ＋ └）のサブ行。締めは `  → 結論：… ＝ <u>…</u>`。
- 伏せ字マーカーは従来どおり：**論点＝`<span class="iss">【論点】…</span>`（番号なし・A27）／規範＝`<span class="krule">…</span>`／
  あてはめキー事実＝`<span class="kfact">…</span>`／結論＝`<u>…</u>`／見出し＝`<span class="b1">…</span>`**。
- おとりチップ `data-kp-decoys`・パズルエンジン・3段階 Lv（Lv1 論点／Lv2 +規範+事実／Lv3 +結論+見出し）は不変。
- **matrix-bone（§9-2 の `.mrow/.mline/.mstage`）は legacy**。CSS は互換のため残置するが新規生成では使わない。

### 17-2. 恒久化（回帰防止）
- `canonical/ARIADNE.html`・`canonical/ARIADNE.placeholder.html` を simple 型へ更新済み（複製で自動継承）。
- `prompts/new-ariadne-headless.md` を simple 型指示へ更新。
- `validate-ariadne.py`：`matrix-bone` 検出時に **A34 WARNING（旧型・§17 で simple へ差し戻し・要移行）**。
  simple `.bone` は `iss`＋`<u>`（論点＋結論）を最低要件として A33 で確認。既存の matrix-bone 出力は
  ERROR にせず（順次移行のため）WARNING で移行残を可視化する。
- **展開前ゲート強化（2026-07-02・A35〜A39）**：残ファイル・他科目へのロールアウトが、監査で見つけた欠陥クラスを
  自分で捕まえるよう `validate-ariadne.py` に追加。
  - **A35＝深掘りテンプレ流用検出（ERROR）**：深掘り層（`.deep-body`）に、本問（`.cast`/問題文/模範答案/骨子/解法ナビ）へ
    一切出ない人物記号（甲乙丙丁戊/XYZVW）が「本問の◯」「◯：」等の強い文脈で出れば、別問題の深掘り丸ごと流用（018型）として ERROR。
  - A36＝旧版スタンプ残置（WARN・現行は v1.2.0）／A37＝未定義 box クラス（`.warn-box` 等の素描画・WARN）／
    A38＝`.draft-problem` が `.problem .pq` の逐語か（§9-4・WARN）／A39＝`.bc-inst` の `.bi` 2カラム（§12-1・WARN）。
  - `canonical/ARIADNE.html` は A35〜A39 すべて PASS（複製起点の gold を実測確認）。A35 のみ ERROR、他は WARN で
    既存コーパスの移行残を可視化する（WARN は preflight を落とさない）。
- 版文字列は `ARIADNE v1.2.0 PLACEHOLDER-LOCK` のまま（guard 非破壊）。

### 17-3. 移行（後日・ユーザー運用）
既存 matrix-bone 出力（刑JX007-008・010-015・019-024・071-074 等 18 問）は**内容保持のまま simple 型へ蒸留変換**して順次差し替える。
各ファイルの模範答案・自己採点を一次情報にし、`.mline` のフル文を骨子用の一行フレーズへ圧縮する（`.iss/.krule/.kfact/<u>` は温存）。
gold 参照＝`刑JX001_ARIADNE.html`（元設計）と `刑JX009_ARIADNE.html`（2026-07-02 変換済み見本）。
