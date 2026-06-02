import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser

with open('yan/examples/basic.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()

try:
    ast = parser.parse_v1(tokens)
    print('Parsing successful')
    print(f'Number of statements: {len(ast.statements)}')
except Exception as e:
    print(f'Parsing error: {e}')
    import traceback
    traceback.print_exc()
