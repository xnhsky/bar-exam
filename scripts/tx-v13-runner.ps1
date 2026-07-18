# tx-v13-runner.ps1 — TJR の TX エンジン（T＝新規TX ／ R＝旧_lex再生成の共通エンジン）
#
# 【役割】v13.0.0 LOOP-CARD 二系統（公式 000_TX ＝本物5択 ／ Lexia _lex ＝ ox-grid＋解法ナビ）を
#   headless（claude -p）で 1 問ずつ生成し、validate-tx-core（公式・_lex 両方）→ 作成日時スタンプ →
#   git commit/push まで通す。旧 night-batch-runner（v10 GOLD-SKELETON・単一ファイル）の後継。
#   TJR.ps1 から呼ばれる内部エンジン（直接叩いてもよいが、通常は「TJR処理」経由）。
#
# 【T モード（既定）】フロンティア前進＝inputs/000_TX/{科目}/*.pdf のうち公式 HTML 未生成 かつ
#   番号が「公式の最大既存番号」より先のものを最若番から生成（過去帯の欠番は R の領分＝二重処理防止）。
# 【R モード（-Regen）】さかのぼり＝(a) 旧版_lex（v13でない・PDFあり）を PDF から最新v13で作り直す
#   （公式も同時に最新化＝両者の本文整合を保つ）＋ (b) 公式最大番号以下の欠番（PDFあり・公式なし）の
#   補完生成（2026-07-18 ユーザー確定「刑法58件未生成の分をR再生成と併せる」）。
#   PDFが消えている旧_lex は再生成不能＝スキップし [R-SKIP-NOPDF] を出す（Drive 復元後に再対象化）。
#
# 使い方:
#   pwsh -NoProfile -File scripts/tx-v13-runner.ps1 -Subject 刑訴 -MaxProblems 12
#   pwsh -NoProfile -File scripts/tx-v13-runner.ps1 -Subject 刑 -Regen -MaxProblems 3
#   pwsh -NoProfile -File scripts/tx-v13-runner.ps1 -Subject 刑 -FromNumber 355 -ToNumber 360
#   pwsh -NoProfile -File scripts/tx-v13-runner.ps1 -Subject 刑訴 -DryRun
param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '刑',
    [int]$MaxProblems = 12,
    [int]$FromNumber = 0,
    [int]$ToNumber = 0,
    [int]$MaxConsecutiveFailures = 3,
    [switch]$Regen,                 # R モード（旧_lex を PDF から再生成）
    [switch]$NoPush,                # commit のみ（push しない）
    [switch]$NoCommit,              # commit もしない（生成・検証・スタンプまで）
    [string]$ProjectRoot = '',
    [switch]$DryRun
)

# === パス解決 ===
$DefaultProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

# 科目 → 00N_科目 フォルダ ／ TX 接頭辞（TX は Subject 文字列がそのまま接頭辞）
$SubjectFolder = switch ($Subject) { '刑'{'001_刑法'} '刑訴'{'002_刑事訴訟法'} '民'{'003_民法'} '商'{'004_商法'} '民訴'{'005_民事訴訟法'} '行政'{'006_行政法'} '憲'{'007_憲法'} }
$Prefix = $Subject   # 刑TX / 刑訴TX / 民TX ...

$PdfDir        = Join-Path $ProjectRoot "inputs\000_TX\$SubjectFolder"
$OfficialDir   = Join-Path $ProjectRoot "outputs\000_TX\$SubjectFolder"
$LexDir        = Join-Path $ProjectRoot "outputs\ux\000_TX\$SubjectFolder"
$LogsDir       = Join-Path $ProjectRoot "logs"
$PromptSource  = Join-Path $ProjectRoot "prompts\new-tx-headless-v13.md"
$Canonical     = Join-Path $ProjectRoot "canonical\GENESIS-CARD.html"
$SolveNav      = Join-Path $ProjectRoot "canonical\SOLVE-NAV.html"
$ValidateCore  = Join-Path $ProjectRoot "scripts\validate-tx-core.py"
$CheckEngine   = Join-Path $ProjectRoot "scripts\check-tx-lex-engine.py"
$CheckOxGrid   = Join-Path $ProjectRoot "scripts\check-lex-oxgrid-integrity.py"
$StampScript   = Join-Path $ProjectRoot "scripts\stamp-created-date.py"
$CostCsv       = Join-Path $LogsDir "tx-v13-summary.csv"
$RunLog        = Join-Path $LogsDir "tx-v13-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
if (-not (Test-Path $LogsDir)) { New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null }

