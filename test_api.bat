@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo.
echo ========================================
echo   AgentSmith-Trace API Test Runner
echo ========================================
echo.

uv sync >nul 2>&1
if errorlevel 1 (
    echo Failed to sync dependencies with uv.
    pause
    exit /b 1
)

uv run python scripts\run_api_tests.py
set "EXIT_CODE=%ERRORLEVEL%"

if not exist "test-results\api-test-report.html" goto :after_open
set "REPORT_PATH=%CD%\test-results\api-test-report.html"
echo.
echo Opening HTML report...
call scripts\open-browser.bat "%REPORT_PATH%"
goto :after_open

:after_open
if not exist "test-results\api-test-report.html" (
    echo.
    echo HTML report was not generated.
)

echo.
if "%EXIT_CODE%"=="0" (
    echo All tests passed.
) else (
    echo Some tests failed. See the HTML report for details.
)
echo.
pause
exit /b %EXIT_CODE%
