@echo off
chcp 65001 >nul
cd /d "%~dp0.."
powershell -ExecutionPolicy Bypass -File "%~dp0install_local_cuda.ps1"
pause
