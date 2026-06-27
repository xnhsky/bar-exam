# Codex 引き継ぎ：TX / JX 生成手順書

> **このファイルの目的**：OpenAI Codex（または Claude 以外のコーディングエージェント）に
> bar-exam の TX（短答）・JX（論文/事例）HTML 教材を生成させるための、**自己完結した実務指示**。
> Codex は Claude Code のスラッシュコマンド（`/new-tx` 等）・`present_files`・サブエージェント
> （`Agent`）を持たない前提で書いてある。正典は `CLAUDE.md`・`spec/`・`.claude/commands/` だが、
> 本書だけ読めば一通り生成できるようにしてある。**矛盾が出たら `CLAUDE.md` と `spec/` が優先**。

---

## 0. Codex に最初に伝えること（要約・コピペ可）

```
あなたは bar-exam リポジトリで司法試験対策 HTML を生成する。守るべき鉄則：

1. 起点は canonical/ だけ。outputs/ の既存 HTML を template に cp/Read/Edit しない。
   - TX コア = canonical/GENESIS-CORE.html
   - TX 別冊 = canonical/GENESIS-DEEP.html（任意・後追い）
   - TX 解法ナビ = canonical/SOLVE-NAV.html（_lex に注入）
   - JX 本体 = canonical/ATHENA.html
   - JX 副産物 = canonical/AXIOM.html(RX) / ARBOR.html(TREE) / ARIADNE.html(ARIADNE)
2. clone したら本文を空文字列で初期化してから PDF を見て新規執筆（content independence）。
   canonical の本文・解説・判例引用を残さない／流用しない。
3. <script>…</script> 内に "</body>" リテラルを書かない（Lexia の正規表現で全機能死亡）。
   代替表現：「body 閉じタグ」「'</'+'body>'」等。
4. ファイル名・出力先は §2 命名規則どおり（科目接頭辞＋3桁0埋め）。
5. 生成＝git commit/push で永続化（コンテナは ephemeral）。検証 PASS まで配信しない。
6. 1 つの Write/Edit で 50KB を超えない（section 単位に分割）。
7. render.py は実行禁止（WIP 上書き事故）。
8. 応答は日本語・簡潔に。
```

---

## 1. 環境とブランチ

- リポジトリ：`xnhsky/bar-exam`。作業ブランチは指示されたもの（例：`claude/codex-tx-jx-handoff-r3p2ws`）。
- 作業開始前に本線を取得：

  ```bash
  git fetch origin
  git switch <作業ブランチ>   # 無ければ git switch -c <作業ブランチ> origin/master
  ```

- Python 依存：`validate-*.py` は標準ライブラリ中心。JX の逐語照合（任意）だけ
  `pymupdf pytesseract pillow scikit-learn` ＋ `tesseract-ocr-jpn` が要る。生成・検証本体には不要。
- **`memory/reference_palette_v3.md`（パレット hex 一覧）はリポジトリに無い**（ローカル専用）。
  Codex は **canonical の `:root{}` が持つ既定配色をそのまま使う**のが安全。TX v11.1.0 は
  `--base` 固定クリーム＋ §18〜§22 の配色オーバーレイが canonical 内蔵なので、配色は
  clone でほぼ揃う（下記 TX 手順 4a 参照）。色を攻めたいときだけ `docs/palette-v3-images/` を参照。

---

## 2. 命名規則（TX・JX 共通）

形式：`{日本語科目接頭辞}{TX|JX}{3桁0埋め}.html`

| 科目 | TX 接頭辞 / 出力先 | JX 接頭辞 / 出力先 | 入力フォルダ |
|---|---|---|---|
| 刑法 | `刑TX` `outputs/000_TX/001_刑法/` | `刑JX` `outputs/001_JX/001_刑法/` | `…/001_刑法/` |
| 刑訴 | `刑訴TX` `outputs/000_TX/002_刑事訴訟法/` | `刑訴JX` `outputs/001_JX/002_刑事訴訟法/` | `…/002_刑事訴訟法/` |
| 民法 | `民TX` `outputs/000_TX/003_民法/` | `民JX` `outputs/001_JX/003_民法/` | `…/003_民法/` |
| 商法 | `商TX` `outputs/000_TX/004_商法/` | `商JX` `outputs/001_JX/004_商法/` | `…/004_商法/` |
| 民訴 | `民訴TX` `outputs/000_TX/005_民事訴訟法/` | `民訴JX` `outputs/001_JX/005_民事訴訟法/` | `…/005_民事訴訟法/` |
| 行政法 | `行政TX` `outputs/000_TX/006_行政法/` | `行政JX` `outputs/001_JX/006_行政法/` | `…/006_行政法/` |
| 憲法 | `憲TX` `outputs/000_TX/007_憲法/` | `憲JX` `outputs/001_JX/007_憲法/` | `…/007_憲法/` |

