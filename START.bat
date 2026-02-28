@echo off
title AI Interviewer — Start
color 0B
cls

cd /d "%~dp0"

echo ============================================================
echo   AI INTERVIEWER
echo ============================================================
echo.

REM ── Use .venv Python directly (no PATH needed) ──────────────
set VENV_PY=.venv\Scripts\python.exe

if not exist "%VENV_PY%" (
    echo  [ERROR] .venv\Scripts\python.exe not found.
    echo.
    echo  Run SETUP.bat first, then try again.
    echo.
    pause
    exit /b 1
)

if not exist "backend\app.py" (
    echo  [ERROR] backend\app.py not found.
    echo  Run this from the project root folder.
    echo.
    pause
    exit /b 1
)

echo  Python  : %VENV_PY%
echo  Backend : backend\app.py
echo.
echo  Starting Flask...
echo  Browser will open at:  http://localhost:5000
echo.
echo  ── Press Ctrl+C to stop ────────────────────────────────
echo.

REM ── Open browser after 4 seconds (in background) ────────────
start "" cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:5000"

REM ── Run Flask using venv Python directly ────────────────────
"%VENV_PY%" backend\app.py

echo.
echo  Server stopped.
pause >nul
