"""Debug bubble_indent parsing with more detail."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from lexer import Lexer
from parser import Parser

code = """-- 测试缩进语法的冒泡排序
定 冒泡排序 = 函 arr
  定 n = 长 arr
  遍历 i 于 范围 n
    定 已交换 = 假
    定 边界 = 减 (减 n i) 1
    定 j = 0
    当 小 j 边界
      定 当前 = 取 arr j
      定 下一个 = 取 arr 加 j 1
      若 大 当前 下一个
        设 arr j 下一个
        设 arr 加 j 1 当前
        定 已交换 = 真
      定 j = 加 j 1
    如果 非也 已交换
      返回 arr
  返回 arr

-- 测试调用
定 列表 = 列 5 3 8 4 2
印 "排序前："
印 列表
定 结果 = 冒泡排序 列表
印 "排序后："
印 结果。"""

print('=== TOKENS ===')
lexer = Lexer()
tokens = lexer.tokenize(code)
for i, tok in enumerate(tokens):
    print(f'  {i}: {tok}')

print()
print('=== PARSE ===')
parser = Parser(syntax_version=2)

# Check user verbs before parsing
parser.parse(tokens)  # This should work now

print('Parse OK!')
print(f'User verbs: {parser.user_verbs}')
print(f'User verb arity: {parser.user_verb_arity}')