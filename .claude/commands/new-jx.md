---
description: 新規 JX ファイルを問題 PDF から生成（v3.2）
---

新規 JX ファイル（事例問題型 HTML 教材）を問題 PDF から生成する。

引数：問題 PDF のパス（例：`inputs/001_JX/{00N_科目}/重問PDF/15.pdf`）

## 必須手順

### Phase 0: 入力アラインメント・チェック（最初に必ず実行）

0. **逐語の解決とズレ検出**：`python scripts/check-jx-alignment.py {科目} {番号}` を実行。
   - `[OK]` → 表示された逐語ファイルを第一次情報源として使う。
   - `[ERROR]`（逐語欠落・keyword 不一致＝ズレ疑い）→ **生成を中断**し、内容照合で正しい逐語を特定して
     `inputs/001_JX/transcript-map.json` の `overrides` に追記してから再実行（無断推定禁止）。
   - **重問PDFと講義逐語は番号がズレる系列がある**（刑28/29/30 は −7 ズレ）。同番号を無断前提にしない。
   - 詳細：`docs/jx-pipeline.md` ①。

### Phase 1: 準備

1. **規律を view**：`spec/jx-v3.2-master.md` を view（第 0 項〜第 23 項＋付録 A〜C 全文）
   - **ゴールド参照**：`canonical/ATHENA.html` を構造・CSS・配色・`.lecturer-advice` の視覚参照に
     view してよい（GENESIS/KTX301 と同じ位置づけ）。**本文・解説の文章流用は禁止**（content independence）
2. **PDF 読解**：問題番号・科目・年度・事案・主要論点（通常 2 件）・関連条文・関連判例を抽出
   - **（補）講義逐語録の確認**：同じ問題の逐語録（`*_文字起こし.txt` 等が入力で渡された／
     `inputs/` 配下にある）場合は読み込み、論点ごとに要点を整理 → Phase 6 で
     `.lecturer-advice`（講師のアドバイス）として該当論点冒頭に配置（第13-2-bis項）
3. **三層ペルソナの統合判断**を意識する：
   - 法学教育者（出題傾向・採点基準・典型ミス）
   - 認知心理エディトリアル（チャンキング・視線誘導・系列位置効果）
   - 機能的色彩設計＋アートディレクター（全パレットから雰囲気で AI 自由選定／第5項）

### Phase 2: ファイル名・出力先の確定（CLAUDE.md §2 参照）

4. **PDF ファイル名から番号抽出**：最初の連続数字 → 3 桁ゼロ埋め
5. **科目接頭辞・出力先決定**：
   - 刑法 → `outputs/001_JX/001_刑法/刑JX{NNN}.html`
   - 憲法 → `outputs/001_JX/007_憲法/憲JX{NNN}.html`
   - 民法 → `outputs/001_JX/003_民法/民JX{NNN}.html`
   - 商法 → `outputs/001_JX/004_商法/商JX{NNN}.html`
   - 民訴 → `outputs/001_JX/005_民事訴訟法/民訴JX{NNN}.html`
   - 刑訴 → `outputs/001_JX/002_刑事訴訟法/刑訴JX{NNN}.html`
   - 行政法 → `outputs/001_JX/006_行政法/行政JX{NNN}.html`
6. **数字抽出不能なら処理中断** → ユーザーに番号確認

### Phase 3: 配色の AI 自由選定（全パレット・雰囲気選定）

> **2026-06-02 改訂**：科目アンカー固定色は**廃止**。5 役割と「pale bg + dark text」は TX と
> 共通だが、**パレットは 11 種に限定しない**。出典 `docs/palette-v3_2.pdf` の全 15 案
> （`docs/palette-v3-images/`）＋派生色から、**問題の雰囲気で AI が自由に配色を選定**する。

