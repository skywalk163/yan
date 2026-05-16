"""
一个 Python 数据分析示例 - 用于测试 py2yan 转换
"""
import os
import json
import math
from datetime import datetime


def load_config(path):
    """加载配置文件"""
    if not os.path.exists(path):
        return {}

    with open(path, 'r') as f:
        config = json.load(f)

    return config


def analyze_numbers(numbers):
    """分析数字列表"""
    if not numbers:
        return {
            'count': 0,
            'sum': 0,
            'mean': 0,
            'max': None,
            'min': None
        }

    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    max_val = max(numbers)
    min_val = min(numbers)

    result = {
        'count': count,
        'sum': total,
        'mean': mean,
        'max': max_val,
        'min': min_val
    }

    return result


def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


def process_data(data):
    """处理数据"""
    result = []

    for item in data:
        if item > 0:
            processed = item * 2
            result.append(processed)

    return result


def generate_report(data, title="Report"):
    """生成报告"""
    stats = analyze_numbers(data)
    timestamp = datetime.now()

    report = f"""
Report: {title}
Date: {timestamp}
Count: {stats['count']}
Sum: {stats['sum']}
Mean: {stats['mean']:.2f}
"""

    return report.strip()


def main():
    """主函数"""
    samples = [1, -2, 3, -4, 5, 6, -7, 8, 9, 10]
    fib_nums = [fibonacci(i) for i in range(10)]

    print(fib_nums)
    print(process_data(samples))
    print(generate_report(samples, "Sample Analysis"))

    pi = math.pi
    sin_pi_4 = math.sin(pi / 4)

    print(sin_pi_4)


if __name__ == '__main__':
    main()