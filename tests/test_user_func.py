import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser, _global_user_verbs

# 先定义函数
source1 = '定阶乘=函n若n小等于1则1否则n乘阶乘n减1。'
lexer = Lexer()
tokens1 = list(lexer.tokenize(source1))
parser = Parser()
parser.parse_v1(tokens1)
print('用户定义的函数:', list(_global_user_verbs))

# 再调用函数
source2 = '印阶乘5。'
lexer = Lexer()
tokens2 = list(lexer.tokenize(source2))
ast = parser.parse_v1(tokens2)
print('\nAST:')
print(ast)
