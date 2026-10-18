# tx-v13-runner.ps1 — TJR の TX エンジン（T＝新規TX ／ R＝欠番補完 ／ F＝修復の共通エンジン）
#
# 【役割】v13.1.0 LOOP-CARD の **公式 1 ファイル**（outputs/000_TX ＝本物の5択＋v13 記述カード・BASIS・
#   体系マップ）を headless（claude -p）で 1 問ずつ生成し、validate-tx-core → 作成日時スタンプ →
#   git commit/push まで通す。旧 night-batch-runner（v10 GOLD-SKELETON・単一ファイル）の後継。
#   TJR.ps1 から呼ばれる内部エンジン（直接叩いてもよいが、通常は「TJR処理」経由）。
#
# 【公式のみ・2026-10-18 ユーザー指示】二系統（公式＋Lexia 用 _lex）を廃止し、TJR は公式だけを作る。
#   _lex（outputs/ux/000_TX）は作らない・触らない（既存 _lex はそのまま残す＝G/D/I 等の付随ストリームの領分）。
#   Lexia は _lex の無い問題を公式から問題単位で取り込む（filterLexiaImportable の既存フォールバック）。
#   「_lex を正本にする」1 ファイル方式は司法書士版（shoshi-exam の STX）の側で採る。
#
# 【T モード（既定）】フロンティア前進＝inputs/000_TX/{科目}/*.pdf のうち公式 HTML 未生成 かつ
#   番号が「公式の最大既存番号」より先のものを最若番から生成（過去帯の欠番は R の領分＝二重処理防止）。
# 【R モード（-Regen）】さかのぼり＝公式最大番号以下の欠番（PDFあり・公式なし）の補完生成
#   （2026-07-18 ユーザー確定「刑法58件未生成の分をR再生成と併せる」）。旧版 _lex の作り直し（旧 R(a)）は
#   _lex を作らない方針により 2026-10-18 に廃止した。
# 【F モード（-RepairIds '60,125'）】修復＝tjr-audit.py が検出したエラー品・未完成品（公式欠落・
#   途切れ・検証FAILの残骸等）を番号直指定で PDF から再生成する（2026-07-24 新設・TJR-F ストリーム用）。
#   破損ファイルは「存在する」ため T/R の検出からは不可視＝この経路だけが回収できる。修復も公式だけを作る。
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
    [switch]$Regen,                 # R モード（公式最大番号以下の欠番を補完生成）
    [string]$RepairIds = '',        # F モード（TJR-F 修復）：カンマ/空白区切りの番号列（例 '60,125'）。
                                    #   tjr-audit.py が検出したエラー品・未完成品を、T/R の対象検出
                                    #   （フロンティア・版判定・欠番）をバイパスして番号直指定で再生成する。
                                    #   指定時は該当番号だけを処理（Regen/From/To より優先）。
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
$LogsDir       = Join-Path $ProjectRoot "logs"
$PromptSource  = Join-Path $ProjectRoot "prompts\new-tx-headless-v13.md"
$Canonical     = Join-Path $ProjectRoot "canonical\GENESIS-CARD.html"
$ValidateCore  = Join-Path $ProjectRoot "scripts\validate-tx-core.py"
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

# === TJR claim ライブラリ（二台同時実行の衝突対策・2026-07-27）===
#   claim 予約＋安全 push（first-push-wins・rebase 途中放置の禁止）。正典 docs/run-patterns.md。
. (Join-Path $ProjectRoot 'scripts\tjr-claim.ps1')

# === スリープ抑止（DryRun 以外・feedback_nbr_keep_awake）===
if (-not $DryRun) {
    try {
        $sig = '[DllImport("kernel32.dll", SetLastError=true)] public static extern uint SetThreadExecutionState(uint esFlags);'
        $PW = Add-Type -MemberDefinition $sig -Name PW -Namespace Win32 -PassThru -ErrorAction Stop
        [void]$PW::SetThreadExecutionState([uint32]2147483651)  # ES_CONTINUOUS|ES_SYSTEM_REQUIRED|ES_DISPLAY_REQUIRED
        Write-Host "[KEEP-AWAKE] スリープ抑止 ON（プロセス終了で自動復帰）" -ForegroundColor DarkGray
    } catch { Write-Host "[KEEP-AWAKE] 抑止設定に失敗（続行）: $($_.Exception.Message)" -ForegroundColor Yellow }
}

