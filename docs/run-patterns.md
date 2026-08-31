# 実行パターン一覧（号令＝TJR に一元化・2026-07-04 改／F 修復ストリーム追加・2026-07-24）

> **【最重要・2026-07-04】生成バッチの号令は `TJR処理` 1 本に統一した。** 旧パターン（TX-MARCH /
> TX-PICK / JX）は**廃止**。TJR が「大元の号令＝指揮者」で、TX新規（T）／JX新規（J）／旧版TXLEX再生成（R）
> ／修復（F・2026-07-24 新設）を 1 号令で束ねる。実生成は各エンジン（`tx-v13-runner.ps1`／`jx-batch-runner.ps1`）へ委譲する。
> チャットで「**TJR処理 刑訴**」のように科目名を添えて指示すれば起動する。両 PC・全セッション共通の語彙。

## TJR の6ストリーム

| 記号 | ストリーム | 内容 | エンジン | 恒久/過渡 |
|---|---|---|---|---|
| **F** | 修復（エラー品・未完成品の回収・2026-07-24 新設） | 毎バッチ**先頭**で `tjr-audit.py` が全科目を監査：**①二系統ペア欠け**（公式のみ/_lexのみ）**②途切れ**（`</html>`なし）**③プレースホルダー残骸**（`{{SLOT}}`）**④サイズ異常 ⑤未コミット残骸**（検証PASS→**回収コミット**のみ・FAIL→再生成）を検出し、入力PDF（JXは＋逐語）が残るものを**修復再生成**。G66/G69 のみの失敗は `tx-sysmap-fit.py`（決定論）で無料修復。**同一問題 2 回失敗で自動再試行停止＝ESCALATE**（`logs/tjr-repair-report.md`）。対象ゼロなら数十秒の監査だけで素通り | `scripts/tjr-audit.py`（検出）＋`tx-v13-runner.ps1 -RepairIds`／`jx-batch-runner.ps1 -RepairNumbers`（再生成） | 恒久（常設の安全網） |
| **T** | 新規TX生成（フロンティア前進） | `inputs/000_TX/{科目}` の未生成番号のうち**公式の最大既存番号より先**を最若番から（過去帯の欠番は R の領分＝二重処理防止・2026-07-18）。**v13 二系統＝公式(000_TX 本物5択)＋Lexia `_lex`(ux/000_TX ox-grid＋解法ナビ＋物語)** | `scripts/tx-v13-runner.ps1` | 恒久（未生成が尽きるまで） |
| **J** | 新規JX生成 | `inputs/001_JX/{科目}` の未生成番号を最若番から。JX＋**副産物 RX/TREE/ARIADNE**＋TTS台本＋配置 | `scripts/jx-batch-runner.ps1`（内部エンジン） | 恒久 |
| **R** | さかのぼり（旧版TXLEX再生成＋欠番補完） | (a) `_lex` が既存だが版が旧い（v13 でない）かつ**入力PDFが残っている**番号を **PDFから最新v13で作り直す**（公式も同時に最新化）。PDFが消えた番号はスキップ。(b) **公式最大番号以下の欠番**（PDFあり・公式なし＝過去帯の未生成穴。例：刑法 15-54/304-309/312-323 の58件）の**補完生成**（2026-07-18 ユーザー確定「刑法58件未生成の分をR再生成と併せる」） | `scripts/tx-v13-runner.ps1 -Regen` | **過渡＝全件最新化で自然消滅** |
| **Q** | §v13q 付随・特別枠（2026-07-28 新設） | **刑訴TX の既存 `_lex`（v13）で答案圧縮（`tx-anscomp-line`）未展開の残件**（設置時点＝081-179 の99本）を若番から **1バッチ10本ずつ** headless（Opus 5 固定＝`-Model claude-opus-5`）で §v13q 改訂（✍答案圧縮＋GIST自己完結＋訂正チップ最小化＋#basis空箱hidden）。レシピ正典＝`docs/v13q-handover.md`／プロンプト＝`prompts/v13q-headless.md`。ランナーが validate-tx-core＋check-tx-lex-engine を再検証し **PASS のみ 1問ずつ commit/push**（FAIL はロールバック・同一問題2回失敗で ESCALATE）。二台衝突は claim（`{ID}_v13q`）＋リモート改訂済み検知で回避 | `scripts/v13q-runner.ps1` | **過渡＝残件ゼロ（完遂）で「該当なし」SKIP＝自然消滅** |
| **S** | §v13v「📖 ものがたり」付随・特別枠（2026-08-22 新設） | **正誤表の各記述に `data-brief-story`（物語解説の全体＋当該記述の要約＋具体例）が未執筆の `_lex`** を、**仕事のある科目へ均等に配る**（ラウンドロビン・2026-08-31 ユーザー指示・`-MaxS` 既定10本／科目内は若番順／「TJR処理 刑訴」で寄せられる）でheadless（Opus 5 固定）で執筆。土台（`TX-VERDICT-STORY` CSS＋`appendStoryLine`）が無いファイルはランナーが `tx-lex-verdict-redesign.py` で先に注入する。レシピ正典＝`docs/v13v-handover.md`／プロンプト＝`prompts/v13v-headless.md`／素材＝`scripts/v13v-extract.py`／注入＝`scripts/v13v-inject.py`。ランナーが validate-tx-core＋check-tx-lex-engine を再検証し **PASS のみ 1問ずつ commit/push**（FAIL はロールバック・同一問題2回失敗で ESCALATE）。二台衝突は claim（`{ID}_v13v`）＋リモート執筆済み検知で回避。**2026-08-28 改定**＝ものがたり帯は「体系的位置づけ・趣旨・考え方のコツ・実務での動き方＋具体例」で書く（旧型＝出題構造・解答技術の解説は書かない）。旧型で執筆済みのファイルは `-Rewrite` で新型へ書き直す（TJR は未執筆が尽きたら自動で `-Rewrite` にフォールバック。判定＝ものがたり本文 200 字未満の行があれば旧型・注入は `--force`・claim/台帳は `_v13v2`／`#rw` で別枠） | `scripts/v13v-runner.ps1` | **過渡＝残件ゼロ（完遂）で「該当なし」SKIP＝自然消滅** |

