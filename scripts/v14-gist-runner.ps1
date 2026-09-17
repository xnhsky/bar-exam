# v14-gist-runner.ps1 — TJR-G（§v14 THE GIST ストーリー型の付随書き換え・特別枠）エンジン（2026-09-17 新設）
#   旧型（1 段落）の 💡THE GIST が残る v13 `_lex` を、**仕事のある科目へ均等に配る**（ラウンドロビン・
#   docs/run-patterns.md「既存展開の配り方」）。1 バッチ MaxProblems 件を科目へ 1 本ずつ順に配り、科目内は若番から
#   headless（claude -p）で JSON 仕様を執筆 → scripts/tx-gist-story.py apply で組む。
#   ユーザー指示（2026-09-17）「残りの LEX は TJR の付随で処理して」＝刑訴TX100-120 の展開後の残件。
#   いま学習中の科目へ寄せたいときだけ -Subject を添える（「TJR処理 刑訴」＝その科目だけを流す・S と同じ）。
#
#   合否はランナーが決定論で判定する（agent の自己申告に依存しない）：
#     ① tx-gist-story.py check      … 全カードがストーリー型・構造・○×の向き
#     ② tx-gist-story.py scope      … git HEAD と比べ GIST 行と CSS 区画以外が不変／GIST が仕様から組んだ HTML と一致／
#                                      ファイル外の判例を持ち込んでいない
#     ③ tx-gist-story.py css --check … CSS 区画が正典（GENESIS-CARD）と一致
#     ④ validate-tx-core ERROR 0 ／ ⑤ check-tx-lex-engine PASS（当該ファイルだけ＝TX_ENGINE_SKIP_CORPUS=1）
#   コーパス横断の判例元号割れゲートはバッチ前に 1 回だけ回し、NG なら G を見送る（他ファイルの問題で正しい
#   書き換えを巻き戻したり ESCALATE したりしない）。
#   PASS のみ 1 問ずつ git commit/push。内容の FAIL はロールバック＋strike（同一問題 2 回で ESCALATE）、
#   連続 MaxConsecutiveFailures 件で打ち切り。headless が対象外の追跡ファイルを変えたら元に戻して FAIL。
#   claude が起動直後に死んだ（ログイン切れ等＝exit≠0 かつ何も変わっていない）ときは基盤障害として
#   strike を付けずに即停止し exit 2（TJR は以後のバッチで G を止める）。
#   push の追随（rebase -X ours）で CSS 区画が落ちたら正典から再注入して追いコミットする。
#
#   対象判定の単一情報源＝`python -X utf8 scripts/tx-gist-story.py pending --json`（v13 でない旧版は R の領分。
#   行構造のせいでツールが書き換えられないファイルは --unreplaceable に分けて対象外）。
#   残件ゼロ＝「該当なし」で即終了（過渡ストリーム＝完遂で消滅）。
#   正典：docs/tx-v12.2.1-inline-lock.md §v14／docs/run-patterns.md（G 節）。プロンプト：prompts/v14-gist-headless.md。
#   二台衝突対策：tjr-claim（予約 ID = {問題ID}_v14g・リモート版が既にストーリー型なら SKIP）。
#   -NoPush／-NoCommit のときは claim を取らない（claim は HEAD ごと push するため・tx-v13-runner と同じ）。
param(
    [int]$MaxProblems = 10,            # 1 バッチの処理件数（既定 10）。仕事のある科目へ均等に配る。
    [ValidateSet('', '刑訴', '民法', '民訴', '商法', '憲法', '行政法', '刑法')]
    [string]$Subject = '',             # 空＝全科目へ均等配分／明示時はその科目だけを流す
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [string]$Model = 'claude-opus-5',  # Q/S と同じく Opus 5 固定
    [int]$MaxConsecutiveFailures = 3,  # 内容の FAIL が連続したら打ち切る（プロンプト・ツールの不具合で全件を焼かない）
    [switch]$CountOnly,                # 今すぐ処理できる件数（科目・ESCALATE 除外済み）だけを出力して終了（TJR 用）
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

# === 科目の並び（配る順序と表示順だけ。配分は均等）=====================================
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

$PromptFile = Join-Path $ProjectRoot 'prompts\v14-gist-headless.md'
$GistTool   = Join-Path $ProjectRoot 'scripts\tx-gist-story.py'
$ValidatePy = Join-Path $ProjectRoot 'scripts\validate-tx-core.py'
$EnginePy   = Join-Path $ProjectRoot 'scripts\check-tx-lex-engine.py'
$EraPy      = Join-Path $ProjectRoot 'scripts\check-citation-era.py'
$LedgerPath = Join-Path $ProjectRoot 'logs\v14g-ledger.json'
$ReportPath = Join-Path $ProjectRoot 'logs\tjr-repair-report.md'
foreach ($p in @($PromptFile, $GistTool, $ValidatePy, $EnginePy)) {
    if (-not (Test-Path $p)) { Write-Host "[G] 前提ファイル不在: $p" -ForegroundColor Red; exit 1 }
}
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot 'logs\v14g-spec') | Out-Null

