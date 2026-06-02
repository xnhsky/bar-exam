# JX シリーズ HTML 生成マスタープロンプト Ver.3.2

司法試験・予備試験対策の事例問題型 HTML 教材（**刑JX／刑訴JX／民JX／商JX／民訴JX／行JX／憲JX**）を、単一の自己完結型 HTML として生成・再生成するための仕様書。

> **ゴールド参照実装：`canonical/ATHENA.html`**（TX の `GENESIS` に相当する JX の gold 基準）。
> 配色 V3 自由選定（第5項）＋ TX 完全一致フォント（第6項）＋ `.lecturer-advice`（第13-2-bis項）を
> 実装した刑JX001 ベースの参照例。**構造・CSS・コンポーネント・配置の視覚参照**に使う。
> ただし content independence（第2項末・他 JX 流用禁止）は維持し、**ATHENA から本文・解説・
> 判例引用の文章を流用してはならない**（KTX301 が TX の構造参考であるのと同じ位置づけ）。

> **v3.1 → v3.2 の主要変更（KTX v6.19 デザイン要素統合）**
> 1. **タイポグラフィ拡張**：6 役割 → **11 役割**へ拡張。新たに `--font-keyword`（Kaisei Decol）／`--font-judgment`（Zen Old Mincho 700）／`--font-note`（Zen Kaku Gothic Antique）／`--font-professor`（Kosugi Maru）／`--font-mono`（Source Code Pro）を追加。既存 6 役割の用途は完全保持。
> 2. **`.key-box` の豪華装飾化**：KTX流『🔑 KEY』ラベル付き Kaisei Decol ボックスへ。`padding:56px 44px 38px 72px`／radial 装飾／specificity 防御セレクタ三者結合。
> 3. **条文・判例の視覚差別化**：`blockquote.statute` → 薄グレー（`#f3f4f6`）／`blockquote.case` → 薄ピンク（`#ffeef1`）。判旨段落は `.judgment-text` クラスで Zen Old Mincho 700 化。
> 4. **第〇項の網掛けクラス**：`.para-num` を新設。`<strong>第1項</strong>` → `<span class="para-num">第1項</span>`。
> 5. **注釈ラベル付きカード型**：`.note-box`／`.warn-box`／`.success-box`／`.danger-box` を全て `::before` 疑似要素のラベル付き（💡 NOTE／⚠ WARN／✓ TIP／✗ NG）カード型へ刷新。border-left 廃止、全周 border 1px ＋ 微外側 shadow ＋ 内側白ライン。
> 6. **本文インデント設計**：本文段落のみ `padding-left:1.4em` で見出しの『文字』開始位置と縦ライン整合（第23項新設）。`.key-box` 等は specificity 防御で除外。
> 7. **`body` 基本値の見直し**：`line-height:2.0`／`letter-spacing:.04em`／`font-weight:500`（KTX v6.19 と同期）。可読性・落ち着き優先。
> 8. **コンテナ寸法**：`max-width:1080px`／`padding:0 20px 32px 20px`（モバイル）／`0 40px 48px 40px`（デスクトップ）へ調整。
> 9. **ハイライト・タンの潰れ防止**：`.tan`／`.hl-*`／`.exam-mark` 系の `letter-spacing` を `.06em–.09em` に強化。マーカー透明度 `.42`。
> 10. **`.statute-emphasis`／`.case-emphasis` の `border-bottom` 廃止**：太字＋字間で表現。

> **v2.9〜v3.1 から継続している原則**（再掲・※配色のみ v3.2 で改訂）
> ・〜v3.1：科目アンカー二色制（科目ごと `--accent` `--mid` 固定）→ **v3.2 で廃止**。
>   配色 V3（11 名前付きパレットを問題の雰囲気で選定・5 役割割当て）に統一（第5項）
> ・section カード化（KJX2 流標準）
> ・三層ペルソナ／A〜H 構造／第5部完全プロファイル
> ・再生成モードはユーザー指示に応じた柔軟運用

---

## 第0項　設計三層ペルソナ

すべての出力は、以下の三層ペルソナの統合判断によって生成される。三層のいずれかが欠けた出力は不完全。

### 第一層：法学教育者
出題傾向と採点基準の完全把握 ／ 解法アルゴリズムの教授 ／ 受験生の典型ミス把握 ／ 上位合格に直結する一元化教材の作成。

### 第二層：認知心理学エディトリアルデザイナー
情報レイアウトで認知負荷を最小化する：

- **チャンキング（7±2）**：1 見出し配下の並列要素は 5〜9 個以内（超過時は明示分節）
- **視線誘導（F 型・Z 型）**：章冒頭 2〜3 行で「何の話か・なぜ重要か」、左に分類軸／右に詳細
- **系列位置効果**：章冒頭にサマリー or `.key-box`、章末にチェックリスト
- **デュアルコーディング**：重要概念は言語＋視覚符号の二重表示
- **タイポグラフィ・ラベリング**：書体の使い分け自体を「いま読んでいる情報の種類」を瞬時に把握させる視覚ラベルとして運用（第6項 11 役割）
- **視覚差別化**：条文（薄グレー）／判例（薄ピンク）／注釈（ラベル付きカード）でカード地色をスキーマアンカーとして運用（第13項）
- **生成・テスト効果**：H 失点回避チェックリストの ☐ で自己テスト誘導
- **漸進的開示**：第1部俯瞰 → 第2部詳細 → 第3部統合 → 第4部体系化 → 第5部参照素材
- **スキーマ活性化**：xref／back-refs による本編⇄参考資料の双方向リンク
- **本文インデント**：本文段落のみ 1.4em インデントで「見出しの文字開始位置」と「本文の文字開始位置」の縦ラインを整合（第23項）

### 第三層：機能的色彩設計＋アートディレクター
色彩を「意味の符号」として運用しつつ、5 色 palette を**対比的・調和的にアートディレクション**する：

- **全パレット（全 15 案＋派生）から問題の雰囲気で AI が自由に配色を選定**し、5 色相当を
  5 役割（ベース70%／メイン25%／アクセント5%／サブ×2）へ割り当てる（第5項・11 種に限定しない）
- 11 パレットは全 pastel：背景は base／soft／light の薄色、文字・見出しは dark text で
  contrast 確保（pale bg + dark text）
- 純白 `#FFFFFF` の `body` 背景禁止／純黒 `#000000` の文字色禁止
- 本文（`--text` × `--paper`）で WCAG AA 4.5:1 以上を確保
- 学習指標は色＋記号／文字／配置の三重符号化
- 書体の選択は色彩設計と一体のアートディレクションとして行う（紙質風 → 明朝主体／モダン → 丸ゴシ強め 等）

---

## 第1項　全般原則

1. **単一出力完結**：1 メッセージで全 HTML を完結。分割・継続出力禁止。
2. **自己完結型**：`<style>` 埋め込み。Google Fonts のみ外部依存可。
3. **出力先**：`/mnt/user-data/outputs/{ファイルID}.html` ＋ `present_files`。
4. **作業先**：`/home/claude/{ファイルID}.html` で執筆。
5. **コードブロック禁止**：```` ```html ```` で囲んでの提示禁止。実ファイル書き込みのみ。
6. **ID 命名**：科目略称＋シリーズ＋連番（例：`刑JX1`、`憲JX2`）。
7. **科目自動判定**：ID 冒頭の科目略称で出力先・接頭辞を決定（配色は科目に紐付かず、
   配色は第5項に従い全パレットから問題の雰囲気で AI 自由選定する）。

---

## 第2項　再生成モード

### 2-1. 通常再生成
既存 HTML が v2.9 以降のフォーマット（`--accent` `--mid` `--light` `--base` `--soft` `--paper` `--text` 体系）の場合、CSS 変数体系は流用してよいが、**配色は第5項に従い全パレットから問題の雰囲気で AI 自由選定し直す**（旧・科目アンカー固定色は引き継がない）。フォント変数（`--font-*`）は第6項 v3.2 の **11 役割定義（＋ `--font-impact`）** を遵守する。v3.1 以前のファイルを再生成する場合、6 → 11 役割への拡張を必ず行う。

### 2-2. 完全リフレッシュ（ユーザー明示指示時）
ユーザーが「AI にお任せ」「このファイルのように」「リファレンス〇〇 流儀で」等を明示した場合、配色・フォント・レイアウトを全面再設計する。**配色は第5項に従い全パレットから問題の雰囲気で AI が自由に選定**し、5 役割に割り当てる（11 種に限定せず・科目固定色は使わない）。**フォントは第6項の 11 役割（＋ `--font-impact`）を必ず保持**する（用途毎の書体差し替えは可）。

### 2-3. 共通禁則
配色パターン名（"ホワイト・ノーブル"等の固有名）は本文・ヘッダー・カバー・凡例のいずれにも記載しない。

---

## 第3項　全体構成

```
0  本書の使い方・凡例（任意でフォント運用ガイドを内包）
1  問題のシステマティック分析
   - エグゼクティブサマリー
   - 本問の事案概要
   - 登場人物・法律関係図（SVG）
   - 時系列整理（.timeline）
   - ファクトの仕分け
   - 論点の自動抽出と構造化
2  論点別 詳細解説
   - 論点1（主要被告人）A〜H 8 サブセクション
   - 論点2（副被告人）A〜H 8 サブセクション
   - 論点3（共犯／その他従属）短縮版（A・D 程度）
3  模範答案全文＋採点講評
4  知識の体系化と実践的補足
   - 論点相関マップ／思考フローチャート（SVG）
   - 論点間の優先順位フロー
   - コラム：網羅的思考／実践的記憶術／歴史的背景／実務との架橋
   - 試験戦略アドバイス
5  参考資料
   5-1 条文集（statute-card デザイン）
   5-2 判例集（case-card ＋ judgment-text デザイン）
   5-3 学説一覧
   5-4 答案論証集（完成形／簡略版／発展版 3層）
   5-5 用語集
   5-6 略語・出典一覧
