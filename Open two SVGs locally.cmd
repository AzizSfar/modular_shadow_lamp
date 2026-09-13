@echo off
python "%~dp0run_local.py" --choose-svg --choose-cover
if errorlevel 1 pause
