import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser, _global_user_verbs

# 先定义函数（使用 函 关键字）
source1 = '定阶乘=函n若n小等于1则1否则n乘阶乘n减1。'
lexer = Lexer()
tokens1 = list(lexer.tokenize(source1))
print('定义阶乘的 Tokens:')
for tok in tokens1:
    print(f'  {tok.type.name} = {repr(tok.value)}')

parser = Parser()
parser.parse_v1(tokens1)
print('\n用户定义的函数:', list(_global_user_verbs))

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
