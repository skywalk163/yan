#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from yan.lexer import Lexer

code = '''定 加载数据 = 函 文件名：
  info 连 "加载数据: " 文件名。
  定 数据 = 读CSV 文件名 空。
  info 连 "加载完成，共 " 长 数据 " 条记录"。
  返回 数据。'''

lexer = Lexer()
tokens = lexer.tokenize(code)
for tok in tokens:
    print(f'{tok.line}:{tok.col} {tok.type.name} {repr(tok.value)}')