7. **問題の雰囲気から配色を AI 自由選定**（全 15 案＋派生・複数パレット組合せ可。
   `memory/reference_palette_v3.md` の 11 名前付きは代表例・出発点）：
   - 重厚・道徳・難解・深刻 → 落ち着いた／くすんだ／紫・スレート系（例：Antique Pearl / Dusty Sage / Twilight Violet / Maison Blanche）
   - 軽快・基礎・親しみ → 明るいピンク・ミント系（例：Sweet Berry / Fresh Citrus / Rose Mist / Mint Tea / Fresh Mint）
   - 手続・公共・清新 → ブルー・セージ系（例：Crystal Blue / Dusty Sage）／経済・活気 → 黄橙系
   - 対立が激しい・意外性 → アクセント反対色を強めに
   - **科目に紐付けず雰囲気で選ぶ**（同一科目でも問題ごとに別配色／必ずしも名前付き 1 つに収めない）
   - **冒頭応答**：採用配色の方向性と雰囲気の意図を 1〜2 文で出力冒頭に記述

8. **5 色を 5 役割へ割当て**（仕様書第 5-2 表）：
   - `--base`(約70%・最 pale)／`--accent`(約25%・最 chromatic を mid-tone 派生)／
     `--mid`(約5%・contrast 色・全パレット越境/派生 OK)／`--soft`(サブ1)／`--light`(サブ2)
   - `--text`／`--bg-dark` は白・黒・黒寄りグレー（text 用は L<40 dark 可）
   - **pale bg + dark text**：背景は薄色、見出し・文字は dark で contrast 確保
   - bg 系派生は L=55-65 mid-tone・**palette 外の独自 dark hex は禁止**
   - semantic 例外：✓ 緑 `#438B48`/`#7BA980`・🏆 金 `#ffd54f`/`#ffaa00` のみ palette 越境可
     （旧・行政JX 専用 `--accent-2:#6FC885` は廃止 → 肯定強調は semantic 緑を使用）

### Phase 4: タイポグラフィ（第 6 項 11 役割・TX 完全準拠）

9. **Google Fonts ロード**（必須）：第 6-2 表の `<link>` を `<head>` に。**TX `canonical/GENESIS.html` と完全一致**（Shippori Mincho B1 / Shippori Antique / Zen Old Mincho / Zen Kaku Gothic Antique / Zen Maru Gothic / Noto Serif JP / Noto Sans JP / Kaisei Decol / Kosugi Maru / Source Code Pro / M PLUS Rounded 1c / M PLUS 1p）
10. **CSS 変数定義**：第 6-3 表通り 11 役割（`--font-body`／`--font-soft`／`--font-display`／`--font-statute`／`--font-quote`／`--font-answer`／`--font-keyword`／`--font-judgment`／`--font-note`／`--font-professor`／`--font-mono`）＋ **TX 由来 `--font-impact`（M PLUS 1p・任意使用）**
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
24-bis. **講師のアドバイス（逐語録がある場合・必須）**：`.lecturer-advice`（第13-2-bis項）を
    該当論点・部の**冒頭**に配置。総論（問題処理パターン・検討順序）は第2部冒頭、論点固有の
    助言は各 `<h3>` 直後。逐語をそのまま貼らず**論点ごとに要点を整理**し、`.la-lead`（主題）／
    `.la-key`（核心語）／`.la-quote`（キーフレーズ）で構造化。バッジ＝accent→mid グラデ・
    背景＝選定パレット淡色パネル・左罫 7px（目立たせる）。CSS は :root と第13-2-bis項を反映し、
    `section>.lecturer-advice` 等をインデント防御・印刷・レスポンシブに登録

### Phase 7: レイアウト・印刷・JS

25. **container**：`max-width:1320px`／padding 第 8 項通り
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

### Phase 9: 副産物生成（RX / TREE / ARIADNE）— リモートでも必須（docs/rx-arb-byproducts.md）

