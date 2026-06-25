# TX 二系統化 仕様（v11.1.0 TWO-TRACK・正典）

> 2026-06-24 確定。TX 1 問を **公式（本物の5択）** と **Lexia 用 `_lex`（ox-grid＋解法ナビ）** の
> 2 ファイルで出力する。基盤は v11.1.0 LOOP-CORE（`spec/tx-v11.0.0-core.md` ＋ `canonical/GENESIS-CORE.html`）。
> 本書はその**差分仕様**であり、構造・配色・PART 規律は v11.1.0 を継承する。

---

## 第0項. なぜ二系統か

- **公式**は過去問そのままの**本物の5択**（番号を選ぶ・組合せ番号を選ぶ）＝出題形式の忠実再現。
- **Lexia 用 `_lex`**は過去問を**記述（肢）単位の○×**へ分解した ox-grid ＋**解法ナビ**（議論形式・穴埋めの
  誘導 UI）。Lexia の Active Recall／復習プール／弱点克服帳は**記述単位**で回るため、組合せ番号の暗記に
  なる公式形では学習資産にならない。よって Lexia には `_lex` だけを取り込む。
- 両者は**同一問題の 2 表示版（ミラー）**。本文・解説・SVG を共有し、`answer-area` と解法ナビだけが異なる。

---

## 第1項. 出力（2ファイル・命名）

| 系統 | パス | answer-area | 解法ナビ | Lexia 取込 |
|---|---|---|---|---|
| **公式** | `outputs/000_TX/{00N_科目}/{接頭辞}{NNN}.html` | `single`／`multi`（本物の5択） | なし | **しない**（_lex 在るとき除外） |
| **Lexia 用** | `outputs/ux/000_TX/{00N_科目}/{接頭辞}{NNN}_lex.html` | `ox-grid`（記述単位○×） | あり（常時表示） | **する** |

- 接頭辞・科目フォルダは §2（CLAUDE.md）と同一（刑TX→001_刑法 など）。
- `_lex` は**末尾 `_lex`** で公式と区別（`刑TX350.html` ↔ `刑TX350_lex.html`）。`txCodeFromPath`（Lexia）・
  `validate-tx-core` G14・`check-duplicates` はいずれも `_lex` を正規化して同一コードとして扱う。

---

## 第2項. 共有と差分（何を共有し、何だけ差し替えるか）

**共有（公式＝_lex で同一）：** `<title>`／doc-header／exam-meta／PART A 問題文・記述原文・`.case-description`／
PART B 各記述カード・PART B+ コラム／参考条文判例（#basis）／SVG（体系ツリー・放射マップ）／footer 本体。

**差分（ここだけ差し替える）：**
1. **answer-area**：公式＝番号5択（`.answer-row`）／_lex＝記述単位○×（`.answer-ox-grid`）。
2. **解法ナビ**：_lex のみ（`canonical/SOLVE-NAV.html` から注入）。公式には入れない。
3. **final-answer（○×一覧表）**：_lex は必須（Lexia 肢キー源）。公式は任意（real-exam では省略可）。
4. **footer feature-tag**：公式＝`official-5choice`／_lex＝`lexia-oxgrid-solvenav` を追記。

---

## 第3項. 公式の answer-area（real-exam 5択）

`GENESIS-CORE.html` 既存の構造・CSS・reveal JS（`data-answer-type` を single/multi/ox-grid で分岐）をそのまま使う。

```html
<div class="answer-area" id="answer-area" data-correct-value="3" data-answer-type="single"
     data-explanation="〔本問の総合解説。各記述の○×と理由（条文・判例・規範のコア）〕">
  <p class="answer-instruction">記述1〜5のうち正しいものを1つ選び、「解答を表示」を押してください。</p>
  <div class="answer-row">
    <button class="answer-slot" type="button" data-value="1">1</button>
    …（2〜5）…
  </div>
  <button class="reveal-answer-btn" type="button" disabled>解答を表示</button>
  <div id="answer-feedback" hidden></div>
  <!-- final-answer は任意 -->
</div>
```

