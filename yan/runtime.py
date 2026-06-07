"""
言语言运行时支持
"""

import math
import random
import os
import time as _time_module
import hashlib
import base64
import uuid
import csv
import json
import sqlite3
import zlib
import requests
import re
import subprocess
from functools import reduce
from io import StringIO
from typing import Any, Callable, List, Optional


# ============ 算术运算 ============

def _add(*args): 
    if not args:
        return 0
    return reduce(lambda a, b: a + b, args)

def _sub(*args): 
    if not args:
        return 0
    if len(args) == 1:
        return -args[0]
    return reduce(lambda a, b: a - b, args)

def _mul(*args): 
    if not args:
        return 1
    return reduce(lambda a, b: a * b, args)

def _div(*args):
    if not args:
        return 1
    result = reduce(lambda a, b: a // b if isinstance(a, int) and isinstance(b, int) else a / b, args)
    return result
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
    """生成从0到n-1的列表"""
    return list(range(n))


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
    # 双字关键字
    '相加': (_add, 2),
    '相减': (_sub, 2),
    '相乘': (_mul, 2),
    '相除': (_div, 2),
    '取余': (_mod, 2),
    '幂方': (_pow, 2),
    '绝对值': (_abs, 1),
    '负数': (_neg, 1),

    # 范围
    '范围': (_range, 1),

    # 列表
    '列': (_list, -1),
    '列表': (_list, -1),
        '求值': (_eval, 1),
    '首': (_head, 1),
    '余': (_tail, 1),
    '取': (_nth, 2),
    '设': (_set_nth, 3),
    '长': (_len, 1),
    '长度': (_len, 1),
    '添': (_append, 2),
    '添加': (_append, 2),
    '连': (_concat, 2),
    '连接': (_concat, 2),
    '含': (_contains, 2),
    '包含': (_contains, 2),
    '空': (_empty, 1),
    # 双字关键字
    '首个': (_head, 1),
    '其余': (_tail, 1),
    '加入': (_append, 2),
    '为空': (_empty, 1),
    # 新增列表操作
    '反转': (_reverse, 1),
    '排序': (_sort, 1),
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
    # 双字关键字
    '大于等于': (_gte, 2),
    '小于等于': (_lte, 2),

    # 逻辑
    '且': (_and, 2),
    '或': (_or, 2),
    '非': (_not, 1),
    # 双字关键字
    '并且': (_and, 2),
    '或者': (_or, 2),
    '非也': (_not, 1),

    # 高阶
    '皆': (_map, 2),
    '映射': (_map, 2),
    '只': (_filter, 2),
    '过滤': (_filter, 2),
    '归': (_reduce, 3),
    '归约': (_reduce, 3),

    # I/O
    '印': (print, 1),
    '输出': (print, 1),
    '读行': (input, 0),
    '行': (input, 0),
    '读': (_read_char, 0),
    '读取': (_read_char, 0),
    # 双字关键字
    '打印': (print, 1),
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
def _random_seed(seed): random.seed(seed)
def _random_range(start, end, step=1): return random.randrange(start, end, step)
def _random_gauss(mu, sigma): return random.gauss(mu, sigma)
def _random_uniform(a, b): return random.uniform(a, b)

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
    '随机种子': (_random_seed, 1),
    '随机范围': (_random_range, 3),
    '正态随机': (_random_gauss, 2),
    '均匀随机': (_random_uniform, 2),
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
def _sleep_ms(milliseconds): _time_module.sleep(milliseconds / 1000); return True
def _year(date_str): return int(_time_module.strptime(date_str, '%Y-%m-%d').tm_year)
def _month(date_str): return int(_time_module.strptime(date_str, '%Y-%m-%d').tm_mon)
def _day(date_str): return int(_time_module.strptime(date_str, '%Y-%m-%d').tm_mday)
def _hour(time_str): return int(_time_module.strptime(time_str, '%H:%M:%S').tm_hour)
def _minute(time_str): return int(_time_module.strptime(time_str, '%H:%M:%S').tm_min)
def _second(time_str): return int(_time_module.strptime(time_str, '%H:%M:%S').tm_sec)
def _weekday(date_str): return ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][_time_module.strptime(date_str, '%Y-%m-%d').tm_wday]
def _is_leap(year): return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
def _date_to_timestamp(date_str): return _time_module.mktime(_time_module.strptime(date_str, '%Y-%m-%d %H:%M:%S'))
def _timestamp_to_date(ts): return _time_module.strftime('%Y-%m-%d', _time_module.localtime(ts))

