@echo off
echo ========================================
echo   Setting Gemini API Key
echo ========================================
echo.

REM Set the API key as environment variable (current session)
set GEMINI_API_KEY=AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ

REM Set the API key permanently for the user
setx GEMINI_API_KEY "AIzaSyCPRLzHy2fmpjWX_n7odENX3K5U3hbUUnQ"

echo.
echo ✅ API Key has been set!
echo.
echo Current session: READY
echo Permanent setting: SAVED (restart terminal to use in new sessions)
echo.
echo Next steps:
echo 1. Run: python test_gemini_ai.py
echo 2. Or integrate into your existing tests
echo.
pause
