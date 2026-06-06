# 実行パターン一覧（パターン名で運用）

> 生成バッチを「パターン名」で呼び出すための一覧。チャットで「**JX-MAIN で**」「**TX-MARCH 回して**」
> のように指示すれば、対応するコマンドを実行する。両 PC・全セッション共通の語彙。

## 一覧

| パターン名 | 系統 | エンジン | 何をするか | 鍵 / 音声 |
|---|---|---|---|---|
| **TX-MARCH** | TX① 連番NBR | GENESIS | tx-pdfs 最若番から N 問（既定5）生成→検証→各問 commit/push | — |
| **TX-PICK** | TX② 任意NBR | GENESIS | 指定番号 / 範囲の TX を生成 | — |
| **JX-MAIN** | JX① メイン | ATHENA | inputs/jx 最若番から N 問（既定3）JX→台本→**Pro 音声**まで一気通貫 | `gemini_main.key` / Pro |
| **JX-SUB** | JX② サブ | ATHENA | JX-MAIN と同じ一気通貫をサブ鍵で。音声は既定 **Flash(無料)** | `gemini_sub.key` / Flash |

## コマンド

```powershell
# TX-MARCH（連番・既定5問）
pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1
pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1 -MaxProblems 3
pwsh -NoProfile -File scripts/patterns/TX-MARCH.ps1 -DryRun

# TX-PICK（任意番号 / 範囲）
pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -Number 366
pwsh -NoProfile -File scripts/patterns/TX-PICK.ps1 -FromNumber 366 -ToNumber 370

# JX-MAIN（メイン鍵・Pro音声・既定3問）
pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1
pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -Subject 民 -MaxProblems 3
pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -DryRun        # 検出のみ・無課金
pwsh -NoProfile -File scripts/patterns/JX-MAIN.ps1 -SkipAudio     # ④まで（音声なし）

# JX-SUB（サブ鍵・Flash音声=無料・既定3問）
pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1
pwsh -NoProfile -File scripts/patterns/JX-SUB.ps1 -TtsModel ''    # サブ鍵が課金可なら Pro 音声に
```

## 鍵の管理（重要・git 管理外）

- 鍵は `.secrets/` に置く。**git 管理外**（`.gitignore` で `.secrets/` と `*.key` を除外）。GitHub に載らない。
  - `.secrets/gemini_main.key` … JX-MAIN 用（**Pro 利用可**の鍵）
  - `.secrets/gemini_sub.key`  … JX-SUB 用（サブ鍵）
- ランナーは `$env:GEMINI_API_KEY` があればそれを優先、無ければ `KeyName`（main/sub）に応じた鍵ファイルを自動読込。
- 鍵を更新するときは該当 `.key` ファイルの中身を差し替えるだけ。コードや本ドキュメントには鍵を書かない。
- **鍵をローテーション（再発行）したら `.secrets/*.key` も更新**すること。

## 音声モデルと課金（JX の ⑤ 段）

- 既定（JX-MAIN）= `gemini-2.5-pro-preview-tts`（本番品質・**課金有効プロジェクトの鍵が必要**。無料枠は上限0で 429）。
- JX-SUB 既定 = `gemini-2.5-flash-preview-tts`（**無料枠で動く**・品質は一段下）。
- 音声を止めて台本までにするなら `-SkipAudio`。
- `GEMINI_API_KEY` 未設定かつ鍵ファイルも無い場合は ⑤ 音声のみ自動スキップ（JX/台本は生成）。

## 入力レイアウト（JX）

```
inputs/jx/{科目}/重問PDF/NN.pdf
inputs/jx/{科目}/講義逐語/{科目}_重問NN[_文字起こし].txt
```
（旧フラット `inputs/jx/{科目}/NN.pdf ＋ NN.txt` も後方互換で拾う）

## 成果物の配置（⑥ deploy・Drive＋repo ミラー）

JX バッチ（JX-MAIN / JX-SUB）は末尾 ⑥ で、生成できた各問の成果物を **2 系統**へ自動配置する。

- **科目別の配置先**（`scripts/jx-deploy.ps1` が解決）:

  | 種別 | 配置先（`2 JX_論 文\` 以下） |
  |---|---|
  | JX HTML | `00N_科目\`（例 刑=`001_刑法`） |
  | TTS 台本 txt | `A_重問耳トレ\N 科目\TTSファイル原本\`（例 刑=`1 刑法`） |
  | 音声 wav | `A_重問耳トレ\N 科目\` |

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
- バッチで配置を止めるには `-SkipDeploy`（例 `JX-MAIN.ps1` 経由なら underlying runner へ委譲）。

## 備考

- いずれのパターンも、巨大プロンプトは **stdin パイプ**で claude -p に渡す（`-p 引数`渡しは PowerShell が壊すため・特に nested 実行で顕著）。
- JX 各問は ATHENA を複製→鋳造、TX 各問は GENESIS を起点に生成。
- HTML 成果物は生成＝コミットで永続化（CLAUDE.md §9）。音声 wav はローカル管理（`tts/output_audio/` は git 管理外）。
