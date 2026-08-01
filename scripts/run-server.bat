@echo off
setlocal EnableExtensions

cd /d "%~dp0\.."

rem Preserve session overrides from run.bat before optional .env reload
set "SESSION_TRACE_HOST=%AGENTSMITH_TRACE_HOST%"
set "SESSION_TRACE_PORT=%AGENTSMITH_TRACE_PORT%"
set "SESSION_TRACE_RELOAD=%AGENTSMITH_TRACE_RELOAD%"

if exist ".env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" set "%%a=%%b"
    )
)

if defined SESSION_TRACE_HOST set "AGENTSMITH_TRACE_HOST=%SESSION_TRACE_HOST%"
if defined SESSION_TRACE_PORT set "AGENTSMITH_TRACE_PORT=%SESSION_TRACE_PORT%"
if defined SESSION_TRACE_RELOAD set "AGENTSMITH_TRACE_RELOAD=%SESSION_TRACE_RELOAD%"

if not defined AGENTSMITH_TRACE_HOST set "AGENTSMITH_TRACE_HOST=127.0.0.1"
if not defined AGENTSMITH_TRACE_PORT set "AGENTSMITH_TRACE_PORT=9000"
if not defined AGENTSMITH_PROJECT_ROOT set "AGENTSMITH_PROJECT_ROOT=%~dp0\.."

set "BASE_URL=http://%AGENTSMITH_TRACE_HOST%:%AGENTSMITH_TRACE_PORT%"

echo Backend:  %BASE_URL%
echo Swagger:  %BASE_URL%/docs
echo Report:   %BASE_URL%/report
echo.

uv sync >nul 2>&1
uv pip install -e . -q 2>nul
uv run agentsmith-trace-server
