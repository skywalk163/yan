#!/usr/bin/env python3
"""调试 _parse_expression 的停止问题"""

import sys
import os

project_root = r'G:\dumategithub\newlisp'
sys.path.insert(0, project_root)

from yan.lexer import Lexer
from yan.parser import Parser
from yan.tokens import TokenType

# 添加调试打印到 _parse_term
original_parse_term = Parser._parse_term

def debug_parse_term(self, stop_tokens=None):
    """带调试的 _parse_term"""
    current = self._current()
    print(f"\n>>> _parse_term called, current: {current}, stop_tokens: {stop_tokens}")
    
    # 检查是否应该停止
    if stop_tokens and current.type in stop_tokens:
        print(f">>> _parse_term: stopping because current token is in stop_tokens")
        return None
    
    result = original_parse_term(self, stop_tokens)
    print(f">>> _parse_term: returned {result}, current is now {self._current()}")
    return result

# 替换 _parse_term
Parser._parse_term = debug_parse_term

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
