@echo off
chcp 65001 >nul
cd /d "%~dp0..\01-源代码\bank"
if not exist .env copy /Y "%~dp0..\03-配置\bank.env" .env
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python app.py
pause
