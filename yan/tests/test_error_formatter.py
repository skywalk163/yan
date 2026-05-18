"""
错误格式化器测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_formatter import ErrorFormatter, ErrorContext

def test_format_simple_error():
    """测试简单错误格式化"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="未定义的变量",
        file_path="examples/demo.yan",
        line=3,
        column=15,
        end_column=18,
        source_lines=[
            "定 数据 = 列 1 2 3。",
            "定 平方 = 函 x 乘 x x。",
            "定 值 = 皆 平方 数据x。"
        ],
        message="未定义的变量：数据x",
        suggestion="检查变量名拼写，或确认变量已定义。"
    )
    
    result = formatter.format(context)
    
    assert "错误：未定义的变量" in result
    assert "文件：examples/demo.yan" in result
    assert "第 3 行" in result
    assert "数据x" in result
    assert "建议" in result

def test_format_error_with_suggestion():
    """测试带建议的错误格式化"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="拼写错误",
        file_path="test.yan",
        line=1,
        column=5,
        end_column=8,
        source_lines=["定 数据 = 42。"],
        message="未定义的变量：数据",
        suggestion="您是否想使用：数据？",
        similar_names=["数据"]
    )
    
    result = formatter.format(context)
    
    assert "您是否想使用：数据？" in result

def test_format_multiline_error():
    """测试多行错误格式化"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="语法错误",
        file_path="test.yan",
        line=2,
        column=1,
        end_column=10,
        source_lines=[
            "定 数据 = 列 1 2 3。",
            "定 平方 = 函 x",
            "  乘 x x。",
            "平方 5。"
        ],
        message="函数定义未闭合",
        suggestion="添加 '。' 结束函数定义。"
    )
    
    result = formatter.format(context)
    
    assert "第 1 行" in result
    assert "第 2 行" in result
    assert "第 3 行" in result

def test_color_output():
    """测试彩色输出"""
    formatter = ErrorFormatter(use_color=True)
    
    context = ErrorContext(
        error_type="测试错误",
        file_path="test.yan",
        line=1,
        column=1,
        end_column=5,
        source_lines=["测试代码。"],
        message="测试消息"
    )
    
    result = formatter.format(context)
    
    assert "\033[" in result

def test_no_color_output():
    """测试无彩色输出"""
    formatter = ErrorFormatter(use_color=False)
    
    context = ErrorContext(
        error_type="测试错误",
        file_path="test.yan",
        line=1,
        column=1,
        end_column=5,
        source_lines=["测试代码。"],
        message="测试消息"
    )
    
    result = formatter.format(context)
    
    assert "\033[" not in result

if __name__ == '__main__':
    test_format_simple_error()
    print("✓ test_format_simple_error")
    test_format_error_with_suggestion()
    print("✓ test_format_error_with_suggestion")
    test_format_multiline_error()
    print("✓ test_format_multiline_error")
    test_color_output()
    print("✓ test_color_output")
    test_no_color_output()
    print("✓ test_no_color_output")
    print("\n错误格式化器测试通过")
