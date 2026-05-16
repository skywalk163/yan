"""模块系统测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen


def test_module_keywords():
    """测试模块关键字词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导入 模块 导出')
    
    # 检查所有关键字都被正确识别
    assert len(tokens) >= 3
    assert tokens[0].type.name == 'WORD'
    assert tokens[0].value == '导入'
    assert tokens[1].type.name == 'WORD'
    assert tokens[1].value == '模块'
    assert tokens[2].type.name == 'WORD'
    assert tokens[2].value == '导出'


def test_import_statement():
    """测试导入语句词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导入 utils')
    
    assert tokens[0].value == '导入'
    assert tokens[1].value == 'utils'


def test_import_statement_parse():
    """测试导入语句语法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导入 utils。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    # 检查是否正确解析
    assert len(ast.statements) >= 1


def test_export_statement_parse():
    """测试导出语句语法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导出 函数名。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    # 检查是否正确解析
    assert len(ast.statements) >= 1


def test_import_codegen():
    """测试导入语句代码生成"""
    code = '导入 utils。'
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert 'import utils' in python_code or 'from utils' in python_code


def test_export_codegen():
    """测试导出语句代码生成"""
    code = '导出 函数名。'
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    # 导出语句在 Python 中通常不需要特殊处理，或者使用 __all__
    assert python_code.strip() == '' or '__all__' in python_code


if __name__ == '__main__':
    test_module_keywords()
    test_import_statement()
    test_import_statement_parse()
    test_export_statement_parse()
    test_import_codegen()
    test_export_codegen()
    print("所有模块测试通过")

