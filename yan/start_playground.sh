#!/bin/bash
# 言语言 Playground 一键启动脚本（Linux/Mac）

echo ""
echo "================================================"
echo "          言语言 Playground 一键启动"
echo "================================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 错误：未找到 Python，请先安装 Python 3.8+"
        echo "下载地址: https://www.python.org/downloads/"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# 启动 Python 脚本
$PYTHON_CMD start_playground.py