# v13v-runner.ps1 — TJR-S（§v13v「📖 ものがたり」付随・特別枠）エンジン（2026-08-22 新設）
#   正誤表の各記述に data-brief-story（物語全体＋当該記述の要約＋具体例）が未執筆の `_lex` を、
#   **2 レーン並行**（2026-08-31 ユーザー指示）で若番から headless（claude -p）で執筆 →
#     ①これから学習する科目レーン＝**刑訴101以降 → 民法 → 民訴 → 商法 → 憲法 → 行政法**（MaxProblems 件）
#     ②学習済みの過去分レーン＝**刑法（全番号）→ 刑訴073 以下**（MaxKeiho 件・既定 10）
#     学習の区切りは刑訴TX074。両レーンを毎バッチ同時に流す。
#   validate-tx-core／check-tx-lex-engine PASS 時のみ 1 問ずつ git commit/push する。
#   土台（TX-VERDICT-STORY の CSS＋appendStoryLine）が無いファイルは、実行前に決定論ツール
#   scripts/tx-lex-verdict-redesign.py で注入してから執筆させる（刑法は未伝播のためここで入る）。
#   残件ゼロ＝「該当なし」で即終了（過渡ストリーム＝完遂で消滅）。
#   正典：docs/v13v-handover.md（レシピ）／docs/run-patterns.md（S 節）。プロンプト：prompts/v13v-headless.md。
#   二台衝突対策：tjr-claim（予約 ID = {問題ID}_v13v・リモート版が既に執筆済みなら SKIP）。
param(
    [int]$MaxProblems = 10,            # 学習科目レーンの 1 バッチ件数（既定 10）
    [int]$MaxKeiho = 10,               # 過去分レーン（刑法→刑訴073以下）の 1 バッチ件数（既定 10・ユーザー指示 2026-08-31）
    [ValidateSet('', '刑訴', '民法', '民訴', '商法', '憲法', '行政法', '刑法')]
    [string]$Subject = '',             # 空＝2 レーン並行／明示時はその科目だけを流す
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [string]$Model = 'claude-opus-5',  # Q と同じく Opus 5 固定
    [switch]$Rewrite,                  # 旧型（出題構造型・2026-08-27 以前）の data-brief-story を新型へ書き直す
    [switch]$NoPush,
    [switch]$NoCommit,
    [switch]$DryRun,
    [string]$ProjectRoot = ''
)

$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

