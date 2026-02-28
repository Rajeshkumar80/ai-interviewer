@echo off
title AI Interviewer — Seed Analytics Data
color 0E
cls

cd /d "%~dp0"

echo ============================================================
echo   AI INTERVIEWER — Seeding Demo Analytics Data
echo ============================================================
echo.
echo  This inserts 18 interview sessions + 12 aptitude results
echo  for the demo account into MongoDB.
echo.

if not exist ".venv\Scripts\python.exe" (
    echo  [ERROR] .venv not found. Run SETUP.bat first.
    pause
    exit /b 1
)

.venv\Scripts\python.exe seed_analytics.py

echo.
echo ============================================================
pause
