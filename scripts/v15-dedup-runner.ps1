# v15-dedup-runner.ps1 — TJR-D（§v15 DEDUP＝罠枠の「1語差し替えで裏返る」比較表化・特別枠）エンジン（2026-09-22 新設）
#   §v15 未適用（罠枠に data-v15 が無い）の v13 `_lex` を、**仕事のある科目へ均等に配る**（ラウンドロビン・
#   docs/run-patterns.md「既存展開の配り方」）。1 バッチ MaxProblems 件を科目へ 1 本ずつ順に配り、科目内は若番から：
#     ① 土台（決定論）：scripts/tx-v15-dedup.py base → 変わればその場で commit（内容執筆なし・冪等）
#     ② headless（claude -p）：JSON 仕様（罠・比較表・フック・判定・転用）を執筆 → scripts/tx-v15-dedup.py apply で組む
#   合否はランナーが決定論で判定する（agent の自己申告に依存しない）：
#     ③ tx-v15-dedup.py check           … 構造・禁止語・比較表の上限・正誤表との複製一致
#     ④ tx-v15-dedup.py scope --spec    … git HEAD（＝①コミット後）と比べ §v15 の許可領域以外が不変／罠枠が仕様から組んだ HTML と一致
#     ⑤ tx-v15-dedup.py css --check     … TX-DGM 区画が正典と一致
#     ⑥ validate-tx-core ERROR 0 ／ ⑦ check-tx-lex-engine PASS（当該ファイルだけ＝TX_ENGINE_SKIP_CORPUS=1）
#   PASS のみ 1 問ずつ git commit/push。内容の FAIL はロールバック＋strike（同一問題 2 回で ESCALATE）、
#   連続 MaxConsecutiveFailures 件で打ち切り。headless が対象外の追跡ファイルを変えたら元に戻して FAIL。
#   claude が起動直後に死んだ（exit≠0 かつ何も変わっていない）ときは基盤障害として strike を付けずに即停止し exit 2。
#   対象判定の単一情報源＝`python -X utf8 scripts/tx-v15-dedup.py pending --json`。残件ゼロ＝「該当なし」で即終了。
#   正典：docs/tx-v12.2.1-inline-lock.md §v15／docs/run-patterns.md（D 節）。プロンプト：prompts/v15-dedup-headless.md。
#   二台衝突対策：tjr-claim（予約 ID = {問題ID}_v15d・リモート版が既に適用済みなら SKIP）。
#   -NoPush／-NoCommit のときは claim を取らない（claim は HEAD ごと push するため）。
param(
    [int]$MaxProblems = 10,
    [ValidateSet('', '刑訴', '民法', '民訴', '商法', '憲法', '行政法', '刑法')]
    [string]$Subject = '',
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [string]$Model = 'claude-opus-5',  # Q/S/G と同じく Opus 5 固定
    [int]$MaxConsecutiveFailures = 3,
    [switch]$CountOnly,
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

$SubjectOrder = @(
    [pscustomobject]@{ Key = '刑法';   Folder = '001_刑法';       Prefix = '刑TX' },
    [pscustomobject]@{ Key = '刑訴';   Folder = '002_刑事訴訟法'; Prefix = '刑訴TX' },
    [pscustomobject]@{ Key = '民法';   Folder = '003_民法';       Prefix = '民TX' },
    [pscustomobject]@{ Key = '民訴';   Folder = '005_民事訴訟法'; Prefix = '民訴TX' },
    [pscustomobject]@{ Key = '商法';   Folder = '004_商法';       Prefix = '商TX' },
    [pscustomobject]@{ Key = '憲法';   Folder = '007_憲法';       Prefix = '憲TX' },
    [pscustomobject]@{ Key = '行政法'; Folder = '006_行政法';     Prefix = '行政TX' }
)
if ($Subject) { $SubjectOrder = @($SubjectOrder | Where-Object { $_.Key -eq $Subject }) }

$PromptFile = Join-Path $ProjectRoot 'prompts\v15-dedup-headless.md'
$Tool       = Join-Path $ProjectRoot 'scripts\tx-v15-dedup.py'
$ValidatePy = Join-Path $ProjectRoot 'scripts\validate-tx-core.py'
$EnginePy   = Join-Path $ProjectRoot 'scripts\check-tx-lex-engine.py'
$LedgerPath = Join-Path $ProjectRoot 'logs\v15d-ledger.json'
$ReportPath = Join-Path $ProjectRoot 'logs\tjr-repair-report.md'
$SpecDir    = Join-Path $ProjectRoot 'logs\v15d-spec'
foreach ($p in @($PromptFile, $Tool, $ValidatePy, $EnginePy)) {
    if (-not (Test-Path $p)) { Write-Host "[D] 前提ファイル不在: $p" -ForegroundColor Red; exit 1 }
}
New-Item -ItemType Directory -Force -Path $SpecDir | Out-Null

function Read-DLedger {
    if (Test-Path $LedgerPath) { try { return (Get-Content -Raw -Encoding UTF8 $LedgerPath | ConvertFrom-Json -AsHashtable) } catch { } }
    return @{}
}
function Save-DLedger { param($Ledger)
    $Ledger | ConvertTo-Json -Depth 4 | Out-File -FilePath $LedgerPath -Encoding utf8
}
function Invoke-DPy { param([string[]]$PyArgs, [switch]$SkipCorpus)
    if ($SkipCorpus) { $env:TX_ENGINE_SKIP_CORPUS = '1' }
    try { $out = & python -X utf8 @PyArgs 2>&1; $code = $LASTEXITCODE }
    finally { if ($SkipCorpus) { Remove-Item Env:\TX_ENGINE_SKIP_CORPUS -ErrorAction SilentlyContinue } }
    return [pscustomobject]@{ Code = $code; Text = ($out | Out-String) }
}
function Get-DDirty {
    $lines = @(& git -C $ProjectRoot -c core.quotepath=false status --porcelain --untracked-files=no 2>$null)
    return @($lines | Where-Object { $_.Length -gt 3 } | ForEach-Object { ($_.Substring(3) -replace '^"|"$', '') })
}

function Get-DTargets {
    $r = Invoke-DPy @($Tool, 'pending', '--json', '--root', $ProjectRoot)
    if ($r.Code -ne 0) { Write-Host "[D] pending 取得に失敗: $($r.Text)" -ForegroundColor Red; return @() }
    $rels = @()
    try { $rels = @($r.Text | ConvertFrom-Json) } catch { Write-Host "[D] pending の JSON を読めない" -ForegroundColor Red; return @() }
    $items = @()
    foreach ($rel in $rels) {
        $parts = $rel -split '/'
        if ($parts.Count -lt 5) { continue }
        $subj = $SubjectOrder | Where-Object { $_.Folder -eq $parts[3] } | Select-Object -First 1
        if (-not $subj) { continue }
        $m = [regex]::Match($parts[4], 'TX(\d+)_lex\.html$')
        if (-not $m.Success) { continue }
        $n = [int]$m.Groups[1].Value
        if ($FromNumber -gt 0 -and $n -lt $FromNumber) { continue }
        if ($ToNumber   -gt 0 -and $n -gt $ToNumber)   { continue }
        $items += [pscustomobject]@{
            Subject = $subj.Key; Num = $n; Name = $parts[4]
            Abs = (Join-Path $ProjectRoot ($rel -replace '/', '\')); Rel = $rel
            Id = ('{0}{1:d3}' -f $subj.Prefix, $n)
        }
    }
    $rank = @{}
    for ($i = 0; $i -lt $SubjectOrder.Count; $i++) { $rank[$SubjectOrder[$i].Key] = $i }
    return @($items | Sort-Object @{Expression = { $rank[$_.Subject] } }, Num)
}

function Test-DResult { param($t, [string]$SpecPath)
    $c = Invoke-DPy @($Tool, 'check', $t.Abs)
    $s = Invoke-DPy @($Tool, 'scope', $t.Abs, '--spec', $SpecPath)
    $k = Invoke-DPy @($Tool, 'css', '--check', $t.Abs)
    $okCheck = ($c.Code -eq 0 -and $c.Text -match '(?m)^OK ')
    $okScope = ($s.Code -eq 0)
    $okCss   = ($k.Code -eq 0)
    $v1 = 1; $v2 = 1
    if ($okCheck -and $okScope -and $okCss) {
        $v1 = (Invoke-DPy @($ValidatePy, $t.Abs)).Code
        $v2 = (Invoke-DPy @($EnginePy, $t.Abs) -SkipCorpus).Code
    }
    Write-Host ("[D] 判定 check={0} scope={1} css={2} validate={3} engine={4}" -f `
        $(if ($okCheck) { 'OK' } else { 'NG' }), $(if ($okScope) { 'OK' } else { 'NG' }), $(if ($okCss) { 'OK' } else { 'NG' }), $v1, $v2)
    if (-not $okCheck) { Write-Host ($c.Text.Trim()) -ForegroundColor DarkYellow }
    if (-not $okScope) { Write-Host ($s.Text.Trim()) -ForegroundColor DarkYellow }
    if (-not $okCss)   { Write-Host ($k.Text.Trim()) -ForegroundColor DarkYellow }
    return ($okCheck -and $okScope -and $okCss -and $v1 -eq 0 -and $v2 -eq 0)
}

function Add-DStrike { param($Ledger, $t, [string]$Why)
    $s = [int]($Ledger[$t.Id] ?? 0) + 1
    $Ledger[$t.Id] = $s
    Save-DLedger $Ledger
    Write-Host "[D] $($t.Id) 失敗（strike $s/2）：$Why" -ForegroundColor Yellow
    if ($s -ge 2) {
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- ESCALATE(D) $($t.Id): §v15 DEDUP の書き換えが 2 回失敗（最後の理由：$Why・$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。人手または個別セッションで対応。"
        Write-Host "[D] $($t.Id) ESCALATE（logs\tjr-repair-report.md）" -ForegroundColor Red
    }
}

$useClaim = (-not $NoCommit -and -not $NoPush)
if (-not $DryRun -and -not $CountOnly -and $useClaim) { [void](Sync-TjrRepo -ProjectRoot $ProjectRoot) }

$targets = @(Get-DTargets)
$ledger = Read-DLedger
$actionable = @($targets | Where-Object { [int]($ledger[$_.Id] ?? 0) -lt 2 })
if ($CountOnly) { Write-Output $actionable.Count; exit 0 }

$scopeLabel = if ($Subject) { "（$Subject）" } else { '' }
if ($targets.Count -eq 0) {
    if ($Subject -or $FromNumber -gt 0 -or $ToNumber -gt 0) {
        Write-Host "[D]$scopeLabel 指定範囲に該当なし（他の科目・番号には残件があり得る）" -ForegroundColor Green
    } else {
        Write-Host "[D] 該当なし＝§v15 特別枠は完遂（未適用の v13 _lex は残っていない）" -ForegroundColor Green
    }
    exit 0
}
$pool = @{}
foreach ($t in $actionable) {
    if (-not $pool.ContainsKey($t.Subject)) { $pool[$t.Subject] = New-Object System.Collections.ArrayList }
    [void]$pool[$t.Subject].Add($t)
}
$rrOrder = @($SubjectOrder | Where-Object { $pool.ContainsKey($_.Key) } | ForEach-Object { $_.Key })
$cursor = @{}; foreach ($k in $rrOrder) { $cursor[$k] = 0 }
$queue = @()
while ($queue.Count -lt $MaxProblems) {
    $added = $false
    foreach ($k in $rrOrder) {
        if ($queue.Count -ge $MaxProblems) { break }
        $list = $pool[$k]
        if ($cursor[$k] -lt $list.Count) { $queue += $list[$cursor[$k]]; $cursor[$k]++; $added = $true }
    }
    if (-not $added) { break }
}
$byS = ($targets | Group-Object Subject | ForEach-Object { "$($_.Name) $($_.Count)" }) -join ' / '
$byQ = ($queue | Group-Object Subject | ForEach-Object { "$($_.Name) $($_.Count)" }) -join ' / '
Write-Host ("[D]{0} 残 {1} 件（{2}）（ESCALATE 済 {3} 件）／今バッチ {4} 件（{5}）（model={6}）" -f `
    $scopeLabel, $targets.Count, $byS, ($targets.Count - $actionable.Count), $queue.Count, $byQ, $Model) -ForegroundColor Cyan
if ($queue.Count -eq 0) {
    Write-Host "[D] 残件は全て ESCALATE 済（logs\tjr-repair-report.md 参照）。人手判断待ち。" -ForegroundColor Yellow
    exit 0
}
if ($DryRun) {
    $queue | ForEach-Object { Write-Host ("  [DRY] {0} {1}" -f $_.Id, $_.Rel) }
    exit 0
}

$promptTemplate = Get-Content -Raw -Encoding UTF8 $PromptFile
$rcAll = 0
$consecutive = 0
foreach ($t in $queue) {
    Write-Host "`n———— D: $($t.Id) （$($t.Rel)）————" -ForegroundColor Green
    $claimId = "$($t.Id)_v15d"
    $claimed = $false

    if ($useClaim) {
        # 二台衝突：リモート版が既に §v15 適用済み（罠枠に data-v15）なら pull 追随して SKIP
        if ((Test-TjrRemotePath -ProjectRoot $ProjectRoot -RelPath $t.Rel) -and
            (Test-TjrRemoteContent -ProjectRoot $ProjectRoot -RelPath $t.Rel -Pattern 'data-v15="1"')) {
            Write-Host "[D] $($t.Id) はリモートで適用済み → pull 追随して SKIP" -ForegroundColor Yellow
            [void](Invoke-TjrSafePull -ProjectRoot $ProjectRoot)
            continue
        }
        $claim = Request-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Stream 'D（§v15 DEDUP）'
        if ($claim -notin @('CLAIMED', 'CLAIMED_OFFLINE')) {
            Write-Host "[D] $($t.Id) claim=$claim → SKIP（次バッチで再判定）" -ForegroundColor Yellow
            continue
        }
        $claimed = $true
        if (Select-String -LiteralPath $t.Abs -Pattern 'data-v15="1"' -SimpleMatch -Quiet) {
            Write-Host "[D] $($t.Id) は pull 後に適用済み → SKIP" -ForegroundColor Yellow
            Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason '適用済み'
            continue
        }
    }

    # ① 土台（決定論）。変われば単独コミット＝headless の scope は土台込みの HEAD と照合する
    $b = Invoke-DPy @($Tool, 'base', $t.Abs)
    if ($b.Text -match '(?m)^BASE ') {
        $v0 = (Invoke-DPy @($ValidatePy, $t.Abs)).Code
        if ($v0 -ne 0) {
            & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
            Add-DStrike -Ledger $ledger -t $t -Why '土台適用後に validate ERROR（決定論ツールの不具合の疑い＝logs/tjr-repair-report.md）'
            if ($claimed) { Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason '失敗' -NoPush:$NoPush }
            $rcAll = [Math]::Max($rcAll, 1); $consecutive++
            if ($consecutive -ge $MaxConsecutiveFailures) { break }
            continue
        }
        if (-not $NoCommit) {
            & git -C $ProjectRoot add -- $t.Rel
            & git -C $ProjectRoot commit -m "chore($($t.Id)): §v15 土台（POINT/イメージ面/BASIS帰結/結論文の削除・TJR-D）" -- $t.Rel 2>&1 | Out-Null
            Write-Host "[D] $($t.Id) 土台 commit" -ForegroundColor DarkGreen
        }
    }

    $dirtyBefore = @(Get-DDirty)
    $prompt = $promptTemplate.Replace('{FILE}', $t.Rel).Replace('{ID}', $t.Id)
    $claudeArgs = @('-p', '--model', $Model, '--output-format', 'json', '--permission-mode', 'acceptEdits',
                    '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep')
    Write-Host "[D] claude -p 起動中（推定 10-20 分）..."
    Push-Location $ProjectRoot
    try { $out = $prompt | & claude @claudeArgs 2>&1; $code = $LASTEXITCODE } catch { $out = "$_"; $code = -1 }
    finally { Pop-Location }

    $dirtyAfter = @(Get-DDirty)
    $others = @($dirtyAfter | Where-Object { $_ -ne $t.Rel -and $dirtyBefore -notcontains $_ })
    & git -C $ProjectRoot diff --quiet -- $t.Rel 2>$null
    $untouched = ($LASTEXITCODE -eq 0)

    if ($code -ne 0 -and $untouched -and $others.Count -eq 0) {
        $head = (($out | Out-String) -replace '\s+', ' ').Trim()
        if ($head.Length -gt 300) { $head = $head.Substring(0, 300) }
        Write-Host "[D] $($t.Id) claude が何も書かずに終了（exit=$code）＝基盤障害とみなし D を停止（strike なし）: $head" -ForegroundColor Red
        if ($claimed) { Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason '基盤障害' -NoPush:$NoPush }
        $rcAll = 2
        break
    }
    if ($code -ne 0) { Write-Host "[D] claude exit=$code（判定は成果物で行う）" -ForegroundColor DarkYellow }

    $why = ''
    $ok = $false
    $specPath = Join-Path $SpecDir "$($t.Id).json"
    if ($others.Count -gt 0) {
        & git -C $ProjectRoot checkout -- @others 2>&1 | Out-Null
        $why = "対象外のファイルを変更（元に戻した）: $($others -join ', ')"
        Write-Host "[D] $($t.Id) $why" -ForegroundColor Red
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- WARN(D) $($t.Id): headless が対象外のファイルを変更したため元に戻した（$($others -join ', ')・$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。logs\v15d-findings.md を確認。"
    } elseif (-not (Test-Path $specPath)) {
        $why = "仕様 JSON が無い（$specPath）"
    } else {
        $ok = Test-DResult $t $specPath
        if (-not $ok) { $why = '判定 NG' }
    }

    $outcome = '失敗'
    if ($ok) {
        if ($NoCommit) {
            Write-Host "[D] $($t.Id) PASS（-NoCommit のため作業ツリーに保持）" -ForegroundColor Green
            $outcome = '完了'
        } else {
            & git -C $ProjectRoot add -- $t.Rel
            & git -C $ProjectRoot commit -m "feat($($t.Id)): 罠枠を隣接命題＋比較表へ（§v15 DEDUP・TJR-D）" -- $t.Rel 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $outcome = '完了'
                if (-not $NoPush) {
                    [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "D $($t.Id)")
                    $post = Invoke-DPy @($Tool, 'check', $t.Abs)
                    $postCss = Invoke-DPy @($Tool, 'css', '--check', $t.Abs)
                    if (-not ($post.Code -eq 0 -and $postCss.Code -eq 0)) {
                        Write-Host "[D] $($t.Id) push 後の検査 NG → CSS 区画を正典から再注入して追いコミット" -ForegroundColor Yellow
                        [void](Invoke-DPy @($Tool, 'css', $t.Abs))
                        $post2 = Invoke-DPy @($Tool, 'check', $t.Abs)
                        if ($post2.Code -eq 0) {
                            & git -C $ProjectRoot add -- $t.Rel
                            & git -C $ProjectRoot commit -m "fix($($t.Id)): TX-DGM の CSS 区画を再注入（push 追随で欠落・TJR-D）" -- $t.Rel 2>&1 | Out-Null
                            [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "D $($t.Id) fix")
                        } else {
                            Write-Host ($post2.Text.Trim()) -ForegroundColor Red
                            Add-Content -Path $ReportPath -Encoding utf8 -Value "- ESCALATE(D) $($t.Id): push 追随後に §v15 の構造が崩れ、CSS 再注入でも直らない（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。"
                            $rcAll = [Math]::Max($rcAll, 1)
                        }
                    }
                }
                Write-Host "[D] $($t.Id) commit 完了" -ForegroundColor Green
            } else {
                & git -C $ProjectRoot diff --quiet -- $t.Rel 2>$null
                if ($LASTEXITCODE -eq 0) { $outcome = 'SKIP'; Write-Host "[D] $($t.Id) 変更なし → SKIP" -ForegroundColor Yellow }
                else {
                    & git -C $ProjectRoot reset -q -- $t.Rel 2>&1 | Out-Null
                    & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
                    $ok = $false
                    $why = 'git commit 失敗（index.lock・フック等）→ ロールバック'
                }
            }
        }
    }

    if ($outcome -eq '完了') {
        if ($ledger.ContainsKey($t.Id)) { $ledger.Remove($t.Id); Save-DLedger $ledger }
        $consecutive = 0
    } elseif ($outcome -eq '失敗') {
        & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
        Add-DStrike -Ledger $ledger -t $t -Why $why
        $rcAll = [Math]::Max($rcAll, 1)
        $consecutive++
    }
    if ($claimed) {
        $reason = switch ($outcome) { '完了' { '完了' } 'SKIP' { '変更なし' } default { '失敗' } }
        Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason $reason -NoPush:$NoPush
    }
    if ($consecutive -ge $MaxConsecutiveFailures) {
        Write-Host "[D] 連続失敗 $consecutive 件 → 今バッチを打ち切り（logs\tjr-repair-report.md）" -ForegroundColor Red
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- STOP(D): 連続 $consecutive 件 FAIL で打ち切り（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。"
        break
    }
}

$remain = (Get-DTargets).Count
Write-Host "`n[D] バッチ終了 exit=$rcAll 残=$remain 件" -ForegroundColor Cyan
exit $rcAll
