import sys
sys.path.insert(0, '.')
from lexer import Lexer

lexer = Lexer()
source = '定是Node=函节点返回节点首等"Node"。'
tokens = lexer.tokenize(source)
for t in tokens:
    print(f'{t.type.name}: {t.value!r}')