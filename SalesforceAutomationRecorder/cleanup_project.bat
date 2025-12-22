@echo off
echo ======================================================================
echo   Cleaning up unnecessary files from project
echo ======================================================================
echo.

REM Delete all the fix/guide markdown files (keep only README.md and MASTER_README.md)
echo Removing documentation files...
del /Q "ADVANCED_FEATURES.md" 2>nul
del /Q "AI_ENHANCEMENT_ARCHITECTURE.md" 2>nul
del /Q "AI_ENHANCEMENT_OPTIONS.md" 2>nul
del /Q "AI_IMPLEMENTATION_SUMMARY.md" 2>nul
del /Q "AI_INTEGRATION_DIAGRAM.md" 2>nul
del /Q "AI_OPTIONS.md" 2>nul
del /Q "AI_QUICK_START.md" 2>nul
del /Q "AI_README.md" 2>nul
del /Q "ALLURE_TEST_RUNNER_README.md" 2>nul
del /Q "ALL_FIXES_COMPLETE.md" 2>nul
del /Q "AMAZING_PROGRESS.md" 2>nul
del /Q "ARCHITECTURE.md" 2>nul
del /Q "ARCHITECTURE_VISUAL.md" 2>nul
del /Q "AUTOMATION_GUIDE.md" 2>nul
del /Q "AUTO_DEMO_GUIDE.md" 2>nul
del /Q "CHECKBOX_FIX.md" 2>nul
del /Q "CLEAR_FIELD_FIX.md" 2>nul
del /Q "COMPLETE_DEMO_PACKAGE.md" 2>nul
del /Q "DEMO_ENHANCEMENTS.md" 2>nul
del /Q "DEMO_GUIDE.md" 2>nul
del /Q "DEMO_PRESENTATION.md" 2>nul
del /Q "DEMO_QUICK_REFERENCE.md" 2>nul
del /Q "DEMO_QUICK_START.md" 2>nul
del /Q "DEMO_READY.md" 2>nul
del /Q "DEMO_SCRIPT.md" 2>nul
del /Q "DROPDOWN_FIX.md" 2>nul
del /Q "ELEMENT_NOT_FOUND_GUIDE.md" 2>nul
del /Q "ENHANCEMENT_COMPLETE.md" 2>nul
del /Q "FIELD_LABEL_FIX.md" 2>nul
del /Q "FINAL_FIX.md" 2>nul
del /Q "FINAL_SUMMARY.md" 2>nul
del /Q "FIX_APPLIED.md" 2>nul
del /Q "FIX_POWERSHELL_POLICY.md" 2>nul
del /Q "FORM_CLICK_FIX.md" 2>nul
del /Q "FORM_FIELD_FIX.md" 2>nul
del /Q "FUTURE_AI_INTEGRATION.md" 2>nul
del /Q "GEMINI_AI_NOW_WORKING.md" 2>nul
del /Q "GEMINI_AI_README.md" 2>nul
del /Q "GEMINI_AI_SETUP.md" 2>nul
del /Q "GEMINI_AI_SUMMARY.md" 2>nul
del /Q "GEMINI_METRICS_ADDED.md" 2>nul
del /Q "GEMINI_PARSER_FIX.md" 2>nul
del /Q "GEMINI_SETUP.md" 2>nul
del /Q "GEMINI_UI_BUTTON_ADDED.md" 2>nul
del /Q "GEMINI_VERIFICATION_GUIDE.md" 2>nul
del /Q "GPT4_SETUP.md" 2>nul
del /Q "IMPLEMENTATION_GUIDE.md" 2>nul
del /Q "INHERITANCE_FIX.md" 2>nul
del /Q "LEARNING_NOT_WORKING.md" 2>nul
del /Q "LOGIN_FIELD_FIX.md" 2>nul
del /Q "LOGIN_GUIDE.md" 2>nul
del /Q "OLLAMA_SETUP.md" 2>nul
del /Q "ORIGINAL_FORMAT_SUPPORT.md" 2>nul
del /Q "PERFORMANCE_METRICS_GUIDE.md" 2>nul
del /Q "PORT_MISMATCH_FIX.md" 2>nul
del /Q "PRESENTATION_OUTLINE.md" 2>nul
del /Q "PROJECT_SUMMARY.md" 2>nul
del /Q "QUICK_REFERENCE.md" 2>nul
del /Q "QUICK_START.md" 2>nul
del /Q "QUICK_START_ADVANCED.md" 2>nul
del /Q "QUICK_START_REAL_TEST.md" 2>nul
del /Q "REALTIME_LOGS_UPDATE.md" 2>nul
del /Q "REAL_TEST_GUIDE.md" 2>nul
del /Q "REQUIRED_FIELD_FIX.md" 2>nul
del /Q "RESTART_AND_TEST.md" 2>nul
del /Q "SMART_FORM_HANDLING.md" 2>nul
del /Q "START_SERVER_GUIDE.md" 2>nul
del /Q "STOP_ON_FAILURE_UPDATE.md" 2>nul
del /Q "TEST_STEP_FORMATS.md" 2>nul
del /Q "TEXT_FILE_GUIDE.md" 2>nul
del /Q "TROUBLESHOOTING.md" 2>nul
del /Q "UI_DEMO_COMPLETE.md" 2>nul
del /Q "UI_DEMO_GUIDE.md" 2>nul
del /Q "UI_DEMO_README.md" 2>nul
del /Q "UI_GUIDE.md" 2>nul
del /Q "USAGE_GUIDE.md" 2>nul
del /Q "VERIFY_COMMAND_GUIDE.md" 2>nul
del /Q "WHATS_NEW.md" 2>nul
del /Q "WHY_NO_GEMINI_DATA.md" 2>nul

