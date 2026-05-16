"""
Python 到言语言转换器测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from py2yan import PythonToYanConverter, ConversionError


def test_basic_arithmetic():
    converter = PythonToYanConverter()
    code = converter.convert("x = 5 + 3")
    assert "定x=5加3。" in code, f"算术运算失败: {code}"
    print("  [OK] 基础算术运算")


def test_comparison():
    converter = PythonToYanConverter()
    code = converter.convert("result = x > 5")
    assert "定result=x大5。" in code, f"比较运算失败: {code}"
    print("  [OK] 比较运算")


def test_if_statement():
    converter = PythonToYanConverter()
    code = converter.convert("""
if x > 0:
    result = "positive"
else:
    result = "negative"
""")
    assert "若x大0则：" in code, f"条件语句失败: {code}"
    assert "否则：" in code
    print("  [OK] 条件语句")


def test_for_loop():
    converter = PythonToYanConverter()
    code = converter.convert("""
for x in range(10):
    print(x)
""")
    assert "遍历x于范围10：" in code, f"for循环失败: {code}"
    print("  [OK] for循环")


def test_while_loop():
    converter = PythonToYanConverter()
    code = converter.convert("""
while x > 0:
    x -= 1
""")
    assert "当x大0：" in code, f"while循环失败: {code}"
    print("  [OK] while循环")


def test_function_def():
    converter = PythonToYanConverter()
    code = converter.convert("""
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)
""")
    assert "定factorial=函n：" in code, f"函数定义失败: {code}"
    assert "返回" in code
    print("  [OK] 函数定义")


def test_list_comprehension():
    converter = PythonToYanConverter()
    code = converter.convert("squares = [x**2 for x in range(10)]")
    assert "皆函xx幂2" in code, f"列表推导式失败: {code}"
    print("  [OK] 列表推导式")


def test_list_operations():
    converter = PythonToYanConverter()
    code = converter.convert("""
lst = [1, 2, 3]
lst.append(4)
first = lst[0]
length = len(lst)
""")
    assert "列1 2 3" in code
    assert "添" in code
    assert "入" in code
    assert "长" in code
    print("  [OK] 列表操作")


def test_dict_operations():
    converter = PythonToYanConverter()
    code = converter.convert("""
d = {'a': 1, 'b': 2}
val = d.get('a')
""")
    assert "典" in code
    assert "取" in code
    print("  [OK] 字典操作")


def test_stdlib_import():
    converter = PythonToYanConverter()
    code = converter.convert("""
import os
import json
from datetime import datetime
path = os.path.join('data', 'file.txt')
data = json.loads('{"a": 1}')
now = datetime.now()
""")
    assert "入文件。" in code
    assert "入JSON。" in code
    assert "入时间。" in code
    assert "路径连接" in code
    assert "JSON解码" in code
    assert "当前时间" in code
    print("  [OK] 标准库导入")


def test_third_party_bridge():
    converter = PythonToYanConverter()
    code = converter.convert("""
import numpy as np
import requests
arr = np.array([1, 2, 3])
""")
    assert "引入Python" in code
    print("  [OK] 第三方库桥接")


def test_lambda():
    converter = PythonToYanConverter()
    code = converter.convert("f = lambda x: x * 2")
    assert "函xx乘2" in code, f"lambda失败: {code}"
    print("  [OK] lambda表达式")


def test_f_string():
    converter = PythonToYanConverter()
    code = converter.convert('name = "World"\ngreeting = f"Hello, {name}!"')
    assert "转字符串" in code
    print("  [OK] f-string")


def test_with_statement():
    converter = PythonToYanConverter()
    code = converter.convert("""
with open('file.txt', 'r') as f:
    content = f.read()
""")
    assert "读文件" in code
    print("  [OK] with语句")


def test_try_except():
    converter = PythonToYanConverter()
    code = converter.convert("""
try:
    result = 10 / x
except ZeroDivisionError:
    result = 0
""")
    assert "尝试：" in code
    assert "捕获" in code
    print("  [OK] 异常处理")


def test_augmented_assign():
    converter = PythonToYanConverter()
    code = converter.convert("""