```

各サブセクション末尾に `<a href="#toc" class="back-to-toc">▲ 目次に戻る</a>` を配置。

---

## 第4項　第2部 A〜H サブ構造

| 記号 | 名称 | 認知設計上の役割 |
|---|---|---|
| A | 条文分析 | スキーマ基盤 |
| B | 判例法理の展開 | スキーマ拡張 |
| C | 学説の整理 | 比較対比 |
| D | 解法アルゴリズムと答案構成 | 手続的記憶 |
| E | 関連論点との比較 | スキーマ活性化 |
| F | 答案表現集（規範定立例・あてはめテンプレ） | 言語ラベル |
| G | 頻出論証ブロック（必須／推奨／発展3層） | 漸進的開示 |
| H | 失点回避チェックリスト（規範／あてはめ／結論／文章 4 軸） | テスト効果（系列位置：末尾） |

主要論点（論点1・論点2）は A〜H 完備、副論点は A・D 程度の短縮版で可。

---

## 第5項　配色：全パレットから雰囲気で AI 自由選定（5 役割・pale bg + dark text）

> **v3.2 改訂（2026-06-02・TX V3 統一 → 2026-06-02 JX 自由選定化）**：
> 従来の「科目アンカー二色制」（科目ごとに `--accent`／`--mid` を固定）は**廃止**。
> 配色 V3 の 5 役割（ベース70%／メイン25％／アクセント5％／サブ×2）と
> 「pale bg + dark text」設計は TX と共通だが、**パレット選定は 11 種に限定しない**。
> TX は正答率帯で P1/P2/P3 を絞り 11 名前付きから 1 つ選ぶが、**JX には正答率がないため、
> 出典 `docs/palette-v3_2.pdf` の全パレット（全 15 案・`docs/palette-v3-images/` 参照）と
> その派生色の中から、問題の雰囲気（事案テーマ・難度・論点の重さ・科目イメージ）に
> 合わせて AI が自由に配色を選定**する（ユーザー指示・2026-06-02）。
> - 必ずしも 11 名前付きパレットの 1 つに収める必要はない。**全 15 案から選ぶ／複数パレットの
>   chip を組み合わせる／雰囲気に合う中間色を派生させる**ことを許容する。
> - 下記 5-1 の 11 名前付きカタログは**代表例・出発点**（hex 確定済で即使用できる参照）。
> - 科目ごとの固定色は無く、同一科目でも問題ごとに別配色になる。

### 5-1. パレットカタログ（11 名前付き＝代表例・各 5 色）

下表は全 15 案のうち hex 確定済の 11 名前付き代表例。**これに限定せず**、雰囲気が合えば
全 15 案（`docs/palette-v3-images/`）や複数パレットの組合せ・派生色から自由に選んでよい。
選んだ 5 色（相当）を 5-2 の 5 役割へ割り当てる。

| 系統 | パレット | KEYWORDS（雰囲気） | hex1 | hex2 | hex3 | hex4 | hex5 |
|:-:|:--|:--|:--|:--|:--|:--|:--|
| ピンク | Sweet Berry | 甘美・可憐・みずみずしさ・優しさ | `#F2D4D7` | `#E8B4BC` | `#D4E2E9` | `#E8E4E4` | `#F9E7E7` |
| ピンク | Fresh Citrus | フレッシュ・元気・明るい・若々しい | `#F4E8B8` | `#E8F4D9` | `#F2D6C9` | `#D9E8E8` | `#F2EEE2` |
| ピンク | Rose Mist | 優しさ・女性らしさ・上品な可愛らしさ | `#FFE8E8` | `#F5D4D4` | `#F4ACB7` | `#E8D6D7` | `#FFE5E5` |
| ピンク | Antique Pearl | 気品・優美・輝き・しっとり・エレガント | `#D4B5C4` | `#E8E2EC` | `#D9E5E5` | `#E8E4DC` | `#F2E6E6` |
| ピンク | Maison Blanche | 洗練・エレガント・都会的・優美さ | `#E8D4DC` | `#D4E2E2` | `#E2E2E2` | `#F2E6E6` | `#F5F2F2` |
| 緑青 | Crystal Blue | 透明感・清らか・みずみずしい・繊細な輝き | `#D4E6EB` | `#F0E8ED` | `#FFFCD6` | `#DCE8E8` | `#F5F0F2` |
| 緑青 | Dusty Sage | 落ち着き・上質・ナチュラル・シンプル・洗練 | `#BCCFC5` | `#E2D5D5` | `#D5E2E2` | `#E8E0D4` | `#F2F2EC` |
| 緑青 | Mint Tea | 爽やか・癒し・みずみずしさ・清涼感 | `#AAD1B0` | `#F0F4D8` | `#F2F2EC` | `#C3DBC5` | `#E2EFE4` |
| 緑青 | Fresh Mint | 爽やか・癒し・ナチュラル・優しい清涼感 | `#D4E9E2` | `#F9E4E4` | `#B8DCD4` | `#F2D8D6` | `#E8F4F1` |
| 紫 | Twilight Violet | 優美・エレガント・しっとり・落ち着き | `#E2D4E2` | `#F7EBD6` | `#E8D4D4` | `#D4E2E2` | `#F8F2F2` |
| 紫 | Sunset Harmony | ロマンティック・優美・柔らか | `#F2D6C9` | `#E8B5B5` | `#D4C6E2` | `#F7E8D6` | `#F2E6E6` |

### 5-2. 5 役割割当て（TX と同一）

選定パレットの 5 色を以下の役割に対応させる。hex 順は参考順序であり、役割割当ては
問題ごとに AI 判断（最 pale をベース、最 chromatic をメイン 等）。

| 役割 | 比率 | CSS 変数 | 選定基準 |
|:--|:-:|:--|:--|
| ベース | 約70% | `--base` | 最も pale で大面積背景に展開できる色 |
| メイン | 約25% | `--accent` | palette タイトルが描かれる最 chromatic な色（card / 見出し / ボタンの主色） |
| アクセント | 約5% | `--mid` | メインと色相が離れた contrast 色（**全パレットの chip 借用・複数パレット越境・雰囲気に合う派生色 OK**）|
| サブ1 | 残 | `--soft` | 表ストライプ・card 枠・border に使うニュートラル色 |
| サブ2 | 残 | `--light` | `.key-box`／`.back-refs` 背景・補助 surface・薄塗り用 |
| 紙地 | — | `--paper` | カード内部地色（小面積限定）。通常 `#FFFFFF` または生成紙系 |
| 文字色 | — | `--text`／`--bg-dark` | 白・黒・黒寄りグレー（**text 用は L<40 dark 可**）|

**派生色・コントラスト規律（pale bg + dark text）**：
パステル系を主体に選ぶと、`--accent`（メイン）をそのまま白文字背景に使うと
contrast 不足になりやすい。**色の選定は自由だが、以下の可読性ガードレールは守る**：

- **bg 系**（背景・surface・薄塗り）は **pale〜mid-tone** を基本とし、大面積に真の dark を敷かない
- **text 系派生**（`--text` / `--bg-dark` / 見出し / `.judgment-text` / `--tan-*-deep` 等）は
  L<40 dark 可（text なので濃い方が読みやすい）
- **濃色を背景に使う箇所（header／重要結論ボックス等）の上の文字は light variant を充てる**
- **濃色背景セル内のリンクも light に**：`th`／header／`--bg-dark` ボックス内の `a`・`a.xref` は
  `color:#fff` で上書きする（`a.xref` の既定色は `--accent`＝濃色のため、濃 `th` 背景と同化する。
  `th a, th a.xref{color:#fff}` を必ず定義）
- 本文（`--text` × `--paper`）で **WCAG AA 4.5:1 以上**を確保（5-6 と共通）
- 原則は「pale bg + dark text」。メイン色は header／見出しの text 色・border 色として活かす
- **palette 外 hex の使用は JX では許容**（雰囲気に合えば全 15 案の chip・複数パレット越境・
  中間派生色を自由に使ってよい。ただし上記コントラストと 5-6 の 5 系統制限・調和を守る）

### 5-3. 配色の AI 自由選定の判断指標（正答率に依らない・全パレット対象）

全 15 案（＋派生色）から問題の雰囲気に合わせて自由に選ぶ。下記は方向づけの目安であり、
**11 名前付きは代表例**。複数パレットの組合せや中間色の派生も可：

1. **テーマの重さ／難度**：道徳論点・重罪・難解・深刻 → 落ち着いた／くすんだ／紫・スレート系
   （例：Antique Pearl / Dusty Sage / Twilight Violet / Maison Blanche）／軽快・基礎・日常 →
   明るいピンク・ミント系（例：Sweet Berry / Fresh Citrus / Rose Mist / Mint Tea / Fresh Mint）
2. **科目イメージ（参考・固定ではない）**：財産・人間味・家族 → ピンク系／手続・公共・行政 →
   ブルー・セージ系（例：Crystal Blue / Dusty Sage）／重厚な権威・統治 → 紫・パール系／経済・活気 → 黄橙系
3. **論点の対立・意外性**：対立が激しい・罠が多い → アクセント反対色を強めに／素直・一本道 → 同系統サブで統一
4. 必ずしも上記の名前付き例に収めず、**雰囲気が最もしっくり来る配色を AI が自由に組む**。
   選定理由（雰囲気の意図・採用色の方向性）は出力冒頭に 1〜2 文で記述する。

### 5-4. semantic exception（TX と同一）

11 パレットは全 pastel のため、普遍認知色のみ palette 越境を許容する：

- ✓ 緑（肯定・許容・`.success-box`）：`#438B48` / `#7BA980` を全パレットで借用
- 🏆 金（最重要強調）：`#ffd54f` / `#ffaa00` を inline hex で保持

> **行JX 専用 `--accent-2:#6FC885` の固定は廃止**：科目アンカー廃止に伴い、肯定／許容の
> 限定強調は上記 semantic 緑（`#438B48` / `#7BA980`）を全科目共通で使用する。

### 5-5. 12 色固定指標（全科目共通・不変）

