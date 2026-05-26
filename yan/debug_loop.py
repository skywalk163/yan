#!/usr/bin/env python3
"""调试 test_simple_loop.yan 的解析"""
from lexer import Lexer
from parser import Parser

with open("examples/test_simple_loop.yan", encoding="utf-8") as f:
    source = f.read()

print("=== 源码 ===")
print(source)

print("\n=== Token 生成 ===")
lexer = Lexer()
tokens = lexer.tokenize(source)

for i, tok in enumerate(tokens):
    print(f"{i:3d}: {tok.type.name:12} '{tok.value}' (行{tok.line}, 列{tok.col})")

print("\n=== 开始解析 ===")
try:
    parser = Parser(use_global_verbs=False)
    ast = parser.parse(tokens)
    print("\n✅ 解析成功！")
    print("\n=== AST ===")
    print(ast)
except Exception as e:
    print(f"\n❌ 解析失败: {e}")
    import traceback
    print("\n=== 堆栈追踪 ===")
    print(traceback.format_exc())
