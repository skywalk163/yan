#!/usr/bin/env python3
import sys
from antlr4 import *
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser
from ast_builder import ASTBuilder
from codegen import PythonCodeGen
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser
from ast_builder import ASTBuilder
from codegen import PythonCodeGen
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser
from ast_builder import ASTBuilder
from codegen import PythonCodeGen
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser
from ast_builder import ASTBuilder
from codegen import PythonCodeGen
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser
from ast_builder import ASTBuilder
from codegen import PythonCodeGen
from generated.YanParser import YanParser
from codegen import PythonCodeGen

def test_codegen(code):
    input_stream = InputStream(code)
    lexer = YanLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = YanParser(token_stream)
    
    tree = parser.program()
    builder = ASTBuilder()
    ast = builder.visit(tree)
    
    codegen = PythonCodeGen()
    python_code = codegen.generate(ast)
    
    print("生成的 Python 代码:")
    print(python_code)

if __name__ == '__main__':
    code = sys.argv[1] if len(sys.argv) > 1 else '若1则：印"yes"。。'
    test_codegen(code)
