@echo off
REM Restart Server with Gemini AI
echo ======================================================================
echo   RESTARTING SERVER WITH GEMINI AI
echo ======================================================================
echo.

REM Step 1: Stop existing server
echo Step 1: Stopping existing server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8888 2^>nul') do (
    echo   Stopping process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo   Done
echo.

REM Step 2: Set API Key
echo Step 2: Setting Gemini API Key...
set GEMINI_API_KEY=AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ
echo   API Key set: %GEMINI_API_KEY:~0,20%...
echo.

REM Step 3: Verify Python
echo Step 3: Verifying Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found!
    echo   Please install Python or add it to PATH
    pause
    exit /b 1
)
echo   Python is available
echo.

REM Step 4: Check if server file exists
if not exist "ui_real_test_server.py" (
    echo   ERROR: ui_real_test_server.py not found!
    echo   Make sure you're in the correct directory
    pause
    exit /b 1
)

echo ======================================================================
echo   STARTING SERVER
echo ======================================================================
echo.
echo API Key: SET
echo Server: ui_real_test_server.py
echo Port: 8888
echo.
echo Starting in 2 seconds...
timeout /t 2 /nobreak >nul
echo.

REM Step 5: Start server
python ui_real_test_server.py

echo.
echo Server stopped.
pause