$modeText = if ($RepairIds) { 'F（修復再生成）' } elseif ($Regen) { 'R（欠番補完）' } else { 'T（新規TX）' }
Write-Host "=== tx-v13-runner 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "Subject=$Subject ($SubjectFolder) / モード=$modeText / MaxProblems=$MaxProblems / 範囲 From=$FromNumber To=$ToNumber / DryRun=$DryRun"
Write-Host "PDF=$PdfDir"
Write-Host "公式=$OfficialDir（公式のみ生成・_lex は作らない）"

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
if (-not (Test-Path $OfficialDir)) { New-Item -Path $OfficialDir -ItemType Directory -Force | Out-Null }

# === 対象検出の前にリモート先行分へ追随（2026-07-27）===
#   pull を怠った側が相手 PC の生成済み番号を「未生成」と誤認して作り直す事故経路を塞ぐ。
#   （旧実装は起動時 pull が無く、push 失敗後のリトライ内でしか追随しなかった）
if (-not $DryRun) { [void](Sync-TjrRepo -ProjectRoot $ProjectRoot) }

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
#   R: さかのぼり＝公式最大番号以下の欠番補完
#      （PDF あり・公式なし＝過去帯の未生成穴。例：刑法 15-54/304-309/312-323 の 58 件）。
#      旧 R(a)（旧版 _lex の作り直し）は 2026-10-18 の公式のみ方針で廃止。
#   T と R は「公式最大番号」を境に番号集合が重ならないため、同一科目で同じ番号を
#   同一バッチ内に二重処理することは構造上ない。欠番帯を明示処理したい時は R をピン（-RFrom/-RTo）。
$MaxOfficial = 0
foreach ($f in @(Get-ChildItem -Path $OfficialDir -Filter "${Prefix}TX*.html" -File -ErrorAction SilentlyContinue)) {
    if ($f.BaseName -match '(\d+)$') { $mn = [int]$Matches[1]; if ($mn -gt $MaxOfficial) { $MaxOfficial = $mn } }
}
$Pending = @()
if ($RepairIds) {
    # --- F モード（TJR-F 修復）：tjr-audit.py が検出したエラー品・未完成品の番号直指定再生成 ---
    # 破損した公式は「存在する」ため T（Test-Path で SKIP）・R（公式ありで SKIP）の
    # いずれからも不可視になる。F はその検出バイパス経路。
    foreach ($tok in @($RepairIds -split '[,\s]+')) {
        if ($tok -notmatch '^\d+$') { continue }
        $n = [int]$tok
        if (-not $PdfMap.ContainsKey($n)) {
            Write-Host "[F-SKIP-NOPDF] ${Prefix}TX$($n.ToString('000'))：入力PDFが無く修復再生成不能（Drive復元後に再対象化）" -ForegroundColor Magenta
            continue
        }
        $num = $n.ToString('000')
        $Pending += [PSCustomObject]@{
            Number=$num; ProblemId="${Prefix}TX${num}"; PdfPath=$PdfMap[$n]
            OfficialPath=(Join-Path $OfficialDir "${Prefix}TX${num}.html")
            Reason='修復再生成'
        }
    }
    $Pending = @($Pending | Sort-Object { [int]$_.Number })
} elseif ($Regen) {
    # --- 公式最大番号以下の欠番補完（過去帯の未生成穴＝公式の無い番号）---
    foreach ($n in ($PdfMap.Keys | Sort-Object)) {
        if (-not (Test-InRange $n)) { continue }
        if ($n -gt $MaxOfficial) { continue }   # フロンティアの先は T の領分
        $num = $n.ToString('000')
        $official = Join-Path $OfficialDir "${Prefix}TX${num}.html"
        if (Test-Path $official) { continue }
        $Pending += [PSCustomObject]@{
            Number=$num; ProblemId="${Prefix}TX${num}"; PdfPath=$PdfMap[$n]
            OfficialPath=$official
            Reason='欠番補完'
        }
    }
} else {
    foreach ($n in ($PdfMap.Keys | Sort-Object)) {
        if (-not (Test-InRange $n)) { continue }
        if ($n -le $MaxOfficial) { continue }   # 過去帯の欠番は R（さかのぼり）の領分＝二重処理防止
        $num = $n.ToString('000')
        $official = Join-Path $OfficialDir "${Prefix}TX${num}.html"
        if (Test-Path $official) { continue }   # 既存＝新規対象外（上書きは -RepairIds で）
        $Pending += [PSCustomObject]@{
            Number=$num; ProblemId="${Prefix}TX${num}"; PdfPath=$PdfMap[$n]
            OfficialPath=$official
            Reason='新規'
        }
    }
}

