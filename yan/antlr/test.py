#!/usr/bin/env python3
"""
测试 ANTLR 版本的言语言
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import parse, compile_to_python, run


def test_basic():
    """测试基本功能"""
    print("=" * 60)
    print("测试基本功能")
    print("=" * 60)
    
    # 测试数字
    code = "印1。"
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)
    
    # 测试字符串
    code = '印"你好"。'
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)
    
    # 测试变量定义
    code = "定张三=10。印张三。"
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)
    
    # 测试省略"定"
    code = "李四=20。印李四。"
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)
    
    # 测试"等于"赋值
    code = "王五等于30。印王五。"
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)


def test_lambda():
    """测试 Lambda 表达式"""
    print("\n" + "=" * 60)
    print("测试 Lambda 表达式")
    print("=" * 60)
    
    # 简单 Lambda
    code = "定平方=函x 乘x x。印平方5。"
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)
    
    # 多参数 Lambda
    code = "定距离=函a b 减a b。印距离10 3。"
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)


def test_if():
    """测试条件表达式"""
    print("\n" + "=" * 60)
    print("测试条件表达式")
    print("=" * 60)
    
    # 简单条件
    code = "若真则印1否则印0。"
    print(f"\n代码: {code}")
    print("输出: ", end="")
    run(code)
    
    # 带块的条件
    code = """
定绝对值=函x：
  若x小0则负x否则x。
。
印绝对值负5。
印绝对值10。
"""
    print(f"\n代码: {code}")
    print("输出:")
    run(code)


def test_recursion():
    """测试递归函数"""
    print("\n" + "=" * 60)
    print("测试递归函数")
    print("=" * 60)
    
    # 阶乘
    code = """
定阶乘=函n：
  若n等1则1否则乘n 阶乘减n 1。
。
印阶乘5。
"""
    print(f"\n代码: {code}")
    print("输出:")
    run(code)


def test_hanoi():
    """测试汉诺塔"""
    print("\n" + "=" * 60)
    print("测试汉诺塔")
    print("=" * 60)
    
    code = """
定汉诺塔=函盘子数 源柱 辅助柱 目标柱：
  若盘子数等1则：
    印源柱 " -> " 目标柱。
  否则：
    汉诺塔减盘子数1 源柱 目标柱 辅助柱。
    印源柱 " -> " 目标柱。
    汉诺塔减盘子数1 辅助柱 源柱 目标柱。
  。
。

印"=== 汉诺塔问题演示 ==="。
印"移动 1 个盘子："。
汉诺塔1 "A" "B" "C"。
印""。
印"移动 2 个盘子："。
汉诺塔2 "A" "B" "C"。
"""
    print(f"\n代码: {code}")
    print("输出:")
    run(code)


def test_compile():
    """测试编译"""
    print("\n" + "=" * 60)
    print("测试编译")
    print("=" * 60)
    
    code = """
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。
印距离3 7。
"""
    print(f"\n言语言代码:\n{code}")
    
    python_code = compile_to_python(code)
    print(f"\n生成的 Python 代码:\n{python_code}")


if __name__ == '__main__':
    test_basic()
    test_lambda()
    test_if()
    test_recursion()
    test_hanoi()
    test_compile()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
