#!/usr/bin/env python3
import sys
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser
from ast_builder import ASTBuilder
from antlr4 import *

def test_ast(code):
    input_stream = InputStream(code)
    lexer = YanLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = YanParser(token_stream)
    
    tree = parser.program()
    builder = ASTBuilder()
    ast = builder.visit(tree)
    
    print("AST:")
    print(ast)

if __name__ == '__main__':
    code = sys.argv[1] if len(sys.argv) > 1 else '定汉诺塔=函盘子数：印盘子数。。'
    test_ast(code)