```css
--hl-super:#ffd54f; --hl-high:#aed581; --hl-std:#90caf9;
--tan-super:#c62828; --tan-high:#ef6c00; --tan-std:#1565c0;
--rank-A:#c62828;   --rank-B:#e65100;   --rank-C:#1565c0; --rank-D:#333333;
```

### 5-6. 色彩運用原則

- **5 系統制限**：1 ページの意味色系統は最大 5。
- **大面積禁止**：純白 `#FFFFFF` を `body` 背景に、純黒 `#000000` を文字色に使用しない。
- **コントラスト**：本文（`--text` × `--paper`）で WCAG AA 4.5:1 以上を確保。
- **重複符号化**：学習指標は色＋記号／文字／配置の三重符号化。
- **ハイライト系**：`.hl-*` はテキスト 1 行未満のフレーズに限定。段落全体への塗布禁止。
- **カード地色のスキーマアンカー**：条文（薄グレー）／判例（薄ピンクまたは accent 派生）／学説（accent 派生）／注釈（淡黄色〜淡ピンク）で「いま何の素材を読んでいるか」を地色から瞬時に判別可能にする。

---

## 第6項　タイポグラフィ：11 役割スタック（v3.2 拡張）

### 6-1. 設計思想

書体は単なる装飾ではなく、**情報の種類を視覚的にラベリング**する記号系統である。読者が「いま自分は法令を読んでいるのか／判例の判旨を読んでいるのか／教授の解説を聞いているのか／自分が書く答案を読んでいるのか／補足注釈を読んでいるのか」を瞬時に判別できるよう、用途ごとに固定の役割を割り当てる。v3.1 の 6 役割を完全保持しつつ、KTX v6.19 と同期した 5 役割を追加した 11 役割体制。

### 6-2. Google Fonts ロード（必須）

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@400;500;700;800&family=Shippori+Antique&family=Zen+Old+Mincho:wght@400;500;700;900&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&family=Noto+Serif+JP:wght@400;500;700&family=Noto+Sans+JP:wght@400;500;700&family=Kaisei+Decol:wght@400;500;700&family=Kosugi+Maru&family=Source+Code+Pro:wght@400;600;700&family=M+PLUS+Rounded+1c:wght@500;700;800&family=M+PLUS+1p:wght@500;700;800;900&display=swap" rel="stylesheet">
```

### 6-3. 11 役割と CSS 変数定義（必須・改変禁止）

```css
:root{
  /* === 既存 6 役割（v3.1 から完全保持） === */

  /* ① 本文ゴシック：A1 ゴシック → Zen Kaku Gothic Antique フォールバック */
  --font-body:    "A1 Gothic","A-OTF A1ゴシック Std","Zen Kaku Gothic Antique",
                  "Hiragino Sans","Yu Gothic Medium","Noto Sans JP",sans-serif;

  /* ② 柔らかい強調・タグ・中見出し・ボタン */
  --font-soft:    "Zen Maru Gothic","Hiragino Maru Gothic ProN","Yu Gothic Medium",sans-serif;

  /* ③ 大見出し・カバー（しっぽり明朝 B1） */
  --font-display: "Shippori Mincho B1","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif;

  /* ④ 条文（フォーマル明朝） */
  --font-statute: "Noto Serif JP","Yu Mincho","Hiragino Mincho ProN",serif;

  /* ⑤ 判例引用（事案要約・blockquote 一般）：游明朝 */
  --font-quote:   "Yu Mincho","游明朝","Hiragino Mincho ProN","Noto Serif JP",serif;

  /* ⑥ 模範答案・論証本体（しっぽりアンチック） */
  --font-answer:  "Shippori Antique","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif;

  /* === v3.2 新規 5 役割（KTX v6.19 と同期） === */

  /* ⑦ KEY フレーズ・核心キーワード（Kaisei Decol） */
  --font-keyword: "Kaisei Decol","M PLUS Rounded 1c","Yu Mincho",serif;

  /* ⑧ 判旨原文専用（Zen Old Mincho 700） */
  --font-judgment:"Zen Old Mincho","Yu Mincho","Hiragino Mincho ProN","Noto Serif JP",serif;

  /* ⑨ 注釈・補足（Zen Kaku Gothic Antique） */
  --font-note:    "Zen Kaku Gothic Antique","Yu Gothic","Hiragino Sans",sans-serif;

  /* ⑩ 教授コメント・親しみある解説（Kosugi Maru） */
  --font-professor:"Kosugi Maru","Hiragino Maru Gothic ProN","Yu Gothic",sans-serif;

  /* ⑪ 等幅・ラベル・ID 表示（Source Code Pro） */
  --font-mono:    "Source Code Pro","Consolas","Menlo",monospace;

  /* ⑫ インパクト・大型数字／強調見出し（M PLUS 1p）：TX と共通定義。
        JX では任意使用（用途がなければ未使用でよいが、TX と font 設定を
        揃えるため定義は保持する） */
  --font-impact:  "M PLUS 1p","Hiragino Sans","Yu Gothic","Noto Sans JP",sans-serif;
}
```

> **TX との font 設定統一（2026-06-02）**：Google Fonts ロード行・`--font-*` 変数は
> TX `canonical/GENESIS.html` と完全一致させる。`--font-impact`（M PLUS 1p）は TX 由来の
> 12 番目の役割で、JX では任意使用だが定義は保持する（設定の byte-level 統一のため）。

### 6-4. 役割別の用途マトリクス

| # | 役割 | 変数 | 主な適用箇所 | 採用書体（先頭） |
|---|---|---|---|---|
| ① | 本文 | `--font-body` | `body`、段落、表 td、`<li>` | A1 ゴシック |
| ② | 柔強調 | `--font-soft` | `.subject-tag`、`h3`〜`h5`、`.tan`、`.arg-tier`、`.back-to-toc`、`th`、TOC 番号 | Zen 丸ゴシック |
| ③ | 表示見出し | `--font-display` | カバー `h1`、`h2`、模範答案内 `h5`、フッター closing | しっぽり明朝 B1 |
| ④ | 条文 | `--font-statute` | `blockquote.statute`、`.para-num`、5-1 条文集の本文 | Noto Serif JP |
| ⑤ | 引用一般 | `--font-quote` | `blockquote`（汎用）、`blockquote.case` の事案要約部、フッター本文 | 游明朝 |
| ⑥ | 答案・論証 | `--font-answer` | `.model-answer`、`blockquote.model-answer`、`.arg-card .arg-body` | しっぽりアンチック |
| ⑦ | KEY | `--font-keyword` | `.key-box`、`.kp-strong`、`.key-phrase` | Kaisei Decol |
| ⑧ | 判旨 | `--font-judgment` | `.judgment-text`（判旨原文段落のみ）、`blockquote.case .judgment` | Zen Old Mincho |
| ⑨ | 注釈 | `--font-note` | `.note-box`／`.warn-box`／`.success-box`／`.danger-box` 本文、`.basis-card .note` | Zen Kaku Gothic Antique |
| ⑩ | 教授 | `--font-professor` | `.prof-comment`、`.teacher-says`（任意採用） | Kosugi Maru |
| ⑪ | 等幅 | `--font-mono` | `.doc-header`、ラベル `::before`（KEY/NOTE/WARN等）、コード | Source Code Pro |

### 6-5. base CSS（必須適用・v3.2 更新）

```css
body{
  font-family:var(--font-body);
  font-weight:500;                     /* v3.2: 400→500 */
  line-height:2.0;                     /* v3.2: 1.92→2.0 */
  font-size:16px;
  letter-spacing:.04em;                /* v3.2: .01→.04em */
  font-feature-settings:"palt" 1;
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  text-rendering:optimizeLegibility;
  background:var(--base);
  color:var(--text);
}
h1{ font-family:var(--font-display); font-weight:700; letter-spacing:.06em; line-height:1.4; }
h2{ font-family:var(--font-display); font-weight:700; letter-spacing:.06em; line-height:1.4; }
h3{ font-family:var(--font-soft);    font-weight:700; letter-spacing:.04em; line-height:1.5; }
h4{ font-family:var(--font-soft);    font-weight:700; letter-spacing:.03em; }
h5{ font-family:var(--font-soft);    font-weight:700; letter-spacing:.03em; }
```

### 6-6. 運用上の鉄則

1. **法令文は必ず `--font-statute`**：条文ブロックを游明朝や明朝以外で組まない。`.para-num` も同変数を使用。
2. **判旨原文は `--font-judgment`**：判決理由の引用・判旨の核心は Zen Old Mincho 700 で固定。事案要約・先例関係などの周辺テキストは `--font-quote` を使い分ける。
3. **受験生が実際に書く文字は `--font-answer`**：模範答案・論証カード本体は必ずしっぽりアンチック系。読者の視覚を「答案用紙」に誘導する。
4. **KEY フレーズは `--font-keyword`**：Kaisei Decol で「核心キーワード」を視覚的に屹立させる。
5. **注釈系は `--font-note`**：Zen Kaku Gothic Antique で穏やかな補足ボイスを表現。
6. **ナビ・タグ・ボタンは `--font-soft`**：丸ゴシックの親密さでクリック誘発要素を識別。
7. **大見出しの威厳は `--font-display`**：しっぽり明朝 B1 で章の重みを表現。
8. **ラベル `::before` は `--font-mono`**：『KEY』『NOTE』『WARN』等の英字ラベルは Source Code Pro で硬質に。
9. **本文 `--font-body` は穏やかな角ゴ**：長時間の読書に耐える、A1 ゴシック系の優しい角ゴで統一。

### 6-7. 禁則

- 11 役割の用途を入れ替えての使用（例：模範答案を Zen 丸ゴシックで組む／判旨を游明朝で組む）。
- `:root` 外での `font-family` 直接指定（必ず `var(--font-*)` 経由）。
  - ただし SVG 内の `<text>` は例外として直接書体名を記述してよい（変数が継承されないため）。SVG 内でも本仕様の役割（見出し的なら明朝、ナビ的なら丸ゴシ）に整合させる。
- 11 役割（＋ TX 由来の `--font-impact`）を無視した独自の追加フォントの新設。
- ロード書体（Google Fonts）を TX `canonical/GENESIS.html` の指定セット以外に拡張すること（パフォーマンス／TX との一貫性のため）。

---

## 第7項　ヘッダーとカバー

### 7-1. 右上 ID タグ（doc-header）

`position:absolute` で配置（スクロール非追従）。`sticky` `fixed` 禁止。

```css
.doc-header{
  position:absolute; top:14px; right:18px; z-index:100;
  display:inline-block;
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff; padding:6px 14px; border-radius:8px;
  font-family:var(--font-mono);                /* v3.2: soft → mono */
  font-weight:600; font-size:16px; letter-spacing:.10em;
  border:1.5px solid rgba(255,255,255,.65);
  box-shadow:0 2px 6px rgba(0,0,0,.2);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
```

### 7-2. カバーヘッダー

```css
header.cover{
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff; padding:70px 32px 44px 32px; text-align:center;
  border-radius:0 0 20px 20px; margin-bottom:24px;
  position:relative; overflow:hidden;
}
header.cover::before{
  content:''; position:absolute; inset:0; pointer-events:none;
  background:
    radial-gradient(ellipse at top right, rgba(255,255,255,.10) 0%, transparent 60%),
    radial-gradient(ellipse at bottom left, rgba(0,0,0,.08) 0%, transparent 60%);
}
header.cover h1{
  margin:0 0 10px 0;
  font-family:var(--font-display);
  font-size:1.9em; font-weight:700; letter-spacing:.06em;
  color:#fff;
}
header.cover .subtitle{
  margin:0;
  font-family:var(--font-quote);
  font-size:1em; opacity:.92; color:#fff;
}
header.cover .subject-tag{
  display:inline-block; margin-bottom:14px; padding:4px 14px;
  background:rgba(255,255,255,.18);
  border:1px solid rgba(255,255,255,.42);
  border-radius:999px;
  font-family:var(--font-soft);
  font-size:.78em; font-weight:700; letter-spacing:.18em;
}
```

```html
<header class="cover">
  <span class="subject-tag">刑　法</span>
  <h1>{タイトル}</h1>
  <p class="subtitle">{出典・サブタイトル}</p>
</header>
```

### 7-3. ヘッダー禁止事項

- `position:sticky` / `position:fixed`
- 中央タイトル要素（`.doc-title`）の追加
- バージョン番号タグ（`.doc-version`）の追加
- 配色パターン名のヘッダー記載

---

## 第8項　レイアウト：section カード化（KJX2 流標準・v3.2 寸法調整）

```css
.container{
  max-width:1080px;                            /* v3.2: 1100→1080 */
  margin:0 auto;
  padding:0 20px 32px 20px;                    /* モバイル：v3.2 */
  background:transparent;
}
@media (min-width:769px){
  .container{ padding:0 40px 48px 40px; }      /* デスクトップ：v3.2 */
}

.container > section, .container > nav#toc, .container > .toc{
  background:var(--paper); border-radius:14px;
  padding:32px 36px;                           /* v3.2: 30/32→32/36 */
  margin:24px 0;
  box-shadow:0 4px 14px rgba(0,0,0,.10);
  border:none;
}
section section{
  background:transparent; padding:0;
  margin:24px 0 0 0; box-shadow:none; border-radius:0;
}
html{ scroll-behavior:smooth; scroll-padding-top:20px; }
```

shadow 色は `--accent` 由来（例：`rgba(123,63,47,.10)`）に置換するとアートディレクションが強化される。

---

## 第9項　見出し階層

```css
h2{
  font-family:var(--font-display);
  color:var(--accent); font-size:1.6em; font-weight:700;
  letter-spacing:.06em;
  margin:0 0 18px 0;
  padding:10px 16px; background:var(--soft);
  border-left:8px solid var(--accent); border-radius:4px;
  line-height:1.4;
}
h3{
  font-family:var(--font-soft);
  color:var(--accent); font-size:1.25em; font-weight:700;
  letter-spacing:.04em;
  margin:26px 0 14px 0;
  padding:7px 14px;
  background:{AI設計の極淡色（accent or mid 派生）};
  border-left:5px solid var(--mid);
}
h4{
  font-family:var(--font-soft);
  color:var(--mid); font-size:1.08em; font-weight:700;
  margin:18px 0 10px 0;
  padding-bottom:4px; border-bottom:1.5px dashed var(--mid);
  letter-spacing:.03em;
}
h5{
  font-family:var(--font-soft);
  color:var(--accent); font-size:1em; font-weight:700;
  margin:14px 0 8px 0; letter-spacing:.03em;
}
```

### 9-1. 第5部スキーマ用の点線見出し（v3.2 新設・KTX 流）

第5部（参考資料）配下のセクションでは、`section[id^="ref-"]` のスコープ下で見出しに点線下線を適用し、本編との視覚差を出す：

```css
section[id^="ref-"] h3{
  border-bottom:3px dotted var(--accent);
  padding-bottom:14px;
  margin-bottom:28px;
  background:transparent;
  border-left:none;
  padding-left:0;
}
section[id^="ref-"] h4{
  border-bottom:2px dotted {AI設計の薄色};
  padding-bottom:6px;
}
```

---

## 第10項　第0部 凡例（4 ブロック・追加禁止／フォント運用ガイドはオプション）

第0部は次の **4 ブロック厳守**：論文式頻度マーカー／短答式頻度マーク／重要度／答案必要度。

ただし、ユーザーが「フォントの効果を見せたい」「リファレンスとして残したい」と要望する場合に限り、4 ブロック直後にオプションとして以下の `.font-guide` ブロックを追加してよい（v3.2 で 11 役割表示に拡張）：

```html
<h3>フォント運用ガイド（11 役割）</h3>
<div class="font-guide">
  <table>
    <thead><tr><th>用途</th><th>採用フォント</th><th>サンプル</th></tr></thead>
    <tbody>
      <tr><td>本文ゴシック</td><td>A1ゴシック</td><td style="font-family:var(--font-body);">…サンプル文…</td></tr>
      <tr><td>柔強調・タグ・見出し</td><td>Zen 丸ゴシック</td><td style="font-family:var(--font-soft);">…サンプル文…</td></tr>
      <tr><td>大見出し・カバー</td><td>しっぽり明朝 B1</td><td style="font-family:var(--font-display);">…サンプル文…</td></tr>
      <tr><td>条文</td><td>Noto Serif JP</td><td style="font-family:var(--font-statute);">…条文サンプル…</td></tr>
      <tr><td>引用一般</td><td>游明朝</td><td style="font-family:var(--font-quote);">…引用サンプル…</td></tr>
      <tr><td>模範答案・論証</td><td>しっぽりアンチック</td><td style="font-family:var(--font-answer);">…答案サンプル…</td></tr>
      <tr><td>KEY フレーズ</td><td>Kaisei Decol</td><td style="font-family:var(--font-keyword);">…核心キーワード…</td></tr>
      <tr><td>判旨原文</td><td>Zen Old Mincho 700</td><td style="font-family:var(--font-judgment);font-weight:700;">…判旨サンプル…</td></tr>
      <tr><td>注釈・補足</td><td>Zen Kaku Gothic Antique</td><td style="font-family:var(--font-note);">…注釈サンプル…</td></tr>
      <tr><td>教授コメント</td><td>Kosugi Maru</td><td style="font-family:var(--font-professor);">…教授ボイス…</td></tr>
      <tr><td>等幅・ラベル</td><td>Source Code Pro</td><td style="font-family:var(--font-mono);">KEY / NOTE / 刑JX1</td></tr>
    </tbody>
  </table>
