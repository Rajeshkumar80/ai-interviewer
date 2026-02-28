@echo off
title AI Interviewer — Setup
color 0A
cls

cd /d "%~dp0"

echo ============================================================
echo   AI INTERVIEWER — First-Time Setup
echo ============================================================
echo.

REM ── If .venv already exists, skip setup ─────────────────────
if exist ".venv\Scripts\activate.bat" (
    echo  .venv already exists — setup is already done!
    echo.
    echo  Just run  START.bat  to launch the application.
    echo.
    pause
    exit /b 0
)

REM ── Find Python ─────────────────────────────────────────────
echo [1/3] Finding Python...
echo.

set PYTHON_EXE=

REM Try the exact path found in .venv/pyvenv.cfg on this machine
if exist "C:\Users\rajes\AppData\Local\Programs\Python\Python313\python.exe" (
    set PYTHON_EXE=C:\Users\rajes\AppData\Local\Programs\Python\Python313\python.exe
    goto :found_python
)
REM Try %LOCALAPPDATA% paths (works for any username)
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    goto :found_python
)
REM Try PATH commands
python --version >nul 2>&1 && set PYTHON_EXE=python && goto :found_python
py --version >nul 2>&1 && set PYTHON_EXE=py && goto :found_python
python3 --version >nul 2>&1 && set PYTHON_EXE=python3 && goto :found_python

echo  [ERROR] Cannot find Python on this machine.
echo.
echo  Please install Python 3.9+ from: https://www.python.org/downloads/
echo  During install, check: [x] Add Python to PATH
echo.
pause
exit /b 1

:found_python
echo   Python found: %PYTHON_EXE%
echo.

REM ── Create .venv ────────────────────────────────────────────
echo [2/3] Creating virtual environment (.venv)...
"%PYTHON_EXE%" -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Failed to create .venv
    pause
    exit /b 1
)
echo   .venv created. OK.
echo.

REM ── Install packages ────────────────────────────────────────
echo [3/3] Installing backend packages (may take 1-2 min)...
echo.
call .venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r backend\requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Package install failed. Check internet and requirements.txt
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo.
echo   Run  START.bat  to launch the app.
echo   Open browser at:  http://localhost:5000
echo   Demo login:       demo@aiinterviewer.com / Demo1234!
echo ============================================================
echo.
pause
