"""
性能基准测试
"""

import time
import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser, process_adverbs
from codegen import PythonCodeGen


def generate_large_source(n_statements: int = 1000) -> str:
    """生成大型测试源码"""
    lines = []
    
    # 添加简单的表达式语句（每个语句以句号结束）
    for i in range(n_statements):
        lines.append("印 加 " + str(i) + " 1。")
    
    return "\n".join(lines)


def benchmark_lexer(source: str, iterations: int = 100) -> float:
    """基准测试词法分析器"""
    lexer = Lexer()
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        tokens = lexer.tokenize(source)
        end = time.perf_counter()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"Lexer Benchmark ({iterations} iterations):")
    print(f"  Mean: {mean_time*1000:.2f} ms")
    print(f"  Min: {min_time*1000:.2f} ms")
    print(f"  Max: {max_time*1000:.2f} ms")
    print(f"  StdDev: {stdev*1000:.2f} ms")
    print(f"  Tokens generated: {len(tokens)}")
    
    return mean_time


def benchmark_parser(source: str, iterations: int = 100) -> float:
    """基准测试语法分析器"""
    lexer = Lexer()
    parser = Parser()
    times = []
    
    for _ in range(iterations):
        tokens = lexer.tokenize(source)
        start = time.perf_counter()
        ast = parser.parse(tokens)
        ast = process_adverbs(ast)
        end = time.perf_counter()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"\nParser Benchmark ({iterations} iterations):")
    print(f"  Mean: {mean_time*1000:.2f} ms")
    print(f"  Min: {min_time*1000:.2f} ms")
    print(f"  Max: {max_time*1000:.2f} ms")
    print(f"  StdDev: {stdev*1000:.2f} ms")
    
    return mean_time


def benchmark_codegen(source: str, iterations: int = 10) -> float:
    """基准测试代码生成器"""
    lexer = Lexer()
    parser = Parser()
    codegen = PythonCodeGen()
    
    # 预先编译
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)
    ast = process_adverbs(ast)
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        py_code = codegen.generate(ast)
        end = time.perf_counter()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"\nCodeGen Benchmark ({iterations} iterations):")
    print(f"  Mean: {mean_time*1000:.2f} ms")
    print(f"  Min: {min_time*1000:.2f} ms")
    print(f"  Max: {max_time*1000:.2f} ms")
    print(f"  StdDev: {stdev*1000:.2f} ms")
    print(f"  Python code length: {len(py_code)} chars")
    
    return mean_time


def benchmark_complete(source: str, iterations: int = 10) -> float:
    """基准测试完整流程（词法分析 + 语法分析 + 代码生成 + 执行）"""
    from main import run
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = run(source, debug=False, use_global_verbs=False, clear_cache=True)
        end = time.perf_counter()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"\nComplete Pipeline Benchmark ({iterations} iterations):")
    print(f"  Mean: {mean_time*1000:.2f} ms")
    print(f"  Min: {min_time*1000:.2f} ms")
    print(f"  Max: {max_time*1000:.2f} ms")
    print(f"  StdDev: {stdev*1000:.2f} ms")
    
    return mean_time


def test_large_code():
    """测试大型代码文件的解析性能"""
    print("=" * 60)
    print("性能基准测试")
    print("=" * 60)
    
    # 生成测试源码
    print("\n生成测试源码...")
    source = generate_large_source(1000)
    print(f"源码大小: {len(source)} 字符")
    print(f"源码行数: {source.count('\\n') + 1} 行")
    
    # 运行基准测试
    print("\n" + "=" * 60)
    lexer_time = benchmark_lexer(source, iterations=50)
    
    print("\n" + "=" * 60)
    parser_time = benchmark_parser(source, iterations=50)
    
    print("\n" + "=" * 60)
    codegen_time = benchmark_codegen(source, iterations=10)
    
    print("\n" + "=" * 60)
    complete_time = benchmark_complete(source, iterations=10)
    
    # 输出总结
    print("\n" + "=" * 60)
    print("性能总结")
    print("=" * 60)
    print(f"词法分析: {lexer_time*1000:.2f} ms")
    print(f"语法分析: {parser_time*1000:.2f} ms")
    print(f"代码生成: {codegen_time*1000:.2f} ms")
    print(f"完整流程: {complete_time*1000:.2f} ms")


def test_keyword_matching():
    """测试关键字匹配性能"""
    print("\n" + "=" * 60)
    print("关键字匹配性能测试")
    print("=" * 60)
    
    # 生成包含大量关键字的源码
    keywords = ['加', '减', '乘', '除', '印', '定', '函', '若', '则', '否则', 
                '遍历', '当', '返回', '列', '长', '首', '余', '大', '小', '等']
    
    lines = []
    for i in range(1000):
        kw = keywords[i % len(keywords)]
        lines.append(f"{kw} {i}")
    
    source = '\n'.join(lines)
    
    print(f"测试源码: {len(lines)} 行关键字调用")
    
    lexer = Lexer()
    times = []
    for _ in range(50):
        start = time.perf_counter()
        tokens = lexer.tokenize(source)
        end = time.perf_counter()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    print(f"平均分词时间: {mean_time*1000:.2f} ms")
    print(f"总 token 数: {len(tokens)}")


if __name__ == "__main__":
    test_large_code()
    test_keyword_matching()