TIME_BUILTINS = {
    '当前时间': (_now, 0),
    '日期': (_date, 0),
    '时间': (_time, 0),
    '日期时间': (_datetime, 0),
    '格式化时间': (_strftime, 2),
    '睡眠': (_sleep, 1),
    '睡眠毫秒': (_sleep_ms, 1),
    '取年': (_year, 1),
    '取月': (_month, 1),
    '取日': (_day, 1),
    '取时': (_hour, 1),
    '取分': (_minute, 1),
    '取秒': (_second, 1),
    '星期几': (_weekday, 1),
    '是闰年': (_is_leap, 1),
    '日期时间戳': (_date_to_timestamp, 1),
    '时间戳日期': (_timestamp_to_date, 1),
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


# ============ 网络库 ============

def _http_get(url, headers=None, timeout=10):
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        return {'status': resp.status_code, 'content': resp.text, 'json': resp.json, 'headers': dict(resp.headers), 'ok': resp.ok}
    except:
        return {'status': 0, 'content': '', 'json': None, 'headers': {}, 'ok': False}

def _http_post(url, data=None, json_data=None, headers=None, timeout=10):
    try:
        resp = requests.post(url, data=data, json=json_data, headers=headers, timeout=timeout)
        return {'status': resp.status_code, 'content': resp.text, 'json': resp.json, 'headers': dict(resp.headers), 'ok': resp.ok}
    except:
        return {'status': 0, 'content': '', 'json': None, 'headers': {}, 'ok': False}

def _http_put(url, data=None, json_data=None, headers=None, timeout=10):
    try:
        resp = requests.put(url, data=data, json=json_data, headers=headers, timeout=timeout)
        return {'status': resp.status_code, 'content': resp.text, 'json': resp.json, 'headers': dict(resp.headers), 'ok': resp.ok}
    except:
        return {'status': 0, 'content': '', 'json': None, 'headers': {}, 'ok': False}

def _http_delete(url, headers=None, timeout=10):
    try:
        resp = requests.delete(url, headers=headers, timeout=timeout)
        return {'status': resp.status_code, 'content': resp.text, 'json': resp.json, 'headers': dict(resp.headers), 'ok': resp.ok}
    except:
        return {'status': 0, 'content': '', 'json': None, 'headers': {}, 'ok': False}

def _http_patch(url, data=None, json_data=None, headers=None, timeout=10):
    try:
        resp = requests.patch(url, data=data, json=json_data, headers=headers, timeout=timeout)
        return {'status': resp.status_code, 'content': resp.text, 'json': resp.json, 'headers': dict(resp.headers), 'ok': resp.ok}
    except:
        return {'status': 0, 'content': '', 'json': None, 'headers': {}, 'ok': False}

def _url_encode(params):
    from urllib.parse import quote
    return quote(str(params))

def _url_decode(url):
    from urllib.parse import unquote
    return unquote(url)

def _url_build(base_url, path, params=None):
    from urllib.parse import urljoin, urlencode
    url = urljoin(base_url, path)
    if params:
        url += '?' + urlencode(params)
    return url

NETWORK_BUILTINS = {
    'HTTP_GET': (_http_get, 1),
    'HTTP_POST': (_http_post, 1),
    'HTTP_PUT': (_http_put, 1),
    'HTTP_DELETE': (_http_delete, 1),
    'HTTP_PATCH': (_http_patch, 1),
    'URL编码': (_url_encode, 1),
    'URL解码': (_url_decode, 1),
    'URL构建': (_url_build, 2),
}


# ============ 加密库 ============

def _md5(s): return hashlib.md5(str(s).encode('utf-8')).hexdigest()
def _sha1(s): return hashlib.sha1(str(s).encode('utf-8')).hexdigest()
def _sha256(s): return hashlib.sha256(str(s).encode('utf-8')).hexdigest()
def _sha512(s): return hashlib.sha512(str(s).encode('utf-8')).hexdigest()
def _b64encode(s): return base64.b64encode(str(s).encode('utf-8')).decode('utf-8')
def _b64decode(s): return base64.b64decode(s).decode('utf-8')
def _b64urlencode(s): return base64.urlsafe_b64encode(str(s).encode('utf-8')).decode('utf-8').rstrip('=')
def _b64urldecode(s):
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s).decode('utf-8')
def _uuid1(): return str(uuid.uuid1())
def _uuid4(): return str(uuid.uuid4())
def _uuid_short(): return str(uuid.uuid4()).replace('-', '')
def _hmac_md5(s, key): return hashlib.md5((str(key) + str(s)).encode('utf-8')).hexdigest()
def _hmac_sha256(s, key): return hashlib.sha256((str(key) + str(s)).encode('utf-8')).hexdigest()
def _crc32(s): return zlib.crc32(str(s).encode('utf-8')) & 0xffffffff
def _secure_compare(a, b): return str(a) == str(b)