- **同時起動＝1号令で F→T→J→R→Q→S を順に自動実行**（1作業ツリーで並行すると git commit/push が衝突する実害が
  記録済み＝`feedback_jx_concurrent_batch_gate_collision`／`feedback_shared_workdir_agent_collision`。よって直列。
  真の並列が要るときは各 PC で番号帯を分ける or 別 worktree で回す）。「1回叩いて放置」を満たす。
  **「修復と新規生成の同時並行」（2026-07-24 ユーザー指示）は「1 号令の中で F と T/J/R の両方が自動で進む」
  形で実現**（プロセス並列は上記 git 衝突実害により不採用）。
- **号令なら指定外も当然に処理（番号ピン方式）**：番号指定は「そのストリームだけ範囲固定」で、他は止めない。
  例「**TX355 を TJR処理**」→ T は 355 固定・**J と R は通常どおり最若番から**。1ストリームだけ回したい時（旧・
  短縮形「TX 355-360 処理」）は `-Only T` を付ける。
- **科目検知順（ユーザー指示・フォルダ番号順とは別）**：**①刑法 ②刑事訴訟法 ③民法 ④民事訴訟法 ⑤商法
  ⑥憲法 ⑦行政法**。**T・J・R がストリーム別に独立に**この優先順で「そのストリームに仕事のある科目」を自動充当する
  （2026-07-18 ユーザー確定。例：T=刑法が尽きたら刑訴へ・R=刑法・J=刑法に無ければ刑訴へ）。`-Subject` 明示時は
  その科目を最優先し、そのストリームに仕事が無ければ優先順の残りへフォールスルー。**R は過渡ストリーム＝全科目を
  遡って旧版_lexが無ければ「該当なし」スキップが正常**（無理に仕事を探さない・ユーザー確認 2026-07-18）。
