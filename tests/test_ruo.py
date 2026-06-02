import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

source = '印若5大3则"大"否则"小"。'
lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens:')
for tok in tokens:
    print(f'  {tok.type.name} = {repr(tok.value)}')