# === 失敗台帳（同一問題 2 回失敗で ESCALATE＝以後スキップ・Q/S/F と同じ無限再挑戦防止）===
function Read-GLedger {
    if (Test-Path $LedgerPath) { try { return (Get-Content -Raw -Encoding UTF8 $LedgerPath | ConvertFrom-Json -AsHashtable) } catch { } }
    return @{}
}
function Save-GLedger { param($Ledger)
    $Ledger | ConvertTo-Json -Depth 4 | Out-File -FilePath $LedgerPath -Encoding utf8
}

# python を UTF-8 で呼ぶ（stdout をパイプ/破棄すると cp932 で落ちて偽 FAIL になるため -X utf8 必須）
function Invoke-GPy { param([string[]]$PyArgs, [switch]$SkipCorpus)
    if ($SkipCorpus) { $env:TX_ENGINE_SKIP_CORPUS = '1' }
    try { $out = & python -X utf8 @PyArgs 2>&1; $code = $LASTEXITCODE }
    finally { if ($SkipCorpus) { Remove-Item Env:\TX_ENGINE_SKIP_CORPUS -ErrorAction SilentlyContinue } }
    return [pscustomobject]@{ Code = $code; Text = ($out | Out-String) }
}

# 追跡ファイルの変更一覧（git status --porcelain・未追跡は除く）
function Get-GDirty {
    # core.quotepath=false：既定では日本語パスが 8 進エスケープ付きの引用符形式で出るため、対象ファイル自身を「対象外」と誤判定する
    $lines = @(& git -C $ProjectRoot -c core.quotepath=false status --porcelain --untracked-files=no 2>$null)
    return @($lines | Where-Object { $_.Length -gt 3 } | ForEach-Object { ($_.Substring(3) -replace '^"|"$', '') })
}