. (Join-Path $ProjectRoot 'scripts\tjr-claim.ps1')

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# === 科目レーン（ユーザー指示 2026-08-31）=========================================
# 学習の区切り＝**刑訴TX074 まで学習済み**。これを境に 2 レーンへ振り分ける。
# レーン①「これから学習する科目」＝**刑訴101 以降** → ③民法 → ④民訴 → ⑤商法 → ⑥憲法 → ⑦行政法。
#   （刑訴074-100 は 2026-08-31 に §v13w で執筆済みのため、この帯の残りは 101 以降になる）
# レーン②「学習済みの過去分」＝**刑法（全番号）→ 刑訴073 以下**。刑法を先に潰し、尽きたら刑訴の
#   若い帯へフォールスルーする。毎バッチ MaxKeiho 件（既定 10）をレーン①と並行して流す。
# Min/Max は科目ごとの番号境界（0＝制限なし）。-FromNumber/-ToNumber は全体にさらに掛かる。
$LearningOrder = @(
    [pscustomobject]@{ Key = '刑訴';   Rel = 'outputs/ux/000_TX/002_刑事訴訟法'; Prefix = '刑訴TX'; Min = 101; Max = 0 },
    [pscustomobject]@{ Key = '民法';   Rel = 'outputs/ux/000_TX/003_民法';       Prefix = '民TX';   Min = 0;   Max = 0 },
    [pscustomobject]@{ Key = '民訴';   Rel = 'outputs/ux/000_TX/005_民事訴訟法'; Prefix = '民訴TX'; Min = 0;   Max = 0 },
    [pscustomobject]@{ Key = '商法';   Rel = 'outputs/ux/000_TX/004_商法';       Prefix = '商TX';   Min = 0;   Max = 0 },
    [pscustomobject]@{ Key = '憲法';   Rel = 'outputs/ux/000_TX/007_憲法';       Prefix = '憲TX';   Min = 0;   Max = 0 },
    [pscustomobject]@{ Key = '行政法'; Rel = 'outputs/ux/000_TX/006_行政法';     Prefix = '行政TX'; Min = 0;   Max = 0 }
)
$KeihoLane = @(
    [pscustomobject]@{ Key = '刑法'; Rel = 'outputs/ux/000_TX/001_刑法';         Prefix = '刑TX';   Min = 0; Max = 0 },
    [pscustomobject]@{ Key = '刑訴'; Rel = 'outputs/ux/000_TX/002_刑事訴訟法';   Prefix = '刑訴TX'; Min = 0; Max = 73 }
)
if ($Subject) {
    # -Subject 明示時は番号境界も外す（その科目を全番号あたる）。刑訴は両レーンに現れるため、
    # 学習レーン側だけを残して二重計上を避ける。
    $LearningOrder = @($LearningOrder | Where-Object { $_.Key -eq $Subject } |
                       ForEach-Object { $_.Min = 0; $_.Max = 0; $_ })
    $KeihoLane     = @($KeihoLane     | Where-Object { $_.Key -eq $Subject } |
                       ForEach-Object { $_.Min = 0; $_.Max = 0; $_ })
    if ($LearningOrder.Count -gt 0) { $KeihoLane = @() }
    elseif ($KeihoLane.Count -gt 0) { $MaxKeiho = $MaxProblems }
}

$PromptFile  = Join-Path $ProjectRoot 'prompts\v13v-headless.md'
$ValidatePy  = Join-Path $ProjectRoot 'scripts\validate-tx-core.py'
$EnginePy    = Join-Path $ProjectRoot 'scripts\check-tx-lex-engine.py'
$BasePy      = Join-Path $ProjectRoot 'scripts\tx-lex-verdict-redesign.py'
$LedgerPath  = Join-Path $ProjectRoot 'logs\v13v-ledger.json'
$ReportPath  = Join-Path $ProjectRoot 'logs\tjr-repair-report.md'
foreach ($p in @($PromptFile, $ValidatePy, $EnginePy, $BasePy)) {
    if (-not (Test-Path $p)) { Write-Host "[S] 前提ファイル不在: $p" -ForegroundColor Red; exit 1 }
}
if (-not (Test-Path (Join-Path $ProjectRoot 'logs'))) { New-Item -ItemType Directory -Path (Join-Path $ProjectRoot 'logs') | Out-Null }

# === 失敗台帳（同一問題 2 回失敗で ESCALATE＝以後スキップ・Q/F と同じ無限再挑戦防止）===
function Read-SLedger {
    if (Test-Path $LedgerPath) { try { return (Get-Content -Raw -Encoding UTF8 $LedgerPath | ConvertFrom-Json -AsHashtable) } catch { } }
    return @{}
}
function Save-SLedger { param($Ledger)
    $Ledger | ConvertTo-Json -Depth 4 | Out-File -FilePath $LedgerPath -Encoding utf8
}

