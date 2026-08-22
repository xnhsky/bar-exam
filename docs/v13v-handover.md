# §v13v「📖 ものがたり」帯 ── 引き継ぎレシピ（TJR-S 特別枠）

> 2026-08-22 新設。正誤表の各記述に **物語解説の全体（その問題を貫く一本の物差し）＋当該記述の要約＋具体例**
> を置く層。外した肢で肢カードまで降りずに、正誤表の中で腑に落とすための面。
> 正典＝`canonical/GENESIS-CARD.html`（CSS 区画 `TX-VERDICT-STORY` ＋エンジン `appendStoryLine`）と
> `canonical/GENESIS-CARD.placeholder.html` の §v13v スロット契約。

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

## 2. 執筆の型（gold＝刑訴TX066-075）

1. **1文目＝物差し**：その問題を貫く軸を出す（物語解説の「導入」「まとめ」から取る。物語解説が無ければ
   全記述の切断点・転用から自分で立てる）。
2. **2〜3文目＝当該記述の位置づけ**：その物差しのどこに当たるか＝結論と理由。条文・判例は**そのファイル内に
   書かれているものだけ**（新しい引用を発明しない）。
3. **具体例**：規範が動く場面を1つ（甲・乙）。抽象論の言い換えにせず、「〜な場面。だから〜になる」で結論まで。
4. **禁止**：他記述への参照（記述N・肢N）、「本問」、問題ローカルの見解ラベル（見解Ⅰ・A説）。
   見解は実体の学説名で書く（罪数標準説／同時処理可能性説／可罰的行為標準説 など）。

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
```

- 科目の優先順は **民法 → 刑法**（2026-08-22 ユーザー指示）。刑訴はセッション側で消化中のため
  自動充当から外している（`-Subject 刑訴` で明示指定は可能）。
- 1バッチ **10本**（`-MaxS`）。ランナーが `validate-tx-core`＋`check-tx-lex-engine` を再検証し
  **PASS のみ 1問ずつ commit/push**（FAIL はロールバック・同一問題2回失敗で ESCALATE →
  `logs/tjr-repair-report.md`）。
- 土台が無いファイル（刑法など未伝播）は、ランナーが実行前に `tx-lex-verdict-redesign.py` で注入する。
- 二台同時実行は claim（`{問題ID}_v13v`）＋リモート執筆済み検知で回避。
- **残件ゼロ＝「該当なし」SKIP が正常**（過渡ストリーム＝完遂で自然消滅）。

## 5. 進捗（2026-08-22 時点）

| 範囲 | 土台（CSS＋エンジン） | ものがたり本文 |
|---|---|---|
| 刑訴TX065-075 | 済 | **済**（gold・11本） |
| 刑訴TX076 以降（〜334 の帯） | 済 | セッションで順次執筆中 |
| 民法（97本） | 済 | TJR-S が10本/バッチで消化 |
| 刑法 | 未（S ランナーが個別注入） | TJR-S が民法の次に消化 |
| 刑訴TX001-064 | 未 | 未（優先度低・必要になれば S に `-Subject 刑訴` で流す） |
