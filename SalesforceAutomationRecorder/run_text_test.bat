@echo off
echo ========================================
echo   Running Test from Text File
echo ========================================
echo.

REM Run the test from text file
python run_from_text.py my_test.txt

REM Open report
if exist test_report.html (
    echo.
    echo Opening test report...
    start test_report.html
)

REM Open latest video
for /f "delims=" %%f in ('dir /b /od test_videos\*.html 2^>nul') do set "latest=%%f"
if defined latest (
    echo Opening video player...
    start test_videos\%latest%
)

echo.
echo ========================================
echo   Complete!
echo ========================================
pause
