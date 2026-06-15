# jx-deploy.ps1 — JX 成果物（JX HTML / TTS 台本 / 音声 wav）を配置する
#
# 配置先は 2 系統（両方に置く。Drive 未マウント時は repo ミラーのみ）:
#   ① repo ミラー : {repo}\deploy\2 JX_論 文\...           （常時・H: と同階層）
#   ② Google Drive: H:\マイドライブ\CATALINA＿G共有\■予備試験進行中\2 JX_論 文\...（マウント時のみ）
#
# 科目ごとの配置:
#   - JX HTML  → 「{2 JX_論 文}\00N_科目\」（フラット）
#   - TTS 台本 → 「{2 JX_論 文}\A_重問耳トレ\N 科目\TTSファイル原本\{問題ID}\」（問題IDサブフォルダ内）
#   - 音声 wav → 「{2 JX_論 文}\A_重問耳トレ\N 科目\{問題ID}\」（問題IDサブフォルダ内）
#     ※ 台本/wav は問題ごとにフォルダを作ってその中へ格納（ユーザー指示 2026-06-06）。HTML は従来どおりフラット。
#   - RX カード → 「{2 JX_論 文}\B_RX\00N_科目\」（フラット・ユーザー指示 2026-06-11）
#   - ARBOR    → 「{2 JX_論 文}\C_ARBOR\00N_科目\」（フラット・同上）
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
$RxRoot      = 'B_RX'            # RX 論証カードの系統フォルダ（2 JX_論 文 直下）
$ArbRoot     = 'C_ARBOR'         # ARBOR 樹形図の系統フォルダ（同上）

# === 配置先ベースの解決 ===
# ① repo ミラー（常時）
$RepoBase = Join-Path (Join-Path $ProjectRoot 'deploy') $JxRootName
# ② Drive（実体をワイルドカード解決＝全角ゆれ対策。未マウントなら $null）
#    PC により Drive のマウント形態が異なる（H:\マイドライブ … or D:\GoogleDrive …）ため
#    複数候補ルートを順に試し、最初に存在したものを採用する。
$DriveBase = $null
$DriveRootCands = @(
    'H:\マイドライブ\CATALINA＿G共有\■予備試験進行中',
    'D:\GoogleDrive\CATALINA＿G共有\■予備試験進行中',
    'G:\マイドライブ\CATALINA＿G共有\■予備試験進行中'
)
foreach ($DriveRootCand in $DriveRootCands) {
    if (Test-Path -LiteralPath $DriveRootCand) {
        $jxDir = Get-ChildItem -LiteralPath $DriveRootCand -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like '*JX*論*文*' } | Select-Object -First 1
        if ($jxDir) { $DriveBase = $jxDir.FullName; break }
    }
}

# 配置先（存在するもの）一覧
$Targets = @()
$Targets += [PSCustomObject]@{ Label = 'repo'; Base = $RepoBase }
if ($DriveBase) { $Targets += [PSCustomObject]@{ Label = "Drive($(($DriveBase -split '\\')[0]))"; Base = $DriveBase } }
else { Write-Host "[NOTE] Drive 未マウント（H:\マイドライブ / D:\GoogleDrive / G:\マイドライブ いずれも不在）→ repo ミラーのみ配置（後で Drive 同期）。" -ForegroundColor Yellow }

function Ensure-Dir([string]$p) {
    if (-not (Test-Path -LiteralPath $p)) {
        if ($DryRun) { Write-Host "  [DRYRUN] mkdir $p" }
        else { New-Item -ItemType Directory -Force -Path $p | Out-Null }
    }
}

function Get-SubjectDirs([string]$base, $info) {
    # base = "...\2 JX_論 文"
    [PSCustomObject]@{
        Html  = Join-Path $base $info.html
        Mimi  = Join-Path (Join-Path $base $MimiRoot) $info.mimi
        Tts   = Join-Path (Join-Path (Join-Path $base $MimiRoot) $info.mimi) $TtsOrigName
        # 入力 PDF / 逐語の原本バックアップ（科目フォルダ直下・TX の「抽出PDF」と並行）
        Pdf   = Join-Path (Join-Path $base $info.html) '重問PDF'
        Trans = Join-Path (Join-Path $base $info.html) '講義逐語'
        # 副産物（RX 論証カード / ARBOR 樹形図）— 系統フォルダ内に科目フォルダ
        Rx    = Join-Path (Join-Path $base $RxRoot)  $info.html
        Arb   = Join-Path (Join-Path $base $ArbRoot) $info.html
    }
}

