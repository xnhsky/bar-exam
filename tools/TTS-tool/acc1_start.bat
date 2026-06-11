@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\run_tts_prep.ps1" -Account acc1
pause
