#!/usr/bin/env python3
"""
言语言断言库 v2

提供丰富的断言函数，支持中文API
"""

import re
from typing import Any, Callable, List, Optional, Type, Union


class AssertionError(Exception):
    """断言错误"""
    pass


class YanAssertion:
    """断言工具类"""
    
    @staticmethod
    def fail(message: str = None):
        """无条件失败"""
        raise AssertionError(message or "断言失败")
    
    @staticmethod
    def diff(actual: Any, expected: Any, path: str = "") -> List[str]:
        """深度比较，返回差异列表"""
        diffs = []
        
        if type(actual) != type(expected):
            diffs.append(f"{path}: 类型不匹配 - 实际: {type(actual).__name__}, 期望: {type(expected).__name__}")
            return diffs
        
        if isinstance(actual, dict):
            all_keys = set(actual.keys()) | set(expected.keys())
            for key in all_keys:
                key_path = f"{path}.{key}" if path else key
                if key not in actual:
                    diffs.append(f"{key_path}: 缺少键")
                elif key not in expected:
                    diffs.append(f"{key_path}: 多余键")
                else:
                    diffs.extend(YanAssertion.diff(actual[key], expected[key], key_path))
        elif isinstance(actual, list):
            if len(actual) != len(expected):
                diffs.append(f"{path}: 列表长度不匹配 - 实际: {len(actual)}, 期望: {len(expected)}")
            for i, (a, e) in enumerate(zip(actual, expected)):
                diffs.extend(YanAssertion.diff(a, e, f"{path}[{i}]"))
        else:
            if actual != expected:
                diffs.append(f"{path}: 值不匹配 - 实际: {actual}, 期望: {expected}")
        
        return diffs


def 等(actual: Any, expected: Any, message: str = None):
    """断言两个值相等"""
    if actual == expected:
        return
    diffs = YanAssertion.diff(actual, expected)
    msg = message or f"断言失败: {actual} != {expected}"
    if diffs:
        msg += "\n差异:\n  " + "\n  ".join(diffs)
    raise AssertionError(msg)


def 不等(actual: Any, expected: Any, message: str = None):
    """断言两个值不相等"""
    if actual != expected:
        return
    raise AssertionError(message or f"断言失败: {actual} == {expected}")


def 为真(value: Any, message: str = None):
    """断言值为真"""
    if bool(value):
        return
    raise AssertionError(message or f"断言失败: {value} 不为真")


def 为假(value: Any, message: str = None):
    """断言值为假"""
    if not bool(value):
        return
    raise AssertionError(message or f"断言失败: {value} 不为假")


def 为空(value: Any, message: str = None):
    """断言值为空（None, [], {}, ""）"""
    if value is None:
        return
    if isinstance(value, (list, tuple, str, dict, set)):
        if len(value) == 0:
            return
    raise AssertionError(message or f"断言失败: {value} 不为空")


def 不为空(value: Any, message: str = None):
    """断言值不为空"""
    if value is None:
        raise AssertionError(message or f"断言失败: {value} 为空")
    if isinstance(value, (list, tuple, str, dict, set)):
        if len(value) > 0:
            return
        raise AssertionError(message or f"断言失败: {value} 为空")
    raise AssertionError(message or f"断言失败: {value} 为空")


def 在范围内(value: Any, min_val: Any, max_val: Any, message: str = None):
    """断言值在范围内"""
    if min_val <= value <= max_val:
        return
    raise AssertionError(message or f"断言失败: {value} 不在 [{min_val}, {max_val}] 范围内")


def 接近(actual: float, expected: float, tolerance: float = 0.001, message: str = None):
    """断言两个数值接近（在容差范围内）"""
    if abs(actual - expected) <= tolerance:
        return
    raise AssertionError(message or f"断言失败: {actual} 与 {expected} 不接近（容差: {tolerance}）")


def 大于(actual: Any, expected: Any, message: str = None):
    """断言实际值大于期望值"""
    if actual > expected:
        return
    raise AssertionError(message or f"断言失败: {actual} 不大于 {expected}")


def 小于(actual: Any, expected: Any, message: str = None):
    """断言实际值小于期望值"""
    if actual < expected:
        return
    raise AssertionError(message or f"断言失败: {actual} 不小于 {expected}")