CRYPTO_BUILTINS = {
    'MD5': (_md5, 1),
    'SHA1': (_sha1, 1),
    'SHA256': (_sha256, 1),
    'SHA512': (_sha512, 1),
    'Base64编码': (_b64encode, 1),
    'Base64解码': (_b64decode, 1),
    'Base64URL编码': (_b64urlencode, 1),
    'Base64URL解码': (_b64urldecode, 1),
    'UUID1': (_uuid1, 0),
    'UUID4': (_uuid4, 0),
    'UUID字符串': (_uuid_short, 0),
    'HMAC_MD5': (_hmac_md5, 2),
    'HMAC_SHA256': (_hmac_sha256, 2),
    '安全比较': (_secure_compare, 2),
}


# ============ 正则表达式库 ============

def _re_match(pattern, text):
    match = re.match(pattern, text)
    return match.group() if match else None

def _re_search(pattern, text):
    match = re.search(pattern, text)
    return match.group() if match else None

def _re_findall(pattern, text):
    return re.findall(pattern, text)

def _re_finditer(pattern, text):
    return [match.group() for match in re.finditer(pattern, text)]

def _re_sub(pattern, repl, text):
    return re.sub(pattern, repl, text)

def _re_split(pattern, text):
    return re.split(pattern, text)

def _re_fullmatch(pattern, text):
    match = re.fullmatch(pattern, text)
    return match.group() if match else None

def _re_compile(pattern):
    return re.compile(pattern)

REGEX_BUILTINS = {
    '正则匹配': (_re_match, 2),
    '正则搜索': (_re_search, 2),
    '正则查找所有': (_re_findall, 2),
    '正则替换': (_re_sub, 3),
    '正则分割': (_re_split, 2),
    '正则完全匹配': (_re_fullmatch, 2),
    '正则编译': (_re_compile, 1),
}


# ============ 进程管理库 ============

