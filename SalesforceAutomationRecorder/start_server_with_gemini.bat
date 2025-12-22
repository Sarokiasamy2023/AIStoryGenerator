@echo off
echo ========================================
echo   Starting UI Server with Gemini AI
echo ========================================
echo.

REM Set API key for this session
set GEMINI_API_KEY=AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ

REM Check if port 8888 is in use
echo Checking if port 8888 is available...
netstat -ano | findstr :8888 >nul
if %errorlevel% equ 0 (
    echo.
    echo ⚠️ Port 8888 is already in use!
    echo.
    echo Options:
    echo 1. Stop the existing server (press Ctrl+C in that terminal)
    echo 2. Or kill the process:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8888') do (
        echo    taskkill /F /PID %%a
    )
    echo.
    pause
    exit /b 1
)

echo ✅ Port 8888 is available
echo ✅ Gemini API Key is set
echo.
echo Starting server...
echo.

python ui_real_test_server.py

pause
