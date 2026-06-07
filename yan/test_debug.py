"""
调试 playground 例子的生成代码
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run
from parser import clear_global_user_verbs

# 读取 playground 例子
with open('playground/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r'(\w+):\s*`(.*?)`\s*,?\s*\n\s*(?=\w+:|})', re.DOTALL)
matches = pattern.findall(content)

targets = ['fibonacci_indent', 'binary_search', 'idiom', 'bubble_indent']
for name, code in matches:
    code = code.strip()
    if not code or name not in targets:
        continue
    print(f'\n{"#"*60}')
    print(f'# {name}')
    print(f'{"#"*60}')
    clear_global_user_verbs()
    result = run(code, syntax_version=2, debug=True, clear_cache=True)
    print(f'RESULT: {result}')