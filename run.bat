@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Start AgentSmith-Trace-Server and open the admin home page.

cd /d "%~dp0"

echo Cleaning up previous run (server window and browser)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-session.ps1" -Action Cleanup -ProjectRoot "%~dp0."

if exist ".env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" set "%%a=%%b"
    )
)

if not defined AGENTSMITH_TRACE_HOST set "AGENTSMITH_TRACE_HOST=127.0.0.1"
if not defined AGENTSMITH_TRACE_PORT set "AGENTSMITH_TRACE_PORT=9000"
if not defined AGENTSMITH_TRACE_RELOAD set "AGENTSMITH_TRACE_RELOAD=1"

set "PREFERRED_PORT=%AGENTSMITH_TRACE_PORT%"

where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv not found. Install from https://docs.astral.sh/uv/
    pause
    exit /b 1
)

echo.
echo ========================================
echo   AgentSmith-Trace-Server
echo ========================================
echo.

echo Syncing dependencies...
uv sync >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv sync failed
    pause
    exit /b 1
)

echo Freeing port %PREFERRED_PORT% ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kill-port.ps1" -Port %PREFERRED_PORT%
set "KILL_RC=%ERRORLEVEL%"
if "%KILL_RC%"=="2" (
    set "AGENTSMITH_TRACE_PORT=9001"
    echo.
    echo Port %PREFERRED_PORT% is stuck with a zombie listener.
    echo Switching to port !AGENTSMITH_TRACE_PORT! for this session.
    echo.
)

set "BASE_URL=http://%AGENTSMITH_TRACE_HOST%:!AGENTSMITH_TRACE_PORT!"
set "HOME_URL=!BASE_URL!/"
set "REPORT_URL=!BASE_URL!/report"
set "DOCS_URL=!BASE_URL!/docs"
set "SIMULATOR_URL=!BASE_URL!/simulator"

echo Starting server at !BASE_URL! ...
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-session.ps1" -Action StartServer -ProjectRoot "%~dp0." -Port !AGENTSMITH_TRACE_PORT! -Reload !AGENTSMITH_TRACE_RELOAD!') do set "SERVER_PID=%%i"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-session.ps1" -Action WriteSession -ProjectRoot "%~dp0." -ServerPid !SERVER_PID! -BrowserPid 0 -Port !AGENTSMITH_TRACE_PORT! -HomeUrl "!HOME_URL!"

echo Waiting for admin home page...
set RETRIES=0
:WAIT_HOME
powershell -NoProfile -Command "try { $h=(Invoke-WebRequest -Uri '!REPORT_URL!' -UseBasicParsing -TimeoutSec 3).Content; if ($h -match 'split-page' -and $h -match '#0f1419') { exit 0 }; exit 2 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto OPEN_BROWSER
set /a RETRIES+=1
if %RETRIES% GEQ 45 (
    echo WARNING: admin home page timeout, opening browser anyway...
    goto OPEN_BROWSER
)
timeout /t 1 /nobreak >nul
goto WAIT_HOME

:OPEN_BROWSER
echo Opening admin home: !HOME_URL!
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\open-browser.ps1" -UpdateSession "!HOME_URL!"

echo.
echo Started:
echo   Admin home    !HOME_URL!
echo   Admin report  !REPORT_URL!
echo   Simulator     !SIMULATOR_URL!
echo   Swagger UI    !DOCS_URL!
echo.
echo Theme matches SEAI ai-end /admin ^(dark^). Use Ctrl+F5 if Chrome shows a cached light page.
echo Re-run run.bat to stop the previous server and browser, then start fresh.
echo Close the server window manually to stop without restarting.
echo.
pause
