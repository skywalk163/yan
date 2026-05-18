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

# 导出所有符号
__all__ = [
    '等', '不等', '为真', '为假', '为空', '不为空', '在范围内',
    '是数', '是串', '是表', '是函', '是真', '是空', '引发异常'
]
