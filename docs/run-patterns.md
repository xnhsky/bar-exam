# 実行パターン一覧（パターン名で運用）

> 生成バッチを「パターン名」で呼び出すための一覧。チャットで「**JX で**」「**TX-MARCH 回して**」
> のように指示すれば、対応するコマンドを実行する。両 PC・全セッション共通の語彙。

## 一覧

| パターン名 | 系統 | エンジン | 何をするか | 鍵 / 音声 |
|---|---|---|---|---|
| **TX-MARCH** | TX① 連番NBR | GENESIS | tx-pdfs 最若番から N 問（既定5）生成→検証→各問 commit/push | — |
| **TX-PICK** | TX② 任意NBR | GENESIS | 指定番号 / 範囲の TX を生成 | — |
| **JX** | JX 生成 | ATHENA | inputs/jx 最若番から N 問（既定3）JX→validate→台本→validate→配置まで（**音声は含まない**） | — |

> **2026-06-06 方針変更：** JX は **TTS 台本生成まで**で止める。**音声（wav）は自動化せず、
> 台本（`outputs/002_TTS/{問題ID}/` ＝ 配置先 `TTSファイル原本\`）から AI Studio で手動生成**する。
> これに伴い Gemini API を使った自動音声生成（旧 ⑤ 段）・鍵（main/sub）・Pro/Flash の区別は撤回した。
>
> **2026-06-08 統合：** 旧 JX-MAIN / JX-SUB は鍵区別の撤去で中身が同一になったため **`JX` 1 本に統合**。
> 二台運用は各 PC で番号帯を分けて並行する（例 PC-A `-FromNumber 1 -ToNumber 20`／PC-B `-FromNumber 21 -ToNumber 40`）。

## コマンド

```powershell
# TX-MARCH（連番・既定5問）
pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1
pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1 -MaxProblems 3
pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1 -DryRun

# TX-PICK（任意番号 / 範囲）
pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -Number 366
pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -FromNumber 366 -ToNumber 370

# JX（JX→台本まで・既定3問。音声は AI Studio で手動）
pwsh -NoProfile -File scripts/patterns/JX.ps1
pwsh -NoProfile -File scripts/patterns/JX.ps1 -Subject 民 -MaxProblems 3
pwsh -NoProfile -File scripts/patterns/JX.ps1 -DryRun        # 検出のみ
pwsh -NoProfile -File scripts/patterns/JX.ps1 -FromNumber 25 -ToNumber 27  # 25〜27 だけ
pwsh -NoProfile -File scripts/patterns/JX.ps1 -Number 25     # 25 を1問だけ
```

## 鍵の管理（JX では不要）

- **JX は API 鍵を使わない**（音声を自動生成しないため）。`.secrets/gemini_*.key` の用意は不要。
- 鍵を使うのは、下の jx-batch-runner.ps1 を**直接** `-SkipAudio` なしで叩いて自動音声を出す場合のみ
  （通常運用では使わない＝お蔵入り）。その場合に限り `.secrets/gemini_{main|sub}.key`（git 管理外）か `$env:GEMINI_API_KEY` を読む。

## 音声（wav）の作り方 — AI Studio で手動（2026-06-06〜）

- JX は**台本（txt）まで**生成する。音声は**自動化しない**。
- 各問の台本は `outputs/002_TTS/{問題ID}/`（配置後は `…\A_重問耳トレ\N 科目\TTSファイル原本\{問題ID}\`）にある。
  ファイル名は **`{問題ID}-{連番}.txt`**（2026-06-08〜・フラット通し番号。例 `刑JX029-1.txt` … `刑JX029-13.txt`）。
  これを **AI Studio（aistudio.google.com）で手動**に音声化し、wav を `…\A_重問耳トレ\N 科目\{問題ID}\` に置く。
- **音声（DL）ファイルの保存名は台本の連番に合わせる**：`{問題番号}-{連番}`（例 `29-1.wav` … `29-13.wav`）。
  AI Studio は出力名を事前固定できないため、**DL 時に手動で台本の番号へリネーム**する（台本 `刑JX029-3.txt` → 音声 `29-3.wav`）。
- 演技指示・声の指定（旧 `STYLE_PROMPT` / `Laomedeia` 等）は AI Studio 側で都度指定する。
- 旧・自動音声段（`jx-batch-runner.ps1 ⑤` / `tts/run-tts.ps1` / `generate_tts.py`）は残置するが、
  パターン経由では呼ばれない（Gemini Pro TTS は無料枠が上限0＝429・Flash は使わない方針のため撤回）。

## 入力レイアウト（JX）

```
inputs/jx/{科目}/重問PDF/NN.pdf
inputs/jx/{科目}/講義逐語/{科目}_重問NN[_文字起こし].txt
```
（旧フラット `inputs/jx/{科目}/NN.pdf ＋ NN.txt` も後方互換で拾う）

## 成果物の配置（⑥ deploy・Drive＋repo ミラー）

JX バッチ（JX）は末尾 ⑥ で、生成できた各問の成果物を **2 系統**へ自動配置する。

- **科目別の配置先**（`scripts/jx-deploy.ps1` が解決）:

  | 種別 | 配置先（`2 JX_論 文\` 以下） |
  |---|---|
  | JX HTML | `00N_科目\`（例 刑=`001_刑法`）※フラット |
  | TTS 台本 txt | `A_重問耳トレ\N 科目\TTSファイル原本\{問題ID}\`（例 `1 刑法\TTSファイル原本\刑JX025\`） |
  | 音声 wav | `A_重問耳トレ\N 科目\{問題ID}\`（例 `1 刑法\刑JX025\`） |

  ※ 台本・音声は**問題IDごとのサブフォルダ**にまとめる。HTML は従来どおりフラット。

- **2 系統**:
  - ① repo ミラー：`deploy\2 JX_論 文\…`（常時。構造のみ git 管理＝`.gitkeep`／実ファイルは `.gitignore`）
  - ② Google Drive：`H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\2 JX_論 文\…`（**H: マウント時のみ**。未マウントなら repo ミラーだけ）

- **フォルダ作成（初回 / 科目追加時）**:
  ```powershell
  pwsh -NoProfile -File scripts/jx-deploy.ps1 -InitAll      # 全7科目を repo＋Drive 両方に作成
  ```
- **手動配置**（バッチを通さず既存成果物を置き直す）:
  ```powershell
  pwsh -NoProfile -File scripts/jx-deploy.ps1 -Subject 刑 -ProblemId 刑JX002
  pwsh -NoProfile -File scripts/jx-deploy.ps1 -Subject 刑                 # 科目の全HTML分
  ```
- バッチで配置を止めるには `-SkipDeploy`（`JX.ps1` 経由なら underlying runner へ委譲）。

## 備考

- いずれのパターンも、巨大プロンプトは **stdin パイプ**で claude -p に渡す（`-p 引数`渡しは PowerShell が壊すため・特に nested 実行で顕著）。
- JX 各問は ATHENA を複製→鋳造、TX 各問は GENESIS を起点に生成。
- HTML 成果物は生成＝コミットで永続化（CLAUDE.md §9）。音声 wav はローカル管理（`tts/output_audio/` は git 管理外）。
