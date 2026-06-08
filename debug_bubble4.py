import sys
sys.path.insert(0, '.')
from yan.lexer import Lexer
from yan.parser import Parser, TokenType

# 最小化示例，只看 '当时 小于 j 减 n 加 i 1:' 这一行
code = """当时 小于 j 减 n 加 i 1:"""

print("=== Testing minimal example ===")
try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    print("Tokens:")
    for i, tok in enumerate(tokens):
        print(f"  [{i}] {tok}")
    
    parser = Parser(syntax_version=2)
    
    print("\n=== Testing _parse_atom on Token 7 ===")
    parser.tokens = tokens
    parser.pos = 7
    print(f"Before _parse_atom, pos: {parser.pos}, current: {parser._current()}")
    node = parser._parse_atom(stop_tokens={TokenType.COLON})
    print(f"After _parse_atom, pos: {parser.pos}, current: {parser._current()}, node: {node}")
    
    print(f"\nIs current.type == TokenType.COLON now? {parser._current().type == TokenType.COLON}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
