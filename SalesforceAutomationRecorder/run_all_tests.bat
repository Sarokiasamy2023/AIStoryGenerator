@echo off
REM Batch script to run all tests automatically

echo ========================================
echo   Automated Test Execution
echo ========================================
echo.

REM Set environment variables (optional)
REM set SALESFORCE_USERNAME=your_username
REM set SALESFORCE_PASSWORD=your_password

REM Run tests in headless mode with video recording
python run_tests_cli.py tests\*.json --headless --batch

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   All tests PASSED!
    echo ========================================
    exit /b 0
) else (
    echo.
    echo ========================================
    echo   Some tests FAILED!
    echo ========================================
    exit /b 1
)
