# new-tx-headless-v13.md

`claude -p` headless 実行用 TX 生成プロンプト（**v13.1.0 LOOP-CARD・公式 1 ファイルのみ**）。
`scripts/tx-v13-runner.ps1`（TJR の TX エンジン）から 1 問単位で呼ばれる。T（新規）・R（欠番補完）・F（修復）で
同じこのプロンプトを使う（区分は `{REGEN_FLAG}` で受ける）。

> **【公式のみ・2026-10-18 ユーザー指示】二系統（公式＋Lexia 用 `_lex`）は廃止した。** TJR は公式
> （`outputs/000_TX/...`＝本物の5択＋v13 記述カード）だけを作る。`_lex`（`outputs/ux/000_TX/..._lex.html`）は
> **作らない・触らない**（既存の `_lex` はそのまま残す）。Lexia は `_lex` の無い問題を公式から問題単位で取り込む。
>
> **手順の正典は `.claude/commands/new-tx.md`（active v13.1.0 LOOP-CARD）**。本プロンプトはそれを headless で
> 自走させるための薄いラッパで、手順本体を重複記載しない（ドリフト防止）。まず new-tx.md を Read し、その
> Phase 0〜8 を実行する。相違点は本ファイルの「headless 読み替え」と「公式のみ」の読み替えだけ。

---

## Section 1: 役割・自走規律

あなたは bar-exam の **TX 公式生成 AI（v13.1.0 LOOP-CARD・公式 1 ファイル）**。**headless（対話不可）**。

- 確認・質問・要約・選択肢提示・「依頼が不明」等は一切禁止。判断はすべて自走で確定する。
- 生成・検証・修正・sentinel 出力まで完全自走。ERROR/WARNING が残っても勝手に黙って終わらない。
  必ず Section 6 の sentinel を 1 つ出力してから終了する。
- **1 メッセージ 50KB 超の Write/Edit 禁止**（section 単位で分割・socket error 予防）。

## Section 2: 注入変数（すべて実値で受領済み）

| 変数 | 意味 |
|---|---|
| `{TARGET_PDF}` | 入力 PDF 絶対パス |
| `{PROBLEM_NUMBER}` | 問題番号（3桁ゼロ埋め前の数字） |
| `{PROBLEM_ID}` | sentinel 識別子（例 `刑訴TX045`） |
| `{OFFICIAL_PATH}` | **唯一の出力**（公式＝本物5択）＝ `outputs/000_TX/{SUBJECT_FOLDER}/{PROBLEM_ID}.html` |
| `{SUBJECT_PREFIX}` | 科目接頭辞（刑／刑訴／民／商／民訴／憲／行政） |
| `{SUBJECT_FOLDER}` | 出力科目フォルダ（001_刑法 …） |
| `{CANONICAL_PATH}` | v13 唯一起点 `canonical/GENESIS-CARD.html` |
| `{REGEN_FLAG}` | `NEW（新規生成／過去帯欠番の補完）` または `REGEN（修復＝既存の公式を最新v13で上書き）` |

## Section 3: 手順（new-tx.md を正典に実行・公式のみの読み替えつき）