- **バッチ単位固定（2026-07-18 ユーザー確定）**：1バッチ＝ **T:12問 / J:3問 / R:3問**（TJR 既定値）。回数は
  ユーザーが「TJRを○バッチ」で指示（`-Batches N`・バッチ間も直列・毎バッチ科目を再解決＝尽きた科目から次へ自動で
  移る）。勝手なチャンク拡大・自動完遂ループは禁止（`feedback_tjr_batch_unit_fixed`）。
  **F の単位（2026-07-24）**：修復再生成は 1バッチ **TX:3問（`-MaxF`）／JX:1問（`-MaxFJx`）**まで・回収コミット
  （再生成しない git 回収）は件数無制限（安価なため）。F は検出があるときだけ動く＝通常はゼロコスト。
- **科目差の自動処理**：`inputs` に対象が無いストリームは自動でスキップ（例：民法は現状 TX 入力ゼロ→T は 0 件で
  即スキップ、J のみ走る）。刑法は公式/_lex がほぼ揃っているので実質 R が主役、刑訴は TX 入力 334 件で T が主役。

## コマンド（号令→実コマンド）

```powershell
# TJR処理（1バッチ＝T12/J3/R3・科目は T/J/R ストリーム別に優先順で自動充当）
pwsh -NoProfile -File scripts/patterns/TJR.ps1

# TJRを3バッチ処理（直列・毎バッチ科目を再解決）
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Batches 3

# TJR処理 刑訴（刑訴を最優先・そのストリームに仕事が無ければ優先順へフォールスルー）
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴

# 番号ピン（そのストリームだけ固定・他は通常）：TX355 を作りつつ J/R は通常
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴 -TxFrom 355 -TxTo 355
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 民 -JxFrom 5 -JxTo 5

# 1ストリームだけ（旧・短縮形「TX 355-360 処理」「JX 1-10 処理」）＝-Only を付ける
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑 -Only T -TxFrom 355 -TxTo 360
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 民 -Only J -JxFrom 1 -JxTo 10

# Q（§v13q 特別枠）だけ回す／件数を変える／止める
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -Only Q            # 10本だけ処理
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -Only Q -MaxQ 20   # 件数変更
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -SkipQ             # 通常TJRからQを外す

# S（§v13v ものがたり特別枠）だけ回す／件数を変える／止める（科目は民法→刑法の優先順）
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -Only S            # 10本だけ処理（民法優先）
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -Only S -MaxS 20   # 件数変更
pwsh -NoProfile -File scripts\patterns\TJR.ps1 -SkipS             # 通常TJRからSを外す
pwsh -NoProfile -File scripts\v13v-runner.ps1 -Subject 刑法 -DryRun # 科目指定で対象確認
pwsh -NoProfile -File scripts\v13v-runner.ps1 -Rewrite -Subject 刑訴 -DryRun # 旧型（出題構造型）の残件を確認
pwsh -NoProfile -File scripts\v13v-runner.ps1 -Rewrite -MaxProblems 10        # 旧型を新型へ書き直す
# ※通常の「TJR処理」でも毎バッチ末尾で自動的に10本ずつ消化される（完遂まで）

# 修復だけ（F単独＝監査→回収コミット→修復再生成。新規生成はしない）
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Only F

# 監査だけ手で見る（read-only・TJR を介さず直接）
python scripts/tjr-audit.py

# チャンク数の調整・検出のみ
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴 -MaxTX 20
pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴 -DryRun     # 各エンジン＋F監査の検出だけ
```

### 号令の言い回し（チャット）
- 「**TJR処理**」「**TJRを1バッチ**」→ 1バッチ（T12/J3/R3）・科目はストリーム別に優先順で自動充当。
- 「**TJRを3バッチ処理**」→ `-Batches 3`（直列・毎バッチ科目再解決）。
- 「**TJR処理 刑訴**」→ 刑訴を最優先（仕事の無いストリームは優先順へフォールスルー）。
- 「**TX355 を TJR処理**」→ `-TxFrom 355 -TxTo 355`（T=355固定・**J/R は通常**）。
- 「**JX5 を TJR処理**」→ `-JxFrom 5 -JxTo 5`（J=5固定・**T/R は通常**）。
- 「**TJR処理 刑（Rだけ）**」→ `-Only R`。
- 「**TX 355-360 処理**」（TXだけ）→ `-Only T -TxFrom 355 -TxTo 360`。
- 「**JX 1-10 処理**」（JXだけ）→ `-Only J -JxFrom 1 -JxTo 10`。
- 「**修復だけ**」「**エラー品を直して**」→ `-Only F`（F は通常の「TJR処理」にも毎バッチ自動で入っている）。

