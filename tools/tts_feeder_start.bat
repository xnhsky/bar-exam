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

rem --- Preflight: GUI deps installed? Missing -> auto install ---
python -c "import pyperclip, pyautogui, keyboard" >nul 2>nul
if errorlevel 1 (
    echo Installing GUI dependencies (pyperclip pyautogui keyboard)...
    python -m pip install pyperclip pyautogui keyboard
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies. Run manually:
        echo     python -m pip install pyperclip pyautogui keyboard
        echo.
        pause
        exit /b 1
    )
)

rem Launch the feeder GUI. Pass a folder path as %1 to preselect it,
rem otherwise pick it with the in-app folder button.
python "tts_feeder.py" %*

rem --- Keep the window open on any exit so an error message stays readable ---
echo.
echo ============================================================
echo  Finished. You can close this window.
echo ============================================================
pause
