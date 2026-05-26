#!/usr/bin/env python3
"""测试 subprocess 调用"""

import subprocess
import sys
from pathlib import Path

MAIN_PY = Path("yan/main.py")

code = '印 "Hello"。'

print(f"测试代码: {code}")
print(f"Python: {sys.executable}")
print(f"Main.py: {MAIN_PY}")

try:
    print("\n执行 subprocess...")
    result = subprocess.run(
        [sys.executable, str(MAIN_PY), "-c"],
        input=code,
        capture_output=True,
        text=True,
        timeout=10,
        encoding='utf-8',
    )
    
    print(f"返回码: {result.returncode}")
    print(f"标准输出: {repr(result.stdout)}")
    print(f"标准错误: {repr(result.stderr)}")
    
except subprocess.TimeoutExpired:
    print("❌ 执行超时")
except Exception as e:
    print(f"❌ 执行错误: {e}")
    import traceback
    traceback.print_exc()
