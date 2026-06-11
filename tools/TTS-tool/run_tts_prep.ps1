# ============================================================
# TTS Tab Preparation Launcher (works on both xnrg2 and OWNER PC)
#
# Auto-detects user profile path, so no per-PC editing needed.
# Place this file together with prep_tts_tabs.py in the same folder.
#
# Usage:
#   .\run_tts_prep.ps1 -Account acc1            # acc1, 15 tabs each
#   .\run_tts_prep.ps1 -Account acc2            # acc2, 15 tabs each
#   .\run_tts_prep.ps1 -Account acc1 -Count 5   # test, 5 tabs each
#
# First time per PC: log in to AI Studio on each opened Chrome window.
# After that, auto login (saved per profile dir).
# ============================================================
param(
    [ValidateSet("acc1","acc2")]
    [string]$Account = "acc1",
    [int]$Count = 15
)

$ErrorActionPreference = "Stop"

# --- Locate Chrome (try common install paths) ---
$ChromeCandidates = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
$Chrome = $ChromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Chrome) {
    Write-Host "[ERROR] chrome.exe not found in standard locations." -ForegroundColor Red
    exit 1
}

# --- Python script (same folder as this launcher) ---
$PyScript = Join-Path $PSScriptRoot "prep_tts_tabs.py"
if (-not (Test-Path $PyScript)) {
    Write-Host "[ERROR] prep_tts_tabs.py not found next to this launcher." -ForegroundColor Red
    exit 1
}

# --- Profile base dir: put debug profiles under the user's home ---
# Folder name includes PC name so xnrg2 and OWNER PC don't collide if synced.
$PC = $env:COMPUTERNAME
$Base = Join-Path $env:USERPROFILE "chrome-tts-profiles"

# --- Port / profile config per account ---
$Config = @{
    "acc1" = @{
        "Aoede"     = @{ Port = 9222; Profile = (Join-Path $Base "acc1-aoede") }
        "Laomedeia" = @{ Port = 9223; Profile = (Join-Path $Base "acc1-laome") }
    }
    "acc2" = @{
        "Aoede"     = @{ Port = 9224; Profile = (Join-Path $Base "acc2-aoede") }
        "Laomedeia" = @{ Port = 9225; Profile = (Join-Path $Base "acc2-laome") }
    }
}

$voices = $Config[$Account]

function Test-DebugPort($port) {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:$port/json/version" -TimeoutSec 2 | Out-Null
        return $true
    } catch { return $false }
}

function Start-DebugChrome($port, $profileDir) {
    if (Test-DebugPort $port) {
        Write-Host "  Port $port already running." -ForegroundColor Green
        return
    }
    Write-Host "  Starting Chrome on port $port ($profileDir)..." -ForegroundColor Cyan
    Start-Process $Chrome -ArgumentList `
        "--remote-debugging-port=$port", `
        "--user-data-dir=$profileDir", `
        "--no-first-run", `
        "--no-default-browser-check"
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep 1
        if (Test-DebugPort $port) {
            Write-Host "  Port $port is up." -ForegroundColor Green
            return
        }
    }
    Write-Host "  [WARN] Port $port did not come up within 15s." -ForegroundColor Yellow
}

Write-Host "=== TTS Tab Prep on [$PC] : account=[$Account], $Count tabs each ===" -ForegroundColor White
Write-Host "  Chrome : $Chrome" -ForegroundColor DarkGray
Write-Host "  Profiles base: $Base" -ForegroundColor DarkGray

# 1. Start the two Chrome windows (Aoede / Laomedeia) for this account
Start-DebugChrome $voices["Aoede"].Port     $voices["Aoede"].Profile
Start-DebugChrome $voices["Laomedeia"].Port $voices["Laomedeia"].Profile

# 2. Login check
Write-Host ""
Write-Host "Make sure both windows are logged in to AI Studio with the [$Account] account." -ForegroundColor Yellow
Write-Host "If first time on this PC, log in on each Chrome, then press Enter." -ForegroundColor Yellow
Read-Host "Press Enter when ready"

# 3. Prepare tabs (Aoede then Laomedeia)
Write-Host ""
Write-Host "--- [$Account] Aoede $Count tabs ---" -ForegroundColor Cyan
python $PyScript --voice Aoede --port $($voices["Aoede"].Port) --count $Count

Write-Host ""
Write-Host "--- [$Account] Laomedeia $Count tabs ---" -ForegroundColor Cyan
python $PyScript --voice Laomedeia --port $($voices["Laomedeia"].Port) --count $Count

Write-Host ""
Write-Host "=== [$Account] DONE on [$PC] ===" -ForegroundColor Green
