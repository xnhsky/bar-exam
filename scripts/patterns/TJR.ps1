# TJR.ps1 — 大元の号令（TX新規＝T ／ JX新規＝J ／ 旧版TXLEX再生成＝R を1本で束ねる指揮者）
#
# 【位置づけ】2026-07-04 確定・ユーザー指示で旧パターン（TX-MARCH / TX-PICK / JX）を廃止し、
#   本 TJR を現行版の唯一の入口にする。TJR は「指揮者」であり、重い生成ロジックは持たない。
#   実生成は各エンジンへ委譲：
#     T（新規TX）    : scripts\tx-v13-runner.ps1              … v13 二系統（公式 000_TX ＋ Lexia _lex）
#     R（旧_lex再生成）: scripts\tx-v13-runner.ps1 -Regen      … PDFから最新v13で作り直す（公式も同時に最新化）
#     J（新規JX）    : scripts\jx-batch-runner.ps1（内部エンジン）… JX＋副産物RX/TREE/ARIADNE＋台本
#
# 【バッチ単位固定・2026-07-18 ユーザー確定】1バッチ＝ T:12問 / J:3問 / R:3問。ユーザーが
#   「TJRを○バッチ」と回数を指示する（-Batches N・バッチ間も直列）。勝手なチャンク拡大・
#   自動完遂ループは禁止（feedback_tjr_batch_unit_fixed）。
#
# 【科目はストリーム別に自動充当・2026-07-18 ユーザー確定】優先順（①刑法 ②刑事訴訟法 ③民法
#   ④民事訴訟法 ⑤商法 ⑥憲法 ⑦行政法）で、T・J・R **それぞれが独立に**「そのストリームに
#   仕事のある科目」を選ぶ（例：T=刑法が尽きていれば刑訴へ、R=刑法、J=刑法が尽きていれば刑訴へ）。
#   -Subject 明示時はその科目を最優先し、そのストリームに仕事が無ければ優先順の残りへフォールスルー。
#   R は過渡ストリーム＝全科目を遡って旧版_lexが無ければ「該当なし」スキップで良い（ユーザー確認 2026-07-18）。
#
# 【号令なら指定外も当然に処理・2026-07-04 ユーザー指示】番号ピンは「そのストリームだけ範囲固定」で、
#   他ストリームは止めない。1ストリームだけ回したい時は -Only を付ける。
#
# 【同時起動＝直列】1作業ツリーで並行すると git commit/push が衝突する実害が記録済み
#   （feedback_jx_concurrent_batch_gate_collision / feedback_shared_workdir_agent_collision）。
#   よって T→J→R を直列・-Batches のバッチ間も直列。
#
# 使い方（号令）:
#   「TJR処理」「TJRを1バッチ」   → pwsh -NoProfile -File scripts/patterns/TJR.ps1
#   「TJRを3バッチ処理」          → ... TJR.ps1 -Batches 3
#   「TJR処理 刑訴」              → ... TJR.ps1 -Subject 刑訴   # 刑訴優先・仕事の無いストリームは科目順へ
#   「TX60 を TJR処理」           → ... -TxFrom 60 -TxTo 60     # T=60固定・J/R=通常
#   「TX 60-71 処理」（Tだけ）     → ... -Only T -TxFrom 60 -TxTo 71
#   「JX 14-16 処理」（Jだけ）     → ... -Only J -JxFrom 14 -JxTo 16
#   検出だけ                      → ... -DryRun
param(
    [ValidateSet('','刑','刑訴','民','民訴','商','憲','行政')]
    [string]$Subject = '',        # '' = ストリーム別自動（優先順で仕事のある科目）／明示時は優先ピン＋フォールスルー
    [ValidateRange(1,99)]
    [int]$Batches = 1,            # 1バッチ＝T12/J3/R3。「TJRを3バッチ」= -Batches 3（直列）
    # 番号ピン（各ストリームを範囲に固定。未指定＝そのストリームは最若番から通常処理）
    [int]$TxFrom = 0, [int]$TxTo = 0,
    [int]$JxFrom = 0, [int]$JxTo = 0,
    [int]$RFrom  = 0, [int]$RTo  = 0,
    # 単一ストリームに限定（既定は空＝T/J/R 全部走る。「指定外も当然に処理」の既定を上書きしたい時だけ）
    [ValidateSet('','T','J','R')]
    [string]$Only = '',
    [switch]$SkipJ,               # 「JX以外を処理」＝J だけ落として T と R を回す
    [int]$MaxTX = 12,             # T の基本単位（ピン時は範囲全件）
    [int]$MaxJX = 3,              # J の基本単位
    [int]$MaxR  = 3,              # R の基本単位
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

# === スリープ抑止（DryRun 以外・feedback_nbr_keep_awake）===
# TJR は指揮者。各エンジン(tx-v13-runner/jx-batch-runner)も同一プロセス内(& 呼び)で
# keep-awake を立てるが、①最初のエンジン起動前の窓 ②全ストリーム skip 時 を取りこぼす。
# NBR として夜間無人で回す前提上、指揮者自身が冒頭で抑止を立てて全 T→J→R を確実にカバーする
# （ES_CONTINUOUS はスレッド継続＝プロセス終了で自動復帰）。
if (-not $DryRun) {
    try {
        $sig = '[DllImport("kernel32.dll", SetLastError=true)] public static extern uint SetThreadExecutionState(uint esFlags);'
        $PW = Add-Type -MemberDefinition $sig -Name PW -Namespace Win32 -PassThru -ErrorAction Stop
        [void]$PW::SetThreadExecutionState([uint32]2147483651)  # ES_CONTINUOUS|ES_SYSTEM_REQUIRED|ES_DISPLAY_REQUIRED
        Write-Host "[KEEP-AWAKE] スリープ抑止 ON（プロセス終了で自動復帰）" -ForegroundColor DarkGray
    } catch { Write-Host "[KEEP-AWAKE] 抑止設定に失敗（続行）: $($_.Exception.Message)" -ForegroundColor Yellow }
}

# === 科目優先順（ユーザー指示・フォルダ番号順とは別）===
#   ①刑法 ②刑事訴訟法 ③民法 ④民事訴訟法 ⑤商法 ⑥憲法 ⑦行政法
$SubjectOrder = @('刑','刑訴','民','民訴','商','憲','行政')
$SubjectFolder = @{ '刑'='001_刑法'; '刑訴'='002_刑事訴訟法'; '民'='003_民法'; '商'='004_商法'; '民訴'='005_民事訴訟法'; '行政'='006_行政法'; '憲'='007_憲法' }

# === 科目ごとの「仕事あり」判定（ストリーム別自動充当用・粗い存在チェック・番号ピン範囲も考慮）===
function Test-NumInRange { param([int]$n, [int]$From, [int]$To)
    if ($From -gt 0 -and $n -lt $From) { return $false }
    if ($To   -gt 0 -and $n -gt $To)   { return $false }
    return $true
}
function Get-TxPending { param([string]$subj, [int]$From = 0, [int]$To = 0)
    $folder = $SubjectFolder[$subj]
    $pdfDir = Join-Path $ProjectRoot "inputs\000_TX\$folder"
    $outDir = Join-Path $ProjectRoot "outputs\000_TX\$folder"
    if (-not (Test-Path $pdfDir)) { return $false }
    foreach ($p in @(Get-ChildItem $pdfDir -Filter '*.pdf' -File -ErrorAction SilentlyContinue)) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($p.Name)
        if ($stem -notmatch '^\d+') { continue }
        $n = [int]$Matches[0]
        if (-not (Test-NumInRange $n $From $To)) { continue }
        if (-not (Test-Path (Join-Path $outDir ("${subj}TX{0}.html" -f $n.ToString('000'))))) { return $true }
    }
    return $false
}
function Get-RPending { param([string]$subj, [int]$From = 0, [int]$To = 0)
    $folder = $SubjectFolder[$subj]
    $lexDir = Join-Path $ProjectRoot "outputs\ux\000_TX\$folder"
    $pdfDir = Join-Path $ProjectRoot "inputs\000_TX\$folder"
    if (-not (Test-Path $lexDir)) { return $false }
    foreach ($lex in @(Get-ChildItem $lexDir -Filter '*_lex.html' -File -ErrorAction SilentlyContinue)) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($lex.Name)
        if ($stem -notmatch '(\d+)_lex$') { continue }
        $n = [int]$Matches[1]
        if (-not (Test-NumInRange $n $From $To)) { continue }
        # 版判定はエンジン（tx-v13-runner.ps1 の $alreadyV13）と同一パターン＝v13 世代全体を SKIP。
        # 旧実装の 'v13\.0\.0' 固定は v13.1.0 を旧版誤判定する既知バグ（runner 側コメント参照）。
        if (Select-String -LiteralPath $lex.FullName -Pattern 'TX v13\.\d+\.\d+ LOOP-CARD' -Quiet -ErrorAction SilentlyContinue) { continue }
        if (Test-Path (Join-Path $pdfDir "$n.pdf")) { return $true }
    }
    return $false
}
function Get-JxPending { param([string]$subj, [int]$From = 0, [int]$To = 0)
    $folder = $SubjectFolder[$subj]
    $base = Join-Path $ProjectRoot "inputs\001_JX\$folder"
    $outDir = Join-Path $ProjectRoot "outputs\001_JX\$folder"
    foreach ($d in @((Join-Path $base '重問PDF'), $base)) {
        if (-not (Test-Path $d)) { continue }
        foreach ($p in @(Get-ChildItem $d -Filter '*.pdf' -File -ErrorAction SilentlyContinue)) {
            $stem = [System.IO.Path]::GetFileNameWithoutExtension($p.Name)
            if ($stem -notmatch '^\d+') { continue }
            $n = [int]$Matches[0]
            if (-not (Test-NumInRange $n $From $To)) { continue }
            if (-not (Test-Path (Join-Path $outDir ("${subj}JX{0}.html" -f $n.ToString('000'))))) { return $true }
        }
    }
    return $false
}

