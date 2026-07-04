# TJR.ps1 — 大元の号令（TX新規＝T ／ JX新規＝J ／ 旧版TXLEX再生成＝R を1本で束ねる指揮者）
#
# 【位置づけ】2026-07-04 確定・ユーザー指示で旧パターン（TX-MARCH / TX-PICK / JX）を廃止し、
#   本 TJR を現行版の唯一の入口にする。TJR は「指揮者」であり、重い生成ロジックは持たない。
#   実生成は各エンジンへ委譲：
#     T（新規TX）    : scripts\tx-v13-runner.ps1              … v13 二系統（公式 000_TX ＋ Lexia _lex）
#     R（旧_lex再生成）: scripts\tx-v13-runner.ps1 -Regen      … PDFから最新v13で作り直す（公式も同時に最新化）
#     J（新規JX）    : scripts\jx-batch-runner.ps1（内部エンジン）… JX＋副産物RX/TREE/ARIADNE＋台本
#
# 【号令なら指定外も当然に処理・2026-07-04 ユーザー指示】番号ピンは「そのストリームだけ範囲固定」で、
#   他ストリームは止めない。例「TX355 を TJR処理」→ T は 355 固定、J と R は通常どおり最若番から処理。
#   1ストリームだけ回したい時（旧・短縮形「TX 355-360 処理」）は -Only を付ける。
#
# 【科目検知順・2026-07-04 ユーザー指示】①刑法 ②刑事訴訟法 ③民法 ④民事訴訟法 ⑤商法 ⑥憲法 ⑦行政法。
#   -Subject 省略時はこの優先順で「仕事のある科目」を自動選択する（フォルダ番号順とは別＝下記 $SubjectOrder）。
#
# 【同時起動＝直列】1作業ツリーで並行すると git commit/push が衝突する実害が記録済み
#   （feedback_jx_concurrent_batch_gate_collision / feedback_shared_workdir_agent_collision）。よって T→J→R を直列。
#
# 使い方（号令）:
#   「TJR処理 刑訴」              → pwsh -NoProfile -File scripts/patterns/TJR.ps1 -Subject 刑訴
#   「TJR処理」(科目自動)          → ... TJR.ps1                       # 優先順で仕事のある科目を1つ
#   「TX355 を TJR処理」           → ... -Subject 刑訴 -TxFrom 355 -TxTo 355   # T=355固定・J/R=通常
#   「JX5 を TJR処理」             → ... -Subject 民 -JxFrom 5 -JxTo 5         # J=5固定・T/R=通常
#   短縮形「TX 355-360 処理」      → ... -Subject 刑 -Only T -TxFrom 355 -TxTo 360   # Tだけ
#   短縮形「JX 1-10 処理」         → ... -Subject 民 -Only J -JxFrom 1 -JxTo 10       # Jだけ
#   検出だけ                       → ... -Subject 刑訴 -DryRun
param(
    [ValidateSet('','刑','刑訴','民','民訴','商','憲','行政')]
    [string]$Subject = '',        # '' = 自動（$SubjectOrder の優先順で仕事のある科目を1つ選ぶ）
    # 番号ピン（各ストリームを範囲に固定。未指定＝そのストリームは最若番から通常処理）
    [int]$TxFrom = 0, [int]$TxTo = 0,
    [int]$JxFrom = 0, [int]$JxTo = 0,
    [int]$RFrom  = 0, [int]$RTo  = 0,
    # 単一ストリームに限定（既定は空＝T/J/R 全部走る。「指定外も当然に処理」の既定を上書きしたい時だけ）
    [ValidateSet('','T','J','R')]
    [string]$Only = '',
    [int]$MaxTX = 12,             # T の通常チャンク（ピン時は範囲全件）
    [int]$MaxJX = 3,             # J の通常チャンク
    [int]$MaxR  = 3,             # R の通常チャンク
    [switch]$NoPush,
    [switch]$DryRun,
    [string]$ProjectRoot = ''
)

# === プロジェクトルート解決（patterns\ の2つ上）===
$DefaultProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $env:BAREXAM_PROJECT_ROOT }
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = $DefaultProjectRoot }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

