#!/usr/bin/env python3
"""
言语言 ANTLR 版本主入口
"""

import sys
import os

# 添加父目录到路径，以便导入 nodes 和 runtime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 添加 generated 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

from antlr4 import *
from antlr4.error.ErrorListener import ConsoleErrorListener
from YanLexer import YanLexer
from YanParser import YanParser
from ast_builder import ASTBuilder
from codegen import PythonCodeGen
from runtime import BUILTINS


def parse(code: str):
    """解析代码，返回 AST"""
    input_stream = InputStream(code)
    lexer = YanLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = YanParser(token_stream)
    
    # 添加错误监听器
    parser.removeErrorListeners()
    parser.addErrorListener(ConsoleErrorListener())
    
    # 解析程序
    tree = parser.program()
    
    # 构建 AST
    builder = ASTBuilder()
    ast = builder.visit(tree)
    
    return ast, builder.user_verbs


def compile_to_python(code: str) -> str:
    """编译代码，返回 Python 代码"""
    ast, user_verbs = parse(code)
    
    # 生成 Python 代码
    codegen = PythonCodeGen()
    python_code = codegen.generate(ast)
    
    return python_code


def run(code: str):
    """运行代码"""
    python_code = compile_to_python(code)
    
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 创建运行时环境
    runtime = {}
    # 添加内置函数（使用 Python 函数名）
    for name, (func, arity) in BUILTINS.items():
        runtime[func.__name__] = func
    # 添加常用的 Python 内置函数
    runtime["print"] = print
    runtime["len"] = len
    runtime["range"] = range
    runtime["list"] = list
    runtime["str"] = str
    runtime["int"] = int
    runtime["float"] = float
    runtime["bool"] = bool
    # 执行代码
    try:
        # 编译 Python 代码
        import builtins
        compiled = builtins.compile(python_code, '<string>', 'exec')
        exec(compiled, runtime, runtime)
    except Exception as e:
        print(f"运行时错误: {e}")
        print(f"生成的代码:\n{python_code}")
        raise


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python main.py <文件名>")
        print("      python main.py -e '代码'")
        sys.exit(1)
    
    if sys.argv[1] == '-e':
        # 直接执行代码
        code = sys.argv[2]
        run(code)
    else:
        # 从文件读取代码
        filename = sys.argv[1]
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        run(code)


if __name__ == '__main__':
    main()
