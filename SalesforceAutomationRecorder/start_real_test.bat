@echo off
echo ============================================================
echo   Real Test Execution with Learning and Playback
echo ============================================================
echo.
echo Features:
echo  - Write tests in plain text
echo  - Watch real browser execution
echo  - Automatic selector learning
echo  - Selector reuse on 2nd run
echo  - Live execution view
echo.
echo Dashboard: http://localhost:8888
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

python ui_real_test_server.py

pause