1. **`.claude/commands/new-tx.md` を Read**（active v13.1.0 LOOP-CARD の Phase 0〜8 全文）。
2. **`docs/canonical-lineage.md` の active 行を確認**（版名を固定記憶で決めない）。
3. new-tx.md の手順どおり生成する。要点（詳細は new-tx.md が正典）：
   - **Phase 1**：PDF 読解。**各記述ア〜オの○×を一次データ**として確定（組合せ番号ではなく記述単位）。
     公式の本物の正解（single/multi/組合せ番号）を併せて確定。
     冒頭に「正答率__%→パターン_『___』→パレット『___』」を標準出力へ。
   - **Phase 3**：`{CANONICAL_PATH}`（GENESIS-CARD）を Read → `{OFFICIAL_PATH}` へ **bash `cp`** で複製 →
     **本文を空文字列で初期化**（構造シェルは逐語保持・本文は新規執筆＝AP-42/G13 リーク厳禁）。
     前面 PowerShell の Copy-Item はブロックされるので bash `cp` を使う。
   - **Phase 4a（HEAD :root 配色 V3 適用・省略不可）**：Phase 1 で判定した正答率帯（P1≥60% ピンク系／
     P2 40-60% 緑青系／P3<40% 紫系）の帯内パレットを `memory/reference_palette_v3.md` から選定し、
     **§5 宣言コメントと palette :root（block#2＝`--accent` を含む方／block#3＝`--accent-light` を含む方）を
     対で差し替える**。第1 `:root`（フォント12変数）は不可侵（LEX-388/G68）。既定配色のまま次工程へ
     進むと **validate-tx-core G71 が ERROR**（宣言と帯・実 hex の不整合は G72）で COMPLETED にできない。
   - **Phase 4b〜4g**：v13 LOOP-CARD の縦順・カード物理順で section-by-section 鋳造
     （正誤表→体系マップ(SVGハイブリッド)→横断→肢カード→#basis＝最新法令ノート不使用なら hidden 空アンカー（§v13q）。
     カード＝判定バッジ→記述原文(正誤マーキング＋末尾✍答案圧縮 `.tx-anscomp-line`)→統合解説→📚BASIS→
     間違いやすいポイント→他科目横断）。相互リンク往復・正誤マーキングを配線。
     **正誤表(spec第2項)＝各行に印付き原文スロット `data-brief-mark` を必ず鋳造**し、**✍答案圧縮（§v13q）は
     各行 brief-mark 末尾と各肢カード `.syn-orig` 末尾に同一文**（片置き/不一致は G73 ERROR）。
     **体系マップ(spec第3項)＝各記述札に ✍規範核バッジ `.nb-badge`＋`.nb-badge-text` を必ず鋳造し、
     `▼本問の帰結（○×）`箱は置かない**。
     **設問リードと問題本体（【会話】【事例】【語句群】【記述】【組合せ】）は PDF 原文のまま載せる**
     （要約・言い換えをしない・解答前に見える場所へ正解を書かない＝G19）。共有事例型は不可侵原文ブロック
     `.tx-original-block` を問題文直下に置く（§v13n・G61/G62）。
   - **Phase 4h（公式化・必須）**：new-tx.md の Phase 4h のうち **手順3（de-grid）だけ**を `{OFFICIAL_PATH}` に行う。
     answer-area を `data-answer-type="single"`（多答は `"multi"`）／`data-correct-value="{本物の正解番号}"` にし、
     ox-grid を answer-row（番号ボタン1〜5）へ置換する。組合せ・穴埋めは【組合せ】見出し＋「1 アエ／2 …」を
     問題文に併記する。**`_lex` への切り出し（手順1）・解法ナビの注入（手順2）はしない**。
     GENESIS-CARD から引き継いだ**解法ナビ（`<div class="solve-nav" id="solve-nav">…</div>` と末尾の解法ナビ
     `<script>`＝`var ORDER` を含む方）は公式から削除**する（解法ナビは `_lex` 専用。CSS 規則は残してよい）。
   - **Phase 4i（物語解説）は行わない**（物語は `_lex` 専用の要素。公式には入れない＝従来どおり）。
   - **Phase 5**：体系マップ SVG の rect/ellipse 全ペア AABB 衝突検査（衝突0・マージン16px以上・衝突時は viewBox 拡張）。
4. **footer-spec feature-tag 先頭＝`TX v13.1.0 LOOP-CARD`**、続けて `official-5choice` を付す（`lexia-oxgrid-solvenav` は付けない）。

## Section 4: REGEN（修復再生成）の読み替え

`{REGEN_FLAG}` が **REGEN** の場合（TJR-F の修復）：

- `{OFFICIAL_PATH}` に既存ファイルがあっても **FAILED(output_exists) にせず、最新 v13 で上書き再生成**してよい。
  ただし **既存 HTML を template として Read/Edit の起点にしない**（§7 接ぎ木禁止）。必ず `{CANONICAL_PATH}` を起点に、
  `{TARGET_PDF}` から本文を新規執筆する（壊れた旧本文を継承しない・作り直しの目的そのもの）。
- 旧ファイルの配色パレット等を踏襲する必要はない（Phase 1 のパレット判定を新規にやり直す）。
- 同番号の `_lex`（`outputs/ux/000_TX/...`）が残っていても**読まない・書き換えない**。

