"""
错误建议生成器测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_suggestions import ErrorSuggestionGenerator

def test_suggest_similar_variable():
    """测试相似变量名建议"""
    generator = ErrorSuggestionGenerator()
    
    defined_vars = {"数据", "列表", "函数"}
    wrong_name = "数据x"
    
    suggestions = generator.suggest_similar_name(wrong_name, defined_vars)
    
    assert "数据" in suggestions

def test_suggest_similar_function():
    """测试相似函数名建议"""
    generator = ErrorSuggestionGenerator()
    
    defined_funcs = {"平方", "立方", "阶乘"}
    wrong_name = "平芳"
    
    suggestions = generator.suggest_similar_name(wrong_name, defined_funcs)
    
    assert "平方" in suggestions

def test_suggest_arity_fix():
    """测试参数数量建议"""
    generator = ErrorSuggestionGenerator()
    
    suggestion = generator.suggest_arity_fix(
        func_name="加",
        expected=2,
        actual=1
    )
    
    assert "加" in suggestion
    assert "2" in suggestion
    assert "1" in suggestion

def test_suggest_type_fix():
    """测试类型错误建议"""
    generator = ErrorSuggestionGenerator()
    
    suggestion = generator.suggest_type_fix(
        expected_type="数",
        actual_type="串"
    )
    
    assert "数" in suggestion
    assert "串" in suggestion

def test_no_suggestion_for_correct_name():
    """测试正确名称不生成建议"""
    generator = ErrorSuggestionGenerator()
    
    defined_vars = {"数据", "列表"}
    correct_name = "数据"
    
    suggestions = generator.suggest_similar_name(correct_name, defined_vars)
    
    assert len(suggestions) == 0

def test_suggest_index_fix():
    """测试索引越界建议"""
    generator = ErrorSuggestionGenerator()
    
    suggestion = generator.suggest_index_fix(5, 3)
    assert "5" in suggestion
    assert "3" in suggestion
    
    suggestion2 = generator.suggest_index_fix(-1, 5)
    assert "负数" in suggestion2 or "负" in suggestion2

if __name__ == '__main__':
    test_suggest_similar_variable()
    print("✓ test_suggest_similar_variable")
    test_suggest_similar_function()
    print("✓ test_suggest_similar_function")
    test_suggest_arity_fix()
    print("✓ test_suggest_arity_fix")
    test_suggest_type_fix()
    print("✓ test_suggest_type_fix")
    test_no_suggestion_for_correct_name()
    print("✓ test_no_suggestion_for_correct_name")
    test_suggest_index_fix()
    print("✓ test_suggest_index_fix")
    print("\n错误建议生成器测试通过")
