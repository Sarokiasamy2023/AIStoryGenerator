@echo off
echo ======================================================================
echo   Salesforce Automation Recorder - Full Setup and Start
echo ======================================================================
echo.

REM Step 1: Install Dependencies
echo [1/3] Installing Python dependencies...
echo ======================================================================
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)
echo   Python dependencies installed successfully
echo.

echo [2/3] Installing Playwright Chromium...
echo ======================================================================
playwright install chromium
if errorlevel 1 (
    echo ERROR: Failed to install Playwright Chromium!
    pause
    exit /b 1
)
echo   Playwright Chromium installed successfully
echo.

REM Step 2: Kill existing sessions
echo [3/3] Killing any existing server sessions on port 8888...
echo ======================================================================
powershell -Command "$pids = (Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue).OwningProcess | Select-Object -Unique; if ($pids) { $pids | ForEach-Object { Write-Host '  Killing PID:' $_; Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } } else { Write-Host '  No process found on port 8888' }"
timeout /t 3 /nobreak >nul
echo   Existing sessions terminated
echo.

REM Step 3: Set API Key (optional)
echo Setting Gemini API Key...
set GEMINI_API_KEY=AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ
echo   API Key: SET
echo.

REM Step 4: Start new server session
echo ======================================================================
echo   Starting New Server Session on Port 8888
echo ======================================================================
echo.
echo Server will be available at: http://localhost:8888
echo Press Ctrl+C to stop the server
echo.

python ui_real_test_server.py

pause
