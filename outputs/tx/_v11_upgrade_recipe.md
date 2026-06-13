# TX v10 GOLD → v11 LOOP-CORE 「中身保存・構造のみ更新」アップグレード recipe

対象：`outputs/tx/刑TX/刑TX{NNN}.html`（既存 v10.0.0 GOLD-SKELETON）を **その場で（同ファイルを上書き編集）** v11.0.0 LOOP-CORE へ。
基準合格：`python scripts/validate-tx-core.py <file>` が **ERROR 0**。

## 大原則（厳守）
1. **中身（問題文・記述ア〜オ・正誤・正答率・解説・条文・判例の法理）は既存ファイルから100%保存**。再OCR・PDF参照・他ファイル参照は一切しない。**法理や答えを新たに導出しない**＝既存を再構成するだけ。
2. 捨てるのは「ガワ＝廃止構造」だけ：PART C・PART D（12問 arena/drill）・flow-svg・判例の完全プロファイルラベル・組合せ導出ナラティブ。
3. 1メッセージ50KB超のEdit禁止。section単位で編集。

## 手順（この順で）

### S1. PART A を ox-grid ○× 化＋機械可読 answer-key 新設
- 既存 `.answer-area` の各記述の **正誤（○=正しい記述／×=誤り記述）を、既存の data-explanation・choice の verdict(✓/✗)・choice-summary「記述Xは正しい/誤り」から確定**（複数ソースが一致するか自己照合。1=正→○、2=誤→×）。
- `<div class="answer-area" ...>` 開始タグ：
  - `data-correct-value` を **○×連結**（記述ア〜オ順。例 ○××××）に。長さ=記述数。
  - `data-answer-type="ox-grid"` を維持/設定。
  - `data-explanation` 先頭の「正解はア=1…」等の**正解値リテラルを削除**（AP-37）。法理の説明本文は保存。
- `<h3>` → `各記述の正誤を ○×で判定`。
- `.answer-instruction` → `記述ア〜オそれぞれに ○（正しい）／×（誤り）を付けてから「解答を表示」を押してください（導き書§3-1：必ず5記述全部に○×を付けてから reveal）。`
- 各 `.ox-row`：`<div class="ox-row" data-stmt="ア">` のように **data-stmt 付与**。ボタンを
  `<button class="ox-btn" type="button" data-value="○">○</button><button class="ox-btn" type="button" data-value="×">×</button>` に（旧 `1 正`/`2 誤` を置換）。`.ox-stmt` 要約は保存。
- reveal ボタン文言を `解答を表示` に。
- **`.answer-area` 内に G23 記述○×一覧表を新設**（reveal ボタン＋answer-feedback の直後・`</div>` 直前）：
```
      <div class="final-answer" hidden="">
        <p class="fa-summary"><strong>正解</strong>　各記述の○×は下表のとおり。組合せ番号を覚えるのではなく、各記述に現れた<strong>法理</strong>で正誤を判定する。下表「論点のコア」が学習資産。</p>
        <table class="statement-verdict-table" data-answer-key="ア:o,イ:x,ウ:x,エ:x,オ:x">
          <thead><tr><th style="width:3em;">記述</th><th style="width:3.5em;">正誤</th><th>登場した論点のコア（転用可能な法理）</th></tr></thead>
          <tbody>
            <tr data-stmt="ア" data-verdict="o"><td style="text-align:center;font-weight:700;">ア</td><td style="text-align:center;font-weight:800;color:var(--recall-correct-light);">○</td><td>{記述アの論点コア＝既存解説の要点1文}</td></tr>
            ...（イ〜オ。×は data-verdict="x"・記号×・color:var(--recall-incorrect)）
          </tbody>
        </table>
      </div>
```
  - **data-answer-key の o/x は data-correct-value の○×と完全一致**（o=○正, x=×誤）。論点コアは既存 choice-summary/解説/choice-points から1文に要約（新たな法理を作らない）。
- 組合せ型（「正しい記述の組合せはどれか」+選択肢1〜5）の場合：fa-summary に正解の組合せ番号を `<span class="answer-num">N</span>` で入れてよい。独立正誤型（各記述に1/2を付す）の場合は番号不要。**記述ごとの○×が一次データ**である点は共通。
- 体系ツリー/放射SVG内に「正解：ア=1 イ=2…」等の旧1/2表記があれば ○× に置換。

