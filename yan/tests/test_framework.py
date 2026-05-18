#!/usr/bin/env python3
"""
测试框架功能验证测试
"""

import sys
sys.path.insert(0, '../')

from yan_test import suite, test, run, print_summary
from yan_assertions import *

@suite("基础断言测试")
class BasicAssertionsTest:
    @test("等断言")
    def test_equal(self):
        等(1, 1)
        等("hello", "hello")
        等([1, 2, 3], [1, 2, 3])
    
    @test("不等断言")
    def test_not_equal(self):
        不等(1, 2)
        不等("hello", "world")
    
    @test("为真断言")
    def test_true(self):
        为真(True)
        为真(1)
        为真("non-empty")
        为真([1])
    
    @test("为假断言")
    def test_false(self):
        为假(False)
        为假(0)
        为假("")
        为假([])

@suite("集合断言测试")
class CollectionAssertionsTest:
    @test("包含断言")
    def test_contains(self):
        包含([1, 2, 3], 2)
        包含("hello", "ell")
        包含({"a": 1}, "a")
    
    @test("不包含断言")
    def test_not_contains(self):
        不包含([1, 2, 3], 4)
        不包含("hello", "xyz")
    
    @test("为空断言")
    def test_empty(self):
        为空(None)
        为空([])
        为空({})
        为空("")
    
    @test("不为空断言")
    def test_not_empty(self):
        不为空([1])
        不为空({"a": 1})
        不为空("hello")

@suite("字符串断言测试")
class StringAssertionsTest:
    @test("串包含断言")
    def test_string_contains(self):
        串包含("hello world", "world")
        串包含("言语言", "语言")
    
    @test("串开始于断言")
    def test_starts_with(self):
        串开始于("hello world", "hello")
        串开始于("言语言测试", "言")
    
    @test("串结束于断言")
    def test_ends_with(self):
        串结束于("hello world", "world")
        串结束于("言语言测试", "试")

@suite("数值断言测试")
class NumericAssertionsTest:
    @test("大于断言")
    def test_greater_than(self):
        大于(5, 3)
        大于(10.5, 10.0)
    
    @test("小于断言")
    def test_less_than(self):
        小于(3, 5)
        小于(9.5, 10.0)
    
    @test("接近断言")
    def test_close_to(self):
        接近(3.14159, 3.14, 0.01)
        接近(1.0001, 1.0, 0.001)
    
    @test("在范围内断言")
    def test_in_range(self):
        在范围内(5, 1, 10)
        在范围内(0, -1, 1)

@suite("类型断言测试")
class TypeAssertionsTest:
    @test("类型检查断言")
    def test_type_checks(self):
        是数(42)
        是串("hello")
        是表([1, 2, 3])
        是函(lambda: None)

@suite("异常断言测试")
class ExceptionAssertionsTest:
    @test("引发异常断言")
    def test_raises_exception(self):
        def bad_func():
            raise ValueError("test error")
        
        引发异常(bad_func)
        引发异常(lambda: 1 / 0, exception_type=ZeroDivisionError)

if __name__ == '__main__':
    report = run()
    print_summary(report)
    
    # 测试生成不同格式的报告
    from yan_test import generate_json_report, generate_html_report, generate_junit_report
    
    # 生成 JSON 报告
    json_report = generate_json_report(report, 'test_report.json')
    print("\nJSON 报告已生成")
    
    # 生成 HTML 报告
    html_report = generate_html_report(report, 'test_report.html')
    print("HTML 报告已生成")
    
    # 生成 JUnit 报告
    junit_report = generate_junit_report(report, 'test_report.xml')
    print("JUnit 报告已生成")
    
    # 返回退出码
    exit(1 if report['failed'] > 0 else 0)