</div>
```

このブロックの追加は任意。要望がない場合は4 ブロックのみとする。

---

## 第11項　学習指標 CSS（v3.2 潰れ防止強化）

```css
.tan{
  display:inline-block;
  font-family:var(--font-soft);
  font-size:.78em; padding:2px 9px; border-radius:4px;
  color:#fff; font-weight:700; margin-right:4px;
  letter-spacing:.08em;                              /* v3.2: .05→.08em */
  vertical-align:1px;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.tan-super{ background:var(--tan-super); border:2px solid #8a1818 }
.tan-high { background:var(--tan-high) }
.tan-std  { background:var(--tan-std) }

.rank-A{ color:var(--rank-A); font-weight:700; letter-spacing:.04em; }
.rank-B{ color:var(--rank-B); font-weight:700; letter-spacing:.04em; }
.rank-C{ color:var(--rank-C); font-weight:500; letter-spacing:.04em; }
.rank-D{ color:var(--rank-D); font-weight:500; letter-spacing:.04em; }

.arg-tier{
  display:inline-block;
  font-family:var(--font-soft);
  font-size:.78em; font-weight:700;
  padding:2px 9px; border-radius:4px; color:#fff;
  margin-right:6px; letter-spacing:.08em;            /* v3.2: .05→.08em */
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.arg-required, .arg-must         { background:#c62828; border:2px solid #8a1818 }
.arg-recommended, .arg-recommend { background:#ef6c00 }
.arg-advanced, .arg-develop      { background:#1565c0 }

/* ハイライト：v3.2 透明度・字間強化 */
.hl-super{
  background:linear-gradient(transparent 55%,rgba(255,213,79,.55) 55%);
  padding:0 4px 1px; font-weight:700; letter-spacing:.08em;
}
.hl-high {
  background:linear-gradient(transparent 60%,rgba(174,213,129,.55) 60%);
  padding:0 4px 1px; font-weight:700; letter-spacing:.08em;
}
.hl-std  {
  background:linear-gradient(transparent 70%,rgba(144,202,249,.50) 70%);
  padding:0 4px 1px; font-weight:500; letter-spacing:.06em;
}

/* exam-mark（出題実績マーカー・KTX 流） */
.exam-mark{
  background:linear-gradient(transparent 60%,currentColor 60%);
  background-size:100% 100%;
  background-repeat:no-repeat;
  padding:0 4px 1px;
  font-weight:700;
  letter-spacing:.09em;
  margin:0 1px;
  -webkit-font-smoothing:antialiased;
}
.exam-mark.freq-high{
  background:linear-gradient(transparent 55%,rgba(198,40,40,.42) 55%);
  color:#8a1818;
}
.exam-mark.freq-mid{
  background:linear-gradient(transparent 55%,rgba(239,108,0,.42) 55%);
  color:#a04500;
}
.exam-mark.freq-low{
  background:linear-gradient(transparent 55%,rgba(21,101,192,.36) 55%);
  color:#1565c0;
}

/* 条文・判例の行内強調（v3.2：border-bottom 廃止） */
.statute-emphasis{
  font-family:var(--font-statute);
  font-weight:700;
  padding:0 3px;
  letter-spacing:.06em;
}
.case-emphasis{
  font-family:var(--font-statute);
  font-weight:700;
  font-style:italic;
  padding:0 3px;
  letter-spacing:.06em;
}
```

---

## 第12項　相互リンク（順方向＋逆方向）

```css
a.xref{
  text-decoration:underline; text-decoration-thickness:2px; text-underline-offset:3px;
  color:var(--accent); font-weight:700; padding:0 2px; transition:.18s;
}
a.xref:hover{ background:var(--light); color:var(--accent) }

.back-refs{
  margin-top:14px; padding:10px 14px;
  background:var(--light); border-radius:6px;
  font-size:.92em; font-weight:700;
  border-left:3px solid var(--accent);
  font-family:var(--font-note);
}
.back-refs::before{ content:'📌 '; font-size:1.1em; }
.back-refs a{
  color:var(--accent); text-decoration:none; margin:0 6px;
  border-bottom:1px dotted var(--accent); font-weight:700;
}
.back-refs a:hover{ color:var(--mid); border-bottom-color:var(--mid); }
```

### アンカー ID 命名規則

| 種別 | プレフィックス | 例 |
|---|---|---|
| 条文 | `ref-stat-{法令略称}-{条数}` | `ref-stat-keih-205` |
| 判例 | `ref-case-{裁判所略称}-{年月日}` | `ref-case-saiketsu-h16-2-17` |
| 学説 | `ref-doctrine-{論点キー}-{説名}` | `ref-doctrine-ingakankei-kikennogenjitsuka` |
| 論証 | `ref-arg-{論点ID}` | `ref-arg-x1` |
| 用語 | `ref-term-{ヨミ}` | `ref-term-ingakankei` |

---

## 第13項　共通コンポーネント CSS（v3.2 大幅強化）

### 13-1. キーボックス（KTX v6.19 流豪華装飾・specificity 防御）

```css
/* specificity 防御セレクタ三者結合（重要） */
.key-box,
.section .key-box,
.container .key-box{
  position:relative;
  background:linear-gradient(135deg,#fff8f0 0%,var(--light) 60%,var(--soft) 100%);
  border:2px solid var(--accent);
  border-radius:8px;
  padding:56px 44px 38px 72px;                  /* v3.2 余裕レイアウト */
  margin:30px 0 24px;
  font-family:var(--font-keyword);              /* Kaisei Decol */
  font-size:1.05rem;
  font-weight:500;
  line-height:2.0;
  letter-spacing:.04em;
  color:var(--text);
  box-shadow:
    0 4px 14px rgba(0,0,0,.10),
    inset 0 0 0 1px rgba(255,255,255,.6);
}
.key-box::before{
  content:'🔑 KEY';
  position:absolute;
  top:-14px; left:22px;
  background:linear-gradient(135deg,var(--accent) 0%,var(--mid) 100%);
  color:#fff;
  padding:5px 16px 4px;
  border-radius:4px;
  font-family:var(--font-mono);
  font-size:.80rem; font-weight:600;
  letter-spacing:.14em;
  box-shadow:0 2px 6px rgba(0,0,0,.20);
  white-space:nowrap;
}
.key-box::after{
  content:'';
  position:absolute;
  top:0; right:0;
  width:64px; height:64px;
  background:radial-gradient(circle at top right, rgba(0,0,0,.08), transparent 70%);
  border-radius:0 8px 0 64px;
  pointer-events:none;
}
.key-box .kp-strong{
  font-weight:700;
  color:var(--accent);
  font-size:1.10rem;
  letter-spacing:.05em;
}
```

### 13-2. 状況伝達系：ラベル付きカード型（v3.2 全面刷新）

旧仕様の `border-left` 単色帯方式を廃止し、KTX v6.19 流の **全周 border 1px ＋ ラベル `::before` ＋ 微外側 shadow ＋ 内側白ライン** に統一。フォントは `--font-note`。

```css
.note-box, .warn-box, .success-box, .danger-box{
  position:relative;
  margin:18px 0;
  padding:20px 22px 16px;
  border-radius:8px;
  font-family:var(--font-note);
  font-weight:500;
  line-height:1.95;
  letter-spacing:.03em;
  box-shadow:
    0 2px 6px rgba(0,0,0,.06),
    inset 0 0 0 1px rgba(255,255,255,.6);
}
.note-box   { background:#e7f1ff; border:1px solid rgba(21,101,192,.30); }
.warn-box   { background:#fff7e0; border:1px solid rgba(239,108,0,.32); }
.success-box{ background:#e8f5e9; border:1px solid rgba(46,125,50,.32); }
.danger-box { background:#ffeef0; border:1px solid rgba(198,40,40,.32); }

.note-box::before, .warn-box::before, .success-box::before, .danger-box::before{
  display:inline-block;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:700;
  letter-spacing:.14em;
  color:#fff;
  padding:3px 10px 2px;
  border-radius:3px;
  margin-bottom:10px;
  margin-right:8px;
  vertical-align:2px;
  box-shadow:0 1px 2px rgba(0,0,0,.18);
}
.note-box::before   { content:'ℹ NOTE';    background:linear-gradient(135deg,#0d47a1,#1565c0); }
.warn-box::before   { content:'⚠ WARN';    background:linear-gradient(135deg,#bf360c,#ef6c00); }
.success-box::before{ content:'✓ TIP';     background:linear-gradient(135deg,#1b5e20,#2e7d32); }
.danger-box::before { content:'✗ NG';      background:linear-gradient(135deg,#7f0000,#c62828); }

/* h4 を内部に置く場合、::before との競合を避けるため margin 調整 */
.note-box h4, .warn-box h4, .success-box h4, .danger-box h4{
  display:inline; font-family:var(--font-soft);
  font-size:1em; font-weight:700; margin:0;
}
```

### 13-2-bis. 講師のアドバイス（講義逐語ベース・教授ボイス／必須コンポーネント）

講義の逐語録（`*_文字起こし.txt` 等）が入力にある場合、その要点を**論点ごとに整理**して
`.lecturer-advice` ボックスに収め、**該当する論点・部の冒頭に配置**する（学習効果が高い重要要素）。
本文は教授ボイス（`--font-professor`／Kosugi Maru）、ラベルは `--font-mono`。
バッジ・背景は「目立つ」設計（accent→mid の鮮やかバッジ＋薄色パネル＋太い左罫）。

```css
.lecturer-advice{
  position:relative;
  margin:30px 0 26px;
  padding:28px 26px 18px 28px;
  border-radius:10px;
  /* 薄色パネル：選定パレットの淡色〜極淡色で構成（下例は紫系。雰囲気に合わせAI調整） */
  background:linear-gradient(135deg, {palette淡色} 0%, {palette極淡色} 58%, var(--paper) 100%);
  border:1px solid {accentのrgba .40前後};
  border-left:7px solid var(--accent);
  font-family:var(--font-professor);
  font-weight:500; line-height:1.95; letter-spacing:.02em;
  color:var(--text);
  box-shadow:0 4px 16px {accentのrgba .20}, inset 0 0 0 1px rgba(255,255,255,.55);
}
.lecturer-advice::before{
  content:'🎓 講師のアドバイス';
  position:absolute; top:-15px; left:20px;
  font-family:var(--font-mono);
  font-size:.84rem; font-weight:700; letter-spacing:.13em;
  color:#fff; padding:6px 18px 5px; border-radius:5px;
  background:linear-gradient(135deg, var(--accent) 0%, var(--mid) 100%);
  box-shadow:0 3px 9px {accentのrgba .42};
  white-space:nowrap;
}
.lecturer-advice .la-lead{                 /* 小見出し（その箱の主題） */
  display:block; font-family:var(--font-soft); font-weight:700;
  color:var(--accent); font-size:1.04em; letter-spacing:.03em; margin:.2em 0 .6em;
}
.lecturer-advice p{ margin:.55em 0; }
.lecturer-advice ul{ margin:.6em 0; padding-left:1.45em; }
.lecturer-advice li{ margin:.34em 0; }
.lecturer-advice .la-key{                  /* 核心語（キーワード強調） */
  font-family:var(--font-keyword); font-weight:700; color:var(--accent); letter-spacing:.02em;
}
.lecturer-advice .la-quote{                /* キーフレーズの軽い網掛け */
  font-family:var(--font-quote); color:var(--bg-dark); font-style:normal;
  background:{accentのrgba .07}; padding:1px 6px; border-radius:3px;
}
```

**インデント防御**：`section > .lecturer-advice` / `.card > .lecturer-advice` を第23項の
`margin-left:0` 防御リストに加える。**印刷**：`page-break-inside:avoid` 群に含める。
**レスポンシブ**：`@media(max-width:768px)` で `padding:20px 18px 14px 18px`。

**HTML テンプレート**（中身のみ本問固有で執筆）：

```html
<div class="lecturer-advice">
  <span class="la-lead">{その箱の主題（例：本問最大のポイント）}</span>
  <p>{講義要点を整理した解説。<span class="la-key">{核心語}</span> や
     <span class="la-quote">{キーフレーズ}</span> を適宜強調}</p>
</div>
```

**配置規律（丁寧に・該当箇所へ）**：
- 逐語録を**そのまま貼らない**。論点ごとに要点を抽出・再構成して配置する。
- 総論（問題処理パターン・検討順序等）は第2部冒頭、各論点固有の助言は当該論点（`<h3>`）の直後。
- 1 論点に複数主題があれば `.la-lead` で区切るか箱を分ける。誇張・新情報の創作はしない（逐語に忠実）。
- 逐語録が無い問題では本コンポーネントは省略可（必須は「逐語録がある場合」）。

### 13-3. テーブル

```css
table{ width:100%; border-collapse:collapse; margin:18px 0; font-size:.96em; page-break-inside:avoid; }
th,td{ border:1px solid {AI設計のmid派生色}; padding:10px 12px; text-align:left; vertical-align:top; }
th{ background:var(--accent); color:#fff; font-family:var(--font-soft); font-weight:700; letter-spacing:.04em; }
/* 濃い --accent 背景の th 内リンクは light に（a.xref 既定色=--accent と同化するため・必須） */
th a, th a.xref{ color:#fff; text-decoration-color:rgba(255,255,255,.6); }
th a.xref:hover{ background:rgba(255,255,255,.18); color:#fff; }
tr:nth-child(even) td{ background:var(--soft) }
```

### 13-4. タイムライン

```css
.timeline{ position:relative; padding-left:32px; margin:18px 0 }
.timeline::before{ content:''; position:absolute; left:10px; top:0; bottom:0;
                   width:3px; background:var(--mid); border-radius:2px }
.timeline-item{ position:relative; margin-bottom:18px; padding-left:18px }
.timeline-item::before{ content:''; position:absolute; left:-26px; top:8px;
                        width:14px; height:14px; background:var(--accent);
                        border-radius:50%; border:3px solid var(--light) }
.timeline-label{
  display:block; font-family:var(--font-soft); font-weight:700;
  color:var(--accent); font-size:1.02em; letter-spacing:.04em;
}
```

### 13-5. SVG

```css
.svg-wrap{
  text-align:center; margin:24px 0; background:var(--paper); border-radius:10px;
  padding:18px; overflow-x:auto; page-break-inside:avoid;
  border:1px solid {AI設計色};
}
```

### 13-6. チェックリスト

```css
.checklist{ margin:14px 0; padding-left:0; list-style:none }
.checklist li{
  margin:6px 0; padding:8px 10px 8px 32px; position:relative;
  background:{AI設計の極淡色}; border-radius:4px;
  font-family:var(--font-note);
  font-weight:500; line-height:1.85;
}
.checklist li::before{
  content:'☐'; position:absolute; left:10px; top:7px;
  font-size:1.15em; color:var(--accent); font-weight:700;
}
```

### 13-7. 論証カード（本体は --font-answer）

```css
.arg-card{
  background:#fff; border:2px solid var(--mid); border-radius:10px;
  padding:22px 24px; margin:20px 0; page-break-inside:avoid;
  box-shadow:0 4px 12px {AI設計シャドウ};
}
.arg-card h5{
  margin-top:0; color:var(--accent);
  border-bottom:1.5px dashed var(--mid); padding-bottom:6px;
  font-family:var(--font-soft); font-weight:700; font-size:1.05em;
}
.arg-card .arg-meta{
  font-family:var(--font-mono);                        /* v3.2: soft → mono */
  font-size:.78em; font-weight:600; letter-spacing:.10em;
  color:var(--mid);
  margin:0 0 12px 0;
}
.arg-card .arg-body{
  font-family:var(--font-answer);
  font-weight:400;
  line-height:2.05; letter-spacing:.02em;
  background:{AI設計極淡色}; padding:16px 18px; border-radius:6px;
  border-left:3px solid var(--light);
}
```

### 13-8. 模範答案（しっぽりアンチック）

```css
.model-answer, blockquote.model-answer{
  position:relative;
  background:linear-gradient(180deg,{AI設計極淡色} 0%,#fff 100%);
  border:2px solid var(--accent); border-radius:10px;
  padding:32px 30px 28px 30px; margin:24px 0;
  font-family:var(--font-answer);
  font-weight:400; line-height:2.05; letter-spacing:.02em;
  page-break-inside:avoid;
  box-shadow:0 4px 14px {AI設計シャドウ};
}
.model-answer::before{
  content:'MODEL ANSWER';
  position:absolute; top:-12px; left:24px;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; padding:4px 14px 3px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:600; letter-spacing:.18em;
  box-shadow:0 2px 5px rgba(0,0,0,.18);
}
.model-answer h5{
  font-family:var(--font-display);
  color:var(--accent); letter-spacing:.04em;
}
```

### 13-9. 採点講評

```css
.grading{
  position:relative;
  background:#fff8e1; border:1px solid rgba(255,179,0,.45); border-radius:10px;
  padding:30px 24px 22px; margin:22px 0; page-break-inside:avoid;
  box-shadow:0 2px 6px rgba(255,179,0,.12);
}
.grading::before{
  content:'GRADING';
  position:absolute; top:-12px; left:24px;
  background:linear-gradient(135deg,#bf6b00,#ef6c00);
  color:#fff; padding:4px 14px 3px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:600; letter-spacing:.18em;
  box-shadow:0 2px 5px rgba(0,0,0,.18);
}
.grading h4{
  font-family:var(--font-soft);
  color:#bf6b00; margin-top:0;
  border-bottom:1.5px solid rgba(255,179,0,.45); padding-bottom:6px;
}
```

### 13-10. 引用：条文（薄グレー差別化）／判例（薄ピンク or accent 派生差別化）

```css
/* 汎用 blockquote（→ 游明朝） */
blockquote{
  margin:14px 0; padding:14px 18px; background:var(--soft);
  border-left:5px solid var(--accent); border-radius:6px;
  font-family:var(--font-quote);
  font-weight:400; line-height:1.95;
}

/* 条文 blockquote：薄グレー（KTX v6.19 流） */
blockquote.statute{
  background:#f3f4f6;
  border:1px solid rgba(0,0,0,.10);
  border-left:4px solid #6b7280;
  border-radius:6px;
  padding:14px 18px;
  font-family:var(--font-statute);
  font-weight:500; letter-spacing:.04em;
}

/* 判例 blockquote：薄ピンク or accent 派生（KTX 流） */
blockquote.case{
  background:#ffeef1;                    /* または AI 設計の accent 極淡派生 */
  border:1px solid rgba(0,0,0,.10);
  border-left:4px solid var(--mid);
  border-radius:6px;
  padding:14px 18px;
  font-family:var(--font-quote);
}

/* 判旨原文専用クラス（v3.2 新設） */
.judgment-text{
  font-family:var(--font-judgment);
  font-weight:700;
  letter-spacing:.03em;
  line-height:1.95;
}
```

### 13-11. 第〇項の網掛けクラス（v3.2 新設）

`<strong>第1項</strong>` などの旧表記を、`<span class="para-num">第1項</span>` に置換する。

```css
.para-num{
  display:inline-block;
  background:var(--accent-3, #fff8f0);   /* AI設計の極淡色 */
  color:var(--accent);
  padding:2px 10px;
  border-radius:3px;
  font-family:var(--font-statute);
  font-weight:700;
  font-size:.96em;
  margin-right:8px;
  border:1px solid {AI設計の薄色};
  letter-spacing:.04em;
}
```

### 13-12. フォント運用ガイド（オプション・第10項）

```css
.font-guide{
  position:relative;
  background:var(--paper); border:1px solid {AI設計の薄色};
  border-radius:10px; padding:28px 26px 22px; margin:18px 0;
}
.font-guide::before{
  content:'TYPOGRAPHY';
  position:absolute; top:-12px; left:24px;
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; padding:4px 14px 3px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:.72rem; font-weight:600; letter-spacing:.18em;
  box-shadow:0 2px 5px rgba(0,0,0,.18);
}
```

### 13-13. 戻るリンク

```css
.back-to-toc{
  display:inline-block; margin:18px 0 4px 0; padding:8px 18px;
  background:var(--accent); color:#fff; border-radius:999px;
  font-family:var(--font-soft);
  font-size:.85em; text-decoration:none; font-weight:700;
  letter-spacing:.05em;
  box-shadow:0 2px 4px rgba(0,0,0,.15); transition:.2s;
}
.back-to-toc:hover{ background:var(--mid) }
```

### 13-14. フッター

```css
footer{
  background:linear-gradient(135deg,var(--accent),var(--mid));
  color:#fff; text-align:center; padding:32px 24px;
  margin:48px 0 0 0; border-radius:16px 16px 0 0;
}
footer p{
  margin:.5em 0;
  font-family:var(--font-quote);
  font-weight:400; color:#fff; line-height:1.95;
}
footer .closing{
  font-family:var(--font-display);
  font-weight:700; letter-spacing:.1em;
}
```

---

## 第14項　第3部 採点講評の必須項目

模範答案直後に `.grading` ボックス（v3.2 でラベル付きカード型に強化）で配置：評価ポイント／失点パターン表／分量バランス／本問特有の発展加点要素。

---

## 第15項　第4部 必須要素

### 15-1. 論点間の優先順位フロー
複数論点が絡む事例で、論ずる順序の合理性を SVG + 表で可視化。原則「主要被告人 → 副被告人 → 共犯」。

### 15-2. コラム：実務との架橋
4 観点で整理：①関連法令／②学説対立の実務上の現れ方（表）／③当該事案が実務に提起する三層構造（刑事・行政・民事）／④受験生として押さえるべき視点。

行政JX では `--accent-2`（鮮グリーン）を `.success-box` 系コラムの強調に活用してよい。

---

## 第16項　第5部 完全プロファイル スキーマ（v3.2 強化）

### 5-1 条文集

各エントリは `<div class="ref-entry statute-entry">` でラップし、`blockquote.statute`（薄グレー）で全文を提示。条文番号は `<span class="para-num">第1項</span>` 形式。

必須項目：識別／視覚マーク／全文（`blockquote.statute`）／体系的位置／要件・効果／立法趣旨／保護法益／関連条文網／要件詳細分解／答案での使い方／📌 本編出現箇所（`back-refs`）

### 5-2 判例集

各エントリは `<div class="ref-entry case-entry">` でラップし、判旨原文は **必ず `<p class="judgment-text">` または `<blockquote class="case"><p class="judgment-text">` 形式で Zen Old Mincho 700 表示**。事案要約・先例関係などの周辺テキストは `--font-quote`（游明朝）。

必須項目：識別／視覚マーク／事件名／裁判所／判決日／出典／事件番号／事案／判旨原文（`.judgment-text`）／先例との関係／射程／後続判例／学説評価／答案での使い方／📌 本編出現箇所

### 5-3 学説一覧

必須項目：識別／視覚マーク／主要論者／主要文献の頁数／内容／形式的論拠／実質的論拠／批判／反論／判例との関係／答案での使い方／📌 本編出現箇所

### 5-4 答案論証集

各論証は `<div class="arg-card">` 構造。本文は `.arg-body` で `--font-answer`（しっぽりアンチック）。メタ情報（出題実績・想定文字数）は `.arg-meta` で `--font-mono`。

必須項目：識別／答案必要度マーク／出題実績／想定文字数／**完成形 → 簡略版 → 発展版の3層**／使用条文・判例・学説の `xref`／📌 本編出現箇所

### 5-5 用語集（五十音順）
定義／類義語・対義語／使用される場面／混同されやすい用語との区別／📌 本編出現箇所

### 5-6 略語・出典一覧
判例集略語／裁判所略称／法令略称／主要教科書略語／主要学者略称

---

## 第17項　印刷最適化

```css
@media print{
  *{-webkit-print-color-adjust:exact!important; print-color-adjust:exact!important}
  body{ background:#fff; font-size:11pt; line-height:1.85; color:var(--text); letter-spacing:.02em; }
  .container{ max-width:100%; padding:0 }
  .container > section, .container > nav#toc{
    box-shadow:none; border-radius:0; padding:14px 0; margin:14px 0;
  }
  @page{ size:A4; margin:20mm 15mm }
  .doc-header{ position:absolute; top:8mm; right:8mm; font-size:13px; padding:4px 10px; box-shadow:none }
  header.cover{
    background:var(--accent)!important; color:#fff!important;
    padding:24px 20px; border-radius:0; margin-bottom:18px;
  }
  .back-to-toc, .back-to-top{ display:none!important }
  h2,h3,h4{ page-break-after:avoid }
  .key-box, .note-box, .warn-box, .success-box, .danger-box,
  .model-answer,blockquote,blockquote.statute,blockquote.case,
  table,.svg-wrap,.legend-card,.arg-card,.grading,.ref-entry,.font-guide{
    page-break-inside:avoid
  }
  .hl-super,.hl-high,.hl-std,.tan,.rank-A,.rank-B,.rank-C,.arg-tier,.exam-mark,.para-num{
    -webkit-print-color-adjust:exact!important; print-color-adjust:exact!important;
  }
  a{ color:var(--accent); text-decoration:none }
  a.xref{ text-decoration:underline }
  details{ display:block } details > summary{ display:none }
  footer{ margin:24px 0 0 0; border-radius:0 }
}
```

---

## 第18項　レスポンシブ

```css
@media screen and (max-width:768px){
  body{ font-size:15px; line-height:1.92; }
  .container{ padding:0 14px 32px 14px }
  .doc-header{ top:10px; right:12px; font-size:13px; padding:4px 10px }
  header.cover{ padding:60px 16px 30px }
  header.cover h1{ font-size:1.4em; letter-spacing:.04em }
  .container > section, .container > nav#toc{ padding:22px 18px }
  h2{ font-size:1.25em } h3{ font-size:1.1em }
  .key-box{ padding:46px 24px 28px 28px; font-size:1rem; }
  .note-box, .warn-box, .success-box, .danger-box{ padding:18px 18px 14px }
  .model-answer{ padding:28px 20px 22px }
  .arg-card{ padding:18px 18px }
  table{ font-size:.88em } th,td{ padding:7px }
}
```

---

## 第19項　末尾 JavaScript

```html
<script>
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click',function(e){
      var t=document.querySelector(this.getAttribute('href'));
      if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'});}
    });
  });
});
</script>
```

---

## 第20項　フッター（励ましの言葉・必須）

```html
<footer>
  <p>本教材は、司法試験・予備試験の上位合格を目指す受験生のために作成された一元化教材である。</p>
  <p>{当該論点の学習意義に関する 1〜2 文}</p>
  <p>{当該事案の核心突破による応用力育成についての 1〜2 文}</p>
  <p class="closing" style="margin-top:18px;font-size:1.05em">― 一日一論点の積み重ねが、必ず合格の扉を開く。あなたの努力は、必ず報われる。―</p>
</footer>
```

---

## 第21項　禁止事項（通則・v3.2 更新）

1. 配色パターン名（"ホワイト・ノーブル"等）の本文・カバー・ヘッダー記載
2. 短答マークのフレーズ末尾配置（必ず頭文字直前）
3. ヘッダーの `position:sticky` / `position:fixed`
4. 中央タイトル要素・バージョン番号タグの追加
5. 第0部凡例の 4 項目以外の追加（`.font-guide` のみ第10項に基づくオプション例外）
6. 出力の分割提出・継続要求
7. **配色の規律違反**：5 役割（ベース70%／メイン25%／アクセント5%／サブ×2）・「pale bg + dark text」・
   WCAG AA 4.5:1・5 系統制限を満たさない配色（色そのものの選定は全 15 案＋派生から自由／第5項）
8. **12 色固定指標（`--hl-*` / `--tan-*` / `--rank-*`）の科目別変更**
9. 純白 `#FFFFFF` の `body` 背景使用、純黒 `#000000` の文字色使用
10. 5 系統制限を超える独自色系統の新設
11. 色彩意味アンカリングへの矛盾使用（例：成功の意味で赤）
12. 色のみによる情報伝達（記号・文字・配置で重複符号化必須）
13. ハイライト系の段落全体塗布
14. **第6項 11 役割の用途を入れ替えての書体使用**（例：模範答案を丸ゴシで組む／判旨を游明朝で組む等）
15. **`:root` 外での `font-family` 直接指定**（SVG 内 `<text>` のみ例外）
16. **11 役割（＋ `--font-impact`）を超える独自フォントの追加・TX 指定セット外への Google Fonts ロード拡張**
17. 1 見出し配下の 9 項目超チャンク（明示分節必須）
18. **`.key-box` を `> ` 子セレクタで上書きする CSS の追加**（specificity 衝突で内部 padding が壊れるため）
19. **`<strong>第1項</strong>` 形式の旧条文番号表記**（必ず `<span class="para-num">` を使用）
20. **`.statute-emphasis`／`.case-emphasis` への `border-bottom` 復活**（v3.2 で完全廃止）

---

## 第22項　出力前チェックリスト（v3.2 更新）

### 法学教育者ペルソナ
- [ ] 第1部：エグゼクティブサマリー＋登場人物図＋時系列＋ファクト仕分け＋論点抽出
- [ ] 第2部：主要論点 A〜H 完備
- [ ] 第3部：模範答案末尾に採点講評（GRADING ラベル付き）
- [ ] 第4部：論点間優先順位フロー＋実務との架橋コラム
- [ ] 第5部：5-1〜5-6 全エントリに 📌 逆方向リンク
- [ ] 5-1 条文集の全文は `blockquote.statute`（薄グレー）で提示
- [ ] 5-2 判例集の判旨原文は `.judgment-text` クラス（Zen Old Mincho 700）で提示

### 認知心理学ペルソナ
- [ ] 1 見出し配下の並列要素 9 個以下
- [ ] 各章冒頭サマリー／章末チェックリスト
- [ ] 重要概念の言語＋視覚二重表示
- [ ] xref／back-refs で双方向リンク
- [ ] 本文段落のみ 1.4em インデント／見出し系は左ベースライン整合
- [ ] **（逐語録がある場合）`.lecturer-advice`（🎓 講師のアドバイス）を該当論点・部の冒頭に配置**
      （第13-2-bis項・総論は第2部冒頭／論点固有は各 `<h3>` 直後・逐語そのまま貼り付け禁止）

### 機能的色彩設計＋アートディレクション
- [ ] `body { background:var(--base); color:var(--text); }`（純白・純黒大面積禁止）
- [ ] **全 15 案＋派生から問題の雰囲気で AI 自由選定**した配色を、5 色相当を 5 役割に割当て（11 種に限定しない）
- [ ] 5 役割（ベース70%／メイン25%／アクセント5%／サブ×2）が成立している
- [ ] 「pale bg + dark text」：背景は pale〜mid-tone、見出し・本文は dark／本文 WCAG AA 4.5:1 以上
- [ ] 5 系統制限内で配色が調和している（雰囲気の意図を冒頭に 1〜2 文記述）
- [ ] semantic 緑（`#438B48`/`#7BA980`）・金（`#ffd54f`/`#ffaa00`）は維持
- [ ] 12 色固定指標は不変
- [ ] 学習指標は色＋記号／文字／配置の三重符号化
- [ ] 条文（薄グレー）／判例（薄ピンク or accent 派生）でカード地色差別化済み

### タイポグラフィ（v3.2：11 役割）
- [ ] Google Fonts `<link>` は TX `canonical/GENESIS.html` と**完全一致**（**Shippori Mincho B1 / Shippori Antique / Zen Old Mincho / Zen Kaku Gothic Antique / Zen Maru Gothic / Noto Serif JP / Noto Sans JP / Kaisei Decol / Kosugi Maru / Source Code Pro / M PLUS Rounded 1c / M PLUS 1p** をロード）
- [ ] `:root` に **11 個の `--font-*` 変数＋ `--font-impact`** を定義済み（body/soft/display/statute/quote/answer/keyword/judgment/note/professor/mono/impact）
- [ ] `body` は `var(--font-body)`／weight 500／line-height 2.0／letter-spacing .04em
- [ ] `h1` `h2` は `var(--font-display)`（しっぽり明朝 B1 先頭）
- [ ] `h3`〜`h5`、`.subject-tag`、`.tan`、`.arg-tier`、`.back-to-toc`、`th`、`.timeline-label` は `var(--font-soft)`
- [ ] `.doc-header`、ラベル `::before`（KEY/NOTE/WARN/TIP/NG/MODEL ANSWER/GRADING/TYPOGRAPHY）、`.arg-meta` は `var(--font-mono)`
- [ ] `blockquote.statute` ／ `.para-num` は `var(--font-statute)`
- [ ] `blockquote`（汎用）／`blockquote.case` 周辺は `var(--font-quote)`
- [ ] **判旨原文は `.judgment-text` クラスで `var(--font-judgment)`（Zen Old Mincho 700）**
- [ ] `.model-answer` ／ `.arg-card .arg-body` は `var(--font-answer)`
- [ ] **`.key-box` は `var(--font-keyword)`（Kaisei Decol）**
- [ ] **`.note-box`／`.warn-box`／`.success-box`／`.danger-box`／`.basis-card .note`／`.checklist li`／`.back-refs` は `var(--font-note)`**
- [ ] `:root` 外で生の `font-family:` を書いていない（SVG 内 `<text>` のみ例外）

### コンポーネント（v3.2 強化）
- [ ] `.key-box` は specificity 防御（`.key-box, .section .key-box, .container .key-box` の三者結合）
- [ ] `.key-box` に `🔑 KEY` ラベル `::before` ＋ radial 装飾 `::after` あり
- [ ] `.key-box` の padding は `56px 44px 38px 72px`
- [ ] `.note-box` 系全 4 種に `::before` ラベル（ℹ NOTE／⚠ WARN／✓ TIP／✗ NG）
- [ ] `.note-box` 系は `border-left` 単色帯ではなく全周 `border 1px`
- [ ] `.model-answer` に `MODEL ANSWER` ラベル `::before`
- [ ] `.grading` に `GRADING` ラベル `::before`
- [ ] `.exam-mark`／`.tan`／`.arg-tier` は letter-spacing `.08em-.09em`、マーカー透明度 `.42`
- [ ] `.statute-emphasis`／`.case-emphasis` に `border-bottom` なし
- [ ] 条文番号は `<span class="para-num">` 形式（`<strong>第1項</strong>` の旧表記なし）

### 構造・実装
- [ ] `<title>` にファイル ID とサブタイトル
- [ ] `.doc-header` 単独・`position:absolute`
- [ ] カバーに `.subject-tag` で科目名表示
- [ ] `.container` max-width 1080px
- [ ] `.container > section` カード化／入れ子 section リセット
- [ ] フッターに励ましの言葉
- [ ] スムーズスクロール JS
- [ ] `/mnt/user-data/outputs/` へコピー＋`present_files`

---

## 第23項　本文インデント設計（v3.2 新設）

### 23-1. 設計思想

本文段落の左端を、見出し（h2/h3/h4）の『文字』の開始位置と縦のラインを揃えることで、視線の左揃えを乱さず、見出し直下の本文に「見出しから一段下りた」階層感を与える。見出し系自身は左ベースラインに揃え、本文段落のみインデント。

### 23-2. 実装

```css
/* 本文段落・リスト・補助テキストをインデント */
.section > p,
.section > ul,
.section > ol,
section > p,
section > ul,
section > ol,
.ref-entry > p,
.ref-entry > ul,
.ref-entry > ol{
  padding-left:1.4em;
}

/* 見出し・カード系・装飾ボックスは左ベースライン */
.section > h2,
.section > h3,
.section > h4,
.section > h5,
.section > .key-box,
.section > .note-box,
.section > .warn-box,
.section > .success-box,
.section > .danger-box,
.section > .arg-card,
.section > .model-answer,
.section > .grading,
.section > .svg-wrap,
.section > blockquote,
.section > blockquote.statute,
.section > blockquote.case,
.section > .timeline,
.section > table{
  padding-left:0;
  margin-left:0;
}
```

### 23-3. ⚠ specificity 防御の重要性

**`.key-box` を「見出し・カード系」リストに含める場合は、必ず `padding-left:0` のみを上書きし、`.key-box` 自身の内部 padding（`56px 44px 38px 72px`）には触れないこと。**

具体的には、`.section > .key-box{ padding-left:0 }` という記述は **NG**（外部 padding-left を 0 にしようとして、内部 padding 全体を 0 に上書きしてしまう）。

正しくは、`.key-box` 自身の CSS で **specificity 三者結合セレクタ**（`.key-box, .section .key-box, .container .key-box`）を使い、本文インデントリストからの上書きを完全に防ぐ（第13-1項参照）。

### 23-4. 適用範囲の明示

| 対象 | インデント | 理由 |
|---|---|---|
| `<p>`／`<ul>`／`<ol>`（直下） | 1.4em | 本文の視線左ライン整合 |
| `h2`〜`h5` | 0 | 見出しは左ベースライン |
| `.key-box` 等装飾ボックス | 0（specificity 防御で内部 padding は保持） | 装飾の枠位置を維持 |
| `blockquote` 系 | 0 | 引用は左フルブリード |
| `.arg-card`／`.model-answer`／`.grading` | 0 | カードはラベル位置を保つ |
| `.svg-wrap`／`table`／`.timeline` | 0 | 中央寄せ・全幅運用 |

---

## 付録 A　v3.2 における配色 V3 パレット選定の運用例

全パレット（全 15 案＋派生）から問題の雰囲気で AI が自由に選び、5 役割に割り当てる運用例
（下表の名前付きは代表例。これに限定せず複数パレットの組合せ・中間派生色も可）：

| 問題の雰囲気 | 選定パレット | ベース `--base` | メイン `--accent` | アクセント `--mid` | 印象 |
|---|---|---|---|---|---|
| 重厚・道徳論点・難解 | Antique Pearl | `#F2E6E6` 極淡 | `#D4B5C4` モーヴ※暗色派生 | （別 chip 借用 contrast）| 気品・しっとり |
| 手続・公共・清新 | Crystal Blue | `#F5F0F2` 極淡 | `#D4E6EB` ブルー※暗色派生 | `#FFFCD6` 淡イエロー | 透明感・冷静 |
| 軽快・基礎・親しみ | Sweet Berry | `#F9E7E7` 極淡 | `#E8B4BC` ベリー※暗色派生 | `#D4E2E9` ブルー借用 | 甘美・優しさ |
| 深刻・対立が激しい | Twilight Violet | `#F8F2F2` 極淡 | `#E2D4E2` バイオレット※暗色派生 | `#F7EBD6` サンド | 優美・落ち着き |

※ 11 パレットは全 pastel のため、メイン `--accent` は palette identity chip を **HSL で
mid-tone（L=55-65）に暗くした派生**を採り、background ではなく見出し／border の色として使う。
背景はベース／サブの薄色、文字は dark text で contrast を確保する（pale bg + dark text）。

AI は事案テーマ・難度・科目イメージ・論点の重さに応じてパレットを選択し、その意図（雰囲気）を
1〜2 文で出力冒頭に記述することが望ましい。正典 hex は第5-1 表（TX と共通・`docs/palette-v3_2.pdf`）。

---

## 付録 B　タイポグラフィの組合せ判断（v3.2 補遺）

第6項の 11 役割は固定であり、書体の役割入れ替えは禁止である。ただし、AI ディレクション（紙質風・モダン・古典権威風 等）に応じて、**フォールバック先頭の書体を差し替えてよい**ケースを以下に示す。

| AI ディレクション | display | body | keyword | 例外的フォールバック差替 |
|---|---|---|---|---|
| 紙質風（fontDemo 採用） | しっぽり明朝 B1 | A1 ゴシック | Kaisei Decol | （差替なし＝標準） |
| モダン・幾何 | （標準維持） | （標準維持） | M PLUS Rounded 1c 先頭化 | body 先頭に Murecho 追加可 |
| 古典権威 | （標準維持） | Noto Serif JP に切替（明朝本文） | （標準維持） | 法令系教材で例外的に許容 |
| 親しみ・教科書風 | （標準維持） | Klee One を `--font-body` 先頭に追加可 | （標準維持） | 入門書性格を強調 |

差替を行う場合、Google Fonts ロード行に必要書体を追加し、11 役割マトリクスとの整合（用途の混線がないか）を必ずチェックリストで確認すること。

---

## 付録 C　v3.1 → v3.2 移行クイックリファレンス

| 項目 | v3.1 | v3.2 |
|---|---|---|
| フォント変数の数 | 6 | **11** |
| `body` font-weight | 400 | **500** |
| `body` line-height | 1.92 | **2.0** |
| `body` letter-spacing | .01em | **.04em** |
| `.container` max-width | 1100px | **1080px** |
| `.key-box` フォント | （指定なし／--font-body継承） | **`--font-keyword`（Kaisei Decol）** |
| `.key-box` padding | 16px 20px | **56px 44px 38px 72px** |
| `.key-box` ラベル | なし | **🔑 KEY ::before** |
| `.note-box` 系 構造 | border-left 単色帯 | **全周 border ＋ ::before ラベル** |
| `.model-answer` ラベル | なし | **MODEL ANSWER ::before** |
| `.grading` ラベル | なし | **GRADING ::before** |
| 条文番号 | `<strong>第1項</strong>` | **`<span class="para-num">第1項</span>`** |
| 判旨フォント | `--font-quote` | **`.judgment-text` で `--font-judgment`** |
| `blockquote.statute` 背景 | AI設計派生色 | **薄グレー `#f3f4f6` 推奨** |
| `blockquote.case` 背景 | AI設計派生色 | **薄ピンク `#ffeef1` または accent 派生** |
| `.statute-emphasis` border-bottom | あり | **削除** |
| `.exam-mark`/`.tan` letter-spacing | .05em | **.08-.09em** |
| 本文インデント | なし | **1.4em（第23項）** |
| ハイライト透明度 | 不問 | **.42 推奨** |

---

**仕様書終わり（Ver.3.2）**