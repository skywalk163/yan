"""
言语言自举构建脚本
将 Python 编译器源码转换为言语言代码
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from py2yan import PythonToYanConverter
from lexer import Lexer, TokenType, LexerError
from parser import Parser

# 源文件列表（按依赖顺序）
SOURCE_FILES = [
    'nodes.py',
    'error.py',
    'lexer.py',
    'parser.py',
    'codegen.py',
]

# 需要在 Yan 输出中移除的 Python 导入
IGNORE_IMPORTS = {
    'from dataclasses import dataclass',
    'from typing import List, Optional, Any, Set, Dict, Tuple',
    'from typing import',
    'from enum import Enum, auto',
    'import sys',
    'sys.path.insert',
    'import os',
    'from dataclasses import',
}

def clean_yan_output(yan_code: str) -> str:
    """清理转换后的 Yan 代码"""
    lines = yan_code.split('\n')
    cleaned = []
    for line in lines:
        # 移除 Python 导入语句
        stripped = line.strip()
        skip = False
        if stripped.startswith('定') or stripped.startswith("'"):
            # 检查是否是 Python 导入的桥接
            if '引入Python' in stripped:
                skip = True
            if stripped.startswith("'") and stripped.endswith("'"):
                skip = True
        # 移除 docstring 表达式
        if stripped.startswith("'") and '。' in stripped:
            skip = True
        # 移除空 docstring 行
        if stripped == "'\\n言语言" or 'AST 节点定义' in stripped:
            skip = True
        if not skip:
            cleaned.append(line)
    return '\n'.join(cleaned)

def convert_file(py_file: str, yan_file: str, converter: PythonToYanConverter) -> bool:
    """转换单个文件"""
    print(f'转换: {py_file} → {yan_file}')
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            py_code = f.read()
        yan_code = converter.convert(py_code)
        
        # 清理
        yan_code = clean_yan_output(yan_code)
        
        # 添加模块头
        module_name = os.path.splitext(os.path.basename(py_file))[0]
        header = f'-- 自举：从 {py_file} 自动转换\n'
        header += f'-- 模块: {module_name}\n'
        if module_name in ('lexer',):
            header += '引入Python"re"。\n\n'
        yan_code = header + yan_code
        
        with open(yan_file, 'w', encoding='utf-8') as f:
            f.write(yan_code)
        print(f'  ✓ 已生成: {yan_file}')
        return True
    except Exception as e:
        print(f'  ❌ 转换失败: {e}')
        return False

def test_parse(yan_file: str) -> bool:
    """测试 Yan 文件是否能被解析"""
    print(f'  测试解析: {yan_file}')
    try:
        with open(yan_file, 'r', encoding='utf-8') as f:
            code = f.read()
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)
        print(f'    ✓ 解析成功: {len(ast.statements)} 语句, {len(tokens)} tokens')
        return True
    except Exception as e:
        print(f'    ❌ 解析失败: {e}')
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(base_dir)
    selfhost_dir = base_dir
    
    converter = PythonToYanConverter()
    
    results = []
    for py_file in SOURCE_FILES:
        src_path = os.path.join(src_dir, py_file)
        yan_name = os.path.splitext(py_file)[0] + '.yan'
        yan_path = os.path.join(selfhost_dir, yan_name)
        
        ok = convert_file(src_path, yan_path, converter)
        if ok:
            ok = test_parse(yan_path)
        results.append((py_file, ok))
    
    print('\n' + '=' * 50)
    print('转换结果汇总:')
    for name, ok in results:
        status = '✓' if ok else '❌'
        print(f'  {status} {name}')
    
    all_ok = all(ok for _, ok in results)
    print(f'\n总体: {"全部成功 ✓" if all_ok else "存在失败 ❌"}')
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())