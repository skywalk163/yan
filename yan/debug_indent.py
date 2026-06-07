#!/usr/bin/env python3
"""调试代码生成器的缩进问题"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yan.lexer import Lexer
from yan.parser import Parser
from yan.codegen import PythonCodeGen
from yan.runtime import ALL_BUILTINS

def test_code_generation(source_code):
    """测试代码生成"""
    print("=" * 60)
    print("源代码:")
    print(source_code)
    print("=" * 60)
    
    # 词法分析
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
    print("\nToken 流:")
    for token in tokens:
        print(f"  {token.type}: {repr(token.value)}")
    
    # 语法分析
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    print("\nAST:")
    print(ast)
    
    # 代码生成
    codegen = PythonCodeGen()
    try:
        generated_code = codegen.generate(ast)
        print("\n生成的 Python 代码:")
        print("-" * 60)
        print(generated_code)
        print("-" * 60)
        
        # 尝试执行
        print("\n执行结果:")
        print("-" * 60)
        exec_globals = {}
        # 添加所有内置函数
        for name, (func, arity) in ALL_BUILTINS.items():
            exec_globals[func.__name__] = func
        exec(generated_code, exec_globals)
        print("执行成功!")
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print()

# 测试用例 1: 简单函数定义
test1 = """
定义 平方 = 函数 x：
    返回 乘 x x

印 平方 5
"""

# 测试用例 2: 条件语句
test2 = """
定义 比较 = 函数 a b：
    如果 大于 a b：
        印 "a 大于 b"
    否则：
        印 "b 大于等于 a"

比较 10 5
"""

# 测试用例 3: 斐波那契
test3 = """
定义 斐波那契 = 函数 n：
    如果 小于等于 n 1：
        返回 n
    否则：
        返回 加 斐波那契 减 n 1 斐波那契 减 n 2

印 斐波那契 10
"""

print("测试 1: 简单函数定义")
test_code_generation(test1)

print("\n测试 2: 条件语句")
test_code_generation(test2)

print("\n测试 3: 斐波那契")
test_code_generation(test3)
