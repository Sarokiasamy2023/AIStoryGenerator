@echo off
echo ========================================
echo  GPT-4 Smart Locators Setup
echo ========================================
echo.

echo Installing OpenAI SDK...
pip install openai

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Get your OpenAI API key from: https://platform.openai.com/api-keys
echo 2. Set environment variable:
echo    $env:OPENAI_API_KEY = "sk-your-key-here"
echo 3. Run: python test_builder_ui.py
echo.
echo See GPT4_SETUP.md for detailed instructions
echo.
pause