Start-Transcript -Path $RunLog -Append | Out-Null

# === 作成日時スタンプ保険フックの冪等インストール（CLAUDE.md §9）===
try {
    $__hp = (& git -C $ProjectRoot config --get core.hooksPath) 2>$null
    if ($__hp -ne 'scripts/git-hooks') { & git -C $ProjectRoot config core.hooksPath scripts/git-hooks 2>$null }
} catch {}

# === スリープ抑止（DryRun 以外・feedback_nbr_keep_awake）===
if (-not $DryRun) {
    try {
        $sig = '[DllImport("kernel32.dll", SetLastError=true)] public static extern uint SetThreadExecutionState(uint esFlags);'
        $PW = Add-Type -MemberDefinition $sig -Name PW -Namespace Win32 -PassThru -ErrorAction Stop
        [void]$PW::SetThreadExecutionState([uint32]2147483651)  # ES_CONTINUOUS|ES_SYSTEM_REQUIRED|ES_DISPLAY_REQUIRED
        Write-Host "[KEEP-AWAKE] スリープ抑止 ON（プロセス終了で自動復帰）" -ForegroundColor DarkGray
    } catch { Write-Host "[KEEP-AWAKE] 抑止設定に失敗（続行）: $($_.Exception.Message)" -ForegroundColor Yellow }
}

$modeText = if ($Regen) { 'R（旧_lex再生成）' } else { 'T（新規TX）' }
Write-Host "=== tx-v13-runner 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "Subject=$Subject ($SubjectFolder) / モード=$modeText / MaxProblems=$MaxProblems / 範囲 From=$FromNumber To=$ToNumber / DryRun=$DryRun"
Write-Host "PDF=$PdfDir"
Write-Host "公式=$OfficialDir"
Write-Host "_lex=$LexDir"

# === 前提ファイル確認 ===
$missing = @()
if (-not (Test-Path $PdfDir))       { $missing += "PDF dir: $PdfDir" }
if (-not (Test-Path $PromptSource)) { $missing += "v13 prompt: $PromptSource（段階2で新設）" }
if (-not (Test-Path $Canonical))    { $missing += "canonical GENESIS-CARD: $Canonical" }
if (-not (Test-Path $ValidateCore)) { $missing += "validate-tx-core: $ValidateCore" }
if ($missing.Count -gt 0) {
    Write-Host "[ABORT] 前提ファイル不足:" -ForegroundColor Red
    foreach ($m in $missing) { Write-Host "  - $m" -ForegroundColor Red }
    Stop-Transcript | Out-Null
    exit 1
}
foreach ($d in @($OfficialDir, $LexDir)) { if (-not (Test-Path $d)) { New-Item -Path $d -ItemType Directory -Force | Out-Null } }

# === 番号 → 入力PDFパス索引（数字ステムのみ）===
function Get-PdfMap {
    $map = @{}
    foreach ($p in @(Get-ChildItem -Path $PdfDir -Filter '*.pdf' -File -ErrorAction SilentlyContinue)) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($p.Name)
        if ($stem -match '^\d+') { $n = [int]$Matches[0]; if (-not $map.ContainsKey($n)) { $map[$n] = $p.FullName } }
    }
    return $map
}
$PdfMap = Get-PdfMap

function Test-InRange { param([int]$n)
    if ($FromNumber -gt 0 -and $n -lt $FromNumber) { return $false }
    if ($ToNumber  -gt 0 -and $n -gt $ToNumber)   { return $false }
    return $true
}

