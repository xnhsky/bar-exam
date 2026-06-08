# jx-finalize.ps1 — JX 生成物の「永続化＋入力クリーンアップ」を 1 本にまとめる（pwsh ネイティブ）
#
# 各問題 ID について、以下を安全な順序で行う:
#   ① GitHub バックアップ : outputs/jx/{Subject}JX/{ID}.html ＋ outputs/tts/{ID}/ を git add → commit
#   ② 入力クリーンアップ  : 入力 PDF（inputs/jx/{科目}/重問PDF/{n}.pdf）＋ 逐語 を git rm → commit
#       └ 削除の多重ガード（1 つでも欠ければ削除しない）:
#            (a) HTML が git にコミット済み（①で担保）
#            (b) その PDF・逐語が Drive バックアップに存在（jx-deploy.ps1 が配置時にコピー済）
#   ③ push（-Push 指定時。既定で実行・-NoPush で抑止）
#
# ※ Drive バックアップは jx-deploy.ps1 が担う。本スクリプトは「バックアップ済みを確認して消す」係。
# ※ 削除は git rm（履歴に残り復元可）。物理 rm はしない。
# ※ Drive 未マウント時はクリーンアップを HOLD（バックアップ確認不可）。--NoDriveCheck で緊急回避可。
#
# 使い方:
#   pwsh -NoProfile -File scripts/jx-finalize.ps1 -Subject 刑 -Ids 刑JX025,刑JX026
#   pwsh -NoProfile -File scripts/jx-finalize.ps1 -Subject 刑 -Ids 刑JX025 -DryRun
#   pwsh -NoProfile -File scripts/jx-finalize.ps1 -Subject 刑 -Ids 刑JX025 -NoPush
param(
    [Parameter(Mandatory=$true)][ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject,
    [Parameter(Mandatory=$true)][string[]]$Ids,   # 例: 刑JX025,刑JX026
    [switch]$NoPush,            # push を抑止（既定は push する）
    [switch]$NoCleanup,         # ①のみ（GitHub バックアップ）で入力削除はしない
    [switch]$NoDriveCheck,      # Drive 未マウント時の緊急用（git 履歴のみが復元元になる）
    [switch]$DryRun
)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# pwsh -File 経由ではカンマ区切りが 1 要素になることがあるため正規化（"a,b" -> a, b）
$Ids = @($Ids | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })

# 科目 → Drive 科目フォルダ名（重問PDF / 講義逐語 はこの直下）
$DriveHtml = @{
    '刑'='001_刑法'; '刑訴'='002_刑事訴訟法'; '民'='003_民法'; '商'='004_商法';
    '民訴'='005_民事訴訟法'; '行政'='006_行政法'; '憲'='007_憲法'
}
$DriveRoot = $null
$cand = 'H:\マイドライブ\CATALINA＿G共有\■予備試験進行中'
if (Test-Path -LiteralPath $cand) {
    $jxDir = Get-ChildItem -LiteralPath $cand -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like '*JX*論*文*' } | Select-Object -First 1
    if ($jxDir) { $DriveRoot = $jxDir.FullName }
}

$PdfInDir   = Join-Path $ProjectRoot "inputs\jx\$Subject\重問PDF"
$TransInDir = Join-Path $ProjectRoot "inputs\jx\$Subject\講義逐語"
$JxOutDir   = Join-Path $ProjectRoot "outputs\jx\${Subject}JX"
$TtsBase    = Join-Path $ProjectRoot "outputs\tts"

function Get-IdNumber([string]$id) {
    if ($id -match '(\d+)\s*$') { return [int]$Matches[1] }
    return $null
}
function Find-TranscriptFile([int]$num) {
    if (-not (Test-Path -LiteralPath $TransInDir)) { return $null }
    $cands = @(Get-ChildItem -LiteralPath $TransInDir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in '.txt','.md' } |
        Where-Object { ($_.BaseName -match '重問(?:逐語)?\s*0*(\d+)') -and ([int]$Matches[1] -eq $num) } |
        Sort-Object { $_.Extension -ne '.txt' })
    if ($cands.Count -gt 0) { return $cands[0] }
    return $null
}
# git ヘルパ（相対パスは forward slash で渡す）
function Git-Tracked([string]$relPath) {
    git ls-files --error-unmatch -- $relPath *> $null
    return ($LASTEXITCODE -eq 0)
}
function Git-Clean([string]$relPath) {
    git diff --quiet -- $relPath; $a = $LASTEXITCODE
    git diff --cached --quiet -- $relPath; $b = $LASTEXITCODE
    return (($a -eq 0) -and ($b -eq 0))
}

$pushNeeded = $false
$cleanupHold = $false

