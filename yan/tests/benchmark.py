"""
性能测试基准
测试不同大小程序的编译速度
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen

def generate_test_code(size):
    """生成测试代码"""
    if size == 'small':
        # 小型程序：~50行
        lines = []
        for i in range(10):
            lines.append(f'定x{i}=加{i} {i+1}。')
        lines.append('印x0。')
        return '\n'.join(lines)
    
    elif size == 'medium':
        # 中型程序：~500行
        lines = []
        for i in range(100):
            lines.append(f'定变量{i}=乘{i} {i+1}。')
        lines.append('印变量0。')
        return '\n'.join(lines)
    
    elif size == 'large':
        # 大型程序：~2000行
        lines = []
        for i in range(400):
            lines.append(f'定数据{i}=列{i} {i+1} {i+2}。')
            lines.append(f'定结果{i}=求和数据{i}。')
        lines.append('印结果0。')
        return '\n'.join(lines)
    
    return ''

def benchmark_compile(source, name):
    """编译性能测试"""
    print(f"\n{'=' * 60}")
    print(f"测试: {name}")
    print(f"{'=' * 60}")
    print(f"源代码大小: {len(source)} 字符, {len(source.splitlines())} 行")
    
    # 词法分析
    start = time.time()
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    lexer_time = time.time() - start
    print(f"词法分析: {lexer_time*1000:.2f}ms ({len(tokens)} tokens)")
    
    # 语法分析
    start = time.time()
    parser = Parser()
    ast = parser.parse(tokens)
    parser_time = time.time() - start
    print(f"语法分析: {parser_time*1000:.2f}ms")
    
    # 代码生成
    start = time.time()
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    codegen_time = time.time() - start
    print(f"代码生成: {codegen_time*1000:.2f}ms")
    
    # 总时间
    total_time = lexer_time + parser_time + codegen_time
    print(f"总时间: {total_time*1000:.2f}ms")
    print(f"生成代码大小: {len(python_code)} 字符")
    
    return {
        'lexer': lexer_time,
        'parser': parser_time,
        'codegen': codegen_time,
        'total': total_time
    }

def run_benchmarks():
    """运行所有性能测试"""
    print("=" * 60)
    print("言语言编译器性能测试")
    print("=" * 60)
    
    sizes = ['small', 'medium', 'large']
    results = {}
    
    for size in sizes:
        source = generate_test_code(size)
        results[size] = benchmark_compile(source, f"{size.upper()} program")
    
    # 性能总结
    print(f"\n{'=' * 60}")
    print("性能总结")
    print(f"{'=' * 60}")
    print(f"{'大小':<10} {'总时间(ms)':<15} {'词法(ms)':<12} {'语法(ms)':<12} {'生成(ms)':<12}")
    print("-" * 60)
    for size in sizes:
        r = results[size]
        print(f"{size:<10} {r['total']*1000:<15.2f} {r['lexer']*1000:<12.2f} {r['parser']*1000:<12.2f} {r['codegen']*1000:<12.2f}")
    
    # 性能目标检查
    print(f"\n{'=' * 60}")
    print("性能目标检查")
    print(f"{'=' * 60}")
    
    checks = [
        ('small', 10, "小型程序应 < 10ms"),
        ('medium', 100, "中型程序应 < 100ms"),
        ('large', 500, "大型程序应 < 500ms"),
    ]
    
    for size, target_ms, desc in checks:
        actual_ms = results[size]['total'] * 1000
        status = "[PASS]" if actual_ms < target_ms else "[FAIL]"
        print(f"{status} {desc} (实际: {actual_ms:.2f}ms)")

if __name__ == '__main__':
    run_benchmarks()
