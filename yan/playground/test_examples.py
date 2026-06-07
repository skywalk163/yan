#!/usr/bin/env python3
"""使用 Playwright 测试 playground 中的所有示例"""

import sys
import os
import re
import asyncio

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 向上两级到达项目根目录
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

print(f"脚本目录: {script_dir}")
print(f"项目根目录: {project_root}")
print(f"Python path: {sys.path[0]}")

# 检查 Playwright 是否安装
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("正在安装 Playwright...")
    os.system(f"{sys.executable} -m pip install playwright")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.async_api import async_playwright

def extract_examples_from_html(html_path):
    """从 HTML 文件中提取所有示例"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 JavaScript examples 对象
    examples = []
    
    # 查找 const examples = { ... } 块
    match = re.search(r'const examples = \{', content)
    if not match:
        print("未找到 examples 对象")
        return examples
    
    # 提取到 examples 对象的结束位置
    start_pos = match.start()
    brace_count = 0
    end_pos = start_pos
    
    # 找到对应的右花括号
    in_string = False
    string_char = None
    i = start_pos
    
    while i < len(content):
        char = content[i]
        
        # 处理字符串
        if not in_string:
            if char in ['"', "'", '`']:
                in_string = True
                string_char = char
            elif char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
        else:
            if char == '\\' and i + 1 < len(content):
                i += 2
                continue
            elif char == string_char:
                in_string = False
        
        i += 1
    
    # 提取 examples 对象
    examples_obj = content[start_pos:end_pos]
    
    # 解析每个示例
    # 格式: exampleName: `code` 或 exampleName: "-- comment\ncode"
    pattern = r'(\w+):\s*`([^`]*)`'
    
    for match in re.finditer(pattern, examples_obj):
        name = match.group(1)
        code = match.group(2)
        
        # 清理转义字符
        code = code.replace('\\n', '\n').replace('\\t', '\t')
        code = code.strip()
        
        examples.append({
            'name': name,
            'code': code
        })
    
    return examples

def parse_yan_code(code):
    """解析言语言代码并执行"""
    try:
        from yan.lexer import Lexer
        from yan.parser import Parser
        from yan.codegen import PythonCodeGen
        from yan.runtime import ALL_BUILTINS
        
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser(syntax_version=2)
        ast = parser.parse(tokens)
        codegen = PythonCodeGen()
        generated = codegen.generate(ast)
        
        # 执行代码
        exec_globals = {}
        for name, (func, arity) in ALL_BUILTINS.items():
            exec_globals[func.__name__] = func
        
        # 捕获输出
        import io
        from contextlib import redirect_stdout
        
        output = io.StringIO()
        with redirect_stdout(output):
            exec(generated, exec_globals)
        
        return {
            'success': True,
            'output': output.getvalue(),
            'generated': generated
        }
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

async def test_with_playwright(html_path, example_name, code):
    """使用 Playwright 测试单个示例"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # 加载页面
            await page.goto(f'file:///{html_path}')
            await page.wait_for_load_state('domcontentloaded')
            
            # 查找并点击对应的示例按钮
            button = page.locator(f'button:has-text("{example_name}")')
            if await button.count() == 0:
                # 尝试其他选择器
                buttons = await page.locator('.example-btn').all()
                for btn in buttons:
                    btn_text = await btn.text_content()
                    if example_name in btn_text:
                        button = btn
                        break
            
            if await button.count() > 0:
                await button.click()
                
                # 等待代码加载到编辑器
                await page.wait_for_timeout(500)
                
                # 点击运行按钮
                run_btn = page.locator('button:has-text("运行")')
                if await run_btn.count() > 0:
                    await run_btn.click()
                    await page.wait_for_timeout(1000)
                    
                    # 获取输出
                    output_elem = page.locator('.output-content')
                    if await output_elem.count() > 0:
                        output_text = await output_elem.inner_text()
                        return {
                            'success': True,
                            'output': output_text
                        }
            
            return {
                'success': False,
                'error': '找不到示例按钮或运行按钮'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            await browser.close()

async def test_all_examples():
    """测试所有示例"""
    html_path = os.path.abspath('yan/playground/index.html')
    print(f"正在从 {html_path} 提取示例...")
    
    examples = extract_examples_from_html(html_path)
    print(f"找到 {len(examples)} 个示例\n")
    
    results = []
    
    for i, example in enumerate(examples, 1):
        print(f"测试 {i}/{len(examples)}: {example['name']}")
        print(f"代码:\n{example['code'][:100]}...")
        
        # 先用 Python 直接测试
        print("\n--- Python 执行测试 ---")
        result = parse_yan_code(example['code'])
        
        if result['success']:
            print(f"✓ 成功!")
            print(f"输出: {result['output']}")
        else:
            print(f"✗ 失败!")
            print(f"错误: {result['error']}")
            if 'traceback' in result:
                print(f"详细错误:\n{result['traceback']}")
        
        results.append({
            'name': example['name'],
            'code': example['code'],
            'python_result': result
        })
        print("\n" + "="*60 + "\n")
    
    # 输出总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    success_count = sum(1 for r in results if r['python_result']['success'])
    print(f"成功: {success_count}/{len(results)}")
    print(f"失败: {len(results) - success_count}/{len(results)}")
    
    if success_count < len(results):
        print("\n失败的示例:")
        for r in results:
            if not r['python_result']['success']:
                print(f"  - {r['name']}: {r['python_result']['error']}")
    
    return results

if __name__ == '__main__':
    asyncio.run(test_all_examples())
