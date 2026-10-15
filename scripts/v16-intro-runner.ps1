# v16-intro-runner.ps1 — TJR-I（§v16 解く前の🔰導入の付随・特別枠）エンジン（2026-10-14 新設）
#   🔰導入（details.tx-intro）が未設置のインライン周回 `_lex` を、**仕事のある科目へ均等に配る**（ラウンドロビン・
#   docs/run-patterns.md「既存展開の配り方」）。1 バッチ MaxProblems 件を科目へ 1 本ずつ順に配り、科目内は若番から：
#     ① headless（claude -p）：仕様 JSON（何の話／使う道具／読む順番）を執筆 → scripts/tx-intro.py apply で組む
#   合否はランナーが決定論で判定する（agent の自己申告に依存しない）：
#     ② tx-intro.py check            … 構造・禁止語（正誤・肢N・記述N・解答技術語）・置き場所・CSS 区画・ナビのヒント
#     ③ tx-intro.py scope --spec     … git HEAD と比べ §v16 の許可領域（導入・CSS 区画・ナビのヒント）以外が不変／導入が仕様どおり
#     ④ tx-intro.py css --check      … TX-INTRO 区画が正典と一致
#     ⑤ validate-tx-core ERROR 0 ／ ⑥ check-tx-lex-engine PASS（当該ファイルだけ＝TX_ENGINE_SKIP_CORPUS=1）
#   PASS のみ 1 問ずつ git commit/push。内容の FAIL はロールバック＋strike（同一問題 2 回で ESCALATE）、
#   連続 MaxConsecutiveFailures 件で打ち切り。headless が対象外の追跡ファイルを変えたら元に戻して FAIL。
#   claude が起動直後に死んだ（exit≠0 かつ何も変わっていない）ときは基盤障害として strike を付けずに即停止し exit 2。
#   対象判定の単一情報源＝`python -X utf8 scripts/tx-intro.py pending --json`。残件ゼロ＝「該当なし」で即終了。
#   正典：docs/tx-v12.2.1-inline-lock.md §v16／docs/run-patterns.md（I 節）。プロンプト：prompts/v16-intro-headless.md。
#   二台衝突対策：tjr-claim（予約 ID = {問題ID}_v16i・リモート版が既に導入済みなら SKIP）。
#   -NoPush／-NoCommit のときは claim を取らない（claim は HEAD ごと push するため）。
param(
    [int]$MaxProblems = 10,
    [ValidateSet('', '刑訴', '民法', '民訴', '商法', '憲法', '行政法', '刑法')]
    [string]$Subject = '',
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [string]$Model = 'claude-opus-5',  # Q/S/G/D と同じく Opus 5 固定
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

$PromptFile = Join-Path $ProjectRoot 'prompts\v16-intro-headless.md'
$Tool       = Join-Path $ProjectRoot 'scripts\tx-intro.py'
$ValidatePy = Join-Path $ProjectRoot 'scripts\validate-tx-core.py'
$EnginePy   = Join-Path $ProjectRoot 'scripts\check-tx-lex-engine.py'
$LedgerPath = Join-Path $ProjectRoot 'logs\v16i-ledger.json'
$ReportPath = Join-Path $ProjectRoot 'logs\tjr-repair-report.md'
$SpecDir    = Join-Path $ProjectRoot 'logs\v16i-spec'
foreach ($p in @($PromptFile, $Tool, $ValidatePy, $EnginePy)) {
    if (-not (Test-Path $p)) { Write-Host "[I] 前提ファイル不在: $p" -ForegroundColor Red; exit 1 }
}
New-Item -ItemType Directory -Force -Path $SpecDir | Out-Null

function Read-ILedger {
    if (Test-Path $LedgerPath) { try { return (Get-Content -Raw -Encoding UTF8 $LedgerPath | ConvertFrom-Json -AsHashtable) } catch { } }
    return @{}
}
function Save-ILedger { param($Ledger)
    $Ledger | ConvertTo-Json -Depth 4 | Out-File -FilePath $LedgerPath -Encoding utf8
}
function Invoke-IPy { param([string[]]$PyArgs, [switch]$SkipCorpus)
    if ($SkipCorpus) { $env:TX_ENGINE_SKIP_CORPUS = '1' }
    try { $out = & python -X utf8 @PyArgs 2>&1; $code = $LASTEXITCODE }
    finally { if ($SkipCorpus) { Remove-Item Env:\TX_ENGINE_SKIP_CORPUS -ErrorAction SilentlyContinue } }
    return [pscustomobject]@{ Code = $code; Text = ($out | Out-String) }
}
function Get-IDirty {
    $lines = @(& git -C $ProjectRoot -c core.quotepath=false status --porcelain --untracked-files=no 2>$null)
    return @($lines | Where-Object { $_.Length -gt 3 } | ForEach-Object { ($_.Substring(3) -replace '^"|"$', '') })
}

function Get-ITargets {
    $r = Invoke-IPy @($Tool, 'pending', '--json', '--root', $ProjectRoot)
    if ($r.Code -ne 0) { Write-Host "[I] pending 取得に失敗: $($r.Text)" -ForegroundColor Red; return @() }
    $rels = @()
    try { $rels = @($r.Text | ConvertFrom-Json) } catch { Write-Host "[I] pending の JSON を読めない" -ForegroundColor Red; return @() }
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

function Test-IResult { param($t, [string]$SpecPath)
    $c = Invoke-IPy @($Tool, 'check', $t.Abs)
    $s = Invoke-IPy @($Tool, 'scope', $t.Abs, '--spec', $SpecPath)
    $k = Invoke-IPy @($Tool, 'css', '--check', $t.Abs)
    $okCheck = ($c.Code -eq 0 -and $c.Text -match '(?m)^OK ')
    $okScope = ($s.Code -eq 0)
    $okCss   = ($k.Code -eq 0)
    $v1 = 1; $v2 = 1
    if ($okCheck -and $okScope -and $okCss) {
        $v1 = (Invoke-IPy @($ValidatePy, $t.Abs)).Code
        $v2 = (Invoke-IPy @($EnginePy, $t.Abs) -SkipCorpus).Code
    }
    Write-Host ("[I] 判定 check={0} scope={1} css={2} validate={3} engine={4}" -f `
        $(if ($okCheck) { 'OK' } else { 'NG' }), $(if ($okScope) { 'OK' } else { 'NG' }), $(if ($okCss) { 'OK' } else { 'NG' }), $v1, $v2)
    if (-not $okCheck) { Write-Host ($c.Text.Trim()) -ForegroundColor DarkYellow }
    if (-not $okScope) { Write-Host ($s.Text.Trim()) -ForegroundColor DarkYellow }
    if (-not $okCss)   { Write-Host ($k.Text.Trim()) -ForegroundColor DarkYellow }
    return ($okCheck -and $okScope -and $okCss -and $v1 -eq 0 -and $v2 -eq 0)
}

function Add-IStrike { param($Ledger, $t, [string]$Why)
    $s = [int]($Ledger[$t.Id] ?? 0) + 1
    $Ledger[$t.Id] = $s
    Save-ILedger $Ledger
    Write-Host "[I] $($t.Id) 失敗（strike $s/2）：$Why" -ForegroundColor Yellow
    if ($s -ge 2) {
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- ESCALATE(I) $($t.Id): §v16 🔰導入の執筆が 2 回失敗（最後の理由：$Why・$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。人手または個別セッションで対応。"
        Write-Host "[I] $($t.Id) ESCALATE（logs\tjr-repair-report.md）" -ForegroundColor Red
    }
}

$useClaim = (-not $NoCommit -and -not $NoPush)
if (-not $DryRun -and -not $CountOnly -and $useClaim) { [void](Sync-TjrRepo -ProjectRoot $ProjectRoot) }

$targets = @(Get-ITargets)
$ledger = Read-ILedger
$actionable = @($targets | Where-Object { [int]($ledger[$_.Id] ?? 0) -lt 2 })
if ($CountOnly) { Write-Output $actionable.Count; exit 0 }

$scopeLabel = if ($Subject) { "（$Subject）" } else { '' }
if ($targets.Count -eq 0) {
    if ($Subject -or $FromNumber -gt 0 -or $ToNumber -gt 0) {
        Write-Host "[I]$scopeLabel 指定範囲に該当なし（他の科目・番号には残件があり得る）" -ForegroundColor Green
    } else {
        Write-Host "[I] 該当なし＝§v16 特別枠は完遂（導入が未設置のインライン _lex は残っていない）" -ForegroundColor Green
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
Write-Host ("[I]{0} 残 {1} 件（{2}）（ESCALATE 済 {3} 件）／今バッチ {4} 件（{5}）（model={6}）" -f `
    $scopeLabel, $targets.Count, $byS, ($targets.Count - $actionable.Count), $queue.Count, $byQ, $Model) -ForegroundColor Cyan
if ($queue.Count -eq 0) {
    Write-Host "[I] 残件は全て ESCALATE 済（logs\tjr-repair-report.md 参照）。人手判断待ち。" -ForegroundColor Yellow
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
    Write-Host "`n———— I: $($t.Id) （$($t.Rel)）————" -ForegroundColor Green
    $claimId = "$($t.Id)_v16i"
    $claimed = $false

    if ($useClaim) {
        # 二台衝突：リモート版が既に導入済みなら pull 追随して SKIP
        if ((Test-TjrRemotePath -ProjectRoot $ProjectRoot -RelPath $t.Rel) -and
            (Test-TjrRemoteContent -ProjectRoot $ProjectRoot -RelPath $t.Rel -Pattern 'class="tx-intro"')) {
            Write-Host "[I] $($t.Id) はリモートで導入済み → pull 追随して SKIP" -ForegroundColor Yellow
            [void](Invoke-TjrSafePull -ProjectRoot $ProjectRoot)
            continue
        }
        $claim = Request-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Stream 'I（§v16 導入）'
        if ($claim -notin @('CLAIMED', 'CLAIMED_OFFLINE')) {
            Write-Host "[I] $($t.Id) claim=$claim → SKIP（次バッチで再判定）" -ForegroundColor Yellow
            continue
        }
        $claimed = $true
        if (Select-String -LiteralPath $t.Abs -Pattern 'class="tx-intro"' -SimpleMatch -Quiet) {
            Write-Host "[I] $($t.Id) は pull 後に導入済み → SKIP" -ForegroundColor Yellow
            Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason '適用済み'
            continue
        }
    }

    $dirtyBefore = @(Get-IDirty)
    $prompt = $promptTemplate.Replace('{FILE}', $t.Rel).Replace('{ID}', $t.Id)
    $claudeArgs = @('-p', '--model', $Model, '--output-format', 'json', '--permission-mode', 'acceptEdits',
                    '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep')
    Write-Host "[I] claude -p 起動中（推定 5-10 分）..."
    Push-Location $ProjectRoot
    try { $out = $prompt | & claude @claudeArgs 2>&1; $code = $LASTEXITCODE } catch { $out = "$_"; $code = -1 }
    finally { Pop-Location }

    $dirtyAfter = @(Get-IDirty)
    $others = @($dirtyAfter | Where-Object { $_ -ne $t.Rel -and $dirtyBefore -notcontains $_ })
    & git -C $ProjectRoot diff --quiet -- $t.Rel 2>$null
    $untouched = ($LASTEXITCODE -eq 0)

    if ($code -ne 0 -and $untouched -and $others.Count -eq 0) {
        $head = (($out | Out-String) -replace '\s+', ' ').Trim()
        if ($head.Length -gt 300) { $head = $head.Substring(0, 300) }
        Write-Host "[I] $($t.Id) claude が何も書かずに終了（exit=$code）＝基盤障害とみなし I を停止（strike なし）: $head" -ForegroundColor Red
        if ($claimed) { Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason '基盤障害' -NoPush:$NoPush }
        $rcAll = 2
        break
    }
    if ($code -ne 0) { Write-Host "[I] claude exit=$code（判定は成果物で行う）" -ForegroundColor DarkYellow }

    $why = ''
    $ok = $false
    $specPath = Join-Path $SpecDir "$($t.Id).json"
    if ($others.Count -gt 0) {
        & git -C $ProjectRoot checkout -- @others 2>&1 | Out-Null
        $why = "対象外のファイルを変更（元に戻した）: $($others -join ', ')"
        Write-Host "[I] $($t.Id) $why" -ForegroundColor Red
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- WARN(I) $($t.Id): headless が対象外のファイルを変更したため元に戻した（$($others -join ', ')・$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。logs\v16i-findings.md を確認。"
    } elseif (-not (Test-Path $specPath)) {
        $why = "仕様 JSON が無い（$specPath）"
    } else {
        $ok = Test-IResult $t $specPath
        if (-not $ok) { $why = '判定 NG' }
    }

    $outcome = '失敗'
    if ($ok) {
        if ($NoCommit) {
            Write-Host "[I] $($t.Id) PASS（-NoCommit のため作業ツリーに保持）" -ForegroundColor Green
            $outcome = '完了'
        } else {
            & git -C $ProjectRoot add -- $t.Rel
            & git -C $ProjectRoot commit -m "feat($($t.Id)): 解く前の🔰導入（§v16 INTRO・TJR-I）" -- $t.Rel 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $outcome = '完了'
                if (-not $NoPush) {
                    [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "I $($t.Id)")
                    $post = Invoke-IPy @($Tool, 'check', $t.Abs)
                    $postCss = Invoke-IPy @($Tool, 'css', '--check', $t.Abs)
                    if (-not ($post.Code -eq 0 -and $postCss.Code -eq 0)) {
                        Write-Host "[I] $($t.Id) push 後の検査 NG → CSS 区画を正典から再注入して追いコミット" -ForegroundColor Yellow
                        [void](Invoke-IPy @($Tool, 'css', $t.Abs))
                        $post2 = Invoke-IPy @($Tool, 'check', $t.Abs)
                        if ($post2.Code -eq 0) {
                            & git -C $ProjectRoot add -- $t.Rel
                            & git -C $ProjectRoot commit -m "fix($($t.Id)): TX-INTRO の CSS 区画を再注入（push 追随で欠落・TJR-I）" -- $t.Rel 2>&1 | Out-Null
                            [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "I $($t.Id) fix")
                        } else {
                            Write-Host ($post2.Text.Trim()) -ForegroundColor Red
                            Add-Content -Path $ReportPath -Encoding utf8 -Value "- ESCALATE(I) $($t.Id): push 追随後に §v16 の構造が崩れ、CSS 再注入でも直らない（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。"
                            $rcAll = [Math]::Max($rcAll, 1)
                        }
                    }
                }
                Write-Host "[I] $($t.Id) commit 完了" -ForegroundColor Green
            } else {
                & git -C $ProjectRoot diff --quiet -- $t.Rel 2>$null
                if ($LASTEXITCODE -eq 0) { $outcome = 'SKIP'; Write-Host "[I] $($t.Id) 変更なし → SKIP" -ForegroundColor Yellow }
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
        if ($ledger.ContainsKey($t.Id)) { $ledger.Remove($t.Id); Save-ILedger $ledger }
        $consecutive = 0
    } elseif ($outcome -eq '失敗') {
        & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
        Add-IStrike -Ledger $ledger -t $t -Why $why
        $rcAll = [Math]::Max($rcAll, 1)
        $consecutive++
    }
    if ($claimed) {
        $reason = switch ($outcome) { '完了' { '完了' } 'SKIP' { '変更なし' } default { '失敗' } }
        Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason $reason -NoPush:$NoPush
    }
    if ($consecutive -ge $MaxConsecutiveFailures) {
        Write-Host "[I] 連続失敗 $consecutive 件 → 今バッチを打ち切り（logs\tjr-repair-report.md）" -ForegroundColor Red
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- STOP(I): 連続 $consecutive 件 FAIL で打ち切り（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。"
        break
    }
}

$remain = (Get-ITargets).Count
Write-Host "`n[I] バッチ終了 exit=$rcAll 残=$remain 件" -ForegroundColor Cyan
exit $rcAll
