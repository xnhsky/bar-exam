# jx-deploy.ps1 — JX 成果物（JX HTML / TTS 台本 / 音声 wav）を配置する
#
# 配置先は 2 系統（両方に置く。Drive 未マウント時は repo ミラーのみ）:
#   ① repo ミラー : {repo}\deploy\2 JX_論 文\...           （常時・H: と同階層）
#   ② Google Drive: H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\2 JX_論 文\...（マウント時のみ）
#
# 科目ごとの配置:
#   - JX HTML  → 「{2 JX_論 文}\00N_科目\」
#   - TTS 台本 → 「{2 JX_論 文}\A_重問耳トレ\N 科目\TTSファイル原本\」
#   - 音声 wav → 「{2 JX_論 文}\A_重問耳トレ\N 科目\」
#
# 使い方:
#   pwsh -NoProfile -File scripts/jx-deploy.ps1 -InitAll                 # 全7科目のフォルダを両方に作成
#   pwsh -NoProfile -File scripts/jx-deploy.ps1 -Subject 刑 -ProblemId 刑JX002   # 1問配置
#   pwsh -NoProfile -File scripts/jx-deploy.ps1 -Subject 刑              # 科目の全 HTML 分を配置
#   pwsh -NoProfile -File scripts/jx-deploy.ps1 -Subject 刑 -ProblemId 刑JX002 -DryRun
param(
    [ValidateSet('刑','刑訴','民','商','民訴','憲','行政')]
    [string]$Subject = '',
    [string]$ProblemId = '',   # 空なら科目の全 {ID}.html を対象
    [switch]$InitAll,          # 全7科目のフォルダを repo ミラー＋Drive に作成して終了
    [switch]$DryRun
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 科目 → Drive フォルダ名（HTML 用 00N_科目 / 耳トレ用 「N 科目」）
$Map = [ordered]@{
    '刑'   = @{ html = '001_刑法';       mimi = '1 刑法' }
    '刑訴' = @{ html = '002_刑事訴訟法'; mimi = '2 刑事訴訟法' }
    '民'   = @{ html = '003_民法';       mimi = '3 民法' }
    '商'   = @{ html = '004_商法';       mimi = '4 商法' }
    '民訴' = @{ html = '005_民事訴訟法'; mimi = '5 民事訴訟法' }
    '行政' = @{ html = '006_行政法';     mimi = '6 行政法' }
    '憲'   = @{ html = '007_憲法';       mimi = '7 憲法' }
}

$JxRootName  = '2 JX_論 文'      # H: と同名（論と文の間は全角空白）
$MimiRoot    = 'A_重問耳トレ'
$TtsOrigName = 'TTSファイル原本'

# === 配置先ベースの解決 ===
# ① repo ミラー（常時）
$RepoBase = Join-Path (Join-Path $ProjectRoot 'deploy') $JxRootName
# ② Drive（実体をワイルドカード解決＝全角ゆれ対策。未マウントなら $null）
$DriveBase = $null
$DriveRootCand = 'H:\マイドライブ\CATALINA＿G共有\■予備試験進行中'
if (Test-Path -LiteralPath $DriveRootCand) {
    $jxDir = Get-ChildItem -LiteralPath $DriveRootCand -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like '*JX*論*文*' } | Select-Object -First 1
    if ($jxDir) { $DriveBase = $jxDir.FullName }
}

# 配置先（存在するもの）一覧
$Targets = @()
$Targets += [PSCustomObject]@{ Label = 'repo'; Base = $RepoBase }
if ($DriveBase) { $Targets += [PSCustomObject]@{ Label = 'Drive(H:)'; Base = $DriveBase } }
else { Write-Host "[NOTE] H: ドライブ未マウント → repo ミラーのみ配置（後で Drive 同期）。" -ForegroundColor Yellow }

function Ensure-Dir([string]$p) {
    if (-not (Test-Path -LiteralPath $p)) {
        if ($DryRun) { Write-Host "  [DRYRUN] mkdir $p" }
        else { New-Item -ItemType Directory -Force -Path $p | Out-Null }
    }
}

function Get-SubjectDirs([string]$base, $info) {
    # base = "...\2 JX_論 文"
    [PSCustomObject]@{
        Html = Join-Path $base $info.html
        Mimi = Join-Path (Join-Path $base $MimiRoot) $info.mimi
        Tts  = Join-Path (Join-Path (Join-Path $base $MimiRoot) $info.mimi) $TtsOrigName
    }
}

