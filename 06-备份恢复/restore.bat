@echo off
chcp 65001 >nul
set /p FILE=备份文件路径:
set /p DBNAME=数据库名(默认 test):
if "%DBNAME%"=="" set DBNAME=test
mysql -u root -p %DBNAME% < %FILE%
echo 恢复完成
pause
