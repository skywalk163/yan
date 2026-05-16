"""
性能对比测试：优化版 vs 原版
"""
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入原版
from lexer import Lexer as LexerOriginal
from parser import Parser as ParserOriginal
from codegen import PythonCodeGen as CodeGenOriginal

# 导入优化版
from lexer_optimized import Lexer as LexerOptimized
from parser_optimized import Parser as ParserOptimized
from codegen_optimized import PythonCodeGen as CodeGenOptimized

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

def benchmark(name, func, iterations=1000):
    start = time.time()
    for _ in range(iterations):
        func()
    elapsed = time.time() - start
    per_call = elapsed / iterations * 1000
    return elapsed, per_call

def test_original():
    lexer = LexerOriginal()
    parser = ParserOriginal()
    gen = CodeGenOriginal()
    
    tokens = lexer.tokenize(test_code)
    ast = parser.parse(tokens)
    code = gen.generate(ast)

def test_optimized():
    lexer = LexerOptimized()
    parser = ParserOptimized()
    gen = CodeGenOptimized()
    
    tokens = lexer.tokenize(test_code)
    ast = parser.parse(tokens)
    code = gen.generate(ast)

def main():
    print('=' * 70)
    print('言语言编译器性能对比测试')
    print('=' * 70)
    
    print('\n1. 原版性能测试')
    print('-' * 70)
    elapsed, per_call = benchmark('原版完整编译', test_original, 10000)
    print(f'执行10000次: {elapsed:.3f} 秒')
    print(f'每次平均: {per_call:.3f} 毫秒')
    
    print('\n2. 优化版性能测试')
    print('-' * 70)
    elapsed, per_call = benchmark('优化版完整编译', test_optimized, 10000)
    print(f'执行10000次: {elapsed:.3f} 秒')
    print(f'每次平均: {per_call:.3f} 毫秒')
    
    print('\n3. 性能对比总结')
    print('=' * 70)

if __name__ == '__main__':
    main()
