@echo off
title Codex Live Portal - Sovereign Local Server
color 0f
cls

echo ----------------------------------------------------------------
echo    ✴ CODEX LIVE PORTAL — INITIALIZING LOCAL SERVER
echo ----------------------------------------------------------------

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python to run the Codex.
    pause
    exit /b
)

:: Install Dependencies
echo [INFO] Verifying dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Could not install dependencies automatically.
    echo Please ensure 'flask' is installed (pip install flask).
    pause
)

:: Run Server
echo [INFO] Starting Flask Server...
echo [INFO] Access the portal at http://localhost:5000
echo ----------------------------------------------------------------
python app.py

pause
