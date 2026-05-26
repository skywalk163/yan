#!/usr/bin/env python3
"""调试缩进语法的 token 生成"""

from lexer import Lexer

source = """定 求和 = 函 列表
  定 结果 = 0。
  遍历 数 于 列表
    定 结果 = 加 结果 数。
  返回 结果。"""

lexer = Lexer()
tokens = lexer.tokenize(source)

print("Token 序列：")
for i, tok in enumerate(tokens):
    print(f"{i:3d}: {tok.type.name:12} '{tok.value}' (行{tok.line}, 列{tok.col})")