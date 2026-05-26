import sys
sys.path.insert(0, '.')

from parser import Parser
from lexer import Lexer
import json

with open('examples/test_idiom_auto.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()
tokens = lexer.tokenize(source)

parser = Parser()
ast = parser.parse(tokens)

# 打印 AST 结构
def node_to_dict(node):
    if node is None:
        return None
    if hasattr(node, '__dataclass_fields__'):
        result = {'type': type(node).__name__}
        for field in node.__dataclass_fields__:
            value = getattr(node, field)
            if isinstance(value, list):
                result[field] = [node_to_dict(v) for v in value]
            else:
                result[field] = node_to_dict(value)
        return result
    elif isinstance(node, list):
        return [node_to_dict(v) for v in node]
    else:
        return str(node)

ast_dict = node_to_dict(ast)
print(json.dumps(ast_dict, indent=2, ensure_ascii=False))