def 大于等于(actual: Any, expected: Any, message: str = None):
    """断言实际值大于等于期望值"""
    if actual >= expected:
        return
    raise AssertionError(message or f"断言失败: {actual} 不大于等于 {expected}")


def 小于等于(actual: Any, expected: Any, message: str = None):
    """断言实际值小于等于期望值"""
    if actual <= expected:
        return
    raise AssertionError(message or f"断言失败: {actual} 不小于等于 {expected}")


def 是数(value: Any, message: str = None):
    """断言值是数字（int或float）"""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return
    raise AssertionError(message or f"断言失败: {value} 不是数字")


def 是整数(value: Any, message: str = None):
    """断言值是整数"""
    if isinstance(value, int) and not isinstance(value, bool):
        return
    raise AssertionError(message or f"断言失败: {value} 不是整数")


def 是浮点数(value: Any, message: str = None):
    """断言值是浮点数"""
    if isinstance(value, float):
        return
    raise AssertionError(message or f"断言失败: {value} 不是浮点数")


def 是串(value: Any, message: str = None):
    """断言值是字符串"""
    if isinstance(value, str):
        return
    raise AssertionError(message or f"断言失败: {value} 不是字符串")


def 是布尔(value: Any, message: str = None):
    """断言值是布尔值"""
    if isinstance(value, bool):
        return
    raise AssertionError(message or f"断言失败: {value} 不是布尔值")


def 是表(value: Any, message: str = None):
    """断言值是列表"""
    if isinstance(value, list):
        return
    raise AssertionError(message or f"断言失败: {value} 不是列表")


def 是元组(value: Any, message: str = None):
    """断言值是元组"""
    if isinstance(value, tuple):
        return
    raise AssertionError(message or f"断言失败: {value} 不是元组")


def 是集合(value: Any, message: str = None):
    """断言值是集合"""
    if isinstance(value, (set, frozenset)):
        return
    raise AssertionError(message or f"断言失败: {value} 不是集合")


def 是字典(value: Any, message: str = None):
    """断言值是字典"""
    if isinstance(value, dict):
        return
    raise AssertionError(message or f"断言失败: {value} 不是字典")


def 是函(value: Any, message: str = None):
    """断言值是函数"""
    if callable(value):
        return
    raise AssertionError(message or f"断言失败: {value} 不是函数")


def 是真(value: Any, message: str = None):
    """断言值是 True"""
    if value is True:
        return
    raise AssertionError(message or f"断言失败: {value} 不是 True")


def 是假(value: Any, message: str = None):
    """断言值是 False"""
    if value is False:
        return
    raise AssertionError(message or f"断言失败: {value} 不是 False")


def 是空(value: Any, message: str = None):
    """断言值是 None"""
    if value is None:
        return
    raise AssertionError(message or f"断言失败: {value} 不是 None")


def 包含(container: Any, item: Any, message: str = None):
    """断言容器包含指定元素"""
    if item in container:
        return
    raise AssertionError(message or f"断言失败: {container} 不包含 {item}")


def 不包含(container: Any, item: Any, message: str = None):
    """断言容器不包含指定元素"""
    if item not in container:
        return
    raise AssertionError(message or f"断言失败: {container} 包含 {item}")


def 包含所有(container: Any, items: List[Any], message: str = None):
    """断言容器包含所有指定元素"""
    missing = [item for item in items if item not in container]
    if not missing:
        return
    raise AssertionError(message or f"断言失败: {container} 缺少 {missing}")


def 包含任意(container: Any, items: List[Any], message: str = None):
    """断言容器包含任意一个指定元素"""
    if any(item in container for item in items):
        return
    raise AssertionError(message or f"断言失败: {container} 不包含任何 {items}")


def 串包含(string: str, substring: str, message: str = None):
    """断言字符串包含子串"""
    if substring in string:
        return
    raise AssertionError(message or f"断言失败: '{string}' 不包含 '{substring}'")


def 串不包含(string: str, substring: str, message: str = None):
    """断言字符串不包含子串"""
    if substring not in string:
        return
    raise AssertionError(message or f"断言失败: '{string}' 包含 '{substring}'")