**番号抽出**：PDF ファイル名から最初の連続数字を取り、3桁未満は0埋め（`1`→`001`、`22`→`022`）、
3桁超はそのまま（`1234`→`1234`）。**数字が取れなければ中断してユーザーに確認**（無断推定禁止）。

- TX 入力 PDF：`inputs/000_TX/{00N_科目}/{番号}.pdf`
- JX 入力：`inputs/001_JX/{00N_科目}/重問PDF/{番号}.pdf` ＋ 逐語 `…/講義逐語/{科目}_重問逐語{NN}.txt`

---

## 3. TX 生成手順（v11.1.0 LOOP-CORE・二系統出力）

> **TX 1 問 = 2 ファイル**を必ず出す（片方だけは禁止）：
> - **公式**：`outputs/000_TX/{科目}/{接頭辞}{NNN}.html` ＝ 本物の5択（番号/組合せ番号を選ぶ）。Lexia は取り込まない。
> - **Lexia 用 `_lex`**：`outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html` ＝ ox-grid（記述単位○×）＋解法ナビ＋物語解説。
> - 本文・PART B/B+・参考条文判例・SVG は両者で共有。違いは **answer-area** と **_lex の解法ナビ／物語解説**のみ。

### Phase 1 — PDF 解析

PDF から抽出：問題番号・科目・年度・全記述（ア〜オ）原文・正解・**正答率**・テーマ・出題形式。
- **記述別の○×を必ず確定**（ア:○/× … オ:○/×）＝ox-grid の素。組合せ問題でも各記述の○×を一次データにする。
- 二系統用に2つを確定：① **公式の本物の正解**（独立5択なら正/誤の番号＝single、複数なら multi、組合せ・穴埋めは組合せ番号＋各選択肢の中身）。② **解法ナビの型**＝○×型（独立5択）か組合せ型（穴埋め・議論形式）。
- **冒頭応答必須**：`正答率 __% → パターン P_『___』 → パレット『___』` を最初に出力。
  - パターン：≥60%→P1（ピンク系）／40〜60%→P2（緑・青系）／<40%→P3（紫系）。

### Phase 2 — ファイル名2つを確定（§2）
公式 `outputs/000_TX/{科目}/{接頭辞}{NNN}.html`、Lexia 用 `outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html`。

### Phase 3 — clone と空化
```bash
cp canonical/GENESIS-CORE.html outputs/000_TX/{科目}/{接頭辞}{NNN}.html
```
コピー直後に**本文を空文字列で初期化**（PART A `.problem-text`/`.case-description`/ox-row の `.ox-stmt`/
`data-explanation`/final-answer 表、各 choice-section の本文、参考条文判例 `.basis-card-body`、SVG 内 `<text>`、
footer-spec 1〜3行目）。**GENESIS-CORE に PART C/D は無い**（別冊送り）。

### Phase 4 — section-by-section で執筆（各 Edit 30〜50KB）

- **4a HEAD `:root{}`**：V3 5色（`--accent`/`--mid`/`--soft`/`--light`/`--bg-dark`）＋派生だけ更新。
  **`--base` は固定クリーム `#F7F1E9` のまま変えない**。**`<style>` 末尾 §18〜§22（配色オーバーレイ・
  ナチュラルマイルド色・SVG配色）は触らない**（content-independent・clone で継承）。配色情報をヘッダー/フッター本文に書かない（G8）。
