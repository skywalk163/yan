import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser

source = '''定阶乘=函n若n小等于1则1否则n乘阶乘n减1。
印阶乘5。
'''

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()
ast = parser.parse_v1(tokens)

print('AST:')
print(ast)

print('\n结构分析:')
for stmt in ast.statements:
    print(f'  Statement: {type(stmt).__name__}')
    if hasattr(stmt, 'name'):
        print(f'    Name: {stmt.name}')
    if hasattr(stmt, 'value'):
        print(f'    Value type: {type(stmt.value).__name__}')
        if hasattr(stmt.value, 'body'):
            body = stmt.value.body
            print(f'    Body type: {type(body).__name__}')
            if hasattr(body, 'statements'):
                print(f'    Number of statements in body: {len(body.statements)}')
                for i, s in enumerate(body.statements):
                    print(f'      Statement {i}: {type(s).__name__}')
