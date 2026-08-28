# §v13v「📖 ものがたり」帯 ── 引き継ぎレシピ（TJR-S 特別枠）

> 2026-08-22 新設／**2026-08-28 改定（体系・趣旨・実務型）**。正誤表の各記述に、その論点の
> **体系的位置づけ・条文の趣旨・考え方のコツ・実務での動き方＋具体例** を置く層。外した肢で肢カードまで
> 降りずに、正誤表の中で腑に落とすための面。正典＝`canonical/GENESIS-CARD.html`（CSS 区画
> `TX-VERDICT-STORY` ＋エンジン `appendStoryLine`）と `canonical/GENESIS-CARD.placeholder.html` の
> §v13v スロット契約。

## 1. 何を作るか

正誤表（`.statement-verdict-table`）の各行のコア列を **原文（＋✍答案圧縮）／ものがたり／切断点／転用** の
帯に点線罫で区切り、原文帯の直後に「📖 ものがたり」帯を挟む。中身は行の属性 `data-brief-story`（単一情報源）：

```
<tr data-stmt="1" data-verdict="o" data-brief-story="…要約 2〜3文…<span class='tx-vb-ex'><span class='tx-vb-ex-tag'>たとえば</span>…具体例…</span>" data-brief-mark="…">
```

- 本文の書体・太さは記述カードの **THE GIST と同じ**（`--font-answer`/500・強調は `--font-note`/700）。
- ラベルは ✍答案圧縮と同じ **食み出しタブ＋本文1字下げ**。
- 属性値なので **半角二重引用符は使えない**（鉤括弧「」を使う）。
- `data-brief-story` が無い行では帯そのものが出ない＝**土台だけ入っていても表示は壊れない**。

## 2. 執筆の型（gold＝刑訴TX073-075・2026-08-28 改定）

**旧型（2026-08-22〜08-27 執筆分）は「その肢がどういう着眼点で作られているか」＝出題構造の解説**に
寄っていた（「『のみ』という限定語を見たら列挙と照合する」「向きが逆になっていないか確かめる」
「この問題は五つを並べる」）。ユーザー指摘（2026-08-28）により、**解答技術は切断点／転用帯の領分**とし、
ものがたり帯は次の 4 層＋具体例で書く。

1. **体系的位置づけ** — その論点が科目の体系のどこに座るか（制度の目的、対になる制度、三類型のどれか）。
2. **趣旨** — 条文・制度がなぜそう作られているか（守ろうとする利益、危険、価値判断）。
3. **考え方のコツ** — 専門用語を使い、直後に生活語で開く（用語サンドイッチ）。要件（あるか無いか）と
   裁量（どの程度か）の別、条文の語尾（必要的／裁量的）、対になる規定の読み合わせ など。
4. **実務での動き方** — 誰がいつ何をするか、運用上の勝負どころ、実務・立法上の批判や最新改正。
   断定できない運用は「〜こともある」「〜が通常」と幅を持たせる（作り話をしない）。
5. **具体例** — 規範が動く場面を1つ（甲・乙）。抽象論の言い換えにせず「〜な場面。だから〜になる」で結論まで。

- 分量の目安：story 4〜6文・250〜400字／example 1〜3文・60〜140字。強調 `<b>` は 2〜4 か所。
- **判例の新規引用は禁止**（ファイル内に書かれたものだけ・年月日も表記のまま）。条文は六法で確認できる
  基本条文なら周辺条文を新たに挙げてよい（番号・項を必ず確認する）。
- **禁止**：出題構造・解答技術の解説、他記述への参照（記述N・肢N）、「本問」、問題ローカルの見解ラベル
  （見解Ⅰ・A説）。見解は実体の学説名で書く（罪数標準説／同時処理可能性説 など）。
- 属性値なので半角二重引用符は使えない（鉤括弧「」を使う）。

## 3. 手作業でやるとき

```bash
python -X utf8 scripts/tx-lex-verdict-redesign.py <file>   # 土台（CSS＋エンジン）※未伝播ファイルのみ
python -X utf8 scripts/v13v-extract.py <file>              # 素材（物語・各記述の原文・切断点・転用）
#  → payload.json を書く: {"stmts":[{"n":"1","story":"…","example":"…"}, …]}
python -X utf8 scripts/v13v-inject.py <file> payload.json  # 決定論注入（冪等・--force で上書き）
python -X utf8 scripts/validate-tx-core.py <file>          # ERROR 0
python -X utf8 scripts/check-tx-lex-engine.py <file>       # PASS
```

## 4. TJR-S（自動消化）

```bash
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -Only S             # 10本だけ（民法優先）
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -Only S -MaxS 20    # 件数変更
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -SkipS              # 通常TJRから S を外す
pwsh -NoProfile -File scripts\v13v-runner.ps1 -Subject 刑法 -DryRun # 科目を指定して対象確認
pwsh -NoProfile -File scripts\v13v-runner.ps1 -Rewrite -DryRun     # 旧型（出題構造型）の残件を確認
pwsh -NoProfile -File scripts\v13v-runner.ps1 -Rewrite -MaxProblems 10 # 旧型を新型へ書き直す（inject は --force）
```

- 科目の優先順は **民法 → 刑法**（2026-08-22 ユーザー指示）。刑訴はセッション側で消化中のため
  自動充当から外している（`-Subject 刑訴` で明示指定は可能）。
- 1バッチ **10本**（`-MaxS`）。ランナーが `validate-tx-core`＋`check-tx-lex-engine` を再検証し
  **PASS のみ 1問ずつ commit/push**（FAIL はロールバック・同一問題2回失敗で ESCALATE →
  `logs/tjr-repair-report.md`）。
- 土台が無いファイル（刑法など未伝播）は、ランナーが実行前に `tx-lex-verdict-redesign.py` で注入する。
- 二台同時実行は claim（`{問題ID}_v13v`）＋リモート執筆済み検知で回避。
- **残件ゼロ＝「該当なし」SKIP が正常**（過渡ストリーム＝完遂で自然消滅）。

## 5. 進捗（2026-08-28 時点）

| 範囲 | 土台（CSS＋エンジン） | ものがたり本文 |
|---|---|---|
| 刑訴TX073-075 | 済 | **済（新型・gold）** |
| 刑訴TX076-100 | 済 | **済（新型・2026-08-28）** |
| 刑訴TX065-072 | 済 | 旧型で執筆済み → 新型への書き直しは **TJR 付随**で消化 |
| 刑訴TX101 以降（〜334 の帯） | 済 | 旧型または未執筆 → **TJR 付随**で消化 |
| 民法（97本） | 済 | TJR-S が10本/バッチで消化（新型プロンプトを適用） |
| 刑法 | 未（S ランナーが個別注入） | TJR-S が民法の次に消化 |
| 刑訴TX001-064 | 未 | 未（`-Subject 刑訴` で流す） |

> **旧型ファイルの扱い（2026-08-28 ユーザー指示）**：旧型（出題構造型）で執筆済みの行も、TJR-S が
> `--force` で新型へ上書きする。既に `data-brief-story` があるファイルはランナー既定ではスキップされるため、
> 旧型の書き直しでは inject を `--force` で呼ぶこと。
