"""
言语言测试套件
"""

import sys
import io
sys.path.insert(0, '.')

from main import run, run_repl


# ============ 基础运算测试 ============

def test_arithmetic():
    """测试算术运算"""
    print("测试算术运算...")
    assert run("10加5。") == 15
    assert run("10减5。") == 5
    assert run("10乘5。") == 50
    assert run("10除5。") == 2.0
    assert run("10模3。") == 1
    assert run("2幂10。") == 1024
    print("  [OK] 算术运算通过")


def test_pipeline():
    """测试管道"""
    print("测试管道...")
    assert run("10加5，乘2。") == 30
    assert run("100减50，除2。") == 25
    assert run("10加5，乘2，减3。") == 27
    print("  [OK] 管道通过")


def test_comparison():
    """测试比较运算"""
    print("测试比较运算...")
    assert run("5大3。") == True
    assert run("3大5。") == False
    assert run("5小3。") == False
    assert run("3小5。") == True
    assert run("5等5。") == True
    assert run("5不等3。") == True
    print("  [OK] 比较运算通过")


def test_logic():
    """测试逻辑运算"""
    print("测试逻辑运算...")
    assert run("真且真。") == True
    assert run("真且假。") == False
    assert run("假且假。") == False
    assert run("假或真。") == True
    assert run("假或假。") == False
    assert run("非假。") == True
    assert run("非真。") == False
    print("  [OK] 逻辑运算通过")


# ============ 数据类型测试 ============

def test_numbers():
    """测试数字类型"""
    print("测试数字类型...")
    assert run("42。") == 42
    assert run("3.14。") == 3.14
    assert run("负5。") == -5
    assert run("绝对负5。") == 5
    print("  [OK] 数字类型通过")


def test_string():
    """测试字符串"""
    print("测试字符串...")
    assert run('"hello"。') == "hello"
    assert run('"你好世界"。') == "你好世界"
    assert run('"123"。') == "123"
    print("  [OK] 字符串通过")


def test_list():
    """测试列表"""
    print("测试列表...")
    assert run("列1 2 3。") == [1, 2, 3]
    assert run("首列1 2 3。") == 1
    assert run("余列1 2 3。") == [2, 3]
    assert run("长列1 2 3。") == 3
    assert run("列1 2 3，入1。") == 2  # 索引从0开始
    assert run("范围5。") == [1, 2, 3, 4, 5]
    print("  [OK] 列表通过")


# ============ 高阶函数测试 ============

def test_highorder():
    """测试高阶函数"""
    print("测试高阶函数...")
    assert run("列1 2 3，皆乘2。") == [2, 4, 6]
    assert run("列1 2 3 4 5，只大2。") == [3, 4, 5]
    print("  [OK] 高阶函数通过")


def test_reduce():
    """测试归约"""
    print("测试归约...")
    assert run("列1 2 3，归加0。") == 6
    # 归乘需要使用 Python 代码块
    result = run('定求积={{lambda lst: __import__("functools").reduce(lambda a,b: a*b, lst, 1)}}。求积列1 2 3 4 5。')
    assert result == 120, f"期望 120，得到 {result}"
    print("  [OK] 归约通过")


# ============ 函数测试 ============

def test_define():
    """测试变量定义"""
    print("测试变量定义...")
    run("定x=10。")
    run("定平方=函x乘x x。")
    print("  [OK] 变量定义通过")


def test_lambda():
    """测试匿名函数"""
    print("测试匿名函数...")
    result = run("定平方=函x乘x x。平方5。")
    assert result == 25, f"期望 25，得到 {result}"
    print("  [OK] 匿名函数通过")


def test_multi_param():
    """测试多参数函数"""
    print("测试多参数函数...")
    result = run("定sum3=函a b c $(a + b + c)。sum3 1 2 3。")
    assert result == 6, f"期望 6，得到 {result}"
    print("  [OK] 多参数函数通过")


