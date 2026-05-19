#!/usr/bin/env python3
"""
言语言 Playground 后端服务

优化版本：
- 使用进程池避免内存泄漏
- 限制执行时间
- 更安全的代码执行
"""

import sys
import os
import json
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import multiprocessing
import time
from pathlib import Path


# 获取正确的路径
BASE_DIR = Path(__file__).parent.parent
MAIN_PY = BASE_DIR / "main.py"


def execute_code_in_process(code: str) -> dict:
    """在独立进程中执行代码，避免内存泄漏"""
    try:
        result = subprocess.run(
            [sys.executable, str(MAIN_PY), "-c"],
            input=code.encode('utf-8'),
            capture_output=True,
            text=True,
            timeout=30,  # 30秒超时
            encoding='utf-8',
        )
        
        output = result.stdout.strip().split('\n') if result.stdout.strip() else []
        error = result.stderr.strip() if result.stderr.strip() else None
        
        if result.returncode != 0:
            output = [f"[ERROR] {line}" for line in output] if output else []
        
        return {
            "success": result.returncode == 0,
            "output": output,
            "error": error,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": [],
            "error": "执行超时（超过30秒）",
        }
    except Exception as e:
        return {
            "success": False,
            "output": [],
            "error": f"执行错误: {str(e)}",
        }


class YanExecutor:
    """言语言代码执行器（使用进程池）"""
    
    def __init__(self):
        # 不预创建进程池，每次使用独立进程
        pass
    
    def execute(self, code: str) -> tuple:
        """执行言语言代码，返回(success, output, error)"""
        result = execute_code_in_process(code)
        return result["success"], result["output"], result["error"]


class PlaygroundHandler(SimpleHTTPRequestHandler):
    """Playground HTTP 处理器"""
    
    executor = YanExecutor()
    protocol_version = 'HTTP/1.1'
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/' or path == '/index.html':
            self.serve_file('/index.html')
        elif path.startswith('/api/examples'):
            self.send_examples()
        else:
            super().do_GET()
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/execute':
            self.handle_execute()
        elif parsed.path == '/api/format':
            self.handle_format()
        elif parsed.path == '/api/lint':
            self.handle_lint()
        else:
            self.send_error(404, 'Not Found')
    
    def serve_file(self, path):
        """服务静态文件"""
        if path == '/':
            path = '/index.html'
        
        file_path = os.path.join(os.path.dirname(__file__), path.lstrip('/'))
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            
            if path.endswith('.html'):
                self.send_header('Content-Type', 'text/html; charset=utf-8')
            elif path.endswith('.css'):
                self.send_header('Content-Type', 'text/css; charset=utf-8')
            elif path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            else:
                self.send_header('Content-Type', 'application/octet-stream')
            
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, 'File Not Found')
    
    def handle_execute(self):
        """处理代码执行请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            code = data.get('code', '')
        except json.JSONDecodeError:
            self.send_json({'success': False, 'error': 'Invalid JSON', 'output': []})
            return
        
        if not code.strip():
            self.send_json({'success': False, 'error': 'Empty code', 'output': []})
            return
        
        success, output, error = self.executor.execute(code)
        
        self.send_json({
            'success': success,
            'output': output,
            'error': error,
        })
    
    def handle_format(self):
        """处理代码格式化请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            code = data.get('code', '')
        except json.JSONDecodeError:
            self.send_json({'success': False, 'error': 'Invalid JSON', 'formatted': ''})
            return
        
        try:
            from yan_fmt import YanFormatter
            formatter = YanFormatter()
            formatted = formatter.format(code)
            self.send_json({'success': True, 'formatted': formatted})
        except Exception as e:
            self.send_json({'success': False, 'error': str(e), 'formatted': code})
    
    def handle_lint(self):
        """处理代码检查请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            code = data.get('code', '')
        except json.JSONDecodeError:
            self.send_json({'success': False, 'error': 'Invalid JSON', 'issues': []})
            return
        
        try:
            from yan_fmt import YanLinter
            linter = YanLinter()
            issues = linter.lint(code)
            self.send_json({
                'success': True,
                'issues': [
                    {'level': level, 'line': line, 'col': col, 'message': msg}
                    for level, line, col, msg in issues
                ],
            })
        except Exception as e:
            self.send_json({'success': False, 'error': str(e), 'issues': []})
    
    def send_examples(self):
        """发送示例列表"""
        examples = {
            'hello': {'name': '你好，世界', 'description': '最简单的程序'},
            'function': {'name': '函数定义', 'description': '如何定义和使用函数'},
            'list': {'name': '列表操作', 'description': '列表和高阶函数'},
            'condition': {'name': '条件判断', 'description': '条件语句示例'},
            'loop': {'name': '循环遍历', 'description': '遍历列表'},
            'fibonacci': {'name': '斐波那契', 'description': '计算斐波那契数列'},
            'hanoi': {'name': '汉诺塔', 'description': '经典汉诺塔问题'},
            'json': {'name': 'JSON处理', 'description': 'JSON编解码'},
        }
        self.send_json({'success': True, 'examples': examples})
    
    def send_json(self, data):
        """发送 JSON 响应"""
        response = json.dumps(data, ensure_ascii=False)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(response.encode('utf-8')))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=5000, host='localhost'):
    """运行服务器"""
    os.chdir(os.path.dirname(__file__))
    
    server = HTTPServer((host, port), PlaygroundHandler)
    print("=" * 60)
    print("言语言 Playground 服务器")
    print("=" * 60)
    print(f"地址: http://{host}:{port}")
    print("✓ 使用独立进程执行代码，避免内存泄漏")
    print("✓ 30秒超时保护")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='言语言 Playground 服务器')
    parser.add_argument('--port', '-p', type=int, default=5000, help='端口号（默认: 5000）')
    parser.add_argument('--host', '-h', default='localhost', help='主机地址（默认: localhost）')
    
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
