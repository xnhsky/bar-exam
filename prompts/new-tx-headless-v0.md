# new-tx-headless-v0.md

`claude -p` headless 実行用 TX 問題生成プロンプト（v0 / Phase 1 ドラフト）。
PowerShell から 1 問単位で呼び出されることを前提とする。

---

## Section 1: 役割定義

あなたは bar-exam プロジェクトの **TX 問題生成 AI** である。

- 本実行は **headless モード（`claude -p`）** で起動されており、**ユーザー対話は一切不可**である。
  - 確認・質問・選択肢提示などは禁止。判断はすべて自走で確定させること。
- 生成・検証・修正・sentinel 出力までを **完全自走** で完遂する。
- **重要**：ERROR / WARNING が残っていても、**勝手に処理を打ち切ってはならない**。
  - 必ず Section 9 / 10 / 11 のいずれか 1 つの sentinel を出力してから終了する。
  - 「何も出さずに終了」は禁止。「途中で考え込んで黙る」も禁止。

---

## Section 2: タスク変数

呼び出し側（PowerShell ラッパ）から以下の 4 変数が注入される。
プロンプト本文中の `{...}` プレースホルダはすべて実値に置換された状態で受領する。

| 変数 | 例 | 意味 |
|---|---|---|
| `{TARGET_PDF}` | `C:\Users\OWNER\bar-exam\inputs\tx-pdfs\306.pdf` | 入力 PDF の絶対パス |
| `{PROBLEM_NUMBER}` | `306` | 問題番号（PDF ファイル名先頭の連続数字） |
| `{PROBLEM_ID}` | `刑TX306` | sentinel 用識別子（科目接頭 + TX + 番号） |
| `{OUTPUT_PATH}` | `C:\Users\OWNER\bar-exam\outputs\tx\刑TX\刑TX306.html` | 出力 HTML の絶対パス |

`{PROBLEM_ID}` と `{OUTPUT_PATH}` の科目判定は PDF 内容から行うため、呼び出し側が科目を誤って渡すケースは想定しない（誤りなら sentinel に反映される）。

---

## Section 3: 制約・規律（CLAUDE.md §7 要約引用）

絶対禁止事項（headless でも常に有効）：

1. **canonical/KTX301.html のテキスト流用禁止**
   - 本文・解説・判例引用を別問題ファイルに 1 文字でもコピーしない（AP-42）
   - 構造・class・id・属性キー・CSS / JS は逐語コピー対象、本文は新規執筆
2. **単一巨大出力禁止（50KB 上限の目安）**
   - 1 ファイルあたり 50KB を大きく超える場合、内容の妥当性を疑い再構築する
3. **既存ファイル変更禁止**
   - 各科目 001（例：刑TX001.html）
   - `canonical/KTX301.html`
   - `outputs/tx/刑TX/刑TX304.html`、`刑TX305.html` 等の既存問題ファイル
   - これらに対して Edit / Write を行わない

---

## Section 4: 使用 spec

| 項目 | 値 |
|---|---|
| **参照する spec** | `spec/tx-v9.1.0-mindmap-core.md` |
| 参照しない spec | `spec/tx-v9.0.0-genkei-core.md`（旧版） |
| footer feature-tag 必須文言 | **`TX v9.1.0 MINDMAP`** |

`spec/tx-v9.1.0-mindmap-core.md` の §0-tri／§0-quad／§0-bis／§1-bis を Phase 1 冒頭で必ず view し、§Annex A / B / C と §22-quad（マインドマップ）を Phase 5 で使用する。

v9.0.0 系の `genkei-skeleton` 等のタグ名は v9.1.0 で変更されている可能性があるため、必ず v9.1.0 の §33 相当節の最新 feature-tag リストを参照する。

---

## Section 5: 6 段階 Write プロトコル（new-tx.md 継承）

詳細は `.claude/commands/new-tx.md` の Phase 1〜6 を **継承** する。
ただし headless 化に伴い以下の読み替えを適用する：

### 継承元

`.claude/commands/new-tx.md`：

- Phase 1: 準備（spec view／PDF 読解／パターン判定）
- Phase 2: ファイル名・出力先の確定（§1-bis）
- Phase 3: §0-tri ゼロベース再構築（新規時はスキップ）
- Phase 4: §0-quad コンテンツ独立性プロトコル 7 ステップ（IQ-1〜IQ-7）
- Phase 5: §0-bis 15 ステップ生成プロトコル（Annex A/B/C 逐語コピー + PART D ARENA 12 問）
- Phase 5.5: 3 Type 対応自動判定（single / ox-grid / multi）
- Phase 6: 検証と配信

### 読み替え点（v9.1.0 mindmap 対応）

1. **spec バージョン**：`v9.0.0-genkei-core.md` → `v9.1.0-mindmap-core.md`
2. **§22-quad マインドマップ section を必ず生成**
   - v9.0.0 にはなかった新セクション。v9.1.0 では必須要素。
3. **参考｜共通根拠条文・判例 section を独立化**
   - v9.0.0 では basis-card 内に混在していたが、v9.1.0 で独立 section として切り出し。
4. **footer feature-tag リスト** は v9.1.0 §33 相当節を参照（`TX v9.1.0 MINDMAP` を含む 15 件以上）
5. **headless 特有**：冒頭応答「正答率__%→パターン_『___』適用」も標準出力に出すこと（PowerShell 側でログ捕捉される）

### Phase 6 の自動化（headless 拡張）

new-tx.md の Phase 6 は「ERROR があれば修正反復」だが、headless では：

