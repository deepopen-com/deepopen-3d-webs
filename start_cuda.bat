@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 光域造景 · 本机启动（自动 CUDA / 演示）
python scripts\start_local.py %*
if errorlevel 1 pause
pause
