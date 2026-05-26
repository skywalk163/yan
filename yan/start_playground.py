#!/usr/bin/env python3
"""
言语言 Playground 一键启动脚本
适用于 Windows、Linux、macOS

功能：
1. 检查 Python 是否安装
2. 检查端口是否被占用，自动选择可用端口
3. 启动 Playground 服务器
4. 自动打开浏览器
"""

import os
import sys
import subprocess
import time
import socket
import webbrowser
import platform
from pathlib import Path


def check_python():
    """检查 Python 是否安装"""
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ Python 版本: {result.stdout.strip()}")
            return True
        else:
            return False
    except Exception as e:
        print(f"✗ 无法检测 Python: {e}")
        return False


def find_available_port(start_port=5000, max_attempts=50):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    return None


def start_server(port):
    """启动 Playground 服务器"""
    print(f"\n🚀 启动 Playground 服务器...")
    print(f"📡 端口: {port}")
    
    # 获取当前脚本所在目录的父目录（yan 目录）
    script_dir = Path(__file__).resolve().parent
    server_path = script_dir / "playground" / "server.py"
    
    if not server_path.exists():
        print(f"✗ 找不到服务器文件: {server_path}")
        return None
    
    # 启动服务器进程
    env = os.environ.copy()
    env['PYTHONPATH'] = str(script_dir)
    
    process = subprocess.Popen(
        [sys.executable, str(server_path), '--port', str(port), '--host', '127.0.0.1'],
        cwd=script_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    return process


def wait_for_server(port, timeout=10):
    """等待服务器启动"""
    print(f"⏳ 等待服务器启动...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print("✅ 服务器启动成功！")
                return True
        except Exception:
            pass
        
        time.sleep(0.5)
    
    print("✗ 服务器启动超时")
    return False


def open_browser(port):
    """打开浏览器"""
    url = f"http://localhost:{port}"
    print(f"🌐 打开浏览器: {url}")
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"⚠ 无法自动打开浏览器，请手动访问: {url}")
        return False


def main():
    """主函数"""
    # 禁用输出缓冲
    sys.stdout = sys.__stdout__
    
    print("=" * 60, flush=True)
    print("          言语言 Playground 一键启动", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)
    
    # 检查 Python
    if not check_python():
        print("\n❌ 错误：请先安装 Python 3.8+", flush=True)
        print("下载地址: https://www.python.org/downloads/", flush=True)
        input("按 Enter 键退出...")
        sys.exit(1)
    
    # 查找可用端口
    port = find_available_port()
    if port is None:
        print("\n❌ 错误：无法找到可用端口", flush=True)
        input("按 Enter 键退出...")
        sys.exit(1)
    
    # 启动服务器
    process = start_server(port)
    if process is None:
        input("按 Enter 键退出...")
        sys.exit(1)
    
    # 等待服务器启动
    if not wait_for_server(port):
        # 打印服务器输出帮助调试
        print("\n--- 服务器输出 ---", flush=True)
        try:
            process.wait(timeout=2)
            print(process.stdout.read(), flush=True)
        except subprocess.TimeoutExpired:
            print("服务器仍在运行，但端口未响应", flush=True)
        input("按 Enter 键退出...")
        sys.exit(1)
    
    # 打开浏览器
    open_browser(port)
    
    print("\n" + "=" * 60, flush=True)
    print("🎉 Playground 已启动！", flush=True)
    print(f"📍 地址: http://localhost:{port}", flush=True)
    print(f"📚 教程: http://localhost:{port}/tutorial", flush=True)
    print("=" * 60, flush=True)
    print("\n按 Ctrl+C 停止服务器", flush=True)
    
    # 等待用户停止服务器
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n👋 正在关闭服务器...", flush=True)
        process.terminate()
        process.wait()
        print("✅ 服务器已停止", flush=True)


if __name__ == "__main__":
    main()