# === 対象検出：tx-gist-story.py pending（単一情報源）→ 科目順・若番 ===
function Get-GTargets {
    $r = Invoke-GPy @($GistTool, 'pending', '--json', '--root', $ProjectRoot)
    if ($r.Code -ne 0) { Write-Host "[G] pending 取得に失敗: $($r.Text)" -ForegroundColor Red; return @() }
    $rels = @()
    try { $rels = @($r.Text | ConvertFrom-Json) } catch { Write-Host "[G] pending の JSON を読めない" -ForegroundColor Red; return @() }
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

# === ランナー側の決定論判定 ===
function Test-GResult { param($t)
    $c = Invoke-GPy @($GistTool, 'check', $t.Abs)
    $s = Invoke-GPy @($GistTool, 'scope', $t.Abs)
    $k = Invoke-GPy @($GistTool, 'css', '--check', $t.Abs)
    $okCheck = ($c.Code -eq 0 -and $c.Text -match '(?m)^OK ')
    $okScope = ($s.Code -eq 0)
    $okCss   = ($k.Code -eq 0)
    $v1 = 1; $v2 = 1
    if ($okCheck -and $okScope -and $okCss) {
        $v1 = (Invoke-GPy @($ValidatePy, $t.Abs)).Code
        $v2 = (Invoke-GPy @($EnginePy, $t.Abs) -SkipCorpus).Code
    }
    Write-Host ("[G] 判定 check={0} scope={1} css={2} validate={3} engine={4}" -f `
        $(if ($okCheck) { 'OK' } else { 'NG' }), $(if ($okScope) { 'OK' } else { 'NG' }), $(if ($okCss) { 'OK' } else { 'NG' }), $v1, $v2)
    if (-not $okCheck) { Write-Host ($c.Text.Trim()) -ForegroundColor DarkYellow }
    if (-not $okScope) { Write-Host ($s.Text.Trim()) -ForegroundColor DarkYellow }
    if (-not $okCss)   { Write-Host ($k.Text.Trim()) -ForegroundColor DarkYellow }
    return ($okCheck -and $okScope -and $okCss -and $v1 -eq 0 -and $v2 -eq 0)
}

function Add-GStrike { param($Ledger, $t, [string]$Why)
    $s = [int]($Ledger[$t.Id] ?? 0) + 1
    $Ledger[$t.Id] = $s
    Save-GLedger $Ledger
    Write-Host "[G] $($t.Id) 失敗（strike $s/2）：$Why" -ForegroundColor Yellow
    if ($s -ge 2) {
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- ESCALATE(G) $($t.Id): §v14 THE GIST ストーリー型の書き換えが 2 回失敗（最後の理由：$Why・$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。人手または個別セッションで対応。"
        Write-Host "[G] $($t.Id) ESCALATE（logs\tjr-repair-report.md）" -ForegroundColor Red
    }
}

$useClaim = (-not $NoCommit -and -not $NoPush)
if (-not $DryRun -and -not $CountOnly -and $useClaim) { [void](Sync-TjrRepo -ProjectRoot $ProjectRoot) }

$targets = @(Get-GTargets)
$ledger = Read-GLedger
$actionable = @($targets | Where-Object { [int]($ledger[$_.Id] ?? 0) -lt 2 })
if ($CountOnly) { Write-Output $actionable.Count; exit 0 }

$scopeLabel = if ($Subject) { "（$Subject）" } else { '' }
if ($targets.Count -eq 0) {
    if ($Subject -or $FromNumber -gt 0 -or $ToNumber -gt 0) {
        Write-Host "[G]$scopeLabel 指定範囲に該当なし（他の科目・番号には残件があり得る）" -ForegroundColor Green
    } else {
        Write-Host "[G] 該当なし＝§v14 特別枠は完遂（旧型 THE GIST の v13 _lex は残っていない）" -ForegroundColor Green
    }
    exit 0
}
# === ラウンドロビン配分：仕事のある科目へ 1 本ずつ順に配り、上限まで埋める（ESCALATE 済みは飛ばす）===
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
Write-Host ("[G]{0} 残 {1} 件（{2}）（ESCALATE 済 {3} 件）／今バッチ {4} 件（{5}）（model={6}）" -f `
    $scopeLabel, $targets.Count, $byS, ($targets.Count - $actionable.Count), $queue.Count, $byQ, $Model) -ForegroundColor Cyan
if ($queue.Count -eq 0) {
    Write-Host "[G] 残件は全て ESCALATE 済（logs\tjr-repair-report.md 参照）。人手判断待ち。" -ForegroundColor Yellow
    exit 0
}
if ($DryRun) {
    $queue | ForEach-Object { Write-Host ("  [DRY] {0} {1}" -f $_.Id, $_.Rel) }
    exit 0
}

# === コーパス横断ゲート（バッチ前に 1 回）：NG のまま回すと正しい書き換えまで FAIL 扱いになる ===
if (Test-Path $EraPy) {
    Write-Host "[G] コーパス横断ゲート（判例元号割れ）を確認中（約 2 分）..."
    $era = Invoke-GPy @($EraPy, 'outputs')
    if ($era.Code -ne 0) {
        Write-Host "[G] コーパス横断ゲート NG → 今バッチの G は見送り（strike なし。check-citation-era.py の指摘を先に解消）" -ForegroundColor Yellow
        exit 0
    }
}

$promptTemplate = Get-Content -Raw -Encoding UTF8 $PromptFile
$rcAll = 0
$consecutive = 0
foreach ($t in $queue) {
    Write-Host "`n———— G: $($t.Id) （$($t.Rel)）————" -ForegroundColor Green
    $claimId = "$($t.Id)_v14g"
    $claimed = $false

    if ($useClaim) {
        # 二台衝突：リモート版が既にストーリー型（旧型 GIST 行が無い）なら pull 追随して SKIP
        if ((Test-TjrRemotePath -ProjectRoot $ProjectRoot -RelPath $t.Rel) -and
            -not (Test-TjrRemoteContent -ProjectRoot $ProjectRoot -RelPath $t.Rel -Pattern '<p class="syn-lead">')) {
            Write-Host "[G] $($t.Id) はリモートで書き換え済み → pull 追随して SKIP" -ForegroundColor Yellow
            [void](Invoke-TjrSafePull -ProjectRoot $ProjectRoot)
            continue
        }
        $claim = Request-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Stream 'G（§v14 GIST）'
        if ($claim -notin @('CLAIMED', 'CLAIMED_OFFLINE')) {
            Write-Host "[G] $($t.Id) claim=$claim → SKIP（次バッチで再判定）" -ForegroundColor Yellow
            continue
        }
        $claimed = $true
        # claim の fetch/pull で相手 PC の書き換えが降りてきていないか、手元のファイルで確かめ直す
        if (-not (Select-String -LiteralPath $t.Abs -Pattern '<p class="syn-lead">' -SimpleMatch -Quiet)) {
            Write-Host "[G] $($t.Id) は pull 後に書き換え済み → SKIP" -ForegroundColor Yellow
            Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason '書き換え済み'
            continue
        }
    }

    $dirtyBefore = @(Get-GDirty)
    $prompt = $promptTemplate.Replace('{FILE}', $t.Rel).Replace('{ID}', $t.Id)
    $claudeArgs = @('-p', '--model', $Model, '--output-format', 'json', '--permission-mode', 'acceptEdits',
                    '--allowedTools', 'Write,Edit,Read,Bash,Glob,Grep')
    Write-Host "[G] claude -p 起動中（推定 10-20 分）..."
    Push-Location $ProjectRoot
    try { $out = $prompt | & claude @claudeArgs 2>&1; $code = $LASTEXITCODE } catch { $out = "$_"; $code = -1 }
    finally { Pop-Location }

    $dirtyAfter = @(Get-GDirty)
    $others = @($dirtyAfter | Where-Object { $_ -ne $t.Rel -and $dirtyBefore -notcontains $_ })
    & git -C $ProjectRoot diff --quiet -- $t.Rel 2>$null
    $untouched = ($LASTEXITCODE -eq 0)

    # 基盤障害（ログイン切れ・起動失敗）＝何も書けていない。strike を付けずに停止する
    if ($code -ne 0 -and $untouched -and $others.Count -eq 0) {
        $head = (($out | Out-String) -replace '\s+', ' ').Trim()
        if ($head.Length -gt 300) { $head = $head.Substring(0, 300) }
        Write-Host "[G] $($t.Id) claude が何も書かずに終了（exit=$code）＝基盤障害とみなし G を停止（strike なし）: $head" -ForegroundColor Red
        if ($claimed) { Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason '基盤障害' -NoPush:$NoPush }
        $rcAll = 2
        break
    }
    if ($code -ne 0) { Write-Host "[G] claude exit=$code（判定は成果物で行う）" -ForegroundColor DarkYellow }

    $why = ''
    $ok = $false
    if ($others.Count -gt 0) {
        # 対象外の追跡ファイル（ツール・プロンプト・他の教材など）を変えた＝無人運転では受け入れない
        & git -C $ProjectRoot checkout -- @others 2>&1 | Out-Null
        $why = "対象外のファイルを変更（元に戻した）: $($others -join ', ')"
        Write-Host "[G] $($t.Id) $why" -ForegroundColor Red
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- WARN(G) $($t.Id): headless が対象外のファイルを変更したため元に戻した（$($others -join ', ')・$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。ツールの不具合報告の可能性があるので logs\v14g-findings.md を確認。"
    } else {
        $ok = Test-GResult $t
        if (-not $ok) { $why = '判定 NG' }
    }

    $outcome = '失敗'
    if ($ok) {
        if ($NoCommit) {
            Write-Host "[G] $($t.Id) PASS（-NoCommit のため作業ツリーに保持）" -ForegroundColor Green
            $outcome = '完了'
        } else {
            & git -C $ProjectRoot add -- $t.Rel
            & git -C $ProjectRoot commit -m "feat($($t.Id)): THE GIST をストーリー型へ（§v14・TJR-G）" -- $t.Rel 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $outcome = '完了'
                if (-not $NoPush) {
                    [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "G $($t.Id)")
                    # 追随（rebase -X ours）で CSS 区画などがリモート版に置き換わっていないか確認
                    $post = Invoke-GPy @($GistTool, 'check', $t.Abs)
                    $postCss = Invoke-GPy @($GistTool, 'css', '--check', $t.Abs)
                    if (-not ($post.Code -eq 0 -and $post.Text -match '(?m)^OK ' -and $postCss.Code -eq 0)) {
                        Write-Host "[G] $($t.Id) push 後の構造検査 NG → CSS 区画を正典から再注入して追いコミット" -ForegroundColor Yellow
                        [void](Invoke-GPy @($GistTool, 'css', $t.Abs))
                        $post2 = Invoke-GPy @($GistTool, 'check', $t.Abs)
                        if ($post2.Code -eq 0 -and $post2.Text -match '(?m)^OK ') {
                            & git -C $ProjectRoot add -- $t.Rel
                            & git -C $ProjectRoot commit -m "fix($($t.Id)): THE GIST の CSS 区画を再注入（push 追随で欠落・TJR-G）" -- $t.Rel 2>&1 | Out-Null
                            [void](Invoke-TjrSafePush -ProjectRoot $ProjectRoot -Label "G $($t.Id) fix")
                        } else {
                            Write-Host ($post2.Text.Trim()) -ForegroundColor Red
                            Add-Content -Path $ReportPath -Encoding utf8 -Value "- ESCALATE(G) $($t.Id): push 追随後に THE GIST の構造が崩れ、CSS 再注入でも直らない（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。"
                            $rcAll = [Math]::Max($rcAll, 1)
                        }
                    }
                }
                Write-Host "[G] $($t.Id) commit 完了" -ForegroundColor Green
            } else {
                & git -C $ProjectRoot diff --cached --quiet -- $t.Rel 2>$null
                if ($LASTEXITCODE -eq 0) {
                    & git -C $ProjectRoot diff --quiet -- $t.Rel 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "[G] $($t.Id) 変更なし（既にストーリー型）→ SKIP" -ForegroundColor Yellow
                        $outcome = 'SKIP'
                    }
                }
                if ($outcome -ne 'SKIP') {
                    & git -C $ProjectRoot reset -q -- $t.Rel 2>&1 | Out-Null
                    & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
                    $ok = $false
                    $why = 'git commit 失敗（index.lock・フック等）→ ロールバック'
                }
            }
        }
    }

    if ($outcome -eq '完了') {
        if ($ledger.ContainsKey($t.Id)) { $ledger.Remove($t.Id); Save-GLedger $ledger }
        $consecutive = 0
    } elseif ($outcome -eq '失敗') {
        & git -C $ProjectRoot checkout -- $t.Rel 2>&1 | Out-Null
        Add-GStrike -Ledger $ledger -t $t -Why $why
        $rcAll = [Math]::Max($rcAll, 1)
        $consecutive++
    }
    if ($claimed) {
        $reason = switch ($outcome) { '完了' { '完了' } 'SKIP' { '変更なし' } default { '失敗' } }
        Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $claimId -Reason $reason -NoPush:$NoPush
    }
    if ($consecutive -ge $MaxConsecutiveFailures) {
        Write-Host "[G] 連続失敗 $consecutive 件 → 今バッチを打ち切り（プロンプト・ツールの不具合の可能性。logs\tjr-repair-report.md）" -ForegroundColor Red
        Add-Content -Path $ReportPath -Encoding utf8 -Value "- STOP(G): 連続 $consecutive 件 FAIL で打ち切り（$(Get-Date -Format 'yyyy-MM-dd HH:mm')）。"
        break
    }
}

$remain = (Get-GTargets).Count
Write-Host "`n[G] バッチ終了 exit=$rcAll 残=$remain 件" -ForegroundColor Cyan
exit $rcAll
