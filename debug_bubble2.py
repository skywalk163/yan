import sys
sys.path.insert(0, '.')
from yan.lexer import Lexer
from yan.parser import Parser, TokenType
from yan.codegen import PythonCodeGen

# 测试 bubble 示例
code = """定义 冒泡排序 = 函数 arr:
  定义 n = 长度 arr
  遍历 i 于 范围 n:
    定义 已交换 = 假
    定义 j = 0
    当时 小于 j 减 n 加 i 1:
      定义 当前 = 取 arr j
      定义 下一个 = 取 arr 加 j 1
      如果 大于 当前 下一个:
        定义 tmp = 当前
        定义 arr = 设 arr j 下一个
        定义 arr = 设 arr 加 j 1 tmp
        定义 已交换 = 真
      定义 j = 加 j 1
    如果 不 已交换:
      返回 arr
  返回 arr
"""

print("=== Testing bubble example ===")
try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    print("Tokens:")
    for i, tok in enumerate(tokens):
        print(f"  [{i}] {tok}")
    
    parser = Parser(syntax_version=2)
    
    # 在 parser 之前添加手动调试
    print("\nParser position tracking:")
    parser.tokens = tokens
    parser.pos = 0
    
    # 手动跟随 _parse_while_v2 路径
    while parser.pos < len(tokens):
        print(f"  parser.pos = {parser.pos}: {parser._current()}")
        
        # 找到 '当时' 关键字
        if parser._current().value == '当时':
            print(f"   - Found '当时' at pos {parser.pos}")
            parser._advance()  # consume '当时'
            
            print(f"   - Now at pos {parser.pos}: {parser._current()}")
            # 尝试解析表达式直到冒号
            # 先看一下接下来有哪些 token
            print(f"   - Next few tokens:")
            for i in range(10):
                if parser.pos + i < len(tokens):
                    print(f"     [{parser.pos + i}] {tokens[parser.pos + i]}")
                    
            print(f"   - Calling _parse_expression with stop_tokens={{TokenType.COLON}}")
            try:
                cond = parser._parse_expression(stop_tokens={TokenType.COLON})
                print(f"   - Got cond: {cond}")
            except Exception as e:
                print(f"   - Error: {e}")
                import traceback
                traceback.print_exc()
            break
        
        parser._advance()
    
    print("\n")
    
    # 让我们直接看一下 TokenType.COLON 是什么
    print(f"TokenType.COLON: {TokenType.COLON}")
    print(f"Current token type at '当时' +3 pos: {tokens[42]}")
    print(f"Current token value: {tokens[42].value}")
    print(f"Current token type: {tokens[42].type}")
    print(f"tokens[42].type == TokenType.COLON: {tokens[42].type == TokenType.COLON}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
