#!/usr/bin/env python3
"""详细调试 condition 和 loop 示例"""

import sys
import os
import re

project_root = r'G:\dumategithub\newlisp'
sys.path.insert(0, project_root)

from yan.lexer import Lexer
from yan.parser import Parser
from yan.codegen import PythonCodeGen
from yan.runtime import ALL_BUILTINS

def extract_example_from_html(name):
    """从 HTML 文件中提取指定名称的示例"""
    html_path = os.path.join(project_root, 'yan', 'playground', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 examples 对象
    match = re.search(rf'{name}:\s*`([^`]*)`', content)
    if match:
        return match.group(1).replace('\\n', '\n')
    return None

def test_and_debug(name, code):
    """测试并显示详细调试信息"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"{'='*60}")
    print("代码:")
    print(code)
    print()
    
    try:
        # 词法分析
        print("1. 词法分析...")
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        print(f"   ✓ 生成了 {len(tokens)} 个 tokens")
        
        # 显示关键 tokens
        print("   关键 tokens:")
        for i, tok in enumerate(tokens[:30]):  # 只显示前30个
            if tok.type.name in ['WORD', 'INDENT', 'DEDENT', 'COLON', 'EQUALS']:
                print(f"   [{i:2d}] {tok.type.name:10} {repr(tok.value):20}")
        
        # 语法分析
        print("\n2. 语法分析...")
        parser = Parser(syntax_version=2)
        ast = parser.parse(tokens)
        print(f"   ✓ 语法分析成功")
        print(f"   AST: {str(ast)[:200]}...")
        
        # 代码生成
        print("\n3. 代码生成...")
        codegen = PythonCodeGen()
        generated = codegen.generate(ast)
        print(f"   ✓ 代码生成成功")
        print("   生成的代码:")
        print("   " + "\n   ".join(generated.split('\n')[:10]))  # 只显示前10行
        
        # 执行
        print("\n4. 执行...")
        exec_globals = {}
        for name_, (func, arity) in ALL_BUILTINS.items():
            exec_globals[func.__name__] = func
        
        import io
        from contextlib import redirect_stdout
        
        output = io.StringIO()
        with redirect_stdout(output):
            exec(generated, exec_globals)
        
        print(f"   ✓ 执行成功")
        print(f"   输出: {output.getvalue().strip()}")
        return True, None
        
    except Exception as e:
        print(f"   ✗ 失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

# 从 HTML 文件提取示例并测试
print("从 HTML 文件提取示例...")

condition_code = extract_example_from_html('condition')
if condition_code:
    test_and_debug("condition", condition_code)
else:
    print("未找到 condition 示例")

loop_code = extract_example_from_html('loop')
if loop_code:
    test_and_debug("loop", loop_code)
else:
    print("未找到 loop 示例")

