@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem Account selection, tab count, Chrome-kill (time-shift) and run are all
rem handled in PowerShell so the menu can show auto-detected account names
rem read from account_names.json.
powershell -ExecutionPolicy Bypass -File ".\run_tts_prep.ps1" -Menu