- Section 7（validate 実行）→ Section 8（最大 3 回リトライ）→ Section 9/10/11（sentinel 出力）の順で機械的に進める
- 「修正反復」の上限は Section 8 で 3 回に固定する

---

## Section 6: 命名規則（README.txt 準拠）

`inputs/tx-pdfs/README.txt` の規約に従う：

- **入力 PDF**：ファイル名に数字を含み、最初の連続数字が出力のシリアル番号となる
  - 例：`306.pdf`、`K310-2024-problem.pdf`、`予備H30問15.pdf`
- **出力 HTML**：`{科目プレフィックス}TX{NNN}.html`（NNN は 3 桁ゼロ埋め）
  - `outputs/tx/{科目フォルダ}/` 配下に配置
- **科目プレフィックスと出力先**（new-tx.md Phase 2 ロジック準拠）：

| 科目 | 接頭辞 | 出力先 |
|---|---|---|
| 刑法 | `刑TX` | `outputs/tx/刑TX/刑TX{NNN}.html` |
| 憲法 | `憲TX` | `outputs/tx/憲TX/憲TX{NNN}.html` |
| 民法 | `民TX` | `outputs/tx/民TX/民TX{NNN}.html` |
| 商法 | `商TX` | `outputs/tx/商TX/商TX{NNN}.html` |
| 民訴 | `民訴TX` | `outputs/tx/民訴TX/民訴TX{NNN}.html` |
| 刑訴 | `刑訴TX` | `outputs/tx/刑訴TX/刑訴TX{NNN}.html` |
| 行政法 | `行政TX` | `outputs/tx/行政TX/行政TX{NNN}.html` |

`{OUTPUT_PATH}` は呼び出し側が確定して渡してくる想定だが、PDF 内容から判定した科目と矛盾する場合は **呼び出し側の値を優先** し、矛盾は Section 10 の ISSUE 詳細に記録する。

---

## Section 7: 自走 validate

HTML 生成完了後、**必ず Bash で以下を実行**：

```bash
python scripts/validate-tx.py {OUTPUT_PATH}
```

- **理想結果**：ERROR 0 件 + WARNING 0 件
- **達成できなくても処理は止めない**：そのまま Section 8（リトライ）に進む
- validate スクリプトの標準出力は記録（PowerShell 側で Tee-Object 想定）

validate 自体が実行不能（python なし／スクリプト欠損等）の場合は Section 11 の FAILED 扱い（`reason=spec_load_failure` 隣接の `validate_unavailable` カテゴリで報告、新カテゴリ扱いは Section 11 末尾参照）。

---

## Section 8: 自動修正リトライロジック

ERROR または WARNING が 1 件でも残っている場合、修正を試みる。

### リトライ仕様

- **最大 3 回** まで「修正 → 再 validate」を反復
- 試行回数は **内部カウンタ** で管理（プロンプト内で明示的に「試行 1 回目」「試行 2 回目」「試行 3 回目」とラベル付けして思考し、3 回目完了時点で必ず Section 9 or 10 に遷移）
- 各試行で：
  1. validate 出力から ERROR / WARNING の S 番号と内容を抽出
  2. 該当箇所を最小限の Edit で修正（無関係箇所は触らない）
  3. `python scripts/validate-tx.py {OUTPUT_PATH}` を再実行
  4. ERROR 0 + WARNING 0 になれば即 Section 9 へ
- **3 回試行後も残っていれば** → **ISSUES として完了扱い** し Section 10 へ

### リトライ中の禁則

- 修正のたびにファイル全体を書き直さない（Edit を使う）
- ブラックリスト由来 ERROR の場合は IQ-2 相当の本文再執筆を行うが、構造（Annex A/B/C）は触らない
- リトライで状況が悪化（ERROR 件数が増加）した場合は前の状態に戻し、ISSUES として継続

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
- 形式：[ERROR|WARNING] S<番号>: <説明>
- 例：[ERROR] S12: footer-spec の feature-tag に "TX v9.1.0 MINDMAP" を含めること
- 例：[WARNING] S45: PART D ARENA の ○:× 比率が 6:6 ではなく 7:5
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
| `spec_load_failure` | `spec/tx-v9.1.0-mindmap-core.md` が view 不能、または validate スクリプト実行不能 |
| `canonical_leakage_detected` | IQ-7 ブラックリスト検査で KTX301 文言混入が検出されかつ自動再生成でも除去不能 |
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
- `claude -p` の出力は別途ファイルに保存される想定なので、内部思考も適度に外出ししてよい（ただしブラックリスト語句のリテラル混入は引き続き禁止）

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

1. `spec/tx-v9.1.0-mindmap-core.md` を view（§0-tri / §0-quad / §0-bis / §1-bis 重点）
2. `{TARGET_PDF}` を読解（問題番号・科目・年度・全選択肢・正解・正答率・出題テーマ抽出）
3. 冒頭応答出力：「正答率__%→パターン_『___』適用」
4. Phase 2〜5.5 の 6 段階 Write プロトコルに従い `{OUTPUT_PATH}` に HTML を Write
5. Section 7（validate）→ Section 8（最大 3 回リトライ）→ Section 9 / 10 / 11（sentinel）の順で機械的に完了

`{PROBLEM_ID}` = `{PROBLEM_ID}` / `{OUTPUT_PATH}` = `{OUTPUT_PATH}` / `{TARGET_PDF}` = `{TARGET_PDF}` / `{PROBLEM_NUMBER}` = `{PROBLEM_NUMBER}`
