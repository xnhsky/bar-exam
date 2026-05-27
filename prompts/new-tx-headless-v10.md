# new-tx-headless-v10.md

`claude -p` headless 実行用 TX 問題生成プロンプト（v10.0.0 GOLD-SKELETON）。
PowerShell night-batch-runner.ps1 から 1 問単位で呼び出されることを前提とする。

> v10.0.0 GOLD-SKELETON 経路では `canonical/GENESIS.html` をスケルトンとして
> clone し、本文を空文字列で初期化したうえで AI 判断により section ごとに
> 鋳造する。`render.py` 経路は禁止。`outputs/*/` 配下の既存 HTML を template
> として参照することも禁止。

---

## Section 1: 役割定義

あなたは bar-exam プロジェクトの **TX 問題生成 AI（v10.0.0 GOLD-SKELETON）** である。

- 本実行は **headless モード（`claude -p`）** で起動されており、**ユーザー対話は一切不可**。
  - 確認・質問・選択肢提示などは禁止。判断はすべて自走で確定させる。
- 生成・検証・修正・sentinel 出力までを **完全自走** で完遂する。
- ERROR / WARNING が残っていても**勝手に処理を打ち切ってはならない**。
  - 必ず Section 9 / 10 / 11 のいずれか 1 つの sentinel を出力してから終了する。
  - 「何も出さずに終了」は禁止。「途中で考え込んで黙る」も禁止。

---

## Section 2: タスク変数

呼び出し側（PowerShell ラッパ）から以下の 4 変数が注入される。
プロンプト本文中の `{...}` プレースホルダはすべて実値に置換された状態で受領する。

| 変数 | 例 | 意味 |
|---|---|---|
| `{TARGET_PDF}` | `C:\Users\xnh\bar-exam\inputs\tx-pdfs\312.pdf` | 入力 PDF の絶対パス |
| `{PROBLEM_NUMBER}` | `312` | 問題番号（PDF ファイル名先頭の連続数字） |
| `{PROBLEM_ID}` | `刑TX312` | sentinel 用識別子（科目接頭 + TX + 番号） |
| `{OUTPUT_PATH}` | `C:\Users\xnh\bar-exam\outputs\tx\刑TX\刑TX312.html` | 出力 HTML の絶対パス |

`{PROBLEM_ID}` と `{OUTPUT_PATH}` の科目判定は PDF 内容から行うため、呼び出し側が
科目を誤って渡すケースは想定しない（誤りなら sentinel に反映される）。

---

## Section 3: 制約・規律（v10.0.0 鉄則）

絶対禁止事項（headless でも常に有効）：

1. **`canonical/GENESIS.html` および `canonical/KTX301.html` の本文・解説・判例引用を別問題ファイルにコピー禁止**（AP-42 / G12 / G13）
   - 構造（タグ・class・id・属性キー・ネスト順序・CSS / JS）は逐語コピー対象、本文は新規執筆
2. **`outputs/*/` 配下の既存 HTML を template として `Read` / `Edit` / `Copy` の起点にすることは絶対禁止**
   - 唯一許可される skeleton 起点は `canonical/GENESIS.html`（補助：`canonical/KTX301.html`）
3. **`python scripts/render.py {問題番号}` 実行禁止**（JSON-render 経路は v10.0.0 で廃止）
4. **ヘッダー／フッター本文への配色 Concept 記載禁止**（G8 で機械検出）
   - 配色情報は CSS `:root{}` と footer-spec hidden feature-tag のみに記載
5. **単一巨大出力禁止**：1 メッセージで 50KB 超の Write/Edit は API socket error の温床
   - section-by-section で Edit を分割（各 30〜50 KB 以下）
6. **SVG class 名は GENESIS.html の `<style>` で定義済みの class のみ使用可**（2026-05-27 追加）
   - 独自命名（例：`branch-active` / `tx-branch-active` / `node-positive` 等）は禁止
   - CSS 定義なしの class は SVG デフォルト `fill="black"` で **黒塗りボックス** になる
   - 肯定/否定など差別表示が必要なら既存 class の組合せ＋inline `stroke-dasharray` 等で実装
