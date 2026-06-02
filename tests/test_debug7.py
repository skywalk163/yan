import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer
from yan.parser import Parser
from yan.nodes import If

# Patch _parse_if to add debug output
original_parse_if = Parser._parse_if
def debug_parse_if(self):
    print(f"_parse_if called, current token: {self._current()}")
    
    # Get the current position
    line, col = self._current().line, self._current().col
    
    # Check if current word starts with 如果
    if self._current().type.name == 'WORD' and self._current().value.startswith('如果') and len(self._current().value) > 2:
        full = self._current().value
        rest = full[2:]
        print(f"  Splitting '{full}' into '如果' and '{rest}'")
        self._advance()
        self.pos -= 1
        from yan.lexer import Token as LexerToken
        from yan.lexer import TokenType
        self.tokens[self.pos] = LexerToken(TokenType.WORD, rest, line, col + 2)
    else:
        print(f"  Advancing past '{self._current().value}'")
        self._advance()
    
    print(f"  After consuming 如果/若, current token: {self._current()}")
    
    # Parse condition
    print(f"  Calling _parse_expr_until for condition...")
    cond = self._parse_expr_until({'则', '：', 'INDENT'})
    print(f"  Condition parsed, next token: {self._current()}")
    
    # Check for 则
    print(f"  Checking for 则 (first time)...")
    if self._check_word('则'):
        print(f"    Found 则, consuming...")
        self._advance()
    print(f"  After first 则 check, current token: {self._current()}")
    
    # Check for 则 (second time)
    print(f"  Checking for 则 (second time)...")
    if self._check_word('那么') or self._check_word('则'):
        print(f"    Found 则, consuming...")
        self._advance()
    print(f"  After second 则 check, current token: {self._current()}")
    
    # Check for block
    has_block = self._current().type.name in ('COLON', 'INDENT')
    print(f"  has_block = {has_block}, current token: {self._current()}")
    
    if self._current().type.name == 'COLON':
        self._advance()
    
    # Parse then branch
    if has_block:
        then_branch = self._parse_block_until({'否则'}, always_block=True)
    else:
        print(f"  Calling _parse_expr_until for then_branch...")
        then_branch = self._parse_expr_until({'否则'})
        print(f"  Then branch parsed, next token: {self._current()}")
    
    print(f"  Then branch: {type(then_branch).__name__}")
    
    # ... continue with else branch
    else_branch = None
    if self._current().type.name == 'DEDENT':
        self._advance()
    
    if self._current().type.name == 'DOT':
        peek = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
        if peek and peek.type.name == 'WORD' and peek.value == '否则':
            self._advance()
    
    if self._check_word('否则'):
        self._advance()
        has_else_block = self._current().type.name in ('COLON', 'INDENT')
        if self._current().type.name == 'COLON':
            self._advance()
        if has_else_block:
            else_branch = self._parse_block_until(set(), always_block=True)
        else:
            else_branch = self._parse_expr_until(set())
    
    print(f"  Else branch: {type(else_branch).__name__ if else_branch else 'None'}")
    print(f"  _parse_if finished, next token: {self._current()}")
    
    return If(cond, then_branch, else_branch)

Parser._parse_if = debug_parse_if

source = '''定阶乘=函n若n小等于1则1否则n乘阶乘n减1。
印阶乘5。
'''

lexer = Lexer()
tokens = list(lexer.tokenize(source))
parser = Parser()
ast = parser.parse_v1(tokens)
print('\nFinal AST:')
print(ast)
