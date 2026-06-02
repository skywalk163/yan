import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

with open('yan/examples/basic.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens:')
for i, tok in enumerate(tokens):
    print(f'{i}: {tok.type.name} = {repr(tok.value)}')