REM Delete debug screenshots
echo Removing debug screenshots...
del /Q "debug_*.png" 2>nul
del /Q "test_failure*.png" 2>nul
del /Q "test_result*.png" 2>nul

REM Delete temporary test files
echo Removing temporary test files...
del /Q "test_parser.py" 2>nul
del /Q "quick_check.py" 2>nul
del /Q "test_compatibility.py" 2>nul
del /Q "test_gemini_demo.py" 2>nul
del /Q "test_gemini_now.py" 2>nul
del /Q "test_login_fix.py" 2>nul
del /Q "test_my_test.py" 2>nul
del /Q "test_recorder_simple.py" 2>nul
del /Q "test_specific_scenario.py" 2>nul
del /Q "test_template.py" 2>nul
del /Q "simple_test.py" 2>nul
del /Q "hsd_complete_workflow_test.py" 2>nul
del /Q "hsd_full_form_test.py" 2>nul

REM Delete backup files
echo Removing backup files...
del /Q "test_learning_backup*.json" 2>nul

REM Delete old/unused batch files
echo Removing old batch files...
del /Q "run_recording_20251022_095152.bat" 2>nul
del /Q "run_test.bat" 2>nul
del /Q "start_auto_demo.bat" 2>nul
del /Q "start_ui_demo.bat" 2>nul
del /Q "start_ui_with_gemini.bat" 2>nul
del /Q "quick_start_gemini.bat" 2>nul
del /Q "run_complete_test.bat" 2>nul

REM Delete unused Python files
echo Removing unused Python files...
del /Q "ai_automation_generator.py" 2>nul
del /Q "convert_recording_to_test.py" 2>nul
del /Q "convert_to_playwright.py" 2>nul
del /Q "fix_form_selectors.py" 2>nul
del /Q "generate_report.py" 2>nul
del /Q "mcp_server.py" 2>nul
del /Q "ollama_locator.py" 2>nul
del /Q "plain_english_to_test.py" 2>nul
del /Q "predictive_analyzer.py" 2>nul
del /Q "run_from_text.py" 2>nul
del /Q "run_from_text_enhanced.py" 2>nul
del /Q "run_playwright_test.py" 2>nul
del /Q "run_recording_direct.py" 2>nul
del /Q "run_test_with_allure.py" 2>nul
del /Q "run_tests_cli.py" 2>nul
del /Q "setup.py" 2>nul
del /Q "setup_ai_models.py" 2>nul
del /Q "setup_gemini_api.py" 2>nul
del /Q "setup_ui_demo.py" 2>nul
del /Q "test_builder_ui.py" 2>nul
del /Q "ui_demo_server.py" 2>nul
del /Q "ui_demo_server_auto.py" 2>nul
del /Q "ui_demo_server_simple.py" 2>nul
del /Q "video_analyzer.py" 2>nul
del /Q "view_current_learning.py" 2>nul
del /Q "view_gemini_learning.py" 2>nul

REM Delete unused data files
echo Removing unused data files...
del /Q "auto_heal_data.json" 2>nul
del /Q "gemini_learning_history.json" 2>nul
del /Q "predictive_data.json" 2>nul
del /Q "learning_feedback.db" 2>nul

REM Delete old PowerShell scripts
echo Removing old PowerShell scripts...
del /Q "restart_with_gemini.ps1" 2>nul
del /Q "start_server_with_gemini.ps1" 2>nul

REM Delete empty directories
echo Removing empty directories...
rmdir /Q "demo" 2>nul
rmdir /Q "recordings" 2>nul
rmdir /Q "TestResults" 2>nul

echo.
echo ======================================================================
echo   Cleanup complete!
echo ======================================================================
echo.
echo Kept essential files:
echo   - Core Python files (executors, AI integration)
echo   - UI files (dashboard, server)
echo   - Configuration files
echo   - README.md and MASTER_README.md
echo   - Active batch scripts
echo   - Test learning data
echo.
echo Removed:
echo   - 80+ documentation/fix guide files
echo   - Debug screenshots
echo   - Temporary test files
echo   - Backup files
echo   - Unused Python modules
echo   - Old batch scripts
echo.
pause
