@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

where pwsh.exe >nul 2>nul
if %ERRORLEVEL%==0 (
  set "RUNNER=pwsh.exe"
) else (
  set "RUNNER=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
)

"%RUNNER%" -NoProfile -ExecutionPolicy Bypass ^
  -File "%SCRIPT_DIR%sync-repo-from-master.ps1" ^
  -ProjectRoot "%PROJECT_ROOT%" ^
  -Remote origin ^
  -Branch master ^
  -Quiet

endlocal
exit /b %ERRORLEVEL%
