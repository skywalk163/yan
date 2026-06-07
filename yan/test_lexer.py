"""
聚焦测试：检查词法分析器如何处理有问题的标识符
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer

lexer = Lexer()

# 测试用例
test_cases = [
    # 测试1: 长度值（长度是关键字）
    """定义 长度值 = 长度 "hello"
印 长度值""",
    # 测试2: 取尾字（取是关键字）
    """定义 取尾字 = 函 成语
  定义 长度值 = 长度 成语
  返回 长度值""",
    # 测试3: 冒泡排序的定义和使用
    """定义 冒泡排序 = 函 arr
  定义 n = 长度 arr
  返回 n
定义 列表 = 列 5 3 8 4 2
定义 结果 = 冒泡排序 列表
印 结果""",
]

for i, code in enumerate(test_cases):
    print(f"\n===== 测试 {i+1} =====")
    print(f"源码:\n{code}\n")
    tokens = lexer.tokenize(code)
    for tok in tokens:
        if tok.type.__str__() == 'TokenType.WORD' or 'WORD' in str(tok.type):
            print(f"  WORD: '{tok.value}' (line={tok.line}, col={tok.col})")
        else:
            print(f"  {tok.type}: '{tok.value}'")