# === ストリーム別の科目確定（2026-07-18 ユーザー指示）===
# 優先順で「そのストリームに仕事のある科目」を独立に選ぶ。-Subject 明示時はその科目を先頭に
# 置き、仕事が無ければ優先順の残りへフォールスルー（例：-Subject 刑訴 で R は刑訴に無ければ刑へ）。
function Resolve-StreamSubject { param([string]$stream, [int]$From = 0, [int]$To = 0)
    $order = if ([string]::IsNullOrWhiteSpace($Subject)) { $SubjectOrder }
             else { @($Subject) + @($SubjectOrder | Where-Object { $_ -ne $Subject }) }
    foreach ($s in $order) {
        $has = $false
        switch ($stream) {
            'T' { $has = Get-TxPending $s $From $To }
            'J' { $has = Get-JxPending $s $From $To }
            'R' { $has = Get-RPending  $s $From $To }
        }
        if ($has) { return $s }
    }
    return ''
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TJR 処理  Batches=$Batches  Subject=$(if($Subject){"$Subject(優先)"}else{'(ストリーム別自動)'})  Only=$(if($Only){$Only}else{'(全部)'})  DryRun=$DryRun" -ForegroundColor Cyan
Write-Host "  ピン: TX=$TxFrom-$TxTo  JX=$JxFrom-$JxTo  R=$RFrom-$RTo   基本単位 T:$MaxTX J:$MaxJX R:$MaxR" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# === ストリーム実行ヘルパ ===
function Invoke-TxStream {
    param([switch]$Regen, [int]$Max, [int]$From, [int]$To, [string]$StreamSubject)
    if (-not (Test-Path $TxRunner)) { Write-Host "[SKIP] TX エンジン不在: $TxRunner" -ForegroundColor Yellow; return 0 }
    $p = @{ Subject = $StreamSubject; ProjectRoot = $ProjectRoot }
    if ($From -gt 0 -or $To -gt 0) {           # ピン：範囲全件
        $p.FromNumber = $From; $p.ToNumber = $To
        $p.MaxProblems = [Math]::Max(1, ($To - $From + 1))
    } else { $p.MaxProblems = $Max }           # 通常：最若番から基本単位
    if ($Regen)  { $p.Regen = $true }
    if ($NoPush) { $p.NoPush = $true }
    if ($DryRun) { $p.DryRun = $true }
    $label = if ($Regen) { "R（旧_lex再生成・$StreamSubject）" } else { "T（新規TX・$StreamSubject）" }
    Write-Host "`n———————— $label 開始 ————————" -ForegroundColor Green
    # 子ランナーが success ストリームに何か漏らしても（例: 監査 check-duplicates の stdout）、
    # それを関数戻り値に混ぜて $rcT を配列化させないため Out-Host で host へ流し、終了コードだけ返す。
    & $TxRunner @p | Out-Host
    return $LASTEXITCODE
}
function Invoke-JxStream {
    param([int]$Max, [int]$From, [int]$To, [string]$StreamSubject)
    if (-not (Test-Path $JxRunner)) { Write-Host "[SKIP] JX エンジン不在: $JxRunner" -ForegroundColor Yellow; return 0 }
    $p = @{ Subject = $StreamSubject; SkipAudio = $true; ProjectRoot = $ProjectRoot; Finalize = $true }
    if ($From -gt 0 -or $To -gt 0) {
        $p.FromNumber = $From; $p.ToNumber = $To
        $p.MaxProblems = [Math]::Max(1, ($To - $From + 1))
    } else { $p.MaxProblems = $Max }
    if ($NoPush) { $p.NoPush = $true }
    if ($DryRun) { $p.DryRun = $true }
    Write-Host "`n———————— J（新規JX＋副産物・$StreamSubject） 開始 ————————" -ForegroundColor Green
    # 同上：JX ランナーの success ストリーム漏れで $rcJ を配列化させない。
    & $JxRunner @p | Out-Host
    return $LASTEXITCODE
}

# === 実行（Only 指定が無ければ T→J→R を全部・直列。バッチ間も直列）===
$runT = ($Only -eq '' -or $Only -eq 'T')
$runJ = ($Only -eq '' -or $Only -eq 'J') -and (-not $SkipJ)
$runR = ($Only -eq '' -or $Only -eq 'R')
$rcAll = 0
$batchCount = $Batches
if ($DryRun -and $Batches -gt 1) {
    Write-Host "[TJR] DryRun は状態が変わらないため 1 バッチ分のみ表示" -ForegroundColor Yellow
    $batchCount = 1
}

for ($b = 1; $b -le $batchCount; $b++) {
    # 毎バッチ再解決＝科目の仕事が尽きたら次バッチから優先順の次科目へ自動で移る
    $subT = ''; $subJ = ''; $subR = ''
    if ($runT) { $subT = Resolve-StreamSubject 'T' $TxFrom $TxTo }
    if ($runJ) { $subJ = Resolve-StreamSubject 'J' $JxFrom $JxTo }
    if ($runR) { $subR = Resolve-StreamSubject 'R' $RFrom  $RTo  }
    if (-not ($subT -or $subJ -or $subR)) {
        Write-Host "`n[TJR] バッチ $b：全ストリーム・全科目で処理対象なし。終了。" -ForegroundColor Green
        break
    }
    Write-Host "`n==================== TJR バッチ $b / $batchCount ====================" -ForegroundColor Cyan
    Write-Host ("  科目割当: T={0}  J={1}  R={2}" -f `
        $(if($subT){$subT}else{'該当なし'}), $(if($subJ){$subJ}else{'該当なし'}), $(if($subR){$subR}else{'該当なし'})) -ForegroundColor Cyan

    $rcT = 0; $rcJ = 0; $rcR = 0
    if ($runT) {
        if ($subT) { $rcT = Invoke-TxStream -Max $MaxTX -From $TxFrom -To $TxTo -StreamSubject $subT }
        else { Write-Host "`n[SKIP] T：全科目で新規TX対象なし" -ForegroundColor Yellow }
    }
    if ($runJ) {
        if ($subJ) { $rcJ = Invoke-JxStream -Max $MaxJX -From $JxFrom -To $JxTo -StreamSubject $subJ }
        else { Write-Host "`n[SKIP] J：全科目で新規JX対象なし" -ForegroundColor Yellow }
    }
    if ($runR) {
        if ($subR) { $rcR = Invoke-TxStream -Regen -Max $MaxR -From $RFrom -To $RTo -StreamSubject $subR }
        else { Write-Host "`n[SKIP] R：全科目を遡って旧版_lexなし＝該当なしでOK（過渡ストリーム）" -ForegroundColor Yellow }
    }

    Write-Host "`n———————— TJR バッチ $b 集計 ————————" -ForegroundColor Cyan
    if ($runT) { Write-Host ("  T（新規TX・{0}）  exit={1}" -f $(if($subT){$subT}else{'-'}), $rcT) }
    if ($runJ) { Write-Host ("  J（新規JX・{0}）  exit={1}" -f $(if($subJ){$subJ}else{'-'}), $rcJ) }
    if ($runR) { Write-Host ("  R（旧_lex・{0}）  exit={1}" -f $(if($subR){$subR}else{'-'}), $rcR) }
    if ($rcT -ne 0 -or $rcJ -ne 0 -or $rcR -ne 0) { $rcAll = 1 }
}

Write-Host "`n  TJR 終了 exit=$rcAll" -ForegroundColor Cyan
exit $rcAll
