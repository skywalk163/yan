"""
详细性能分析脚本
使用 cProfile 进行热点分析
"""
import cProfile
import pstats
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen

# 测试代码
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

# 大型测试代码
large_code = """
定fib=函n 若n小等于1 则n 否则加fib减n 1 fib减n 2。
定factorial=函n 若n等1 则1 否则乘n factorial减n 1。

定nums=列1 2 3 4 5 6 7 8 9 10。
定squares=列1 4 9 16 25 36 49 64 81 100。
定cubes=列1 8 27 64 125 216 343 512 729 1000。

印fib 10。
印factorial 5。
印nums。
印squares。
印cubes。

定sum=0。
遍历x 于 nums：
  sum=加sum x。
。
印sum。

定product=1。
遍历x 于 nums：
  product=乘product x。
。
印product。

定filtered=列只大于5。
印filtered。

定mapped=列皆乘2。
印mapped。
"""

def profile_lexer():
    print('=' * 70)
    print('1. 词法分析器性能分析')
    print('=' * 70)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    lexer = Lexer()
    for _ in range(10000):
        tokens = lexer.tokenize(test_code)
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())
    
    print('\n2. 大型代码词法分析')
    profiler = cProfile.Profile()
    profiler.enable()
    
    for _ in range(1000):
        tokens = lexer.tokenize(large_code)
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

def profile_parser():
    print('\n' + '=' * 70)
    print('3. 语法分析器性能分析')
    print('=' * 70)
    
    lexer = Lexer()
    tokens = lexer.tokenize(test_code)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    parser = Parser()
    for _ in range(10000):
        ast = parser.parse(tokens)
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

def profile_codegen():
    print('\n' + '=' * 70)
    print('4. 代码生成器性能分析')
    print('=' * 70)
    
    lexer = Lexer()
    tokens = lexer.tokenize(test_code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    gen = PythonCodeGen()
    for _ in range(10000):
        code = gen.generate(ast)
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

def profile_full_compilation():
    print('\n' + '=' * 70)
    print('5. 完整编译流程性能分析')
    print('=' * 70)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    for _ in range(10000):
        lexer = Lexer()
        tokens = lexer.tokenize(test_code)
        parser = Parser()
        ast = parser.parse(tokens)
        gen = PythonCodeGen()
        code = gen.generate(ast)
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    print(s.getvalue())

def main():
    print('言语言编译器详细性能分析')
    print('=' * 70)
    
    profile_lexer()
    profile_parser()
    profile_codegen()
    profile_full_compilation()
    
    print('\n' + '=' * 70)
    print('分析完成！')
    print('=' * 70)

if __name__ == '__main__':
    main()
