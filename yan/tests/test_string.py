#!/usr/bin/env python3
"""
言语言标准库测试 - String 模块
"""

from yan_test import *
from yan_assertions import *


@suite("String 模块测试")
class StringTests:

    @test("字符串长度测试")
    def test_length(self):
        """测试字符串长度"""
        from stdlib.string import 长度
        等(长度(""), 0)
        等(长度("hello"), 5)
        等(长度("你好"), 2)

    @test("字符串拼接测试")
    def test_concat(self):
        """测试字符串拼接"""
        from stdlib.string import 拼接
        等(拼接("hello", "world"), "helloworld")
        等(拼接("", "test"), "test")
        等(拼接("a", "b"), "ab")

    @test("字符串大写测试")
    def test_upper(self):
        """测试大写转换"""
        from stdlib.string import 大写
        等(大写("hello"), "HELLO")
        等(大写("Hello"), "HELLO")
        等(大写("heLLo"), "HELLO")

    @test("字符串小写测试")
    def test_lower(self):
        """测试小写转换"""
        from stdlib.string import 小写
        等(小写("HELLO"), "hello")
        等(小写("Hello"), "hello")
        等(小写("HeLLo"), "hello")

    @test("首字母大写测试")
    def test_capitalize(self):
        """测试首字母大写"""
        from stdlib.string import 首字母大写
        等(首字母大写("hello"), "Hello")
        等(首字母大写("hello world"), "Hello world")

    @test("去除空白测试")
    def test_strip(self):
        """测试去除空白"""
        from stdlib.string import 去空白
        等(去空白("  hello  "), "hello")
        等(去空白("\thello\n"), "hello")
        等(去空白("hello"), "hello")

    @test("字符串替换测试")
    def test_replace(self):
        """测试字符串替换"""
        from stdlib.string import 替换
        等(替换("hello world", "world", "python"), "hello python")
        等(替换("aaa", "a", "b"), "bbb")
        等(替换("hello", "x", "y"), "hello")

    @test("查找子字符串测试")
    def test_find(self):
        """测试查找子字符串"""
        from stdlib.string import 查找
        等(查找("hello world", "world"), 6)
        等(查找("hello world", "python"), -1)
        等(查找("hello", "l"), 2)

    @test("包含检查测试")
    def test_contains(self):
        """测试包含检查"""
        from stdlib.string import 包含
        为真(包含("hello world", "world"))
        为假(包含("hello world", "python"))
        为真(包含("hello", "l"))

    @test("开头检查测试")
    def test_startswith(self):
        """测试开头检查"""
        from stdlib.string import 开头
        为真(开头("hello world", "hello"))
        为假(开头("hello world", "world"))
        为真(开头("hello", "hel"))

    @test("结尾检查测试")
    def test_endswith(self):
        """测试结尾检查"""
        from stdlib.string import 结尾
        为真(结尾("hello world", "world"))
        为假(结尾("hello world", "hello"))
        为真(结尾("hello", "llo"))

    @test("分割字符串测试")
    def test_split(self):
        """测试字符串分割"""
        from stdlib.string import 分割
        等(分割("a,b,c", ","), ["a", "b", "c"])
        等(分割("hello", ","), ["hello"])

    @test("连接字符串测试")
    def test_join(self):
        """测试字符串连接"""
        from stdlib.string import 连接
        等(连接("-", ["a", "b", "c"]), "a-b-c")
        等(连接(" ", ["hello", "world"]), "hello world")

    @test("子字符串测试")
    def test_substring(self):
        """测试子字符串"""
        from stdlib.string import 子串
        等(子串("hello world", 0, 5), "hello")
        等(子串("hello world", 6, 11), "world")

    @test("字符串重复测试")
    def test_repeat(self):
        """测试字符串重复"""
        from stdlib.string import 重复
        等(重复("ab", 3), "ababab")
        等(重复("x", 1), "x")
        等(重复("test", 0), "")

    @test("统计子字符串测试")
    def test_count(self):
        """测试统计子字符串"""
        from stdlib.string import 统计
        等(统计("hello", "l"), 2)
        等(统计("hello", "x"), 0)
        等(统计("aaaa", "a"), 4)

    @test("反转字符串测试")
    def test_reverse(self):
        """测试反转字符串"""
        from stdlib.string import 反转
        等(反转("hello"), "olleh")
        等(反转("abc"), "cba")
        等(反转(""), "")

    @test("判断是否数字测试")
    def test_isdigit(self):
        """测试数字判断"""
        from stdlib.string import 是数字
        为真(是数字("123"))
        为真(是数字("0"))
        为假(是数字("12.3"))
        为假(是数字("hello"))

    @test("判断是否字母测试")
    def test_isalpha(self):
        """测试字母判断"""
        from stdlib.string import 是字母
        为真(是字母("hello"))
        为真(是字母("你好"))
        为假(是字母("hello123"))

    @test("数字转字符串测试")
    def test_to_string(self):
        """测试数字转字符串"""
        from stdlib.string import 转字符串
        等(转字符串(123), "123")
        等(转字符串(3.14), "3.14")


if __name__ == "__main__":
    report = run()
    print_summary(report)
