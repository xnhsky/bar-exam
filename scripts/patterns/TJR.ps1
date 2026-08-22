# TJR.ps1 — 大元の号令（TX新規＝T ／ JX新規＝J ／ 旧版TXLEX再生成＝R ／ 修復＝F を1本で束ねる指揮者）
#
# 【位置づけ】2026-07-04 確定・ユーザー指示で旧パターン（TX-MARCH / TX-PICK / JX）を廃止し、
#   本 TJR を現行版の唯一の入口にする。TJR は「指揮者」であり、重い生成ロジックは持たない。
#   実生成は各エンジンへ委譲：
#     T（新規TX）    : scripts\tx-v13-runner.ps1              … フロンティア前進（公式最大番号より先）・v13 二系統
#     R（さかのぼり）  : scripts\tx-v13-runner.ps1 -Regen      … 旧版_lex再生成＋公式最大番号以下の欠番補完
#                        （2026-07-18「刑法58件未生成の分をR再生成と併せる」・T と番号集合が重ならない）
#     J（新規JX）    : scripts\jx-batch-runner.ps1（内部エンジン）… JX＋副産物RX/TREE/ARIADNE＋台本
#     F（修復）      : scripts\tjr-audit.py（検出）＋各エンジンの修復モード（2026-07-24 新設・ユーザー指示
#                      「エラー品・未完成品を検出して新規生成と同時並行で修正」）。生成が途中で死んだ／
#                      validate ERROR で commit されず残った HTML は「存在する」ため T/J/R の対象検出から
#                      不可視＝永久放置になる構造穴があり、F が毎バッチ先頭で検出→回収する：
#                        ・検証PASSの未コミット残骸 → 回収 commit/push（再生成せず＝安価）
#                        ・ペア欠け/途切れ/プレースホルダー残骸/検証FAIL → tx-v13-runner -RepairIds ／
#                          jx-batch-runner -RepairNumbers で PDF から修復再生成
#                        ・G66/G69 のみの失敗 → tx-sysmap-fit.py（決定論）で無料修復（--fix-safe）
#                        ・同一問題の修復 2 回失敗 → 自動再試行を停止し logs\tjr-repair-report.md へ
#                          ESCALATE（無限再生成でトークンを溶かさない・省エネ規律）
#                      修復対象ゼロなら数十秒の監査だけで即終了（F の常設コストはほぼゼロ）。
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
#   よって F→T→J→R を直列・-Batches のバッチ間も直列。「同時並行」は
#   「1 号令の中で修復と新規生成の両方が自動で進む」ことで実現する（プロセス並列は上記実害により不採用。
#   真の並列が要るときは従来どおり二台 PC / 番号帯分け）。F を先頭に置くのは、放置品の回収を
#   新規生成より優先するユーザー方針（2026-07-24）と、破損公式が MaxOfficial を汚したまま
#   T のフロンティア判定へ入るのを防ぐため。
#
# 使い方（号令）:
#   「TJR処理」「TJRを1バッチ」   → pwsh -NoProfile -File scripts/patterns/TJR.ps1
#   「TJRを3バッチ処理」          → ... TJR.ps1 -Batches 3
#   「TJR処理 刑訴」              → ... TJR.ps1 -Subject 刑訴   # 刑訴優先・仕事の無いストリームは科目順へ
#   「TX60 を TJR処理」           → ... -TxFrom 60 -TxTo 60     # T=60固定・J/R=通常
#   「TX 60-71 処理」（Tだけ）     → ... -Only T -TxFrom 60 -TxTo 71
#   「JX 14-16 処理」（Jだけ）     → ... -Only J -JxFrom 14 -JxTo 16
#   修復だけ（F単独）             → ... -Only F
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
    # 単一ストリームに限定（既定は空＝F/T/J/R 全部走る。「指定外も当然に処理」の既定を上書きしたい時だけ）
    [ValidateSet('','T','J','R','F','Q','S')]
    [string]$Only = '',
    [switch]$SkipJ,               # 「JX以外を処理」＝J だけ落として T と R を回す
    [switch]$SkipF,               # F（修復）を止める（既定は毎バッチ先頭で監査→修復）
    [switch]$SkipQ,               # Q（§v13q 付随・特別枠）を止める
    [switch]$SkipS,               # S（§v13v ものがたり付随・特別枠）を止める
    [int]$MaxTX = 12,             # T の基本単位（ピン時は範囲全件）
    [int]$MaxJX = 3,              # J の基本単位
    [int]$MaxR  = 3,              # R の基本単位
    [int]$MaxF  = 3,              # F の TX 修復再生成 上限/バッチ（回収コミットは無制限＝安価なため）
    [int]$MaxFJx = 1,             # F の JX 修復再生成 上限/バッチ（JX は 1〜2 時間/問のため既定 1）
    [int]$MaxQ  = 10,             # Q の基本単位（2026-07-28 ユーザー指示＝10個ずつ・完遂まで）
    [int]$MaxS  = 10,             # S の基本単位（2026-08-22 ユーザー指示＝民法優先で10個ずつ）
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
$QRunner  = Join-Path $ProjectRoot 'scripts\v13q-runner.ps1'
$SRunner  = Join-Path $ProjectRoot 'scripts\v13v-runner.ps1'
$AuditTool = Join-Path $ProjectRoot 'scripts\tjr-audit.py'
$LogsDir = Join-Path $ProjectRoot 'logs'
$RepairLedger = Join-Path $LogsDir 'tjr-repair-ledger.json'   # F の再試行台帳（PCローカル・git外）
$RepairReport = Join-Path $LogsDir 'tjr-repair-report.md'     # ESCALATE / report-only の追記先

