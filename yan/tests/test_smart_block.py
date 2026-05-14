"""
测试智能块推断机制
"""
import pytest
import sys
import os

# 添加父目录到路径以便导入 yan 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import BlockStack


class TestBlockStack:
    """测试 BlockStack 类"""

    def test_block_stack_push_pop(self):
        """测试 push/pop 操作"""
        stack = BlockStack()

        # 空栈
        assert stack.is_empty() is True
        assert stack.depth() == 0

        # 压入一个块
        stack.push('if', 4)
        assert stack.is_empty() is False
        assert stack.depth() == 1

        # 获取当前块
        current = stack.current()
        assert current is not None
        assert current['type'] == 'if'
        assert current['indent'] == 4

        # 压入另一个块
        stack.push('while', 8)
        assert stack.depth() == 2

        current = stack.current()
        assert current['type'] == 'while'
        assert current['indent'] == 8

        # 弹出块
        popped = stack.pop()
        assert popped['type'] == 'while'
        assert popped['indent'] == 8
        assert stack.depth() == 1

        current = stack.current()
        assert current['type'] == 'if'

        # 弹出最后一个块
        popped = stack.pop()
        assert popped['type'] == 'if'
        assert stack.is_empty() is True
        assert stack.depth() == 0

    def test_block_stack_empty(self):
        """测试空栈行为"""
        stack = BlockStack()

        # 空栈检查
        assert stack.is_empty() is True
        assert stack.depth() == 0

        # 空栈调用 current() 应返回 None
        assert stack.current() is None

        # 空栈调用 pop() 应返回 None
        assert stack.pop() is None

    def test_block_stack_depth(self):
        """测试栈深度"""
        stack = BlockStack()

        assert stack.depth() == 0

        stack.push('if', 4)
        assert stack.depth() == 1

        stack.push('while', 8)
        assert stack.depth() == 2

        stack.push('for', 12)
        assert stack.depth() == 3

        stack.pop()
        assert stack.depth() == 2

        stack.pop()
        assert stack.depth() == 1

        stack.pop()
        assert stack.depth() == 0


class TestShouldEndBlock:
    """测试 _should_end_block() 方法"""

    def test_should_end_block_at_eof(self):
        """测试文件结束时结束块"""
        from lexer import Lexer
        from parser import Parser

        code = "定x=1。"
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        parser.tokens = tokens
        parser.pos = len(tokens) - 1  # 指向 EOF

        assert parser._should_end_block(0) == True

    def test_should_end_block_at_define(self):
        """测试遇到新定义时结束块"""
        from lexer import Lexer
        from parser import Parser

        code = "定x=1。定y=2。"
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        parser.tokens = tokens
        parser.pos = 5  # 指向第二个 '定'

        assert parser._should_end_block(0) == True

    def test_should_end_block_at_if(self):
        """测试遇到条件语句时结束块"""
        from lexer import Lexer
        from parser import Parser

        code = "若真则1。若假则0。"
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        parser.tokens = tokens
        parser.pos = 5  # 指向第二个 '若'

        assert parser._should_end_block(0) == True

    def test_should_not_end_block_in_middle(self):
        """测试块中间不应结束"""
        from lexer import Lexer
        from parser import Parser

        code = "定x=1。定y=2。"
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        parser.tokens = tokens
        parser.pos = 1  # 指向 'x'

        assert parser._should_end_block(0) == False


class TestParseBlock:
    """测试 _parse_block() 方法"""

    def test_parse_single_line_block(self):
        """测试单行块"""
        from lexer import Lexer
        from parser import Parser

        code = "定x=1。"
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        assert ast.statements[0].name == 'x'

    def test_parse_multi_line_block_auto_end(self):
        """测试多行块自动结束"""
        from lexer import Lexer
        from parser import Parser

        code = """
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        # 验证函数定义
        define = ast.statements[0]
        assert define.name == '距离'
        # 验证函数体是 Block
        assert hasattr(define.value, 'body')
        # 验证块包含 2 个语句
        assert hasattr(define.value.body, 'statements')
        assert len(define.value.body.statements) == 2

    def test_parse_consecutive_definitions(self):
        """测试连续定义"""
        from lexer import Lexer
        from parser import Parser

        code = """
定x=1。
定y=2。
定z=加x y。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 3
        assert ast.statements[0].name == 'x'
        assert ast.statements[1].name == 'y'
        assert ast.statements[2].name == 'z'


