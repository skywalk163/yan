"""
言语言测试
"""

import sys
sys.path.insert(0, '.')

from main import run


def test_arithmetic():
    """测试算术运算"""
    print("测试算术运算...")
    assert run("10加5。") == 15
    assert run("10减5。") == 5
    assert run("10乘5。") == 50
    assert run("10除5。") == 2.0
    print("  [OK] 算术运算通过")


def test_pipeline():
    """测试管道"""
    print("测试管道...")
    assert run("10加5，乘2。") == 30
    assert run("100减50，除2。") == 25
    print("  [OK] 管道通过")


def test_list():
    """测试列表"""
    print("测试列表...")
    assert run("列1 2 3。") == [1, 2, 3]
    assert run("首列1 2 3。") == 1
    assert run("余列1 2 3。") == [2, 3]
    assert run("长列1 2 3。") == 3
    print("  [OK] 列表通过")


def test_highorder():
    """测试高阶函数"""
    print("测试高阶函数...")
    assert run("列1 2 3，皆乘2。") == [2, 4, 6]
    assert run("列1 2 3 4 5，只大2。") == [3, 4, 5]
    print("  [OK] 高阶函数通过")


def test_define():
    """测试变量定义"""
    print("测试变量定义...")
    run("定x=10。")
    run("定平方=函x乘x x。")
    print("  [OK] 变量定义通过")


def test_lambda():
    """测试匿名函数"""
    print("测试匿名函数...")
    # 定义并调用
    result = run("定平方=函x乘x x。平方5。")
    assert result == 25, f"期望 25，得到 {result}"
    print("  [OK] 匿名函数通过")


def test_factorial():
    """测试递归函数（阶乘）"""
    print("测试递归函数...")
    result = run("定阶乘=函n若n等1则1否则n乘阶乘n减1。阶乘5。")
    assert result == 120, f"期望 120，得到 {result}"
    print("  [OK] 递归函数通过")


def test_comparison():
    """测试比较运算"""
    print("测试比较运算...")
    assert run("5大3。") == True
    assert run("3大5。") == False
    assert run("5小3。") == False
    assert run("3小5。") == True
    assert run("5等5。") == True
    print("  [OK] 比较运算通过")


def test_logic():
    """测试逻辑运算"""
    print("测试逻辑运算...")
    assert run("真且真。") == True
    assert run("真且假。") == False
    assert run("假或真。") == True
    assert run("非假。") == True
    print("  [OK] 逻辑运算通过")


def test_string():
    """测试字符串"""
    print("测试字符串...")
    assert run('"hello"。') == "hello"
    print("  [OK] 字符串通过")


def test_reduce():
    """测试归约"""
    print("测试归约...")
    result = run("列1 2 3，归加0。")
    assert result == 6, f"期望 6，得到 {result}"
    print("  [OK] 归约通过")


def run_all():
    """运行所有测试"""
    print("=" * 40)
    print("言语言 MVP 测试")
    print("=" * 40)
    print()

    test_arithmetic()
    test_pipeline()
    test_list()
    test_highorder()
    test_define()
    test_lambda()
    test_factorial()
    test_comparison()
    test_logic()
    test_string()
    test_reduce()

    print()
    print("=" * 40)
    print("所有测试通过！")
    print("=" * 40)


if __name__ == "__main__":
    run_all()