- **4b HEADER**：doc-header 問題番号／h1（出典・テーマ）／exam-meta（**正答率と難度のみ**）／toc-row。
- **4c PART A（ox-grid）**：A-1 `.problem-text` に問題文・記述ア〜オ原文を逐語。組合せ型は【見解】を `.case-description` に。
  - **単純5択型**では canonical（刑TX311＝組合せ型）由来の末尾2ブロック（「（参照条文）…」`blockquote.statute` と「【組合せ】…」見出し＋番号リスト）を**必ず削除**。参照条文は PDF 原文に印刷がある場合のみ残す（無ければ削除＝G27 WARNING）。
  - A-2 `.answer-area`：`data-answer-type="ox-grid"`／`data-correct-value="××○×○"`（記述ア〜オの○×連結）。5 `.ox-row`（`data-stmt="ア"…`）。各行 `.ox-main` は **`<p class="ox-gist">`（要点一行・記号フリー・30〜50字・○×をにじませない・`<b>`太字）＋ `<details class="ox-detail"><summary>全文</summary><span class="ox-stmt">…</span></details>`**。`<button class="reveal-answer-btn" disabled>解答を表示</button>` 必須。
  - **final-answer 表（G23）**：`<table class="statement-verdict-table" data-answer-key="ア:x,イ:x,ウ:o,エ:x,オ:o">` ＋各 `<tr data-stmt data-verdict>`。`.final-answer` は hidden。**answer-key・data-correct-value・○×表の三者一致**。
- **4d PART B（記述単位）**：各 choice-section（choice-1=記述ア…）。順序厳守：
  1. `.choice-header-block` の `.verdict`（✓○/✗× ＋ 法理とのズレ一文・**組合せ判定を書かない**）。
  1-bis.（学説/見解問題のみ）`.choice-premise`（🔎 この記述が前提とする見解を PART A 原文どおり再掲＝遡読防止）。
  2. `.sub-card.synthesis`：`.syn-orig`（📜 記述原文）→ `.syn-lead`（💡 THE GIST 一文）→ `.syn-path`（①②③ 噛み砕き）→ `.syn-image`（💭 INTUITION）。
  3. `.choice-points`（📌 POINT 2〜4点・主語は法概念）。**禁止：正解は肢N／組合せ判定／本記述は誤り・正しい／他記述参照（G22）**。
  4. `.sub-card.basis-link`（📚 BASIS アンカー）。
- **4d-bis PART B+**：`.cross-column` の3ブロック（`cb-cross` 🔗CROSS／`cb-compare` 📊比較／`cb-trap` ⚠️罠）。色は §20 継承・本文のみ。
- **4e 参考条文・判例（#basis）**：条文カード（文言＋`.kd-item`：保護法益/制度趣旨/要件）／判例カード（判旨は `.judgment-text`、判旨以外は `<div class="note">`）。完全プロファイルは書かない（別冊送り・G24）。
- **4f SVG（2枚のみ）**：体系ツリー（mindmap-tree）＋放射マップ（mindmap-radial）。座標・class は据置、テキストのみ差替。class は canonical 定義済みのみ（G16）。**フローチャートは core に置かない**。
- **4g footer-spec**：feature-tag 先頭＝`TX v11.1.0 LOOP-CORE`。配色情報を書かない。

### Phase 4h — 二系統に分離（順序厳守）

1. **_lex を先に切り出す**（ox-grid のまま複製）：
   ```bash
   cp outputs/000_TX/{科目}/{接頭辞}{NNN}.html outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html
   ```
   > これは**同一問題の自分自身の複製**なので template 流用禁止の例外（許可）。
2. **_lex に解法ナビを注入**：`canonical/SOLVE-NAV.html` を Read し3ブロックを移植。**エンジン JS は逐語コピー（編集禁止）**、問題固有データのデリミタ内だけ本問値。
   - `[STYLE]` → `<head>` の `</style>` 直前。
   - `[SHELL]` → answer-area の `<h3>【解答】…` 直前。
   - **型に応じ1つだけ** → `</body>` 直前：
     - 独立5択（○×型）→ `[SCRIPT-OX]`：`MODE`（`'correct'`/`'incorrect'`）＋ `STMT`（各記述 q/tip/note）。答えは ox-grid の `data-correct-value` から自動。
     - 組合せ・穴埋め・議論形式 → `[SCRIPT-COMBO]`：`COMBOS`/`OFFICIAL`/`ORDER`/`STEP`。
   - `tip`（💡コツ）は**決め手1点・1文40〜70字**。
   - footer-spec feature-tag に `lexia-oxgrid-solvenav` 追記。
   > **Type A（議論形式・空欄補充）**は ox-grid を空欄単位にし `[SCRIPT-A]` を使う。判別は `python scripts/tx-classify-format.py`。
   > 既存問の作り直しは `python scripts/tx-build-typeA.py <CODE> <DATA.json>`（物語解説内蔵＝この場合 4i 不要）。
