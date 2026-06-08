#!/usr/bin/env python3
"""调试 parser 的 token 流"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / 'yan'))

from yan.lexer import Lexer
from yan.parser import Parser, TokenType

# 测试代码
test_code = """-- 测试包含用户定义函数调用的简单情况
定义 平方 = 函数 n
  返回 乘 n n

定义 a = 平方 3
定义 b = 平方 4
定义 结果 = 加 a b
印 结果
"""

print("=== Lexing...")
# 先看看 tokens
lexer = Lexer()
tokens = lexer.tokenize(test_code)
print("=== Tokens ===")
for i, tok in enumerate(tokens):
    print(f"{i:3d}: {tok}")

print("\n=== Parsing ===")
try:
    # 创建 parser
    parser = Parser(syntax_version=2)
    program = parser.parse(tokens)
    print(f"Parsed successfully!")
    print(f"\nStatements count: {len(program.statements)}")
    for i, stmt in enumerate(program.statements):
        print(f"{i:2d}: {type(stmt).__name__}: {stmt}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()