- **独立5択**（「正しい/誤っているものを1つ選べ」）：`single`・`data-correct-value="{番号}"`。
- **多答**（「正しいものをすべて」等）：`multi`・`data-correct-value="2,4"`・selection-counter は GENESIS-CORE 継承。
- **組合せ・穴埋め・議論形式**：`single` で**組合せ番号**を選ばせる。answer-area の上に【組合せ】見出し＋
  「1 ①a ②d ③f …／2 …」を `.problem-text`（`.choice-num-inline`）で併記し、instruction は
  「①〜⑤に入る語句の正しい組合せを 1〜5 から1つ選び…」。

---

## 第4項. `_lex` の answer-area（ox-grid）＋解法ナビ

### 4-1. ox-grid（GENESIS-CORE native のまま）

`data-answer-type="ox-grid"`・`data-correct-value="××○××"`（各記述の○×連結）・5 `.ox-row`
（`data-stmt`＋`.ox-stmt`＋○/× ボタン）＋ `reveal-answer-btn` ＋ `.final-answer` の
`<table class="statement-verdict-table" data-answer-key="1:x,2:x,3:o,4:x,5:x">`。
**answer-key・data-correct-value・○×一覧表の三者一致**（G29）。

> **組合せ・穴埋めの ox-stmt（最重要・G30）**：組合せ番号ではなく**各空欄ごとの実質命題**にする
> （例「公共の危険の内容＝b（限定せず…）が正しい」）。「①b②c…」の記号のみ肢は Lexia 復習プールから
> 除外されるため**禁止**（`validate-tx-core` G30 が検出）。

### 4-2. 解法ナビ注入（`canonical/SOLVE-NAV.html`）

`SOLVE-NAV.html` の 3 ブロックを `_lex` へ移植する。**エンジン JS は逐語コピー（編集禁止）**、問題固有データの
デリミタ内だけを本問値にする。`document.body.classList.add('snav-on')` で常時表示。ナビの「確定」は裏で
ox-grid の○×ボタンを click して採点（**記録は ox-grid 一本**＝Lexia 記録の単一情報源）。

- `[STYLE]` → `<head>` の `</style>` 直前。
- `[SHELL]`（`<div class="solve-nav" id="solve-nav">…</div>`）→ answer-area の `<h3>【解答】…` 直前。
- `[SCRIPT-OX]` か `[SCRIPT-COMBO]` を1つだけ → `</body>` 直前。

**型の選び方：**

| 問題型 | SCRIPT | 埋めるデータ | 答えの出所 |
|---|---|---|---|
| 独立5択（正しい/誤りを1つ） | `[SCRIPT-OX]` | `MODE`（correct/incorrect）・`STMT`（各記述 q/tip/note）・`ORDER`（既定1..5） | ox-grid の `data-correct-value` から自動 |
| 組合せ・穴埋め・議論形式 | `[SCRIPT-COMBO]` | `COMBOS`（番号→各空欄キー）・`OFFICIAL`（各空欄の正解キー）・`ORDER`（検討順）・`STEP`（q/loc/tip/opts/note） | `OFFICIAL` に一致する組合せ |

### 4-3. 解法ナビ sn-sub のネタバレ禁止（2026-06-25 確定・G32）

**`sn-sub`（解法ナビの常時表示ヘッダー）に、学生が一問一答で○×判定して自力導出すべき
「各話者・各説の到達結論」を断定形で書いてはならない。** 書くと組合せ問題の正答が一読で割れる。

- **実害**：刑TX351_lex の sn-sub が「学生Bは限定説・判例反対、学生Aは認識不要説、という立場の
  一貫性が鍵です」と結論を断定し、正答（○××××＝組合せ1）が解く前に判明した（是正 commit 389df14）。
- **許容**：手順説明＋「各話者の立場が最後まで一貫しているかが鍵」型の**中立メタヒント**のみ
  （正典 `canonical/SOLVE-NAV.html` の sn-sub＝手順説明が基準）。
