"""
言语言运行时支持
"""

import math
import random
import os
import time as _time_module
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
def _gte(a, b): return a >= b
def _lt(a, b): return a < b
def _lte(a, b): return a <= b
def _ne(a, b): return a != b
def _eq(a, b): return a == b


# ============ 逻辑运算 ============

def _and(a, b): return a and b
def _or(a, b): return a or b
def _not(a): return not a


# ============ 表达式求值 ============

def _eval(expr_str):
    """求值算术表达式字符串，支持加减乘除和括号"""
    import re
    import operator as op

    def tokenize(s):
        """将表达式字符串分解为token"""
        tokens = []
        i = 0
        s = s.strip()
        while i < len(s):
            if s[i].isspace():
                i += 1
            elif s[i].isdigit() or (s[i] == '-' and (not tokens or tokens[-1] in {'(', '+', '-', '*', '/'})):
                j = i
                if s[i] == '-':
                    j += 1
                while j < len(s) and (s[j].isdigit() or s[j] == '.'):
                    j += 1
                tokens.append(('NUM', float(s[i:j]) if '.' in s[i:j] else int(s[i:j])))
                i = j
            elif s[i] in '+-*/()':
                tokens.append(('OP', s[i]))
                i += 1
            else:
                i += 1
        return tokens

    def parse(tokens):
        """递归下降解析器"""
        pos = [0]

        def peek():
            return tokens[pos[0]] if pos[0] < len(tokens) else None

        def consume():
            pos[0] += 1
            return tokens[pos[0] - 1]

        def parse_expr():
            return parse_add_sub()

        def parse_add_sub():
            left = parse_mul_div()
            while True:
                tok = peek()
                if tok and tok[0] == 'OP' and tok[1] in '+-':
                    op_tok = consume()
                    right = parse_mul_div()
                    if op_tok[1] == '+':
                        left = left + right
                    else:
                        left = left - right
                else:
                    break
            return left

        def parse_mul_div():
            left = parse_unary()
            while True:
                tok = peek()
                if tok and tok[0] == 'OP' and tok[1] in '*/':
                    op_tok = consume()
                    right = parse_unary()
                    if op_tok[1] == '*':
                        left = left * right
                    else:
                        left = left / right if right != 0 else 0
                else:
                    break
            return left

        def parse_unary():
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] == '-':
                consume()
                return -parse_unary()
            return parse_primary()

        def parse_primary():
            tok = peek()
            if not tok:
                return 0
            if tok[0] == 'NUM':
                consume()
                return tok[1]
            if tok[0] == 'OP' and tok[1] == '(':
                consume()  # (
                result = parse_expr()
                tok = peek()
                if tok and tok[0] == 'OP' and tok[1] == ')':
                    consume()  # )
                return result
            return 0

        return parse_expr()

    tokens = tokenize(expr_str)
    if not tokens:
        return 0
    return parse(tokens)


# ============ 范围生成 ============

def _range(n):
    """生成从1到n的列表"""
    return list(range(1, n + 1))


# ============ 列表操作 ============

def _list(*args): return list(args)
def _head(lst): return lst[0] if lst else None
def _tail(lst): return lst[1:] if len(lst) > 1 else []
def _nth(lst, n): return lst[n] if -len(lst) <= n < len(lst) else None
def _contains(lst, item): return item in lst
def _set_nth(lst, n, value):
    """设置列表中指定索引的值"""
    if -len(lst) <= n < len(lst):
        lst[n] = value
        return lst
    return None
def _len(lst): return len(lst)
def _append(lst, item): 
    lst.append(item)
    return lst
def _concat(*args):
    """连接多个参数，支持任意数量的参数"""
    if len(args) == 0:
        return ""
    if len(args) == 1:
        return args[0]
    
    # 检查是否有字符串
    has_string = any(isinstance(arg, str) for arg in args)
    
    if has_string:
        return ''.join(str(arg) for arg in args)
    
    # 都是列表
    result = []
    for arg in args:
        result.extend(arg)
    return result
def _contains(lst, item): return item in lst
def _empty(lst): return len(lst) == 0

