#!/usr/bin/env python3
"""健壮的 Playground 示例测试脚本"""

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

# 查找 examples 对象
match = re.search(r'const examples = \{', content)
if not match:
    print("❌ 未找到 examples 对象")
    sys.exit(1)

print(f"✅ 找到 examples 对象在位置: {match.start()}")

# 找到 examples 对象的范围
start = match.start()
brace_count = 0
in_string = False
string_char = None
end = start

for i in range(start, len(content)):
    char = content[i]
    
    if not in_string:
        if char in ['"', "'", '`']:
            in_string = True
            string_char = char
        elif char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end = i + 1
                print(f"✅ examples 对象结束位置: {end}, 长度: {end - start}")
                break
    else:
        if char == '\\' and i + 1 < len(content):
            i += 2
            continue
        elif char == string_char:
            in_string = False
    
    if i - start > 100000:
        print(f"⚠️  达到最大搜索长度")
        break

if end == start:
    print("❌ 无法确定 examples 对象范围")
    sys.exit(1)

examples_obj = content[start:end]
print(f"✅ 提取 examples 对象成功，长度: {len(examples_obj)}")

# 提取示例
examples = []
pattern = r'(\w+):\s*`([^`]*)`'
for match in re.finditer(pattern, examples_obj):
    name = match.group(1)
    code = match.group(2).replace('\\n', '\n').strip()
    examples.append((name, code))

print(f"找到 {len(examples)} 个示例\n")
print("=" * 70)

success = 0
fail = 0
failed_examples = []

for name, code in examples:
    ok, result = test_example(name, code)
    if ok:
        success += 1
        print(f"✅ {name}")
    else:
        fail += 1
        failed_examples.append((name, result))
        print(f"❌ {name}: {result[:80]}...")

print("\n" + "=" * 70)
print(f"总结: ✅ {success} | ❌ {fail}")

if failed_examples:
    print("\n失败的示例详情:")
    for name, error in failed_examples:
        print(f"\n{name}:")
        print(f"  {error}")
