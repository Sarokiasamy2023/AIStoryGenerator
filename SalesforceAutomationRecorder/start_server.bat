@echo off
REM Simple Server Startup with Gemini AI
echo ======================================================================
echo   Starting Server with Gemini AI
echo ======================================================================
echo.

REM Set API Key
set GEMINI_API_KEY=AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ
echo API Key: SET
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Check server file
if not exist "ui_real_test_server.py" (
    echo ERROR: ui_real_test_server.py not found!
    echo Current directory: "%CD%"
    pause
    exit /b 1
)

echo Starting server on http://localhost:8889
echo Press Ctrl+C to stop
echo.

REM Start server
python ui_real_test_server.py

pause
