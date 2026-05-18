#!/usr/bin/env python3
"""
言语言标准库测试运行器（改进版）
通过 yan 编译器运行测试文件
"""

import os
import sys
import time
from pathlib import Path

# 添加 yan 模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import run as yan_run
from runtime import *


def preprocess_test(source: str) -> str:
    """
    预处理测试文件，将混合语法转换为纯 yan 语法
    """
    lines = source.split('\n')
    result = []
    
    for line in lines:
        # 将 Python 注释转换为 yan 注释
        if line.lstrip().startswith('#'):
            # 保留 shebang
            if line.startswith('#!/'):
                result.append('-- ' + line[2:])
            else:
                result.append('--' + line[1:])
        else:
            result.append(line)
    
    return '\n'.join(result)


def run_yan_test(test_file: str):
    """
    运行单个 yan 测试文件
    """
    print(f"\n运行测试: {test_file}")
    print("-" * 80)
    
    try:
        # 读取测试文件
        with open(test_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 预处理
        source = preprocess_test(source)
        
        # 创建执行环境，包含测试框架
        env = create_test_env()
        
        # 运行测试
        start_time = time.time()
        result = yan_run(source, debug=False, env=env, current_file=Path(test_file))
        elapsed = time.time() - start_time
        
        print(f"\n文件测试完成，耗时: {elapsed:.2f}秒")
        
        return result
        
    except Exception as e:
        print(f"\033[91m错误: 无法运行测试文件 {test_file}\033[0m")
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_test_env():
    """
    创建测试执行环境，包含测试框架和运行时函数
    """
    env = globals().copy()
    
    # 添加 yan 运行时函数
    env.update({
        # 列表操作
        '列': _list,
        '入': _nth,
        '长': _len,
        '空': None,
        '真': True,
        '假': False,
        
        # 算术运算
        '加': _add,
        '减': _sub,
        '乘': _mul,
        '除': _div,
        '模': _mod,
        '幂': _pow,
        '绝对': _abs,
        
        # 比较运算
        '大': _gt,
        '小': _lt,
        '等': _eq,
        
        # 逻辑运算
        '且': _and,
        '或': _or,
        '非': _not,
        
        # 高阶函数
        '皆': _map,
        '只': _filter,
        
        # 测试断言（从 yan_assertions）
        '等': lambda a, b: assert_equal(a, b),
        '不等': lambda a, b: assert_not_equal(a, b),
        '为真': lambda x: assert_true(x),
        '为假': lambda x: assert_false(x),
    })
    
    return env


# 简单的断言函数
def assert_equal(a, b):
    if a != b:
        raise AssertionError(f"期望 {b}，实际 {a}")

def assert_not_equal(a, b):
    if a == b:
        raise AssertionError(f"期望不等于 {b}，但相等")

def assert_true(x):
    if not x:
        raise AssertionError(f"期望为真，实际为 {x}")

def assert_false(x):
    if x:
        raise AssertionError(f"期望为假，实际为 {x}")


def main():
    """主函数"""
    print("=" * 80)
    print("言语言标准库测试报告")
    print("=" * 80)
    
    # 查找测试文件
    test_dir = Path(__file__).parent
    test_files = [
        test_dir / "test_math.yan",
        test_dir / "test_string.yan",
        test_dir / "test_collections.yan",
        test_dir / "test_time.yan",
    ]
    
    # 过滤存在的文件
    test_files = [f for f in test_files if f.exists()]
    
    if not test_files:
        print("\033[91m未找到测试文件！\033[0m")
        return
    
    # 运行所有测试
    for test_file in test_files:
        run_yan_test(str(test_file))
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
