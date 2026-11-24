@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\pythonw.exe (
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Python 3.12 is required. Install it from python.org and run this again.
    pause
    exit /b 1
  )
  .venv\Scripts\python.exe -m pip install -r requirements.txt
)
start "" .venv\Scripts\pythonw.exe main.py
