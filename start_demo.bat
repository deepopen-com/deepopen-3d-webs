@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 光域造景 · 本机演示模式
python scripts\start_local.py --demo %*
if errorlevel 1 pause
pause
