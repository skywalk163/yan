import sys
sys.path.insert(0, '.')
from yan.lexer import Lexer
from yan.parser import Parser
from yan.codegen import PythonCodeGen

# 测试 condition 示例（已成功）
code_condition = """定义 年龄 = 25

如果 大于 年龄 18:
  印 "成年人"
否则:
  印 "未成年"
"""

print("=== 测试 condition 示例 ===")
try:
    lexer = Lexer()
    tokens = lexer.tokenize(code_condition)
    print("Tokens:")
    for tok in tokens:
        print(f"  {tok}")
    
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    print("\nAST:")
    print(ast)
    
    codegen = PythonCodeGen()
    generated = codegen.generate(ast)
    print("\nGenerated Code:")
    print(generated)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n\n=== 测试 bubble 示例（有问题）===")
code_bubble = """定义 冒泡排序 = 函数 arr:
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

定义 原始 = 列表 64 34 25 12 22 11 90
印 连 "原始数组: " 原始
定义 排序后 = 冒泡排序 原始
印 连 "排序后: " 排序后
"""

try:
    lexer = Lexer()
    tokens = lexer.tokenize(code_bubble)
    print("Tokens:")
    for tok in tokens:
        print(f"  {tok}")
    
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    print("\nAST:")
    print(ast)
    
    codegen = PythonCodeGen()
    generated = codegen.generate(ast)
    print("\nGenerated Code:")
    print(generated)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