> **背景**：副産物（Lexia 取込用の RX 論証カード・TREE 樹形図・ARIADNE 解法ナビ）は従来
> `jx-batch-runner.ps1`（PowerShell・ローカル専用）の ②-rx/②-arb/②-ariadne 段でしか作られず、
> **リモート（Claude Code on the web）で `/new-jx` 単発生成すると副産物が欠落**していた。
> 本 Phase で**リモート生成でも 3 種すべてを生成**する（バッチランナーと同じ成果物を揃える）。

35. **JX が J1〜J20 PASS したら、副産物 3 種を生成する**（**非致命**：副産物が失敗しても JX 本体の
    完了報告・push は妨げない）。各副産物は **`Agent`（general-purpose サブエージェント）を 1 つずつ起動**して
    生成させる（バッチランナーの「別 `claude -p` セッション」のリモート相当。メイン文脈を保護）。
    起動順は **RX → TREE → ARIADNE**。各サブエージェントには対応プロンプトの全文と、下表の
    repo 相対パス（プレースホルダ置換済み）を渡す。`{NNN}`＝3桁番号、`{ID}`＝`{科目接頭}JX{NNN}`、
    `{00N_科目}`＝出力先サブフォルダ（001_刑法/002_刑事訴訟法/003_民法/004_商法/005_民事訴訟法/006_行政法/007_憲法）。

    | 副産物 | 起動プロンプト | 出力先 | 検証 |
    |---|---|---|---|
    | **RX** | `prompts/new-rx-headless.md` 全文 | `outputs/ux/001_RX/{00N_科目}/`（基幹 `{科目接頭}RX{NNN}`） | `python scripts/validate-rx.py <出力DIR> {科目接頭}RX{NNN}` |
    | **TREE** | `prompts/new-arb-headless.md` 全文（**vendored モード**） | `outputs/ux/002_TREE/{00N_科目}/{ID}_TREE.html` | `python scripts/validate-tree.py <出力ファイル>` |
    | **ARIADNE** | `prompts/new-ariadne-headless.md` 全文 | `outputs/ux/000_ARIADNE/{00N_科目}/{ID}_ARIADNE.html` | `python scripts/validate-ariadne.py <出力ファイル>` |

    - **共通の素材**：いま生成・検証 PASS した JX HTML（`outputs/001_JX/{00N_科目}/{ID}.html`）が一次情報源。
      同一問題由来の再構成なので流用は正当（**他 JX からの流用は禁止**）。
    - **TREE は vendored モードで起動**：外部 arbor リポジトリはリモートに無いので、
      **`canonical/ARBOR.html`（gold TREE の正典複製）を構造・配色・密度の唯一の参照**にし、
      検証は `scripts/validate-tree.py`（T1〜T9）で行う。canonical/ARBOR.html の本文・論点は
      コピーせず**構造シェルのみ参照**（content independence）。密度は 13 分枝・葉 57・問題 15・約 68KB に揃える。
    - **ARIADNE は `canonical/ARIADNE.html` を複製起点**にする（プロンプト記載どおり）。
    - 各サブエージェントは末尾で sentinel（`BATCH_ITEM_COMPLETED:{ID}-RX` 等）を echo して終了する。
      検証 ERROR が残ったら最大 3 周修正。**3 種いずれかが失敗してもメインは続行**し、完了報告に成否を併記する。
    - **`<script>...</script>` 内 `</body>` リテラル禁止**は副産物にも適用（各 validate が機械検出）。

