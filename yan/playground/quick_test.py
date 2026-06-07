#!/usr/bin/env python3
"""快速测试 playground 示例"""

import sys
import os
import re

# 设置路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(script_dir)  # 这是 yan 目录
project_root = os.path.dirname(os.path.dirname(script_dir))  # 向上两级到 newlisp
sys.path.insert(0, project_root)

print(f"Script dir: {script_dir}")
print(f"Project root: {project_root}")
print(f"Sys.path[0]: {sys.path[0]}")

from yan.lexer import Lexer
from yan.parser import Parser
from yan.codegen import PythonCodeGen
from yan.runtime import ALL_BUILTINS

def test_example(name, code):
    """测试单个示例"""
    try:
        # 词法分析
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        
        # 语法分析
        parser = Parser(syntax_version=2)
        ast = parser.parse(tokens)
        
        # 代码生成
        codegen = PythonCodeGen()
        generated = codegen.generate(ast)
        
        # 执行
        exec_globals = {}
        for name_, (func, arity) in ALL_BUILTINS.items():
            exec_globals[func.__name__] = func
        
        # 捕获输出
        import io
        from contextlib import redirect_stdout
        
        output = io.StringIO()
        with redirect_stdout(output):
            exec(generated, exec_globals)
        
        return {
            'success': True,
            'output': output.getvalue().strip()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def extract_examples(html_path):
    """提取示例"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 examples 对象
    match = re.search(r'const examples = \{', content)
    if not match:
        return []
    
    start_pos = match.start()
    examples_obj = content[start_pos:]
    
    # 提取示例
    examples = []
    pattern = r'(\w+):\s*`([^`]*)`'
    
    for match in re.finditer(pattern, examples_obj):
        name = match.group(1)
        code = match.group(2).replace('\\n', '\n').strip()
        examples.append({'name': name, 'code': code})
        
        # 找到右花括号就停止
        brace_pos = examples_obj.find('}', match.start())
        if match.start() > brace_pos > 0:
            break
    
    return examples

if __name__ == '__main__':
    html_path = os.path.join(script_dir, 'index.html')
    
    print("=" * 60)
    print("言语言 Playground 示例测试")
    print("=" * 60)
    
    examples = extract_examples(html_path)
    print(f"找到 {len(examples)} 个示例\n")
    
    results = []
    for example in examples:
        result = test_example(example['name'], example['code'])
        results.append({
            'name': example['name'],
            **result
        })
    
    # 打印结果
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    success = sum(1 for r in results if r['success'])
    print(f"\n成功: {success}/{len(results)}")
    print(f"失败: {len(results) - success}/{len(results)}\n")
    
    # 失败的示例
    if success < len(results):
        print("失败的示例:")
        for r in results:
            if not r['success']:
                print(f"\n  ❌ {r['name']}")
                print(f"     错误: {r['error'][:100]}")
    else:
        print("\n✅ 所有示例都通过！")
