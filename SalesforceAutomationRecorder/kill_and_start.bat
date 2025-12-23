@echo off
echo ======================================================================
echo   Killing processes and starting Test Automation System
echo ======================================================================
echo.

REM Kill any process on port 8888
echo Stopping any process on port 8888...
powershell -Command "$pids = (Get-NetTCPConnection -LocalPort 8888 -ErrorAction SilentlyContinue).OwningProcess | Select-Object -Unique; if ($pids) { $pids | ForEach-Object { Write-Host '  Killing PID:' $_; Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } } else { Write-Host '  No process found on port 8888' }"

REM Wait a moment
timeout /t 3 /nobreak >nul
echo   Done
echo.

REM Set API Keys
echo Setting API Keys...
set GEMINI_API_KEY=AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ
set OPENAI_API_KEY=
set OPENAI_MODEL=gpt-4o-mini
set MAX_TOKENS=2000
set TEMPERATURE=0.7
echo   API Keys: SET
echo.

echo ======================================================================
echo   Starting Test Automation Server on Port 8888
echo ======================================================================
echo.
echo Features:
echo   - Test Execution Engine
echo   - AI-Powered Gherkin Conversion (OpenAI)
echo   - Gemini AI Selector Generation
echo   - Parallel Test Execution
echo   - Allure Reporting
echo.

REM Start server
python ui_real_test_server.py

pause