- **結論を確定させる誘導は STEP の💡コツ（`tip`）側**で段階的かつ疑問形で行う（「Bは限定説か
  非限定説か」「賛否はどちらか」「…を確かめる」）。tip は progressive nav なので結論再掲・断定も可。
- **機械検出**：`validate-tx-core.py` **G32**（WARNING）。sn-sub を節分割し「は／＝で主語に到達結論
  キーワード（限定説・不要説・判例反対 等）を結びつけ かつ 疑問・検討マーカーを欠く」節を検出する。

---

## 第5項. 検証（validate-tx-core.py の二系統対応）

`python scripts/validate-tx-core.py <file>` を**両ファイル**に対して実行（G1〜G30 ERROR 0 件）。
パス（`_lex` 接尾辞）で公式／Lexia 用を判定し、ox-grid 固有検査を出し分ける：

- **G25（PART A ox-grid）**：`_lex` は ox-grid 必須。**公式は `single`/`multi` を許容**（ox-grid 固有検査をスキップ）。
- **G23（○×一覧表 data-answer-key）**：`_lex` は必須。**公式 single/multi は対象外**（任意）。
- **G29（答え整合）**：ox-grid のときのみ（公式 single/multi は自動スキップ）。
- **G30（記号のみ肢の禁止）**：ox-grid（=_lex）で `①b②c…` の記号のみ ox-stmt を検出 ERROR。
- **G32（解法ナビ sn-sub のネタバレ）**：`sn-sub` が各話者の到達結論を断定的に先出しした場合 WARNING（第4-3項）。
- **G14（命名）**：`_lex` を正規化してコード×フォルダ整合を判定。

`python scripts/check-duplicates.py outputs` も push 前に通す。公式↔_lex は**同一 title のミラー**として
DUP-TITLE から除外（`is_official_lexia_mirror`）＝**重複ではない**。他問からのコピペ等のみ検出する。

---

## 第6項. Lexia 連携

`src/lib/barExamSync.js`（lexia repo）：

- `txCodeFromPath(path)`：`刑TX350.html` と `刑TX350_lex.html` を同じ `刑TX350` に正規化（ミラー判定キー）。
- `filterLexiaImportable(entries)`（`fetchBarExamManifest` に内蔵）：
  - `outputs/ux/000_TX/..._lex.html`（Lexia 用）→ **取り込む**。
  - `outputs/000_TX/...html`（公式）で**対応する `_lex` が在るもの**→ **除外**（5択混入・二重を防止）。
  - `_lex` が**まだ無い**公式 TX → **従来どおり `000_TX` から取り込む**（全展開の移行期は混在で安全）。
  - JX / RX / TREE / ARIADNE / references → 従来どおり。

---

## 第7項. 全展開（既存問の _lex 化）

- **新規生成**は `new-tx`（`/new-tx`・TX-MARCH・TX-PICK・RB）が Phase 4h で**最初から2ファイル**を出す。
- **既存 362 問（刑法）の _lex 化（全展開）はローカルPCのバッチで回す**（PDF・Drive・PowerShell 依存）。
  移行期は `filterLexiaImportable` が「_lex 在る問だけ公式を除外」するので、**部分的に _lex 化しても
  既存ライブラリは壊れない**（_lex 未生成の問は公式のまま取り込まれる）。

---

## 第8項. 基準ペア（worked examples）

- **組合せ型**：`刑TX350`（公共の危険・議論形式の穴埋め組合せ）。公式＝組合せ番号 single、`_lex`＝ox-grid＋`[SCRIPT-COMBO]`。
- **○×型**：`刑TX001`（応報刑論・独立5択「正しいものを1つ」）。公式＝single、`_lex`＝ox-grid＋`[SCRIPT-OX]`。
- 拡大パイロット：`刑TX010/055/056/057`（いずれも独立5択＝○×型）。

> パイロット 6 問は本仕様の実証例。**新規・全展開とも本書と `canonical/SOLVE-NAV.html` を正典**とし、
> 既存 outputs を template 流用しない（§7 の物理的禁止）。