# === 対象検出 ===
# 役割分担（2026-07-18 ユーザー確定「刑法58件未生成の分をR再生成と併せる」・TJR のストリーム別科目自動充当と対）：
#   T: フロンティア前進＝PDF あり かつ 公式 HTML 未生成 かつ 番号 > 公式の最大既存番号。
#   R: さかのぼり＝(a) 旧版_lex（v13 でない）の再生成 ＋ (b) 公式最大番号以下の欠番補完
#      （PDF あり・公式なし＝過去帯の未生成穴。例：刑法 15-54/304-309/312-323 の 58 件）。
#   T と R は「公式最大番号」を境に番号集合が重ならないため、同一科目で同じ番号を
#   同一バッチ内に二重処理することは構造上ない。欠番帯を明示処理したい時は R をピン（-RFrom/-RTo）。
$MaxOfficial = 0
foreach ($f in @(Get-ChildItem -Path $OfficialDir -Filter "${Prefix}TX*.html" -File -ErrorAction SilentlyContinue)) {
    if ($f.BaseName -match '(\d+)$') { $mn = [int]$Matches[1]; if ($mn -gt $MaxOfficial) { $MaxOfficial = $mn } }
}
$Pending = @()
if ($Regen) {
    $seen = @{}
    # --- (a) 旧版 _lex の再生成 ---
    foreach ($lex in @(Get-ChildItem -Path $LexDir -Filter "*_lex.html" -File -ErrorAction SilentlyContinue | Sort-Object Name)) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($lex.Name)   # 例 刑TX125_lex
        if ($stem -notmatch '(\d+)_lex$') { continue }
        $n = [int]$Matches[1]
        if (-not (Test-InRange $n)) { continue }
        # 版判定：footer feature-tag 'TX v13.<minor>.<patch> LOOP-CARD' を全文走査（先頭だけ見ると
        # footer を読めず旧版誤判定するため Select-String で全文一致）。
        # R（PDF→再生成）が作り直すのは「まだ v13 世代でない」旧版（v11.x / タグ無し）だけ。
        # 既に v13 世代なら SKIP：
        #   - v13.1.0（最新）    ＝ 何もしない（再生成すると査読済み内容を捨てて金を溶かす）。
        #   - v13.0.0（1つ前）   ＝ v13.0.0→v13.1.0 は内容保存の verdict-redesign 経路（別作業・
        #                          docs/tx-v13-migration-targets.md）で上げる。PDF から作り直さない。
        # 旧マーカー 'v13\.0\.0' だけを見る実装は v13.1.0（'v13.0.0' 文字列を含まない）を旧版扱いして
        # 再生成する重大バグだったため、v13 世代全体を一致させる形へ修正（版が上がっても耐える）。
        $alreadyV13 = [bool](Select-String -LiteralPath $lex.FullName -Pattern 'TX v13\.\d+\.\d+ LOOP-CARD' -Quiet -ErrorAction SilentlyContinue)
        if ($alreadyV13) { continue }
        if (-not $PdfMap.ContainsKey($n)) {
            Write-Host "[R-SKIP-NOPDF] ${Prefix}TX$($n.ToString('000'))：旧版だが入力PDFが無く再生成不能（Drive復元後に再対象化）" -ForegroundColor Magenta
            continue
        }
        $seen[$n] = $true
        $num = $n.ToString('000')
        $Pending += [PSCustomObject]@{
            Number=$num; ProblemId="${Prefix}TX${num}"; PdfPath=$PdfMap[$n]
            OfficialPath=(Join-Path $OfficialDir "${Prefix}TX${num}.html")
            LexPath=(Join-Path $LexDir "${Prefix}TX${num}_lex.html")
            Reason='旧_lex最新化'
        }
    }
    # --- (b) 公式最大番号以下の欠番補完（過去帯の未生成穴＝_lex も公式も無い番号）---
    foreach ($n in ($PdfMap.Keys | Sort-Object)) {
        if ($seen.ContainsKey($n)) { continue }
        if (-not (Test-InRange $n)) { continue }
        if ($n -gt $MaxOfficial) { continue }   # フロンティアの先は T の領分
        $num = $n.ToString('000')
        $official = Join-Path $OfficialDir "${Prefix}TX${num}.html"
        if (Test-Path $official) { continue }
        $Pending += [PSCustomObject]@{
            Number=$num; ProblemId="${Prefix}TX${num}"; PdfPath=$PdfMap[$n]
            OfficialPath=$official
            LexPath=(Join-Path $LexDir "${Prefix}TX${num}_lex.html")
            Reason='欠番補完'
        }
    }
    $Pending = @($Pending | Sort-Object { [int]$_.Number })
} else {
    foreach ($n in ($PdfMap.Keys | Sort-Object)) {
        if (-not (Test-InRange $n)) { continue }
        if ($n -le $MaxOfficial) { continue }   # 過去帯の欠番は R（さかのぼり）の領分＝二重処理防止
        $num = $n.ToString('000')
        $official = Join-Path $OfficialDir "${Prefix}TX${num}.html"
        if (Test-Path $official) { continue }   # 既存＝新規対象外（上書きは -Regen で）
        $Pending += [PSCustomObject]@{
            Number=$num; ProblemId="${Prefix}TX${num}"; PdfPath=$PdfMap[$n]
            OfficialPath=$official
            LexPath=(Join-Path $LexDir "${Prefix}TX${num}_lex.html")
            Reason='新規'
        }
    }
}