3. **公式を de-grid**（本物の5択へ）：answer-area を `data-answer-type="single"`（多答は `"multi"`）／`data-correct-value="{本物の正解番号}"`。`.answer-ox-grid` を `.answer-row`（番号ボタン1〜5・GENESIS-CORE 既存構造）に置換。instruction を「記述1〜5のうち正しいものを1つ選び…」へ。**解法ナビは公式に入れない**。footer-spec に `official-5choice` 追記。
4. **整合**：_lex の `data-correct-value` の○の位置 ＝ 公式の正解番号（独立5択）。両ファイルの title・doc-header・footer の問題コードは同一。

### Phase 4i — 物語解説（_lex のみ・必須）

`_lex` の `.final-answer` 冒頭に**初学者向けの読み物**を入れる（公式には入れない）。
- **記号フリー**（①〜/(a)〜/「A説・B説」「甲乙説」「第N説」/記述記号ア〜オ への言及禁止）。見解は実体学説名、当事者は登場人物名、各記述は内容で指す。
- 問題の論理に沿って一本に（核心→各記述の正/誤理由→まとめ）。寄せ集め問題は偽の物語を捏造せず共通概念で束ねる。
- 形式：`{"title":"この問題を物語で読む ── <主題>","paras":["段落1",…]}`（**6〜9段落**・重要語 `<b>`・markdown禁止）。手本＝`outputs/ux/000_TX/001_刑法/刑TX311_lex.html` の `.fa-narrative`。
- 注入：JSON を一時ファイルに python で安全出力 → `python scripts/tx-inject-narrative.py {接頭辞}{NNN} <json>`（冪等）。素材抽出は `python scripts/tx-extract-source.py {接頭辞}{NNN}`。

### Phase 5 — SVG 重なり検査
体系ツリー＋放射マップの `<rect>`/`<ellipse>` の bounding box を全ペア AABB 衝突判定（衝突0・マージン16px以上）。衝突時は viewBox 拡張を最優先。

### Phase 6 — 検証（両ファイル）
```bash
python scripts/validate-tx-core.py outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html   # ox-grid 必須
python scripts/validate-tx-core.py outputs/000_TX/{科目}/{接頭辞}{NNN}.html          # 公式 single/multi 可
python scripts/check-duplicates.py outputs                                           # 公式↔_lex ミラーは除外＝正常
```
**G1〜G30 ERROR 0 件**まで修正→再検証。`grep -c 'fa-narrative-title' …_lex.html` が 1 以上であること（物語解説の存在確認）。

### Phase 7 — 永続化
```bash
python scripts/stamp-created-date.py        # 公式・_lex 双方に生成日時＋版を刻む（Lexia が読む・必須）
git add outputs/000_TX/{科目}/{接頭辞}{NNN}.html outputs/ux/000_TX/{科目}/{接頭辞}{NNN}_lex.html
git commit -m "feat({接頭辞}): {接頭辞}{NNN} を二系統生成（公式5択／Lexia用 ox-grid＋解法ナビ）"
git push -u origin <作業ブランチ>
```

---

## 4. JX 生成手順（v4.0.0 LOOP-FOLD＋副産物3種）

> **JX 1 問 = 本体 HTML ＋ 副産物3種（RX / TREE / ARIADNE）で 1 セット**。HTML だけで完結扱いにしない。
> Claude は副産物をサブエージェントで作るが、**Codex はサブエージェントを持たないので自分で順に生成する**
> （RX → TREE → ARIADNE）。下記 Phase 9 参照。

### Phase 0 — 入力アラインメント（必ず最初）
```bash
python scripts/check-jx-alignment.py {科目} {番号}
```
`[OK]` 以外（逐語欠落・keyword 不一致＝ズレ疑い）は**生成中断**。内容照合で正しい逐語を特定し
`inputs/001_JX/transcript-map.json` の `overrides` に追記してから再実行。
**重問PDFと講義逐語は番号がズレる系列がある**（刑28/29/30 は −7 ズレ）。同番号を無断前提にしない。

