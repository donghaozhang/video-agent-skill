@echo off
REM ViMax CLI Wrapper
REM Usage: vimax.bat <command> [options]

set PYTHONPATH=%~dp0packages\core
python -c "from ai_content_platform.vimax.cli.commands import vimax; vimax()" %*
