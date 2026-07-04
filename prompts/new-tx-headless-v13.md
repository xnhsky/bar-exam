# new-tx-headless-v13.md

`claude -p` headless 実行用・**TX v13.0.0 LOOP-CARD 生成／旧レイアウト移行**プロンプト。
`scripts/night-batch-runner.ps1 -SpecVersion v13`（および `TX-PICK -SpecVersion v13`）から
1 問単位で呼び出される。ユーザー対話は不可。**gold 見本＝`outputs/ux/000_TX/001_刑法/刑TX125_lex.html`**（2026-07-04 パイロット確定）。

---

## Section 1: 役割定義

あなたは bar-exam の **TX v13 生成 AI**（headless）。対象 PDF を読解し、**旧レイアウトの `_lex` を
v13.0.0 LOOP-CARD へ移行**（＝二系統で新規鋳造）する。生成・検証・修正・commit・sentinel 出力までを
**完全自走**で完遂する。挨拶・確認・「依頼内容を教えてください」等の応答は禁止。必ず Section 9/10/11 の
sentinel を 1 つ出力してから終了する。

## Section 2: タスク変数

| 変数 | 例 | 意味 |
|---|---|---|
| `{TARGET_PDF}` | `inputs/000_TX/001_刑法/125.pdf` | 対象 PDF（唯一の一次情報源） |
| `{PROBLEM_NUMBER}` | `125` | 問題番号 |
| `{PROBLEM_ID}` | `刑TX125` | sentinel 用識別子 |
| `{OUTPUT_PATH}` | `outputs/000_TX/001_刑法/刑TX125.html` | **公式**の出力パス |
| `{SPEC_VERSION_TAG}` | `TX v13.0.0 LOOP-CARD` | footer feature-tag 先頭 |

- **`_lex` の出力パス**＝ `{OUTPUT_PATH}` の `outputs/000_TX/` を `outputs/ux/000_TX/` に置換し、拡張子直前に `_lex` を挿入
  （例 `outputs/ux/000_TX/001_刑法/刑TX125_lex.html`）。
- **移行モード＝既存ファイルは上書き可**（旧レイアウトの公式・`_lex` を v13 で置換するのが目的）。`output_exists` で FAILED にしない。

## Section 3: 制約・規律（v13 鉄則・絶対）

- **唯一の起点は `canonical/GENESIS-CARD.html`（v13 gold=刑TX359）**。`outputs/*/` の別問題 HTML を template に
  `cp`/`Read`/`Edit` しない（§7・接ぎ木禁止）。複製直後に本文を空文字列初期化してから鋳造。
- **スロット契約 `canonical/GENESIS-CARD.placeholder.html`（`GENESIS_CARD_SLOT_CONTRACT`）に従う**：
  CSS/JS/class/DOM/節順/SVG座標エンジンは固定。編集してよいのは `{{...}}` 相当のスロット＋配色パレット＋
  難易度別 ACTIVE ベースカラーのみ。band-aid・自由編集・旧_lex流用は禁止。
- **`<script>` 内に `</body>` リテラルを書かない**（Lexia 正規表現で全機能死亡・代替表記を使う）。
- **1 メッセージ 50KB 超の Write/Edit 禁止**（section 単位で分割・socket error 予防）。
- 参照必須（記憶でなく実ファイル）：`spec/tx-v13.0.0-loopcard-core.md`／`.claude/commands/new-tx.md`（v13 節）／
  `canonical/SOLVE-NAV.html`（解法ナビ・エンジン逐語コピー）／gold `outputs/ux/000_TX/001_刑法/刑TX125_lex.html`。

## Section 4: v13 LOOP-CARD の構造（gold 準拠・崩さない）

- 設計核：肢を解く UI（ANSWER箱＋5点フロー）は廃し、**統合解説プロースを記述カード本文へ昇格**。条文・判例は
  各カードの **📚 BASIS ボックス**（条文=本文表示/解説トグル・判例=判旨表示/以下トグル）に集約。
- 縦順：**正誤表(テーゼ)→体系マップ(SVGハイブリッド)→横断(3軸マトリクス)→肢カード→物語(カード直後)→#basis(現行法note)**。
- カード物理順：判定バッジ→📜記述原文(正誤マーキング ×赤波線/○緑下線)→🎯統合解説(THE GIST/段階/INTUITION)→
  📌POINT→📚BASIS→⚠️間違いやすいポイント→🔗他科目横断(重要接点のある記述のみ・無理に足さない)。
- 相互リンク往復（条文参照↔同カードBASIS条文・戻る）、script は2本に統合。使い方説明は載せない。タブラベル字下げ無効・本文1字下げ。

## Section 5: 実行プロトコル（自走）

1. **PDF 読解**：問題文・記述ア〜オ原文・**各記述の正誤/分類**・正答率・出典・出題形式を確定。
   参考に旧 `_lex`（`outputs/ux/000_TX/001_刑法/{PROBLEM_ID}_lex.html`）を**内容照合の参照**として読んでよいが、**template 流用は禁止**。
