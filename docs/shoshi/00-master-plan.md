# 司法書士試験対策アプリ（コードネーム SCRIBA）全体計画

> 確定日 2026-10-18（設計セッション＝最上位モデル）。本書が司法書士版の **入口** であり、
> 下位文書（`01-kijutsu-html-contract.md`／`02-content-repo-canonical.md`／`03-session-briefs.md`）の正典順位を定める。
> コードネームはすべて仮（SCRIBA＝アプリ／shoshi-exam＝コンテンツリポジトリ／THOTH＝記述式正典／STYLUS＝ひな形正典）。
> 名前を変えるときは本書だけ直せばよいよう、他文書は本書の名前を参照する。

---

## 0. 結論（学習法 → 製品方針）

| 試験区分 | 学習法の結論 | 製品への写像 |
|---|---|---|
| 択一式（午前35＋午後35） | 過去問集（合格ゾーン級）を肢ごと理由付き○×で回し切る | **TX をそのまま横展開**（`_lex` 一問一答＋肢キー SM-2）。新規開発なし＝科目追加だけ |
| 記述式（不登1＋商登1・各70点） | ①ひな形暗記（部品）②過去問で判断の型を周回（骨子まで）③月1〜2回の通し | ①**HX ひな形カード**（想起→自己採点＝ARIADNE 想起契約を流用）②**KX 申請一覧パズル**（骨子パズル同型）③**KX 申請書フォーム採点＋タイマー** |

「ひな形暗記だけで完結するアプリにしない」が最重要の製品規律。HX だけでは記述式の基準点割れを防げない。

試験の骨格（法務省受験案内に基づく。年度ごとに要再確認）：

| 部 | 形式 | 科目と問数 |
|---|---|---|
| 午前 択一 35問 | 5肢（組合せ型が主） | 憲法3・民法20・刑法3・商法会社法9 |
| 午後 択一 35問 | 同上 | 民訴5・民執1・民保1・司法書士法1・供託法3・不登法16・商登法8 |
| 午後 記述式 2問 | 申請書作成 | 不動産登記法1・商業登記法1（令和6年度から各70点） |

法令基準日は **当該年の 4 月 1 日現在施行の法令**（受験案内）。択一・記述とも旧年度問題は現行法ノートで差分を補う（bar-exam の `tx-current-law-note` と同型）。

---

## 1. アーキテクチャ（決定）

### 1-1. アプリ＝Lexia の **ビルド変種**（フォークしない）

前回の口頭案「UI はフォーク・lib は共有」を、Lexia の実コードを読んだ上で次のように確定する：

- Lexia の本体 `src/App.jsx`（2.3万行）のうち、取込・ライブラリ・復習プール・SM-2・統計・同期は **司法書士版でもそのまま要る**。フォークすると 2.3 万行の二重保守になる。
- 真のコアは **トラッカー（`QUIZ_TRACKER_SCRIPT`）＋HTML 抽出器群（App.jsx 1,204〜3,035 行の素の関数）＋`src/lib`** であり、ここは単一ソースにすべき。
- よって **同一リポジトリ `lexia` を `VITE_EXAM_PROFILE=bar|shoshi` の 2 ビルドにする**。別 Cloudflare Worker（名前 `scriba`）・別 Supabase プロジェクト・別 IndexedDB 名・別 manifest/アイコンで **利用者から見れば別アプリ**。
- 司法書士固有 UI（HX/KX の一覧・採点画面）は `src/components/kx/*` に置き、プロファイルの `features` で表示を切る（bar ビルドには一切出ない）。

| 層 | bar と shoshi で共有 | shoshi だけ |
|---|---|---|
| トラッカー・抽出器・SM-2・同期・UI 骨格 | ◯（単一ソース） | — |
| 試験プロファイル（科目表・接頭辞・取込元・カテゴリ・機能フラグ） | 形は共有 | 値は別 |
| HX/KX 用 抽出器・トラッカー枝・採点カード UI | コードは共有リポに置く（bar では不活性） | 有効化は shoshi |
| 保存域（IndexedDB 名・Supabase プロジェクト）・配布（Worker 名・manifest） | — | 別 |

### 1-2. コンテンツ＝別リポジトリ `shoshi-exam`

bar-exam とは **別リポジトリ**。理由＝命名規則・科目表・CLAUDE.md・検証ゲート・TJR ランナーが司法書士固有になり、bar-exam の CLAUDE.md（司法試験専用の規律が数百行）と混ぜると両方が読めなくなる。
bar-exam からは **canonical と scripts の必要分を複製**して出発する（`02-content-repo-canonical.md`）。

シリーズ記号：

