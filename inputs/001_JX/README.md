# JX 入力（問題 PDF ＋ 講義逐語）保存場所

**2026-06-20 更新レイアウト（科目フォルダを 00N_科目 へ統一・outputs と対称）。**
JX 1 問の入力は **科目フォルダ配下の `重問PDF/`・`講義逐語/`** に分けて保存する。

```
inputs/001_JX/{00N_科目}/重問PDF/NN.pdf            問題 PDF
inputs/001_JX/{00N_科目}/講義逐語/{科目名}_重問逐語NN.txt   同番号の講義逐語（.md も可）
```

- `{00N_科目}` ∈ `001_刑法 / 002_刑事訴訟法 / 003_民法 / 004_商法 / 005_民事訴訟法 / 006_行政法 / 007_憲法`
  （`jx-batch-runner.ps1 -Subject` や `check-jx-alignment.py` の科目引数は短縮名 `刑/憲/…` を維持。
  スクリプトが内部で 00N_科目 フォルダへ解決する）
- `NN` は問題番号（PDF と逐語は内容照合で同番号に揃える。正典は各科目 `逐語-PDF対応表.md`）

## 逐語は必須

`jx-batch-runner.ps1` は **同番号の逐語が無い PDF を `SKIP_NO_TRANSCRIPT` で対象外**にする。
逐語（講義文字起こし）は論点・規範・あてはめ・`.lecturer-advice` の第一次情報源。

刑法の逐語コーパスは `outputs/003_WHISPER/001_刑法/刑法_重問NN.txt` にある。これを
`inputs/001_JX/001_刑法/講義逐語/` へ内容照合して同番号で配置する（PDF 番号 N ＝ 重問 N で対応）。

## 生成動線

各問は `canonical/ATHENA.html`（正典スケルトン）を **複製 → 本文空文字列化 →
問題固有内容を鋳造**して生成する（TX の GENESIS 経路と対称）。構造・CSS・
`.lecturer-advice` 4 ブロックが必ず正典品質で揃う。詳細は `CLAUDE.md §4`。

## 起動例

```
pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -MaxProblems 3 -DryRun
pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -MaxProblems 5
```