Write-Host "`n$modeText 対象: $($Pending.Count) 件（本起動で最大 $MaxProblems 件）" -ForegroundColor Yellow
$Targets = @($Pending | Select-Object -First $MaxProblems)
foreach ($t in $Targets) { Write-Host "  - $($t.ProblemId)  <- $($t.PdfPath)" }

if ($Targets.Count -eq 0) { Write-Host "対象なし、終了。" -ForegroundColor Green; Stop-Transcript | Out-Null; exit 0 }
if ($DryRun) { Write-Host "`n[DRY-RUN] claude -p / validate / commit はスキップ。" -ForegroundColor Yellow; Stop-Transcript | Out-Null; exit 0 }

if (-not (Test-Path $CostCsv)) { "timestamp,problem_id,mode,elapsed,official_bytes,lex_bytes,sentinel,exit,validate,committed" | Out-File -FilePath $CostCsv -Encoding utf8 }

# === claude -p 起動ヘルパ（stdin パイプ・model 固定・実行指示前置）===
function Invoke-ClaudeHeadless {
    param([string]$Prompt, [string]$JsonOutPath)
    $claudeArgs = @('-p','--model','claude-opus-4-8[1m]','--output-format','json','--permission-mode','acceptEdits','--allowedTools','Write,Edit,Read,Bash,Glob,Grep')
    try { $out = $Prompt | & claude @claudeArgs 2>&1; $code = $LASTEXITCODE } catch { $out = "$_"; $code = -1 }
    $out | Out-File -FilePath $JsonOutPath -Encoding utf8
    return [PSCustomObject]@{ Output = ($out -join "`n"); ExitCode = $code }
}

