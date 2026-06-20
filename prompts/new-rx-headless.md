# new-rx-headless.md

`claude -p` headless 実行用 **RX 論証カード生成プロンプト**（v1.1）。
検証 PASS 済みの JX HTML を素材に、Lexia アプリ用の論証カード
（**1 ファイル = 1 論点**の自己完結 HTML）を抽出・鋳造する。
**TX/JX/ARIADNE と同じく、誌面デザインは正典スケルトン `{RX_SKELETON}`
（canonical/RX.html）を複製して継承する**（v1.1・2026-06-20。TX 級のボックス／
バッジ／フォント／配色を作り込み済み）。
`jx-batch-runner.ps1` の ②-rx 段、または `rx-arb-backfill.ps1` から呼び出される。

> RX は Lexia 側で **TX/JX と同格の SRS カード**として間隔反復される。
> 生成完了後に必ず sentinel 1 つを標準出力に echo して終了する。

---

## Section 1: 役割定義

あなたは bar-exam プロジェクトの **RX 論証カード生成 AI** である。

- 本実行は **headless モード（`claude -p`）**。ユーザー対話は一切不可。
  確認・質問・選択肢提示は禁止。判断はすべて自走で確定させる。
- 生成・検証・修正・sentinel 出力までを完全自走で完遂する。
- 「何も出さずに終了」「途中で考え込んで黙る」は禁止。
  必ず Section 7 / 8 / 9 のいずれか 1 つの sentinel を出力してから終了する。

---

## Section 2: タスク変数

| 変数 | 例 | 意味 |
|---|---|---|
| `{SOURCE_HTML_PATH}` | `C:\...\outputs\001_JX\001_刑法\刑JX032.html` | 素材となる **検証 PASS 済み JX HTML** の絶対パス |
| `{PROBLEM_ID}` | `刑JX032` | 元 JX の識別子 |
| `{PROBLEM_NUMBER}` | `032` | 元 JX の 3 桁番号 |
| `{SUBJECT_PREFIX}` | `刑` | 科目接頭辞 |
| `{RX_BASENAME}` | `刑RX032` | RX ファイル名の共通幹（科目接頭 + RX + 元 JX 番号） |
| `{OUTPUT_DIR}` | `C:\...\outputs\ux\001_RX\001_刑法\刑JX032` | 出力ディレクトリの絶対パス（問題ごとに `{科目}JX{NNN}/` サブフォルダ・2026-06-20 恒久化） |
| `{RX_SKELETON}` | `C:\...\canonical\RX.html`（リモートは `canonical/RX.html`） | **複製起点**＝gold RX スケルトン（TX 級の誌面デザイン正典） |
| `{VALIDATE_RX}` | `C:\...\scripts\validate-rx.py` | 検証スクリプトの絶対パス |

---

## Section 3: 素材の読み方（content source）

`{SOURCE_HTML_PATH}` を読み、以下から論点ごとの素材を収集する：

1. **第2部（論点別 詳細解説）の各 `.card#issue-{n}`** — 最重要素材
   - A 条文分析 / B 判例法理 / C 学説 / D 解法アルゴリズム
   - F 答案表現集（規範定立例・あてはめテンプレ）
   - G 頻出論証ブロック（必須・推奨・発展 3 層）
   - H 失点回避チェックリスト
2. **第5部 5-4 答案論証集**（完成形・簡略版・発展版）
3. **第5部 5-1 条文集 / 5-2 判例集**（関連条文・判例の正確な表記）

**同一問題由来の内容の再構成なので流用は正当**（他 JX からの流用は禁止のまま）。
ただし JX の文章を漫然と貼らず、カードの想起構造（Section 4）へ再構成する。

### カード化する論点の選定

- 第2部で **A〜H 完全セット（主要論点）として扱われている論点を全て**カード化する。
  通常 1 問あたり **2〜5 枚**になる。
- 副論点（A・D 程度の短縮版）は、G 相当の論証（規範）が素材に存在する場合のみカード化。
- 規範が存在しない手続的・整理的な項目はカード化しない。

---

## Section 4: RX カード仕様（Lexia 取込仕様・厳守）

### 4-1. ファイル名と粒度

- **1 ファイル = 1 論点**
- ファイル名: `{RX_BASENAME}_{n}.html`（n = 1 からの連番）
  - 例: `刑RX032_1.html`, `刑RX032_2.html`