def 串开始于(string: str, prefix: str, message: str = None):
    """断言字符串以指定前缀开头"""
    if string.startswith(prefix):
        return
    raise AssertionError(message or f"断言失败: '{string}' 不以 '{prefix}' 开头")


def 串结束于(string: str, suffix: str, message: str = None):
    """断言字符串以指定后缀结尾"""
    if string.endswith(suffix):
        return
    raise AssertionError(message or f"断言失败: '{string}' 不以 '{suffix}' 结尾")


def 串匹配(string: str, pattern: str, message: str = None):
    """断言字符串匹配正则表达式"""
    if re.match(pattern, string):
        return
    raise AssertionError(message or f"断言失败: '{string}' 不匹配模式 '{pattern}'")


def 串搜索(string: str, pattern: str, message: str = None):
    """断言字符串搜索到匹配项"""
    if re.search(pattern, string):
        return
    raise AssertionError(message or f"断言失败: '{string}' 中找不到模式 '{pattern}'")


def 串长度(string: str, length: int, message: str = None):
    """断言字符串长度"""
    if len(string) == length:
        return
    raise AssertionError(message or f"断言失败: 字符串长度为 {len(string)}，期望 {length}")


def 串长度范围(string: str, min_len: int, max_len: int, message: str = None):
    """断言字符串长度在范围内"""
    if min_len <= len(string) <= max_len:
        return
    raise AssertionError(message or f"断言失败: 字符串长度为 {len(string)}，期望 [{min_len}, {max_len}]")


def 列表长度(list_: list, length: int, message: str = None):
    """断言列表长度"""
    if len(list_) == length:
        return
    raise AssertionError(message or f"断言失败: 列表长度为 {len(list_)}，期望 {length}")


def 列表为空(list_: list, message: str = None):
    """断言列表为空"""
    if len(list_) == 0:
        return
    raise AssertionError(message or f"断言失败: 列表长度为 {len(list_)}，不为空")


def 列表非空(list_: list, message: str = None):
    """断言列表非空"""
    if len(list_) > 0:
        return
    raise AssertionError(message or f"断言失败: 列表为空")


def 列表相等(list1: list, list2: list, message: str = None):
    """断言两个列表相等（元素顺序和值都相等）"""
    if list1 == list2:
        return
    raise AssertionError(message or f"断言失败: {list1} != {list2}")


def 列表无序相等(list1: list, list2: list, message: str = None):
    """断言两个列表无序相等"""
    if sorted(list1) == sorted(list2):
        return
    raise AssertionError(message or f"断言失败: {list1} 和 {list2} 无序不相等")


def 列表包含(list_: list, item: Any, message: str = None):
    """断言列表包含元素"""
    if item in list_:
        return
    raise AssertionError(message or f"断言失败: 列表 {list_} 不包含 {item}")


def 字典包含键(dict_: dict, key: Any, message: str = None):
    """断言字典包含指定键"""
    if key in dict_:
        return
    raise AssertionError(message or f"断言失败: 字典不包含键 '{key}'")


def 字典不包含键(dict_: dict, key: Any, message: str = None):
    """断言字典不包含指定键"""
    if key not in dict_:
        return
    raise AssertionError(message or f"断言失败: 字典包含键 '{key}'")


def 字典包含值(dict_: dict, value: Any, message: str = None):
    """断言字典包含指定值"""
    if value in dict_.values():
        return
    raise AssertionError(message or f"断言失败: 字典不包含值 {value}")


def 字典相等(dict1: dict, dict2: dict, message: str = None):
    """断言两个字典相等"""
    if dict1 == dict2:
        return
    diffs = YanAssertion.diff(dict1, dict2)
    msg = message or f"断言失败: {dict1} != {dict2}"
    if diffs:
        msg += "\n差异:\n  " + "\n  ".join(diffs)
    raise AssertionError(msg)


def 有属性(obj: Any, attr_name: str, message: str = None):
    """断言对象有指定属性"""
    if hasattr(obj, attr_name):
        return
    raise AssertionError(message or f"断言失败: 对象没有属性 '{attr_name}'")


def 无属性(obj: Any, attr_name: str, message: str = None):
    """断言对象没有指定属性"""
    if not hasattr(obj, attr_name):
        return
    raise AssertionError(message or f"断言失败: 对象有属性 '{attr_name}'")


