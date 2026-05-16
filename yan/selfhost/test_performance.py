"""
性能优化测试脚本
验证词法分析器、语法分析器和代码生成器的优化效果
"""
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen

def test_performance():
    print('=' * 70)
    print('性能优化测试')
    print('=' * 70)
    
    # 测试用代码
    test_code = """
定x=1。
定y=2。
定z=加x y。
印z。

定平方=函n 乘n n。
定立方=函n 乘n 平方n。

列1 2 3 4 5皆平方。

若z大3 则印"大" 否则印"小"。

定i=0。
当i小10：
  印i。
  定i=加i 1。
。
"""
    
    # 测试词法分析
    print('\n1. 词法分析器测试')
    lexer = Lexer()
    
    start = time.time()
    for _ in range(1000):
        tokens = lexer.tokenize(test_code)
    elapsed = time.time() - start
    
    print(f'  执行1000次词法分析: {elapsed:.3f} 秒')
    print(f'  每次平均: {elapsed/1000*1000:.3f} 毫秒')
    print(f'  Token数量: {len(tokens)}')
    
    # 测试语法分析
    print('\n2. 语法分析器测试')
    parser = Parser()
    
    start = time.time()
    for _ in range(1000):
        tokens = lexer.tokenize(test_code)
        result = parser.parse(tokens)
    elapsed = time.time() - start
    
    print(f'  执行1000次语法分析: {elapsed:.3f} 秒')
    print(f'  每次平均: {elapsed/1000*1000:.3f} 毫秒')
    
    # 测试代码生成
    print('\n3. 代码生成器测试')
    gen = PythonCodeGen()
    
    tokens = lexer.tokenize(test_code)
    ast = parser.parse(tokens)
    
    start = time.time()
    for _ in range(1000):
        code = gen.generate(ast)
    elapsed = time.time() - start
    
    print(f'  执行1000次代码生成: {elapsed:.3f} 秒')
    print(f'  每次平均: {elapsed/1000*1000:.3f} 毫秒')
    print(f'  生成代码长度: {len(code)} 字符')
    
    # 测试完整编译流程
    print('\n4. 完整编译流程测试')
    
    start = time.time()
    for _ in range(1000):
        tokens = lexer.tokenize(test_code)
        ast = parser.parse(tokens)
        code = gen.generate(ast)
    elapsed = time.time() - start
    
    print(f'  执行1000次完整编译: {elapsed:.3f} 秒')
    print(f'  每次平均: {elapsed/1000*1000:.3f} 毫秒')
    
    print('\n' + '=' * 70)
    print('测试完成！')
    print('=' * 70)

if __name__ == '__main__':
    test_performance()
