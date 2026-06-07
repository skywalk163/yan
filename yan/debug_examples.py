"""
调试 playground 例子的代码生成
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser, process_adverbs
from codegen import PythonCodeGen

# 读取 playground 例子
with open('playground/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r'(\w+):\s*`(.*?)`\s*,?\s*\n\s*(?=\w+:|})', re.DOTALL)
matches = pattern.findall(content)

targets = ['idiom', 'binary_search', 'bubble_indent']
for name, code in matches:
    code = code.strip()
    if not code:
        continue
    if name not in targets:
        continue
    print(f'\n===== {name} =====')
    try:
        # 词法分析
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        print("Tokens:")
        for t in tokens:
            print(f"  {t}")
        
        # 语法分析
        parser = Parser(syntax_version=2)
        ast = parser.parse(tokens)
        ast = process_adverbs(ast)
        
        # 代码生成
        codegen = PythonCodeGen()
        py_code = codegen.generate(ast)
        print("\nGenerated Python code:")
        print(py_code)
        print("\n--- END ---")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()