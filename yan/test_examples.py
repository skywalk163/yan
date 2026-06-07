"""
Playground 示例测试脚本 v2
"""
import subprocess
import time
import json
import sys
import re
from pathlib import Path

def extract_examples():
    """从 index.html 提取示例"""
    html_path = Path(__file__).parent / "playground" / "index.html"
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    examples = {}
    
    # 提取所有示例
    pattern = r"(\w+):\s*`([^`]*)`"
    matches = re.findall(pattern, content)
    
    for name, code in matches:
        examples[name] = code
    
    return examples

def wait_for_server(url, timeout=30):
    """等待服务器启动"""
    import urllib.request
    import urllib.error
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, ConnectionRefusedError):
            time.sleep(0.5)
    return False

def start_server(port=5001):
    """启动 playground 服务器"""
    server_script = Path(__file__).parent / "playground" / "server.py"
    process = subprocess.Popen(
        [sys.executable, str(server_script), "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent
    )
    return process

def test_example_via_api(code, port=5001):
    """通过 API 测试示例"""
    import urllib.request
    import urllib.error
    
    url = f'http://localhost:{port}/api/execute'
    
    try:
        data = json.dumps({'code': code}).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {'success': False, 'error': str(e), 'output': []}

def main():
    """主函数"""
    print("=" * 60)
    print("言语言 Playground 示例测试")
    print("=" * 60)
    
    # 提取示例
    examples = extract_examples()
    print(f"\n找到 {len(examples)} 个示例\n")
    
    # 列出所有示例
    for i, name in enumerate(examples.keys(), 1):
        print(f"  {i}. {name}")
    
    print()
    
    # 启动服务器
    print("启动 Playground 服务器...")
    server_process = start_server(5001)
    
    # 等待服务器启动
    print("等待服务器启动...")
    if not wait_for_server('http://localhost:5001'):
        print("错误：服务器启动失败")
        server_process.terminate()
        return
    
    print("服务器已启动\n")
    
    try:
        # 测试每个示例
        results = []
        for i, (name, code) in enumerate(examples.items(), 1):
            print(f"测试 {i}/{len(examples)}: {name}...", end=' ', flush=True)
            
            result = test_example_via_api(code, 5001)
            
            success = result.get('success', False)
            output = '\n'.join(result.get('output', []))
            error = result.get('error', '')
            
            # 检查是否有错误
            has_error = error or 'error' in output.lower() or '错误' in output or '语法' in output or 'SyntaxError' in output
            
            results.append({
                'name': name,
                'success': success and not has_error,
                'output': output,
                'error': error,
                'has_error': has_error
            })
            
            if success and not has_error:
                print("✓ 通过")
            else:
                print("✗ 失败")
                if error:
                    print(f"  错误: {error[:150]}")
                if output:
                    print(f"  输出: {output[:150]}")
        
        # 输出总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)
        
        passed = sum(1 for r in results if r['success'])
        failed = sum(1 for r in results if not r['success'])
        
        print(f"\n通过: {passed}/{len(results)}")
        print(f"失败: {failed}/{len(results)}\n")
        
        if failed > 0:
            print("失败的示例:")
            for r in results:
                if not r['success']:
                    print(f"\n  - {r['name']}")
                    if r['error']:
                        print(f"    错误: {r['error'][:200]}")
                    if r['output']:
                        print(f"    输出: {r['output'][:200]}")
        
    finally:
        # 停止服务器
        print("\n停止服务器...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()
