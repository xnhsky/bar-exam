---
description: 既存 JX HTML を v3.2 にアップグレード
---

既存の JX ファイル（v3.1 以下）を JX v3.2 にアップグレードする。

引数：対象 HTML ファイルのパス（例：`inputs/jx-legacy/民JX001.html` または `outputs/001_JX/003_民法/民JX001.html`）

## 必須手順

### Phase 1: 準備

1. **規律を view**：`spec/jx-v3.2-master.md` の以下を重点的に確認：
   - 冒頭の「v3.1 → v3.2 の主要変更（KTX v6.19 デザイン要素統合）」10 項目
   - 第 6 項（11 役割タイポグラフィ）
   - 第 13 項（v3.2 大幅強化された共通コンポーネント）
   - 第 23 項（本文インデント設計）
   - 付録 C（v3.1 → v3.2 移行クイックリファレンス）
2. **対象ファイルを view**：既存 HTML 全体を読み込み、現状の構造・色変数・タイポを把握
   - **ゴールド参照**：`canonical/ATHENA.html` を構造・CSS・配色・`.lecturer-advice` の視覚参照に
     view してよい（本文・解説の文章流用は禁止＝content independence）
   - **（補）講義逐語録の確認**：同じ問題の逐語録（`*_文字起こし.txt` 等）があれば読み込み、
     論点ごとに要点を整理 → Phase 4 で `.lecturer-advice`（第13-2-bis項）を該当論点冒頭に配置

### Phase 2: 旧スタイルの破棄（最優先）

3. 以下の旧パターンを **すべて破棄**：
   - 旧 6 役割タイポグラフィのみの記述（5 役割追加が必要）
   - `<strong>第N項</strong>` 表記（`<span class="para-num">第N項</span>` に置換）
   - `border-left` ベースの `.note-box` / `.warn-box` / `.success-box` / `.danger-box`（v3.2 はラベル付きカード型）
   - `.statute-emphasis` / `.case-emphasis` の `border-bottom`
   - `.key-box` の旧装飾（v3.2 は specificity 防御セレクタ三者結合 + `🔑 KEY` ラベル）
   - 旧 body 値（`line-height` 1.8 等）

### Phase 3: v3.2 必須項目の追加

4. **タイポグラフィ 11 役割化**（第 6 項）：以下 5 役割を CSS 変数に**追加**
   - `--font-keyword`（Kaisei Decol）
   - `--font-judgment`（Zen Old Mincho 700）
   - `--font-note`（Zen Kaku Gothic Antique）
   - `--font-professor`（Kosugi Maru）
   - `--font-mono`（Source Code Pro）
5. **Google Fonts ロード**（第 6-2 項）：`<link>` を **TX `canonical/GENESIS.html` と完全一致**に
   置換し、`--font-impact`（M PLUS 1p）も定義（11 役割＋impact）
5-bis. **配色を V3 自由選定へ移行**（第5項）：旧・科目アンカー固定色は破棄し、**全パレット
   （全 15 案＋派生）から問題の雰囲気で AI 自由選定**して 5 役割（`--base`/`--accent`/`--mid`/
   `--soft`/`--light`）に割当て。pale bg + dark text／WCAG AA／5 系統制限を守る（semantic 緑/金は維持）。
   旧色をハードコードした SVG fill・gradient 等も新配色へ一括置換（旧色残存ゼロを確認）
5-ter. **th 内リンクのコントラスト対策**（第13-3項）：`th a, th a.xref{color:#fff}` を追加
   （`a.xref` 既定色＝`--accent` が濃い th 背景と同化するため・必須）
6. **base CSS 更新**（第 6-5 項）：
   - `body { line-height:2.0; letter-spacing:.04em; font-weight:500; }`
7. **container 寸法調整**（第 8 項）：
   - `max-width:1080px`
   - モバイル padding: `0 20px 32px 20px`
   - デスクトップ padding: `0 40px 48px 40px`
8. **doc-header**（第 7-1 項）：`position:absolute` で右上配置

### Phase 4: コンポーネント刷新

9. **`.key-box` 豪華装飾化**（第 13-1 項）：
   - `padding:56px 44px 38px 72px`
   - radial 装飾
   - **specificity 防御セレクタ三者結合**：`.key-box`／`section .key-box`／`.container .key-box`
   - `::before { content:'🔑 KEY'; }` ラベル
   - Kaisei Decol フォント
