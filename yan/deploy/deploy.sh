#!/bin/bash
# 部署脚本：构建并部署 Playground

set -e

echo "=== 言语言 Playground 部署脚本 ==="

# 进入项目目录
cd "$(dirname "$0")/.."

# 构建
echo "1. 构建 Playground..."
python deploy/deploy_playground.py build

# 创建 Docker 配置（如果需要）
if [ "$1" = "--docker" ]; then
    echo "2. 创建 Docker 配置..."
    python deploy/deploy_playground.py docker
fi

# 创建 Nginx 配置（如果需要）
if [ "$1" = "--nginx" ]; then
    echo "3. 创建 Nginx 配置..."
    python deploy/deploy_playground.py nginx
fi

echo "=== 部署准备完成 ==="
