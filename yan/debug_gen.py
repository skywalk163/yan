import sys
sys.path.insert(0, '.')

from parser import Parser
from lexer import Lexer
from codegen import PythonCodeGen

with open('examples/test_idiom_auto.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()
tokens = lexer.tokenize(source)

parser = Parser()
ast = parser.parse(tokens)

gen = PythonCodeGen()
code = gen.generate(ast)

# 只打印前100行
lines = code.split('\n')
for i, line in enumerate(lines[:100], 1):
    print(f"{i:3d}: {line}")
