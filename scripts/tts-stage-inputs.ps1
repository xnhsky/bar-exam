# tts-stage-inputs.ps1
#
# 【JX パイプライン → Gemini TTS 連携・橋渡し】
# 既存 jx-batch-runner.ps1 が生成・検証した音声台本
#   outputs/tts/{PROBLEM_ID}/{ID}-{N}{a-d}.txt
# を、Gemini TTS の入力フォルダ
#   tts/input_texts/
# へコピー（集約）する。コピー後 tts/run-tts.ps1 で wav 化する想定。
#
# 設計方針（疎結合・課金 API は手動トリガー）:
#   - jx-batch-runner.ps1 は改変しない（無料のローカル生成と課金 TTS を分離）
#   - 既に tts/output_audio/{stem}.wav がある台本はコピーしない（重複課金防止・generate_tts.py 側でも二重に防御）
#   - コピーのみ。元の outputs/tts/ は一切削除・変更しない
#
# 実行例:
#   pwsh -NoProfile -File scripts\tts-stage-inputs.ps1 -ProblemId 刑JX032         # 1 問だけ集約
#   pwsh -NoProfile -File scripts\tts-stage-inputs.ps1 -ProblemId 刑JX032 -DryRun  # コピー予定の確認のみ
#   pwsh -NoProfile -File scripts\tts-stage-inputs.ps1                            # outputs/tts 配下の全問題を集約
#   pwsh -NoProfile -File scripts\tts-stage-inputs.ps1 -Run                       # 集約後に run-tts.ps1 を続けて実行

param(
    [string]$ProblemId = "",   # 例: 刑JX032。未指定なら outputs/tts 配下の全 ID
    [switch]$Force,            # 既に wav がある台本もコピーする
    [switch]$Run,              # 集約後に tts/run-tts.ps1 を実行
    [switch]$DryRun            # コピーせず予定だけ表示
)

# === stdout/stderr UTF-8 化 ===
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# === パス定義（scripts\ の親 = プロジェクトルート）===
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$TtsSrcBase  = Join-Path $ProjectRoot "outputs\tts"        # JX パイプラインの台本出力
$TtsInputDir = Join-Path $ProjectRoot "tts\input_texts"    # Gemini TTS 入力
$TtsAudioDir = Join-Path $ProjectRoot "tts\output_audio"   # 既存 wav 判定用
$RunTts      = Join-Path $ProjectRoot "tts\run-tts.ps1"

if (-not (Test-Path $TtsSrcBase)) {
    Write-Host "[ABORT] 台本ソースがありません: $TtsSrcBase" -ForegroundColor Red
    Write-Host "  先に jx-batch-runner.ps1 で JX→台本txt を生成してください。" -ForegroundColor Yellow
    exit 1
}
if (-not $DryRun) {
    if (-not (Test-Path $TtsInputDir)) { New-Item -Path $TtsInputDir -ItemType Directory -Force | Out-Null }
}

# === コピー対象の問題フォルダを決定 ===
if ($ProblemId) {
    $srcDirs = @(Get-Item -Path (Join-Path $TtsSrcBase $ProblemId) -ErrorAction SilentlyContinue)
    if (-not $srcDirs -or $srcDirs.Count -eq 0) {
        Write-Host "[ABORT] 台本フォルダが見つかりません: $(Join-Path $TtsSrcBase $ProblemId)" -ForegroundColor Red
        exit 1
    }
} else {
    $srcDirs = @(Get-ChildItem -Path $TtsSrcBase -Directory | Sort-Object Name)
}

Write-Host "=== tts-stage-inputs 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
Write-Host "ソース: $TtsSrcBase  (対象 $($srcDirs.Count) 問題)"
Write-Host "宛先  : $TtsInputDir"
Write-Host "Force=$Force / DryRun=$DryRun / Run=$Run"

$copied = 0; $skippedWav = 0; $skippedSame = 0

foreach ($dir in $srcDirs) {
    $txts = @(Get-ChildItem -Path $dir.FullName -Filter "*.txt" -File -ErrorAction SilentlyContinue | Sort-Object Name)
    if ($txts.Count -eq 0) { continue }
    Write-Host "`n--- [$($dir.Name)] $($txts.Count) 件 ---" -ForegroundColor Yellow
    foreach ($txt in $txts) {
        $stem    = [System.IO.Path]::GetFileNameWithoutExtension($txt.Name)
        $destTxt = Join-Path $TtsInputDir $txt.Name
        $wavPath = Join-Path $TtsAudioDir "$stem.wav"

        # 既に wav 済み → コピー不要（-Force で上書き集約は可）
        if ((Test-Path $wavPath) -and -not $Force) {
            Write-Host "  [SKIP wav済] $($txt.Name)" -ForegroundColor DarkGray
            $skippedWav++
            continue
        }
        # 既に同名 txt が入力にあり中身一致 → スキップ
        if ((Test-Path $destTxt) -and -not $Force) {
            $srcHash = (Get-FileHash $txt.FullName -Algorithm SHA256).Hash
            $dstHash = (Get-FileHash $destTxt      -Algorithm SHA256).Hash
            if ($srcHash -eq $dstHash) {
                Write-Host "  [SKIP 同一]  $($txt.Name)" -ForegroundColor DarkGray
                $skippedSame++
                continue
            }
        }

        if ($DryRun) {
            Write-Host "  [DRYRUN] would copy -> $destTxt" -ForegroundColor Cyan
        } else {
            Copy-Item -Path $txt.FullName -Destination $destTxt -Force
            Write-Host "  [COPY] $($txt.Name)" -ForegroundColor Green
        }
        $copied++
    }
}

Write-Host "`n--- 集約結果 ---" -ForegroundColor Yellow
Write-Host "コピー: $copied / wav済スキップ: $skippedWav / 同一スキップ: $skippedSame"

if ($DryRun) {
    Write-Host "[DRY-RUN] 実コピーなし。終了。" -ForegroundColor Yellow
    exit 0
}

if ($Run) {
    if (Test-Path $RunTts) {
        Write-Host "`n=== run-tts.ps1 を続けて実行します ===" -ForegroundColor Cyan
        & pwsh -NoProfile -File $RunTts
        exit $LASTEXITCODE
    } else {
        Write-Host "[WARN] run-tts.ps1 が見つかりません: $RunTts" -ForegroundColor Yellow
    }
}

Write-Host "`n次の手順:  pwsh -NoProfile -File tts\run-tts.ps1" -ForegroundColor Cyan
exit 0
