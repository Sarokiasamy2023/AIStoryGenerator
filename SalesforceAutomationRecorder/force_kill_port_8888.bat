@echo off
echo ======================================================================
echo   Force Killing ALL processes on port 8888
echo ======================================================================
echo.

REM Get all PIDs using port 8888 and kill them
echo Searching for processes on port 8888...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8888 ^| findstr LISTENING') do (
    echo   Found PID: %%a - Killing...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   [FAILED] Could not kill PID %%a
    ) else (
        echo   [SUCCESS] Killed PID %%a
    )
)

REM Wait a moment
timeout /t 2 /nobreak >nul

echo.
echo Verifying port 8888 is free...
netstat -ano | findstr :8888 >nul 2>&1
if errorlevel 1 (
    echo   [SUCCESS] Port 8888 is now free!
) else (
    echo   [WARNING] Port 8888 may still be in use
    echo   Current connections:
    netstat -ano | findstr :8888
)

echo.
echo ======================================================================
echo   Done
echo ======================================================================
pause
