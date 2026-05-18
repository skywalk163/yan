#!/usr/bin/env python3
"""
言语言断言库
"""

# 基础断言
def 等(actual, expected, message=None):
    """断言两个值相等"""
    if message is None:
        message = f"断言失败: {actual} != {expected}"
    assert actual == expected, message

def 不等(actual, expected, message=None):
    """断言两个值不相等"""
    if message is None:
        message = f"断言失败: {actual} == {expected}"
    assert actual != expected, message

def 为真(value, message=None):
    """断言值为真"""
    if message is None:
        message = f"断言失败: {value} 不为真"
    assert bool(value), message

def 为假(value, message=None):
    """断言值为假"""
    if message is None:
        message = f"断言失败: {value} 不为假"
    assert not bool(value), message

def 为空(value, message=None):
    """断言值为空（None, [], {}, ""）"""
    if message is None:
        message = f"断言失败: {value} 不为空"
    
    if value is None:
        return
    if isinstance(value, (list, tuple, str, dict)):
        assert len(value) == 0, message
    else:
        assert False, message

def 不为空(value, message=None):
    """断言值不为空"""
    if message is None:
        message = f"断言失败: {value} 为空"
    
    if value is None:
        assert False, message
    if isinstance(value, (list, tuple, str, dict)):
        assert len(value) > 0, message

def 在范围内(value, min_val, max_val, message=None):
    """断言值在范围内"""
    if message is None:
        message = f"断言失败: {value} 不在 [{min_val}, {max_val}] 范围内"
    assert min_val <= value <= max_val, message

# 类型断言
def 是数(value, message=None):
    """断言值是数字"""
    if message is None:
        message = f"断言失败: {value} 不是数字"
    assert isinstance(value, (int, float)), message

def 是串(value, message=None):
    """断言值是字符串"""
    if message is None:
        message = f"断言失败: {value} 不是字符串"
    assert isinstance(value, str), message

def 是表(value, message=None):
    """断言值是列表"""
    if message is None:
        message = f"断言失败: {value} 不是列表"
    assert isinstance(value, list), message

def 是函(value, message=None):
    """断言值是函数"""
    if message is None:
        message = f"断言失败: {value} 不是函数"
    assert callable(value), message

def 是真(value, message=None):
    """断言值是 True"""
    if message is None:
        message = f"断言失败: {value} 不是 True"
    assert value is True, message

def 是空(value, message=None):
    """断言值是 None"""
    if message is None:
        message = f"断言失败: {value} 不是 None"
    assert value is None, message

# 异常断言
def 引发异常(func, *args, exception_type=Exception, message=None, **kwargs):
    """断言函数会引发异常"""
    try:
        func(*args, **kwargs)
        if message is None:
            message = f"断言失败: 期望 {exception_type.__name__} 但未抛出"
        assert False, message
    except exception_type:
        pass
    except Exception as e:
        if message is None:
            message = f"断言失败: 期望 {exception_type.__name__} 但得到 {type(e).__name__}: {e}"
        assert False, message

# 集合断言
def 包含(container, item, message=None):
    """断言容器包含指定元素"""
    if message is None:
        message = f"断言失败: {container} 不包含 {item}"
    assert item in container, message

def 不包含(container, item, message=None):
    """断言容器不包含指定元素"""
    if message is None:
        message = f"断言失败: {container} 包含 {item}"
    assert item not in container, message

# 字符串断言
def 串包含(string, substring, message=None):
    """断言字符串包含子串"""
    if message is None:
        message = f"断言失败: '{string}' 不包含 '{substring}'"
    assert substring in string, message

def 串开始于(string, prefix, message=None):
    """断言字符串以指定前缀开头"""
    if message is None:
        message = f"断言失败: '{string}' 不以 '{prefix}' 开头"
    assert string.startswith(prefix), message

def 串结束于(string, suffix, message=None):
    """断言字符串以指定后缀结尾"""
    if message is None:
        message = f"断言失败: '{string}' 不以 '{suffix}' 结尾"
    assert string.endswith(suffix), message

# 数值断言
def 接近(actual, expected, tolerance=0.001, message=None):
    """断言两个数值接近（在容差范围内）"""
    if message is None:
        message = f"断言失败: {actual} 与 {expected} 不接近（容差: {tolerance}）"
    assert abs(actual - expected) <= tolerance, message

def 大于(actual, expected, message=None):
    """断言实际值大于期望值"""
    if message is None:
        message = f"断言失败: {actual} 不大于 {expected}"
    assert actual > expected, message

def 小于(actual, expected, message=None):
    """断言实际值小于期望值"""
    if message is None:
        message = f"断言失败: {actual} 不小于 {expected}"
    assert actual < expected, message

def 大于等于(actual, expected, message=None):
    """断言实际值大于等于期望值"""
    if message is None:
        message = f"断言失败: {actual} 不大于等于 {expected}"
    assert actual >= expected, message

def 小于等于(actual, expected, message=None):
    """断言实际值小于等于期望值"""
    if message is None:
        message = f"断言失败: {actual} 不小于等于 {expected}"
    assert actual <= expected, message

# 列表断言
def 列表长度(list_, length, message=None):
    """断言列表长度"""
    if message is None:
        message = f"断言失败: 列表长度为 {len(list_)}，期望 {length}"
    assert len(list_) == length, message

def 列表相等(list1, list2, message=None):
    """断言两个列表相等（元素顺序和值都相等）"""
    if message is None:
        message = f"断言失败: {list1} != {list2}"
    assert list1 == list2, message

# 字典断言
def 字典包含键(dict_, key, message=None):
    """断言字典包含指定键"""
    if message is None:
        message = f"断言失败: 字典不包含键 '{key}'"
    assert key in dict_, message

def 字典包含值(dict_, value, message=None):
    """断言字典包含指定值"""
    if message is None:
        message = f"断言失败: 字典不包含值 {value}"
    assert value in dict_.values(), message

# 对象断言
def 有属性(obj, attr_name, message=None):
    """断言对象有指定属性"""
    if message is None:
        message = f"断言失败: 对象没有属性 '{attr_name}'"
    assert hasattr(obj, attr_name), message

def 方法返回(obj, method_name, expected, *args, message=None, **kwargs):
    """断言对象方法返回期望值"""
    method = getattr(obj, method_name)
    result = method(*args, **kwargs)
    if message is None:
        message = f"断言失败: {method_name}() 返回 {result}，期望 {expected}"
    assert result == expected, message

# 导出所有符号
__all__ = [
    # 基础断言
    '等', '不等', '为真', '为假', '为空', '不为空', '在范围内',
    # 类型断言
    '是数', '是串', '是表', '是函', '是真', '是空',
    # 异常断言
    '引发异常',
    # 集合断言
    '包含', '不包含',
    # 字符串断言
    '串包含', '串开始于', '串结束于',
    # 数值断言
    '接近', '大于', '小于', '大于等于', '小于等于',
    # 列表断言
    '列表长度', '列表相等',
    # 字典断言
    '字典包含键', '字典包含值',
    # 对象断言
    '有属性', '方法返回'
]