## エンジン（内部・直接は叩かない）

| エンジン | 役割 | 備考 |
|---|---|---|
| `scripts/tx-v13-runner.ps1` | T・R の TX 生成（v13 二系統・validate-tx-core 両検証・作成日時スタンプ・各問 commit/push）＋F の TX 修復再生成（`-RepairIds '60,125'`＝T/R の検出をバイパスして番号直指定・REGEN 上書き） | headless prompt＝`prompts/new-tx-headless-v13.md`（手順正典は `.claude/commands/new-tx.md`） |
| `scripts/jx-batch-runner.ps1` | J の JX 生成（副産物 RX/TREE/ARIADNE・TTS台本・deploy・finalize・hooks・keep-awake）＋F の JX 修復再生成（`-RepairNumbers '5'`＝SKIP_EXISTS を突破・既存破損 HTML は `logs/jx-repair-backup/` へ退避し生成空振り時は自動復元） | TJR から `-SkipAudio -Finalize` で呼ばれる。多数の常駐スクリプトが依存するため温存 |
| `scripts/tjr-audit.py` | F の検出器（read-only 基本）。ペア欠け／途切れ／プレースホルダー残骸／サイズ異常／未コミット残骸（検証PASS=回収コミット候補・FAIL=再生成候補）／JX 副産物欠落（報告のみ）を JSON で TJR へ渡す。`--fix-safe` 時のみ G66/G69 限定で `tx-sysmap-fit.py` を実行 | 直接叩いてもよい（`python scripts/tjr-audit.py`＝人間向けサマリ表示・exit 1=修復対象あり） |

> **廃止済み（呼ばない）**：`scripts/patterns/{TX-MARCH,TX-PICK,JX}.ps1`（TJR へ転送するだけの deprecation スタブ）。
> `scripts/night-batch-runner.ps1` は v10 GOLD-SKELETON 専用で TX 生成からは引退（`tx-v13-runner.ps1` が後継）。
> Windows スケジュールタスク（`register-night-batch-tasks.ps1`）がまだ night-batch を指す場合は TJR/tx-v13 へ
> 貼り替える（未整理なら旧 v10 を叩き続けるので注意）。

## 既存展開の配り方（仕事のある科目へ均等に配る・2026-08-31 ユーザー指示）

> **正典改定を既存ファイルへ後追い展開するとき、対象の選び方はこの一本に統一する。**
> S ストリームだけの話ではなく、**以後の「既存分の修正依頼」全般に適用する考え方**とする。

### 既定：ラウンドロビン（設定不要・維持不要）

1 バッチ分（既定 10 本）を、**仕事のある科目へ 1 本ずつ順に配って**埋める。科目内は若番順。
科目が尽きたら飛ばして次へ回るので枠は余らない（残り 1 科目なら全枠がそこへ行く）。

**なぜこれか**：学習は全教科を順に回して一巡したらまた戻る、という形で進む。であれば
**どの科目も同じペースで改訂されている**のが最も都合がよい。戻ってきたときに、どの科目も
等しく手が入っているからである。

**なぜ「学習の進度」を設定に書かないか**：一度は
`$LearnedUpTo = @{ '刑訴' = 74 }` のように学習の区切りを設定へ持たせたが、これは
**①学習が進むたび人が書き換えないと実態とズレる**（ズレても何のエラーも出ない）
**②一巡すると全科目が「学習済み」になり区切り自体が消える**、という 2 点で運用に合わない。
維持されない設定は、無いほうが安全である。

### いま学習中の科目へ寄せたいとき