# === 1 問処理ループ ===
$ConsecutiveFailures = 0
$Processed = 0
foreach ($t in $Targets) {
    $startTime = Get-Date
    Write-Host "`n==================== [$($t.ProblemId)] $modeText ====================" -ForegroundColor Cyan

    # プロンプト組み立て（実行指示を前置＝参照資料誤認による挨拶終了の防止）
    $tmpl = Get-Content $PromptSource -Raw -Encoding utf8
    $prompt = $tmpl `
        -replace '\{TARGET_PDF\}',       $t.PdfPath `
        -replace '\{PROBLEM_NUMBER\}',   $t.Number `
        -replace '\{PROBLEM_ID\}',       $t.ProblemId `
        -replace '\{OFFICIAL_PATH\}',    $t.OfficialPath `
        -replace '\{LEX_PATH\}',         $t.LexPath `
        -replace '\{SUBJECT_PREFIX\}',   $Prefix `
        -replace '\{SUBJECT_FOLDER\}',   $SubjectFolder `
        -replace '\{CANONICAL_PATH\}',   $Canonical `
        -replace '\{SOLVENAV_PATH\}',    $SolveNav `
        -replace '\{REGEN_FLAG\}',       ($(if ($Regen -and $t.Reason -eq '欠番補完') { 'NEW（過去帯欠番の補完生成・既存ファイルなし）' } elseif ($Regen) { 'REGEN（既存の旧_lexと公式を最新v13で上書き）' } else { 'NEW（新規生成）' }))
    $execHeader = @"
【最優先・実行指示 / headless】これは参照資料ではなく実行命令である。あなたは今すぐ TX 問題
$($t.ProblemId) を v13.0.0 二系統（公式＝本物5択／_lex＝ox-grid＋解法ナビ＋物語解説）で生成せよ。
挨拶・確認・要約・「依頼内容が不明」等の応答は禁止。下記手順書に厳密に従い、対象PDFを読解して
直ちに着手し、公式＝$($t.OfficialPath)／_lex＝$($t.LexPath) の2ファイルを出力し、最後に必ず
sentinel（BATCH_ITEM_COMPLETED:$($t.ProblemId) 等）を出力して終了せよ。区分=$(if($Regen){'REGEN・既存上書き可'}else{'NEW'})。
━━━━━━━━━━━━━━━━ 以下、手順書本体 ━━━━━━━━━━━━━━━━

"@
    $prompt = $execHeader + $prompt
    $prompt | Out-File -FilePath (Join-Path $LogsDir "tx-v13-prompt-$($t.ProblemId).txt") -Encoding utf8

    Write-Host "[INFO] claude -p 起動中（推定 20-35 分）..."
    $res = Invoke-ClaudeHeadless -Prompt $prompt -JsonOutPath (Join-Path $LogsDir "tx-v13-$($t.ProblemId).json")
    $exitCode = $res.ExitCode
    $elapsed = [int]((Get-Date) - $startTime).TotalSeconds

    # sentinel grep
    $sentinel = "UNKNOWN"
    $esc = [regex]::Escape($t.ProblemId)
    if     ($res.Output -match "BATCH_ITEM_COMPLETED:$esc(\b|`$)") { $sentinel = "COMPLETED" }
    elseif ($res.Output -match "BATCH_ITEM_COMPLETED_WITH_ISSUES:$esc") { $sentinel = "WITH_ISSUES" }
    elseif ($res.Output -match "BATCH_ITEM_FAILED:$esc") { $sentinel = "FAILED" }

    $offBytes = if (Test-Path $t.OfficialPath) { (Get-Item $t.OfficialPath).Length } else { 0 }
    $lexBytes = if (Test-Path $t.LexPath)      { (Get-Item $t.LexPath).Length }      else { 0 }
    Write-Host "[DONE] elapsed=$([math]::Round($elapsed/60,1))min official=$offBytes lex=$lexBytes sentinel=$sentinel exit=$exitCode"

    # === 検証（公式・_lex 両方）===
    $validate = "skipped"
    $committed = $false
    if ($offBytes -gt 0 -and $lexBytes -gt 0 -and $sentinel -ne "FAILED") {
        Write-Host "--- validate-tx-core（_lex＝ox-grid必須／公式＝single・multi可）---"
        $vLex = & python $ValidateCore $t.LexPath 2>&1;      $vLexCode = $LASTEXITCODE
        $vOff = & python $ValidateCore $t.OfficialPath 2>&1; $vOffCode = $LASTEXITCODE
        ($vLex -join "`n") | Out-File -FilePath (Join-Path $LogsDir "tx-v13-validate-lex-$($t.ProblemId).txt") -Encoding utf8
        ($vOff -join "`n") | Out-File -FilePath (Join-Path $LogsDir "tx-v13-validate-off-$($t.ProblemId).txt") -Encoding utf8
        # エンジン整合（script2本・G41）
        if (Test-Path $CheckEngine) { $vEng = & python $CheckEngine $t.LexPath 2>&1; $vEngCode = $LASTEXITCODE } else { $vEngCode = 0 }
        # ox-grid 健全性（strict）：特殊型の全○退化(L4)・○×矛盾(L1)・組合せ当否(L2/L3)を弾く。
        # 再生成が判別性ある○×になっていなければ ERROR で commit させない（新規は必ず改善して通す）。
        if (Test-Path $CheckOxGrid) { $vOx = & python $CheckOxGrid $t.LexPath 2>&1; $vOxCode = $LASTEXITCODE } else { $vOxCode = 0 }
        ($vOx -join "`n") | Out-File -FilePath (Join-Path $LogsDir "tx-v13-oxgrid-$($t.ProblemId).txt") -Encoding utf8
        if ($vLexCode -eq 0 -and $vOffCode -eq 0 -and $vEngCode -eq 0 -and $vOxCode -eq 0) {
            $validate = "PASS"
            Write-Host "[validate] PASS（_lex/公式/エンジン/ox-grid）" -ForegroundColor Green
        } else {
            $validate = "ERROR(lex=$vLexCode,off=$vOffCode,eng=$vEngCode,ox=$vOxCode)"
            Write-Host "[validate] ERROR lex=$vLexCode off=$vOffCode eng=$vEngCode ox=$vOxCode — commit しない" -ForegroundColor Yellow
        }
    } else {
        $validate = "skipped_incomplete"
        Write-Host "[validate] スキップ（出力不完全 or FAILED）" -ForegroundColor Yellow
    }

    # === 作成日時スタンプ＋git commit/push（validate PASS 時のみ）===
    if ($validate -eq "PASS" -and -not $NoCommit) {
        try { if (Test-Path $StampScript) { & python $StampScript 2>&1 | Out-Null } } catch {}
        try {
            & git -C $ProjectRoot add -- $t.OfficialPath $t.LexPath 2>&1 | Out-Null
            $msg = if ($Regen -and $t.Reason -eq '欠番補完') { "feat($($Prefix)TX): $($t.ProblemId) を v13 で補完生成（過去帯欠番・二系統）" }
                   elseif ($Regen) { "feat($($Prefix)TX): $($t.ProblemId) を v13 で再生成（旧_lex最新化・二系統）" }
                   else            { "feat($($Prefix)TX): $($t.ProblemId) を二系統生成（公式5択／Lexia用 ox-grid＋解法ナビ）" }
            & git -C $ProjectRoot commit -m $msg 2>&1 | Out-Null
            $committed = $true
            $pushed = $false
            if (-not $NoPush) {
                for ($try=1; $try -le 3; $try++) {
                    & git -C $ProjectRoot push 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) { $pushed = $true; break }
                    # 別PCの並行 push に先行されると fetch-first 拒否で3回とも同じ失敗になるため、
                    # リトライ前に rebase で追随（autoStash＝settings.local.json 等の未staged差分を退避）。
                    # 旧実装は追随なし＋失敗でも「push 済」表示＝未pushコミット滞留の実害（刑訴TX038-042/刑TX057-059）。
                    & git -C $ProjectRoot -c rebase.autoStash=true pull --rebase 2>&1 | Out-Null
                    Start-Sleep -Seconds ([Math]::Min(30, 5 * $try))
                }
            }
            if ($NoPush)      { Write-Host "[COMMIT] $($t.ProblemId) 永続化（commit のみ・-NoPush）" -ForegroundColor Green }
            elseif ($pushed)  { Write-Host "[COMMIT] $($t.ProblemId) 永続化（push 済）" -ForegroundColor Green }
            else              { Write-Host "[COMMIT] $($t.ProblemId) commit 済・push 未了（リモート先行。次問の push か手動回収で反映）" -ForegroundColor Yellow }
        } catch { Write-Host "[COMMIT FAIL] $_" -ForegroundColor Yellow }
    }

    Add-Content -Path $CostCsv -Encoding utf8 -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$($t.ProblemId),$modeText,$elapsed,$offBytes,$lexBytes,$sentinel,$exitCode,$validate,$committed")

    # 連続失敗判定
    if ($sentinel -eq "FAILED" -or $exitCode -ne 0 -or $offBytes -eq 0 -or $lexBytes -eq 0 -or $validate -notlike "PASS*") {
        $ConsecutiveFailures++
        Write-Host "[WARN] 連続失敗 $ConsecutiveFailures / $MaxConsecutiveFailures" -ForegroundColor Yellow
        if ($ConsecutiveFailures -ge $MaxConsecutiveFailures) { Write-Host "[ABORT] 連続失敗上限。中断。" -ForegroundColor Red; break }
    } else { $ConsecutiveFailures = 0 }
    $Processed++
}

Write-Host "`n=== tx-v13-runner 終了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 処理 $Processed / $($Targets.Count) ===" -ForegroundColor Cyan

# バッチ後監査：ファイル間重複・ID 不整合
if (Test-Path (Join-Path $ProjectRoot 'scripts\check-duplicates.py')) {
    Write-Host "--- 監査: check-duplicates.py outputs ---" -ForegroundColor Cyan
    # 出力を捕捉して host へ流す（success ストリームに漏らさない）。TJR が & 呼び出しで
    # このランナーを走らせるとき、ここの stdout が戻り値に混じると exit コードが配列化する。
    $dupOut = & python (Join-Path $ProjectRoot 'scripts\check-duplicates.py') (Join-Path $ProjectRoot 'outputs') 2>&1
    $dupCode = $LASTEXITCODE
    $dupOut | ForEach-Object { Write-Host $_ }
    if ($dupCode -ne 0) { Write-Host "[AUDIT FAIL] 重複/ID不整合を検出（push前に修正）。" -ForegroundColor Red }
}

Stop-Transcript | Out-Null
exit 0