# === 旧型判定（2026-08-31 §v13w 対応）===
#   ①3枚化されていない（⚙ IN PRACTICE の .tx-vb-prac が無い）＝§v13w 以前 → 旧型。
#   ②地の文（practice / CASE FILE を除いた本体）が 200 字未満＝2026-08-27 以前の出題構造型 → 旧型。
#   1 行でも該当すればそのファイルを旧型とみなす。
function Test-V13vLegacy {
    param([string]$Path)
    $raw = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
    foreach ($m in [regex]::Matches($raw, 'data-brief-story="([^"]*)"')) {
        $body = $m.Groups[1].Value
        if ($body -notmatch "tx-vb-prac") { return $true }
        foreach ($cls in @("tx-vb-prac", "tx-vb-ex")) {
            $i = $body.IndexOf("<span class='$cls'")
            if ($i -ge 0) { $body = $body.Substring(0, $i) }
        }
        $body = [regex]::Replace($body, '<[^>]+>', '')
        if ($body.Length -lt 200) { return $true }
    }
    return $false
}

# === 対象検出：data-brief-story を 1 つも持たない `_lex`（科目優先順→若番）===
#   正誤表（statement-verdict-table）が無いファイルは対象外（ものがたり帯の置き場所が無い）。
function Get-STargets {
    param([object[]]$Subjects)
    $items = @()
    foreach ($subj in $Subjects) {
        $dir = Join-Path $ProjectRoot ($subj.Rel -replace '/', '\')
        if (-not (Test-Path $dir)) { continue }
        Get-ChildItem -LiteralPath $dir -Filter '*_lex.html' | ForEach-Object {
            $m = [regex]::Match($_.Name, 'TX(\d+)_lex\.html$')
            if (-not $m.Success) { return }
            $n = [int]$m.Groups[1].Value
            if ($FromNumber -gt 0 -and $n -lt $FromNumber) { return }
            if ($ToNumber   -gt 0 -and $n -gt $ToNumber)   { return }
            if ($subj.Min   -gt 0 -and $n -lt $subj.Min)   { return }   # レーンごとの番号境界
            if ($subj.Max   -gt 0 -and $n -gt $subj.Max)   { return }
            if (-not (Select-String -LiteralPath $_.FullName -Pattern 'statement-verdict-table' -Quiet)) { return }
            $hasStory = Select-String -LiteralPath $_.FullName -Pattern 'data-brief-story=' -Quiet
            if ($Rewrite) {
                if (-not $hasStory) { return }
                if (-not (Test-V13vLegacy -Path $_.FullName)) { return }
            } elseif ($hasStory) { return }
            $items += [pscustomobject]@{
                Subject = $subj.Key; Num = $n; Name = $_.Name; Abs = $_.FullName
                Rel = "$($subj.Rel)/$($_.Name)"; Id = ('{0}{1:d3}' -f $subj.Prefix, $n)
            }
        }
    }
    # 科目はレーン内の並びを保ったまま、科目内は若番順
    $rank = @{}
    for ($i = 0; $i -lt $Subjects.Count; $i++) { $rank[$Subjects[$i].Key] = $i }
    return @($items | Sort-Object @{Expression = { $rank[$_.Subject] } }, Num)
}

if (-not $DryRun) { [void](Sync-TjrRepo -ProjectRoot $ProjectRoot) }

# 2 レーンを別々に集め、それぞれの上限で切ってから合流する（刑法がレーン①を押し出さない）
$learnTargets = if ($LearningOrder.Count) { @(Get-STargets -Subjects $LearningOrder) } else { @() }
$keihoTargets = if ($KeihoLane.Count)     { @(Get-STargets -Subjects $KeihoLane)     } else { @() }
$targets = @($learnTargets) + @($keihoTargets)
if ($targets.Count -eq 0) {
    Write-Host $(if ($Rewrite) { "[S] 該当なし＝旧型のものがたり帯は残っていない（-Rewrite）" } else { "[S] 該当なし＝§v13v 特別枠は完遂（対象科目の全 _lex にものがたり帯あり）" }) -ForegroundColor Green
    exit 0
}
$ledgerSuffix = if ($Rewrite) { '#rw' } else { '' }
$ledger = Read-SLedger
$notEscalated = { param($x) [int]($ledger["$($x.Id)$ledgerSuffix"] ?? 0) -lt 2 }
$learnQueue = @($learnTargets | Where-Object { & $notEscalated $_ } | Select-Object -First $MaxProblems)
$keihoQueue = @($keihoTargets | Where-Object { & $notEscalated $_ } | Select-Object -First $MaxKeiho)
$queue = @($learnQueue) + @($keihoQueue)
$escalated = @($targets | Where-Object { [int]($ledger["$($_.Id)$ledgerSuffix"] ?? 0) -ge 2 })
$byS = ($targets | Group-Object Subject | ForEach-Object { "$($_.Name) $($_.Count)" }) -join ' / '
Write-Host ("[S] 残 {0} 件（{1}）（ESCALATE 済 {2} 件）／今バッチ {3} 件＝学習レーン {4}＋過去分レーン {5}（model={6}）" -f `
    $targets.Count, $byS, $escalated.Count, $queue.Count,
    $learnQueue.Count, $keihoQueue.Count, $Model) -ForegroundColor Cyan
if ($queue.Count -eq 0) {
    Write-Host "[S] 残件は全て ESCALATE 済（logs\tjr-repair-report.md 参照）。人手判断待ち。" -ForegroundColor Yellow
    exit 0
}
if ($DryRun) {
    $queue | ForEach-Object { Write-Host ("  [DRY] {0} {1}" -f $_.Id, $_.Rel) }
    exit 0
}

$promptTemplate = Get-Content -Raw -Encoding UTF8 $PromptFile
$rcAll = 0
foreach ($t in $queue) {
    Write-Host "`n———— S: $($t.Id) （$($t.Rel)）————" -ForegroundColor Green

    # 二台衝突：リモート版が既に執筆済みなら pull 追随して SKIP
    if (-not $Rewrite -and (Test-TjrRemoteContent -ProjectRoot $ProjectRoot -RelPath $t.Rel -Pattern 'data-brief-story=')) {
        Write-Host "[S] $($t.Id) はリモートで執筆済み → pull 追随して SKIP" -ForegroundColor Yellow
        [void](Invoke-TjrSafePull -ProjectRoot $ProjectRoot)
        continue
    }
    $claim = Request-TjrClaim -ProjectRoot $ProjectRoot -ProblemId "$($t.Id)$(if ($Rewrite) { '_v13v2' } else { '_v13v' })" -Stream 'S'
    if ($claim -notin @('CLAIMED','CLAIMED_OFFLINE')) {
        Write-Host "[S] $($t.Id) claim=$claim → SKIP（次バッチで再判定）" -ForegroundColor Yellow
        continue
    }

    # 土台（CSS＋エンジン）が無ければ決定論ツールで先に注入（刑法は未伝播）
    if (-not (Select-String -LiteralPath $t.Abs -Pattern 'TX-VERDICT-STORY:BEGIN' -Quiet)) {
        Write-Host "[S] $($t.Id) 土台なし → tx-lex-verdict-redesign.py で注入"
        & python -X utf8 $BasePy $t.Abs 2>&1 | Out-Host
    }

    $prompt = $promptTemplate.Replace('{FILE}', $t.Rel)
    if ($Rewrite) {
        $prompt = $prompt + "`n`n## 今回は旧型の書き直し（-Rewrite）`n" +
            "対象ファイルには旧型（出題構造型、または §v13w 以前の1枚もの）の data-brief-story が既に入っている。" +
            "全記述を新型（体系・趣旨・コツ・実務＋具体例）で書き直し、注入は必ず --force を付けて実行する" +
            "（python -X utf8 scripts/v13v-inject.py " + $t.Rel + " <payload> --force）。" +
            "--force なしでは既存行がスキップされ、旧型が残る。`n"
    }
    $claudeArgs = @('-p','--model',$Model,'--output-format','json','--permission-mode','acceptEdits','--allowedTools','Write,Edit,Read,Bash,Glob,Grep')
    Write-Host "[S] claude -p 起動中（推定 5-10 分）..."
    Push-Location $ProjectRoot
    try { $out = $prompt | & claude @claudeArgs 2>&1; $code = $LASTEXITCODE } catch { $out = "$_"; $code = -1 }
    finally { Pop-Location }

    # === ランナー側の決定論検証（agent の自己申告に依存しない）===
    #   ものがたり帯は「全記述に入って初めて完成」＝行数と data-brief-story 数の一致を要求する。
    $rows  = @(Select-String -LiteralPath $t.Abs -Pattern '<tr data-stmt="' -AllMatches | ForEach-Object { $_.Matches.Count } | Measure-Object -Sum).Sum
    $story = @(Select-String -LiteralPath $t.Abs -Pattern 'data-brief-story=' -AllMatches | ForEach-Object { $_.Matches.Count } | Measure-Object -Sum).Sum
    if ($null -eq $rows)  { $rows = 0 }
    if ($null -eq $story) { $story = 0 }
    $ok = $false
    if ($rows -gt 0 -and $story -ge $rows) {
        & python $ValidatePy $t.Abs 2>&1 | Out-Null; $v1 = $LASTEXITCODE
        & python $EnginePy   $t.Abs 2>&1 | Out-Null; $v2 = $LASTEXITCODE
        $ok = ($v1 -eq 0 -and $v2 -eq 0)
        Write-Host ("[S] 検証 rows={0} story={1} validate={2} engine={3}" -f $rows, $story, $v1, $v2)
    } else {
        Write-Host "[S] $($t.Id) 執筆痕が足りない（rows=$rows story=$story・claude exit=$code）" -ForegroundColor Yellow
    }

    if ($ok) {
        if ($NoCommit) {
            Write-Host "[S] $($t.Id) PASS（-NoCommit のため作業ツリーに保持）" -ForegroundColor Green
        } else {
            & git -C $ProjectRoot add -- $t.Rel
            & git -C $ProjectRoot commit -m $(if ($Rewrite) { "feat($($t.Id)): 📖CONTEXT帯を3枚化＋実名CASE FILEへ改訂（§v13w・TJR-S）" } else { "feat($($t.Id)): 正誤表に📖CONTEXT帯を執筆（§v13v/§v13w・TJR-S）" }) 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                if (-not $NoPush) { [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "S $($t.Id)") }
                Write-Host "[S] $($t.Id) commit 完了" -ForegroundColor Green
            } else {
                Write-Host "[S] $($t.Id) commit 失敗" -ForegroundColor Red; $rcAll = 1
            }
        }
        if ($ledger.ContainsKey("$($t.Id)$ledgerSuffix")) { $ledger.Remove("$($t.Id)$ledgerSuffix"); Save-SLedger $ledger }
    } else {
        # 失敗＝部分状態を残さない（土台注入ごと戻す）
        & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
        $s = [int]($ledger["$($t.Id)$ledgerSuffix"] ?? 0) + 1
        $ledger["$($t.Id)$ledgerSuffix"] = $s
        Save-SLedger $ledger
        Write-Host "[S] $($t.Id) 失敗（strike $s/2）→ ロールバック" -ForegroundColor Yellow
        if ($s -ge 2) {
            $line = "- ESCALATE(S) $($t.Id): §v13v ものがたり執筆が 2 回失敗（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。人手または個別セッションで対応。"
            Add-Content -Path $ReportPath -Value $line -Encoding utf8
            Write-Host "[S] $($t.Id) ESCALATE（logs\tjr-repair-report.md）" -ForegroundColor Red
        }
        $rcAll = 1
    }
    Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId "$($t.Id)$(if ($Rewrite) { '_v13v2' } else { '_v13v' })" -Reason $(if ($ok) { '完了' } else { '失敗' }) -NoPush:$NoPush
}

$remain = (Get-STargets).Count
Write-Host "`n[S] バッチ終了 exit=$rcAll 残=$remain 件" -ForegroundColor Cyan
exit $rcAll