- `<title>` タグ = 論点名そのまま（例: `<title>承継的共同正犯の成立範囲</title>`）。
  Lexia はここをカードタイトルとして抽出する。

### 4-2. カード本文の構成（この順序で）

1. **論点名**（h1）と元問題への言及（小さく「出典: {PROBLEM_ID}」）
2. **問題の所在** — どんな場面で何が問題になるか。3 行以内
3. **規範（暗記対象）** — 最重要ブロック。判例の規範・要件を正確に。
   **初期状態では隠し、「規範を表示」ボタンで開閉**できるようにする
   （自力想起 → タップ確認、という使い方をするため）
4. **理由づけ** — 趣旨・利益衡量。3 行以内
5. **あてはめの型** — 答案でどの順に何を認定するかの型。箇条書き
6. **関連判例・条文** — 判例名（年月日）と条文番号のみ。解説不要
7. **規範チェック（○×クイズ 2〜4 問）** — 4-3 のマークアップ厳守

### 4-3. ○×クイズのマークアップ（Lexia が自動抽出する・厳守）

```html
<div class="self-check-quiz" data-correct-value="×"
     data-explanation="正しくは「○○」。規範の主体を入れ替えたひっかけ。">
  <div class="quiz-question">（規範を改変したひっかけ命題、または正しい命題）</div>
  <div class="quiz-buttons">
    <button class="quiz-btn" data-value="○" onclick="lexiaAnswer(this,'○')">○</button>
    <button class="quiz-btn" data-value="×" onclick="lexiaAnswer(this,'×')">×</button>
  </div>
  <div class="quiz-result" style="display:none"></div>
</div>
```

- `data-correct-value` は全角の `○` / `×`
- `data-explanation` は必須（Lexia の復習プール・弱点克服帳に表示される解説）
- `lexiaAnswer` 関数は各 HTML 内 `<script>` に自前実装
  （押されたボタンと `data-correct-value` を比較し、`.quiz-result` に正誤と解説を表示）
- ひっかけの作り方: 主体の入替え / 要件の脱落 / 「直ちに」「特段の事情」等の限定句の有無 /
  判例と学説の入替え

### 4-4. デザイン・技術制約（**スケルトン複製で自動充足**）

**デザインは `{RX_SKELETON}`（canonical/RX.html）を複製して継承する**（Section 5）。
TX v11 GENESIS を見本にした誌面（12 役割フォント・V3 配色・ボックス／バッジの作り込み・
背景テクスチャ）が clone で必ず正典品質で揃う＝二台運用でも同一出力。以下は継承で満たされる：

- スマホ縦画面で読みやすい（本文 16px・行間広め・余白十分）
- カード幅 `.card{max-width:920px;margin:0 auto}`（2026-06-20 Lexia ワイド化で 680→920）
- **フォントは TX と同ファミリー**（Shippori Mincho B1／Zen Kaku Gothic Antique／Zen Maru Gothic／
  Source Code Pro／M PLUS 1p）を Google Fonts で読み込む。**システムフォント fallback を厚く持つ**ので
  オフラインでも明朝＋ゴシックで成立する（TX／ARIADNE と同方針。validate-rx R9 は CDN を WARNING のみ）
- 規範ボックス（`.norm-box`）＝TX `key-phrase-box` 相当の琥珀＋🔑バッジ。問題の所在（`.lead`）・
  関連判例条文（`.refs`）・○×クイズ（`.self-check-quiz`）も TX 流の `::before` バッジ付きボックス
- **配色は元 JX の雰囲気・論点の難度で `:root` の「▼ ACTIVE」プリセットを選ぶ**
  （EASY ローズ=P1／STD ブルー=P2／HARD バイオレット=P3。3 案 hex は `:root` コメントにカタログ常時記載）。
  **1 問の RX カード群は同一プリセットで揃える**（束として配色統一）。科目が `刑` で既定（HARD）のままでも可
- 1 ファイル 12〜40KB 目安（誌面装飾込みでも軽量。1 論点 1 ファイルは厳守）
- **【絶対禁止】`<script>...</script>` 内に `</body>` リテラル文字列を書くこと**
  （Lexia アプリの正規表現マッチで全機能死亡。スケルトンの script はこれを回避済み＝**逐語コピー**する）