### Phase 1 — 準備
- 規律 `spec/jx-v3.2-master.md`＋構造 `spec/jx-v4.0.0-core.md` を参照。`canonical/ATHENA.html` は視覚参照可（**本文流用禁止**）。
- PDF 読解（事案・主要論点 通常2件・関連条文・関連判例）。**Phase 0 で解決した逐語を必ず併読**（論点・規範・あてはめの第一次情報源）。
- **照合ガード**：併読の冒頭で逐語の事案と PDF の事案が一致するか自己照合。不一致なら使わず中断・報告。

### Phase 2 — ファイル名（§2）→ clone → 空化
```bash
cp canonical/ATHENA.html outputs/001_JX/{科目}/{接頭辞}JX{NNN}.html
```
clone 直後に**本文を空文字列で初期化**（`.problem-text`／各部の解説・規範・あてはめ・結論／判例引用／`.lecturer-advice` 中身／採点講評／用語集／第5部各カード）。**ATHENA の本文を残さない**。

### Phase 3 — 配色（AI 自由選定）
全パレット（全15案＋派生）から問題の雰囲気で自由選定し5役割へ（`--base`70%/`--accent`25%/`--mid`5%/`--soft`/`--light`、文字は `--text`/`--bg-dark`）。pale bg + dark text・WCAG AA 4.5:1・5系統制限・semantic 緑`#438B48`/`#7BA980`・金`#ffd54f`/`#ffaa00` のみ越境可。科目固定色なし。**刑で ATHENA 配色のままでよければ流用可**。

### Phase 4〜7 — 構造を鋳造（v4 LOOP-FOLD・ATHENA 複製で骨格は継承）
- 11役割タイポ＋Google Fonts（TX GENESIS と完全一致）を維持。
- **exec-summary は作らない**。事案足場（事案概要・登場人物図・時系列・ファクト仕分け・`#issue-extraction`）は前半コアに残す（結論先出ししない）。
- **後半 deep（第4部体系化＋第5部）は `<details id="deep-dive">` で折りたたみ**（DOM は温存）。
- **模範答案＋採点講評は `<details class="reveal-answer">` で封じる**。
- **用語集5-5＋略語5-6 は deep の外**（`<section id="part5-ref">`）。
- 第3部 reveal 直前に **照合ナビ（`.collation-nav`）**、各 H 末尾に **口頭骨格（`.oral-skeleton`）**。
- v3.2 必須コンポーネント：`.key-box`（防御セレクタ三者結合・🔑KEY）／ラベルカード4種（💡NOTE/⚠WARN/✓TIP/✗NG）／`blockquote.statute`（薄グレー）・`blockquote.case`（薄ピンク）の色差別化／`.judgment-text`／`.para-num`／`.model-answer`／`.grading`。
- 逐語がある場合 **`.lecturer-advice`（🎓）を該当論点・部の冒頭**に（逐語のまま貼らず要点整理）。
- container `max-width:1320px`／doc-header `position:absolute` 右上／末尾スムーズスクロール JS／フッター励まし文言。

### Phase 8 — 検証
```bash
python scripts/validate-jx.py outputs/001_JX/{科目}/{接頭辞}JX{NNN}.html
```
**J1〜J20（＋v4 の JC/JD）ERROR 0 件**まで修正→再検証。

### Phase 9 — 副産物3種を生成（必須・Codex は自分で順に作る）

各副産物は **いま検証 PASS した JX HTML を一次情報源**に再構成（同一問題由来なので正当・他 JX 流用禁止）。
`{ID}`＝`{接頭辞}JX{NNN}`、`{00N_科目}`＝出力先サブフォルダ。各 headless プロンプトの全文を読んで従う。

| 副産物 | 起点 canonical | 手順書 | 出力先 | 検証 |
|---|---|---|---|---|
| **RX** 論証カード | `canonical/AXIOM.html` | `prompts/new-rx-headless.md` | `outputs/ux/002_RX/{00N_科目}/{ID}/{接頭辞}RX{NNN}_*.html`（1論点1枚） | `python scripts/validate-rx.py <DIR> {接頭辞}RX{NNN}` |
| **TREE** 樹形図 | `canonical/ARBOR.html`（**vendored**） | `prompts/new-arb-headless.md` | `outputs/ux/003_TREE/{00N_科目}/{ID}_TREE.html` | `python scripts/validate-tree.py <file>` |
| **ARIADNE** 解法ナビ | `canonical/ARIADNE.html` | `prompts/new-ariadne-headless.md` | `outputs/ux/001_ARIADNE/{00N_科目}/{ID}_ARIADNE.html` | `python scripts/validate-ariadne.py <file>` |

