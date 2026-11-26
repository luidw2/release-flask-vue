@echo off
chcp 65001 >nul
start "bank" cmd /c "%~dp0start-bank.bat"
start "backend" cmd /c "%~dp0start-backend.bat"
start "frontend" cmd /c "%~dp0start-frontend.bat"
