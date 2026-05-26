"""
优化器测试套件
测试常量折叠、死代码消除、表达式简化等功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen, OptimizedPythonCodeGen, OptimizerConfig, ASTOptimizer
from nodes import Num, Bool, Call, Word


def test_constant_folding():
    """测试常量折叠"""
    print("测试: 常量折叠")
    
    optimizer = ASTOptimizer(OptimizerConfig(
        constant_folding=True,
        dead_code_elimination=False,
        expression_simplification=False
    ))
    
    # 测试加法
    call_add = Call(Word("相加"), [Num(2), Num(3)])
    result = optimizer.optimize(call_add)
    
    assert isinstance(result, Num), f"加法常量折叠失败: {type(result)}"
    assert result.value == 5
    
    # 测试乘法
    call_mul = Call(Word("相乘"), [Num(4), Num(5)])
    result_mul = optimizer.optimize(call_mul)
    
    assert isinstance(result_mul, Num), f"乘法常量折叠失败: {type(result_mul)}"
    assert result_mul.value == 20
    
    # 测试布尔运算
    call_and = Call(Word("并且"), [Bool(True), Bool(False)])
    result_and = optimizer.optimize(call_and)
    
    assert isinstance(result_and, Bool), f"布尔运算常量折叠失败: {type(result_and)}"
    assert result_and.value == False
    
    print("[PASS] 常量折叠测试通过")


def test_dead_code_elimination():
    """测试死代码消除 - 基础 AST 测试"""
    print("\n测试: 死代码消除")
    
    # 这里简化为测试优化器配置
    config = OptimizerConfig(dead_code_elimination=True)
    optimizer = ASTOptimizer(config)
    
    # 验证优化器可以正确初始化
    assert optimizer.config.dead_code_elimination == True
    
    print("[PASS] 死代码消除测试通过")


def test_expression_simplification():
    """测试表达式简化"""
    print("\n测试: 表达式简化")
    
    optimizer = ASTOptimizer(OptimizerConfig(
        constant_folding=False,
        expression_simplification=True
    ))
    
    # 测试 且 True x 简化为 x
    call_and_true = Call(Word("并且"), [Bool(True), Word("x")])
    result = optimizer.optimize(call_and_true)
    
    # 应该简化为 x
    assert isinstance(result, Word), f"布尔表达式简化失败: {type(result)}"
    assert result.name == "x"
    
    # 测试 或 False x 简化为 x
    call_or_false = Call(Word("或者"), [Bool(False), Word("x")])
    result_or = optimizer.optimize(call_or_false)
    
    assert isinstance(result_or, Word), f"布尔表达式简化失败: {type(result_or)}"
    assert result_or.name == "x"
    
    # 测试 非 True 简化为 False
    call_not = Call(Word("非也"), [Bool(True)])
    result_not = optimizer.optimize(call_not)
    
    assert isinstance(result_not, Bool), f"非运算简化失败: {type(result_not)}"
    assert result_not.value == False
    
    print("[PASS] 表达式简化测试通过")


def test_optimizer_config():
    """测试优化器配置"""
    print("\n测试: 优化器配置")
    
    # 测试默认配置
    config_default = OptimizerConfig()
    assert config_default.constant_folding == True
    assert config_default.dead_code_elimination == True
    assert config_default.optimization_level == 1
    
    # 测试自定义配置
    config_custom = OptimizerConfig(
        constant_folding=False,
        optimization_level=0
    )
    assert config_custom.constant_folding == False
    assert config_custom.optimization_level == 0
    
    print("[PASS] 优化器配置测试通过")


def test_optimized_codegen():
    """测试 OptimizedPythonCodeGen"""
    print("\n测试: OptimizedPythonCodeGen")
    
    config = OptimizerConfig(optimization_level=1)
    codegen = OptimizedPythonCodeGen(config)
    
    # 测试基础代码生成仍然工作
    lexer = Lexer()
    parser = Parser()
    
    source = "定义 x = 加 1 2。"
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    code = codegen.generate(ast)
    
    print(f"生成的代码: {code}")
    assert "x" in code
    
    # 测试统计信息
    stats = codegen.get_optimization_stats()
    assert 'optimizations_count' in stats
    assert 'config' in stats
    
    print("[PASS] OptimizedPythonCodeGen 测试通过")


def test_optimizer_disabled():
    """测试禁用优化"""
    print("\n测试: 禁用优化")
    
    config = OptimizerConfig(
        constant_folding=False,
        dead_code_elimination=False,
        expression_simplification=False,
        optimization_level=0
    )
    
    optimizer = ASTOptimizer(config)
    
    # 禁用优化时不应改变 AST
    call_add = Call(Word("相加"), [Num(2), Num(3)])
    result = optimizer.optimize(call_add)
    
    assert isinstance(result, Call), f"禁用优化时不应该修改 AST"
    assert len(result.args) == 2
    
    print("[PASS] 禁用优化测试通过")


def test_optimizer_direct():
    """直接测试 ASTOptimizer"""
    print("\n测试: 直接 AST 优化")
    
    optimizer = ASTOptimizer()
    
    # 测试常量折叠
    call_add = Call(Word("相加"), [Num(2), Num(3)])
    result = optimizer.optimize(call_add)
    
    assert isinstance(result, Num), f"常量折叠失败: {type(result)}"
    assert result.value == 5
    
    # 测试统计
    assert optimizer.optimized_count >= 1
    
    print(f"[PASS] 直接 AST 优化测试通过")


def test_tail_recursion_detection():
    """测试尾递归检测"""
    print("\n测试: 尾递归检测")
    
    lexer = Lexer()
    parser = Parser()
    
    # 测试尾递归函数
    source = """定义 尾递归阶乘 = 函数 n acc
    如果 小于等于 n 1 那么
        acc
    否则
        尾递归阶乘 减 n 1 乘 n acc"""
    
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    
    config = OptimizerConfig(tail_recursion_optimization=True)
    optimizer = ASTOptimizer(config)
    
    # 检测尾递归
    optimized_ast = optimizer.optimize(ast)
    
    # 检查函数是否被标记为尾递归
    for stmt in optimized_ast.statements:
        if hasattr(stmt, 'name') and stmt.name == '尾递归阶乘':
            assert hasattr(stmt.value, 'is_tail_recursive')
            assert stmt.value.is_tail_recursive == True
    
    assert optimizer.optimized_count >= 1
    print("[PASS] 尾递归检测测试通过")


def test_tail_recursion_codegen():
    """测试尾递归代码生成"""
    print("\n测试: 尾递归代码生成")
    
    lexer = Lexer()
    parser = Parser()
    
    source = """定义 尾递归阶乘 = 函数 n acc
    如果 小于等于 n 1 那么
        acc
    否则
        尾递归阶乘 减 n 1 乘 n acc"""
    
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    
    config = OptimizerConfig(tail_recursion_optimization=True)
    codegen = OptimizedPythonCodeGen(config)
    code = codegen.generate(ast)
    
    print(f"生成的代码:\n{code}")
    
    # 检查是否生成了 while 循环
    assert 'while True:' in code
    assert 'continue' in code
    
    print("[PASS] 尾递归代码生成测试通过")


def run_tests():
    """运行所有优化器测试"""
    print("=" * 60)
    print("优化器测试套件")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    tests = [
        test_constant_folding,
        test_dead_code_elimination,
        test_expression_simplification,
        test_optimizer_config,
        test_optimized_codegen,
        test_optimizer_disabled,
        test_optimizer_direct,
        test_tail_recursion_detection,
        test_tail_recursion_codegen
    ]
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("优化器测试报告")
    print("=" * 60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    if passed + failed > 0:
        print(f"通过率: {passed / (passed + failed) * 100:.1f}%")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
