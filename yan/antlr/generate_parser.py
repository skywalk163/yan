#!/usr/bin/env python3
"""
ANTLR 代码生成脚本
"""

import subprocess
import os
import sys

def generate_antlr():
    """生成 ANTLR 解析器"""
    grammar_file = "Yan.g4"
    output_dir = "generated"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 使用 Python 模块方式运行 antlr4
    cmd = [
        sys.executable, "-m", "antlr4",
        "-Dlanguage=Python3",
        "-visitor",
        "-no-listener",
        "-o", output_dir,
        grammar_file
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    print(f"Success! Generated files in {output_dir}/")
    print(result.stdout)
    return True

if __name__ == "__main__":
    generate_antlr()
