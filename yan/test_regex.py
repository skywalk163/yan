"""
诊断 playground 例子提取是否正确
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with open('playground/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取所有 examples 对象中的键名
pattern = re.compile(r'(\w+):\s*`(.*?)`\s*,?\s*\n\s*(?=\w+:|})', re.DOTALL)
matches = pattern.findall(content)

for name, code in matches:
    code = code.strip()
    print(f'\n--- {name} (len={len(code)}) ---')
    # 只打印前50个字符确认
    preview = code[:80].replace('\n', '\\n')
    print(f'  START: "{preview}..."')
    if len(code) > 0:
        last_chars = code[-30:].replace('\n', '\\n')
        print(f'  END: "...{last_chars}"')