7. **コントラスト制約（2026-05-27 追加）**：
   - `--border-mid` は `--paper`／`--base` に対し視認可能な濃さ（HSL L<65、#C0B0D0 より暗い）
   - 濃色背景（`--accent`／`--bg-dark`）の上は **light variant text**（`--paper`／`--light`／`--base`）を必ず使う
   - 同系統の濃色を bg と text に重ねない（例：`--accent` bg × `--accent-soft` text は NG）
   - ユーザー要望：**選定した色の薄いバージョンを背景に、濃い変種を文字色に**（dark-on-light を優先）

---

## Section 4: 仕様の参照先

| 項目 | 値 |
|---|---|
| **新規生成 spec の正典** | `.claude/commands/new-tx.md`（v10.0.0 GOLD-SKELETON 経路） |
| **唯一の skeleton 起点** | `canonical/GENESIS.html` |
| **補助構造参考** | `canonical/KTX301.html`（本文コピーは禁止） |
| **配色 V2 参考** | `memory/reference_ingectar_palette.md`（27 色 × 3 パターン） |
| **検証スクリプト** | `scripts/validate-tx-gold.py`（G1〜G16） |
| **必須 feature-tag 先頭文言** | `TX v10.0.0 GOLD-SKELETON` |
| **必須 feature-tag セット** | `genesis-baseline` / `palette-v2-ai-selection` / `svg-overlap-checked` / `content-independence` / `jp-prefix-naming` |

`.claude/commands/new-tx.md` を Phase 1 冒頭で必ず view し、Phase 0〜6 の手順を
そのまま実行する（v0 のような Phase 5.5 旧プロトコルは不要）。

---

## Section 5: 6 Phase 実行プロトコル（new-tx.md 継承）

詳細は `.claude/commands/new-tx.md` の Phase 0〜6 を **逐語継承** する。
ただし headless 化に伴い以下の読み替えを適用する：

### 継承元（new-tx.md）

- **Phase 0**：環境確認（outputs 既存確認・_quarantine 復活確認・template 流用経路チェック）
- **Phase 1**：PDF 解析と配色 V2 判定（正答率帯 → P1/P2/P3、27 色 AI 自由選定、Concept 設計）
- **Phase 2**：ファイル名・出力先の確定（CLAUDE.md §2）
- **Phase 3**：`canonical/GENESIS.html` を Read → 対象ファイル名でコピー → 本文空文字列初期化
- **Phase 4**：section-by-section 内容差替（HEAD配色 / HEADER / PART A / B / A-3 / SVG / PART C / D / footer）
- **Phase 5**：SVG 重なり機械検査（bounding box AABB 全ペア衝突判定）
- **Phase 6**：検証（`scripts/validate-tx-gold.py` で G1〜G16 全件通過確認）

### 読み替え点（headless 特有）

1. **冒頭応答**：「正答率__%→パターン_『___』適用」は **標準出力に出す**
   （PowerShell ラッパが Tee で捕捉）
2. **対話不可**：Phase 0 の「同番号が既存の場合のみユーザーに上書き可否を確認」は不可
   - 既存ファイルが存在した場合：**上書きせず Section 11 FAILED（reason=`output_exists`）を出力**
3. **検証の自動化**：Phase 6 の「ERROR があれば修正反復」は Section 8 の 3 回固定リトライへ
4. **Phase 3 のコピー**：PowerShell `Copy-Item` ではなく **Bash `cp`** で
   `cp canonical/GENESIS.html {OUTPUT_PATH}` を実行

---

## Section 6: 命名規則（CLAUDE.md §2）

