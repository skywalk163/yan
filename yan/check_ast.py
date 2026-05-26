import sys
sys.path.insert(0, '.')

from parser import Parser
from lexer import Lexer

src = """
定 已用过 = 假。
定 z = "意"。
定 尾 = "意"。
定 匹配 = 且 非 已用过 等 z 尾。
印 连 "匹配=" 匹配。
"""

tokens = Lexer().tokenize(src)
parser = Parser()
ast = parser.parse(tokens)

# 打印 AST
import json

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
