"""图灵机模拟器测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lexer import Lexer
from parser import Parser, clear_global_user_verbs
from codegen import PythonCodeGen
from runtime import ALL_BUILTINS

def run_yan_source(source: str):
    """运行言语言源码并返回输出"""
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    
    clear_global_user_verbs()
    parser = Parser(use_global_verbs=True)
    ast = parser.parse(tokens)
    
    codegen = PythonCodeGen()
    py_code = codegen.generate(ast)
    
    # 使用 runtime 的命名空间执行
    import runtime
    exec('from runtime import *', runtime.__dict__)
    
    exec(py_code, runtime.__dict__)
    
    return runtime.__dict__, py_code

# 测试图灵机
yan_code = open('examples/turing_machine.yan', 'r', encoding='utf-8').read()

print("=== 编译言语言代码 ===")
lexer = Lexer()
tokens = lexer.tokenize(yan_code)
print(f"Token 数量: {len(tokens)}")

clear_global_user_verbs()
parser = Parser(use_global_verbs=True)
ast = parser.parse(tokens)
print(f"AST 语句数: {len(ast.statements)}")

codegen = PythonCodeGen()
py_code = codegen.generate(ast)

print("\n=== 生成的 Python 代码 ===")
print(py_code)
print()

print("=== 执行图灵机模拟器 ===")
import runtime
exec('from runtime import *', runtime.__dict__)
exec(py_code, runtime.__dict__)

print("\n=== 测试完成 ===")