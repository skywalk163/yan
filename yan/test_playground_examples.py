"""Verify all playground examples parse correctly."""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lexer import Lexer
from parser import Parser

with open('playground/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract examples from JavaScript object: name: `code` (with optional trailing comma)
pattern = re.compile(r'(\w+):\s*`(.*?)`\s*,?\s*\n\s*(?=\w+:|})', re.DOTALL)
matches = pattern.findall(content)

print(f'Found {len(matches)} examples')
passed = 0
failed = 0

for name, code in matches:
    code = code.strip()
    if not code:
        continue
    try:
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser(syntax_version=2)
        ast = parser.parse(tokens)
        print(f'  OK  {name}')
        passed += 1
    except Exception as e:
        print(f'  FAIL {name}: {e}')
        failed += 1

print(f'\nResults: {passed} passed, {failed} failed')
if failed > 0:
    sys.exit(1)