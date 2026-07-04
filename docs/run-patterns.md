# 実行パターン一覧（号令＝TJR に一元化・2026-07-04 改）

> **【最重要・2026-07-04】生成バッチの号令は `TJR処理` 1 本に統一した。** 旧パターン（TX-MARCH /
> TX-PICK / JX）は**廃止**。TJR が「大元の号令＝指揮者」で、TX新規（T）／JX新規（J）／旧版TXLEX再生成（R）
> を 1 号令で束ねる。実生成は各エンジン（`tx-v13-runner.ps1`／`jx-batch-runner.ps1`）へ委譲する。
> チャットで「**TJR処理 刑訴**」のように科目名を添えて指示すれば起動する。両 PC・全セッション共通の語彙。

## TJR の3ストリーム

| 記号 | ストリーム | 内容 | エンジン | 恒久/過渡 |
|---|---|---|---|---|
| **T** | 新規TX生成 | `inputs/000_TX/{科目}` の未生成番号を最若番から。**v13 二系統＝公式(000_TX 本物5択)＋Lexia `_lex`(ux/000_TX ox-grid＋解法ナビ＋物語)** | `scripts/tx-v13-runner.ps1` | 恒久（未生成が尽きるまで） |
| **J** | 新規JX生成 | `inputs/001_JX/{科目}` の未生成番号を最若番から。JX＋**副産物 RX/TREE/ARIADNE**＋TTS台本＋配置 | `scripts/jx-batch-runner.ps1`（内部エンジン） | 恒久 |
| **R** | 旧版TXLEX再生成 | `_lex` が既存だが版が旧い（v13 でない）かつ**入力PDFが残っている**番号を **PDFから最新v13で作り直す**（公式も同時に最新化）。PDFが消えた番号はスキップ | `scripts/tx-v13-runner.ps1 -Regen` | **過渡＝全件最新化で自然消滅** |

- **同時起動＝1号令で T→J→R を順に自動実行**（1作業ツリーで並行すると git commit/push が衝突する実害が
  記録済み＝`feedback_jx_concurrent_batch_gate_collision`／`feedback_shared_workdir_agent_collision`。よって直列。
  真の並列が要るときは各 PC で番号帯を分ける or 別 worktree で回す）。「1回叩いて放置」を満たす。
- **号令なら指定外も当然に処理（番号ピン方式）**：番号指定は「そのストリームだけ範囲固定」で、他は止めない。
  例「**TX355 を TJR処理**」→ T は 355 固定・**J と R は通常どおり最若番から**。1ストリームだけ回したい時（旧・
  短縮形「TX 355-360 処理」）は `-Only T` を付ける。
- **科目検知順（ユーザー指示・フォルダ番号順とは別）**：**①刑法 ②刑事訴訟法 ③民法 ④民事訴訟法 ⑤商法
  ⑥憲法 ⑦行政法**。`-Subject` 省略時はこの優先順で「仕事のある科目」を1つ自動選択（繰り返し叩くと順に消化）。
- **科目差の自動処理**：`inputs` に対象が無いストリームは自動でスキップ（例：民法は現状 TX 入力ゼロ→T は 0 件で
  即スキップ、J のみ走る）。刑法は公式/_lex がほぼ揃っているので実質 R が主役、刑訴は TX 入力 334 件で T が主役。

## コマンド（号令→実コマンド）

```powershell
# TJR処理 刑訴（T→J→R を順に・既定チャンク T:12 J:3 R:3）
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴

# 科目自動（優先順 刑>刑訴>民>民訴>商>憲>行政 で仕事のある科目を1つ）
pwsh -NoProfile -File scripts/patterns/TJR.ps1

# 番号ピン（そのストリームだけ固定・他は通常）：TX355 を作りつつ J/R は通常
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴 -TxFrom 355 -TxTo 355
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 民 -JxFrom 5 -JxTo 5

# 1ストリームだけ（旧・短縮形「TX 355-360 処理」「JX 1-10 処理」）＝-Only を付ける
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑 -Only T -TxFrom 355 -TxTo 360
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 民 -Only J -JxFrom 1 -JxTo 10

# チャンク数の調整・検出のみ
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴 -MaxTX 20
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴 -DryRun     # 各エンジンの検出だけ
```

### 号令の言い回し（チャット）
- 「**TJR処理 刑訴**」→ 全ストリーム（T→J→R・その科目）。
- 「**TJR処理**」（科目省略）→ 優先順で仕事のある科目を1つ。
- 「**TX355 を TJR処理**」→ `-TxFrom 355 -TxTo 355`（T=355固定・**J/R は通常**）。
- 「**JX5 を TJR処理**」→ `-JxFrom 5 -JxTo 5`（J=5固定・**T/R は通常**）。
- 「**TJR処理 刑（Rだけ）**」→ `-Only R`。
- 「**TX 355-360 処理**」（TXだけ）→ `-Only T -TxFrom 355 -TxTo 360`。
- 「**JX 1-10 処理**」（JXだけ）→ `-Only J -JxFrom 1 -JxTo 10`。

