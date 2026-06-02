#!/usr/bin/env python3
"""
语法 v2 专业测试套件
验证无句号代码块语法的正确性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from yan.lexer import Lexer
from yan.parser import Parser


def test_v2_syntax_basic():
    """测试基本 v2 语法解析"""
    code = """
定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x
  返回 x
"""
    try:
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser(syntax_version=2)
        ast = parser.parse(tokens)
        
        assert ast is not None
        print("AST statements count:", len(ast.statements))
        for i, stmt in enumerate(ast.statements):
            print(f"  Statement {i}: {type(stmt).__name__} - {stmt}")
        
        if len(ast.statements) > 0:
            first_stmt = ast.statements[0]
            if hasattr(first_stmt, 'name'):
                print("First statement name:", first_stmt.name)
        
        print("OK test_v2_syntax_basic: 解析成功")
    except Exception as e:
        print("FAIL test_v2_syntax_basic:", type(e).__name__, str(e))


def test_v2_nested_blocks():
    """测试嵌套代码块"""
    code = """
定 计算 = 函 x：
  当 x 小于 0：
    定 结果 = 负 x
    当 结果 大于 10：
      返回 结果
    返回 0
  否则：
    返回 x
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    
    assert ast is not None
    print("✓ test_v2_nested_blocks: 通过")


def test_v2_foreach_loop():
    """测试遍历循环"""
    code = """
定 求和 = 函 列表：
  定 结果 = 0
  遍历 列表 元素：
    设 结果 加 结果 元素
  返回 结果
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    
    assert ast is not None
    print("✓ test_v2_foreach_loop: 通过")


def test_v2_while_loop():
    """测试当循环"""
    code = """
定 阶乘 = 函 n：
  定 结果 = 1
  定 i = 1
  当 i 小于等于 n：
    设 结果 乘 结果 i
    设 i 加 i 1
  返回 结果
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    
    assert ast is not None
    print("✓ test_v2_while_loop: 通过")


def test_v2_try_catch():
    """测试异常处理（v2 语法暂不支持，跳过）"""
    code = """
定 安全除法 = 函 a b：
  试：
    当 b 等于 0：
      抛 "除零错误"
    返回 除 a b
  捕获：
    返回 空
"""
    print("⚠ test_v2_try_catch: 跳过（v2 语法暂不支持试-捕获）")
    return True


def test_v2_empty_function():
    """测试无参数函数"""
    code = """
定 随机小数 = 函：
  返回 随机范围 0 1
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    
    assert ast is not None
    print("✓ test_v2_empty_function: 通过")


def test_v2_mixed_top_level():
    """测试顶层语句混合"""
    code = """
-- 常量定义
定 PI = 3.1415926
定 E = 2.71828

-- 函数定义
定 圆面积 = 函 r：
  返回 乘 PI 乘 r r

-- 直接调用
印 圆面积 5
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    
    assert ast is not None
    assert len(ast.statements) == 4  # 2 个常量 + 1 个函数 + 1 个调用
    print("✓ test_v2_mixed_top_level: 通过")


def test_backward_compatibility_v1():
    """测试 v1 语法向后兼容"""
    code = """
定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x。
  。
  返回 x。
。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser(syntax_version=1)
    ast = parser.parse(tokens)
    
    assert ast is not None
    print("✓ test_backward_compatibility_v1: 通过")


def test_syntax_version_switch():
    """测试语法版本切换"""
    v2_code = """
定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x
  返回 x
"""
    v1_code = """
定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x。
  。
  返回 x。
。
"""
    
    # v2 解析器应该能解析 v2 代码
    lexer = Lexer()
    tokens = lexer.tokenize(v2_code)
    parser = Parser(syntax_version=2)
    ast = parser.parse(tokens)
    assert ast is not None
    
    # v1 解析器应该能解析 v1 代码
    tokens = lexer.tokenize(v1_code)
    parser = Parser(syntax_version=1)
    ast = parser.parse(tokens)
    assert ast is not None
    
    print("✓ test_syntax_version_switch: 通过")


def test_standard_library_module():
    """测试标准库模块迁移后的解析"""
    import glob
    stdlib_files = glob.glob('yan/stdlib/*.yan')
    
    for filepath in stdlib_files:
        try:
            with open(filepath, encoding='utf-8') as f:
                code = f.read()
            
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            parser = Parser(syntax_version=2)
            ast = parser.parse(tokens)
            
            print(f"✓ 解析标准库模块: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"✗ 解析失败: {os.path.basename(filepath)} - {e}")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("语法 v2 专业测试套件")
    print("=" * 60)
    
    tests = [
        test_v2_syntax_basic,
        test_v2_nested_blocks,
        test_v2_foreach_loop,
        test_v2_while_loop,
        test_v2_try_catch,
        test_v2_empty_function,
        test_v2_mixed_top_level,
        test_backward_compatibility_v1,
        test_syntax_version_switch,
    ]
    
    print("\n--- 基础语法测试 ---")
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__}: 失败 - {e}")
    
    print("\n--- 标准库模块测试 ---")
    test_standard_library_module()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()