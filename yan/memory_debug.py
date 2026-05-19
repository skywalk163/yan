#!/usr/bin/env python3
"""
言语言内存泄漏诊断工具
"""

import sys
import gc
import os
from pathlib import Path
import tracemalloc
from typing import Dict, Any, List, Tuple


def print_memory_usage(prefix: str = ""):
    """打印内存使用情况"""
    import psutil
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"{prefix}内存使用: {memory_mb:.2f} MB")


def debug_module_system():
    """调试模块系统"""
    print("\n=== 模块系统调试 ===")
    
    try:
        import main
        if hasattr(main, '_module_system'):
            ms = main._module_system
            print(f"模块缓存大小: {len(ms.cache)}")
            print(f"模块搜索路径: {len(ms.search_paths)}")
            for i, path in enumerate(ms.search_paths):
                print(f"  {i+1}. {path}")
            print("\n已缓存的模块:")
            for path, module in ms.cache.items():
                print(f"  - {module.name}: {path}")
                print(f"    导出: {list(module.exports.keys())}")
                print(f"    依赖: {module.dependencies}")
    except Exception as e:
        print(f"调试模块系统时出错: {e}")


def debug_global_env():
    """调试全局环境"""
    print("\n=== 全局环境调试 ===")
    
    try:
        import main
        if hasattr(main, '_global_env') and main._global_env is not None:
            env = main._global_env
            print(f"全局环境大小: {len(env)}")
            print("环境中的键（前20个）:")
            keys = list(env.keys())[:20]
            for i, key in enumerate(keys):
                value = env[key]
                value_repr = repr(value)[:50]
                print(f"  {i+1}. {key}: {value_repr}")
            if len(env) > 20:
                print(f"  ... (还有 {len(env)-20} 个)")
    except Exception as e:
        print(f"调试全局环境时出错: {e}")


def run_gc():
    """运行垃圾回收"""
    print("\n=== 垃圾回收 ===")
    gc.collect()
    print(f"不可达对象: {len(gc.garbage)}")


def trace_memory():
    """跟踪内存分配"""
    print("\n=== 内存跟踪 ===")
    tracemalloc.start()
    
    snapshot1 = tracemalloc.take_snapshot()
    
    # 做一些操作以观察内存变化
    print("执行测试操作...")
    
    snapshot2 = tracemalloc.take_snapshot()
    
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    print("\nTop 10 内存增长:")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()


def fix_memory_leaks():
    """修复内存泄漏"""
    print("\n=== 修复内存泄漏 ===")
    
    try:
        import main
        
        # 修复1: 清空模块系统缓存
        if hasattr(main, '_module_system'):
            ms = main._module_system
            cache_size_before = len(ms.cache)
            ms.clear_cache()
            print(f"已清空模块缓存 ({cache_size_before} -> 0)")
        
        # 修复2: 重置全局环境
        if hasattr(main, '_global_env'):
            main._global_env = None
            print("已重置全局环境")
        
        # 修复3: 清理其他全局变量
        import parser
        if hasattr(parser, '_global_user_verbs'):
            parser._global_user_verbs = {}
            print("已重置全局用户动词")
        
        # 运行垃圾回收
        import gc
        gc.collect()
        
        print("✓ 内存泄漏修复完成")
    except Exception as e:
        print(f"修复内存泄漏时出错: {e}")


def main():
    """主入口"""
    print("=" * 60)
    print("言语言内存泄漏诊断工具")
    print("=" * 60)
    
    print_memory_usage("初始")
    
    # 运行诊断
    debug_module_system()
    debug_global_env()
    run_gc()
    
    # 询问是否修复
    print("\n" + "=" * 60)
    print("是否修复内存泄漏？(y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        fix_memory_leaks()
        print_memory_usage("修复后")
    else:
        print("跳过修复")


if __name__ == "__main__":
    main()
