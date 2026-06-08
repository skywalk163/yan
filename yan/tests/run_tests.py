#!/usr/bin/env python3
"""
言语言测试运行器
运行所有标准库测试
"""

import os
import sys
import time
import psutil
import threading
from pathlib import Path

# 内存限制（单位：字节）
MAX_MEMORY_BYTES = 20 * 1024 * 1024 * 1024  # 20GB
MEMORY_CHECK_INTERVAL = 1.0  # 每秒检查一次内存


class MemoryMonitor:
    """内存监控器"""

    def __init__(self, max_memory: int = MAX_MEMORY_BYTES):
        self.max_memory = max_memory
        self.current_memory = 0
        self.running = False
        self.thread = None
        self.process = psutil.Process(os.getpid())

    def start(self):
        """启动内存监控"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """停止内存监控"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def _monitor(self):
        """监控循环"""
        while self.running:
            try:
                # 获取当前进程及其子进程的内存占用
                memory_info = self.process.memory_info()
                children_memory = 0

                try:
                    for child in self.process.children(recursive=True):
                        try:
                            children_memory += child.memory_info().rss
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                self.current_memory = memory_info.rss + children_memory

                # 检查是否超过内存限制
                if self.current_memory > self.max_memory:
                    print(f"\n\033[91m! Warning: Memory usage exceeds limit ({self.current_memory / (1024**3):.2f}GB > {self.max_memory / (1024**3):.2f}GB)\033[0m")
                    self._cleanup_large_objects()
                    time.sleep(1)

            except Exception as e:
                print(f"\nMemory monitor error: {e}")

            time.sleep(MEMORY_CHECK_INTERVAL)

    def _cleanup_large_objects(self):
        """清理大型对象"""
        try:
            import gc
            gc.collect()
        except Exception as e:
            print(f"Error cleaning up objects: {e}")

    def get_memory_usage(self):
        """获取当前内存占用"""
        return self.current_memory


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.memory_monitor = MemoryMonitor()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.total_time = 0

    def print_header(self):
        """打印测试报告头部"""
        print("=" * 80)
        print("Yan Language Standard Library Test Report")
        print("=" * 80)
        print()

    def print_summary(self):
        """打印测试摘要"""
        print()
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        print(f"  Total tests: {self.total_tests}")
        print(f"  Passed: {self.passed_tests}")
        print(f"  Failed: {self.failed_tests}")
        print(f"  Errors: {self.error_tests}")
        print(f"  Skipped: {self.skipped_tests}")
        print(f"  Total time: {self.total_time:.2f}s")
        print()

        # 打印内存占用统计
        memory_usage = self.memory_monitor.get_memory_usage()
        print(f"  Max memory usage: {memory_usage / (1024**3):.2f}GB")
        print(f"  Memory limit: {MAX_MEMORY_BYTES / (1024**3):.2f}GB")
        print("=" * 80)

        # 根据测试结果打印不同的消息
        if self.failed_tests == 0 and self.error_tests == 0:
            print("\033[92m[PASS] All tests passed!\033[0m")
        else:
            print("\033[91m[FAIL] Some tests failed\033[0m")

    def run_test_file(self, test_file: str):
        """运行单个测试文件"""
        print(f"\nRunning test: {test_file}")
        print("-" * 80)

        try:
            # 创建测试模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules["test_module"] = module
            spec.loader.exec_module(module)

            # 获取测试结果
            start_time = time.time()

            # 运行测试
            from yan_test import run, print_summary
            report = run()

            elapsed = time.time() - start_time

            # 更新统计
            self.total_tests += report.total
            self.passed_tests += report.passed
            self.failed_tests += report.failed
            self.error_tests += report.errors
            self.skipped_tests += report.skipped
            self.total_time += elapsed

            print(f"\nTest file completed, elapsed: {elapsed:.2f}s")

        except Exception as e:
            print(f"\033[91mError: Cannot load test file {test_file}\033[0m")
            print(f"Error info: {e}")
            import traceback
            traceback.print_exc()

    def run_all_tests(self):
        """运行所有测试"""
        start_time = time.time()

        # 启动内存监控
        print("Starting memory monitor...")
        self.memory_monitor.start()
        print(f"Memory limit: {MAX_MEMORY_BYTES / (1024**3):.2f}GB")
        print()

        # 查找所有测试文件
        test_dir = Path(__file__).parent
        test_files = [
            test_dir / "test_math.py",
            test_dir / "test_string.py",
            test_dir / "test_collections.py",
            test_dir / "test_time.py",
        ]

        # 过滤存在的文件
        test_files = [f for f in test_files if f.exists()]

        if not test_files:
            print("\033[91mNo test files found!\033[0m")
            return

        # 打印头部
        self.print_header()

        # 运行所有测试
        for test_file in test_files:
            self.run_test_file(str(test_file))

        # 停止内存监控
        self.memory_monitor.stop()

        # 打印摘要
        self.print_summary()

        # 返回退出码
        return 0 if self.failed_tests == 0 and self.error_tests == 0 else 1


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="言语言测试运行器")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-q", "--quiet", action="store_true", help="安静模式")
    parser.add_argument("-f", "--failfast", action="store_true", help="快速失败")
    parser.add_argument("-m", "--memory", type=str, default="20G", help="内存限制 (如: 20G, 1T)")
    args = parser.parse_args()

    # 解析内存限制
    global MAX_MEMORY_BYTES
    if args.memory.endswith("G"):
        MAX_MEMORY_BYTES = int(args.memory[:-1]) * 1024 * 1024 * 1024
    elif args.memory.endswith("M"):
        MAX_MEMORY_BYTES = int(args.memory[:-1]) * 1024 * 1024
    elif args.memory.endswith("T"):
        MAX_MEMORY_BYTES = int(args.memory[:-1]) * 1024 * 1024 * 1024 * 1024

    # 创建测试运行器
    runner = TestRunner()

    # 运行测试
    exit_code = runner.run_all_tests()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