# === -InitAll: 全7科目のフォルダを両配置先に作成 ===
if ($InitAll) {
    Write-Host "=== jx-deploy -InitAll：全7科目フォルダ作成（DryRun=$DryRun）===" -ForegroundColor Cyan
    foreach ($t in $Targets) {
        Write-Host "--- 配置先: $($t.Label)  ($($t.Base)) ---"
        foreach ($subj in $Map.Keys) {
            $d = Get-SubjectDirs $t.Base $Map[$subj]
            Ensure-Dir $d.Html; Ensure-Dir $d.Mimi; Ensure-Dir $d.Tts
            Write-Host ("  {0,-4} -> {1} / {2}\{3}" -f $subj, $Map[$subj].html, $Map[$subj].mimi, $TtsOrigName)
        }
    }
    Write-Host "=== InitAll 完了 ===" -ForegroundColor Green
    exit 0
}

# === 単一/科目配置 ===
if (-not $Subject) { Write-Host "[ABORT] -Subject か -InitAll を指定してください。" -ForegroundColor Red; exit 1 }
$info = $Map[$Subject]

# 対象 ID 群（ProblemId 指定 or 科目の全 HTML）
$JxOutDir = Join-Path $ProjectRoot "outputs\jx\${Subject}JX"
$TtsBase  = Join-Path $ProjectRoot "outputs\tts"
$WavDir   = Join-Path $ProjectRoot "tts\output_audio"
$Ids = @()
if ($ProblemId) { $Ids = @($ProblemId) }
else { $Ids = @(Get-ChildItem -Path $JxOutDir -Filter "*.html" -File -ErrorAction SilentlyContinue | ForEach-Object { $_.BaseName }) }

if ($Ids.Count -eq 0) { Write-Host "[NOTE] 配置対象 ID なし（$JxOutDir に HTML が無い）。" -ForegroundColor Yellow; exit 0 }

Write-Host "=== jx-deploy：$Subject / 対象 $($Ids.Count) 問 / 配置先 $($Targets.Count) 系統（DryRun=$DryRun）===" -ForegroundColor Cyan
$sumHtml = 0; $sumTxt = 0; $sumWav = 0
foreach ($t in $Targets) {
    $d = Get-SubjectDirs $t.Base $info
    Ensure-Dir $d.Html; Ensure-Dir $d.Mimi; Ensure-Dir $d.Tts
    foreach ($id in $Ids) {
        # HTML
        $html = Join-Path $JxOutDir "$id.html"
        if (Test-Path -LiteralPath $html) {
            if ($DryRun) { Write-Host "  [DRYRUN] HTML $id.html -> $($t.Label):$($info.html)" }
            else { Copy-Item -LiteralPath $html -Destination $d.Html -Force; $sumHtml++ }
        }
        # TTS 台本 txt（outputs/tts/{ID}/*.txt）
        $txts = @(Get-ChildItem -Path (Join-Path $TtsBase $id) -Filter "*.txt" -File -ErrorAction SilentlyContinue)
        foreach ($x in $txts) {
            if ($DryRun) { } else { Copy-Item -LiteralPath $x.FullName -Destination $d.Tts -Force; $sumTxt++ }
        }
        # 音声 wav（tts/output_audio/{ID}-*.wav）
        $wavs = @(Get-ChildItem -Path $WavDir -Filter "$id-*.wav" -File -ErrorAction SilentlyContinue)
        foreach ($w in $wavs) {
            if ($DryRun) { } else { Copy-Item -LiteralPath $w.FullName -Destination $d.Mimi -Force; $sumWav++ }
        }
        if ($DryRun) { Write-Host ("  [DRYRUN] {0}: txt {1}本 / wav {2}本 -> {3}" -f $id, $txts.Count, $wavs.Count, $t.Label) }
    }
    Write-Host "  [$($t.Label)] 配置先ベース: $($t.Base)" -ForegroundColor DarkGray
}
if (-not $DryRun) { Write-Host ("=== 配置完了: HTML {0} / 台本 {1} / wav {2}（全系統合計）===" -f $sumHtml, $sumTxt, $sumWav) -ForegroundColor Green }
exit 0