### S2. PART C・PART D・flow-svg を削除（G9・G26）
- 放射マップ section の `</section>` 直後（PART C 見出しコメント/`<div class="part-title">PART C`）から、footer 直前（`<!-- …footer-spec…`）までを丸ごと削除。
- 確認：`class="flow-svg"`・`id="part-d"`・`recall-arena`/`drill-block` が **要素として** 0（CSS定義の残存は無害）。`id="c-` も 0。
- #basis・#mindmap-tree・#mindmap-radial は**残す**（G4）。

### S3. choice-points 浄化（G22）
- 各 `.choice-points` 内の `本記述は正しい/誤り`・`記述[アイウエオ]は…`・`（正/誤＝N）`・`正解は肢` を**除去**。
- 「結論：…記述Xは正しい/誤り」型の項目は、**法概念主語の論点コア or ひっかけの型**に書き換え（中身の法理は保存）。

### S4. 参考条文・判例の濃淡化（G24）
- 判例カードの `<strong>【事案】`・`<strong>【判旨】`・`<strong>【補足】`・`<strong>【審級経過】` ラベルを**除去**し、**判旨核心＋射程**の流し込み段落＋短い本問適用へ濃縮。判旨の核心引用は保存。
- 条文カードは **保護法益・制度趣旨が note 等に既にあれば温存**（無ければ既存解説から1文補う）。要件効果の網羅一覧は作らない。

### S5. footer feature-tag を v11 化（G15）
- `footer-meta-hidden` の feature-tag を：
```
      <span class="feature-tag" hidden="">TX v11.0.0 LOOP-CORE</span>
      <span class="feature-tag" hidden="">genesis-core-baseline</span>
      <span class="feature-tag" hidden="">part-b-statement-unit</span>
      <span class="feature-tag" hidden="">oxgrid-statement-answer-key</span>
      <span class="feature-tag" hidden="">refs-hogo-eki-shushi</span>
      <span class="feature-tag" hidden="">mindmap-tree-and-radial</span>
      <span class="feature-tag" hidden="">deep-volume-separated</span>
      <span class="feature-tag" hidden="">palette-v3-11-named</span>
      <span class="feature-tag" hidden="">palette: {既存のパレット名} (P{N})</span>
      <span class="feature-tag" hidden="">svg-overlap-checked</span>
      <span class="feature-tag" hidden="">content-independence</span>
      <span class="feature-tag" hidden="">jp-prefix-naming</span>
```
  先頭は必ず `TX v11.0.0 LOOP-CORE`。footer-date に `v11 LOOP-CORE 改訂：2026-06-13` と `深掘り別冊：刑TX{NNN}-deep.html（未生成）` を併記してよい。

### S6. 教授ブロックを①②のみに＋choice-points 前倒し（真コア化・必須）
- v11 コアの professor は **①ポイント・②考え方の道筋のみ**。③イメージ・④あてはめ・key-phrase-box・
  prof-analogy・warning・cross-link は別冊 D-1 送り＝**コアから削除**。
- PART B のブロック順は **ヘッダー→choice-points（論点コア前倒し）→記述原文→解説→根拠リンク→教授①②**。
- ox-grid 化（S1〜S5）の後、**`python scripts/tx-v11-coreify.py <file...>`**（決定的・冪等）で一括適用すると
  教授③④等の削除＋choice-points 前倒しが行われ「真コア」になる。**validator は professor 数・ブロック順序を
  検査しない**ため、これを省くと validate は通るが真コアにならない（刑TX326-445 で実証・第1パスで漏らした）。
- 削除した③④等の中身は git 履歴に残る（必要時 /deepen-tx で別冊 -deep.html へ）。

### S7. 検証
- `python scripts/validate-tx-core.py outputs/tx/刑TX/刑TX{NNN}.html` → **ERROR 0** まで修正。WARNING は許容。

## 返却（必須・人手スポットチェック用）
- 問題ID・出題テーマ・**確定した○×（記述別、根拠にした既存ソース行）**・組合せ型/独立正誤型の別・validate 結果（PASS/残ERROR）・主要な変更点。