号令に科目名を添えるだけ ── 「**TJR処理 刑訴**」。これで S もその科目だけを流す。
（2026-08-31 以前は TJR の `-Subject` が S へ渡っておらず、この号令が S にだけ効いていなかった。
`$SSubjectMap` で TJR の短縮キー（刑/民/…）を S のキー（刑法/民法/…）へ写像して繋いだ。）
番号を狙い撃ちするときは `-FromNumber` / `-ToNumber`。

### 新規生成（T/J/R）とは別系統

新規生成の科目検知順は従来どおり **①刑法 ②刑事訴訟法 ③民法 ④民事訴訟法 ⑤商法 ⑥憲法 ⑦行政法**
（本ページ冒頭）で、こちらは「そのストリームに仕事のある科目」を優先順で 1 つ選ぶ方式のまま。
均等配分にしているのは**既存ファイルへの展開（S）**だけである。

### 修正依頼を受けたときの型

正典改定そのものの進め方は `docs/canonical-revision-migration-playbook.md` が正典。要約すると
①gold を 1 本作って型を承認してもらう ②土台（CSS/エンジン）は決定論ツールで一括伝播する
③**内容の執筆はラウンドロビンで消化する** ④再発防止の機械ゲートを足す、の 4 段。

## R（さかのぼり＝旧版TXLEX再生成＋欠番補完）の対象判定

- **(a) 旧版再生成**＝`outputs/ux/000_TX/{科目}/*_lex.html` のうち **版マーカーが v13 世代でない**（feature-tag
  `TX v13.x.y LOOP-CARD` を含まない）もの、**かつ** `inputs/000_TX/{科目}/{番号}.pdf` が残っているもの。
- **(b) 欠番補完（2026-07-18 追加）**＝`公式の最大既存番号以下`で **PDF あり・公式 HTML なし**の番号（過去帯の
  未生成穴・_lex も無い）。**T との境界は「公式最大番号」**＝T はその先（フロンティア前進）だけを扱うため、
  同一科目で T と R が同じ番号を同一バッチに二重処理することは構造上ない。欠番帯を明示処理したい時は
  R をピン（`-RFrom`/`-RTo`）する（T ピンはフロンティア外の番号を拾わない）。
- PDF が既に削除された旧_lex は **再生成不能**＝`[R-SKIP-NOPDF]` を出してスキップ（Drive の抽出PDFバックアップから
  復元後に再対象化）。R は全件 v13 化＋欠番解消で対象が尽きて自然消滅する（該当なし=正常）。
- 方式は **PDFから完全新規再生成**（決定論 recanon ではない・ユーザー選択 2026-07-04）。旧本文（Codex期）の判例誤りを
  継承しないため、既存 HTML を template 起点にせず GENESIS-CARD から作り直す。

## F（修復＝エラー品・未完成品の回収）の対象判定と安全設計（2026-07-24 新設）

**動機**：T/J/R は「出力ファイルが存在するか」で対象を決めるため、生成が途中で死んだ／validate ERROR で
commit されずに残った HTML は、**存在するだけで** T（`Test-Path` SKIP）・R(a)（v13 マーカーで SKIP）・
R(b)（公式ありで SKIP）・J（`SKIP_EXISTS`）の全てから不可視＝**未完成のまま永久放置**になる構造穴があった。
F はこの「事故の残骸」を毎バッチ検出して回収する常設の安全網（ユーザー指示 2026-07-24）。

- **検査スコープはインシデント（事故の残骸）に限定**：①TX 二系統ペア欠け ②途切れ（末尾 `</html>` なし）
  ③プレースホルダー残骸（`{{SLOT}}`）④サイズ異常（30KB 未満）⑤未コミット残骸（`git status` dirty）
  ⑥JX 副産物欠落（**検出・報告のみ**＝修復は ②-verify／`rx-arb-autofill` の領分）。
  **コミット済み・構造健全なファイルへ最新ゲート（G70 等）を遡及適用する再監査はしない**
  （旧作の後付けゲート違反は「TJR 付随で消化」＝R の領分・ユーザー方針 2026-07-14/18 のまま）。