x = 5
x += 1
""")
    assert "设x=x加1。" in code
    print("  [OK] 增强赋值")


def test_boolean_ops():
    converter = PythonToYanConverter()
    code = converter.convert("result = x > 0 and x < 10")
    assert "且" in code
    print("  [OK] 布尔运算")


def test_math_functions():
    converter = PythonToYanConverter()
    code = converter.convert("""
import math
result = math.sin(math.pi / 4)
""")
    assert "正弦" in code
    assert "圆周率" in code
    print("  [OK] 数学函数")


def test_string_methods():
    converter = PythonToYanConverter()
    code = converter.convert("""
s = "Hello"
upper = s.upper()
lower = s.lower()
parts = s.split(",")
""")
    assert "大写" in code
    assert "小写" in code
    assert "分割" in code
    print("  [OK] 字符串方法")


def test_class_conversion():
    converter = PythonToYanConverter()
    code = converter.convert("""
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def greet(self):
        return f"Hello, {self.name}"
""")
    assert "创建Person" in code
    print("  [OK] 类转换")


def test_list_comp_with_filter():
    converter = PythonToYanConverter()
    code = converter.convert("result = [x*2 for x in range(10) if x > 3]")
    assert "只" in code
    assert "皆" in code
    print("  [OK] 带过滤的列表推导式")


def test_chain_comparison():
    converter = PythonToYanConverter()
    code = converter.convert("result = 0 < x < 10")
    assert "且" in code
    print("  [OK] 链式比较")


def test_import_report():
    converter = PythonToYanConverter()
    converter.convert("""
import os
import json
import numpy as np
from datetime import datetime
""")
    report = converter.conversion_report.generate()
    assert "总导入数：4" in report
    assert "已转换" in report
    assert "已桥接" in report
    print("  [OK] 导入报告")


def test_break_continue():
    converter = PythonToYanConverter()
    code = converter.convert("""
for x in range(10):
    if x == 5:
        break
    if x < 3:
        continue
""")
    assert "跳出。" in code
    assert "继续。" in code
    print("  [OK] break/continue")


def test_return_none():
    converter = PythonToYanConverter()
    code = converter.convert("""
def func():
    return None
""")
    assert "返回空。" in code
    print("  [OK] 返回空值")


def test_assert_statement():
    converter = PythonToYanConverter()
    code = converter.convert('assert x > 0, "x must be positive"')
    assert "断言" in code
    print("  [OK] 断言")


def test_dict_comprehension():
    converter = PythonToYanConverter()
    code = converter.convert("squares = {x: x**2 for x in range(10)}")
    assert "遍历" in code
    print("  [OK] 字典推导式")


def test_slice_operations():
    converter = PythonToYanConverter()
    code = converter.convert("""
lst = [1, 2, 3, 4, 5]
first = lst[0]
rest = lst[1:]
head = lst[:3]
""")
    assert "入0" in code
    assert "余1" in code
    print("  [OK] 切片操作")


def test_if_exp():
    converter = PythonToYanConverter()
    code = converter.convert("result = 'yes' if x > 0 else 'no'")
    assert "若x大0则" in code
    assert "否则" in code
    print("  [OK] 三元表达式")


def test_elifs():
    converter = PythonToYanConverter()
    code = converter.convert("""
if x > 0:
    result = "positive"
elif x < 0:
    result = "negative"
else:
    result = "zero"
""")
    assert "若x大0则：" in code
    assert "否则" in code
    print("  [OK] elif 链")


def test_nested_functions():
    converter = PythonToYanConverter()
    code = converter.convert("""
def outer(x):
    def inner(y):
        return y + 1
    return inner(x) + 1
""")
    assert "定outer=函x：" in code
    assert "定inner=函y：" in code
    print("  [OK] 嵌套函数")


def test_multiple_assign():
    converter = PythonToYanConverter()
    code = converter.convert("a, b = 1, 2")
    assert "定a=1。" in code
    assert "定b=2。" in code
    print("  [OK] 多重赋值")


def test_delete_statement():
    converter = PythonToYanConverter()
    code = converter.convert("del x")
    assert "删x。" in code
    print("  [OK] del 语句")


def test_global_statement():
    converter = PythonToYanConverter()
    code = converter.convert("""
