@echo off
set PYTHONPATH=%PYTHONPATH%;%cd%\desktop
python desktop\src\init_db.py
python desktop\src\main.py
pause
