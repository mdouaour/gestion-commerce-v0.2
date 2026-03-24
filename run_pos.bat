@echo off
set PYTHONPATH=%cd%\desktop
python desktop\src\init_db.py
python desktop\src\seed_data.py
python desktop\src\main.py
pause
