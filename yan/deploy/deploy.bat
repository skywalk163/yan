@echo off
REM 言语言 Playground 部署脚本 (Windows)

echo === 言语言 Playground 部署脚本 ===

cd /d "%~dp0\.."

echo 1. 构建 Playground...
python deploy\deploy_playground.py build

echo === 部署准备完成 ===
pause
