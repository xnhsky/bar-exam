@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem --- Resolve a REAL Python. Prefer the py launcher: plain "python" may resolve
rem     to the 0-byte Microsoft Store stub (WindowsApps) which silently fails. ---
py -3 -c "import sys" >nul 2>nul && goto :use_py
where python >nul 2>nul && goto :use_python

echo [ERROR] Python not found. Install Python and add it to PATH,
echo         or install the "py" launcher.
echo.
pause
exit /b 1

rem NOTE: never put literal ( ) in echo text inside an if(...) block:
rem cmd closes the block at the first ) and dies with "was unexpected at this time".

:use_py
py -3 -c "import pyperclip, pyautogui, keyboard" >nul 2>nul
if errorlevel 1 (
    echo Installing GUI dependencies: pyperclip pyautogui keyboard ...
    py -3 -m pip install pyperclip pyautogui keyboard
)
py -3 "tts_feeder.py" %*
goto :done

:use_python
python -c "import pyperclip, pyautogui, keyboard" >nul 2>nul
if errorlevel 1 (
    echo Installing GUI dependencies: pyperclip pyautogui keyboard ...
    python -m pip install pyperclip pyautogui keyboard
)
python "tts_feeder.py" %*
goto :done

:done
rem --- Keep the window open on any exit so an error message stays readable ---
echo.
echo ============================================================
echo  Finished. You can close this window.
echo ============================================================
pause
