---
description: RB（リモートバッチ）— inputs/000_TX/{科目} の「N番からM番まで」をリモートで active v13.1.0 LOOP-CARD の二系統（公式＋Lexia _lex）で連続生成し、各問完了ごとに git commit/push で永続化する。「346-350 を RB して」「RB 346〜350」等で起動。
---

# rb：リモートバッチ（Remote Batch）コマンド

## 何をするか

`inputs/000_TX/{科目}/` 配下の **指定番号レンジ（N番〜M番）** を、`new-tx` / `batch-tx` の
**active 経路そのまま**で 1 問ずつ連続生成し、**各問の検証通過ごとに git commit/push**
で GitHub に永続化する。リモート実行環境（Claude Code on the web）でのバッチ運用を
1 コマンドで回すための薄いラッパー。**版・起点・検証は固定記憶に頼らず、必ず先に
`docs/canonical-lineage.md` の active 行を読んで決める**（下記は 2026-07-07 時点の active）。

> **active＝v13.1.0 LOOP-CARD（基盤 v13.0.0）。** `_lex` の唯一起点は
> **`canonical/GENESIS-CARD.html`（gold=刑TX359）＋`canonical/GENESIS-CARD.placeholder.html`（スロット契約）**、
> 構造 spec は **`spec/tx-v13.1.0-loopcard-core.md`**。生成規律は **`.claude/commands/new-tx.md` を完全に継承**する
> （このファイルはレンジ・ループと永続化だけを足す薄いラッパー＝生成方法は new-tx が正典）。

## 引数（レンジ指定・必須）

`$ARGUMENTS` から **開始番号と終了番号** を読み取る。次のいずれの表記も許容：

- `346-350` / `346〜350` / `346~350`
- `346 350`
- `346から350`（「から」「まで」「を」「RBして」等の語は無視して数字だけ抽出）

抽出ルール：
- 数字グループを 2 つ取り、小さい方を `START`、大きい方を `END` とする。
- 数字が 1 つしか無い場合：その番号から **5 問**（`START`〜`START+4`）を既定とする。
- 数字が 0 個 → **処理中断**し、user にレンジを確認（無断推定禁止）。
- 科目が文脈から特定できなければ既定は刑法（`001_刑法`）。他科目は「刑訴 401-405 を RB」等で指定。

## Phase 0：プリフライト（必須・自動）

1. **canonical-lineage.md の active 行を読む**（版・起点・validator を確定。固定記憶の版名に頼らない）。
2. **本線同期の確認**（二台運用・CLAUDE.md §8）：
   ```bash
   git fetch && git log --oneline origin/master -3
   ```
   ローカルが遅れていれば user に `git pull origin master` を促す。
3. **対象 PDF の実在確認**：`START`〜`END` の各 `inputs/000_TX/{科目}/{N}.pdf` が存在するか点検。
   - **TX 入力 PDF は削除しない方針（CLAUDE.md §9「TX 入力 PDF の保持」）**なので、生成後も残す。
   - 欠番があれば一覧で報告し、**欠番を除いた実在分のみ**を対象にするか、Drive「抽出PDF」
     （`1 TX_短答/{科目}/抽出PDF`・原本 445 問）から `inputs/000_TX/{科目}/` へ回収するかを user に確認。
     **repo のローカル PDF は現状 000〜330。360 以降は Drive のみ**なので、その帯は回収してから対象化する。
4. **対象リスト提示 → 即実行**（RB は明示レンジ起動なので確認は 1 回だけ）：
   ```
   RB 対象：346.pdf 〜 350.pdf（5 ファイル・実在 5 / 欠番 0）
   経路：active v13.1.0 LOOP-CARD（canonical/GENESIS-CARD.html＋placeholder スロット・二系統）
   配色：大前提のみ V3（P1/P2/P3・11 パレット AI 選定）／--base は固定クリーム #F7F1E9
   保存：各問完了ごとに git commit/push（本線 master へ集約）で GitHub 永続化
   開始します。
   ```
   欠番ゼロ・PDF 実在が確認できれば、原則そのまま Phase 1 へ進む
   （ブロッキングの y/n は取らない。中断を嫌う運用方針 CLAUDE.md §8）。

## Phase 1〜N：レンジ・ループ実行

`START` から `END` まで 1 問ずつ、**`.claude/commands/new-tx.md` の active v13.1.0 経路を完全実施**：

- **起点＝`canonical/GENESIS-CARD.html` を複製**し、`canonical/GENESIS-CARD.placeholder.html` の
  **スロットだけ**を本問固有に埋める（CSS/JS/class/DOM/節順は固定・接ぎ木禁止・例外は配色パレット選定のみ）。
  `outputs/*/` の別問題 HTML を template 参照しない・`render.py` 経路は禁止。
- **二系統出力（必須・new-tx Phase 4h）**：1 問＝公式 `outputs/000_TX/{科目}/{接頭辞}{NNN}.html`（本物5択）
  ＋ Lexia 用 `outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html`（ox-grid＋解法ナビ）。解法ナビは
  `canonical/SOLVE-NAV.html` のエンジンを逐語コピーし問題固有データのみ記述。
