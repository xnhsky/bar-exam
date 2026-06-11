@echo off
cd /d "%~dp0"
echo Closing all Chrome to free memory before acc2...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 3 /nobreak >nul
powershell -ExecutionPolicy Bypass -File ".\run_tts_prep.ps1" -Account acc2
pause
