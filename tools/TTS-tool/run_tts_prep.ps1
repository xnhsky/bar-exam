# ============================================================
# TTS Tab Preparation Launcher (works on both xnrg2 and OWNER PC)
#
# Auto-detects user profile path, so no per-PC editing needed.
# Place this file together with prep_tts_tabs.py in the same folder.
#
# Usage:
#   .\run_tts_prep.ps1 -Menu                     # interactive menu (account names auto-shown)
#   .\run_tts_prep.ps1 -Account acc1             # acc1, 15 tabs each
#   .\run_tts_prep.ps1 -Account acc1 -Count 5    # test, 5 tabs each
#
# Account names: after you run an account once while logged in, the logged-in
# Gmail is detected and cached to account_names.json, then shown in the menu
# automatically (e.g. "[1] tanaka@gmail.com (acc1)"). No manual naming needed.
#
# First time per PC: log in to AI Studio on each opened Chrome window.
# After that, auto login (saved per profile dir).
# ============================================================
param(
    [switch]$Menu,
    [ValidateSet("acc1","acc2","acc3","acc4","acc5")]
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

# --- Account name cache (written by prep_tts_tabs.py --account) ---
$CachePath = Join-Path $PSScriptRoot "account_names.json"

# --- Profile base dir: put debug profiles under the user's home ---
# Folder name includes PC name so xnrg2 and OWNER PC don't collide if synced.
$PC = $env:COMPUTERNAME
$Base = Join-Path $env:USERPROFILE "chrome-tts-profiles"

# --- Port / profile config per account ---
# acc1: 9222/9223, acc2: 9224/9225, acc3: 9226/9227, acc4: 9228/9229, acc5: 9230/9231
$Config = @{
    "acc1" = @{
        "Aoede"     = @{ Port = 9222; Profile = (Join-Path $Base "acc1-aoede") }
        "Laomedeia" = @{ Port = 9223; Profile = (Join-Path $Base "acc1-laome") }
    }
    "acc2" = @{
        "Aoede"     = @{ Port = 9224; Profile = (Join-Path $Base "acc2-aoede") }
        "Laomedeia" = @{ Port = 9225; Profile = (Join-Path $Base "acc2-laome") }
    }
    "acc3" = @{
        "Aoede"     = @{ Port = 9226; Profile = (Join-Path $Base "acc3-aoede") }
        "Laomedeia" = @{ Port = 9227; Profile = (Join-Path $Base "acc3-laome") }
    }
    "acc4" = @{
        "Aoede"     = @{ Port = 9228; Profile = (Join-Path $Base "acc4-aoede") }
        "Laomedeia" = @{ Port = 9229; Profile = (Join-Path $Base "acc4-laome") }
    }
    "acc5" = @{
        "Aoede"     = @{ Port = 9230; Profile = (Join-Path $Base "acc5-aoede") }
        "Laomedeia" = @{ Port = 9231; Profile = (Join-Path $Base "acc5-laome") }
    }
}

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

# --- Read cached account names (acc -> display label). Missing -> key itself. ---
function Get-AccountLabels {
    $names = @{}
    if (Test-Path $CachePath) {
        try {
            $json = Get-Content $CachePath -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($p in $json.PSObject.Properties) { $names[$p.Name] = $p.Value }
        } catch { }
    }
    return $names
}

# --- Run one account: start 2 Chromes, wait login, prep tabs (Aoede then Laomedeia) ---
function Invoke-Account {
    param([string]$Acct, [int]$Cnt)

    $voices = $Config[$Acct]
    Write-Host "=== TTS Tab Prep on [$PC] : account=[$Acct], $Cnt tabs each ===" -ForegroundColor White
    Write-Host "  Chrome : $Chrome" -ForegroundColor DarkGray
    Write-Host "  Profiles base: $Base" -ForegroundColor DarkGray

    # 1. Start the two Chrome windows (Aoede / Laomedeia) for this account
    Start-DebugChrome $voices["Aoede"].Port     $voices["Aoede"].Profile
    Start-DebugChrome $voices["Laomedeia"].Port $voices["Laomedeia"].Profile

    # 2. Login check
    Write-Host ""
    Write-Host "Make sure both windows are logged in to AI Studio with the [$Acct] account." -ForegroundColor Yellow
    Write-Host "If first time on this PC, log in on each Chrome, then press Enter." -ForegroundColor Yellow
    Read-Host "Press Enter when ready"

    # 3. Prepare tabs (Aoede then Laomedeia). --account lets the script cache the
    #    detected Gmail into account_names.json for the menu display.
    Write-Host ""
    Write-Host "--- [$Acct] Aoede $Cnt tabs ---" -ForegroundColor Cyan
    python $PyScript --voice Aoede --port $($voices["Aoede"].Port) --count $Cnt --account $Acct

    Write-Host ""
    Write-Host "--- [$Acct] Laomedeia $Cnt tabs ---" -ForegroundColor Cyan
    python $PyScript --voice Laomedeia --port $($voices["Laomedeia"].Port) --count $Cnt --account $Acct

    Write-Host ""
    Write-Host "=== [$Acct] DONE on [$PC] ===" -ForegroundColor Green
}

# --- Interactive menu (account names auto-resolved from cache) ---
function Show-Menu {
    $accounts = @("acc1", "acc2", "acc3", "acc4", "acc5")
    while ($true) {
        Clear-Host
        $names = Get-AccountLabels
        Write-Host "============================================================"
        Write-Host "  AI Studio TTS Tab Preparation"
        Write-Host "============================================================"
        Write-Host ""
        Write-Host "  Select account:"
        for ($i = 0; $i -lt $accounts.Count; $i++) {
            $key = $accounts[$i]
            if ($names.ContainsKey($key) -and $names[$key]) {
                $label = "{0}  ({1})" -f $names[$key], $key
            } else {
                $label = $key
            }
            Write-Host ("    [{0}] {1}" -f ($i + 1), $label)
        }
        Write-Host "    [Q] Quit"
        Write-Host ""
        $choice = Read-Host "Enter number (1-5) or Q"

        if ($choice -match '^[Qq]$') { return }
        if ($choice -notmatch '^[1-5]$') {
            Write-Host "Invalid choice. Try again." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
            continue
        }
        $sel = $accounts[[int]$choice - 1]

        $cntInput = Read-Host "Tabs per voice (Enter = 15)"
        $cnt = 15
        if ($cntInput -match '^\d+$') { $cnt = [int]$cntInput }

        # Choice-A (time-shift): free memory by closing all Chrome before launching.
        Write-Host ""
        Write-Host "------------------------------------------------------------"
        Write-Host "  Closing all Chrome to free memory (time-shift operation)..."
        Write-Host "------------------------------------------------------------"
        taskkill /F /IM chrome.exe 2>$null | Out-Null
        Start-Sleep -Seconds 3

        Write-Host ""
        Write-Host "  Starting $sel with $cnt tabs each..."
        Write-Host ""
        Invoke-Account -Acct $sel -Cnt $cnt

        Write-Host ""
        Read-Host "Press Enter to return to menu"
    }
}

# --- Entry point ---
if ($Menu) {
    Show-Menu
} else {
    Invoke-Account -Acct $Account -Cnt $Count
}
