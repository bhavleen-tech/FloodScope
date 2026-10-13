@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
if not exist .venv\Scripts\python.exe (
  %PY% -m venv .venv
  if errorlevel 1 (echo Could not create Python virtual environment. & pause & exit /b 1)
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed. Check Python version and internet connection. & pause & exit /b 1)
echo Open http://127.0.0.1:8000 in your browser.
start "" http://127.0.0.1:8000
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