def func():
    global x
    x = 5
""")
    assert "全局x。" in code
    print("  [OK] global 语句")


def test_raise_statement():
    converter = PythonToYanConverter()
    code = converter.convert('raise ValueError("invalid")')
    assert "抛出" in code
    print("  [OK] raise 语句")


def test_file_operations():
    converter = PythonToYanConverter()
    code = converter.convert("""
import os
files = os.listdir('.')
os.makedirs('new_dir')
""")
    assert "列目录" in code
    assert "建目录" in code
    print("  [OK] 文件操作")


def test_random_functions():
    converter = PythonToYanConverter()
    code = converter.convert("""
import random
num = random.randint(1, 10)
""")
    assert "随机整数" in code
    print("  [OK] 随机函数")


def test_re_functions():
    converter = PythonToYanConverter()
    code = converter.convert("""
import re
result = re.match(r'\\d+', '123abc')
""")
    assert "正则匹配" in code
    print("  [OK] 正则表达式")


def test_time_functions():
    converter = PythonToYanConverter()
    code = converter.convert("""
import time
time.sleep(1)
""")
    assert "睡眠" in code
    print("  [OK] 时间函数")


def test_bool_constants():
    converter = PythonToYanConverter()
    code = converter.convert("""
a = True
b = False
c = None
""")
    assert "真" in code
    assert "假" in code
    assert "空" in code
    print("  [OK] 布尔常量")


def test_type_conversion():
    converter = PythonToYanConverter()
    code = converter.convert("""
a = int("123")
b = str(456)
c = float("3.14")
""")
    assert "转整数" in code
    assert "转字符串" in code
    assert "转浮点" in code
    print("  [OK] 类型转换")


def test_sum_function():
    converter = PythonToYanConverter()
    code = converter.convert("total = sum([1, 2, 3])")
    assert "归加0" in code
    print("  [OK] sum 函数")


def test_sorted_reversed():
    converter = PythonToYanConverter()
    code = converter.convert("""
sorted_lst = sorted([3, 1, 2])
reversed_lst = list(reversed([1, 2, 3]))
""")
    assert "排序" in code
    assert "反转" in code
    print("  [OK] 排序和反转")


def test_enumerate_zip():
    converter = PythonToYanConverter()
    code = converter.convert("""
for i, v in enumerate([1, 2, 3]):
    print(i, v)
""")
    assert "枚举" in code
    print("  [OK] 枚举")


def test_abs_function():
    converter = PythonToYanConverter()
    code = converter.convert("result = abs(-5)")
    assert "绝对" in code
    print("  [OK] 绝对值")


def test_max_min():
    converter = PythonToYanConverter()
    code = converter.convert("""
m = max(1, 2, 3)
n = min(1, 2, 3)
""")
    assert "最大" in code
    assert "最小" in code
    print("  [OK] 最大最小")


def test_round_function():
    converter = PythonToYanConverter()
    code = converter.convert("result = round(3.14)")
    assert "四舍五入" in code
    print("  [OK] 四舍五入")


def test_input_function():
    converter = PythonToYanConverter()
    code = converter.convert('name = input("Enter name: ")')
    assert "输入" in code
    print("  [OK] 输入")


def test_isinstance():
    converter = PythonToYanConverter()
    code = converter.convert("result = isinstance(x, int)")
    assert "是实例" in code
    print("  [OK] isinstance")


def test_floor_division():
    converter = PythonToYanConverter()
    code = converter.convert("result = 10 // 3")
    assert "整除" in code
    print("  [OK] 整除")


def test_bit_operations():
    converter = PythonToYanConverter()
    code = converter.convert("""
a = 1 << 2
b = 8 >> 2
c = 5 & 3
d = 5 | 3
e = 5 ^ 3
""")
    assert "左移" in code
    assert "右移" in code
    assert "位与" in code
    assert "位或" in code
    assert "位异或" in code
    print("  [OK] 位运算")


def test_not_operator():
    converter = PythonToYanConverter()
    code = converter.convert("result = not x")
    assert "非x" in code
    print("  [OK] 非运算")


def test_neg_operator():
    converter = PythonToYanConverter()
    code = converter.convert("result = -x")
    assert "负x" in code
    print("  [OK] 取负")


def test_in_not_in():
    converter = PythonToYanConverter()
    code = converter.convert("""