10. **ラベル付きカード型刷新**（第 13-2 項）：
    - `.note-box::before { content:'💡 NOTE'; }`
    - `.warn-box::before { content:'⚠ WARN'; }`
    - `.success-box::before { content:'✓ TIP'; }`
    - `.danger-box::before { content:'✗ NG'; }`
    - **border-left 廃止**、全周 `border:1px` + 微外側 shadow + 内側白ライン
11. **引用差別化**（第 13-10 項）：
    - `blockquote.statute` → 薄グレー（`#f3f4f6`）
    - `blockquote.case` → 薄ピンク（`#ffeef1`）
12. **判旨段落**：`.judgment-text` クラス（Zen Old Mincho 700）を追加
13. **第N項網掛け**（第 13-11 項）：本文中の `<strong>第N項</strong>` → `<span class="para-num">第N項</span>` 全件置換
14. **模範答案**：`.model-answer::before { content:'MODEL ANSWER'; }` を追加（しっぽりアンチック）
15. **採点講評**：`.grading::before { content:'GRADING'; }` を追加
15-bis. **講師のアドバイス（逐語録がある場合・必須）**：`.lecturer-advice`（第13-2-bis項）を
    該当論点・部の冒頭に配置（総論は第2部冒頭、論点固有は各 `<h3>` 直後）。逐語をそのまま
    貼らず論点ごとに要点を整理し `.la-lead`/`.la-key`/`.la-quote` で構造化。バッジ＝accent→mid
    グラデ・背景＝選定パレット淡色・左罫 7px。`section>.lecturer-advice` 等をインデント防御・
    印刷・レスポンシブに登録

### Phase 5: 第 23 項本文インデント設計（v3.2 新設）

16. **本文段落のみ**：`padding-left:1.4em`
17. **specificity 防御**で除外：`.key-box` / `.note-box` / `.warn-box` / `.success-box` / `.danger-box` / `.lecturer-advice` / `blockquote` / `.model-answer` / `.grading` 内の `<p>` には適用しない

### Phase 6: マーカーの潰れ防止強化

18. `.tan` / `.hl-super` / `.hl-high` / `.hl-std` / `.exam-mark` 系の `letter-spacing` を `.06em〜.09em` に強化
19. マーカー透明度を `.42` に統一

### Phase 7: ファイル名・出力先（CLAUDE.md §2 命名規則）

20. **ファイル名を「{日本語接頭辞}JX{3桁0埋め}.html」形式**に揃える
21. **`<title>` / `.doc-header` / フッターのファイル ID** を一致させる
22. **出力先**：`outputs/001_JX/{科目JX}/` 配下（科目接頭辞に対応）

### Phase 8: 検証と配信

23. **検証実行**：
    ```bash
    python scripts/validate-jx.py <出力ファイル>
    ```
24. **J1〜J20 ERROR 0 件確認**
25. **ERROR 0 件確認後**：`present_files` で完了報告
26. **ERROR があれば**：該当箇所を修正し、再検証 → 通過するまで繰り返し

## 鉄則（絶対遵守）

- **三層ペルソナ統合判断**を維持（v3.1 で確立した法学教育者・認知心理・色彩設計の三層は v3.2 でも継承）
- **配色は V3 へ移行**（2026-06-02 統一）：旧・科目アンカー固定色は引き継がず、第 5 項の 11 名前付きパレットから**問題の雰囲気で 1 つ選び直し**、5 役割（`--base`/`--accent`/`--mid`/`--soft`/`--light`）に割当てる。palette 外 hex 禁止（semantic 緑／金のみ越境可）
- **フォントは TX と完全一致**：Google Fonts リンクを TX `canonical/GENESIS.html` に揃え、11 役割＋`--font-impact` を定義
- **第 21 項禁止事項を再点検**：通則違反を新たに作らない
- **他 JX ファイルからの本文引用は禁止**（v3.1 → v3.2 移行であっても本文は当該問題固有のまま）
- **`<script>...</script>` 内に `</body>` リテラル文字列禁止**（Lexia 致命的バグ）

## 注意点

- **JX のアップグレードは時間がかかる**（フル書換に近い・1〜2 時間／問）
- **検証通過まで部分配信しない**：1 問完成 → 検証通過 → 次の問題
- **付録 C 移行クイックリファレンスを必ず参照**：v3.1 → v3.2 の全変更点が網羅されている

$ARGUMENTS
