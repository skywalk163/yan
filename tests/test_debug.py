import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

source = '''定阶乘=函n若n小等于1则1否则n乘阶乘n减1。
印阶乘5。
'''

lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens:')
for i, tok in enumerate(tokens):
    print(f'{i}: {tok.type.name} = {repr(tok.value)}')