### 4-5. 内容の正確性

- 規範は判例の文言に忠実に。要約しても要件の数・順序を変えない
- 判例引用には年月日（例: 最判平17.3.10）
- 学説対立は判例の立場を本筋とし、有力説は理由づけ欄に 1 行で触れる程度

---

## Section 5: 実行手順（スケルトン複製 → 鋳造）

1. `{SOURCE_HTML_PATH}` を読み、第2部の論点構成を箇条書きで整理（カード化対象を確定）。
   **冒頭で逐語コピー対象と新規執筆対象を区別**（4-4 と同じ content independence の考え方）。
2. **`{RX_SKELETON}`（canonical/RX.html）を Read** し、構造シェル（`<head>`／`<style>`／`<script>`／
   `<body>` の骨格）を把握する。
3. `{OUTPUT_DIR}` が無ければ作成。既存の `{RX_BASENAME}_*.html` があれば一旦削除してよい
   （この problem の RX のみ・全カードを書き直す前提）。
4. **論点ごとに 1 ファイルを生成**（n=1 からの連番）。各ファイルは **`{RX_SKELETON}` を複製**して作る：
   - **逐語コピー（structural shell）**：`<head>` のフォントリンク・`<style>` 全体・`<script>` 全体・
     各コンポーネントの class／タグ構造。**書き換えない**（TX 級デザインと Lexia 契約・`</body>` 回避が崩れる）。
   - **問題固有で執筆（差し替える中身だけ）**：`<title>`＝論点名／`.masthead` の論点名・`出典`／
     `.lead`（問題の所在）／`.norm-box`（規範＋`.cite`）／理由づけの `<p>`／`.card ol`（あてはめの型）／
     `.refs`（条文・判例）／`.self-check-quiz` 各問の `data-correct-value`・`data-explanation`・`.quiz-question`。
   - **配色**：`:root` の「▼ ACTIVE」プリセットを、元 JX の雰囲気・論点難度で EASY/STD/HARD から選定
     （1 問の全カードで同一プリセットに揃える）。
   - 1 メッセージ 50KB 超の Write は禁止（カード単位なら自然に収まる）。
5. 検証: `python {VALIDATE_RX} {OUTPUT_DIR} {RX_BASENAME}` を実行
6. ERROR があれば修正 → 再検証（最大 3 周）
7. sentinel を echo して終了

---

## Section 6: 自己検証チェックリスト（Write 後・validate 前に目視確認）

- [ ] ファイル名が `{RX_BASENAME}_{n}.html` 形式（n は 1 始まり連番・欠番なし）
- [ ] **`{RX_SKELETON}` の `<style>`／`<script>` を逐語コピーしている**（独自 CSS を書き起こしていない）
- [ ] **`:root` の「▼ ACTIVE」プリセットを 1 つ選定**（1 問の全カードで同一）
- [ ] 各ファイルの `<title>` が論点名／`.masthead` の論点名・出典が問題固有
- [ ] 規範ブロック（`.norm-box`）が初期非表示＋`.norm-toggle` で開閉
- [ ] ○×クイズが各カード 2〜4 問、`data-correct-value`（全角○×）/ `data-explanation` あり
- [ ] `<script>` 内に `</body>` リテラルなし（スケルトンのまま）
- [ ] スケルトンの本文プレースホルダ（`〔…〕`）が 1 つも残っていない

---

## Section 7: 完了 sentinel（完全成功時のみ）

検証 ERROR 0 で全カード生成完了したら：

```
echo "BATCH_ITEM_COMPLETED:{PROBLEM_ID}-RX"
```

## Section 8: ISSUES sentinel（生成成功・検証未達時）

カードは生成できたが ERROR / WARNING が残った場合：

```
echo "BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}-RX:errors=<N>:warnings=<M>"
```

直前に残存 ERROR の概要を 1 行ずつ出力すること。

## Section 9: FAILED sentinel（生成不能時のみ）

素材 HTML が読めない・論点が 1 つも抽出できない等：

```
echo "BATCH_ITEM_FAILED:{PROBLEM_ID}-RX:reason=<具体的理由>"
```

---

## 実行開始

上記仕様に従い、`{SOURCE_HTML_PATH}` から `{OUTPUT_DIR}` への
RX 論証カード生成を**今すぐ**開始せよ。
