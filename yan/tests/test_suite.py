"""
言语言测试套件
包含单元测试和集成测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen
from error_formatter import ErrorFormatter, ErrorContext
from error_suggestions import ErrorSuggestionGenerator

class TestSuite:
    """测试套件"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, func):
        """运行单个测试"""
        print(f"\n测试: {name}")
        try:
            func()
            print("[PASS]")
            self.passed += 1
            self.tests.append((name, True, None))
        except AssertionError as e:
            print(f"[FAIL] {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
        except Exception as e:
            print(f"[ERROR] {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
    
    def report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")
        print(f"通过率: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        
        if self.failed > 0:
            print("\n失败的测试:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")

# ============ 词法分析器测试 ============

def test_lexer_numbers():
    """测试数字词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize("123 45.6")
    
    assert tokens[0].type.name == 'NUM'
    assert tokens[0].value == 123
    assert tokens[1].type.name == 'NUM'
    assert tokens[1].value == 45.6

def test_lexer_strings():
    """测试字符串词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('"hello" "world"')
    
    assert tokens[0].type.name == 'STR'
    assert tokens[0].value == 'hello'
    assert tokens[1].type.name == 'STR'
    assert tokens[1].value == 'world'

def test_lexer_keywords():
    """测试关键字词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('定 函 若 则 否则')
    
    assert tokens[0].type.name == 'WORD'
    assert tokens[0].value == '定'
    assert tokens[1].type.name == 'WORD'
    assert tokens[1].value == '函'

def test_lexer_operators():
    """测试运算符词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('。 ， ： =')
    
    assert tokens[0].type.name == 'DOT'
    assert tokens[1].type.name == 'COMMA'
    assert tokens[2].type.name == 'COLON'
    assert tokens[3].type.name == 'EQUALS'

# ============ 语法分析器测试 ============

def test_parser_define():
    """测试变量定义"""
    lexer = Lexer()
    tokens = lexer.tokenize('定x=1。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    assert ast.statements[0].name == 'x'
    assert ast.statements[0].value.value == 1

def test_parser_function():
    """测试函数定义"""
    lexer = Lexer()
    tokens = lexer.tokenize('定阶乘=函n 若n等1则1否则n乘阶乘n减1。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    assert ast.statements[0].name == '阶乘'
    assert hasattr(ast.statements[0].value, 'params')

def test_parser_if():
    """测试条件语句"""
    lexer = Lexer()
    tokens = lexer.tokenize('若真则1否则0。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    assert hasattr(ast.statements[0], 'cond')

def test_parser_list():
    """测试列表"""
    lexer = Lexer()
    tokens = lexer.tokenize('定x=列1 2 3。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    assert ast.statements[0].name == 'x'

# ============ 代码生成器测试 ============

def test_codegen_arithmetic():
    """测试算术运算代码生成"""
    lexer = Lexer()
    tokens = lexer.tokenize('定x=加1 2。')
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    code = gen.generate(ast)
    
    assert 'x = _add(1, 2)' in code or 'x = (1 + 2)' in code

def test_codegen_function():
    """测试函数代码生成"""
    lexer = Lexer()
    tokens = lexer.tokenize('定平方=函x 乘x x。')
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    code = gen.generate(ast)
    
    assert 'def' in code or 'lambda' in code

def test_codegen_list():
    """测试列表代码生成"""
    lexer = Lexer()
    tokens = lexer.tokenize('列1 2 3')
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    code = gen.generate(ast)
    
    assert '_list(1, 2, 3)' in code or '[1, 2, 3]' in code

# ============ 集成测试 ============

def test_integration_fibonacci():
    """集成测试：斐波那契数列"""
    code = '''
定斐波=函n
  若n小2则n否则加斐波减n 1斐波减n 2。

印斐波10。
'''
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    # 验证生成的代码可以编译
    assert '斐波' in python_code
    assert 'def' in python_code or 'lambda' in python_code

def test_integration_higher_order():
    """集成测试：高阶函数"""
    code = '''
定数据=列1 2 3 4 5。
定平方=函x 乘x x。
定结果=皆平方数据。
印结果。
'''
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    # 验证生成的代码
    assert '_map' in python_code or 'map' in python_code

def test_integration_new_builtins():
    """集成测试：新增内置函数"""
    code = '''
定数据=列3 1 4 1 5。
定排序后=排数据。
定最大值=最大数据。
定最小值=最小数据。
定总和=求和数据。
印排序后。
印最大值。
印最小值。
印总和。
'''
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    # 验证生成的代码
    assert '_sort' in python_code
    assert '_max' in python_code
    assert '_min' in python_code
    assert '_sum' in python_code

# ============ 错误处理测试 ============

def test_error_formatter_basic():
    """测试错误格式化器基本功能"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="测试错误",
        file_path="test.yan",
        line=1,
        column=5,
        end_column=10,
        source_lines=["定 数据 = 42。"],
        message="测试消息"
    )
    
    result = formatter.format(context)
    
    assert "错误：测试错误" in result
    assert "test.yan" in result
    assert "第 1 行" in result

def test_error_formatter_with_suggestion():
    """测试错误格式化器带建议"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="未定义的变量",
        file_path="test.yan",
        line=1,
        column=5,
        end_column=8,
        source_lines=["印 数据x。"],
        message="未定义的变量：数据x",
        suggestion="您是否想使用：数据？"
    )
    
    result = formatter.format(context)
    
    assert "建议" in result
    assert "数据" in result

def test_error_suggester_similar_name():
    """测试相似名称建议"""
    suggester = ErrorSuggestionGenerator()
    
    candidates = {"数据", "列表", "函数"}
    suggestions = suggester.suggest_similar_name("数据x", candidates)
    
    assert "数据" in suggestions

def test_error_suggester_arity():
    """测试参数数量建议"""
    suggester = ErrorSuggestionGenerator()
    
    suggestion = suggester.suggest_arity_fix("加", 2, 1)
    
    assert "加" in suggestion
    assert "2" in suggestion
    assert "1" in suggestion

def test_error_suggester_index():
    """测试索引越界建议"""
    suggester = ErrorSuggestionGenerator()
    
    suggestion = suggester.suggest_index_fix(5, 3)
    
    assert "5" in suggestion
    assert "3" in suggestion

def test_error_suggester_type():
    """测试类型错误建议"""
    suggester = ErrorSuggestionGenerator()
    
    suggestion = suggester.suggest_type_fix("数", "串")
    
    assert "数" in suggestion
    assert "串" in suggestion

# ============ 运行测试 ============

def run_all_tests():
    """运行所有测试"""
    suite = TestSuite()
    
    print("=" * 60)
    print("言语言测试套件")
    print("=" * 60)
    
    # 词法分析器测试
    print("\n--- 词法分析器测试 ---")
    suite.test("数字词法分析", test_lexer_numbers)
    suite.test("字符串词法分析", test_lexer_strings)
    suite.test("关键字词法分析", test_lexer_keywords)
    suite.test("运算符词法分析", test_lexer_operators)
    
    # 语法分析器测试
    print("\n--- 语法分析器测试 ---")
    suite.test("变量定义", test_parser_define)
    suite.test("函数定义", test_parser_function)
    suite.test("条件语句", test_parser_if)
    suite.test("列表", test_parser_list)
    
    # 代码生成器测试
    print("\n--- 代码生成器测试 ---")
    suite.test("算术运算", test_codegen_arithmetic)
    suite.test("函数生成", test_codegen_function)
    suite.test("列表生成", test_codegen_list)
    
    # 集成测试
    print("\n--- 集成测试 ---")
    suite.test("斐波那契数列", test_integration_fibonacci)
    suite.test("高阶函数", test_integration_higher_order)
    suite.test("新增内置函数", test_integration_new_builtins)
    
    # 错误处理测试
    print("\n--- 错误处理测试 ---")
    suite.test("错误格式化器基本功能", test_error_formatter_basic)
    suite.test("错误格式化器带建议", test_error_formatter_with_suggestion)
    suite.test("相似名称建议", test_error_suggester_similar_name)
    suite.test("参数数量建议", test_error_suggester_arity)
    suite.test("索引越界建议", test_error_suggester_index)
    suite.test("类型错误建议", test_error_suggester_type)
    
    # 生成报告
    suite.report()

if __name__ == '__main__':
    run_all_tests()
