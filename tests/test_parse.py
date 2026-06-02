import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser, _global_user_verbs

# 先定义函数
source1 = '定阶乘={{lambda n: 1 if n <= 1 else n * 阶乘(n-1)}}。'
lexer = Lexer()
tokens1 = list(lexer.tokenize(source1))
parser = Parser()
parser.parse_v1(tokens1)
print('用户定义的函数:', list(_global_user_verbs))

# 再调用函数
source2 = '印阶乘5。'
lexer = Lexer()
tokens2 = list(lexer.tokenize(source2))
print('\n调用函数的 Tokens:')
for tok in tokens2:
    print(f'  {tok.type.name} = {repr(tok.value)}')

ast = parser.parse_v1(tokens2)
print('\nAST:')
print(ast)