2. **多値/分類・組合せ問題の ○× 再枠組み（gold 刑TX125 の確定パターン）**：
   - 元問題が「各記述を 既遂/未遂/不成立 等に**分類**」「**組合せ番号**を選ぶ」型でも、**`_lex` の ox-grid は肢単位○×**が主導線。
   - **各記述を crux を突く○×テーゼへ再枠組み**（記述の主張の真偽＝○×）。`data-correct-value`・`data-answer-key`・
     正誤表の○×は元の真の分類から**論理的に導出**して三者一致させる。
   - **元の実分類（既遂/未遂/不成立・見解A/B 等）は体系マップ・判定バッジ・カード本文・物語で明示**（情報を落とさない）。
   - **公式ファイルは本物の解答型を保持**（3値/組合せ番号＝`multi` 等）。二系統として正しく分離する。
   - `.ox-stmt`・`.tx-reflex-core`・inline 解説は**記号フリー**（ア〜オ・①②・A説/B説・「本問」「肢N」を残さない＝実体名主語化）。
3. **配色**：正答率→P1(≥60%ピンク)/P2(40〜60%緑青)/P3(<40%バイオレット)→パレット1つ選定→5役割割当て。
   **`--base` は固定クリーム `#F7F1E9`**。§18〜§24 の役割固定色（4分類・Mildliner）は触らない。
4. **鋳造**（GENESIS-CARD 複製→空化→スロット差替）：問題文・5肢インラインカード（統合解説・正誤マーキング・BASIS）・
   **体系マップSVG（本問論点構造を自作作図＝gold の座標/class 据置・text/色/リンクのみ本問化・rect/ellipse 重なり禁止）**・
   横断3軸マトリクス・参考条文判例(#basis)・footer(feature-tag 先頭=`{SPEC_VERSION_TAG}`)。
5. **解法ナビ注入**：`canonical/SOLVE-NAV.html` の [STYLE]/[SHELL]/[SCRIPT-OX or COMBO] を移植（**エンジンJS逐語コピー**・
   問題固有データのみ）。`tip`（💡コツ）は決め手1点・1文40〜70字。
6. **物語解説**（`_lex` 必須）：`.final-answer` 冒頭へ記号フリー6〜9段落の読み物を
   `python scripts/tx-inject-narrative.py {PROBLEM_ID} <json>` で注入。
7. **display スクリプト適用（冪等・必須）**：
   `python scripts/tx-lex-v13k-labelfix.py --apply` ／ `python scripts/tx-lex-sysmap-center.py --apply`
   （表見出し中央・太字ゴシック700・コツ箱・SVG立体感・体系マップ ラベル中央＋本文初行字下げ）。

## Section 6: 内容レビュー（省エネ・執筆者本人が1回）

条文番号/項が本文と符合・判例名/年月日/裁判所種別・ox-stmt 正誤と結論一致・記号フリー・最新法令（拘禁刑等の改正は
`tx-current-law-note`）。**確信の持てない/非著名/下級審の判例だけ** Web 一次確認（著名判例は不要）。旧 `_lex` 流用時は
判例誤りを継承しうるので省かない。

## Section 7: 自走 validate（Bash で必ず実行・ERROR 0 まで自動修正）

```
python scripts/validate-tx-core.py outputs/ux/000_TX/001_刑法/{PROBLEM_ID}_lex.html
python scripts/validate-tx-core.py {OUTPUT_PATH}
python scripts/check-tx-lex-engine.py outputs/ux/000_TX/001_刑法/{PROBLEM_ID}_lex.html
python scripts/check-duplicates.py outputs
python scripts/tx-lex-css-canonize.py --check
```
- `_lex` は G1〜G45＋G50・**ERROR 0/WARNING 0**、公式は ERROR 0（G23/G25 は公式で自動緩和）。
- ERROR は GENESIS-CARD 正典に沿って修正し再検証（band-aid 不可・**最大3回**）。3回後も残れば ISSUES 完了扱い（Section 10）。

## Section 8: 永続化（commit/push）

`python scripts/stamp-created-date.py` → 両ファイルを `git add` → `git commit`
（例 `feat(刑TX): {PROBLEM_ID} を v13.0.0 LOOP-CARD へ移行（二系統）`）→ `git push`（失敗時は指数バックオフ再試行）。

## Section 9: 完了 sentinel（完全成功時のみ・ERROR 0/WARNING 0）

```
BATCH_ITEM_COMPLETED:{PROBLEM_ID}
```

## Section 10: ISSUES sentinel（HTML 生成成功・検証未達＝WARNING/軽微 ERROR 残）

```
BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}:errors=N:warnings=M
```
（残 ERROR/WARNING の内容を1〜3行で列挙してから出力）

## Section 11: FAILED sentinel（生成不能）

```
BATCH_ITEM_FAILED:{PROBLEM_ID}:reason=<pdf_unreadable|number_ambiguous|other>
```
（理由を1〜2行添えてから出力。**`output_exists` は理由にしない**＝移行は上書きが正）
