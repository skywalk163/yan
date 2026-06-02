import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser

with open('yan/examples/test_dollar.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()
ast = parser.parse_v1(tokens)
print('AST:')
print(ast)
