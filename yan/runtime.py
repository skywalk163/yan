"""
言语言运行时支持
"""

from functools import reduce
from typing import Any, Callable, List, Optional


# ============ 算术运算 ============

def _add(a, b): return a + b
def _sub(a, b): return a - b
def _mul(a, b): return a * b
def _div(a, b): return a / b
def _mod(a, b): return a % b
def _pow(a, b): return a ** b
def _abs(a): return abs(a)
def _neg(a): return -a


# ============ 比较运算 ============

def _gt(a, b): return a > b
def _lt(a, b): return a < b
def _eq(a, b): return a == b
def _ne(a, b): return a != b


# ============ 逻辑运算 ============

def _and(a, b): return a and b
def _or(a, b): return a or b
def _not(a): return not a


# ============ 范围生成 ============

def _range(n):
    """生成从1到n的列表"""
    return list(range(1, n + 1))


# ============ 列表操作 ============

def _list(*args): return list(args)
def _head(lst): return lst[0] if lst else None
def _tail(lst): return lst[1:] if len(lst) > 1 else []
def _nth(lst, n): return lst[n] if -len(lst) <= n < len(lst) else None
def _len(lst): return len(lst)
def _append(lst, item): return lst + [item]
def _concat(lst1, lst2): return lst1 + lst2
def _contains(lst, item): return item in lst
def _empty(lst): return len(lst) == 0


# ============ 高阶函数 ============

def _map(func_or_lst, lst_or_func=None):
    """映射：支持柯里化

    用法：
    - _map(func, lst) -> list(map(func, lst))
    - _map(lst)(func) -> list(map(func, lst))  # 管道形式
    """
    if lst_or_func is not None:
        # _map(func, lst)
        if callable(func_or_lst) and isinstance(lst_or_func, list):
            return list(map(func_or_lst, lst_or_func))
        # _map(lst, func) - 管道形式
        elif isinstance(func_or_lst, list) and callable(lst_or_func):
            return list(map(lst_or_func, func_or_lst))
        else:
            return list(map(func_or_lst, lst_or_func))
    else:
        # _map(func) 或 _map(lst)
        if callable(func_or_lst):
            # _map(func) -> 返回等待列表的函数
            return lambda lst: list(map(func_or_lst, lst))
        else:
            # _map(lst) -> 返回等待函数的函数（管道形式）
            return lambda func: list(map(func, func_or_lst))


def _filter(pred, lst=None):
    """过滤：支持柯里化"""
    if lst is None:
        return lambda x: list(filter(pred, x))
    return list(filter(pred, lst))


def _reduce(func_or_init, init_or_lst=None, lst=None):
    """归约：支持柯里化

    用法：
    - _reduce(func, init, lst) -> reduce(func, lst, init)
    - _reduce(func, init)(lst) -> reduce(func, lst, init)
    """
    if lst is not None:
        # _reduce(func, init, lst)
        return reduce(func_or_init, lst, init_or_lst)
    elif init_or_lst is not None:
        if isinstance(init_or_lst, list):
            # _reduce(func, lst) - 无初始值
            return reduce(func_or_init, init_or_lst)
        else:
            # _reduce(func, init) - 返回柯里化函数，等待列表
            return lambda x: reduce(func_or_init, x, init_or_lst)
    else:
        # _reduce(func) - 返回等待初始值和列表的函数
        # 但这种用法在言语言中不常见
        return lambda init, lst=None: (
            reduce(func_or_init, lst, init) if lst is not None
            else lambda x: reduce(func_or_init, x, init)
        )


# ============ 柯里化辅助 ============

def curry(func, arity):
    """将函数转为可柯里化形式"""
    def wrapper(*args):
        if len(args) >= arity:
            return func(*args[:arity])
        return curry(lambda *more: func(*args, *more), arity - len(args))
    return wrapper


# ============ 内置动词映射 ============

BUILTINS = {
    # 算术
    '加': (_add, 2),
    '减': (_sub, 2),
    '乘': (_mul, 2),
    '除': (_div, 2),
    '模': (_mod, 2),
    '幂': (_pow, 2),
    '绝对': (_abs, 1),
    '负': (_neg, 1),

    # 范围
    '范围': (_range, 1),

    # 列表
    '列': (_list, -1),
    '首': (_head, 1),
    '余': (_tail, 1),
    '入': (_nth, 2),
    '长': (_len, 1),
    '添': (_append, 2),
    '连': (_concat, 2),
    '含': (_contains, 2),
    '空': (_empty, 1),

    # 比较
    '大': (_gt, 2),
    '小': (_lt, 2),
    '等': (_eq, 2),
    '不等': (_ne, 2),

    # 逻辑
    '且': (_and, 2),
    '或': (_or, 2),
    '非': (_not, 1),

    # 高阶
    '皆': (_map, 2),
    '只': (_filter, 2),
    '归': (_reduce, 3),

    # I/O
    '印': (print, 1),
}