# === TJR claim ライブラリ（二台同時実行の衝突対策・2026-07-27）===
#   claim 予約＋安全 push（first-push-wins・rebase 途中放置の禁止）。正典 docs/run-patterns.md。
#   各エンジン（tx-v13-runner / jx-batch-runner）も dot-source するが、TJR 自身も
#   バッチ頭の Sync-TjrRepo / Clear-TjrStaleClaims / F の安全 push で使う。
. (Join-Path $ProjectRoot 'scripts\tjr-claim.ps1')

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
function Get-MaxOfficial { param([string]$subj)
    # T/R の境界＝公式の最大既存番号（T=これより先のフロンティア／R=これ以下のさかのぼり）
    $outDir = Join-Path $ProjectRoot "outputs\000_TX\$($SubjectFolder[$subj])"
    $max = 0
    foreach ($f in @(Get-ChildItem $outDir -Filter "${subj}TX*.html" -File -ErrorAction SilentlyContinue)) {
        if ($f.BaseName -match '(\d+)$') { $n = [int]$Matches[1]; if ($n -gt $max) { $max = $n } }
    }
    return $max
}
function Get-TxPending { param([string]$subj, [int]$From = 0, [int]$To = 0)
    $folder = $SubjectFolder[$subj]
    $pdfDir = Join-Path $ProjectRoot "inputs\000_TX\$folder"
    $outDir = Join-Path $ProjectRoot "outputs\000_TX\$folder"
    if (-not (Test-Path $pdfDir)) { return $false }
    $maxOff = Get-MaxOfficial $subj
    foreach ($p in @(Get-ChildItem $pdfDir -Filter '*.pdf' -File -ErrorAction SilentlyContinue)) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($p.Name)
        if ($stem -notmatch '^\d+') { continue }
        $n = [int]$Matches[0]
        if ($n -le $maxOff) { continue }   # 過去帯の欠番は R の領分（エンジンと同一規則）
        if (-not (Test-NumInRange $n $From $To)) { continue }
        if (-not (Test-Path (Join-Path $outDir ("${subj}TX{0}.html" -f $n.ToString('000'))))) { return $true }
    }
    return $false
}
function Get-QPending {
    # Q（§v13q 付随・特別枠・過渡）：刑訴TX の既存 _lex で答案圧縮（tx-anscomp-line）未展開の残数。
    # 0 件＝完遂（該当なし SKIP が正常）。対象科目は当面 刑訴 固定（2026-07-28 ユーザー指示の残件 081-179）。
    $dir = Join-Path $ProjectRoot 'outputs\ux\000_TX\002_刑事訴訟法'
    if (-not (Test-Path $dir)) { return 0 }
    $c = 0
    foreach ($lex in @(Get-ChildItem $dir -Filter '*_lex.html' -File -ErrorAction SilentlyContinue)) {
        if (-not (Select-String -LiteralPath $lex.FullName -Pattern 'tx-anscomp-line' -Quiet -ErrorAction SilentlyContinue)) { $c++ }
    }
    return $c
}
function Get-SPending {
    # S（§v13v「📖 ものがたり」付随・特別枠・過渡）：正誤表の記述に data-brief-story が
    # 1 つも入っていない _lex の残数。科目は 民法 → 刑法 の優先順（2026-08-22 ユーザー指示）で、
    # 刑訴はセッション側で消化中のため S の自動充当からは外す（-Subject 刑訴 で明示指定は可）。
    $c = 0
    foreach ($folder in @('003_民法', '001_刑法')) {
        $dir = Join-Path $ProjectRoot "outputs\ux\000_TX\$folder"
        if (-not (Test-Path $dir)) { continue }
        foreach ($lex in @(Get-ChildItem $dir -Filter '*_lex.html' -File -ErrorAction SilentlyContinue)) {
            if (-not (Select-String -LiteralPath $lex.FullName -Pattern 'statement-verdict-table' -Quiet -ErrorAction SilentlyContinue)) { continue }
            if (-not (Select-String -LiteralPath $lex.FullName -Pattern 'data-brief-story=' -Quiet -ErrorAction SilentlyContinue)) { $c++ }
        }
    }
    return $c
}
function Get-RPending { param([string]$subj, [int]$From = 0, [int]$To = 0)
    $folder = $SubjectFolder[$subj]
    $lexDir = Join-Path $ProjectRoot "outputs\ux\000_TX\$folder"
    $pdfDir = Join-Path $ProjectRoot "inputs\000_TX\$folder"
    # (a) 旧版 _lex の再生成対象
    if (Test-Path $lexDir) {
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
    }
    # (b) 公式最大番号以下の欠番補完（PDF あり・公式なし＝過去帯の未生成穴・エンジンと同一規則）
    if (Test-Path $pdfDir) {
        $outDir = Join-Path $ProjectRoot "outputs\000_TX\$folder"
        $maxOff = Get-MaxOfficial $subj
        foreach ($p in @(Get-ChildItem $pdfDir -Filter '*.pdf' -File -ErrorAction SilentlyContinue)) {
            $stem = [System.IO.Path]::GetFileNameWithoutExtension($p.Name)
            if ($stem -notmatch '^\d+') { continue }
            $n = [int]$Matches[0]
            if ($n -gt $maxOff) { continue }
            if (-not (Test-NumInRange $n $From $To)) { continue }
            if (-not (Test-Path (Join-Path $outDir ("${subj}TX{0}.html" -f $n.ToString('000'))))) { return $true }
        }
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

# === F（修復）ストリーム：tjr-audit.py の検出 → 回収コミット／修復再生成へ振り分け ===
# 台帳（logs\tjr-repair-ledger.json・PCローカル）で同一問題の修復試行を数え、2回失敗で自動再試行を
# 停止（ESCALATE）＝壊れた入力等で無限に claude -p を回してトークンを溶かさない（省エネ規律）。
function Read-RepairLedger {
    if (Test-Path $RepairLedger) {
        try { return (Get-Content $RepairLedger -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable) } catch { return @{} }
    }
    return @{}
}
function Save-RepairLedger { param($Ledger)
    if (-not (Test-Path $LogsDir)) { New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null }
    ($Ledger | ConvertTo-Json -Depth 5) | Out-File -FilePath $RepairLedger -Encoding utf8
}
function Add-RepairReport { param([string[]]$Lines)
    if ($Lines.Count -eq 0) { return }
    if (-not (Test-Path $LogsDir)) { New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null }
    Add-Content -Path $RepairReport -Encoding utf8 -Value (@("## $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') TJR-F") + $Lines + @(''))
}
function Invoke-GitPushWithRetry {
    # 2026-07-27: 安全 push（tjr-claim.ps1）へ委譲。push 拒否 → pull --rebase -X ours（同一
    # ファイル衝突はリモート先着版を採用）→ 再 push。解決不能でも rebase --abort で必ず復帰
    # ＝旧実装の「rebase 途中放置→以降の commit 全滅」を根絶。
    return (Invoke-TjrSafePush -ProjectRoot $ProjectRoot -MaxTries 3 -Label 'TJR-F')
}
function Invoke-FStream {
    # 戻り値: @{ Rc=<0/1>; Dispatched=<今回実際に動かした件数>; Actionable=<監査の要対応件数> }
    $res = @{ Rc = 0; Dispatched = 0; Actionable = 0 }
    if (-not (Test-Path $AuditTool)) {
        Write-Host "[SKIP] F：監査ツール不在: $AuditTool" -ForegroundColor Yellow
        return $res
    }
    Write-Host "`n———————— F（修復＝エラー品・未完成品の検出/回収） 開始 ————————" -ForegroundColor Green
    if (-not (Test-Path $LogsDir)) { New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null }
    $auditJson = Join-Path $LogsDir 'tjr-audit-latest.json'
    Remove-Item -LiteralPath $auditJson -Force -ErrorAction SilentlyContinue
    $auditArgs = @($AuditTool, '--root', $ProjectRoot, '--json', $auditJson, '--min-age-min', '45')
    if (-not $DryRun) { $auditArgs += '--fix-safe' }   # G66/G69 のみの失敗は決定論ツールで無料修復
    & python @auditArgs | Out-Host
    if (-not (Test-Path $auditJson)) {
        Write-Host "[F] 監査 JSON なし（監査ツール失敗）→ F をスキップして続行" -ForegroundColor Yellow
        $res.Rc = 1; return $res
    }
    try { $audit = Get-Content $auditJson -Raw -Encoding utf8 | ConvertFrom-Json }
    catch { Write-Host "[F] 監査 JSON 解析失敗 → F をスキップして続行" -ForegroundColor Yellow; $res.Rc = 1; return $res }
    $res.Actionable = [int]$audit.summary.actionable

    # 台帳の掃除は actionable=0 の早期 return より前に行う（監査に出なくなった項目＝修復完了とみなし削除）。
    # 末尾でだけ掃除すると「修復完了→クリーン」の回で stale な attempts が残り、同じ番号が将来
    # 別の事故で壊れたときに即 ESCALATE する誤動作になる（DryRun は状態を変えないので掃除しない）。
    $ledger = @{}
    if (-not $DryRun) {
        $ledger = Read-RepairLedger
        $activeIds = @(@($audit.txRepairs) + @($audit.jxRepairs) | Where-Object { $_ } | ForEach-Object { $_.id })
        $stale = @($ledger.Keys | Where-Object { $activeIds -notcontains $_ })
        if ($stale.Count -gt 0) {
            foreach ($k in $stale) { $ledger.Remove($k) }
            Save-RepairLedger $ledger
        }
    }

    if ($res.Actionable -eq 0) {
        Write-Host "[F] 修復対象なし（クリーン）" -ForegroundColor Green
        return $res
    }
    if ($DryRun) {
        Write-Host "[F][DRY-RUN] 修復対象 $($res.Actionable) 件（内訳は上記監査出力）。実行はしない。" -ForegroundColor Yellow
        return $res
    }

    $reportLines = @()

    # --- 1) 回収コミット（検証PASSの未コミット残骸＝再生成不要・安価） ---
    $commitItems = @(@($audit.txCommits) + @($audit.jxCommits) | Where-Object { $_ })
    foreach ($c in $commitItems) {
        # 監査 JSON の path は repo 相対・スラッシュ区切り。git は Windows でもスラッシュを解する
        # ため変換せずそのまま `git -C` に渡す（バックスラッシュ変換は Linux pwsh で壊れる）。
        $paths = @($c.paths)
        try {
            & git -C $ProjectRoot add -- @paths 2>&1 | Out-Null
            & git -C $ProjectRoot commit -m "fix(TJR-F): $($c.problemId) の未コミット成果物を回収（検証PASS）" 2>&1 | Out-Null
            Write-Host "[F-COMMIT] $($c.problemId) を回収コミット（$($paths.Count) ファイル）: $($c.note)" -ForegroundColor Green
            $res.Dispatched++
        } catch { Write-Host "[F-COMMIT FAIL] $($c.problemId): $_" -ForegroundColor Yellow; $res.Rc = 1 }
    }
    if ($commitItems.Count -gt 0 -and -not $NoPush) {
        if (Invoke-GitPushWithRetry) { Write-Host "[F-COMMIT] push 済" -ForegroundColor Green }
        else { Write-Host "[F-COMMIT] push 未了（リモート先行。以後のストリームの push か手動回収で反映）" -ForegroundColor Yellow }
    }

    # --- 2) TX 修復再生成（tx-v13-runner -RepairIds・上限 MaxF/バッチ・台帳で再試行制御） ---
    $txQueue = @()
    foreach ($r in @($audit.txRepairs | Where-Object { $_ })) {
        $att = 0; if ($ledger.ContainsKey($r.id)) { $att = [int]$ledger[$r.id].attempts }
        if ($att -ge 2) {
            Write-Host "[F-ESCALATE] $($r.problemId)：修復 $att 回失敗済み → 自動再試行を停止（手動対応要・logs\tjr-repair-report.md）" -ForegroundColor Red
            $reportLines += "- ESCALATE $($r.problemId)（修復 $att 回失敗→自動停止）: $($r.reasons -join '；')"
            $res.Rc = 1
            continue
        }
        $txQueue += $r
    }
    foreach ($grp in @($txQueue | Select-Object -First $MaxF | Group-Object subject)) {
        $ids = @($grp.Group | ForEach-Object { $_.number }) -join ','
        foreach ($r in $grp.Group) {
            if (-not $ledger.ContainsKey($r.id)) { $ledger[$r.id] = @{ attempts = 0 } }
            $ledger[$r.id].attempts = [int]$ledger[$r.id].attempts + 1
            $ledger[$r.id].last = Get-Date -Format 's'
            $ledger[$r.id].reasons = ($r.reasons -join '；')
        }
        Save-RepairLedger $ledger
        Write-Host "[F] TX 修復再生成 → $($grp.Name): $ids" -ForegroundColor Cyan
        $p = @{ Subject = $grp.Name; RepairIds = $ids; MaxProblems = @($grp.Group).Count; ProjectRoot = $ProjectRoot }
        if ($NoPush) { $p.NoPush = $true }
        & $TxRunner @p | Out-Host
        if ($LASTEXITCODE -ne 0) { $res.Rc = 1 }
        $res.Dispatched += @($grp.Group).Count
    }

    # --- 3) JX 修復再生成（jx-batch-runner -RepairNumbers・上限 MaxFJx/バッチ・台帳で再試行制御） ---
    $jxQueue = @()
    foreach ($r in @($audit.jxRepairs | Where-Object { $_ })) {
        $att = 0; if ($ledger.ContainsKey($r.id)) { $att = [int]$ledger[$r.id].attempts }
        if ($att -ge 2) {
            Write-Host "[F-ESCALATE] $($r.problemId)：修復 $att 回失敗済み → 自動再試行を停止（手動対応要・logs\tjr-repair-report.md）" -ForegroundColor Red
            $reportLines += "- ESCALATE $($r.problemId)（修復 $att 回失敗→自動停止）: $($r.reasons -join '；')"
            $res.Rc = 1
            continue
        }
        $jxQueue += $r
    }
    foreach ($r in @($jxQueue | Select-Object -First $MaxFJx)) {
        if (-not $ledger.ContainsKey($r.id)) { $ledger[$r.id] = @{ attempts = 0 } }
        $ledger[$r.id].attempts = [int]$ledger[$r.id].attempts + 1
        $ledger[$r.id].last = Get-Date -Format 's'
        $ledger[$r.id].reasons = ($r.reasons -join '；')
        Save-RepairLedger $ledger
        Write-Host "[F] JX 修復再生成 → $($r.problemId)" -ForegroundColor Cyan
        $p = @{ Subject = $r.subject; RepairNumbers = "$($r.number)"; MaxProblems = 1; SkipAudio = $true; Finalize = $true; ProjectRoot = $ProjectRoot }
        if ($NoPush) { $p.NoPush = $true }
        & $JxRunner @p | Out-Host
        if ($LASTEXITCODE -ne 0) { $res.Rc = 1 }
        $res.Dispatched++
    }

    # --- 4) report-only・副産物欠落はレポートへ（副産物の修復は ②-verify／rx-arb-autofill の領分） ---
    foreach ($ro in @($audit.reportOnly | Where-Object { $_ })) { $reportLines += "- REPORT $($ro.path): $($ro.reasons -join '；')" }
    foreach ($g in @($audit.byproductGaps | Where-Object { $_ })) { $reportLines += "- GAP $($g.problemId): 副産物欠落 $($g.missing -join '/')（autofill/②-verify が回収）" }
    Add-RepairReport -Lines $reportLines

    return $res
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TJR 処理  Batches=$Batches  Subject=$(if($Subject){"$Subject(優先)"}else{'(ストリーム別自動)'})  Only=$(if($Only){$Only}else{'(全部)'})  DryRun=$DryRun" -ForegroundColor Cyan
Write-Host "  ピン: TX=$TxFrom-$TxTo  JX=$JxFrom-$JxTo  R=$RFrom-$RTo   基本単位 F:$MaxF(+JX$MaxFJx) T:$MaxTX J:$MaxJX R:$MaxR" -ForegroundColor Cyan
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

function Invoke-QStream {
    param([int]$Max)
    if (-not (Test-Path $QRunner)) { Write-Host "[SKIP] Q エンジン不在: $QRunner" -ForegroundColor Yellow; return 0 }
    $p = @{ MaxProblems = $Max; ProjectRoot = $ProjectRoot }
    if ($NoPush) { $p.NoPush = $true }
    if ($DryRun) { $p.DryRun = $true }
    Write-Host "`n———————— Q（§v13q 付随・刑訴 特別枠） 開始 ————————" -ForegroundColor Green
    & $QRunner @p | Out-Host
    return $LASTEXITCODE
}

function Invoke-SStream {
    param([int]$Max)
    if (-not (Test-Path $SRunner)) { Write-Host "[SKIP] S エンジン不在: $SRunner" -ForegroundColor Yellow; return 0 }
    $p = @{ MaxProblems = $Max; ProjectRoot = $ProjectRoot }
    if ($NoPush) { $p.NoPush = $true }
    if ($DryRun) { $p.DryRun = $true }
    Write-Host "`n———————— S（§v13v ものがたり付随・民法優先） 開始 ————————" -ForegroundColor Green
    & $SRunner @p | Out-Host
    return $LASTEXITCODE
}

# === 実行（Only 指定が無ければ F→T→J→R→Q を全部・直列。バッチ間も直列）===
$runT = ($Only -eq '' -or $Only -eq 'T')
$runJ = ($Only -eq '' -or $Only -eq 'J') -and (-not $SkipJ)
$runR = ($Only -eq '' -or $Only -eq 'R')
$runF = ($Only -eq '' -or $Only -eq 'F') -and (-not $SkipF)
$runQ = ($Only -eq '' -or $Only -eq 'Q') -and (-not $SkipQ)
$runS = ($Only -eq '' -or $Only -eq 'S') -and (-not $SkipS)
$rcAll = 0
$batchCount = $Batches
if ($DryRun -and $Batches -gt 1) {
    Write-Host "[TJR] DryRun は状態が変わらないため 1 バッチ分のみ表示" -ForegroundColor Yellow
    $batchCount = 1
}

for ($b = 1; $b -le $batchCount; $b++) {
    # 毎バッチ先頭でリモート先行分へ追随＋失効 claim を掃除（二台同時実行の衝突対策・2026-07-27）。
    # 追随してから対象検出することで、相手 PC の生成済み番号を「仕事あり」と誤検出しない。
    if (-not $DryRun) {
        [void](Sync-TjrRepo -ProjectRoot $ProjectRoot)
        Clear-TjrStaleClaims -ProjectRoot $ProjectRoot -NoPush:$NoPush
    }

    # 毎バッチ再解決＝科目の仕事が尽きたら次バッチから優先順の次科目へ自動で移る
    $subT = ''; $subJ = ''; $subR = ''
    if ($runT) { $subT = Resolve-StreamSubject 'T' $TxFrom $TxTo }
    if ($runJ) { $subJ = Resolve-StreamSubject 'J' $JxFrom $JxTo }
    if ($runR) { $subR = Resolve-StreamSubject 'R' $RFrom  $RTo  }
    $qPend = 0
    if ($runQ) { $qPend = Get-QPending }
    $sPend = 0
    if ($runS) { $sPend = Get-SPending }
    $hasTJRWork = [bool]($subT -or $subJ -or $subR -or ($qPend -gt 0) -or ($sPend -gt 0))
    if (-not $hasTJRWork -and -not $runF) {
        Write-Host "`n[TJR] バッチ $b：全ストリーム・全科目で処理対象なし。終了。" -ForegroundColor Green
        break
    }
    Write-Host "`n==================== TJR バッチ $b / $batchCount ====================" -ForegroundColor Cyan
    Write-Host ("  科目割当: T={0}  J={1}  R={2}  F={3}  Q={4}  S={5}" -f `
        $(if($subT){$subT}else{'該当なし'}), $(if($subJ){$subJ}else{'該当なし'}), $(if($subR){$subR}else{'該当なし'}), `
        $(if($runF){'全科目監査'}else{'OFF'}), $(if($runQ){"刑訴 残$qPend"}else{'OFF'}), `
        $(if($runS){"民法優先 残$sPend"}else{'OFF'})) -ForegroundColor Cyan

    # F は毎バッチ先頭（放置品の回収を新規生成より優先＋破損公式が T のフロンティア判定を汚す前に直す）。
    # 修復対象ゼロなら監査（数十秒）だけで即抜けるので常設コストはほぼ無い。
    $fRes = @{ Rc = 0; Dispatched = 0; Actionable = 0 }
    if ($runF) { $fRes = Invoke-FStream }
    if (-not $hasTJRWork -and $fRes.Dispatched -eq 0) {
        if ($fRes.Actionable -gt 0) {
            Write-Host "`n[TJR] バッチ $b：T/J/R 対象なし・F は自動修復不能の残件のみ（logs\tjr-repair-report.md 参照）。終了。" -ForegroundColor Yellow
        } else {
            Write-Host "`n[TJR] バッチ $b：全ストリーム・全科目で処理対象なし（修復対象もなし）。終了。" -ForegroundColor Green
        }
        if ($fRes.Rc -ne 0) { $rcAll = 1 }
        break
    }

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
    $rcQ = 0
    if ($runQ) {
        if ($qPend -gt 0) { $rcQ = Invoke-QStream -Max $MaxQ }
        else { Write-Host "`n[SKIP] Q：刑訴TX 残なし＝§v13q 特別枠は完遂（過渡ストリーム）" -ForegroundColor Yellow }
    }
    $rcS = 0
    if ($runS) {
        if ($sPend -gt 0) { $rcS = Invoke-SStream -Max $MaxS }
        else { Write-Host "`n[SKIP] S：民法・刑法とも残なし＝§v13v 特別枠は完遂（過渡ストリーム）" -ForegroundColor Yellow }
    }

    Write-Host "`n———————— TJR バッチ $b 集計 ————————" -ForegroundColor Cyan
    if ($runF) { Write-Host ("  F（修復）        exit={0}  実行 {1} 件 / 検出 {2} 件" -f $fRes.Rc, $fRes.Dispatched, $fRes.Actionable) }
    if ($runT) { Write-Host ("  T（新規TX・{0}）  exit={1}" -f $(if($subT){$subT}else{'-'}), $rcT) }
    if ($runJ) { Write-Host ("  J（新規JX・{0}）  exit={1}" -f $(if($subJ){$subJ}else{'-'}), $rcJ) }
    if ($runR) { Write-Host ("  R（旧_lex・{0}）  exit={1}" -f $(if($subR){$subR}else{'-'}), $rcR) }
    if ($runQ) { Write-Host ("  Q（§v13q・刑訴） exit={0}  残={1} 件（バッチ開始時点）" -f $rcQ, $qPend) }
    if ($runS) { Write-Host ("  S（§v13v・民法優先）exit={0}  残={1} 件（バッチ開始時点）" -f $rcS, $sPend) }
    if ($rcT -ne 0 -or $rcJ -ne 0 -or $rcR -ne 0 -or $rcQ -ne 0 -or $rcS -ne 0 -or $fRes.Rc -ne 0) { $rcAll = 1 }
}

Write-Host "`n  TJR 終了 exit=$rcAll" -ForegroundColor Cyan
exit $rcAll
