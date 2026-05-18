#!/usr/bin/env python3
"""
言语言标准库测试 - Collections 模块
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yan_test import *
from yan_assertions import *


@suite("Collections 模块测试")
class CollectionsTests:

    @test("列表去重测试")
    def test_distinct(self):
        """测试列表去重"""
        from stdlib.collections import 去重
        等(去重([1, 2, 2, 3, 3, 3]), [1, 2, 3])
        等(去重([1, 1, 1]), [1])
        等(去重([]), [])

    @test("列表反转测试")
    def test_reverse(self):
        """测试列表反转"""
        from stdlib.collections import 反转
        等(反转([1, 2, 3]), [3, 2, 1])
        等(反转(["a", "b", "c"]), ["c", "b", "a"])
        等(反转([]), [])

    @test("列表切片测试")
    def test_slice(self):
        """测试列表切片"""
        from stdlib.collections import 切片
        等(切片([0, 1, 2, 3, 4, 5], 1, 4), [1, 2, 3])
        等(切片([1, 2, 3], 0, 2), [1, 2])
        等(切片([1, 2, 3], 1, 1), [])

    @test("范围生成测试")
    def test_range(self):
        """测试范围生成"""
        from stdlib.collections import 范围
        等(范围(0, 5), [0, 1, 2, 3, 4])
        等(范围(1, 6), [1, 2, 3, 4, 5])
        等(范围(0, 10, 2), [0, 2, 4, 6, 8])

    @test("查找元素测试")
    def test_find(self):
        """测试查找元素"""
        from stdlib.collections import 查找
        等(查找([1, 2, 3, 4, 5], lambda x: x > 3), 4)
        等(查找([1, 2, 3], lambda x: x > 10), None)
        等(查找([], lambda x: x > 3), None)

    @test("查找所有匹配测试")
    def test_find_all(self):
        """测试查找所有匹配"""
        from stdlib.collections import 查找所有
        等(查找所有([1, 2, 3, 4, 5], lambda x: x > 2), [3, 4, 5])
        等(查找所有([1, 2, 3], lambda x: x > 10), [])

    @test("存在检查测试")
    def test_exists(self):
        """测试存在检查"""
        from stdlib.collections import 存在
        为真(存在([1, 2, 3, 4, 5], lambda x: x > 3))
        为假(存在([1, 2, 3], lambda x: x > 10))

    @test("全为真检查测试")
    def test_all(self):
        """测试全为真检查"""
        from stdlib.collections import 所有
        为真(所有([2, 4, 6], lambda x: x % 2 == 0))
        为假(所有([1, 2, 3], lambda x: x > 0))

    @test("列表排序测试")
    def test_sort(self):
        """测试列表排序"""
        from stdlib.collections import 排序
        等(排序([3, 1, 2], lambda a, b: a < b), [1, 2, 3])
        等(排序([3, 1, 2], lambda a, b: a > b), [3, 2, 1])

    @test("展平列表测试")
    def test_flatten(self):
        """测试展平列表"""
        from stdlib.collections import 展平
        等(展平([[1, 2], [3, 4]]), [1, 2, 3, 4])
        等(展平([[1], [2, [3]]]), [1, 2, [3]])

    @test("列表分组测试")
    def test_group(self):
        """测试列表分组"""
        from stdlib.collections import 分组
        等(分组(["apple", "banana", "cherry"], lambda s: len(s) > 5), {
            "false": ["apple"],
            "true": ["banana", "cherry"]
        })

    @test("集合交集测试")
    def test_intersection(self):
        """测试集合交集"""
        from stdlib.collections import 交集
        等(交集({"a": True, "b": True, "c": True}, {"b": True, "c": True, "d": True}), {"b": True, "c": True})

    @test("集合并集测试")
    def test_union(self):
        """测试集合并集"""
        from stdlib.collections import 并集
        等(并集({"a": True, "b": True}, {"b": True, "c": True}), {"a": True, "b": True, "c": True})

    @test("集合差集测试")
    def test_difference(self):
        """测试集合差集"""
        from stdlib.collections import 差集
        等(差集({"a": True, "b": True, "c": True}, {"b": True}), {"a": True, "c": True})

    @test("字典获取键测试")
    def test_dict_keys(self):
        """测试字典获取键"""
        from stdlib.collections import 取键
        等(取键({"a": 1, "b": 2}), ["a", "b"])

    @test("字典获取值测试")
    def test_dict_values(self):
        """测试字典获取值"""
        from stdlib.collections import 取值
        等(取值({"a": 1, "b": 2}), [1, 2])

    @test("字典长度测试")
    def test_dict_length(self):
        """测试字典长度"""
        from stdlib.collections import 典长
        等(典长({"a": 1, "b": 2}), 2)
        等(典长({}), 0)

    @test("字典过滤测试")
    def test_dict_filter(self):
        """测试字典过滤"""
        from stdlib.collections import 典滤
        等(典滤({"a": 1, "b": 2, "c": 3}, lambda v: v > 1), {"b": 2, "c": 3})

    @test("字典映射测试")
    def test_dict_map(self):
        """测试字典映射"""
        from stdlib.collections import 典映
        等(典映({"a": 1, "b": 2}, lambda v: v * 2), {"a": 2, "b": 4})


if __name__ == "__main__":
    report = run()
    print_summary(report)
