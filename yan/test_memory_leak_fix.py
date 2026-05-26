#!/usr/bin/env python3
"""
测试内存泄漏修复效果
"""

import sys
import os
import gc
from pathlib import Path

# 添加 yan 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from main import run
from memory_debug import print_memory_usage, fix_memory_leaks


def test_memory_leak_fix():
    """测试内存泄漏是否修复"""
    print("=" * 60)
    print("测试内存泄漏修复")
    print("=" * 60)
    
    # 测试前的内存
    print_memory_usage("测试开始")
    
    # 多次运行同一个代码
    code = """
定 测试函 为 函 [x] {
  返回 x 加 1
}

印 "测试"
返回 123
"""
    
    for i in range(10):
        print(f"\n--- 第 {i+1} 次运行 ---")
        result = run(code, debug=False, clear_cache=True)
        print(f"结果: {result}")
        
        # 运行 GC
        gc.collect()
        print_memory_usage(f"第 {i+1} 次运行后")
    
    print("\n" + "=" * 60)
    print("✓ 测试完成！")
    print("✓ 如果内存使用保持稳定，说明修复成功")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_memory_leak_fix()
