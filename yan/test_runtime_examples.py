"""
测试 playground 例子的运行时执行
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run
import traceback

# 读取 playground 例子
with open('playground/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r'(\w+):\s*`(.*?)`\s*,?\s*\n\s*(?=\w+:|})', re.DOTALL)
matches = pattern.findall(content)

targets = ['fibonacci_indent', 'binary_search', 'idiom', 'quick_sort', 'bubble_indent']
for name, code in matches:
    code = code.strip()
    if not code:
        continue
    if name not in targets:
        continue
    print(f'\n===== {name} =====')
    try:
        result = run(code, syntax_version=2, clear_cache=False)
        print(f'  RESULT: {result}')
    except Exception as e:
        print(f'  ERROR: {e}')
        traceback.print_exc()