a = x in lst
b = x not in lst
""")
    assert "含" in code
    print("  [OK] 包含检查")


def test_is_isnot():
    converter = PythonToYanConverter()
    code = converter.convert("""
a = x is None
b = x is not None
""")
    assert "是" in code
    print("  [OK] 身份比较")


def test_empty_function():
    converter = PythonToYanConverter()
    code = converter.convert("""
def empty():
    pass
""")
    assert "定empty=函_" in code
    print("  [OK] 空函数")


def test_complex_expression():
    converter = PythonToYanConverter()
    code = converter.convert("result = (a + b) * (c - d) / e")
    assert "加" in code
    assert "减" in code
    assert "除" in code
    print("  [OK] 复杂表达式")


def test_method_chaining():
    converter = PythonToYanConverter()
    code = converter.convert("result = '  hello  '.strip().upper()")
    assert "去空" in code
    assert "大写" in code
    print("  [OK] 方法链式调用")


def test_yield():
    converter = PythonToYanConverter()
    code = converter.convert("""
def gen():
    yield 1
    yield 2
""")
    assert "产出" in code
    print("  [OK] yield")


def test_starred_expression():
    converter = PythonToYanConverter()
    code = converter.convert("func(*args)")
    assert "展开" in code
    print("  [OK] 星号表达式")


def test_import_from_multiple():
    converter = PythonToYanConverter()
    code = converter.convert("""
from os import path, listdir
""")
    assert "入文件。" in code
    print("  [OK] 从同一模块导入多个")


def test_import_with_dot():
    converter = PythonToYanConverter()
    code = converter.convert("""
from os.path import join, exists
""")
    assert "入文件。" in code
    print("  [OK] 带点的模块导入")


def test_import_unknown_module():
    converter = PythonToYanConverter()
    code = converter.convert("""
import some_local_module
""")
    assert "引入Python" in code
    print("  [OK] 未知模块导入")


def test_import_stdlib_with_as():
    converter = PythonToYanConverter()
    code = converter.convert("""
import math as m
""")
    assert "入数学。" in code
    print("  [OK] 标准库 import 带别名")


def test_import_all_types():
    """综合测试所有导入类型"""
    converter = PythonToYanConverter()
    code = converter.convert("""
import os
import json
import numpy as np
from datetime import datetime
from math import sin
from sklearn.metrics import accuracy_score

path = os.path.join('data', 'file.txt')
data = json.loads('{}')
arr = np.array([1, 2, 3])
now = datetime.now()
val = sin(3.14)
""")
    assert "入文件。" in code
    assert "入JSON。" in code
    assert "入时间。" in code
    assert "入数学。" in code
    assert "定np=引入Python" in code
    assert "路径连接" in code
    assert "JSON解码" in code
    assert "当前时间" in code
    assert "正弦" in code
    print("  [OK] 综合导入测试")


def test_import_report_comprehensive():
    """综合导入报告"""
    converter = PythonToYanConverter()
    converter.convert("""
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from math import sin, cos
from sklearn.metrics import accuracy_score
""")
    report = converter.conversion_report.generate()
    assert "总导入数：7" in report
    assert "已转换" in report
    assert "已桥接" in report
    print("  [OK] 综合导入报告")


def test_import_no_imports():
    converter = PythonToYanConverter()
    converter.convert("x = 5")
    report = converter.conversion_report.generate()
    assert "无导入语句需要处理" in report
    print("  [OK] 无导入语句报告")


def test_high_order_functions():
    converter = PythonToYanConverter()
    code = converter.convert("""
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
filtered = list(filter(lambda x: x > 2, numbers))
""")
    assert "皆" in code, f"map失败: {code}"
    assert "只" in code
    print("  [OK] 高阶函数")


def test_default_arguments():
    converter = PythonToYanConverter()
    code = converter.convert("""
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
""")
    assert "定greet=函" in code
    print("  [OK] 默认参数")


def test_annotation_assign():
    converter = PythonToYanConverter()
    code = converter.convert("x: int = 5")
    assert "定x=5。" in code
    print("  [OK] 注解赋值")


def test_nested_list_comp():
    converter = PythonToYanConverter()
    code = converter.convert("matrix = [[i*j for j in range(3)] for i in range(3)]")
    assert "皆函" in code, f"嵌套列表推导式失败: {code}"
    print("  [OK] 嵌套列表推导式")


def test_generator_exp():
    converter = PythonToYanConverter()
    code = converter.convert("gen = (x*2 for x in range(10))")
    assert "皆函xx乘2" in code, f"生成器表达式失败: {code}"
    print("  [OK] 生成器表达式")


def test_set_comp():
    converter = PythonToYanConverter()
    code = converter.convert("s = {x*2 for x in range(10)}")
    assert "皆函" in code
    print("  [OK] 集合推导式")


def test_async_function():
    converter = PythonToYanConverter()
    code = converter.convert("""