# ID（例 刑JX025）末尾の数字 → PDF/逐語の問題番号
function Get-IdNumber([string]$id) {
    if ($id -match '(\d+)\s*$') { return [int]$Matches[1] }
    return $null
}

# === -InitAll: 全7科目のフォルダを両配置先に作成 ===
if ($InitAll) {
    Write-Host "=== jx-deploy -InitAll：全7科目フォルダ作成（DryRun=$DryRun）===" -ForegroundColor Cyan
    foreach ($t in $Targets) {
        Write-Host "--- 配置先: $($t.Label)  ($($t.Base)) ---"
        foreach ($subj in $Map.Keys) {
            $d = Get-SubjectDirs $t.Base $Map[$subj]
            Ensure-Dir $d.Html; Ensure-Dir $d.Mimi; Ensure-Dir $d.Tts
            Ensure-Dir $d.Rx; Ensure-Dir $d.Arb
            # PDF/逐語の原本バックアップ先は Drive のみ（repo ミラーには作らない＝git 肥大化回避）
            if ($t.Label -ne 'repo') { Ensure-Dir $d.Pdf; Ensure-Dir $d.Trans }
            Write-Host ("  {0,-4} -> {1} / {2}\{3} / {4}\{1} / {5}\{1}" -f $subj, $Map[$subj].html, $Map[$subj].mimi, $TtsOrigName, $RxRoot, $ArbRoot)
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
# 入力 PDF / 逐語（原本バックアップ元）
$PdfInDir   = Join-Path $ProjectRoot "inputs\jx\$Subject\重問PDF"
$TransInDir = Join-Path $ProjectRoot "inputs\jx\$Subject\講義逐語"

# 問題番号に一致する逐語（.txt 優先）を探す。命名: {科目}_重問逐語NN / 旧 重問NN。
function Find-TranscriptFile([int]$num) {
    if (-not (Test-Path -LiteralPath $TransInDir)) { return $null }
    $cands = @(Get-ChildItem -LiteralPath $TransInDir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in '.txt','.md' } |
        Where-Object { ($_.BaseName -match '重問(?:逐語)?\s*0*(\d+)') -and ([int]$Matches[1] -eq $num) } |
        Sort-Object { $_.Extension -ne '.txt' })   # .txt を先頭に
    if ($cands.Count -gt 0) { return $cands[0] }
    return $null
}
$Ids = @()
if ($ProblemId) { $Ids = @($ProblemId) }
else { $Ids = @(Get-ChildItem -Path $JxOutDir -Filter "*.html" -File -ErrorAction SilentlyContinue | ForEach-Object { $_.BaseName }) }

# 副産物（RX/ARB）の生成元
$RxOutDir  = Join-Path $ProjectRoot "outputs\rx\${Subject}RX"
$ArbOutDir = Join-Path $ProjectRoot "outputs\arb\${Subject}ARB"

if ($Ids.Count -eq 0) { Write-Host "[NOTE] 配置対象 ID なし（$JxOutDir に HTML が無い）。" -ForegroundColor Yellow; exit 0 }

Write-Host "=== jx-deploy：$Subject / 対象 $($Ids.Count) 問 / 配置先 $($Targets.Count) 系統（DryRun=$DryRun）===" -ForegroundColor Cyan
$sumHtml = 0; $sumTxt = 0; $sumWav = 0; $sumPdf = 0; $sumTr = 0; $sumRx = 0; $sumArb = 0
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
        # RX 論証カード（outputs/rx/{科目}RX/{科目}RX{NNN}_*.html）→ B_RX\00N_科目\
        $idNum = Get-IdNumber $id
        if ($null -ne $idNum) {
            $rxPat = "${Subject}RX$($idNum.ToString('000'))_*.html"
            $rxFiles = @(Get-ChildItem -Path $RxOutDir -Filter $rxPat -File -ErrorAction SilentlyContinue)
            if ($rxFiles.Count -gt 0) {
                Ensure-Dir $d.Rx
                foreach ($r in $rxFiles) {
                    if ($DryRun) { Write-Host "  [DRYRUN] RX   $($r.Name) -> $($t.Label):$RxRoot\$($info.html)" }
                    else { Copy-Item -LiteralPath $r.FullName -Destination $d.Rx -Force; $sumRx++ }
                }
            }
        }
        # ARBOR 樹形図（outputs/arb/{科目}ARB/{ID}_ARB.html）→ C_ARBOR\00N_科目\
        $arbSrc = Join-Path $ArbOutDir "${id}_ARB.html"
        if (Test-Path -LiteralPath $arbSrc) {
            Ensure-Dir $d.Arb
            if ($DryRun) { Write-Host "  [DRYRUN] ARB  ${id}_ARB.html -> $($t.Label):$ArbRoot\$($info.html)" }
            else { Copy-Item -LiteralPath $arbSrc -Destination $d.Arb -Force; $sumArb++ }
        }
        # TTS 台本 txt（outputs/tts/{ID}/*.txt）→ TTSファイル原本\{問題ID}\ サブフォルダ内へ
        $txts = @(Get-ChildItem -Path (Join-Path $TtsBase $id) -Filter "*.txt" -File -ErrorAction SilentlyContinue)
        if ($txts.Count -gt 0) {
            $ttsDest = Join-Path $d.Tts $id          # 例: ...\TTSファイル原本\刑JX025\
            Ensure-Dir $ttsDest
            foreach ($x in $txts) {
                if ($DryRun) { } else { Copy-Item -LiteralPath $x.FullName -Destination $ttsDest -Force; $sumTxt++ }
            }
        }
        # 音声 wav（tts/output_audio/{ID}-*.wav）→ 耳トレ\N 科目\{問題ID}\ サブフォルダ内へ
        $wavs = @(Get-ChildItem -Path $WavDir -Filter "$id-*.wav" -File -ErrorAction SilentlyContinue)
        if ($wavs.Count -gt 0) {
            $wavDest = Join-Path $d.Mimi $id         # 例: ...\A_重問耳トレ\1 刑法\刑JX025\
            Ensure-Dir $wavDest
            foreach ($w in $wavs) {
                if ($DryRun) { } else { Copy-Item -LiteralPath $w.FullName -Destination $wavDest -Force; $sumWav++ }
            }
        }
        # 入力 PDF / 逐語の原本バックアップ（Drive のみ。repo ミラーは大容量 PDF の git 肥大化を避け対象外）。
        # ※ TX の「抽出PDF」と並行＝Drive を入力原本の恒久アーカイブにする。inputs からの削除は
        #    jx-cleanup-pdf.sh が「HTML コミット済み＋本バックアップ存在」を確認してから git rm する。
        if ($t.Label -ne 'repo') {
            $num = Get-IdNumber $id
            if ($null -ne $num) {
                $srcPdf = Join-Path $PdfInDir "$num.pdf"
                if (Test-Path -LiteralPath $srcPdf) {
                    Ensure-Dir $d.Pdf
                    if ($DryRun) { Write-Host "  [DRYRUN] PDF $num.pdf -> $($t.Label):$($info.html)\重問PDF" }
                    else { Copy-Item -LiteralPath $srcPdf -Destination $d.Pdf -Force; $sumPdf++ }
                }
                $srcTr = Find-TranscriptFile $num
                if ($srcTr) {
                    Ensure-Dir $d.Trans
                    if ($DryRun) { Write-Host "  [DRYRUN] 逐語 $($srcTr.Name) -> $($t.Label):$($info.html)\講義逐語" }
                    else { Copy-Item -LiteralPath $srcTr.FullName -Destination $d.Trans -Force; $sumTr++ }
                }
            }
        }
        if ($DryRun) { Write-Host ("  [DRYRUN] {0}: txt {1}本 -> {3}:{2}\TTSファイル原本\{0}\ ／ wav {5}本 -> {3}:{4}\{0}\" -f $id, $txts.Count, $info.mimi, $t.Label, $info.mimi, $wavs.Count) }
    }
    Write-Host "  [$($t.Label)] 配置先ベース: $($t.Base)" -ForegroundColor DarkGray
}
if (-not $DryRun) { Write-Host ("=== 配置完了: HTML {0} / 台本 {1} / wav {2} / PDF {3} / 逐語 {4} / RX {5} / ARB {6}（全系統合計）===" -f $sumHtml, $sumTxt, $sumWav, $sumPdf, $sumTr, $sumRx, $sumArb) -ForegroundColor Green }
exit 0
