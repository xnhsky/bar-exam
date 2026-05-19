---
description: 新規 JX ファイルを問題 PDF から生成（v3.2）
---

新規 JX ファイル（事例問題型 HTML 教材）を問題 PDF から生成する。

引数：問題 PDF のパス（例：`inputs/jx-pdfs/15.pdf`）

## 必須手順

### Phase 1: 準備

1. **規律を view**：`spec/jx-v3.2-master.md` を view（第 0 項〜第 23 項＋付録 A〜C 全文）
2. **PDF 読解**：問題番号・科目・年度・事案・主要論点（通常 2 件）・関連条文・関連判例を抽出
3. **三層ペルソナの統合判断**を意識する：
   - 法学教育者（出題傾向・採点基準・典型ミス）
   - 認知心理エディトリアル（チャンキング・視線誘導・系列位置効果）
   - 機能的色彩設計＋アートディレクター（アンカー二色制＋AI 創造設計の 3 色）

### Phase 2: ファイル名・出力先の確定（CLAUDE.md §2 参照）

4. **PDF ファイル名から番号抽出**：最初の連続数字 → 3 桁ゼロ埋め
5. **科目接頭辞・出力先決定**：
   - 刑法 → `outputs/jx/刑JX/刑JX{NNN}.html`
   - 憲法 → `outputs/jx/憲JX/憲JX{NNN}.html`
   - 民法 → `outputs/jx/民JX/民JX{NNN}.html`
   - 商法 → `outputs/jx/商JX/商JX{NNN}.html`
   - 民訴 → `outputs/jx/民訴JX/民訴JX{NNN}.html`
   - 刑訴 → `outputs/jx/刑訴JX/刑訴JX{NNN}.html`
   - 行政法 → `outputs/jx/行政JX/行政JX{NNN}.html`
6. **数字抽出不能なら処理中断** → ユーザーに番号確認

### Phase 3: 配色アンカー取得（第 5-1 表）

7. **科目別 `--accent`／`--mid`** を仕様書第 5-1 表から取得：
   - 刑JX：`--accent:#2d7282` 深ティール／`--mid:#00adc1` 鮮ティール
   - 刑訴JX：`--accent:#585257` スレート／`--mid:#94b5b2` スモーキー
   - 民JX：`--accent:#582341` 深プラム／`--mid:#a53d59` ローズ
   - 商JX：`--accent:#B5611A` 深オレンジ／`--mid:#ED9455` 鮮オレンジ
   - 民訴JX：`--accent:#6e618e` パープル／`--mid:#bda4a1` ローズブラウン
   - 行政JX：`--accent:#425B80` ネイビー／`--mid:#78B9C6` スカイ／`--accent-2:#6FC885` 鮮グリーン（行政のみ）
   - 憲JX：`--accent:#14518e` ロイヤル／`--mid:#c59650` ゴールド
8. **AI 創造設計の 3 色**：`--light`／`--base`／`--soft` をアンカーに対する対比または調和で設計

### Phase 4: タイポグラフィ（第 6 項 11 役割）

9. **Google Fonts ロード**（必須）：第 6-2 表の全フォントを `<head>` に `<link>`
10. **11 役割 CSS 変数定義**：第 6-3 表通り（`--font-body`／`--font-soft`／`--font-display`／`--font-statute`／`--font-quote`／`--font-answer`／`--font-keyword`／`--font-judgment`／`--font-note`／`--font-professor`／`--font-mono`）
11. **base CSS 適用**（第 6-5 表）：`body` の `line-height:2.0`／`letter-spacing:.04em`／`font-weight:500`

### Phase 5: 全体構造（第 3 項）

12. **第 0 部 凡例**：4 ブロック（追加禁止）＋オプションのフォント運用ガイド
13. **第 1 部 俯瞰**：本問の事案を短く図解／論点提示
14. **第 2 部 本論**：主要論点 × A〜H 8 サブセクション構成
    - A 事案要旨・B 論点抽出・C 規範定立・D あてはめ・E 結論・F 補足・G 関連知識・H 失点回避チェックリスト
15. **第 3 部 採点講評**：第 14 項必須項目
16. **第 4 部 体系化**：論点間優先順位フロー＋実務コラム
17. **第 5 部 完全プロファイル**：5-1 条文集／5-2 判例集／5-3 学説一覧／5-4 答案論証集／5-5 用語集／5-6 略語出典一覧（back-refs ≥ 3 必須）

### Phase 6: v3.2 必須コンポーネント

18. **`.key-box`**：豪華装飾化（specificity 防御セレクタ三者結合・`::before` に `🔑 KEY` ラベル）
19. **ラベル付きカード型**：`.note-box`（💡 NOTE）／`.warn-box`（⚠ WARN）／`.success-box`（✓ TIP）／`.danger-box`（✗ NG）の全 4 種
20. **`blockquote.statute`**：薄グレー（`#f3f4f6`）／**`blockquote.case`**：薄ピンク（`#ffeef1`）
21. **判旨段落**：`.judgment-text` クラスで Zen Old Mincho 700 化
22. **第 N 項網掛け**：`<strong>第N項</strong>` ではなく `<span class="para-num">第N項</span>`
23. **模範答案**：`.model-answer` ラベル付き（しっぽりアンチック）
24. **採点講評**：`.grading` ラベル付き

### Phase 7: レイアウト・印刷・JS

25. **container**：`max-width:1080px`／padding 第 8 項通り
26. **doc-header**：`position:absolute` で右上配置（第 7-1 項）
27. **本文インデント**：本文段落のみ `padding-left:1.4em`（第 23 項・specificity 防御で `.key-box` 等は除外）
28. **第 18 項レスポンシブ**＋**第 17 項印刷最適化**
29. **第 19 項末尾 JavaScript**：スムーズスクロール
30. **第 20 項フッター**：励まし文言必須

### Phase 8: 検証と配信

31. **第 22 項チェックリスト全項目**を自己確認
32. **検証実行**：
    ```bash
    python scripts/validate-jx.py <出力ファイル>
    ```
33. **J1〜J20 ERROR 0 件確認**
34. **ERROR 0 件確認後**：`present_files` で完了報告
35. **ERROR があれば**：該当箇所を修正し、再検証 → 通過するまで繰り返し

## 鉄則（絶対遵守）

- **三層ペルソナ統合判断**（一層でも欠けた出力は不完全）
- **科目アンカー `--accent`／`--mid` は第 5-1 表通り改変禁止**（パレットは固定）
- **`--light`／`--base`／`--soft` は AI の創造設計**（accent との対比または調和）
- **11 役割タイポ完全遵守**（v3.1 の 6 役割からの拡張・5 役割追加が必須）
- **他 JX ファイルの本文・解説・判例引用を流用禁止**（各問題固有の独自設計）
- **`<script>...</script>` 内に `</body>` リテラル文字列禁止**（Lexia アプリ正規表現マッチで全機能死亡）
- **JX v3.2 が要求する全ての色変更・装飾追加を実装**（v3.1 互換だけでは不十分）

## 注意点

- **JX は処理時間が長い**（1〜2 時間／問）。途中で中断せず最後まで生成する
- **HTML サイズが大きい**（数百 KB〜1 MB 規模）。トークン消費を考慮し、必要な仕様書節を `view_range` で部分的に取得する戦略を取ってもよい
- **行政JX は `--accent-2:#6FC885`** が追加定義される唯一の科目（`.success-box` 系の限定強調用）

$ARGUMENTS
