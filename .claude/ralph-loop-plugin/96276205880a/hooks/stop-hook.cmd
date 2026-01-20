@echo off
setlocal EnableDelayedExpansion

REM Ralph Loop Stop Hook - Windows Wrapper
REM Uses Git Bash to execute stop-hook.sh (handles Windows paths natively)

REM Get the directory of this script
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Convert Windows path to Git Bash path format (/c/Users/... instead of C:\Users\...)
set "BASH_PATH=%SCRIPT_DIR:\=/%"
set "BASH_PATH=%BASH_PATH:C:=/c%"
set "BASH_PATH=%BASH_PATH:D:=/d%"
set "BASH_PATH=%BASH_PATH:E:=/e%"

REM Add user bin to PATH for jq
set "PATH=C:\Users\zdhpe\bin;%PATH%"

REM Execute the bash script using Git Bash (NOT WSL)
"C:\Program Files\Git\usr\bin\bash.exe" "%BASH_PATH%/stop-hook.sh"
exit /b %ERRORLEVEL%
