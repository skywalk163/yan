
"""
言语言编译器 - 统一入口
整合所有核心功能模块

言语言是一门以中文为语法核心的函数式编程语言。
"""

__version__ = "0.5.0"
__author__ = "言语言开发团队"

# 导出核心模块
from . import lexer
from . import parser
from . import nodes
from . import codegen
from . import runtime
from . import main

# 导出高级功能模块（直接作为模块访问）
from . import optimizer
from . import module_system
from . import yan_package_manager
from . import debugger_enhanced
from . import profiler
from . import concurrency
from . import ffi
from . import type_system
from . import macro_system
from . import error_recovery
from . import smart_error_suggestor
from . import codegen_multi

# 便捷函数
def compile(source, target="python"):
    from yan.lexer import Lexer
    from yan.parser import Parser
    from yan.codegen import PythonCodeGen
    
    if target == "python":
        lexer_obj = Lexer()
        tokens = lexer_obj.tokenize(source)
        parser_obj = Parser()
        ast = parser_obj.parse(tokens)
        codegen_obj = PythonCodeGen()
        return codegen_obj.generate(ast)
    else:
        try:
            return codegen_multi.compile_yan(source, target)
        except Exception:
            lexer_obj = Lexer()
            tokens = lexer_obj.tokenize(source)
            parser_obj = Parser()
            ast = parser_obj.parse(tokens)
            codegen_obj = PythonCodeGen()
            return codegen_obj.generate(ast)


def run(source, filename="<string>"):
    python_code = compile(source)
    namespace = {}
    exec(python_code, namespace)
    return namespace.get("__main_result__")


def run_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        source = f.read()
    return run(source, filename=filepath)


def interactive():
    main.main()


__all__ = [
    "lexer",
    "parser",
    "nodes",
    "codegen",
    "runtime",
    "main",
    "optimizer",
    "module_system",
    "yan_package_manager",
    "debugger_enhanced",
    "profiler",
    "concurrency",
    "ffi",
    "type_system",
    "macro_system",
    "error_recovery",
    "smart_error_suggestor",
    "codegen_multi",
    "compile",
    "run",
    "run_file",
    "interactive",
]
