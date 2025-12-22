@echo off
echo ============================================================
echo Starting Integrated Test Automation System
echo ============================================================
echo.
echo This will start:
echo 1. AITestGenerator (Node.js) on port 3000
echo 2. SalesforceAutomationRecorder (Python) on port 8888
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Starting AITestGenerator service...
cd /d "C:\Test Automation\Integration\AI Story Generator Integrated\AITestGenerator"

REM Check if node_modules exists
if not exist "node_modules" (
    echo [INFO] Installing Node.js dependencies...
    call npm install
)

REM Start AITestGenerator in background
start "AITestGenerator" cmd /k "node server.js"
timeout /t 3 /nobreak >nul

echo [2/4] AITestGenerator started on http://localhost:3000
echo.

echo [3/4] Starting SalesforceAutomationRecorder service...
cd /d "C:\Test Automation\Integration\AI Story Generator Integrated\SalesforceAutomationRecorder"

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and start server
start "SalesforceAutomationRecorder" cmd /k "venv\Scripts\activate && python ui_real_test_server.py"
timeout /t 3 /nobreak >nul

echo [4/4] SalesforceAutomationRecorder started on http://localhost:8888
echo.
echo ============================================================
echo Both services are now running!
echo ============================================================
echo.
echo Dashboard: http://localhost:8888
echo AITestGenerator: http://localhost:3000
echo.
echo Press any key to open the dashboard in your browser...
pause >nul
start http://localhost:8888
echo.
echo To stop the services, close both command windows.
echo.
