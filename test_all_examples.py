#!/usr/bin/env python3
"""测试 playground 示例"""

import sys
import os
import re

# 设置路径
project_root = r'G:\dumategithub\newlisp'
sys.path.insert(0, project_root)

from yan.lexer import Lexer
from yan.parser import Parser
from yan.codegen import PythonCodeGen
from yan.runtime import ALL_BUILTINS

def test_example(name, code):
    """测试单个示例"""
    try:
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser(syntax_version=2)
        ast = parser.parse(tokens)
        codegen = PythonCodeGen()
        generated = codegen.generate(ast)

        exec_globals = {}
        for name_, (func, arity) in ALL_BUILTINS.items():
            exec_globals[func.__name__] = func

        import io
        from contextlib import redirect_stdout

        output = io.StringIO()
        with redirect_stdout(output):
            exec(generated, exec_globals)

        return True, output.getvalue().strip()
    except Exception as e:
        return False, str(e)

# 从 HTML 提取示例
html_path = os.path.join(project_root, 'yan', 'playground', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找示例
match = re.search(r'const examples = \{', content)
if not match:
    print("未找到 examples")
    sys.exit(1)

# 提取所有示例
examples = {}

# 使用更简单的方法：逐个查找 "word: `" 模式
pattern = re.compile(r'(\w+):\s*`', re.MULTILINE)

for match in pattern.finditer(content):
    name = match.group(1)
    code_start = match.end()

    # 找到对应的反引号（考虑转义）
    j = code_start
    while j < len(content):
        if content[j] == '\\' and j + 1 < len(content):
            j += 2
            continue
        elif content[j] == '`':
            # 找到结束的反引号
            code = content[code_start:j]
            examples[name] = code
            break
        j += 1

print(f"找到 {len(examples)} 个示例\n")
print("=" * 70)

success = 0
fail = 0

for name, code in examples.items():
    ok, result = test_example(name, code)
    if ok:
        success += 1
        print(f"✅ {name}")
    else:
        fail += 1
        print(f"❌ {name}: {result[:100]}...")

print("\n" + "=" * 70)
print(f"总结: ✅ {success} | ❌ {fail}")