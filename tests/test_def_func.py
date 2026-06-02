import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

source = '定阶乘={{lambda n: 1 if n <= 1 else n * 阶乘(n-1)}}。'
lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('定义阶乘函数的 Tokens:')
for tok in tokens:
    print(f'  {tok.type.name} = {repr(tok.value)}')
