@echo off
chcp 65001 >nul
cd /d "%~dp0..\01-源代码\backend"
if not exist .env copy /Y "%~dp0..\03-配置\demo.env" .env
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python seed_staff.py
python run.py
pause