$TxRunner = Join-Path $ProjectRoot 'scripts\tx-v13-runner.ps1'
$JxRunner = Join-Path $ProjectRoot 'scripts\jx-batch-runner.ps1'

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# === 科目優先順（ユーザー指示・フォルダ番号順とは別）===
#   ①刑法 ②刑事訴訟法 ③民法 ④民事訴訟法 ⑤商法 ⑥憲法 ⑦行政法
$SubjectOrder = @('刑','刑訴','民','民訴','商','憲','行政')
$SubjectFolder = @{ '刑'='001_刑法'; '刑訴'='002_刑事訴訟法'; '民'='003_民法'; '商'='004_商法'; '民訴'='005_民事訴訟法'; '行政'='006_行政法'; '憲'='007_憲法' }

# === 科目ごとの「仕事あり」判定（自動科目選択用・粗い存在チェック）===
function Get-TxPending { param([string]$subj)
    $folder = $SubjectFolder[$subj]
    $pdfDir = Join-Path $ProjectRoot "inputs\000_TX\$folder"
    $outDir = Join-Path $ProjectRoot "outputs\000_TX\$folder"
    if (-not (Test-Path $pdfDir)) { return $false }
    foreach ($p in @(Get-ChildItem $pdfDir -Filter '*.pdf' -File -ErrorAction SilentlyContinue)) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($p.Name)
        if ($stem -notmatch '^\d+') { continue }
        $num = ([int]$Matches[0]).ToString('000')
        if (-not (Test-Path (Join-Path $outDir "${subj}TX${num}.html"))) { return $true }
    }
    return $false
}
function Get-RPending { param([string]$subj)
    $folder = $SubjectFolder[$subj]
    $lexDir = Join-Path $ProjectRoot "outputs\ux\000_TX\$folder"
    $pdfDir = Join-Path $ProjectRoot "inputs\000_TX\$folder"
    if (-not (Test-Path $lexDir)) { return $false }
    foreach ($lex in @(Get-ChildItem $lexDir -Filter '*_lex.html' -File -ErrorAction SilentlyContinue)) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($lex.Name)
        if ($stem -notmatch '(\d+)_lex$') { continue }
        $n = [int]$Matches[1]
        if (Select-String -LiteralPath $lex.FullName -Pattern 'v13\.0\.0' -Quiet -ErrorAction SilentlyContinue) { continue }
        if (Test-Path (Join-Path $pdfDir "$n.pdf")) { return $true }
        if (Test-Path (Join-Path $pdfDir ("{0}.pdf" -f ([int]$n)))) { return $true }
    }
    return $false
}
function Get-JxPending { param([string]$subj)
    $folder = $SubjectFolder[$subj]
    $base = Join-Path $ProjectRoot "inputs\001_JX\$folder"
    $outDir = Join-Path $ProjectRoot "outputs\001_JX\$folder"
    foreach ($d in @((Join-Path $base '重問PDF'), $base)) {
        if (-not (Test-Path $d)) { continue }
        foreach ($p in @(Get-ChildItem $d -Filter '*.pdf' -File -ErrorAction SilentlyContinue)) {
            $stem = [System.IO.Path]::GetFileNameWithoutExtension($p.Name)
            if ($stem -notmatch '^\d+') { continue }
            $num = ([int]$Matches[0]).ToString('000')
            if (-not (Test-Path (Join-Path $outDir "${subj}JX${num}.html"))) { return $true }
        }
    }
    return $false
}

