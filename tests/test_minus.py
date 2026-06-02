import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

source = '印10减5。'
lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens:')
for i, tok in enumerate(tokens):
    print(f'{i}: {tok.type.name} = {repr(tok.value)}')
