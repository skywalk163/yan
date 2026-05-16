#!/usr/bin/env python3
# 快速测试编译器1

import sys

print("读取编译器1...")
with open('compiler1_from_c0.py', 'r', encoding='utf-8') as f:
    compiler_code = f.read()

print("执行编译器1...")
exec_globals = {'__builtins__': __builtins__}
exec(compiler_code, exec_globals)

print("测试编译简单代码...")
test_source = '定x=1。'
result = exec_globals['compile'](test_source)
print(f"输入: {test_source}")
print(f"输出: {result[0]}")
print("测试成功!")
