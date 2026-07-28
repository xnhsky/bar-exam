# v13q-runner.ps1 — TJR-Q（§v13q 付随・特別枠）エンジン（2026-07-28 新設）
#   刑訴TX の既存 _lex のうち答案圧縮（tx-anscomp-line）未展開の残件を、若番から MaxProblems 件ずつ
#   headless（claude -p）で §v13q 改訂 → validate-tx-core／check-tx-lex-engine PASS 時のみ
#   1 問ずつ git commit/push する。残件ゼロ＝「該当なし」で即終了（過渡ストリーム＝完遂で消滅）。
#   正典：docs/v13q-handover.md（レシピ）／docs/run-patterns.md（Q 節）。プロンプト：prompts/v13q-headless.md。
#   二台衝突対策：tjr-claim（予約 ID = {問題ID}_v13q・リモート版が既に改訂済みなら SKIP）。
param(
    [int]$MaxProblems = 10,          # 1 バッチの処理件数（TJR 特別枠の既定＝10）
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [string]$Model = 'claude-opus-5',  # ユーザー指定（2026-07-28）＝Opus 5 固定。変更はこのパラメータで
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

$SubjRel     = 'outputs/ux/000_TX/002_刑事訴訟法'
$SubjDir     = Join-Path $ProjectRoot ($SubjRel -replace '/', '\')
$PromptFile  = Join-Path $ProjectRoot 'prompts\v13q-headless.md'
$ValidatePy  = Join-Path $ProjectRoot 'scripts\validate-tx-core.py'
$EnginePy    = Join-Path $ProjectRoot 'scripts\check-tx-lex-engine.py'
$LedgerPath  = Join-Path $ProjectRoot 'logs\v13q-ledger.json'
$ReportPath  = Join-Path $ProjectRoot 'logs\tjr-repair-report.md'
foreach ($p in @($SubjDir, $PromptFile, $ValidatePy, $EnginePy)) {
    if (-not (Test-Path $p)) { Write-Host "[Q] 前提ファイル不在: $p" -ForegroundColor Red; exit 1 }
}
if (-not (Test-Path (Join-Path $ProjectRoot 'logs'))) { New-Item -ItemType Directory -Path (Join-Path $ProjectRoot 'logs') | Out-Null }

# === 失敗台帳（同一問題 2 回失敗で ESCALATE＝以後スキップ・F と同じ無限再挑戦防止）===
function Read-QLedger {
    if (Test-Path $LedgerPath) { try { return (Get-Content -Raw -Encoding UTF8 $LedgerPath | ConvertFrom-Json -AsHashtable) } catch { } }
    return @{}
}
function Save-QLedger { param($Ledger)
    $Ledger | ConvertTo-Json -Depth 4 | Out-File -FilePath $LedgerPath -Encoding utf8
}

# === 対象検出：tx-anscomp-line を持たない 刑訴TX _lex（若番から）===
function Get-QTargets {
    $items = @()
    Get-ChildItem -LiteralPath $SubjDir -Filter '*_lex.html' | ForEach-Object {
        $m = [regex]::Match($_.Name, 'TX(\d+)_lex\.html$')
        if (-not $m.Success) { return }
        $n = [int]$m.Groups[1].Value
        if ($FromNumber -gt 0 -and $n -lt $FromNumber) { return }
        if ($ToNumber   -gt 0 -and $n -gt $ToNumber)   { return }
        if (Select-String -LiteralPath $_.FullName -Pattern 'tx-anscomp-line' -Quiet) { return }
        $items += [pscustomobject]@{ Num = $n; Name = $_.Name; Abs = $_.FullName; Rel = "$SubjRel/$($_.Name)" }
    }
    return @($items | Sort-Object Num)
}

if (-not $DryRun) { [void](Sync-TjrRepo -ProjectRoot $ProjectRoot) }

$targets = Get-QTargets
if ($targets.Count -eq 0) {
    Write-Host "[Q] 該当なし＝§v13q 特別枠は完遂（刑訴TX の全 _lex に答案圧縮あり）" -ForegroundColor Green
    exit 0
}
$ledger = Read-QLedger
$queue = @($targets | Where-Object { [int]($ledger["$($_.Num)"] ?? 0) -lt 2 } | Select-Object -First $MaxProblems)
$escalated = @($targets | Where-Object { [int]($ledger["$($_.Num)"] ?? 0) -ge 2 })
Write-Host ("[Q] 残 {0} 件（ESCALATE 済 {1} 件）／今バッチ {2} 件を処理（model={3}）" -f $targets.Count, $escalated.Count, $queue.Count, $Model) -ForegroundColor Cyan
if ($queue.Count -eq 0) {
    Write-Host "[Q] 残件は全て ESCALATE 済（logs\tjr-repair-report.md 参照）。人手判断待ち。" -ForegroundColor Yellow
    exit 0
}
if ($DryRun) {
    $queue | ForEach-Object { Write-Host ("  [DRY] 刑訴TX{0:d3} {1}" -f $_.Num, $_.Rel) }
    exit 0
}

$promptTemplate = Get-Content -Raw -Encoding UTF8 $PromptFile
$rcAll = 0
foreach ($t in $queue) {
    $pid3 = '刑訴TX{0:d3}' -f $t.Num
    Write-Host "`n———— Q: $pid3 （$($t.Rel)）————" -ForegroundColor Green

    # 二台衝突：リモート版が既に改訂済みなら pull 追随して SKIP
    if (Test-TjrRemoteContent -ProjectRoot $ProjectRoot -RelPath $t.Rel -Pattern 'tx-anscomp-line') {
        Write-Host "[Q] $pid3 はリモートで改訂済み → pull 追随して SKIP" -ForegroundColor Yellow
        [void](Invoke-TjrSafePull -ProjectRoot $ProjectRoot)
        continue
    }
    $claim = Request-TjrClaim -ProjectRoot $ProjectRoot -ProblemId "${pid3}_v13q" -Stream 'Q'
    if ($claim -notin @('CLAIMED','CLAIMED_OFFLINE')) {
        Write-Host "[Q] $pid3 claim=$claim → SKIP（次バッチで再判定）" -ForegroundColor Yellow
        continue
    }

    $prompt = $promptTemplate.Replace('{FILE}', $t.Rel)
    $claudeArgs = @('-p','--model',$Model,'--output-format','json','--permission-mode','acceptEdits','--allowedTools','Write,Edit,Read,Bash,Glob,Grep')
    Write-Host "[Q] claude -p 起動中（推定 5-10 分）..."
    Push-Location $ProjectRoot
    try { $out = $prompt | & claude @claudeArgs 2>&1; $code = $LASTEXITCODE } catch { $out = "$_"; $code = -1 }
    finally { Pop-Location }

    # === ランナー側の決定論検証（agent の自己申告に依存しない）===
    $ok = $false
    $hasAns = Select-String -LiteralPath $t.Abs -Pattern 'tx-anscomp-line' -Quiet
    if ($hasAns) {
        & python $ValidatePy $t.Abs 2>&1 | Out-Null; $v1 = $LASTEXITCODE
        & python $EnginePy   $t.Abs 2>&1 | Out-Null; $v2 = $LASTEXITCODE
        $ok = ($v1 -eq 0 -and $v2 -eq 0)
        Write-Host ("[Q] 検証 anscomp={0} validate={1} engine={2}" -f $hasAns, $v1, $v2)
    } else {
        Write-Host "[Q] $pid3 注入痕なし（claude exit=$code）" -ForegroundColor Yellow
    }

    if ($ok) {
        if ($NoCommit) {
            Write-Host "[Q] $pid3 PASS（-NoCommit のため作業ツリーに保持）" -ForegroundColor Green
        } else {
            & git -C $ProjectRoot add -- $t.Rel
            & git -C $ProjectRoot commit -m "feat(${pid3}): §v13q 改訂（答案圧縮・GIST自己完結）（TJR-Q）" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                if (-not $NoPush) { [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "Q $pid3") }
                Write-Host "[Q] $pid3 commit 完了" -ForegroundColor Green
            } else {
                Write-Host "[Q] $pid3 commit 失敗" -ForegroundColor Red; $rcAll = 1
            }
        }
        if ($ledger.ContainsKey("$($t.Num)")) { $ledger.Remove("$($t.Num)") ; Save-QLedger $ledger }
    } else {
        # 失敗＝部分状態を残さない（§v13q 引き継ぎ規律）
        & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
        $s = [int]($ledger["$($t.Num)"] ?? 0) + 1
        $ledger["$($t.Num)"] = $s
        Save-QLedger $ledger
        Write-Host "[Q] $pid3 失敗（strike $s/2）→ ロールバック" -ForegroundColor Yellow
        if ($s -ge 2) {
            $line = "- ESCALATE(Q) ${pid3}: §v13q 改訂が 2 回失敗（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。人手または個別セッションで対応。"
            Add-Content -Path $ReportPath -Value $line -Encoding utf8
            Write-Host "[Q] $pid3 ESCALATE（logs\tjr-repair-report.md）" -ForegroundColor Red
        }
        $rcAll = 1
    }
    Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId "${pid3}_v13q" -Reason $(if ($ok) { '完了' } else { '失敗' }) -NoPush:$NoPush
}

$remain = (Get-QTargets).Count
Write-Host "`n[Q] バッチ終了 exit=$rcAll 残=$remain 件" -ForegroundColor Cyan
exit $rcAll