def _exec_cmd(cmd, shell=True):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, encoding='utf-8')
        return {'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode}
    except Exception as e:
        return {'stdout': '', 'stderr': str(e), 'returncode': -1}

def _get_env(name):
    return os.environ.get(name, '')

def _set_env(name, value):
    os.environ[name] = value
    return True

def _get_env_dict():
    return dict(os.environ)

def _exec_popen(cmd, shell=True):
    try:
        process = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate()
        return {'stdout': stdout, 'stderr': stderr, 'returncode': process.returncode}
    except Exception as e:
        return {'stdout': '', 'stderr': str(e), 'returncode': -1}

PROCESS_BUILTINS = {
    '执行命令': (_exec_cmd, 1),
    '获取环境变量': (_get_env, 1),
    '设置环境变量': (_set_env, 2),
    '获取所有环境变量': (_get_env_dict, 0),
    '启动进程': (_exec_popen, 1),
}


# ============ JSON库 ============

def _json_parse(s):
    try:
        return json.loads(str(s))
    except:
        return None

def _json_generate(obj, indent=2):
    return json.dumps(obj, ensure_ascii=False, indent=indent)

def _json_readfile(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _json_writefile(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return True

JSON_BUILTINS = {
    'JSON解析': (_json_parse, 1),
    'JSON生成': (_json_generate, 1),
    'JSON读文件': (_json_readfile, 1),
    'JSON写文件': (_json_writefile, 2),
}


# ============ 数据库库 ============

def _db_open(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def _db_close(conn):
    if conn:
        conn.close()
    return True

def _db_execute(conn, sql, params=None):
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    conn.commit()
    return cursor.rowcount

def _db_query(conn, sql, params=None):
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def _db_query_one(conn, sql, params=None):
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    row = cursor.fetchone()
    return dict(row) if row else None

def _db_query_value(conn, sql, params=None):
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    row = cursor.fetchone()
    return row[0] if row else None

def _db_insert(conn, table, data):
    keys = list(data.keys())
    placeholders = ','.join(['?' for _ in keys])
    values = [data[k] for k in keys]
    sql = f'INSERT INTO {table} ({",".join(keys)}) VALUES ({placeholders})'
    cursor = conn.execute(sql, values)
    conn.commit()
    return cursor.lastrowid

DATABASE_BUILTINS = {
    '打开数据库': (_db_open, 1),
    '关闭数据库': (_db_close, 1),
    '执行SQL': (_db_execute, 2),
    '查询': (_db_query, 2),
    '查询单行': (_db_query_one, 2),
    '查询值': (_db_query_value, 2),
    '插入记录': (_db_insert, 3),
}


# ============ CSV库 ============

def _csv_read(path, delimiter=','):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return list(reader)

def _csv_write(path, data, delimiter=','):
    if not data:
        return True
    headers = list(data[0].keys()) if isinstance(data[0], dict) else []
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
    return True

def _csv_read_raw(path, delimiter=','):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter=delimiter)
        return list(reader)

def _csv_write_raw(path, data, delimiter=','):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(data)
    return True

def _csv_parse(s, delimiter=','):
    f = StringIO(s)
    reader = csv.DictReader(f, delimiter=delimiter)
    return list(reader)

def _csv_serialize(data, delimiter=','):
    if not data:
        return ''
    headers = list(data[0].keys()) if isinstance(data[0], dict) else []
    f = StringIO()
    writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(data)
    return f.getvalue()

CSV_BUILTINS = {
    'CSV读取': (_csv_read, 1),
    'CSV写入': (_csv_write, 2),
    'CSV读取纯文本': (_csv_read_raw, 1),
    'CSV写入纯文本': (_csv_write_raw, 2),
    'CSV解析': (_csv_parse, 1),
    'CSV序列化': (_csv_serialize, 1),
}


# ============ 合并所有内置函数 ============

ALL_BUILTINS = {
    **BUILTINS,
    **DICT_BUILTINS,
    **MATH_BUILTINS,
    **STRING_BUILTINS,
    **FILE_BUILTINS,
    **TIME_BUILTINS,
    **TYPE_BUILTINS,
    **NETWORK_BUILTINS,
    **CRYPTO_BUILTINS,
    **REGEX_BUILTINS,
    **PROCESS_BUILTINS,
    **JSON_BUILTINS,
    **DATABASE_BUILTINS,
    **CSV_BUILTINS,
}