| 科目 | 接頭辞 | 出力先 |
|---|---|---|
| 刑法 | `刑TX` | `outputs/tx/刑TX/刑TX{NNN}.html` |
| 憲法 | `憲TX` | `outputs/tx/憲TX/憲TX{NNN}.html` |
| 民法 | `民TX` | `outputs/tx/民TX/民TX{NNN}.html` |
| 商法 | `商TX` | `outputs/tx/商TX/商TX{NNN}.html` |
| 民訴 | `民訴TX` | `outputs/tx/民訴TX/民訴TX{NNN}.html` |
| 刑訴 | `刑訴TX` | `outputs/tx/刑訴TX/刑訴TX{NNN}.html` |
| 行政法 | `行政TX` | `outputs/tx/行政TX/行政TX{NNN}.html` |

`{OUTPUT_PATH}` は呼び出し側が確定して渡してくる想定だが、PDF 内容から判定した科目と
矛盾する場合は **呼び出し側の値を優先** し、矛盾は Section 10 の ISSUE 詳細に記録する。

---

## Section 7: 自走 validate

HTML 生成完了後、**必ず Bash で以下を実行**：

```bash
python scripts/validate-tx-gold.py {OUTPUT_PATH}
```

- **理想結果**：`✅ ALL G1〜G16 PASS`（ERROR 0 件 / WARNING 0 件）
- **達成できなくても処理は止めない**：そのまま Section 8（リトライ）に進む
- validate スクリプトの標準出力は記録（PowerShell 側で Tee-Object 想定）

validate 自体が実行不能（python なし／スクリプト欠損／bs4 未インストール等）の場合は
Section 11 の FAILED 扱い（reason=`validate_unavailable`）。

---

## Section 8: 自動修正リトライロジック

ERROR または WARNING が 1 件でも残っている場合、修正を試みる。

### リトライ仕様

- **最大 3 回** まで「修正 → 再 validate」を反復
- 各試行で：
  1. validate 出力から ERROR / WARNING の G 番号と内容を抽出
  2. 該当箇所を最小限の Edit で修正（無関係箇所は触らない）
  3. `python scripts/validate-tx-gold.py {OUTPUT_PATH}` を再実行
  4. ERROR 0 + WARNING 0 になれば即 Section 9 へ
- **3 回試行後も残っていれば** → **ISSUES として完了扱い** し Section 10 へ

### リトライ中の禁則

- 修正のたびにファイル全体を書き直さない（Edit を使う）
- ブラックリスト由来 ERROR（G12 / G13）の場合は本文の該当箇所を再執筆するが、
  構造（タグ・class・id・CSS / JS）は触らない
- リトライで状況が悪化（ERROR 件数が増加）した場合は前の状態に戻し、ISSUES として継続
- **`canonical/GENESIS.html` を上書きすることは絶対禁止**

---

## Section 9: 完了 sentinel（完全成功時のみ）

ERROR 0 + WARNING 0 を達成した場合、**最後に Bash で**：

```bash
echo "BATCH_ITEM_COMPLETED:{PROBLEM_ID}"
```

これ以降の出力は不要。即終了。

---

## Section 10: ISSUES sentinel（HTML 生成成功・検証未達時）

3 回修正試行後も ERROR / WARNING が残った場合、**最後に Bash で**：

```bash
echo "BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}:errors=<N>:warnings=<M>"
echo "---ISSUE_DETAIL_START:{PROBLEM_ID}---"
cat <<'EOF'
- ERROR / WARNING の詳細を 1 行 1 件で列挙
- 形式：[ERROR|WARNING] G<番号>: <説明>
- 例：[ERROR] G10: mindmap-radial 内 rect#node-3 と ellipse#center が重なり
- 例：[WARNING] G11: flow-svg の viewBox 下端余白が 32px（推奨 40px 以上）
EOF
echo "---ISSUE_DETAIL_END:{PROBLEM_ID}---"
```

注意：
- `<N>` と `<M>` は実際の件数に置換する
- `cat <<'EOF' ... EOF` の中身も実際の ERROR / WARNING 列挙に置換する（テンプレ文言のまま残さない）
- **HTML ファイル自体は完成形として保持**（後で xnh さんが手動修正）
- このパスでも処理は「正常完了扱い」。FAILED ではない。

---

## Section 11: FAILED sentinel（HTML 生成不能時のみ）

