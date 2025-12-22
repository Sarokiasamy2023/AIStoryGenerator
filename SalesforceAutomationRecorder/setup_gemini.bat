@echo off
echo ========================================
echo   Gemini AI Setup for Test Automation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/4] Installing required packages...
pip install google-generativeai playwright asyncio python-dateutil
echo.

echo [2/4] Installing Playwright browsers...
playwright install chromium
echo.

echo [3/4] Setting up Gemini API Key...
echo.
echo Please enter your Gemini API Key:
echo (Get it from: https://makersuite.google.com/app/apikey)
echo.
set /p GEMINI_KEY="API Key: "

if "%GEMINI_KEY%"=="" (
    echo.
    echo WARNING: No API key entered. You can set it later with:
    echo set GEMINI_API_KEY=your-key-here
    echo.
) else (
    setx GEMINI_API_KEY "%GEMINI_KEY%"
    echo.
    echo API Key saved to environment variables!
    echo.
)

echo [4/4] Verifying installation...
python -c "import google.generativeai; print('✓ google-generativeai installed')"
python -c "from playwright.async_api import async_playwright; print('✓ playwright installed')"
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your terminal/IDE to load environment variables
echo 2. Run: python test_gemini_ai.py
echo.
echo Documentation: GEMINI_AI_SETUP.md
echo.
pause