## エンジン（内部・直接は叩かない）

| エンジン | 役割 | 備考 |
|---|---|---|
| `scripts/tx-v13-runner.ps1` | T・R の TX 生成（v13 二系統・validate-tx-core 両検証・作成日時スタンプ・各問 commit/push） | headless prompt＝`prompts/new-tx-headless-v13.md`（手順正典は `.claude/commands/new-tx.md`） |
| `scripts/jx-batch-runner.ps1` | J の JX 生成（副産物 RX/TREE/ARIADNE・TTS台本・deploy・finalize・hooks・keep-awake） | TJR から `-SkipAudio -Finalize` で呼ばれる。多数の常駐スクリプトが依存するため温存 |

> **廃止済み（呼ばない）**：`scripts/patterns/{TX-MARCH,TX-PICK,JX}.ps1`（TJR へ転送するだけの deprecation スタブ）。
> `scripts/night-batch-runner.ps1` は v10 GOLD-SKELETON 専用で TX 生成からは引退（`tx-v13-runner.ps1` が後継）。
> Windows スケジュールタスク（`register-night-batch-tasks.ps1`）がまだ night-batch を指す場合は TJR/tx-v13 へ
> 貼り替える（未整理なら旧 v10 を叩き続けるので注意）。

## R（旧版TXLEX再生成）の対象判定

- 対象＝`outputs/ux/000_TX/{科目}/*_lex.html` のうち **版マーカーが v13 でない**（`v13.0.0`/`LOOP-CARD`/`GENESIS-CARD` を
  含まない）もの、**かつ** `inputs/000_TX/{科目}/{番号}.pdf` が残っているもの。
- PDF が既に削除された旧_lex は **再生成不能**＝`[R-SKIP-NOPDF]` を出してスキップ（Drive の抽出PDFバックアップから
  復元後に再対象化）。R は全件 v13 化で対象が尽きて自然消滅する。
- 方式は **PDFから完全新規再生成**（決定論 recanon ではない・ユーザー選択 2026-07-04）。旧本文（Codex期）の判例誤りを
  継承しないため、既存 HTML を template 起点にせず GENESIS-CARD から作り直す。

## 音声（wav）の作り方 — AI Studio で手動（2026-06-06〜・変更なし）

- J（JX）は**台本（txt）まで**生成する。音声は**自動化しない**。各問の台本は
  `outputs/002_TTS/{科目}/{問題ID}/`（配置後は `…\A_重問耳トレ\N 科目\TTSファイル原本\{問題ID}\`）。
- これを **AI Studio（aistudio.google.com）で手動**に音声化し、wav を `…\A_重問耳トレ\N 科目\{問題ID}\` に置く。
  DL 時に台本の連番へリネーム（台本 `刑JX029-3.txt` → 音声 `29-3.wav`）。
- 旧・自動音声段（`jx-batch-runner.ps1 ⑤` / `tts/run-tts.ps1` / `generate_tts.py`）は残置するが TJR 経由では呼ばれない。

## 入力レイアウト

```
# TX
inputs/000_TX/{科目}/NN.pdf                       （フラット・科目フォルダ 00N_科目）
# JX
inputs/001_JX/{科目}/重問PDF/NN.pdf
inputs/001_JX/{科目}/講義逐語/{科目}_重問逐語NN.txt
```

## 成果物の配置（J＝JX の ⑥ deploy・Drive＋repo ミラー）

JX バッチは末尾 ⑥ で成果物を **2 系統**へ自動配置する（`scripts/jx-deploy.ps1`）。

| 種別 | 配置先（`2 JX_論 文\` 以下） |
|---|---|
| JX HTML | `00N_科目\`（例 刑=`001_刑法`）※フラット |
| TTS 台本 txt | `A_重問耳トレ\N 科目\TTSファイル原本\{問題ID}\` |
| 音声 wav | `A_重問耳トレ\N 科目\{問題ID}\` |

- ① repo ミラー：`deploy\2 JX_論 文\…`（構造のみ git・実ファイルは `.gitignore`）
- ② Google Drive：`H:\マイドライブ\…\2 JX_論 文\…`（H: マウント時のみ）
- フォルダ作成：`pwsh -NoProfile -File scripts/jx-deploy.ps1 -InitAll`／配置停止：`-SkipDeploy`

## 備考

- 巨大プロンプトは **stdin パイプ**で `claude -p` に渡す（`-p 引数`渡しは PowerShell が壊す）。
- TX 各問は GENESIS-CARD を起点に v13 二系統で生成、JX 各問は ATHENA を複製→鋳造。
- HTML 成果物は生成＝コミットで永続化（CLAUDE.md §9）。作成日時スタンプは pre-commit フックが保険で刻む。
