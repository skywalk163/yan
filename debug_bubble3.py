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
    
    print("\n=== Let's just test the full parse ===")
    try:
        full_code = code  # Let's test parsing this entire line with our parser
        ast = parser.parse(tokens)
        print("SUCCESS!")
        print(ast)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n=== Debug info: ===")
        print(f"Number of tokens: {len(tokens)}")
        for i, tok in enumerate(tokens):
            print(f"  Token {i}: type={tok.type}, value={repr(tok.value)}, line={tok.line}, col={tok.col}")
            print(f"    Is colon? {tok.type == TokenType.COLON}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
