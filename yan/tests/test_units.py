#!/usr/bin/env python3
"""
单元测试示例
测试语言核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yan_test import suite, test, run, YanTestFramework
from yan_assertions import *

# 创建测试框架实例
_test = YanTestFramework()


@_test.suite("算术运算测试")
class ArithmeticTests:
    """算术运算单元测试"""

    def test_addition(self):
        """测试加法"""
        断言等(1 + 2, 3)
        断言等(0 + 0, 0)
        断言等(-1 + 1, 0)

    def test_subtraction(self):
        """测试减法"""
        断言等(5 - 3, 2)
        断言等(0 - 0, 0)
        断言等(1 - 5, -4)

    def test_multiplication(self):
        """测试乘法"""
        断言等(3 * 4, 12)
        断言等(0 * 100, 0)
        断言等(-2 * 3, -6)

    def test_division(self):
        """测试除法"""
        断言等(10 / 2, 5)
        断言等(9 / 3, 3)

    def test_modulo(self):
        """测试取模"""
        断言等(10 % 3, 1)
        断言等(15 % 5, 0)

    def test_power(self):
        """测试幂运算"""
        断言等(2 ** 3, 8)
        断言等(5 ** 2, 25)
        断言等(10 ** 0, 1)


@_test.suite("字符串操作测试")
class StringTests:
    """字符串操作单元测试"""

    def test_string_concatenation(self):
        """测试字符串拼接"""
        断言等("Hello" + " " + "World", "Hello World")

    def test_string_length(self):
        """测试字符串长度"""
        断言等(len("Hello"), 5)
        断言等(len(""), 0)

    def test_string_upper(self):
        """测试字符串大写"""
        断言等("hello".upper(), "HELLO")

    def test_string_lower(self):
        """测试字符串小写"""
        断言等("HELLO".lower(), "hello")

    def test_string_strip(self):
        """测试去除空白"""
        断言等("  hello  ".strip(), "hello")

    def test_string_split(self):
        """测试字符串分割"""
        断言等("a,b,c".split(","), ["a", "b", "c"])


@_test.suite("列表操作测试")
class ListTests:
    """列表操作单元测试"""

    def test_list_creation(self):
        """测试列表创建"""
        lst = [1, 2, 3]
        断言等(len(lst), 3)

    def test_list_append(self):
        """测试列表追加"""
        lst = [1, 2]
        lst.append(3)
        断言等(lst, [1, 2, 3])

    def test_list_index(self):
        """测试列表索引"""
        lst = [1, 2, 3]
        断言等(lst[0], 1)
        断言等(lst[1], 2)

    def test_list_slice(self):
        """测试列表切片"""
        lst = [1, 2, 3, 4, 5]
        断言等(lst[1:3], [2, 3])


@_test.suite("字典操作测试")
class DictTests:
    """字典操作单元测试"""

    def test_dict_creation(self):
        """测试字典创建"""
        d = {"a": 1, "b": 2}
        断言等(len(d), 2)

    def test_dict_access(self):
        """测试字典访问"""
        d = {"a": 1, "b": 2}
        断言等(d["a"], 1)

    def test_dict_keys(self):
        """测试字典键"""
        d = {"a": 1, "b": 2}
        断言等(list(d.keys()), ["a", "b"])


@_test.suite("函数测试")
class FunctionTests:
    """函数单元测试"""

    def test_simple_function(self):
        """测试简单函数"""
        def add(a, b):
            return a + b

        断言等(add(1, 2), 3)

    def test_lambda_function(self):
        """测试Lambda函数"""
        square = lambda x: x ** 2
        断言等(square(5), 25)

    def test_recursive_function(self):
        """测试递归函数"""
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)

        断言等(factorial(5), 120)

    def test_higher_order_function(self):
        """测试高阶函数"""
        def apply_twice(func, x):
            return func(func(x))

        断言等(apply_twice(lambda x: x + 1, 0), 2)


@_test.suite("条件语句测试")
class ConditionalTests:
    """条件语句单元测试"""

    def test_if_statement(self):
        """测试if语句"""
        x = 10
        if x > 5:
            result = True
        else:
            result = False
        断言为真(result)

    def test_elif_statement(self):
        """测试elif语句"""
        x = 0
        if x > 0:
            result = "positive"
        elif x < 0:
            result = "negative"
        else:
            result = "zero"
        断言等(result, "zero")


@_test.suite("循环语句测试")
class LoopTests:
    """循环语句单元测试"""

    def test_for_loop(self):
        """测试for循环"""
        result = 0
        for i in range(5):
            result += i
        断言等(result, 10)

    def test_while_loop(self):
        """测试while循环"""
        result = 0
        i = 0
        while i < 5:
            result += i
            i += 1
        断言等(result, 10)


@_test.suite("异常处理测试")
class ExceptionTests:
    """异常处理单元测试"""

    def test_try_except(self):
        """测试try-except"""
        try:
            x = 1 / 0
        except ZeroDivisionError:
            result = "caught"
        断言等(result, "caught")

    def test_raise_exception(self):
        """测试抛出异常"""
        def should_raise():
            raise ValueError("test")

        断言抛出(should_raise, ValueError)


def main():
    """运行单元测试"""
    print("言语言单元测试")
    print("=" * 70)

    report = _test.run()
    _test.print_summary(report)

    return report


if __name__ == "__main__":
    report = main()
    sys.exit(0 if report.failed == 0 and report.errors == 0 else 1)