async def fetch():
    result = await some_async_func()
    return result
""")
    assert "定fetch=函" in code
    print("  [OK] 异步函数")


def test_import_with_as():
    converter = PythonToYanConverter()
    code = converter.convert("""
import numpy as np
import pandas as pd
""")
    assert "定np=引入Python" in code
    assert "定pd=引入Python" in code
    print("  [OK] 带别名的导入")


def test_import_from():
    converter = PythonToYanConverter()
    code = converter.convert("""
from math import sin, cos
from datetime import datetime
""")
    assert "入数学。" in code
    assert "入时间。" in code
    print("  [OK] from import")


def test_third_party_from_import():
    converter = PythonToYanConverter()
    code = converter.convert("""
from numpy import array, mean
""")
    assert "引入Python" in code
    print("  [OK] 第三方库 from import")


def test_conversion_error():
    converter = PythonToYanConverter()
    try:
        converter.convert("x = @invalid")
        assert False, "应该抛出异常"
    except ConversionError:
        pass
    print("  [OK] 转换错误处理")


def run_all():
    print("=" * 50)
    print("Python 到言语言转换器测试")
    print("=" * 50)

    tests = [
        test_basic_arithmetic,
        test_comparison,
        test_if_statement,
        test_for_loop,
        test_while_loop,
        test_function_def,
        test_list_comprehension,
        test_list_operations,
        test_dict_operations,
        test_stdlib_import,
        test_third_party_bridge,
        test_lambda,
        test_f_string,
        test_with_statement,
        test_try_except,
        test_augmented_assign,
        test_boolean_ops,
        test_math_functions,
        test_string_methods,
        test_class_conversion,
        test_list_comp_with_filter,
        test_chain_comparison,
        test_import_report,
        test_break_continue,
        test_return_none,
        test_assert_statement,
        test_dict_comprehension,
        test_slice_operations,
        test_if_exp,
        test_elifs,
        test_nested_functions,
        test_multiple_assign,
        test_delete_statement,
        test_global_statement,
        test_raise_statement,
        test_file_operations,
        test_random_functions,
        test_re_functions,
        test_time_functions,
        test_bool_constants,
        test_type_conversion,
        test_sum_function,
        test_sorted_reversed,
        test_enumerate_zip,
        test_abs_function,
        test_max_min,
        test_round_function,
        test_input_function,
        test_isinstance,
        test_floor_division,
        test_bit_operations,
        test_not_operator,
        test_neg_operator,
        test_in_not_in,
        test_is_isnot,
        test_empty_function,
        test_complex_expression,
        test_method_chaining,
        test_yield,
        test_starred_expression,
        test_import_from_multiple,
        test_import_with_dot,
        test_import_unknown_module,
        test_import_stdlib_with_as,
        test_import_all_types,
        test_import_report_comprehensive,
        test_import_no_imports,
        test_high_order_functions,
        test_default_arguments,
        test_annotation_assign,
        test_nested_list_comp,
        test_generator_exp,
        test_set_comp,
        test_async_function,
        test_import_with_as,
        test_import_from,
        test_third_party_from_import,
        test_conversion_error,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"总计: {len(tests)}, 通过: {passed}, 失败: {failed}")
    print(f"{'=' * 50}")
    return failed == 0


if __name__ == '__main__':
    success = run_all()
    sys.exit(0 if success else 1)