Write-Host "`n$modeText 対象: $($Pending.Count) 件（本起動で最大 $MaxProblems 件・相手 PC の claim 先取り分は次候補へ繰り上げ）" -ForegroundColor Yellow
$Targets = @($Pending | Select-Object -First $MaxProblems)   # 当初候補の表示用（実際の着手は claim 取得順）
foreach ($t in $Targets) { Write-Host "  - $($t.ProblemId)  <- $($t.PdfPath)" }

if ($Targets.Count -eq 0) { Write-Host "対象なし、終了。" -ForegroundColor Green; Stop-Transcript | Out-Null; exit 0 }
if ($DryRun) { Write-Host "`n[DRY-RUN] claude -p / validate / commit はスキップ。" -ForegroundColor Yellow; Stop-Transcript | Out-Null; exit 0 }

if (-not (Test-Path $CostCsv)) { "timestamp,problem_id,mode,elapsed,official_bytes,lex_bytes,sentinel,exit,validate,committed" | Out-File -FilePath $CostCsv -Encoding utf8 }

# === claude -p 起動ヘルパ（stdin パイプ・model 固定・実行指示前置）===
function Invoke-ClaudeHeadless {
    param([string]$Prompt, [string]$JsonOutPath)
    $claudeArgs = @('-p','--model','claude-opus-5[1m]','--output-format','json','--permission-mode','acceptEdits','--allowedTools','Write,Edit,Read,Bash,Glob,Grep')
    try { $out = $Prompt | & claude @claudeArgs 2>&1; $code = $LASTEXITCODE } catch { $out = "$_"; $code = -1 }
    $out | Out-File -FilePath $JsonOutPath -Encoding utf8
    return [PSCustomObject]@{ Output = ($out -join "`n"); ExitCode = $code }
}

