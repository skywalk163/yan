import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser

with open('yan/examples/basic.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()
ast = parser.parse_v1(tokens)

print(f'Number of statements: {len(ast.statements)}')
print('\nStatement summary:')
for i, stmt in enumerate(ast.statements):
    print(f'{i+1}: {type(stmt).__name__}', end='')
    if hasattr(stmt, 'verb') and hasattr(stmt.verb, 'name'):
        print(f' (verb={stmt.verb.name})', end='')
    if hasattr(stmt, 'args'):
        args_str = ', '.join([type(a).__name__ for a in stmt.args])
        print(f' (args=[{args_str}])', end='')
    print()
