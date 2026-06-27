# G32 記号フリー化 ── 再開用タスク＆指示文（2026-06-27 時点）

> 復習プール GIST/POINT の記号フリー化（validate-tx-core.py **G32**）の続き。
> 関連の他バックログ（ERROR化・意味ラベル A 展開・FA_LABEL_SEED 撤去）は
> `docs/deferred-safeguards.md` が正典。本書は G32 残作業の即再開用。

---

## 1. 現状（このセッション終了時）

- **G32 残：93 / 362問**（前倒し開始 151 → 58問解消・すべて push 済み）。
- 中断理由：8並列エージェントがサーバ側レート制限（混雑制限・自分の上限ではない）に触れ多くが失敗。
  → **次回は 2〜3 エージェントずつ**に絞る。
- 完了分・部分修正分はすべて commit/push 済み・ERROR 0。

## 2. 再開手順

### 2-1. まず残リストを再生成（コードは下記より新しい方を信頼）

```bash
cd bar-exam
python - <<'PY'
import importlib.util, glob, re
spec=importlib.util.spec_from_file_location('v','scripts/validate-tx-core.py')
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
files=sorted(glob.glob('outputs/ux/000_TX/001_刑法/*_lex.html'),key=lambda f:int(re.search(r'\d+',f.split('/')[-1]).group()))
rem=[]
for f in files:
    code=re.search(r'(刑TX\d+)_lex',f).group(1)
    val=v.Validator(f); val.run()
    g=[m for c,m in val.warnings if c=='G32']
    if g:
        n=re.search(r'(\d+) 件',g[0]); rem.append((code,int(n.group(1)) if n else 1))
print(len(rem)); print(" ".join(c for c,_ in rem))
PY
```

### 2-2. 残コード（93問・番号順・2026-06-27 スナップショット）

```
刑TX010 刑TX057 刑TX058 刑TX059 刑TX060 刑TX065 刑TX069 刑TX076 刑TX084 刑TX089
刑TX090 刑TX091 刑TX092 刑TX094 刑TX098 刑TX103 刑TX104 刑TX105 刑TX114 刑TX117
刑TX118 刑TX119 刑TX120 刑TX121 刑TX122 刑TX130 刑TX133 刑TX134 刑TX135 刑TX139
刑TX141 刑TX142 刑TX143 刑TX144 刑TX145 刑TX146 刑TX149 刑TX156 刑TX169 刑TX172
刑TX174 刑TX184 刑TX191 刑TX203 刑TX211 刑TX212 刑TX217 刑TX218 刑TX220 刑TX228
刑TX233 刑TX234 刑TX256 刑TX257 刑TX262 刑TX263 刑TX267 刑TX269 刑TX270 刑TX273
刑TX275 刑TX283 刑TX288 刑TX289 刑TX310 刑TX329 刑TX330 刑TX331 刑TX333 刑TX334
刑TX338 刑TX344 刑TX348 刑TX349 刑TX351 刑TX352 刑TX365 刑TX368 刑TX371 刑TX381
刑TX402 刑TX403 刑TX415 刑TX416 刑TX418 刑TX419 刑TX421 刑TX428 刑TX430 刑TX442
刑TX443 刑TX444 刑TX445
```

- **重い問（20件級・組合せGIST全面）**：058,118,174,351,381,418（各20件）／065,089,119,121,415（各19件）。
  これらは1問1エージェント推奨（他は2〜4問/エージェント）。**gold 刑TX351** は要注意（既出の手本問）。

## 3. 作業の型（確立済み・厳守）

- **編集対象は `.syn-lead`（THE GIST）と `.choice-points` 内 `<li>`（POINT）の本文だけ**。
  `.problem-text`/`.case-description`/`.ox-stmt`/`data-answer-key`/`data-correct-value`/SVG/解法ナビ/`.fa-narrative` は触らない。
