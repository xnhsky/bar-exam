@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal

:MENU
cls
echo ============================================================
echo   AI Studio TTS Tab Preparation
echo ============================================================
echo.
echo   Select account:
echo     [1] acc1
echo     [2] acc2
echo     [3] acc3
echo     [4] acc4
echo     [5] acc5
echo     [Q] Quit
echo.
set /p choice="Enter number (1-5) or Q: "

if /i "%choice%"=="Q" goto END
if "%choice%"=="1" set ACC=acc1& goto TABS
if "%choice%"=="2" set ACC=acc2& goto TABS
if "%choice%"=="3" set ACC=acc3& goto TABS
if "%choice%"=="4" set ACC=acc4& goto TABS
if "%choice%"=="5" set ACC=acc5& goto TABS
echo Invalid choice. Try again.
pause
goto MENU

:TABS
echo.
set /p cnt="Tabs per voice (Enter = 15): "
if "%cnt%"=="" set cnt=15

echo.
echo ------------------------------------------------------------
echo   Closing all Chrome to free memory (time-shift operation)...
echo ------------------------------------------------------------
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo.
echo   Starting %ACC% with %cnt% tabs each...
echo.
powershell -ExecutionPolicy Bypass -File ".\run_tts_prep.ps1" -Account %ACC% -Count %cnt%

echo.
echo ============================================================
echo   Done. Press any key to return to menu, or close window.
echo ============================================================
pause >nul
goto MENU

:END
endlocal