foreach ($id in $Ids) {
    Write-Host "`n=== finalize $id ===" -ForegroundColor Cyan
    $num = Get-IdNumber $id
    $htmlRel = "outputs/jx/${Subject}JX/$id.html"
    $htmlAbs = Join-Path $JxOutDir "$id.html"
    if (-not (Test-Path -LiteralPath $htmlAbs)) {
        Write-Host "[SKIP] HTML が無い: $htmlAbs" -ForegroundColor Yellow; continue
    }

    # --- ① GitHub バックアップ（HTML + TTS 台本）---
    $addPaths = @($htmlRel)
    $ttsDir = Join-Path $TtsBase $id
    if (Test-Path -LiteralPath $ttsDir) { $addPaths += "outputs/tts/$id" }
    if ($DryRun) {
        Write-Host "  [DRYRUN] git add $($addPaths -join ' ') ; commit"
    } else {
        git add -- $addPaths
        # 差分があれば commit（無ければ既コミット済みとして続行）
        git diff --cached --quiet -- $addPaths
        if ($LASTEXITCODE -ne 0) {
            git commit -q -m "chore(jx): $id を生成・GitHub バックアップ保存（HTML＋TTS台本）"
            Write-Host "  [① backup] commit 済み: $id" -ForegroundColor Green
            $pushNeeded = $true
        } else {
            Write-Host "  [① backup] 既にコミット済み（差分なし）: $id" -ForegroundColor DarkGray
        }
    }

    if ($NoCleanup) { continue }

    # --- ② 入力クリーンアップ（PDF + 逐語）---
    if ($null -eq $num) { Write-Host "  [② cleanup] 番号抽出不可 → スキップ" -ForegroundColor Yellow; continue }

    # ガード(a): HTML がコミット済み＆差分なし
    if (-not $DryRun) {
        if (-not (Git-Tracked $htmlRel)) { Write-Host "  [HOLD] HTML 未追跡 → 入力を消さない" -ForegroundColor Yellow; $cleanupHold=$true; continue }
        if (-not (Git-Clean   $htmlRel)) { Write-Host "  [HOLD] HTML に未コミット差分 → 入力を消さない" -ForegroundColor Yellow; $cleanupHold=$true; continue }
    }

    $pdfAbs   = Join-Path $PdfInDir "$num.pdf"
    $trFile   = Find-TranscriptFile $num
    $rmRel = @()

    # ガード(b): Drive バックアップ存在確認
    $driveOk = $true
    if (-not $NoDriveCheck) {
        if ($null -eq $DriveRoot) {
            Write-Host "  [HOLD] Drive 未マウント → バックアップ確認不可。クリーンアップ中止（-NoDriveCheck で緊急回避可）" -ForegroundColor Yellow
            $cleanupHold=$true; continue
        }
        $drivePdf = Join-Path (Join-Path $DriveRoot $DriveHtml[$Subject]) "重問PDF\$num.pdf"
        if ((Test-Path -LiteralPath $pdfAbs) -and -not (Test-Path -LiteralPath $drivePdf)) {
            Write-Host "  [HOLD] PDF の Drive バックアップ無し: $drivePdf → 先に jx-deploy" -ForegroundColor Yellow; $driveOk=$false
        }
        if ($trFile) {
            $driveTr = Join-Path (Join-Path $DriveRoot $DriveHtml[$Subject]) "講義逐語\$($trFile.Name)"
            if (-not (Test-Path -LiteralPath $driveTr)) {
                Write-Host "  [HOLD] 逐語の Drive バックアップ無し: $driveTr → 先に jx-deploy" -ForegroundColor Yellow; $driveOk=$false
            }
        }
    }
    if (-not $driveOk) { $cleanupHold=$true; continue }

    if (Test-Path -LiteralPath $pdfAbs) { $rmRel += "inputs/jx/$Subject/重問PDF/$num.pdf" }
    if ($trFile) { $rmRel += "inputs/jx/$Subject/講義逐語/$($trFile.Name)" }
    if ($rmRel.Count -eq 0) { Write-Host "  [② cleanup] 削除対象なし（既に削除済み）" -ForegroundColor DarkGray; continue }

    if ($DryRun) {
        Write-Host "  [DRYRUN] git rm $($rmRel -join ' ') ; commit"
    } else {
        git rm --quiet -- $rmRel
        git commit -q -m "chore(jx): $id 処理済み入力（PDF＋逐語）を削除（Drive バックアップ済）"
        Write-Host "  [② cleanup] 入力削除 commit 済み: $($rmRel -join ', ')" -ForegroundColor Green
        $pushNeeded = $true
    }
}

# --- ③ push ---
if (-not $DryRun -and $pushNeeded -and -not $NoPush) {
    Write-Host "`n--- push origin master ---" -ForegroundColor Cyan
    $ok = $false
    for ($i=1; $i -le 3; $i++) {
        git push origin master
        if ($LASTEXITCODE -eq 0) { $ok=$true; break }
        Write-Host "[push] 失敗（試行 $i/3）。再試行..." -ForegroundColor Yellow
        Start-Sleep -Seconds ([math]::Pow(2,$i))
    }
    if ($ok) { Write-Host "[push] 完了。" -ForegroundColor Green }
    else { Write-Host "[push] 3 回失敗。後で手動 push してください。" -ForegroundColor Red; exit 1 }
}
if ($cleanupHold) { Write-Host "`n[NOTE] 一部 HOLD（入力未削除）あり。上記理由を解消後に再実行してください。" -ForegroundColor Yellow }
exit 0
