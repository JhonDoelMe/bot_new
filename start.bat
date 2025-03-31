@echo off
call venv\Scripts\activate
python bot.py
if %errorlevel% == 0 exit
pause