- **TREE は vendored モード**：外部 arbor リポジトリは無いので `canonical/ARBOR.html` の**構造シェルのみ**参照（本文・論点はコピーしない）。密度は約13分枝・葉57・問題15・約68KB に揃える。
- 各副産物も clone→空化→鋳造／`</body>` リテラル禁止／検証 ERROR 0 件まで修正。
- 3種を**そろえてから** push（HTML＋TTS だけの push にしない）。

### Phase 10 — 永続化
```bash
scripts/jx-push.sh "feat(jx): {ID} を生成保存（J1〜J20 PASS＋RX/TREE/ARIADNE）"
```
`jx-push.sh` は `outputs/001_JX` ＋ `outputs/ux` を stage し、生成日時スタンプ＋指数バックオフ再試行付きで push する。
PDF 削除（`jx-cleanup-pdf.sh`）はリモートでは Drive ガードが効かないので**実行しない**（ローカル PC 側に任せる）。

> **TTS 台本・音声は Codex の担当外**（音声は AI Studio で手動）。指示が無ければ作らない。

---

## 5. 絶対禁止事項（TX・JX 共通）

1. `outputs/*/` の**別問題** HTML を template に `cp`/`Read`/`Edit`（唯一の起点は canonical/。Phase 4h の自己複製は例外）。
2. canonical の本文・解説・判例引用を別問題に流用（content independence 違反）。
3. `<script>…</script>` 内に `</body>` リテラル（Lexia 全機能死亡）。
4. ファイル名・出力先の §2 違反（レガシー K/MIN/KEN 等の混在）。
5. **TX を公式だけ／`_lex` だけで完結**（必ず2ファイル）。`_lex` の ox-stmt を `①b②c…` の記号のみ肢にする（G30）。
6. **JX を HTML（＋TTS）だけで完結**し副産物3種を省く。
7. `python scripts/render.py` の実行（WIP 上書き）。
8. 1 メッセージで 50KB 超の Write/Edit。
9. ヘッダー/フッター本文に配色情報を書く（G8）。
10. 「保守的書き換え」（既存コードを引き継ごうとする癖）。

---

## 6. クイックリファレンス

```
# TX（公式＋_lex）検証
python scripts/validate-tx-core.py outputs/ux/000_TX/001_刑法/刑TX{NNN}_lex.html
python scripts/validate-tx-core.py outputs/000_TX/001_刑法/刑TX{NNN}.html
python scripts/check-duplicates.py outputs
python scripts/tx-classify-format.py            # Type A/B 判別
python scripts/tx-inject-narrative.py {ID} <json>   # 物語解説注入（_lex）

# JX 本体＋副産物 検証
python scripts/check-jx-alignment.py {科目} {番号}
python scripts/validate-jx.py outputs/001_JX/001_刑法/刑JX{NNN}.html
python scripts/validate-rx.py outputs/ux/002_RX/001_刑法/刑JX{NNN} 刑RX{NNN}
python scripts/validate-tree.py outputs/ux/003_TREE/001_刑法/刑JX{NNN}_TREE.html
python scripts/validate-ariadne.py outputs/ux/001_ARIADNE/001_刑法/刑JX{NNN}_ARIADNE.html

# 永続化
python scripts/stamp-created-date.py            # TX（手動 git commit 時）
scripts/jx-push.sh "feat(jx): …"                # JX（push まで一括）
```

| 役割 | TX | JX |
|---|---|---|
| 起点 canonical | `GENESIS-CORE.html`（＋`SOLVE-NAV.html`／別冊 `GENESIS-DEEP.html`） | `ATHENA.html`（＋`AXIOM`/`ARBOR`/`ARIADNE`） |
| 構造正典 spec | `spec/tx-v11.0.0-core.md`＋`spec/tx-v11.1.0-twotrack.md` | `spec/jx-v4.0.0-core.md`＋`spec/jx-v3.2-master.md` |
| 手順書 | `.claude/commands/new-tx.md` | `.claude/commands/new-jx.md` |
| 検証 | `validate-tx-core.py`（G1〜G30） | `validate-jx.py`（J1〜J20＋JC/JD） |

> 詳細・例外・最新方針は常に `CLAUDE.md` と `spec/` を正典とすること。本書はその運用ダイジェスト。