# 新增列表操作函数
def _reverse(lst): return list(reversed(lst))
def _sort(lst): return sorted(lst)
def _max(lst): return max(lst) if lst else None
def _min(lst): return min(lst) if lst else None
def _sum(lst): return sum(lst)
def _count(lst, item): return lst.count(item)


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


# ============ 字典操作 ============

def _dict(*args):
    """创建字典：典 'key1' val1 'key2' val2 或 典 key1 val1 key2 val2"""
    d = {}
    for i in range(0, len(args), 2):
        if i + 1 < len(args):
            key = args[i]
            # 如果键不是字符串，将其转换为字符串
            if not isinstance(key, str):
                key = str(key)
            d[key] = args[i + 1]
    return d

def _keys(d): return list(d.keys())
def _values(d): return list(d.values())
def _items(d): return list(d.items())
def _get(d, key):
    """获取字典中指定键的值"""
    if isinstance(key, str) and key in d:
        return d[key]
    return None
def _delkey(d, key):
    if key in d:
        del d[key]
    return d

# 字典操作
DICT_BUILTINS = {
    '典': (_dict, -1),
    '键': (_keys, 1),
    '值': (_get, 2),
    '项': (_items, 1),
    '删键': (_delkey, 2),
}


# ============ I/O 辅助函数 ============

def _read_char():
    """读取单个字符"""
    import sys
    try:
        import msvcrt
        # Windows 系统
        return msvcrt.getch().decode('utf-8', errors='ignore')
    except ImportError:
        # Unix 系统
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


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
        '求值': (_eval, 1),
    '首': (_head, 1),
    '余': (_tail, 1),
    '取': (_nth, 2),
    '设': (_set_nth, 3),
    '长': (_len, 1),
    '添': (_append, 2),
    '连': (_concat, 2),
    '含': (_contains, 2),
    '空': (_empty, 1),
    # 新增列表操作
    '反': (_reverse, 1),
    '排': (_sort, 1),
    '最大': (_max, 1),
    '最小': (_min, 1),
    '求和': (_sum, 1),
    '计数': (_count, 2),

    # 比较
    '大': (_gt, 2),
    '大于': (_gt, 2),
    '大等于': (_gte, 2),
    '小': (_lt, 2),
    '小于': (_lt, 2),
    '小等于': (_lte, 2),
    '不等于': (_ne, 2),
    '等': (_eq, 2),
    '等于': (_eq, 2),
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
    '读行': (input, 0),  # 读取一行输入
    '行': (input, 0),  # 向后兼容
    '读': (_read_char, 0),  # 读取单个字符
}


# ============ 数学库 ============

def _sin(x): return math.sin(x)
def _cos(x): return math.cos(x)
def _tan(x): return math.tan(x)
def _asin(x): return math.asin(x)
def _acos(x): return math.acos(x)
def _atan(x): return math.atan(x)
def _exp(x): return math.exp(x)
def _log(x): return math.log(x)
def _log10(x): return math.log10(x)
def _sqrt(x): return math.sqrt(x)
def _floor(x): return math.floor(x)
def _ceil(x): return math.ceil(x)
def _round(x): return round(x)
def _random(): return random.random()
def _randint(a, b): return random.randint(a, b)
def _pi(): return math.pi
def _e(): return math.e

# 数学库扩展
MATH_BUILTINS = {
    '正弦': (_sin, 1),
    '余弦': (_cos, 1),
    '正切': (_tan, 1),
    '反正弦': (_asin, 1),
    '反余弦': (_acos, 1),
    '反正切': (_atan, 1),
    '指数': (_exp, 1),
    '对数': (_log, 1),
    '对数10': (_log10, 1),
    '开方': (_sqrt, 1),
    '取整': (_floor, 1),
    '进位': (_ceil, 1),
    '四舍五入': (_round, 1),
    '随机': (_random, 0),
    '随机整数': (_randint, 2),
    '圆周率': (_pi, 0),
    '自然常数': (_e, 0),
}


# ============ 字符串库 ============

def _strlen(s): return len(s)
def _strcat(a, b): return str(a) + str(b)
def _strsplit(s, sep): return s.split(sep)
def _strreplace(s, old, new): return s.replace(old, new)
def _strslice(s, start, end): return s[start:end]
def _strlower(s): return s.lower()
def _strupper(s): return s.upper()
def _strfind(s, sub): return s.find(sub)
def _strcontains(s, sub): return sub in s
def _strstrip(s): return s.strip()
def _strstartswith(s, prefix): return s.startswith(prefix)
def _strendswith(s, suffix): return s.endswith(suffix)

