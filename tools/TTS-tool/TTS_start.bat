@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem --- Preflight: Python present? (ASCII only: non-ASCII here breaks cmd parsing) ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] python not found. Install Python and add it to PATH.
    echo.
    pause
    exit /b 1
)

rem --- Preflight: is the 'playwright' package installed? Missing -> instant crash ---
python -c "import playwright" >nul 2>nul
if errorlevel 1 (
    echo playwright is not installed. Installing now...
    python -m pip install playwright
    if errorlevel 1 (
        echo [ERROR] Failed to install playwright. Run manually:
        echo     python -m pip install playwright
        echo.
        pause
        exit /b 1
    )
)

rem Account selection, tab count, Chrome-kill (time-shift) and run are all
rem handled in PowerShell so the menu can show auto-detected account names
rem read from account_names.json.
powershell -ExecutionPolicy Bypass -File ".\run_tts_prep.ps1" -Menu

rem --- Keep the window open on any exit so an error message stays readable ---
echo.
echo ============================================================
echo  Finished. You can close this window.
echo ============================================================
pause
