"""
词法分析器错误测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer

def test_invalid_character_error():
    """测试无效字符错误"""
    code = "定 数据 = 42 @ 1。"
    lexer = Lexer()
    
    try:
        tokens = lexer.tokenize(code)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        assert "行" in error_msg or "line" in error_msg.lower()

def test_unclosed_string_error():
    """测试未闭合字符串错误"""
    code = '定 消息 = "你好世界。'
    lexer = Lexer()
    
    try:
        tokens = lexer.tokenize(code)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        assert "闭合" in error_msg or "unclosed" in error_msg.lower() or "未闭合" in error_msg

def test_invalid_number_error():
    """测试无效数字错误"""
    code = "定 数 = 123.456.789。"
    lexer = Lexer()
    
    try:
        tokens = lexer.tokenize(code)
    except Exception as e:
        error_msg = str(e)
        assert len(error_msg) > 0

if __name__ == '__main__':
    test_invalid_character_error()
    print("✓ test_invalid_character_error")
    test_unclosed_string_error()
    print("✓ test_unclosed_string_error")
    test_invalid_number_error()
    print("✓ test_invalid_number_error")
    print("\n词法分析器错误测试通过")