class TestFunctionDefinition:
    """测试函数定义解析"""

    def test_single_line_function(self):
        """测试单行函数"""
        from lexer import Lexer
        from parser import Parser

        code = "定阶乘=函n 若n等1则1否则n乘阶乘n减1。"
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        define = ast.statements[0]
        assert define.name == '阶乘'
        # 验证是 Lambda
        assert hasattr(define.value, 'params')
        assert define.value.params == ['n']

    def test_multi_line_function(self):
        """测试多行函数"""
        from lexer import Lexer
        from parser import Parser

        code = """
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        define = ast.statements[0]
        assert define.name == '距离'
        # 验证是 Lambda
        assert hasattr(define.value, 'params')
        assert define.value.params == ['a', 'b']
        # 验证 body 是 Block
        assert hasattr(define.value.body, 'statements')
        assert len(define.value.body.statements) == 2


class TestIfWithBlock:
    """测试带块的条件语句"""

    def test_if_with_block(self):
        """测试带块的条件语句"""
        from lexer import Lexer
        from parser import Parser

        code = """
若x大0则：
  印"正数"。
  印x。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        if_node = ast.statements[0]
        # 验证是 If 节点
        assert hasattr(if_node, 'cond')
        assert hasattr(if_node, 'then_branch')
        # 验证 then_branch 是 Block
        assert hasattr(if_node.then_branch, 'statements')
        assert len(if_node.then_branch.statements) == 2

    def test_if_else_with_block(self):
        """测试带 else 块的条件语句"""
        from lexer import Lexer
        from parser import Parser

        code = """
若x大0则：
  印"正数"。
否则：
  印"非正数"。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        if_node = ast.statements[0]
        # 验证有 else 分支
        assert if_node.else_branch is not None
        assert hasattr(if_node.else_branch, 'statements')


class TestLoopWithBlock:
    """测试带块的循环语句"""

    def test_foreach_with_block(self):
        """测试遍历循环"""
        from lexer import Lexer
        from parser import Parser

        code = """
遍历x 于 列1 2 3：
  印x。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        foreach = ast.statements[0]
        # 验证是 ForEach 节点
        assert hasattr(foreach, 'var')
        assert foreach.var == 'x'
        assert hasattr(foreach, 'iterable')
        assert hasattr(foreach, 'body')

    def test_while_with_block(self):
        """测试当循环"""
        from lexer import Lexer
        from parser import Parser

        code = """
当x小10：
  印x。
  定x=加x 1。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        while_node = ast.statements[0]
        # 验证是 While 节点
        assert hasattr(while_node, 'cond')
        assert hasattr(while_node, 'body')

    def test_nested_loops(self):
        """测试嵌套循环"""
        from lexer import Lexer
        from parser import Parser

        code = """
遍历x 于 列1 2 3：
  遍历y 于 列4 5：
    印x。
    印y。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        outer_foreach = ast.statements[0]
        assert hasattr(outer_foreach, 'var')
        assert outer_foreach.var == 'x'
        # 验证外层循环体包含内层循环
        # 当循环体只有一个语句时，_parse_block 返回该语句本身
        assert hasattr(outer_foreach.body, 'var')
        assert outer_foreach.body.var == 'y'

    def test_while_with_complex_condition(self):
        """测试带复杂条件的当循环"""
        from lexer import Lexer
        from parser import Parser

        code = """
当x小10且y大5：
  印x。
  印y。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        while_node = ast.statements[0]
        # 验证是 While 节点
        assert hasattr(while_node, 'cond')
        # 验证条件是中缀表达式链
        assert hasattr(while_node.cond, 'verb')
        assert hasattr(while_node, 'body')


class TestTestFramework:
    """测试测试框架解析"""

    def test_test_suite_auto_end(self):
        """测试测试套件自动结束"""
        from lexer import Lexer
        from parser import Parser

        code = """
套 "算术运算测试"：
  测 "加法运算"：
    断言等 加 1 2 3。

  测 "减法运算"：
    断言等 减 5 3 2。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        suite = ast.statements[0]
        # 验证是 TestSuite
        assert hasattr(suite, 'tests')
        assert len(suite.tests) == 2

    def test_test_suite_with_multiple_tests(self):
        """测试套件包含多个测试"""
        from lexer import Lexer
        from parser import Parser

        code = """
套 "数据操作测试"：
  测 "数据创建"：
    定 数据 = 列 1 2 3。
    断言等 长 数据 3。

  测 "首元素"：
    定 数据 = 列 1 2 3。
    断言等 首 数据 1。

  测 "余元素"：
    定 数据 = 列 1 2 3。
    断言等 余 数据 列 2 3。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        suite = ast.statements[0]
        assert hasattr(suite, 'tests')
        assert len(suite.tests) == 3

    def test_multiple_test_suites(self):
        """测试多个测试套件"""
        from lexer import Lexer
        from parser import Parser

        code = """
套 "算术测试"：
  测 "加法"：
    断言等 加 1 2 3。

套 "数据测试"：
  测 "列表"：
    断言等 长 列 1 2 3 3。
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 2
        # 第一个套件
        suite1 = ast.statements[0]
        assert hasattr(suite1, 'tests')
        assert len(suite1.tests) == 1
        # 第二个套件
        suite2 = ast.statements[1]
        assert hasattr(suite2, 'tests')
        assert len(suite2.tests) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
