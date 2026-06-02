import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser

source = '印阶乘5。'
lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens:')
for tok in tokens:
    print(f'  {tok.type.name} = {repr(tok.value)}')

parser = Parser()
ast = parser.parse_v1(tokens)
print('\nAST:')
print(ast)
