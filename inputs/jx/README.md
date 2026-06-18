# JX 入力（問題 PDF ＋ 講義逐語）保存場所

**2026-06-06 確定レイアウト。** JX 1 問につき 2 ファイルを **科目フォルダに同居**で保存する。

```
inputs/jx/{科目}/NN.pdf      問題 PDF
inputs/jx/{科目}/NN.txt      同番号の講義逐語（whisper 文字起こし等。.md も可）
```

- `{科目}` ∈ `刑 / 憲 / 民 / 商 / 民訴 / 刑訴 / 行政`
- `NN` は問題番号（ファイル名先頭の連続数字。例 `1.pdf` ＋ `1.txt`）
- **PDF と逐語は同じ番号・同じフォルダ**に置く（例：`inputs/jx/刑/1.pdf` ＋ `inputs/jx/刑/1.txt`）

## 逐語は必須

`jx-batch-runner.ps1` は **同番号の逐語が無い PDF を `SKIP_NO_TRANSCRIPT` で対象外**にする。
逐語（講義文字起こし）は論点・規範・あてはめ・`.lecturer-advice` の第一次情報源。

刑法の逐語コーパスは `outputs/003_WHISPER/001_刑法/刑法_重問NN.txt` にある。これを
`inputs/jx/刑/NN.txt` へコピーして配置する（PDF 番号 N ＝ 重問 N で対応）。

## 生成動線

各問は `canonical/ATHENA.html`（正典スケルトン）を **複製 → 本文空文字列化 →
問題固有内容を鋳造**して生成する（TX の GENESIS 経路と対称）。構造・CSS・
`.lecturer-advice` 4 ブロックが必ず正典品質で揃う。詳細は `CLAUDE.md §4`。

## 起動例

```
pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -MaxProblems 3 -DryRun
pwsh -NoProfile -File scripts/jx-batch-runner.ps1 -Subject 刑 -MaxProblems 5
```
