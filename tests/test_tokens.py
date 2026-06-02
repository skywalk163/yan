import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

source = '印阶乘5。'
lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens:')
for tok in tokens:
    print(f'  {tok.type.name} = {repr(tok.value)}')
