from lexer import Lexer
from parser import Parser, process_adverbs

with open('test_nested_def.yan', 'r', encoding='utf-8') as f:
    source = f.read()

print("源码:")
print(source)
print("\n解析中...")

lexer = Lexer()
tokens = lexer.tokenize(source)

parser = Parser()
try:
    ast = parser.parse(tokens)
    print("\n解析成功!")
    print(f"AST: {ast}")
except Exception as e:
    print(f"\n解析失败: {e}")
