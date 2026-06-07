#!/usr/bin/env python3
"""调试块解析问题"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yan.lexer import Lexer
from yan.parser import Parser
from yan.tokens import TokenType

def debug_parsing(source_code):
    """调试解析过程"""
    print("=" * 60)
    print("源代码:")
    print(source_code)
    print("=" * 60)
    
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
    
    print("\n完整 Token 流 (位置和类型):")
    for i, token in enumerate(tokens):
        print(f"  [{i:2d}] {token.type:12} {repr(token.value):20} line={token.line}, col={token.col}")
    
    # 手动跟踪解析过程
    print("\n开始解析，手动跟踪 _parse_block_v2 调用:")
    parser = Parser(syntax_version=2)
    parser.tokens = tokens
    parser.pos = 0
    parser.user_verbs = set()
    parser._reset_verbs_cache()
    
    print(f"初始位置: pos={parser.pos}, token={parser.tokens[parser.pos]}")
    
    # 让我们执行第一遍收集用户动词
    parser._collect_user_verbs()
    parser._reset_verbs_cache()
    
    parser.pos = 0  # 重置位置
    
    # 现在开始解析程序
    statements = []
    parser.current_indent = 0
    parser.indent_stack = [0]
    
    while not parser._is_at_end():
        # 查看当前位置的token
        print(f"\n循环开始: pos={parser.pos}")
        if parser.pos < len(parser.tokens):
            tok = parser.tokens[parser.pos]
            print(f"  当前 token: [{parser.pos}] {tok.type} {repr(tok.value)}")
        
        # 跳过 DEDENT
        while parser._current().type in {TokenType.DEDENT, TokenType.DOT}:
            print(f"  跳过 token: {parser._current().type} {repr(parser._current().value)}")
            parser._advance()
        if parser._is_at_end():
            break
        
        # 检测缩进
        current_indent = parser._get_indent_level()
        print(f"  当前缩进: {current_indent}, 栈顶: {parser.indent_stack[-1]}")
        
        if current_indent < parser.indent_stack[-1]:
            print("  缩进减少，调整栈")
            while parser.indent_stack and parser.indent_stack[-1] > current_indent:
                parser.indent_stack.pop()
            continue
        
        # 解析语句
        print("  调用 _parse_statement_v2")
        stmt = parser._parse_statement_v2()
        print(f"  _parse_statement_v2 返回: {stmt}")
        if stmt:
            statements.append(stmt)
    
    print("\n最终语句列表:")
    for stmt in statements:
        print(f"  {stmt}")
    
    print("\n=" * 60)
    
    # 现在让我们直接打印AST
    parser.pos = 0
    ast = parser.parse(tokens)
    print(f"\nAST: {ast}")

test_source = """
定义 平方 = 函数 x：
    返回 乘 x x

印 平方 5
"""

debug_parsing(test_source)