# === 科目確定（-Subject 明示 or 自動＝優先順で最初に仕事のある科目）===
if ([string]::IsNullOrWhiteSpace($Subject)) {
    foreach ($s in $SubjectOrder) {
        if ((Get-TxPending $s) -or (Get-JxPending $s) -or (Get-RPending $s)) { $Subject = $s; break }
    }
    if ([string]::IsNullOrWhiteSpace($Subject)) {
        Write-Host "[TJR] 全科目で処理対象なし（T/J/R とも空）。終了。" -ForegroundColor Green
        exit 0
    }
    Write-Host "[TJR] 科目自動選択（優先順 $($SubjectOrder -join '>')）→ $Subject" -ForegroundColor Cyan
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TJR 処理  Subject=$Subject  Only=$(if($Only){$Only}else{'(全部)'})  DryRun=$DryRun" -ForegroundColor Cyan
Write-Host "  ピン: TX=$TxFrom-$TxTo  JX=$JxFrom-$JxTo  R=$RFrom-$RTo   チャンク T:$MaxTX J:$MaxJX R:$MaxR" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# === ストリーム実行ヘルパ ===
function Invoke-TxStream {
    param([switch]$Regen, [int]$Max, [int]$From, [int]$To)
    if (-not (Test-Path $TxRunner)) { Write-Host "[SKIP] TX エンジン不在: $TxRunner" -ForegroundColor Yellow; return 0 }
    $p = @{ Subject = $Subject; ProjectRoot = $ProjectRoot }
    if ($From -gt 0 -or $To -gt 0) {           # ピン：範囲全件
        $p.FromNumber = $From; $p.ToNumber = $To
        $p.MaxProblems = [Math]::Max(1, ($To - $From + 1))
    } else { $p.MaxProblems = $Max }           # 通常：最若番からチャンク
    if ($Regen)  { $p.Regen = $true }
    if ($NoPush) { $p.NoPush = $true }
    if ($DryRun) { $p.DryRun = $true }
    $label = if ($Regen) { 'R（旧_lex再生成）' } else { 'T（新規TX）' }
    Write-Host "`n———————— $label 開始 ————————" -ForegroundColor Green
    # 子ランナーが success ストリームに何か漏らしても（例: 監査 check-duplicates の stdout）、
    # それを関数戻り値に混ぜて $rcT を配列化させないため Out-Host で host へ流し、終了コードだけ返す。
    & $TxRunner @p | Out-Host
    return $LASTEXITCODE
}
function Invoke-JxStream {
    param([int]$Max, [int]$From, [int]$To)
    if (-not (Test-Path $JxRunner)) { Write-Host "[SKIP] JX エンジン不在: $JxRunner" -ForegroundColor Yellow; return 0 }
    $p = @{ Subject = $Subject; SkipAudio = $true; ProjectRoot = $ProjectRoot; Finalize = $true }
    if ($From -gt 0 -or $To -gt 0) {
        $p.FromNumber = $From; $p.ToNumber = $To
        $p.MaxProblems = [Math]::Max(1, ($To - $From + 1))
    } else { $p.MaxProblems = $Max }
    if ($NoPush) { $p.NoPush = $true }
    if ($DryRun) { $p.DryRun = $true }
    Write-Host "`n———————— J（新規JX＋副産物） 開始 ————————" -ForegroundColor Green
    # 同上：JX ランナーの success ストリーム漏れで $rcJ を配列化させない。
    & $JxRunner @p | Out-Host
    return $LASTEXITCODE
}

# === 実行（Only 指定が無ければ T→J→R を全部・直列）===
$runT = ($Only -eq '' -or $Only -eq 'T')
$runJ = ($Only -eq '' -or $Only -eq 'J')
$runR = ($Only -eq '' -or $Only -eq 'R')
$rcT = 0; $rcJ = 0; $rcR = 0
if ($runT) { $rcT = Invoke-TxStream          -Max $MaxTX -From $TxFrom -To $TxTo }
if ($runJ) { $rcJ = Invoke-JxStream          -Max $MaxJX -From $JxFrom -To $JxTo }
if ($runR) { $rcR = Invoke-TxStream -Regen   -Max $MaxR  -From $RFrom  -To $RTo }

Write-Host "`n———————— TJR 集計（$Subject）————————" -ForegroundColor Cyan
if ($runT) { Write-Host "  T（新規TX）  exit=$rcT" }
if ($runJ) { Write-Host "  J（新規JX）  exit=$rcJ" }
if ($runR) { Write-Host "  R（旧_lex）  exit=$rcR" }
$rc = if ($rcT -ne 0 -or $rcJ -ne 0 -or $rcR -ne 0) { 1 } else { 0 }
Write-Host "  TJR 終了 exit=$rc" -ForegroundColor Cyan
exit $rc
