@echo off
setlocal
set "RUFF=%~dp0..\.venv\Scripts\ruff.exe"
set "FILE=%~1"
if not exist "%RUFF%" exit /b 1
"%RUFF%" format "%FILE%"
"%RUFF%" check --fix "%FILE%"
exit /b 0
