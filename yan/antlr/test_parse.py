#!/usr/bin/env python3
import sys
from antlr4 import *
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser

def test_parse(code):
    input_stream = InputStream(code)
    lexer = YanLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = YanParser(token_stream)
    
    tree = parser.program()
    
    # 打印 token
    print("Tokens:")
    lexer.reset()
    for token in lexer.getAllTokens():
        print(f"  {token.text} -> {YanLexer.symbolicNames[token.type]}")
    
    # 打印解析树
    print("\nParse Tree:")
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    code = sys.argv[1] if len(sys.argv) > 1 else "x等1"
    test_parse(code)
