#!/usr/bin/env python3
"""
言语言测试验证脚本
用于验证测试框架是否正常工作
"""

import sys
import os

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠ 警告: 建议使用 Python 3.8+")
        return False
    return True

def check_required_modules():
    """检查必需的模块"""
    required = ['psutil']
    missing = []

    print("\n检查必需的模块:")
    for module in required:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} (未安装)")
            missing.append(module)

    if missing:
        print(f"\n请安装缺失的模块: pip install {' '.join(missing)}")
        return False
    return True

def test_imports():
    """测试导入"""
    print("\n测试导入:")

    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from yan_test import YanTestFramework, suite, test, run
        print("✓ yan_test 模块")

        from yan_assertions import 断言等, 断言包含, 断言为真
        print("✓ yan_assertions 模块")

        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_simple_test():
    """运行简单测试"""
    print("\n运行简单测试:")

    try:
        from yan_test import YanTestFramework
        from yan_assertions import 断言等, 断言为真

        # 创建简单的测试
        framework = YanTestFramework()

        @framework.suite("验证测试")
        def test_suite():
            @framework.test("基础断言")
            def test_basic():
                断言等(1 + 1, 2)
                断言为真(True)

        # 运行测试
        report = framework.run()

        print(f"\n✓ 简单测试通过: {report.passed}/{report.total}")

        return report.failed == 0

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("言语言测试框架验证")
    print("=" * 80)

    results = []

    # 检查 Python 版本
    print("\n1. 检查 Python 版本")
    results.append(check_python_version())

    # 检查必需模块
    print("\n2. 检查必需模块")
    results.append(check_required_modules())

    # 测试导入
    print("\n3. 测试模块导入")
    results.append(test_imports())

    # 运行简单测试
    print("\n4. 运行简单测试")
    results.append(run_simple_test())

    # 总结
    print("\n" + "=" * 80)
    print("验证结果")
    print("=" * 80)

    if all(results):
        print("\n✓ 所有检查通过！测试框架已准备就绪。")
        print("\n运行完整测试:")
        print("  python tests/run_tests.py")
        print("\n或运行单个测试:")
        print("  python tests/test_math.py")
        print("  python tests/test_string.py")
        return 0
    else:
        print("\n✗ 部分检查失败，请修复上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