# === 1 問処理ループ ===
#   $Pending 全体を候補に、claim が取れた問題から着手する（着手数は $MaxProblems で打ち止め）。
#   相手 PC に先取りされた番号は SKIP して次候補へ繰り上げ＝2 台が交互に番号を取り合って前進する。
$ConsecutiveFailures = 0
$Processed = 0
$Attempted = 0
foreach ($t in $Pending) {
    if ($Attempted -ge $MaxProblems) { break }
    Write-Host "`n==================== [$($t.ProblemId)] $modeText ====================" -ForegroundColor Cyan

    # ----- claim 予約（二台同時 TJR の同番号二重生成を防止・2026-07-27）-----
    $claimStatus = 'CLAIMED_OFFLINE'
    if (-not $NoCommit -and -not $NoPush) {
        if ($t.Reason -eq '修復再生成') {
            $existsRel = @()   # 破損品の上書き修復＝存在が前提。claim だけで直列化
        } else {
            # 新規／欠番補完＝リモートに公式が出現していれば相手 PC が完成済み
            $existsRel = @( (ConvertTo-TjrRelPath $ProjectRoot $t.OfficialPath) )
        }
        $claimStatus = Request-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $t.ProblemId -Stream $modeText -TtlMinutes 150 -RemoteExistsRelPaths $existsRel
        if ($claimStatus -in @('REMOTE_EXISTS', 'CLAIMED_BY_OTHER', 'ERROR')) { continue }
    }
    $Attempted++
    $startTime = Get-Date

    # プロンプト組み立て（実行指示を前置＝参照資料誤認による挨拶終了の防止）
    $tmpl = Get-Content $PromptSource -Raw -Encoding utf8
    $prompt = $tmpl `
        -replace '\{TARGET_PDF\}',       $t.PdfPath `
        -replace '\{PROBLEM_NUMBER\}',   $t.Number `
        -replace '\{PROBLEM_ID\}',       $t.ProblemId `
        -replace '\{OFFICIAL_PATH\}',    $t.OfficialPath `
        -replace '\{SUBJECT_PREFIX\}',   $Prefix `
        -replace '\{SUBJECT_FOLDER\}',   $SubjectFolder `
        -replace '\{CANONICAL_PATH\}',   $Canonical `
        -replace '\{REGEN_FLAG\}',       ($(if ($t.Reason -eq '修復再生成') { 'REGEN（エラー品・未完成品の修復再生成＝既存の公式を最新v13で上書き）' } elseif ($Regen) { 'NEW（過去帯欠番の補完生成・既存ファイルなし）' } else { 'NEW（新規生成）' }))
    $execHeader = @"
【最優先・実行指示 / headless】これは参照資料ではなく実行命令である。あなたは今すぐ TX 問題
$($t.ProblemId) を v13.1.0 LOOP-CARD の公式 1 ファイル（本物の5択＋v13 記述カード）で生成せよ。
Lexia 用 _lex（outputs/ux/000_TX）は作らない。
挨拶・確認・要約・「依頼内容が不明」等の応答は禁止。下記手順書に厳密に従い、対象PDFを読解して
直ちに着手し、公式＝$($t.OfficialPath) の1ファイルを出力し、最後に必ず
sentinel（BATCH_ITEM_COMPLETED:$($t.ProblemId) 等）を出力して終了せよ。区分=$(if($t.Reason -eq '修復再生成'){'REGEN・既存上書き可（破損品の修復）'}else{'NEW'})。
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
    Write-Host "[DONE] elapsed=$([math]::Round($elapsed/60,1))min official=$offBytes sentinel=$sentinel exit=$exitCode"

    # === 検証（公式）===
    #   解法ナビ engine（check-tx-lex-engine）と ox-grid 健全性（check-lex-oxgrid-integrity）は _lex 専用＝公式には掛けない。
    $validate = "skipped"
    $committed = $false
    if ($offBytes -gt 0 -and $sentinel -ne "FAILED") {
        Write-Host "--- validate-tx-core（公式＝single・multi）---"
        $vOff = & python -X utf8 $ValidateCore $t.OfficialPath 2>&1; $vOffCode = $LASTEXITCODE
        ($vOff -join "`n") | Out-File -FilePath (Join-Path $LogsDir "tx-v13-validate-off-$($t.ProblemId).txt") -Encoding utf8
        if ($vOffCode -eq 0) {
            $validate = "PASS"
            Write-Host "[validate] PASS（公式）" -ForegroundColor Green
        } else {
            $validate = "ERROR(off=$vOffCode)"
            Write-Host "[validate] ERROR off=$vOffCode — commit しない" -ForegroundColor Yellow
        }
    } else {
        $validate = "skipped_incomplete"
        Write-Host "[validate] スキップ（出力不完全 or FAILED）" -ForegroundColor Yellow
    }

    # === 作成日時スタンプ＋git commit/push（validate PASS 時のみ）===
    if ($validate -eq "PASS" -and -not $NoCommit) {
        try { if (Test-Path $StampScript) { & python $StampScript 2>&1 | Out-Null } } catch {}
        try {
            & git -C $ProjectRoot add -- $t.OfficialPath 2>&1 | Out-Null
            # claim 解放を同じ commit に同梱（予約→成果物→解放が 1 push で完結・2026-07-27）
            [void](Remove-TjrClaimLocal -ProjectRoot $ProjectRoot -ProblemId $t.ProblemId)
            $msg = if ($t.Reason -eq '修復再生成') { "fix($($Prefix)TX): $($t.ProblemId) を修復再生成（TJR-F・エラー品/未完成品の回収）" }
                   elseif ($Regen) { "feat($($Prefix)TX): $($t.ProblemId) を v13 で補完生成（過去帯欠番・公式5択）" }
                   else            { "feat($($Prefix)TX): $($t.ProblemId) を生成（公式5択）" }
            & git -C $ProjectRoot commit -m $msg 2>&1 | Out-Null
            $committed = $true
            $pushed = $false
            if (-not $NoPush) {
                # 安全 push（2026-07-27・tjr-claim.ps1）: push 拒否 → pull --rebase -X ours（同一
                # ファイル衝突はリモート先着版を採用＝first-push-wins・自コミットは空化して自動 drop）
                # → 再 push。解決不能な競合は必ず rebase --abort で復帰して commit をローカル保持。
                # 旧実装の素の pull --rebase は同一ファイル add/add で rebase を途中放置し、
                # 以降の全問の commit が unmerged paths で失敗する連鎖があった。
                $pushed = Invoke-TjrSafePush -ProjectRoot $ProjectRoot -MaxTries 3 -Label $t.ProblemId
            }
            if ($NoPush)      { Write-Host "[COMMIT] $($t.ProblemId) 永続化（commit のみ・-NoPush）" -ForegroundColor Green }
            elseif ($pushed)  { Write-Host "[COMMIT] $($t.ProblemId) 永続化（push 済）" -ForegroundColor Green }
            else              { Write-Host "[COMMIT] $($t.ProblemId) commit 済・push 未了（リモート先行。次問の push か手動回収で反映）" -ForegroundColor Yellow }
        } catch { Write-Host "[COMMIT FAIL] $_" -ForegroundColor Yellow }
    }

    if (-not $committed -and $claimStatus -eq 'CLAIMED') {
        # 検証 NG・出力不完全・commit 失敗などで成果物が載らない場合は予約を解放
        # （相手 PC／次回 TJR-F が着手できるようにする。解放漏れは TTL 失効＋掃除が回収）
        Release-TjrClaim -ProjectRoot $ProjectRoot -ProblemId $t.ProblemId -Reason '生成/検証失敗' -NoPush:$NoPush
    }

    # lex_bytes 列は二系統期の CSV と列をそろえるため残す（公式のみになった 2026-10-18 以降は常に 0）
    Add-Content -Path $CostCsv -Encoding utf8 -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$($t.ProblemId),$modeText,$elapsed,$offBytes,0,$sentinel,$exitCode,$validate,$committed")

    # 連続失敗判定
    if ($sentinel -eq "FAILED" -or $exitCode -ne 0 -or $offBytes -eq 0 -or $validate -notlike "PASS*") {
        $ConsecutiveFailures++
        Write-Host "[WARN] 連続失敗 $ConsecutiveFailures / $MaxConsecutiveFailures" -ForegroundColor Yellow
        if ($ConsecutiveFailures -ge $MaxConsecutiveFailures) { Write-Host "[ABORT] 連続失敗上限。中断。" -ForegroundColor Red; break }
    } else { $ConsecutiveFailures = 0 }
    $Processed++
}

Write-Host "`n=== tx-v13-runner 終了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 処理 $Processed / 着手 $Attempted（候補 $($Pending.Count) 件・最大 $MaxProblems）===" -ForegroundColor Cyan

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