35-bis. **【push 前ゲート・必須】副産物そろい検査**（2026-06-22 追加・「HTML＋TTS だけ」push の
    再発防止＝別PC生成の 刑JX056〜063 が副産物ゼロで push された実害への恒久対策）。
    Phase 10 の push に進む**前に**、3 種の出力が実在するかを **Glob/ls で機械的に確認**する：

    | 系統 | 存在条件 |
    |---|---|
    | **RX** | `outputs/ux/001_RX/{00N_科目}/{ID}/` に `{科目接頭}RX{NNN}_*.html` が **1 枚以上** |
    | **TREE** | `outputs/ux/002_TREE/{00N_科目}/{ID}_TREE.html` が存在 |
    | **ARIADNE** | `outputs/ux/000_ARIADNE/{00N_科目}/{ID}_ARIADNE.html` が存在 |

    - 各系統の **validate（validate-rx / validate-tree / validate-ariadne）が PASS** であることも併せて確認。
    - **欠落・未検証があれば、その系統の `Agent` を最大 2 回まで再起動**して埋める（RX→TREE→ARIADNE のうち
      欠けている分のみ・非致命の「黙って継続」を打ち切るための強制リトライ）。
    - 再試行後も揃わない系統が残る場合に限り push に進んでよいが、**完了報告とコミットメッセージの双方に
      「副産物欠落: {欠落系統}」を明示**する（黙って成功扱いにしない）。3 種すべて揃えば通常どおり Phase 10 へ。
    - **このゲートを通すまで Phase 10 の push をしてはならない**（揃っていれば即進む）。ローカルなら
      代替として `pwsh -NoProfile -File scripts/rx-arb-backfill.ps1 -Subject {科目} -Number {NNN}` でも補完可。

### Phase 10: 回収（永続化）と後始末（docs/jx-pipeline.md ②③）

36. **回収＝git push**：`scripts/jx-push.sh "feat(jx): {ID} を生成保存（J1〜J21 PASS＋副産物 RX/TREE/ARIADNE）"`
    （add→commit→push、ネットワークエラー時は指数バックオフ再試行。リモートはコンテナ回収前に必ず push）。
    **コミットメッセージは 35-bis ゲートの結果を反映する**：3 種揃っていれば上記どおり、欠落が残った場合は
    末尾に「／副産物欠落: {欠落系統}」を付す（後で backfill 対象と分かるように）。
    **jx-push.sh は既定で `outputs/001_JX` ＋ `outputs/ux` を stage する**ので、本体 JX と副産物が同じ push で永続化される。
37. **処理済 PDF 削除**：`scripts/jx-cleanup-pdf.sh {科目} {番号} --commit` →
    `scripts/jx-push.sh "chore(jx): remove processed input PDFs"`（HTML が commit 済のときのみ削除＝安全ガード）。
38. **ERROR があれば**：該当箇所を修正し、再検証 → 通過するまで繰り返し

## 鉄則（絶対遵守）

- **三層ペルソナ統合判断**（一層でも欠けた出力は不完全）
- **配色：全パレット（全 15 案＋派生）から問題の雰囲気で AI 自由選定し 5 役割に割当て**（11 種に限定しない・科目固定色は廃止）
- **pale bg + dark text／WCAG AA 4.5:1／5 系統制限**を守る（色そのものの選定は自由・semantic 緑/金は維持）
- **11 役割タイポ完全遵守＋ `--font-impact`**（Google Fonts リンクは TX GENESIS と完全一致）
- **他 JX ファイルの本文・解説・判例引用を流用禁止**（各問題固有の独自設計）
- **`<script>...</script>` 内に `</body>` リテラル文字列禁止**（Lexia アプリ正規表現マッチで全機能死亡）
- **JX v3.2 が要求する全ての色変更・装飾追加を実装**（v3.1 互換だけでは不十分）

## 注意点

- **JX は処理時間が長い**（1〜2 時間／問）。途中で中断せず最後まで生成する
- **HTML サイズが大きい**（数百 KB〜1 MB 規模）。トークン消費を考慮し、必要な仕様書節を `view_range` で部分的に取得する戦略を取ってもよい
- **肯定／許容の限定強調**は全科目共通で semantic 緑 `#438B48`／`#7BA980` を使用（旧・行政JX 専用 `--accent-2:#6FC885` 固定は廃止）

$ARGUMENTS
