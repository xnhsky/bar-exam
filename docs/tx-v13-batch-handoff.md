# TX v13 移行・刑訴新規生成 引継ぎ（ローカルPC バッチ）

> 2026-07-04 リモートセッションで整備。以降の実行はローカルPC（VS Code CC / CLI CC・Drive マウント側）。
> ブランチ `claude/problem-display-layout-n5dvph` に整備済み。**回す前に必ず本線を pull**（二台運用・§8）。

## 0. まず取得（毎回）

```
git fetch origin
git checkout claude/problem-display-layout-n5dvph   # or master へマージ後 master で
git pull
```

## 1. 全体像（刑法TX _lex・全362問／2026-07-04 実測）

| 区分 | 問数 | 備考 |
|---|---|---|
| v13 最新（`getInlineAnswerTablePanel` 有） | 36 | 済 |
| 旧レイアウト（要移行） | 326 | |
| └ PDF が inputs に有＝即バッチ可 | 190 | 番号帯 55〜330・`docs/tx-v13-migration-targets.md` |
| └ PDF が Drive のみ＝復元要 | 136 | 若い76＋前線60 |

**学習の前線 360〜445 は全86問 _lex 既存**（新規生成不要）。うち旧レイアウト60問・**PDFは inputs に0**（全て Drive のみ）。
刑訴（002_刑事訴訟法）は **PDF 334件・_lex 0**＝完全新規生成。

## 2. やること（ユーザー指示の順序）

### ① まず 360〜445 を v13 アップデート
PDF が inputs に無いので、先に Drive の「抽出PDF」から復元 → v13 バッチ。

```
# 1) PDF 復元（dry-run → 実コピー）
pwsh -NoProfile -File scripts\tx-restore-pdfs.ps1 -FromNumber 360 -ToNumber 445
pwsh -NoProfile -File scripts\tx-restore-pdfs.ps1 -FromNumber 360 -ToNumber 445 -Apply

# 2) v13 移行バッチ（旧60問だけ pending で拾われる・v13済26問は冪等スキップ）
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -FromNumber 360 -ToNumber 445 -MaxProblems 86 -SpecVersion v13
```

### ② 若い190を裏バッチで回しつつ、刑訴を新規生成（並行）

**若い190（PDF有）**＝`docs/tx-v13-migration-targets.md` の連続レンジを順に：
```
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -FromNumber 65  -ToNumber 84  -MaxProblems 20 -SpecVersion v13
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -FromNumber 126 -ToNumber 173 -MaxProblems 48 -SpecVersion v13
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -FromNumber 175 -ToNumber 217 -MaxProblems 43 -SpecVersion v13
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -FromNumber 219 -ToNumber 255 -MaxProblems 37 -SpecVersion v13
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -FromNumber 257 -ToNumber 289 -MaxProblems 33 -SpecVersion v13
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -FromNumber 324 -ToNumber 330 -MaxProblems 7  -SpecVersion v13
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -Number 55  -SpecVersion v13
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -Number 303 -SpecVersion v13
```

**刑訴の新規生成**（別PC or 別時間帯で並行推奨・v13 二系統）：
```
pwsh -NoProfile -File scripts\patterns\TX-PICK.ps1 -Subject 刑訴 -FromNumber 1 -ToNumber 20 -MaxProblems 20 -SpecVersion v13
```
- 刑訴は _lex 0 なので全番号が pending＝そのまま新規生成される。新規は1問20〜30分と重い。
- PDF は inputs/000_TX/002_刑事訴訟法 に334件あるので復元不要。
- 二台運用は番号帯を分けて並行（PC-A 1-30／PC-B 31-60 等・§8）。

### ③（後回し）PDF無しの若い76＋前線は復元してから
```
pwsh -NoProfile -File scripts\tx-restore-pdfs.ps1 -FromNumber 55 -ToNumber 359 -Apply   # 欠落分だけ復元
# その後 TX-PICK -SpecVersion v13 のレンジで消化
```

## 3. 今回リモートで整備したもの（このブランチに含む）

- **`prompts/new-tx-headless-v13.md`**（新規）… v13 headless プロンプト（GENESIS-CARD 複製→空化→鋳造・○×再枠組み gold=刑TX125・display スクリプト適用・両ファイル検証・commit/push・sentinel）。
- **`scripts/night-batch-runner.ps1`** … `-SpecVersion v13` と `-Subject`（7科目）を追加。**既定 v10.0.0・刑 は不変**。
  - v13 pending 判定＝`_lex` が `getInlineAnswerTablePanel` を持たない問（未移行/未生成）のみ拾う＝冪等。
  - v13 は入力 PDF を削除しない（再移行のため保持）。監査は outputs 全体（_lex 含む）。
- **`scripts/patterns/TX-PICK.ps1`** … `-SpecVersion` / `-Subject` 透過。
- **`scripts/tx-restore-pdfs.ps1`**（新規）… Drive「抽出PDF」→ inputs 復元（既定 dry-run・`-Apply` で実行）。

## 4. 注意・ゲート

- **v13 完了条件**＝`_lex` が G1〜G45＋G50 で ERROR0/WARNING0、公式は ERROR0。プロンプト Section 7 が自走検証。
- **内容レビュー**＝執筆者本人が1回自己照合＋機械ゲート（CLAUDE.md §3 省エネ規律）。判例の非著名/下級審だけ Web 一次確認。
- **永続化**＝各問 commit/push（プロンプト Section 8）。素の git commit でも pre-commit フックで作成日時スタンプが入る（§9）。
- **ps1 が文字化けする場合**＝BOM 付き UTF-8 で保存し直す（pwsh 7.6.x 想定・runner 冒頭コメント参照）。
- **Drive 未マウント**なら `tx-restore-pdfs.ps1` は中断（バックアップ無き復元をしない安全側）。

## 5. 未対応・保留

- 他科目（民/商/民訴/行政/憲）の TX 生成も `-Subject` で回せる状態だが、入力 PDF の在庫・番号整合は未確認。
- 刑訴の新規生成は v13 プロンプトで動くが、**刑訴1問目の gold 見本は未確定**（刑法は 刑TX125）。最初の数問を目視確認してから量産推奨。
