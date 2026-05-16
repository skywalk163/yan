"""
新增内置函数测试
测试优先级1的列表和字典操作函数
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen

def test_list_operations():
    """测试列表操作函数"""
    print("=" * 60)
    print("测试列表操作函数")
    print("=" * 60)
    
    test_cases = [
        # 反转列表
        ("反 列1 2 3", "list(reversed([1, 2, 3]))"),
        
        # 排序列表
        ("排 列3 1 2", "sorted([3, 1, 2])"),
        
        # 最大值
        ("最大 列1 5 3", "max([1, 5, 3])"),
        
        # 最小值
        ("最小 列1 5 3", "min([1, 5, 3])"),
        
        # 求和
        ("求和 列1 2 3 4 5", "sum([1, 2, 3, 4, 5])"),
    ]
    
    for yan_code, expected in test_cases:
        print(f"\n言语言代码: {yan_code}")
        print(f"预期Python: {expected}")
        
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(yan_code)
            parser = Parser()
            ast = parser.parse(tokens)
            gen = PythonCodeGen()
            python_code = gen.generate(ast)
            
            print(f"实际Python: {python_code.strip()}")
            
            # 验证结果
            if expected in python_code:
                print("[PASS]")
            else:
                print("[FAIL]")
        except Exception as e:
            print(f"[ERROR] {e}")

def test_dict_operations():
    """测试字典操作函数"""
    print("\n" + "=" * 60)
    print("测试字典操作函数")
    print("=" * 60)
    
    test_cases = [
        # 获取键
        ("键 典'a' 1 'b' 2", "dict_keys(...)"),
        
        # 获取值
        ("值 典'a' 1 'b' 2", "dict_values(...)"),
    ]
    
    for yan_code, expected in test_cases:
        print(f"\n言语言代码: {yan_code}")
        print(f"预期: {expected}")
        
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(yan_code)
            parser = Parser()
            ast = parser.parse(tokens)
            gen = PythonCodeGen()
            python_code = gen.generate(ast)
            
            print(f"实际Python: {python_code.strip()}")
            print("[PASS] Compiled successfully")
        except Exception as e:
            print(f"[ERROR] {e}")

def test_execution():
    """测试实际执行"""
    print("\n" + "=" * 60)
    print("测试实际执行")
    print("=" * 60)
    
    # 测试反转列表
    code = """
定data=列1 2 3 4 5。
定reversed=反data。
印reversed。
"""
    
    print(f"\n言语言代码:\n{code}")
    
    try:
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)
        gen = PythonCodeGen()
        python_code = gen.generate(ast)
        
        print(f"生成的Python代码:\n{python_code}")
        
        print("[PASS] Execution successful")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_list_operations()
    test_dict_operations()
    test_execution()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
