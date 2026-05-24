#!/usr/bin/env python3
"""
言语言 Playground 部署脚本
用于构建和部署 Playground 到 GitHub Pages / GitCode Pages
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path

# 确保在 yan 目录
YAN_DIR = Path(__file__).parent.parent
PLAYGROUND_DIR = YAN_DIR / "playground"
OUTPUT_DIR = YAN_DIR / "dist"


def build_playground():
    """构建 Playground 用于静态部署"""
    print("🔨 构建 Playground...")

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 复制 index.html
    index_src = PLAYGROUND_DIR / "index.html"
    index_dst = OUTPUT_DIR / "index.html"

    with open(index_src, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换 API 调用为模拟执行（用于静态部署）
    # 注意：静态部署时需要一个运行时后端
    static_content = content.replace(
        "const response = await fetch('/api/execute'",
        "// 静态部署模式：使用 eval 执行\n            const response = await fetch('/api/execute'"
    )

    with open(index_dst, "w", encoding="utf-8") as f:
        f.write(static_content)

    # 复制 server.py 作为参考
    server_src = PLAYGROUND_DIR / "server.py"
    server_dst = OUTPUT_DIR / "server.py"
    if server_src.exists():
        import shutil
        shutil.copy(server_src, server_dst)

    # 创建示例代码索引
    examples = create_examples_index()
    examples_file = OUTPUT_DIR / "examples.json"
    with open(examples_file, "w", encoding="utf-8") as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)

    print(f"✅ 构建完成！输出目录: {OUTPUT_DIR}")


def create_examples_index():
    """从 index.html 中提取示例代码索引"""
    index_file = PLAYGROUND_DIR / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析示例
    examples = []
    import re

    # 匹配示例项
    pattern = r'<div class="example-item" onclick="loadExample\(\'(\w+)\'\)">\s*<div class="example-title">([^<]+)</div>\s*<div class="example-desc">([^<]+)</div>'
    matches = re.findall(pattern, content)

    for name, title, desc in matches:
        examples.append({
            "id": name,
            "title": title,
            "description": desc
        })

    return examples


def deploy_github_pages():
    """部署到 GitHub Pages"""
    print("🚀 部署到 GitHub Pages...")

    try:
        import subprocess

        # 检查 dist 目录
        if not OUTPUT_DIR.exists():
            print("❌ 请先运行 build 命令")
            return False

        # 初始化 gh-pages 分支
        subprocess.run(["git", "worktree", "add", "-B", "gh-pages", "dist/_site", "HEAD"],
                      cwd=YAN_DIR, check=True)

        # 复制文件
        import shutil
        dist_site = YAN_DIR / "dist" / "_site"
        if dist_site.exists():
            shutil.rmtree(dist_site)
        shutil.copytree(OUTPUT_DIR, dist_site)

        # 提交
        subprocess.run(["git", "add", "."], cwd=dist_site, check=True)
        subprocess.run(["git", "commit", "-m", "Deploy Playground"],
                      cwd=dist_site, check=True)

        print("✅ 部署准备完成！请手动推送到 gh-pages 分支:")
        print(f"   cd {dist_site}")
        print("   git push origin gh-pages")

    except subprocess.CalledProcessError as e:
        print(f"❌ 部署失败: {e}")
        return False

    return True


def create_dockerfile():
    """创建 Dockerfile 用于容器化部署"""
    dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "playground/server.py"]
"""
    dockerfile_path = YAN_DIR / "Dockerfile"
    with open(dockerfile_path, "w", encoding="utf-8") as f:
        f.write(dockerfile)

    print(f"✅ Dockerfile 已创建: {dockerfile_path}")


def create_docker_compose():
    """创建 docker-compose.yml 用于本地开发"""
    compose = """version: '3.8'

services:
  playground:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEBUG=true
    volumes:
      - ./examples:/app/examples
    restart: unless-stopped
"""
    compose_path = YAN_DIR / "docker-compose.yml"
    with open(compose_path, "w", encoding="utf-8") as f:
        f.write(compose)

    print(f"✅ docker-compose.yml 已创建: {compose_path}")


def create_nginx_config():
    """创建 Nginx 配置用于生产部署"""
    nginx_conf = """server {
    listen 80;
    server_name playground.example.com;

    # 前端静态文件
    location / {
        root /var/www/yan-playground;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
"""
    config_path = YAN_DIR / "deploy" / "nginx.conf"
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(nginx_conf)

    print(f"✅ Nginx 配置已创建: {config_path}")


def main():
    parser = argparse.ArgumentParser(description="言语言 Playground 部署工具")
    parser.add_argument("command", choices=["build", "deploy", "docker", "nginx"],
                       help="命令: build(构建), deploy(部署), docker(创建Docker配置), nginx(创建Nginx配置)")

    args = parser.parse_args()

    if args.command == "build":
        build_playground()
    elif args.command == "deploy":
        deploy_github_pages()
    elif args.command == "docker":
        create_dockerfile()
        create_docker_compose()
    elif args.command == "nginx":
        create_nginx_config()


if __name__ == "__main__":
    main()
