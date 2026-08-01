@echo off
rem Launcher for trace server window (called from run.bat)
cd /d "%~dp0\.."
call "%~dp0run-server.bat"
if errorlevel 1 pause
