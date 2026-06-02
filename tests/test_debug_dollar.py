import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser

with open('yan/examples/test_dollar.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens:')
for i, tok in enumerate(tokens):
    print(f'{i}: {tok.type.name} = {repr(tok.value)}')

parser = Parser()
ast = parser.parse_v1(tokens)
print('\nAST:')
print(ast)

print('\nNumber of statements:', len(ast.statements))
for i, stmt in enumerate(ast.statements):
    print(f'Statement {i}: {type(stmt).__name__}')
    if hasattr(stmt, 'verb'):
        print(f'  Verb: {stmt.verb}')
    if hasattr(stmt, 'args'):
        print(f'  Args: {stmt.args}')
