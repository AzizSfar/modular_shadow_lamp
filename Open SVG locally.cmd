@echo off
python "%~dp0run_local.py" --choose-svg
if errorlevel 1 pause
