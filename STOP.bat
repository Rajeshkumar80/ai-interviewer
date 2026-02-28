@echo off
title AI Interviewer — Stop
color 0C
cls

echo ============================================================
echo   AI INTERVIEWER — Stopping Server
echo ============================================================
echo.
echo  Killing any Python process running on port 5000...

REM Kill by port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    echo  Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo  Done. Server stopped.
echo  Run START.bat to restart.
echo.
pause