def 方法返回(obj: Any, method_name: str, expected: Any, *args, message: str = None, **kwargs):
    """断言对象方法返回期望值"""
    method = getattr(obj, method_name)
    result = method(*args, **kwargs)
    if result == expected:
        return
    raise AssertionError(message or f"断言失败: {method_name}() 返回 {result}，期望 {expected}")


def 引发异常(func: Callable, exception_type: Type[Exception] = Exception, 
             message: str = None, **kwargs):
    """断言函数会引发异常"""
    try:
        func(**kwargs)
        raise AssertionError(message or f"断言失败: 期望 {exception_type.__name__} 但未抛出")
    except exception_type:
        pass
    except Exception as e:
        raise AssertionError(message or f"断言失败: 期望 {exception_type.__name__} 但得到 {type(e).__name__}: {e}")


def 不引发异常(func: Callable, message: str = None, **kwargs):
    """断言函数不引发异常"""
    try:
        func(**kwargs)
    except Exception as e:
        raise AssertionError(message or f"断言失败: 不应抛出异常，但抛出了 {type(e).__name__}: {e}")


def 引发异常匹配(func: Callable, pattern: str, message: str = None, **kwargs):
    """断言函数引发的异常消息匹配正则表达式"""
    try:
        func(**kwargs)
        raise AssertionError(message or f"断言失败: 期望异常但未抛出")
    except Exception as e:
        if re.search(pattern, str(e)):
            return
        raise AssertionError(message or f"断言失败: 异常消息 '{e}' 不匹配模式 '{pattern}'")


def 全部通过(items: List[bool], message: str = None):
    """断言所有项都为真"""
    if all(items):
        return
    failed_indices = [i for i, item in enumerate(items) if not item]
    raise AssertionError(message or f"断言失败: 以下项未通过: {failed_indices}")


def 任意通过(items: List[bool], message: str = None):
    """断言任意一项为真"""
    if any(items):
        return
    raise AssertionError(message or f"断言失败: 没有项通过")


def 深度相等(actual: Any, expected: Any, message: str = None):
    """深度相等断言"""
    if actual == expected:
        return
    diffs = YanAssertion.diff(actual, expected)
    msg = message or "断言失败: 对象不相等"
    if diffs:
        msg += "\n差异:\n  " + "\n  ".join(diffs)
    raise AssertionError(msg)


def 断言等(actual: Any, expected: Any, message: str = None):
    """断言两个值相等（别名）"""
    return 等(actual, expected, message)


def 断言不等(actual: Any, expected: Any, message: str = None):
    """断言两个值不相等（别名）"""
    return 不等(actual, expected, message)


def 断言为真(value: Any, message: str = None):
    """断言值为真（别名）"""
    return 为真(value, message)


def 断言为假(value: Any, message: str = None):
    """断言值为假（别名）"""
    return 为假(value, message)


def 断言抛出(func: Callable, exception_type: Type[Exception] = Exception, 
              message: str = None, **kwargs):
    """断言函数抛出异常（别名）"""
    return 引发异常(func, exception_type, message, **kwargs)


__all__ = [
    # 基础断言
    '等', '不等', '为真', '为假', '为空', '不为空', '在范围内', '接近',
    # 比较断言
    '大于', '小于', '大于等于', '小于等于',
    # 类型断言
    '是数', '是整数', '是浮点数', '是串', '是布尔', '是表', '是元组', '是集合', '是字典', '是函', '是真', '是假', '是空',
    # 异常断言
    '引发异常', '不引发异常', '引发异常匹配',
    # 集合断言
    '包含', '不包含', '包含所有', '包含任意',
    # 字符串断言
    '串包含', '串不包含', '串开始于', '串结束于', '串匹配', '串搜索', '串长度', '串长度范围',
    # 列表断言
    '列表长度', '列表为空', '列表非空', '列表相等', '列表无序相等', '列表包含',
    # 字典断言
    '字典包含键', '字典不包含键', '字典包含值', '字典相等',
    # 对象断言
    '有属性', '无属性', '方法返回',
    # 组合断言
    '全部通过', '任意通过',
    # 深度比较
    '深度相等',
    # 别名
    '断言等', '断言不等', '断言为真', '断言为假', '断言抛出',
    # 工具类
    'YanAssertion', 'AssertionError'
]