| 記号 | 内容 | 1ファイル | 正典（複製起点） | Lexia 取込 |
|---|---|---|---|---|
| **TX** | 択一（公式5択＋`_lex`） | 1問 | bar-exam の `GENESIS-CARD`／`GENESIS-CORE`／`SOLVE-NAV` を複製（司法書士向け追補＝先例カード・法令階層） | `_lex` のみ（従来どおり） |
| **HX** | ひな形カード集（記述式の部品層） | 1登記類型 | **STYLUS.html**（新規・ARIADNE 想起契約＋GENESIS-CARD 誌面） | 想起カード（`data-recall`） |
| **KX** | 記述式過去問（別紙＋申請一覧パズル＋申請書フォーム採点＋deep） | 1問 | **THOTH.html**（新規・ARIADNE LOOP-FOLD／骨子パズル／周回モード同型） | 欄単位（新 kind `kxfield`） |

---

## 2. フェーズ計画（担当モデル・完了条件）

| Phase | 内容 | 場所 | モデル | 完了条件 |
|---|---|---|---|---|
| **0** | 設計固定（本書＋01/02/03） | bar-exam `docs/shoshi/` | 最上位（本セッション） | draft PR → master へマージ |
| **1** | Lexia：試験プロファイル導入＋抽出器とトラッカーの `src/lib` 分離＋`data-qid` 安定キー | lexia | Opus 5.5（effort high） | `npm run test:all` PASS・bar ビルドの挙動不変（本番デプロイ後の実機確認）・PR |
| **2a** | コンテンツリポ bootstrap（CLAUDE.md・フォルダ・canonical 複製・validate の科目表設定化・TJR 移植） | shoshi-exam（新規） | Opus 5.5 | 不登TX の試作 1 問が二系統で validate PASS し `_lex` が SCRIBA に取り込める |
| **2b** | SCRIBA ビルド変種（プロファイル・Worker・Supabase・manifest・IndexedDB 分離）＋KX/HX トラッカー枝＋kxfield プールカード | lexia | Opus 5.5 | `VITE_EXAM_PROFILE=shoshi` のビルドが別 URL で動き、shoshi-exam から取込できる。bar ビルドは不変 |
| **3** | gold 3 点＝不登TX×5／不登HX×1群／不登KX×1 ＋ 正典 STYLUS/THOTH の本文 | shoshi-exam | **最上位モデル・推論最大**（内容レビュー規律＝bar-exam CLAUDE.md §3 と同じ） | validator PASS・内容の一次確認済み・実機で SM-2 に乗る・ユーザー承認 |
| **4** | 量産（TJR 移植：T=択一 11 科目／H=ひな形／K=記述式過去問） | shoshi-exam | Opus 5.5 固定（headless） | バッチごとに PASS のみ commit/push（bar-exam と同じ claim・ESCALATE 規律） |
| **5** | 変種生成（同一論点で登場人物・日付・登記記録を差し替えた KX 派生） | shoshi-exam | 後日 | gold の型が安定してから |

順序の理由：Phase 1 は Phase 2b の前提（プロファイルが無いと変種ビルドが作れない）。Phase 2a と 2b は独立（並行可）。Phase 3 は 2a/2b の両方が要る（gold を実機で SM-2 に乗せて初めて契約の妥当性が分かる）。

---

## 3. 正典順位と変更規律

1. 本書（計画・名前・フェーズ）
2. `01-kijutsu-html-contract.md`（HX/KX の DOM 契約・SM-2 キー・Lexia 側の抽出規則・validator ゲート）
3. `02-content-repo-canonical.md`（shoshi-exam の構造・命名・科目表・bar-exam からの複製範囲・TX 追補）
4. `03-session-briefs.md`（各 Phase のセッション用プロンプト）

契約（01）を変えるときは **コンテンツ側 validator と Lexia 側抽出器を同じ PR 群で変える**（bar-exam の「検出ゲートと復元ツールは同一式」の規律と同じ）。契約を変えずに実装だけ進めるのが原則。

---

## 4. やらないこと（最初から決めておく）

- ひな形暗記だけで完結する記述式 UI（§0）。
- 記述式の自由記述を LLM 採点する機能。欄単位の決定論採点＋自己採点に限る（LLM 講評は Lexia 既存の AI 講評を後日流用してよいが、基準点対策の主経路にしない）。
- 司法試験 corpus（bar-exam の 民法/憲法/刑法/商法/民訴 TX）の流用。問われ方が違う（§0・前回決定）。
- `<table>` を一問一答の面に使うこと（bar-exam §v15 の実測＝Lexia の行複製が壊れる）。
- 設問・別紙の要約／言い換え（原文不可侵＝bar-exam §v13r/§v13s と同じ）。
