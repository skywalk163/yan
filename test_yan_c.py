#!/usr/bin/env python3
"""测试 yan main.py -c 命令"""

import subprocess
import sys

code = '印 "你好"。'

print(f"测试命令: python yan/main.py -c")
print(f"输入代码: {code}")
print("---")

# 直接从 stdin 读取
result = subprocess.run(
    [sys.executable, "yan/main.py", "-c"],
    input=code + '\n',  # 添加换行符
    capture_output=True,
    text=True,
    encoding='utf-8',
    timeout=10
)

print(f"返回码: {result.returncode}")
print(f"标准输出: {result.stdout}")
print(f"标准错误: {result.stderr}")
print("---")
