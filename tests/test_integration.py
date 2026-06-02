#!/usr/bin/env python3
"""
整合功能测试
验证言语言编译器的所有功能模块
"""

import sys
sys.path.insert(0, "g:/dumategithub/newlisp")


def test_imports():
    """测试导入所有模块"""
    print("测试模块导入...")
    
    try:
        import yan
        print(f"✓ 言语言版本: {yan.__version__}")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_type_system():
    """测试类型系统"""
    print("\n测试类型系统...")
    
    try:
        from yan.type_system import (
            IntType,
            StringType,
            BoolType,
            ArrayType,
            OptionalType,
            make_array,
            is_numeric_type,
        )
        
        # 测试基本类型
        int_type = IntType()
        str_type = StringType()
        print(f"✓ 基本类型: {int_type}, {str_type}")
        
        # 测试数组类型
        arr_type = make_array(IntType())
        print(f"✓ 数组类型: {arr_type}")
        
        # 测试可选类型
        opt_type = OptionalType(IntType())
        print(f"✓ 可选类型: {opt_type}")
        
        # 测试类型检查
        print(f"✓ 数值类型检查: {is_numeric_type(int_type)}")
        
        return True
    except Exception as e:
        print(f"✗ 类型系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ffi():
    """测试 FFI"""
    print("\n测试 FFI...")
    
    try:
        from yan.ffi import call_external
        
        # 调用 Python 标准库
        result = call_external("math", "sin", 0)
        print(f"✓ 调用 math.sin(0) = {result}")
        
        # 调用 time 模块
        current_time = call_external("time", "time")
        print(f"✓ 获取当前时间戳: {current_time}")
        
        return True
    except Exception as e:
        print(f"✗ FFI 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_macro_system():
    """测试宏系统"""
    print("\n测试宏系统...")
    
    try:
        from yan.macro_system import (
            MacroSystem,
            Macro,
            MacroType,
        )
        
        system = MacroSystem()
        print(f"✓ 宏系统初始化")
        print(f"✓ 内置宏: {system.list_macros()}")
        
        # 定义简单宏
        macro = Macro(
            name="测试宏",
            macro_type=MacroType.FUNCTION,
            args=["x"],
            body="x * 2",
        )
        system.define_macro(macro)
        print(f"✓ 宏定义成功")
        
        return True
    except Exception as e:
        print(f"✗ 宏系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_concurrency():
    """测试并发模块"""
    print("\n测试并发模块...")
    
    try:
        from yan.concurrency import (
            YanThreadPool,
            ConcurrentQueue,
        )
        
        # 测试线程池
        pool = YanThreadPool(max_workers=2)
        
        # 测试队列
        queue = ConcurrentQueue()
        queue.put("测试数据")
        print(f"✓ 队列操作: {queue.get()}")
        
        print(f"✓ 并发模块初始化成功")
        
        pool.shutdown()
        return True
    except Exception as e:
        print(f"✗ 并发测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_codegen_multi():
    """测试多目标代码生成"""
    print("\n测试多目标代码生成...")
    
    try:
        from yan.codegen_multi import compile_yan
        
        # 简单测试代码
        yan_code = """定义 x = 42"""
        
        # 编译到 JavaScript
        js_code = compile_yan(yan_code, "javascript")
        print(f"✓ JavaScript 代码生成")
        
        # 编译到 WebAssembly
        wasm_code = compile_yan(yan_code, "wasm")
        print(f"✓ WebAssembly 代码生成")
        
        return True
    except Exception as e:
        print(f"✗ 代码生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n测试错误处理...")
    
    try:
        from yan.error_recovery import ErrorRecoveryManager
        from yan.smart_error_suggestor import SmartErrorSuggestor
        
        print(f"✓ 错误恢复管理器")
        print(f"✓ 智能错误建议器")
        return True
    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_debugger():
    """测试调试器"""
    print("\n测试调试器...")
    
    try:
        from yan.debugger_enhanced import YanDebuggerEnhanced
        
        debugger = YanDebuggerEnhanced()
        print(f"✓ 调试器初始化成功")
        return True
    except Exception as e:
        print(f"✗ 调试器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_profiler():
    """测试性能分析器"""
    print("\n测试性能分析器...")
    
    try:
        from yan.profiler import (
            YanProfiler,
        )
        
        profiler = YanProfiler()
        profiler.start()
        result = sum(range(1000))
        profiler.stop()
        
        print(f"✓ 性能分析器测试成功 (结果: {result})")
        return True
    except Exception as e:
        print(f"✗ 性能分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_optimizer():
    """测试优化器"""
    print("\n测试优化器...")
    
    try:
        from yan.optimizer import ASTOptimizer
        print(f"✓ 优化器模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 优化器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_core_compiler():
    """测试核心编译器功能"""
    print("\n测试核心编译器功能...")
    
    try:
        # 测试主要模块可以导入
        import yan.lexer
        import yan.parser
        import yan.codegen
        
        print(f"✓ 核心编译器模块导入成功")
        print(f"  - Lexer 可用")
        print(f"  - Parser 可用")
        print(f"  - CodeGen 可用")
        
        return True
    except Exception as e:
        print(f"✗ 核心编译器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("言语言编译器 - 整合功能测试")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_type_system,
        test_ffi,
        test_macro_system,
        test_concurrency,
        test_codegen_multi,
        test_error_handling,
        test_debugger,
        test_profiler,
        test_optimizer,
        test_core_compiler,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"✗ {test.__name__} 异常: {e}")
            results.append((test.__name__, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for name, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("⚠️ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
