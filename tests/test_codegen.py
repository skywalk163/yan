import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser
from yan.codegen import PythonCodeGen

source = '''定阶乘=函n若n小等于1则1否则n乘阶乘n减1。
印阶乘5。
'''

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()
ast = parser.parse_v1(tokens)
print('AST:')
print(ast)

codegen = PythonCodeGen()
py_code = codegen.generate(ast)
print('\n生成的 Python 代码:')
print(py_code)
