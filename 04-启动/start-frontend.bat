@echo off
chcp 65001 >nul
cd /d "%~dp0..\01-源代码\frontend"
if not exist node_modules call npm ci
call npm run dev
pause