- **v13.1.0 の中身（new-tx 上部ボックス）**：正誤表（印付き原文 `data-brief-mark`＋法理コア＋成績エンジン）→
  体系マップ SVG（記述札に ✍規範核バッジ `.nb-badge`・`▼本問の帰結`箱は置かない）→ 横断3軸マトリクス →
  記述カード（統合解説＋📚BASIS＋⚠️横串trap＋🗝記憶のフック＋相互リンク往復）→ 物語解説（`_lex` のみ）。
  v13m 執筆規約（`docs/tx-v12.2.1-inline-lock.md` §v13m）を守る。
- **物語解説は `_lex` の必須要素**（new-tx Phase 4i・`.fa-narrative`・記号フリー）。

各問完了時に内部記録（`pdf_number` / `output_path`(公式・_lex) / `validate_errors` /
`palette_pattern` / `committed`(commit hash) / `status` / `failure_reason`）を保持。

## Phase 6 相当：検証（両ファイル・省エネ方針）

各問、公式と `_lex` の**両方**に機械ゲートを通す（new-tx Phase 6・トークンほぼ0の安全網）：

- `python scripts/validate-tx-core.py <_lex.html>`（**ox-grid 必須**・G1〜G45＋**G50 v13構造**＝印付き原文/
  規範核バッジ/帰結箱不在/成績エンジン。G51〜G55 ERROR）。
- `python scripts/validate-tx-core.py <公式.html>`（公式＝single/multi 可・G23/G25 自動緩和）。
- `python scripts/check-tx-lex-engine.py <_lex.html>`（G41/G50〜G54・接ぎ木/表示LOCK の push 前ゲート）。
- `python scripts/check-duplicates.py outputs`（公式↔_lex ミラーは除外＝正常・他の重複のみ検出）。
- **ERROR 0 件**を確認（G50 の WARNING＝規範核バッジ/印付き原文の未鋳造は、新規生成では 0 にしてから配信）。
- 執筆者本人が自己照合1回＋確信の持てない/非著名判例だけ的絞りWeb一次確認（new-tx Phase 6 (b)(c)）。

## エラーハンドリング（batch-tx 継承）

- API socket error → その問 **PARTIAL**、次へ（停止しない）。
- validate ERROR → その問 **FAILED**、出力残置、次へ。
- **3 問連続失敗で停止**し、user に報告。
- 失敗問の再生成は `/new-tx inputs/000_TX/{科目}/{N}.pdf` で個別実施（自動 retry はしない）。

## Phase 7 相当：git コミットで永続化（§9）

各問、検証通過後に：

1. **フッター生成日時＋版を刻む**：`python scripts/stamp-created-date.py`（`outputs/000_TX` と `outputs/ux` を走査し
   `Generated: … / TX v13.1.0 LOOP-CARD`・class=lexia-genmeta を冪等付与。版は実体判定で
   `scripts/tx-lex-v13-stamp.py --apply` が確定）。素の git commit でも pre-commit フック（§9）が保険で刻む。
2. **両ファイルを add → 本問単位で commit → push**（本線 master へ集約・§8/§9・数十問を1コミットにまとめない）：
   ```
   git add outputs/000_TX/{科目}/{接頭辞}{NNN}.html outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html
   git commit -m "feat(tx): {接頭辞}{NNN} を二系統生成（公式5択／Lexia用 v13.1.0 LOOP-CARD）"
   git push -u origin <作業ブランチ>
   ```

## 完了レポート（必須）

- 各問：番号 / status / サイズ(公式・_lex) / validate 結果 / 採用パレット / **commit hash**。
- **`committed` 未完の問が無いか点検**し、全 SUCCESS 問の GitHub 反映（push 済み）を保証してから終了。
- HTML は git 管理（§9）。**生成＝コミットで GitHub が永続先**。未 commit/push の問が残る場合は、
  コンテナ回収前に最優先で commit/push する。

## v13.1.0 LOOP-CARD 鉄則（new-tx / batch-tx から継承）

- **唯一の skeleton 起点＝`canonical/GENESIS-CARD.html`（＋`.placeholder.html` スロット契約）**。
  `outputs/*/` の別問題流用・`render.py` 経路は禁止（同一問題の公式→_lex 複製は二系統手順で許可）。
- スロットだけ本問固有に埋める（CSS/JS/class/DOM/節順/SVG エンジンは固定・接ぎ木禁止・例外は配色パレット）。
- 二系統は必須（公式＋_lex を両方 push・answer は整合）。物語解説は `_lex` の必須要素。
- 配色 V3 は**大前提のみ**（`--base` は固定クリーム #F7F1E9）。SVG は AABB 衝突検査。
- 1 メッセージ 50KB 超出力禁止（section 分割）。最新法令・判例・学説レビューと省エネ検証（new-tx Phase 6）。

$ARGUMENTS
