"""
Playground 所有示例测试脚本
使用 Playwright 测试所有例子是否正常运行
"""
import asyncio
import subprocess
import time
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# 等待服务器启动
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

# 启动 playground 服务器
def start_server(port=5000):
    """启动 playground 服务器"""
    server_script = Path(__file__).parent / "playground" / "server.py"
    process = subprocess.Popen(
        [sys.executable, str(server_script), "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent
    )
    return process

# 加载示例代码
def load_examples():
    """从 index.html 中加载示例"""
    html_path = Path(__file__).parent / "playground" / "index.html"
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 examples 对象
    import re
    match = re.search(r'const examples = \{([^}]+(?:\{[^}]*\}[^}]*)*)\};', content, re.DOTALL)
    if not match:
        return {}
    
    examples_str = match.group(0).replace('const examples = ', '').replace('};', '}')
    
    # 使用简单的解析
    examples = {}
    current_key = None
    current_value = []
    in_string = False
    string_char = None
    
    for i, char in enumerate(examples_str):
        if char in ['"', "'"] and (i == 0 or examples_str[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
                if current_key is None:
                    # 开始新键
                    pass
            elif char == string_char:
                in_string = False
                string_char = None
                # 检查是否是键或值
                if current_key is None:
                    # 这是键
                    pass
        elif not in_string:
            if char == ':':
                # 开始值
                pass
            elif char == ',' and current_key:
                # 保存当前示例
                code = ''.join(current_value).strip()
                if code.startswith('`') and code.endswith('`'):
                    code = code[1:-1]
                examples[current_key.strip()] = code
                current_key = None
                current_value = []
            elif char == '`':
                in_string = True
                string_char = '`'
    
    return examples

async def test_example(page, name, code):
    """测试单个示例"""
    try:
        # 加载页面
        await page.goto('http://localhost:5000')
        await page.wait_for_load_state('networkidle')
        
        # 等待编辑器加载
        await page.wait_for_selector('#editor', timeout=5000)
        
        # 清除编辑器并输入代码
        await page.fill('#editor', code)
        
        # 点击运行按钮
        await page.click('#runBtn')
        
        # 等待执行完成
        await asyncio.sleep(2)
        
        # 获取输出
        output = await page.text_content('#output')
        
        # 检查是否有错误
        has_error = 'error' in output.lower() or '错误' in output or '语法' in output
        
        return {
            'name': name,
            'success': not has_error,
            'output': output.strip(),
            'has_error': has_error
        }
    except Exception as e:
        return {
            'name': name,
            'success': False,
            'output': str(e),
            'has_error': True
        }

async def main():
    """主测试函数"""
    print("=" * 60)
    print("言语言 Playground 示例测试")
    print("=" * 60)
    
    # 启动服务器
    print("\n启动 Playground 服务器...")
    server_process = start_server(5000)
    
    # 等待服务器启动
    print("等待服务器启动...")
    if not wait_for_server('http://localhost:5000'):
        print("错误：服务器启动失败")
        server_process.terminate()
        return
    
    print("服务器已启动\n")
    
    try:
        # 加载示例
        examples = load_examples()
        
        if not examples:
            print("错误：无法加载示例")
            return
        
        print(f"找到 {len(examples)} 个示例\n")
        
        # 启动 Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 测试每个示例
            results = []
            for i, (name, code) in enumerate(examples.items(), 1):
                print(f"测试 {i}/{len(examples)}: {name}...", end=' ')
                
                result = await test_example(page, name, code)
                results.append(result)
                
                if result['success']:
                    print("✓ 通过")
                else:
                    print("✗ 失败")
                    print(f"  输出: {result['output'][:200]}...")
            
            await browser.close()
        
        # 输出总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)
        
        passed = sum(1 for r in results if r['success'])
        failed = sum(1 for r in results if not r['success'])
        
        print(f"通过: {passed}/{len(results)}")
        print(f"失败: {failed}/{len(results)}\n")
        
        if failed > 0:
            print("失败的示例:")
            for r in results:
                if not r['success']:
                    print(f"  - {r['name']}")
                    print(f"    {r['output'][:100]}...")
        
    finally:
        # 停止服务器
        print("\n停止服务器...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(main())