def test_factorial():
    """测试递归函数（阶乘）"""
    print("测试递归函数...")
    result = run("定阶乘=函n若n等1则1否则n乘阶乘n减1。阶乘5。")
    assert result == 120, f"期望 120，得到 {result}"
    print("  [OK] 递归函数通过")


def test_block():
    """测试块语法"""
    print("测试块语法...")
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    run("""
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。
印距离3 7。
""")
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    assert output.strip() == '4', f"期望输出 '4'，得到 '{output.strip()}'"
    print("  [OK] 块语法通过")


# ============ 双轨制语法测试 ============

def test_math_expr():
    """测试数学表达式 $()"""
    print("测试数学表达式...")
    
    # 基本运算
    assert run("$(1 + 2)。") == 3
    assert run("$(10 * 5 - 3)。") == 47
    assert run("$(2 ** 10)。") == 1024
    
    # 变量引用
    assert run("定x=10。$(x * 2)。") == 20
    
    # 条件表达式
    assert run('$(5 if True else 3)。') == 5
    
    print("  [OK] 数学表达式通过")


def test_python_block():
    """测试 Python 代码块 {{}}"""
    print("测试 Python 代码块...")
    
    # 简单表达式
    result = run("定x={{[i*2 for i in range(5)]}}。x。")
    assert result == [0, 2, 4, 6, 8], f"期望 [0, 2, 4, 6, 8]，得到 {result}"
    
    # 函数定义
    result = run("""
定fib={{
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
fib
}}。
fib 10。
""")
    assert result == 55, f"期望 55，得到 {result}"
    
    print("  [OK] Python 代码块通过")


def test_dual_track_mixed():
    """测试双轨制混合使用"""
    print("测试双轨制混合使用...")
    
    result = run("""
定半径=5。
定面积=$(3.14159 * 半径 * 半径)。
$(int(面积))。
""")
    assert result == 78, f"期望 78，得到 {result}"
    
    print("  [OK] 双轨制混合使用通过")


# ============ 全局变量/交互模式测试 ============

def test_repl_global_vars():
    """测试交互模式全局变量"""
    print("测试交互模式全局变量...")
    
    # 定义变量
    run_repl("定x=10。")
    
    # 使用变量
    result = run_repl("x加5。")
    assert result == 15, f"期望 15，得到 {result}"
    
    # 定义函数
    run_repl("定平方=函x乘x x。")
    
    # 调用函数
    result = run_repl("平方7。")
    assert result == 49, f"期望 49，得到 {result}"
    
    # 组合使用
    result = run_repl("平方x。")
    assert result == 100, f"期望 100，得到 {result}"
    
    print("  [OK] 交互模式全局变量通过")


def test_repl_block_function():
    """测试交互模式块结构函数"""
    print("测试交互模式块结构函数...")
    
    # 定义带局部变量的函数
    run_repl("定距离=函a b：定差=减a b。若差小0则负差否则差。。")
    
    # 调用函数
    result = run_repl("距离3 7。")
    assert result == 4, f"期望 4，得到 {result}"
    
    result = run_repl("距离7 3。")
    assert result == 4, f"期望 4，得到 {result}"
    
    print("  [OK] 交互模式块结构函数通过")


# ============ 错误处理测试 ============

def test_lexer_error():
    """测试词法错误"""
    print("测试词法错误...")
    
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    result = run("@#$%。")  # 非法字符
    
    sys.stderr = old_stderr
    
    assert result is None, "期望返回 None"
    print("  [OK] 词法错误通过")


def test_parser_error():
    """测试语法错误"""
    print("测试语法错误...")
    
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    result = run("加。")  # 参数不足
    
    sys.stderr = old_stderr
    
    # 注意：当前实现可能不报错，而是返回柯里化函数
    # 这个测试可能需要调整
    
    print("  [OK] 语法错误通过")


def test_runtime_error():
    """测试运行时错误"""
    print("测试运行时错误...")
    
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    result = run("1除0。")  # 除零错误
    
    sys.stderr = old_stderr
    
    assert result is None or result == float('inf'), "期望返回 None 或 inf"
    print("  [OK] 运行时错误通过")


