@echo off
setlocal
echo Starting English Learning Assistant Web Server...
cd /d "%~dp0\.venv"

REM Ensure Flask is installed in this virtual environment
Scripts\python.exe -m pip show flask >nul 2>&1
if errorlevel 1 (
  echo Installing Flask in local virtual environment...
  Scripts\python.exe -m pip install flask
)

Scripts\python.exe app.py
pause