- **記号→実体の置換のみ・法的意味は不変**：
  - 空欄①②③/選択肢(a)(b)＝その記号が指す**学説・概念の実体名**へ（例「学生B＝限定説（①a）＋認識必要説（⑥l）」→「学生B＝限定説と認識必要説の組合せ」）。復元不能な空欄は記号を外し意味の通る一般表現に。
  - A説/B説/甲乙説/第N説＝本文・ox-stmt から**実際の学説名**を復元して置換。
  - 記述ア/肢N参照＝参照を消し記述の**内容**で自己完結。
  - 学生A等の話者ラベル＝指す**見解の実体名**へ（座談会型で本文に3つ以上ある話者は G32 が自動除外）。
- **注意**：`<a>`/`<strong>` が文中に挟まり Edit の一意マッチが外れる→生HTMLを grep し `</a>` 以降など実在部分文字列で置換。
- **ゲート**：各ファイルで `python scripts/validate-tx-core.py <file>` → `[G32]` 消失・`ALL ... PASS`・新規 ERROR なしを確認。
- 既存の G27（PART A 参照条文）警告は別領域・対象外（残ってよい）。

## 4. エージェント起動の指示文（コピペ用・1バッチ分）

> レート制限回避のため **同時 2〜3 エージェント**まで。1エージェントの担当は 2〜4 問（重い20件問は1問）。
> 下記の `{対象コード列}` を差し替えて使う。

```
bar-exam（/home/user/bar-exam）で TX _lex の「復習プール記号フリー化（G32）」を行う。対象：{対象コード列}
各ファイル outputs/ux/000_TX/001_刑法/{コード}_lex.html。

目的：Lexia 復習プールは肢キーカードに PART B の THE GIST(.syn-lead)と POINT(.choice-points 内 li)を
併載する。そこに問題ローカル記号が残ると記号暗記になる。scripts/validate-tx-core.py の G32 がこれを検出。
各問で G32=0 かつ「ALL ... PASS」（新規ERRORゼロ）にする。

記号→実体の置換（syn-lead/choice-points 本文のみ）：
- 空欄①②③/選択肢(a)(b)：空欄が表す学説・概念の実体名に置換。例「学生B＝限定説（①a）＋認識必要説（⑥l）」
  →「学生B＝限定説と認識必要説の組合せ」。復元不能な空欄は記号を外し意味の通る一般表現に。
- A説/B説/甲乙説/第N説：本文・ox-stmt から実際の学説名を復元して置換。
- 記述ア/肢N参照：参照を消し記述の内容で自己完結。
- 学生A等の話者ラベル：指す見解の実体名へ（復元可能なら）。

厳守：
1. 編集は .syn-lead と .choice-points 内 li の本文だけ。problem-text/case-description/ox-stmt/
   data-answer-key/data-correct-value/SVG/解法ナビ/.fa-narrative は触らない。
2. 法的意味を変えない。復元不能箇所は変えず報告に「未解決」。
3. 各ファイルで python scripts/validate-tx-core.py <file> を実行し [G32] 消失・ALL ... PASS を確認。
   <a>/<strong> が挟まり一意マッチが外れる時は生HTMLを grep し </a> 以降など実在文字列で置換。
4. commit/push はしない（呼び出し元がレビュー後に実施）。

レポート：各問1行「{コード}: PASS(G32=0) | 要約」または「{コード}: 未解決 — 理由」。最後に「全N問中 PASS x・未解決 y」。
```

## 5. 完了後（呼び出し元）

1. 変更ファイルを in-process validate で一括点検（ERROR 0・G32=0 を確認）。
2. `python scripts/check-duplicates.py outputs`。
3. `git add outputs/ux/000_TX/001_刑法/ && git commit && git push`（committer は `noreply@anthropic.com`）。
4. 全件 G32=0 になったら `docs/deferred-safeguards.md` #1 を完了にし、#3（G32 の ERROR 化）の発火を検討。

## 6. 関連する他の残タスク（`docs/deferred-safeguards.md` 参照）

- **#2 A 意味ラベル展開**：刑法 _lex 339問に `data-fa-label` 後追い（新規生成は自動付与済み）。
- **#3 ERROR化**：G31(=0 済)・G32(本作業完了後)・JX JC1〜JD1・ARIADNE A22/A26。
- **#4 Lexia FA_LABEL_SEED 撤去**：A 全展開→再取込が済んだら削除（前提は整備済み）。
