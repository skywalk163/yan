@echo off
chcp 65001 >nul
echo.
echo ============================================
echo          言语言 Playground 一键启动
echo ============================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 启动 Python 脚本
python start_playground.py

pause