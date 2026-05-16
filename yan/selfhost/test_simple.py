#!/usr/bin/env python3
# 测试编译器1处理简单输入

# 读取编译器1代码
with open('compiler1_from_c0.py', 'r', encoding='utf-8') as f:
    compiler_code = f.read()

# 创建执行环境
exec_globals = {'__builtins__': __builtins__}

# 执行编译器1
exec(compiler_code, exec_globals)

# 测试简单输入
test_source = '定x=1。'
result = exec_globals['compile'](test_source)
print(f"输入: {test_source}")
print(f"输出: {result[0]}")
