@echo off
echo ========================================
echo   Running HSD Complete Test
echo ========================================
echo.

REM Run the test
python run_tests_cli.py tests/hsd_complete_test.json --headless --batch

REM Generate report
echo.
echo ========================================
echo   Generating Test Report
echo ========================================
echo.
python generate_report.py

REM Open report
echo.
echo Opening test report...
start test_report.html

REM Open video
echo Opening video player...
for %%f in (test_videos\*.html) do (
    start %%f
    goto :done
)
:done

echo.
echo ========================================
echo   Test Complete!
echo ========================================
pause
