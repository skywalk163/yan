#!/usr/bin/env python3
"""简单测试"""

import sys
import os

project_root = r'G:\dumategithub\newlisp'
sys.path.insert(0, project_root)

# 启用调试
sys.argv.append('DEBUG')

from yan.lexer import Lexer
from yan.parser import Parser

code = """当时 小于 j 减 n 加 i 1:
  印 "test"
"""

print("开始解析...")
lexer = Lexer()
tokens = lexer.tokenize(code)

parser = Parser(syntax_version=2)
try:
    ast = parser.parse(tokens)
    print(f"\n解析成功！AST: {ast}")
except Exception as e:
    print(f"\n解析失败: {e}")
