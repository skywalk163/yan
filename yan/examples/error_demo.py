"""
错误处理演示
展示言语言的新错误信息格式
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_formatter import ErrorFormatter, ErrorContext
from error_suggestions import ErrorSuggestionGenerator

def demo_undefined_variable():
    """演示未定义变量错误"""
    print("\n" + "="*60)
    print("演示1：未定义变量错误")
    print("="*60)
    
    formatter = ErrorFormatter()
    suggester = ErrorSuggestionGenerator()
    
    defined_vars = {"数据", "列表", "函数"}
    wrong_name = "数据x"
    suggestions = suggester.suggest_similar_name(wrong_name, defined_vars)
    
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
        message=f"未定义的变量：{wrong_name}",
        suggestion="检查变量名拼写，或确认变量已定义。",
        similar_names=suggestions
    )
    
    print(formatter.format(context))

def demo_arity_error():
    """演示参数数量错误"""
    print("\n" + "="*60)
    print("演示2：参数数量错误")
    print("="*60)
    
    formatter = ErrorFormatter()
    suggester = ErrorSuggestionGenerator()
    
    suggestion = suggester.suggest_arity_fix("加", 2, 1)
    
    context = ErrorContext(
        error_type="参数数量错误",
        file_path="examples/calc.yan",
        line=5,
        column=10,
        end_column=15,
        source_lines=[
            "定 平方 = 函 x 乘 x x。",
            "定 立方 = 函 x 乘 x 平方 x。",
            "",
            "定 a = 5。",
            "定 结果 = 加 a。"
        ],
        message="函数调用参数不足",
        suggestion=suggestion
    )
    
    print(formatter.format(context))

def demo_index_error():
    """演示索引越界错误"""
    print("\n" + "="*60)
    print("演示3：索引越界错误")
    print("="*60)
    
    formatter = ErrorFormatter()
    suggester = ErrorSuggestionGenerator()
    
    suggestion = suggester.suggest_index_fix(5, 3)
    
    context = ErrorContext(
        error_type="索引越界",
        file_path="examples/list.yan",
        line=4,
        column=12,
        end_column=18,
        source_lines=[
            "定 数据 = 列 1 2 3。",
            "定 平方 = 函 x 乘 x x。",
            "",
            "定 值 = 入 数据 5。"
        ],
        message="索引 5 超出范围",
        suggestion=suggestion
    )
    
    print(formatter.format(context))

def demo_type_error():
    """演示类型错误"""
    print("\n" + "="*60)
    print("演示4：类型错误")
    print("="*60)
    
    formatter = ErrorFormatter()
    suggester = ErrorSuggestionGenerator()
    
    suggestion = suggester.suggest_type_fix("数", "串")
    
    context = ErrorContext(
        error_type="类型错误",
        file_path="examples/type.yan",
        line=2,
        column=10,
        end_column=15,
        source_lines=[
            "定 消息 = \"hello\"。",
            "定 结果 = 加 消息 1。"
        ],
        message="类型不匹配：期望数，实际串",
        suggestion=suggestion
    )
    
    print(formatter.format(context))

def demo_syntax_error():
    """演示语法错误"""
    print("\n" + "="*60)
    print("演示5：语法错误")
    print("="*60)
    
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="语法错误",
        file_path="examples/syntax.yan",
        line=2,
        column=1,
        end_column=10,
        source_lines=[
            "定 平方 = 函 x",
            "  乘 x x。",
            "平方 5。"
        ],
        message="函数定义未闭合",
        suggestion="添加 '。' 结束函数定义。"
    )
    
    print(formatter.format(context))

def main():
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          言语言错误处理演示                               ║")
    print("║          Error Handling Demonstration                    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    demo_undefined_variable()
    demo_arity_error()
    demo_index_error()
    demo_type_error()
    demo_syntax_error()
    
    print("\n" + "="*60)
    print("演示结束")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