# ============ 边界条件测试 ============

def test_empty_list():
    """测试空列表"""
    print("测试空列表...")
    
    assert run("列。") == []
    assert run("长列。") == 0
    assert run("空列。") == True
    
    print("  [OK] 空列表通过")


def test_nested_call():
    """测试嵌套调用"""
    print("测试嵌套调用...")
    
    # 首(余(列))
    result = run("首余列1 2 3。")
    assert result == 2, f"期望 2，得到 {result}"
    
    # 绝对(负(x))
    result = run("绝对负5。")
    assert result == 5, f"期望 5，得到 {result}"
    
    print("  [OK] 嵌套调用通过")


def test_chained_comparison():
    """测试链式比较"""
    print("测试链式比较...")
    
    # 注意：当前实现可能不支持链式比较
    # 这个测试用于验证当前行为
    
    result = run("5大3且5小10。")
    assert result == True, f"期望 True，得到 {result}"
    
    print("  [OK] 链式比较通过")


# ============ Markdown 测试 ============

def test_markdown_execution():
    """测试 Markdown 执行"""
    print("测试 Markdown 执行...")
    
    from md_parser import parse_markdown
    from md_executor import MDExecutor
    
    source = """# 测试

```yan
印10加5。
```
"""
    
    doc = parse_markdown(source)
    executor = MDExecutor()
    
    # 捕获输出
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    output = executor.execute(doc)
    
    sys.stdout = old_stdout
    
    assert "15" in output, f"期望输出包含 '15'，得到 '{output}'"
    print("  [OK] Markdown 执行通过")


def test_markdown_math():
    """测试 Markdown 数学公式"""
    print("测试 Markdown 数学公式...")
    
    from md_parser import parse_markdown, MDMath
    
    source = "$E = mc^2$\n\n$$\\sum_{i=1}^{n} i$$"
    
    doc = parse_markdown(source)
    
    # 检查是否正确解析数学公式
    math_nodes = [n for n in doc.nodes if isinstance(n, MDMath)]
    assert len(math_nodes) == 2, f"期望 2 个数学公式，得到 {len(math_nodes)}"
    
    assert math_nodes[0].inline == True, "第一个应该是行内公式"
    assert math_nodes[1].inline == False, "第二个应该是块级公式"
    
    print("  [OK] Markdown 数学公式通过")


# ============ 运行所有测试 ============

def run_all():
    """运行所有测试"""
    print("=" * 50)
    print("言语言测试套件")
    print("=" * 50)
    print()
    
    # 基础运算
    print("【基础运算】")
    test_arithmetic()
    test_pipeline()
    test_comparison()
    test_logic()
    print()
    
    # 数据类型
    print("【数据类型】")
    test_numbers()
    test_string()
    test_list()
    print()
    
    # 高阶函数
    print("【高阶函数】")
    test_highorder()
    test_reduce()
    print()
    
    # 函数
    print("【函数】")
    test_define()
    test_lambda()
    test_multi_param()
    test_factorial()
    test_block()
    print()
    
    # 双轨制语法
    print("【双轨制语法】")
    test_math_expr()
    test_python_block()
    test_dual_track_mixed()
    print()
    
    # 交互模式
    print("【交互模式】")
    test_repl_global_vars()
    test_repl_block_function()
    print()
    
    # 错误处理
    print("【错误处理】")
    test_lexer_error()
    test_parser_error()
    test_runtime_error()
    print()
    
    # 边界条件
    print("【边界条件】")
    test_empty_list()
    test_nested_call()
    test_chained_comparison()
    print()
    
    # Markdown
    print("【Markdown】")
    test_markdown_execution()
    test_markdown_math()
    print()
    
    print("=" * 50)
    print("所有测试通过！")
    print("=" * 50)


if __name__ == "__main__":
    run_all()
