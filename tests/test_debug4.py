import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser

# Patch _parse_if to add debug output
original_parse_if = Parser._parse_if
def debug_parse_if(self):
    print(f"_parse_if called, current token: {self._current()}")
    result = original_parse_if(self)
    print(f"_parse_if finished, next token after _parse_if: {self._current()}")
    return result

Parser._parse_if = debug_parse_if

# Patch _parse_expr_until to add debug output
original_parse_expr_until = Parser._parse_expr_until
def debug_parse_expr_until(self, stop_words):
    print(f"  _parse_expr_until called, stop_words={stop_words}, current token: {self._current()}")
    result = original_parse_expr_until(self, stop_words)
    print(f"  _parse_expr_until returned, next token: {self._current()}")
    return result

Parser._parse_expr_until = debug_parse_expr_until

source = '''定阶乘=函n若n小等于1则1否则n乘阶乘n减1。
印阶乘5。
'''

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()
ast = parser.parse_v1(tokens)
print('\nFinal AST:')
print(ast)
