#!/usr/bin/env python3
"""详细调试 _parse_while_v2 的问题"""

import sys
import os

project_root = r'G:\dumategithub\newlisp'
sys.path.insert(0, project_root)

from yan.lexer import Lexer
from yan.parser import Parser
from yan.tokens import TokenType

# 添加调试打印
original_parse_while_v2 = Parser._parse_while_v2

def debug_parse_while_v2(self):
    """带调试的 _parse_while_v2"""
    print(f"\n>>> _parse_while_v2 called at token: {self._current()}")
    
    self._advance()  # 消耗 '当满足' 或 '当时'
    print(f">>> After advance, current token: {self._current()}")
    
    # 解析条件表达式，遇到冒号时停止
    print(f">>> Calling _parse_expression(stop_tokens={{TokenType.COLON}})")
    cond = self._parse_expression(stop_tokens={TokenType.COLON})
    print(f">>> _parse_expression returned: {cond}")
    print(f">>> Current token after _parse_expression: {self._current()}")
    
    # 消耗冒号（如果有）
    if self._current().type == TokenType.COLON:
        print(f">>> Consuming COLON token")
        self._advance()
    
    print(f">>> Current token after COLON check: {self._current()}")
    
    # 解析循环体
    print(f">>> Calling _parse_block_v2()")
    body = self._parse_block_v2()
    print(f">>> _parse_block_v2 returned: {body}")
    
    return original_parse_while_v2(self)

# 替换 _parse_while_v2
Parser._parse_while_v2 = debug_parse_while_v2

code = """定义 冒泡排序 = 函数 arr:
  定义 n = 长度 arr
  遍历 i 于 范围 n:
    定义 已交换 = 假
    定义 j = 0
    当时 小于 j 减 n 加 i 1:
      定义 当前 = 取 arr j
      定义 下一个 = 取 arr 加 j 1
      如果 大于 当前 下一个:
        定义 tmp = 当前
        定义 arr = 设 arr j 下一个
        定义 arr = 设 arr 加 j 1 tmp
        定义 已交换 = 真
      定义 j = 加 j 1
    如果 不 已交换:
      返回 arr
  返回 arr

定义 原始 = 列表 64 34 25 12 22 11 90
印 连 "原始数组: " 原始
定义 排序后 = 冒泡排序 原始
印 连 "排序后: " 排序后"""

print("开始解析...")
lexer = Lexer()
tokens = lexer.tokenize(code)

parser = Parser(syntax_version=2)
try:
    ast = parser.parse(tokens)
    print(f"\n解析成功！AST: {ast}")
except Exception as e:
    print(f"\n解析失败: {e}")
    import traceback
    traceback.print_exc()
