#!/usr/bin/env python3
"""Verify all 4 fixes."""
FILEPATH = 'g:/dumategithub/newlisp/yan/playground/index.html'

with open(FILEPATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

# ============================
# Verify Fix 1: data_process
# ============================
print('\n=== Fix 1: data_process ===')
for i, line in enumerate(lines):
    if 'data_process:' in line and 'example' not in line and 'loadExample' not in line:
        print(f'  Start line {i+1}: {repr(line.rstrip())}')
        # Show next ~30 lines
        for j in range(i+1, min(i+35, len(lines))):
            s = lines[j].rstrip()
            if s:
                print(f'  {j+1}: {s}')
            else:
                print(f'  {j+1}: (empty)')
            if '`,' in lines[j]:
                break
        break

# Verify v2 keywords in data_process
print('\n  Key checks:')
print(f'  定义 found: {any("定义 " in line for i, line in enumerate(lines) if 859 < i < 900)}')
print(f'  列表 found: {any("列表 " in line for i, line in enumerate(lines) if 859 < i < 900)}')
print(f'  当时 found: {any("当时 " in line for i, line in enumerate(lines) if 859 < i < 900)}')
print(f'  如果 found: {any("如果 " in line for i, line in enumerate(lines) if 859 < i < 900)}')
print(f'  v1 keyword 当 (standalone) found: {any(line.strip().startswith("当 ") for i, line in enumerate(lines) if 859 < i < 900)}')
print(f'  v1 keyword 若 found: {any(line.strip().startswith("若 ") for i, line in enumerate(lines) if 859 < i < 900)}')

# ============================
# Verify Fix 2: text_process
# ============================
print('\n=== Fix 2: text_process ===')
for i, line in enumerate(lines):
    if 'text_process:' in line and 'example' not in line and 'loadExample' not in line:
        print(f'  Start line {i+1}: {repr(line.rstrip())}')
        # Check for \" 
        backslash_quotes = 0
        for j in range(i, min(i+70, len(lines))):
            if '\\"' in lines[j]:
                backslash_quotes += 1
                print(f'  \\" found at line {j+1}: {repr(lines[j].rstrip()[:60])}')
        print(f'  Total \\" in section: {backslash_quotes}')
        if backslash_quotes == 0:
            print('  ✓ No backslash-quote sequences found')
        break

# ============================
# Verify Fix 3: interactive_calc
# ============================
print('\n=== Fix 3: interactive_calc ===')
for i, line in enumerate(lines):
    if 'interactive_calc:' in line and 'example' not in line and 'loadExample' not in line:
        print(f'  Start line {i+1}: {repr(line.rstrip())}')
        for j in range(i+1, min(i+30, len(lines))):
            s = lines[j].rstrip()
            if s:
                print(f'  {j+1}: {s}')
            if '`,' in lines[j]:
                break
        break

print('\n  Key checks:')
print(f'  定义 found: {any("定义 " in line for i, line in enumerate(lines) if 967 < i < 993)}')
print(f'  当时 found: {any("当时 " in line for i, line in enumerate(lines) if 967 < i < 993)}')
print(f'  如果 found: {any("如果 " in line for i, line in enumerate(lines) if 967 < i < 993)}')

# ============================
# Verify Fix 4: interactive_demo
# ============================
print('\n=== Fix 4: interactive_demo ===')
for i, line in enumerate(lines):
    if 'interactive_demo:' in line and 'example' not in line and 'loadExample' not in line:
        print(f'  Start line {i+1}: {repr(line.rstrip())}')
        for j in range(i+1, min(i+30, len(lines))):
            s = lines[j].rstrip()
            if s:
                print(f'  {j+1}: {s}')
            else:
                print(f'  {j+1}: (empty)')
            if '`,' in lines[j]:
                break
        break

print('\n  Key checks:')
print(f'  定义 found: {any("定义 " in line for i, line in enumerate(lines) if 994 < i < 1025)}')
print(f'  (简化版  without closing paren fixed: {any("（简化版）" in line or "(简化版)" in line for i, line in enumerate(lines) if 994 < i < 1025)}')
# Check no 句号 at end of non-empty, non-comment lines (except strings)
print(f'  句号 at line endings (should be 0 or very few): {sum(1 for i, line in enumerate(lines) if 994 < i < 1025 and line.rstrip().endswith("。") and "印" not in line[:5] and "--" not in line)}')