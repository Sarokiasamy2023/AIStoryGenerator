@echo off
echo ========================================
echo   Setup Salesforce Credentials
echo ========================================
echo.

REM Prompt for credentials
set /p USERNAME="Enter Salesforce Username: "
set /p PASSWORD="Enter Salesforce Password: "

REM Set environment variables for current session
set SALESFORCE_USERNAME=%USERNAME%
set SALESFORCE_PASSWORD=%PASSWORD%
set SALESFORCE_URL=https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/

echo.
echo ========================================
echo   Credentials Set!
echo ========================================
echo.
echo Username: %USERNAME%
echo URL: %SALESFORCE_URL%
echo.
echo These credentials are set for this session only.
echo To make them permanent, run as Administrator.
echo.
echo ========================================
echo   Ready to Run Tests!
echo ========================================
echo.
echo Run your test with:
echo   python run_from_text.py my_test.txt
echo.
pause