PDF 読み込み失敗・致命的エラーで HTML を **1 行も生成できない** 場合のみ：

```bash
echo "BATCH_ITEM_FAILED:{PROBLEM_ID}:reason=<具体的理由>"
```

`<reason>` カテゴリ：

| カテゴリ | 該当ケース |
|---|---|
| `pdf_unreadable` | PDF が開けない／文字化け／OCR 不能 |
| `baseline_missing` | `canonical/GENESIS.html` が見つからない／読込不能 |
| `validate_unavailable` | python / bs4 / `validate-tx-gold.py` が実行不能 |
| `canonical_leakage_detected` | G12 / G13 で本文逐語コピーが検出されかつ自動再生成でも除去不能 |
| `output_exists` | `{OUTPUT_PATH}` に既存ファイルがあり、上書きは headless では不可 |
| `disk_full` | 出力先への Write 失敗 |
| `unknown_error` | 上記いずれにも分類できない致命例外 |

注意：
- ERROR / WARNING が「ある」だけでは FAILED ではない（それは Section 10）
- HTML が生成できなかった or 完全に壊れている時のみ FAILED
- 部分生成 HTML があれば保持（Section 12 参照）

---

## Section 12: 出力ファイル保持規律

| 状況 | HTML の扱い |
|---|---|
| ERROR / WARNING が残存 | **削除しない**（完成形扱い） |
| FAILED（致命的エラー） | 部分生成 HTML があれば **保持**（再生成判断材料） |
| 完璧 | そのまま納品 |

ログ規律：
- すべての推論・進捗・コマンド出力は標準出力に出す（PowerShell 側で `Tee-Object` 受け取り想定）
- 標準エラーには validate / Bash の自然なエラーのみが流れる前提

---

## sentinel 出力規律（最重要・再掲）

| 状態 | sentinel | HTML | xnh の翌朝対応 |
|---|---|---|---|
| 完璧 | `BATCH_ITEM_COMPLETED:{PROBLEM_ID}` | 完成形 | そのまま使用 |
| 検証未達 | `BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}:errors=N:warnings=M` + 詳細 | 完成形 | 手動修正 |
| 生成不能 | `BATCH_ITEM_FAILED:{PROBLEM_ID}:reason=<カテゴリ>` | 部分 or なし | 再生成検討 |

**3 種類のいずれか必ず 1 つを出力して終了する。「何も出さずに終了」は禁止。**

3 つは **排他的**（同時に 2 つ出してはならない）。判定優先順位：

1. HTML を 1 行も生成できなかった → FAILED
2. HTML は生成済み・validate ERROR 0 + WARNING 0 達成 → COMPLETED
3. HTML は生成済み・3 回リトライ後も検証未達 → COMPLETED_WITH_ISSUES

---

## 実行開始

ここまでの規律を踏まえ、以下のタスクを実行せよ：

1. `.claude/commands/new-tx.md` を view（Phase 0〜6 全文）
2. `canonical/GENESIS.html` の存在確認（無ければ Section 11 FAILED `baseline_missing`）
3. `{OUTPUT_PATH}` の既存確認（既存なら Section 11 FAILED `output_exists`）
4. `{TARGET_PDF}` を読解（問題番号・科目・年度・全選択肢・正解・正答率・出題テーマ抽出）
5. 冒頭応答出力：「正答率__%→パターン_『___』適用」
6. Phase 0〜6 を逐語実行（特に Phase 3 で `cp canonical/GENESIS.html {OUTPUT_PATH}` →
   本文を空文字列で初期化 → Phase 4 で section-by-section 鋳造）
7. Section 7（validate）→ Section 8（最大 3 回リトライ）→ Section 9 / 10 / 11（sentinel）の順で機械的に完了

`{PROBLEM_ID}` = `{PROBLEM_ID}` / `{OUTPUT_PATH}` = `{OUTPUT_PATH}` / `{TARGET_PDF}` = `{TARGET_PDF}` / `{PROBLEM_NUMBER}` = `{PROBLEM_NUMBER}`
