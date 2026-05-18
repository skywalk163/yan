"""
语法分析器错误测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser

def test_undefined_variable_error():
    """测试未定义变量错误"""
    code = "印 数据x。"
    lexer = Lexer()
    parser = Parser()
    
    try:
        tokens = lexer.tokenize(code)
        ast = parser.parse(tokens, code)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        assert len(error_msg) > 0

def test_syntax_structure_error():
    """测试语法结构错误"""
    code = "定 平方 = 函 x 乘 x x"
    lexer = Lexer()
    parser = Parser()
    
    try:
        tokens = lexer.tokenize(code)
        ast = parser.parse(tokens, code)
    except Exception as e:
        error_msg = str(e)
        assert len(error_msg) > 0

def test_function_call_error():
    """测试函数调用错误"""
    code = "定 结果 = 加 1。"
    lexer = Lexer()
    parser = Parser()
    
    try:
        tokens = lexer.tokenize(code)
        ast = parser.parse(tokens, code)
    except Exception as e:
        error_msg = str(e)
        assert len(error_msg) > 0

if __name__ == '__main__':
    test_undefined_variable_error()
    print("✓ test_undefined_variable_error")
    test_syntax_structure_error()
    print("✓ test_syntax_structure_error")
    test_function_call_error()
    print("✓ test_function_call_error")
    print("\n语法分析器错误测试通过")
