#!/usr/bin/env python3
"""追踪 _parse_term 的所有调用"""

import sys
import os
import traceback

project_root = r'G:\dumategithub\newlisp'
sys.path.insert(0, project_root)

from yan.lexer import Lexer
from yan.parser import Parser
from yan.tokens import TokenType

# 跟踪调用栈
call_count = [0]

# 保存原始的 _parse_term
original_parse_term = Parser._parse_term

def traced_parse_term(self, stop_tokens=None):
    call_count[0] += 1
    call_id = call_count[0]
    indent = "  " * call_id
    
    current = self._current()
    
    # 只追踪 stop_tokens=None 的调用
    if stop_tokens is None:
        print(f"\n{'='*60}")
        print(f"{indent}[#{call_id}] _parse_term called with STOP_TOKENS=None!!!")
        print(f"{indent}  current: {current}")
        print(f"{indent}  调用栈:")
        for line in traceback.format_stack()[-8:-1]:
            if 'yan/parser.py' in line:
                print(f"{indent}    {line.strip()}")
        print(f"{'='*60}\n")
    
    result = original_parse_term(self, stop_tokens)
    
    return result

# 替换 _parse_term
Parser._parse_term = traced_parse_term

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
    print(f"\n总共调用 _parse_term {call_count[0]} 次")
