---
description: 新規 TX ファイルを問題 PDF から生成（v10.0.0-gold-skeleton：311 baseline + 配色 V2 + SVG 重なり検査）
---

新規 TX ファイル（短答式 HTML カード）を問題 PDF から生成する。

> **v10.0.0 GOLD-SKELETON 経路（2026-05-27 確定）**：刑TX311 で確定した「baseline HTML スケルトン
> + 配色 V2 (27 色 AI 自由選定) + SVG 重なり機械検査」の 3 本柱経路を新規生成の唯一の標準とする。
> 旧 v9.2.0 DEEP-DIVE 経路（§Annex B body skeleton + 6 段階 Write）は廃止。
> 旧 render.py 経路（JSON-render）も新規生成では使用しない（WIP 上書き事故予防）。

引数：問題 PDF のパス（例：`inputs/tx-pdfs/312.pdf`）

---

## 必須手順

### Phase 0：環境確認（最優先）

0a. **outputs/tx/{対象科目}/ に既存ファイルがあるか確認**
    - 既存ファイルが存在しても **template として Read/Edit 起点にしない**
    - 同番号が既存の場合のみユーザーに上書き可否を確認

0b. **`_quarantine*` や非 canonical フォルダが復活していないか確認**
    - 復活している場合は `bar-exam-archive\` への再排除を提案

0c. **直近のセッションログから「template 流用経路」が選ばれていないか確認**
    - `Read outputs/*.html` や `cp outputs/*.html` の痕跡があれば即停止して
      `canonical/KTX311-gold-baseline.html` から再開

### Phase 1：PDF 解析と配色 V2 判定

1. **PDF 読解**：問題番号・科目・年度・全選択肢・正解・正答率・出題テーマ・出題形式
   （single-choice-5 / ox-grid-5 / multi-choice / etc.）を抽出

2. **冒頭応答必須**：「正答率 __%→パターン_『___』適用」を最初に出力

3. **パターン判定**（配色 V2）：
   - 正答率 ≥ 60% → **P1** ピンクを使った可愛い配色
   - 正答率 40〜60% → **P2** グリーンを使った可愛い配色
   - 正答率 < 40% → **P3** ロマンティックなパープル配色

4. **Concept 設計**（AI 判断・問題ごとに別 Concept）：
   - テーマの重さ（道徳論点／重罪 → 落ち着き寄り、日常論点 → 爽やか）
   - 難度（易 → 明るめ、難 → 重め）
   - 罪名イメージ（財産罪 → ピンク系優先、身体犯 → 暖系、手続 → クール）
   - 正解の意外性（罠多い → コントラスト強、素直 → 同系統調和）

5. **色選定**：`memory/reference_ingectar_palette.md` の該当パターン 27 色から
   AI 判断で 15〜20 色を選択し、CSS 変数 ~20 個（`--accent` / `--mid` / `--light` /
   `--base` / `--soft` / `--bg-dark` / `--accent-3` / `--accent-soft` / `--border-mid` /
   `--kp-text-color` + 派生色 10 個）へ役割割当て

6. **Semantic exception**：
   - ✓ 緑（`--recall-correct`）：P2 #438B48 / #7BA980 を借用（P1/P3 採用時）
   - 🏆 金（ARENA）：`#ffd54f` / `#ffaa00` inline hex で保持（CSS 変数化しない）

### Phase 2：ファイル名・出力先の確定（CLAUDE.md §2）

7. **PDF ファイル名から番号抽出**：最初の連続数字 → 3 桁ゼロ埋め

8. **科目接頭辞・出力先決定**：
   - 刑法 → `outputs/tx/刑TX/刑TX{NNN}.html`
   - 憲法 → `outputs/tx/憲TX/憲TX{NNN}.html`
   - 民法 → `outputs/tx/民TX/民TX{NNN}.html`
   - 商法 → `outputs/tx/商TX/商TX{NNN}.html`
   - 民訴 → `outputs/tx/民訴TX/民訴TX{NNN}.html`
   - 刑訴 → `outputs/tx/刑訴TX/刑訴TX{NNN}.html`
   - 行政法 → `outputs/tx/行政TX/行政TX{NNN}.html`

9. **数字抽出不能なら処理中断** → ユーザーに番号確認

### Phase 3：Baseline スケルトンの取得

10. **`canonical/KTX311-gold-baseline.html` を Read**（構造参考の唯一の正典）
    - 例外：`canonical/KTX301.html` も「構造参考」として Read 可
      （ただし 311 baseline の方が v10.0.0 設計に沿うため優先）

11. **対象ファイル名でコピー作成**（PowerShell `Copy-Item` または Write 経由）：
    ```powershell
    Copy-Item canonical/KTX311-gold-baseline.html outputs/tx/{科目TX}/{接頭辞}{NNN}.html
    ```

12. **コピー直後に本文初期化**（content-independence 確保）：
    - PART A `.problem-text` 本文
    - 各 choice-section の `.sub-card.original`／`.sub-card.explanation`／
      `.sub-card.basis-link`／`.sub-card.professor` 本文
    - PART A-3（参考｜共通根拠条文・判例）の各 `.basis-card-body` 本文
    - PART C C-1〜C-7 各 section 本文（table 内容含む）
    - SVG 内の `<text>` 要素テキスト（座標・class は据置・テキストのみ空文字列化）
    - PART D drill-block × 12 の問題文・解説
    - footer-spec 1〜3 行目
    - これらを **空文字列で初期化**してから問題 PDF を見て新規執筆

### Phase 4：section-by-section 内容差替

各 section を独立して差替える。**1 メッセージで 50KB 超の Write/Edit は禁止**
（API socket error 予防）。Edit 単位で section ごとに分割。

#### 4a. HEAD（`<style>` 内 `:root{}`）の配色 V2 適用
- Phase 1-5 で決定した CSS 変数 ~20 個を `:root{}` に反映
- 派生色 10 個（`--accent-darker`／`--mid-warm` 等）も合わせて設定
- header／footer の表示テキストには **配色情報を書かない**（Concept 説明文を入れない）

#### 4b. HEADER 差替
- `<div class="doc-header">` の問題番号
- `<h1>` の問題タイトル（出典・テーマ）
- `.exam-badge`（科目／試験種別／年度／問題番号）
- `.theme-tag`（本問の主要論点 5〜10 個）
- `.exam-meta`：**正答率と難度のみ**（配色記載なし）
- `.toc-row`（本問の section リンク）

#### 4c. PART A 差替（出題形式に応じて）
- A-1 `.problem-text`：PDF 逐語コピー
- A-2 `.answer-area`：
  - `data-answer-type` を出題形式に合わせて設定（single / multi / ox-grid）
  - `data-correct-value` を正解値で設定（例：`5` / `1,3` / `11112`）
  - `<button class="reveal-answer-btn" type="button" disabled>解答を表示</button>` 必須
  - `data-explanation` 先頭に正解値リテラル禁止（AP-37）

#### 4d. PART B 差替（記述ア〜オ または ○× 各記述）
- 各 choice-section に 4 sub-card（original / explanation / basis-link / professor）
- prof-heading 4 段構成 + key-phrase-box + analogy + warning + cross-link
- ref-stat / ref-case リンクは本問関連条文・判例の id を参照

#### 4e. A-3（参考｜共通根拠条文・判例）差替
- 本問に直接関係する条文・判例のみ 3〜5 枚に絞る（AI 判断）
- `.basis-card.statute` / `.basis-card.case` で振り分け
- 各 `.basis-card-body` は本問の文脈で執筆

#### 4f. SVG 差替（座標は 311 baseline のまま、テキスト・色 class のみ）
- **体系ツリー** (mindmap-tree)：L0/L1/L2/L3 の text を本問体系に
- **論点マインドマップ放射** (mindmap-radial)：8 主要枝・サブ要素 text を本問論点に
- **C-5 総合フローチャート** (flow-svg)：decision diamond / chip / end の text を本問判断フローに
- 詳細は **Phase 5 SVG 重なり検査** で全 bounding box を機械検査してから出力

#### 4g. PART C 差替（C-1〜C-7）
- C-1 体系図解説（key-phrase-box + cmp-table）
- C-2 概念比較・全肢俯瞰（cmp-table 2 枚）
- C-3 cross-grid（関連の深い科目との接続・3 cross-card）
- C-4 学説対立（cmp-table + theory-detail-grid：主要説 vs 少数説）
  - 主要 2 説を AI 判断で選定
  - dt.why-adopted / why-not-adopted 必須
- C-5 総合フローチャート（4f で配置済）+ 解説
- C-6 ref-cases（重要判例 1〜3 件詳細）
- C-7 memory-item（3 層 priority-a/b/c）

#### 4h. PART D 差替（ARENA drill 12 問）
- ○×=6:6 で構築（本問オリジナル）
- 各 drill-block：問題文・選択肢・解説（本問関連で完結）

#### 4i. footer-spec 差替
- 1 行目：`<strong>{接頭辞}{NNN}</strong>・{科目}（{出典}）`
- 2 行目：`正答率 {N}%／難度 {★}`（**配色情報は書かない**）
- 3 行目：`作成日：{YYYY-MM-DD}`
- `.footer-meta-hidden` 内 feature-tag：
  - `TX v10.0.0 GOLD-SKELETON`（必須・先頭）
  - `ktx311-baseline`／`palette-v2-ai-selection`／`svg-overlap-checked`／
    `content-independence`／`jp-prefix-naming`

### Phase 5：SVG 重なり機械検査（必須・新規）

13. SVG 3 種すべての `<rect>` / `<ellipse>` / `<polygon>` について bounding box
    `(x_min, x_max, y_min, y_max)` を計算

14. 全ペアで衝突判定：
    `x_min_A < x_max_B AND x_max_A > x_min_B AND y_min_A < y_max_B AND y_max_A > y_min_B`
    が成立してはならない

15. マージン 16px 以上を確認（重なりなくても窮屈な隙間は避ける）

16. **衝突発見時の対処順序**（[[feedback-svg-box-overlap]]）：
    1. viewBox 拡張（最も安全・他要素への影響なし）
    2. 中心から放射する要素を更に外側へ
    3. ラベル短縮（最終手段）

### Phase 6：検証と配信

17. **新仕様 validate 実行**：
    ```bash
    python scripts/validate-tx-gold.py <出力ファイル>
    ```

18. **G1〜G15 ERROR 0 件確認**：
    - G1〜G5：構造（HEAD/HEADER/PART A〜D/footer 存在）
    - G6〜G8：配色 V2（:root 内 CSS 変数 ~20 個・派生色 10 個・配色情報がヘッダー／フッター本文にない）
    - G9〜G11：SVG（3 種存在・ボックス重なり 0 件・viewBox 余白十分）
    - G12〜G13：content-independence（KTX301 / KTX311 本文逐語コピー禁止）
    - G14〜G15：命名規則（ID 形式・出力先サブフォルダ）

19. **視覚確認推奨**：ユーザーがブラウザで開いて gold quality 到達判定

20. **ERROR 0 件 + 視覚 OK** → `present_files` で完了報告

21. **ERROR があれば**：該当箇所を修正し、再検証

---

## 鉄則（絶対遵守）

### template 流用の物理的禁止（最重要）

- **`outputs/*/` 配下の既存 HTML を別問題生成の template として
  `cp` / `Read` / `Edit` の起点にすることは絶対禁止**
- **唯一許可される起点**：`canonical/KTX311-gold-baseline.html`（最優先）
  および `canonical/KTX301.html`（補助・構造参考のみ）
- 既存 `.html` を「速い経路」として参照することは canonical text leakage の温床

### canonical text leakage の禁止

- canonical/KTX311-gold-baseline.html および KTX301.html の本文・解説・判例引用を
  別問題ファイルにコピー禁止（AP-42）
- スケルトンを clone した直後に **本文を空文字列で初期化**してから執筆開始

### render.py 経路の禁止

- **`python scripts/render.py {問題番号}` 実行禁止**：JSON-render 結果が target ファイルを
  上書きし WIP 作業全消失（過去事故あり）
- 新規生成は問題 PDF + canonical baseline のみから新規鋳造

### 配色 V2 の越境（Semantic exception）

- ✓ 緑（recall-correct）：P1/P3 採用時も P2 緑 #438B48 / #7BA980 を借用
- 🏆 金（ARENA）：全パターンで #ffd54f / #ffaa00 inline hex 保持
- 詳細：[[feedback-semantic-exceptions]]

### SVG ボックス重なり禁止

- Phase 5 の機械検査を必ず実施
- 311 で「本問の論点ボックス」が左右サブ要素と重なる事故あり
- 詳細：[[feedback-svg-box-overlap]]

### ヘッダー／フッター本文への配色記載禁止

- `.exam-meta` 内に「配色: P1 …」を書かない
- `.footer-meta-info` に「配色 P1「…」AI 自由選定」を書かない
- 配色情報は CSS の `:root{}` と footer-spec hidden feature-tag のみに記載

### 単一巨大出力の禁止（API socket error 予防）

- **1 メッセージで 50KB 超の `Write` / `Edit` 出力は禁止**
- section-by-section で Edit を分割（各 30〜50 KB 以下）

### 中断・再開時の禁則

- API socket error 等で中断した場合、**既存 outputs/*.html を template として
  参照する経路を選んではならない**
- 必ず canonical/KTX311-gold-baseline.html + PDF から続行
- 失敗した section だけ再生成し、他 section は流用しない

### 行動原則

- **「保守的書き換え」を絶対にしない**（既存コードを引き継ごうとする AI の癖を強制無効化）
- **冒頭応答必須**：「正答率__%→パターン_『___』適用」

$ARGUMENTS