- **修復の振り分け**：未コミット残骸は該当検証（validate-tx-core／check-tx-lex-engine／
  check-lex-oxgrid-integrity／validate-jx）を通し、**PASS→回収コミットのみ（再生成しない＝安価）／
  FAIL→修復再生成**。構造破損（①〜④）は入力（TX=PDF・JX=PDF＋逐語）が残っていれば**修復再生成**、
  無ければ report-only（`[F-SKIP-NOPDF]`・Drive 復元後に再対象化）。
- **生成中ガード**：関連ファイルの最終更新が 45 分以内なら「in-flight（生成中の可能性）」として
  今回はスキップ（並行する手動セッション等の書きかけを事故と誤認しない）。
- **再試行の上限＝ESCALATE**：台帳 `logs/tjr-repair-ledger.json`（PC ローカル）で試行を数え、
  **同一問題 2 回失敗で自動再試行を停止**し `logs/tjr-repair-report.md` へ ESCALATE 記録（手動対応待ち）。
  無限再生成でトークンを溶かさない（省エネ規律）。修復が完了して監査から消えれば台帳エントリは自動削除。
- **決定論修復の優先**：validate 失敗が G66/G69（体系マップ幾何）だけなら `tx-sysmap-fit.py`（冪等・
  本文不変）で直して再検証＝claude -p を使わない（`--fix-safe`）。
- **T/R との二重処理なし**：F が直る前に他ストリームが同番号を拾うことはない（破損品は T/R から不可視・
  直列実行・修復完了後は通常の SKIP 判定に戻る）。

## 二台同時 TJR の衝突対策（claim 予約・first-push-wins・2026-07-27）

**背景**：T/J/R の対象選定は決定論的（T=フロンティア最若番・R=旧版番号順・J=未生成最若番）なので、
2 台が同時に TJR を始めると**同じ問題を選び**、生成 20〜35 分（JX は 1〜2 時間）を二重消費した上で
push が衝突する。さらに旧実装は push 衝突時の素の `pull --rebase` が同一ファイル add/add で**途中停止
したまま次問へ進み、以降の全 commit が unmerged paths で失敗する連鎖**があった。対策は三層：

1. **claim 予約（`scripts/tjr-claim.ps1`・T/J/R/F 全ストリーム）**：各問の生成前に
   `locks/claims/{問題ID}.json`（PC名・UTC時刻・ストリーム・TTL）を commit→push して番号を原子的に
   予約する（GitHub の push 直列化を分散ロックに使う）。先取りされていたら `[SKIP-CLAIMED]`、
   リモートに成果物が既に在れば `[SKIP-REMOTE]` で**次候補へ繰り上げ**（着手数 quota は維持＝
   2 台が交互に番号を取り合って前進する。例：A が 49 を取れば B は 50 へ）。
   - **解放**：TX は完成 commit に claim 削除を同梱（1 push で完結）。JX は ⑦ finalize の commit に同梱。
     生成/検証失敗時は明示解放（`Release-TjrClaim`）。
   - **TTL**：TX=150 分／JX=600 分（バッチ全体を覆う）。**失効 claim は他 PC が引き継ぎ可**＋TJR が
     毎バッチ先頭で掃除（`Clear-TjrStaleClaims`）＝クラッシュした PC が番号を永久占有しない。
   - **オフライン**：リモート到達不可なら予約なしで続行（単機運転を止めない。最終網は下記 2）。
   - R(a) は claim の前に**リモート _lex が既に v13 か**を直接確認して `[SKIP-REMOTE]`（相手が再生成済み）。
2. **安全 push（`Invoke-TjrSafePush`・first-push-wins）**：push 拒否 → `pull --rebase -X ours`
   （rebase 中の ours=upstream＝**同一ファイル衝突はリモート先着版を採用・自分の commit は空化して
   自動 drop**）→ 再 push。`-X` で解決できない競合（claim の modify/delete 等）は必ず
   `git rebase --abort` で復帰して commit をローカル保持＝**rebase 途中放置の禁止**（連鎖 commit
   失敗の根絶）。置換済みの push 経路＝tx-v13-runner／TJR-F（回収コミット）／jx-finalize ③／
   rx-arb-autofill。起動時・毎バッチ頭にも同追随（`Sync-TjrRepo`）を入れ、pull を怠った側が相手の
   生成済み番号を「未生成」と誤認する事故経路も塞いだ。