STRING_BUILTINS = {
    '长度': (_strlen, 1),
    '连接': (_strcat, 2),
    '分割': (_strsplit, 2),
    '替换': (_strreplace, 3),
    '截取': (_strslice, 3),
    '小写': (_strlower, 1),
    '大写': (_strupper, 1),
    '查找': (_strfind, 2),
    '包含': (_strcontains, 2),
    '去空': (_strstrip, 1),
    '开头是': (_strstartswith, 2),
    '结尾是': (_strendswith, 2),
}


# ============ 文件IO库 ============

def _readfile(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def _writefile(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def _appendfile(path, content):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)
    return True

def _fileexists(path): return os.path.exists(path)
def _isfile(path): return os.path.isfile(path)
def _isdir(path): return os.path.isdir(path)
def _listdir(path): return os.listdir(path)
def _mkdir(path): os.makedirs(path, exist_ok=True); return True
def _removefile(path): os.remove(path); return True
def _removedir(path): os.rmdir(path); return True
def _getcwd(): return os.getcwd()
def _basename(path): return os.path.basename(path)
def _dirname(path): return os.path.dirname(path)
def _extname(path): return os.path.splitext(path)[1]

FILE_BUILTINS = {
    '读文件': (_readfile, 1),
    '写文件': (_writefile, 2),
    '追加文件': (_appendfile, 2),
    '存在': (_fileexists, 1),
    '是文件': (_isfile, 1),
    '是目录': (_isdir, 1),
    '列目录': (_listdir, 1),
    '建目录': (_mkdir, 1),
    '删文件': (_removefile, 1),
    '删目录': (_removedir, 1),
    '当前目录': (_getcwd, 0),
    '文件名': (_basename, 1),
    '目录名': (_dirname, 1),
    '扩展名': (_extname, 1),
}


# ============ 时间库 ============

def _now(): return _time_module.time()
def _date(): return _time_module.strftime('%Y-%m-%d')
def _time(): return _time_module.strftime('%H:%M:%S')
def _datetime(): return _time_module.strftime('%Y-%m-%d %H:%M:%S')
def _strftime(fmt, ts=None):
    if ts is None:
        return _time_module.strftime(fmt)
    return _time_module.strftime(fmt, _time_module.localtime(ts))
def _sleep(seconds): _time_module.sleep(seconds); return True

TIME_BUILTINS = {
    '当前时间': (_now, 0),
    '日期': (_date, 0),
    '时间': (_time, 0),
    '日期时间': (_datetime, 0),
    '格式化时间': (_strftime, 2),
    '睡眠': (_sleep, 1),
}


# ============ 类型检查库 ============

def _isnum(x): return isinstance(x, (int, float))
def _isstr(x): return isinstance(x, str)
def _islist(x): return isinstance(x, list)
def _isfunc(x): return callable(x)
def _isbool(x): return isinstance(x, bool)
def _isnone(x): return x is None
def _typeof(x):
    if isinstance(x, bool): return '真'
    if isinstance(x, int): return '整数'
    if isinstance(x, float): return '浮点'
    if isinstance(x, str): return '串'
    if isinstance(x, list): return '表'
    if callable(x): return '函'
    if x is None: return '空'
    return '未知'

TYPE_BUILTINS = {
    '是数': (_isnum, 1),
    '是串': (_isstr, 1),
    '是表': (_islist, 1),
    '是函': (_isfunc, 1),
    '是真': (_isbool, 1),
    '是空': (_isnone, 1),
    '类型': (_typeof, 1),
}


# ============ 测试断言 ============

class YanAssertionError(Exception):
    """言语言断言错误"""
    pass


# ============ 合并所有内置函数 ============

ALL_BUILTINS = {
    **BUILTINS,
    **DICT_BUILTINS,
    **MATH_BUILTINS,
    **STRING_BUILTINS,
    **FILE_BUILTINS,
    **TIME_BUILTINS,
    **TYPE_BUILTINS,
}
