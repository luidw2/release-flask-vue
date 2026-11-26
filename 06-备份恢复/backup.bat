@echo off
chcp 65001 >nul
set /p DBNAME=数据库名(默认 test_release):
if "%DBNAME%"=="" set DBNAME=test_release
mysqldump -u root -p --single-transaction %DBNAME% > backup_%date:~0,4%%date:~5,2%%date:~8,2%.sql
echo 备份完成
pause
