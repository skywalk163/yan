"""
诊断阶段2 - 查看编译器1如何处理 compiler.yan
"""
import sys
import os

# 读取编译器1
with open('compiler1_from_c0.py', 'r', encoding='utf-8') as f:
    compiler1_code = f.read()

# 读取 compiler.yan
with open('compiler.yan', 'r', encoding='utf-8') as f:
    yan_source = f.read()

print('=' * 60)
print('诊断阶段2')
print('=' * 60)
print(f'compiler.yan 大小: {len(yan_source)} 字符')
print(f'compiler1 大小: {len(compiler1_code)} 字符')
print()

# 提取编译器1的编译函数（不执行测试代码）
lines = compiler1_code.splitlines()
# 移除最后的测试代码
compile_func_start = None
for i, line in enumerate(lines):
    if line.startswith('def compile(source):'):
        compile_func_start = i
        break

if compile_func_start:
    # 提取到 compile 函数结束
    compile_code_lines = []
    indent_level = None
    for i in range(compile_func_start, len(lines)):
        line = lines[i]
        if i == compile_func_start:
            compile_code_lines.append(line)
            indent_level = len(line) - len(line.lstrip())
        elif line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.startswith('\t'):
            # 函数结束
            break
        else:
            compile_code_lines.append(line)
    
    print(f'compile 函数行数: {len(compile_code_lines)}')
    print()

# 尝试编译（不执行测试）
print('尝试使用编译器1编译 compiler.yan...')
print()

# 创建一个安全的执行环境
exec_globals = {
    '__builtins__': __builtins__,
    'tokenize': None,
    'parse': None,
    'generate': None,
    'compile': None,
}

try:
    # 只执行到 compile 函数定义，跳过测试代码
    code_without_test = '\n'.join(lines[:429])  # 停在测试代码之前
    exec(code_without_test, exec_globals)
    
    # 现在调用 compile 函数
    if 'compile' in exec_globals and callable(exec_globals['compile']):
        result = exec_globals['compile'](yan_source)
        generated_code = result[0]
        errors = result[1]
        
        print(f'生成的代码大小: {len(generated_code)} 字符')
        print(f'错误: {errors if errors else "无"}')
        print()
        
        # 保存生成的代码
        with open('compiler2_diagnostic.py', 'w', encoding='utf-8') as f:
            f.write(generated_code)
        print('已保存到 compiler2_diagnostic.py')
        
        # 显示前20行
        print()
        print('生成代码的前20行:')
        for i, line in enumerate(generated_code.splitlines()[:20], 1):
            print(f'{i:3}: {line}')
    else:
        print('错误: compile 函数未定义')
        
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