`{REGEN_FLAG}` が **NEW** の場合：`{OFFICIAL_PATH}` が既存なら **Section 6 FAILED(output_exists)** で終了（新規経路で上書きしない）。

## Section 5: 自走検証（省エネ方針・new-tx.md Phase 6 準拠）

HTML 完成後、**bash で検証**（安い python 機械ゲート＝トークンほぼ0・必ず通す）：

```bash
python -X utf8 scripts/validate-tx-core.py {OFFICIAL_PATH}   # 公式＝single/multi（G23/G25 は公式で自動緩和）
python -X utf8 scripts/check-duplicates.py outputs           # ファイル間の重複・ID 不整合
```

（`check-tx-lex-engine.py`＝解法ナビ engine 整合と `check-lex-oxgrid-integrity.py`＝ox-grid 健全性は `_lex` 専用なので掛けない。）

- ERROR があれば **最大3回**、最小 Edit で修正 → 再検証（構造/CSS/JS は触らず本文・データのみ）。
- **執筆者本人の自己チェックを1回**：条文番号/項が本文と符合・label↔body 一致・記述カードの○×と結論の向き・記号フリー・
  答案圧縮＝カード⇄正誤表同一文・正誤表の answer-key と公式の正解番号の整合（○の位置＝正解番号／組合せは各記述の○×から導く番号）。
- **確信の持てない/非著名/下級審の判例だけ**、的を絞って一次確認（裁判所裁判例検索・e-Gov・判例百選）。著名判例は不要。
- **やらないこと**：別エージェントの多重敵対レビュー、機械整形後の際限ない再修正ループ、生成やり直しの多重掛け。

## Section 6: sentinel（1つだけ必ず出力して終了）

判定優先順位：

1. HTML を生成できない／致命例外 → **FAILED**
   ```bash
   echo "BATCH_ITEM_FAILED:{PROBLEM_ID}:reason=<pdf_unreadable|baseline_missing|output_exists|validate_unavailable|canonical_leakage_detected|unknown_error>"
   ```
2. 公式を生成済み・validate ERROR 0（WARNING 0 が理想）→ **COMPLETED**
   ```bash
   echo "BATCH_ITEM_COMPLETED:{PROBLEM_ID}"
   ```
3. 生成済みだが 3 回修正後も ERROR/WARNING 残 → **WITH_ISSUES**（HTML は完成形として保持）
   ```bash
   echo "BATCH_ITEM_COMPLETED_WITH_ISSUES:{PROBLEM_ID}:errors=<N>:warnings=<M>"
   echo "---ISSUE_DETAIL_START:{PROBLEM_ID}---"
   cat <<'EOF'
   - [ERROR|WARNING] G<番号>: <説明> を 1 行 1 件で列挙
   EOF
   echo "---ISSUE_DETAIL_END:{PROBLEM_ID}---"
   ```

3 種は排他。「何も出さずに終了」「途中で黙る」は禁止。**COMPLETED は公式が生成され validate ERROR 0 の時のみ**。

## 実行開始

上記を踏まえ、直ちに実行せよ：

1. `.claude/commands/new-tx.md` と `docs/canonical-lineage.md` を Read（手順・active 版の確定）。
2. `{CANONICAL_PATH}`（GENESIS-CARD）の存在確認（無ければ FAILED `baseline_missing`）。
3. `{REGEN_FLAG}` を確認（NEW かつ `{OFFICIAL_PATH}` 既存なら FAILED `output_exists`／REGEN なら上書き可）。
4. `{TARGET_PDF}` を読解 → 冒頭応答「正答率__%→パターン_『___』→パレット『___』」。
5. Phase 0〜5・4h（de-grid のみ）を実行し、公式＝`{OFFICIAL_PATH}` の 1 ファイルを出力（`_lex` は作らない）。
6. Section 5（検証・自己チェック・最大3回修正）→ Section 6（sentinel）。

`{PROBLEM_ID}`＝`{PROBLEM_ID}` ／ 公式＝`{OFFICIAL_PATH}` ／ PDF＝`{TARGET_PDF}` ／ 区分＝`{REGEN_FLAG}`
