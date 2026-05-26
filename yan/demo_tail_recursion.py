#!/usr/bin/env python3
"""
尾递归优化演示
展示尾递归优化如何工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from codegen import OptimizedPythonCodeGen, OptimizerConfig


def demo_tail_recursion():
    """演示尾递归优化"""
    print("=" * 60)
    print("言语言尾递归优化演示")
    print("=" * 60)
    
    # 测试代码：尾递归阶乘
    source = """定义 尾递归阶乘 = 函数 n acc
    如果 小于等于 n 1 那么
        acc
    否则
        尾递归阶乘 减 n 1 乘 n acc

输出 尾递归阶乘 5 1
"""
    
    print("\n1. 原始言语言代码:")
    print("-" * 40)
    print(source)
    
    # 词法分析
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    
    # 语法分析
    parser = Parser()
    ast = parser.parse(tokens)
    
    # 使用优化的代码生成器
    print("\n2. 使用尾递归优化生成 Python 代码:")
    print("-" * 40)
    
    config = OptimizerConfig(tail_recursion_optimization=True)
    codegen = OptimizedPythonCodeGen(config)
    optimized_code = codegen.generate(ast)
    print(optimized_code)
    
    print("\n3. 优化统计:")
    print("-" * 40)
    stats = codegen.get_optimization_stats()
    print(f"优化次数: {stats['optimizations_count']}")
    print(f"配置: {stats['config']}")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


def demo_without_tail_recursion():
    """对比：不使用尾递归优化"""
    print("\n\n" + "=" * 60)
    print("对比：不使用尾递归优化")
    print("=" * 60)
    
    source = """定义 尾递归阶乘 = 函数 n acc
    如果 小于等于 n 1 那么
        acc
    否则
        尾递归阶乘 减 n 1 乘 n acc

输出 尾递归阶乘 5 1
"""
    
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    parser = Parser()
    ast = parser.parse(tokens)
    
    # 禁用尾递归优化
    config = OptimizerConfig(tail_recursion_optimization=False)
    codegen = OptimizedPythonCodeGen(config)
    code = codegen.generate(ast)
    
    print("\n生成的代码（无尾递归优化）:")
    print("-" * 40)
    print(code)


if __name__ == "__main__":
    demo_tail_recursion()
    demo_without_tail_recursion()
