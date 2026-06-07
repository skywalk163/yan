"""Debug idiom example"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from main import run
from parser import clear_global_user_verbs

with open(os.path.join('playground', 'index.html'), 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r'(\w+):\s*`(.*?)`\s*,?\s*\n\s*(?=\w+:|})', re.DOTALL)
matches = pattern.findall(content)

for name, code in matches:
    code = code.strip()
    if name != 'idiom':
        continue
    print(f'=== {name} ===')
    print(f'SOURCE:\n{code}')
    print()
    clear_global_user_verbs()
    result = run(code, syntax_version=2, debug=True, clear_cache=True)
    print(f'RESULT: {result}')