3. **夜間タスクの時差**（`register-tjr-night-task.ps1 -StaggerMinutes`）：AUTO＝xnrg2 PC
   （DESKTOP-5664QR6）のみ +60 分（21:00→22:00 …）。同時刻起動そのものを減らす運用緩和
   （claim は保険に回る）。**反映には各 PC でタスクの再登録が必要**。

- 番号帯の手動分割（`-TxFrom/-TxTo` を PC で分ける旧運用）は**不要になったが併用可**（claim と両立）。
- F の「回収コミット」（未コミット残骸）はその PC のローカルにしか無いので claim 不要（push は安全 push）。
- ストリームの科目自動充当は claim を見ない＝両 PC が同科目を選ぶことはあるが、問題単位で交互に
  取り合うため二重生成にはならない。
- 検証：2 クローン＋bare リポジトリで claim 競走（add/add→先着勝ち）・同一成果物衝突（-X ours で
  先着版採用＋敗者 commit 自動 drop）・modify/delete（rebase 停止→abort 復帰）を実測確認済み。

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

## 入力の取り込み（PC 間セットアップ・Drive→ローカル）

**入力 PDF と講義逐語は `.gitignore` 対象**（2026-07-09 方針転換・CLAUDE.md §4-5-bis）なので、
`git pull` では降りてこない。**新しい PC／未取込の科目では、まず Drive から取り込まないと
TJR-T・TJR-J が「該当なし」で永久にスキップされる**（実害＝xnrg2 PC で民法以降の T/J が
ずっと空振り・2026-08-15 に導線を新設して解消）。

```powershell
# TX 入力（1問1PDF）: Drive「1 TX_短 答\{00N_科目}\抽出PDF\」→ inputs\000_TX\{00N_科目}\
pwsh -NoProfile -File scripts/tx-pull-inputs-from-drive.ps1            # 全科目
pwsh -NoProfile -File scripts/tx-pull-inputs-from-drive.ps1 -Subject 民
pwsh -NoProfile -File scripts/tx-pull-inputs-from-drive.ps1 -DryRun    # コピーせず確認

# JX 入力（重問PDF＋講義逐語）: Drive「2 JX_論 文\{00N_科目}\{重問PDF,講義逐語}\」→ inputs\001_JX\…
pwsh -NoProfile -File scripts/jx-pull-inputs-from-drive.ps1            # 全科目
pwsh -NoProfile -File scripts/jx-pull-inputs-from-drive.ps1 -Subject 民
```

- どちらも **Drive マウント先を自動検出**・**既存ファイルはスキップ（冪等・ローカル優先）**・
  **一方向（Drive→ローカル・ローカルの余剰は消さない）**。上書きは `-Force`。
- TX 側は **ステム全体が数字の 1問1PDF だけ**を取り込む。分割前の原本
  （`2026 短答過去問パーフェクト民法1.pdf` 等）は数字始まりでも取り込まない＝
  番号抽出 `^\d+` が 2026 を拾って `民TX2026` を生成する事故を防ぐため（原本は
  `-IncludeSource` で `_原本\` へ）。`抽出PDF` に 1問1PDF が無い科目で `別PDF` 等の
  別系統がある場合は件数だけ報告し、既定では取り込まない（番号体系不明のため・`-IncludeAlt`）。
- **Drive 側が未分割なら取り込むものが無い**（2026-08-15 時点：TX は刑法 445・民法 150 のみ。
  商法・民訴・行政法・憲法の TX は Drive にも 1問1PDF が無い＝分割待ち）。
- JX は取り込み後、`逐語-PDF対応表.md`（git 管理＝pull 済み）の番号規則で同番号ペアリングされる。

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
