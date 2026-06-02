import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser
from yan.codegen import PythonCodeGen
from yan import nodes as nodes_module
from yan import codegen as codegen_module

source = '''定阶乘=函n若n小等于1则1否则n乘阶乘n减1。
印阶乘5。
'''

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()
ast = parser.parse_v1(tokens)

print('Program from nodes module:', nodes_module.Program)
print('Program from codegen module:', codegen_module.Program if hasattr(codegen_module, 'Program') else 'Not found')
print('Are they the same?', nodes_module.Program is codegen_module.Program if hasattr(codegen_module, 'Program') else 'N/A')
