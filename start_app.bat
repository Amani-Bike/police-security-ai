@echo off
title Police Security AI Platform

echo ============================================
echo SafetyNet - Police Security AI Platform
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python and make sure it's added to your PATH.
    pause
    exit /b 1
)

REM Install dependencies if not already installed
echo Installing dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo Warning: requirements.txt not found
)

REM Initialize the database
echo.
echo Initializing database...
if exist init_db.py (
    python init_db.py
) else (
    echo Warning: init_db.py not found
)

REM Start the server in a separate window and open browser
echo.
echo Starting the server...
start "" python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
timeout /t 5 /nobreak >nul
echo Opening browser...
start http://localhost:8000
echo Server started and browser opened.
echo Press any key to stop the server and exit.
echo.
pause >nul
taskkill /f /im python.exe >nul 2>&1