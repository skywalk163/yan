#!/usr/bin/env python3
"""修复所有示例中的英文冒号为中文冒号"""

# 读取文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 examples 对象的起始位置
examples_start = -1
examples_end = -1
brace_count = 0
in_string = False
string_char = None

for i, line in enumerate(lines):
    for j, char in enumerate(line):
        if not in_string:
            if char in ['"', "'", '`']:
                in_string = True
                string_char = char
            elif char == '{' and 'const examples' in ''.join(lines[:i+1]):
                if examples_start == -1:
                    examples_start = i
                brace_count += 1
            elif char == '}' and examples_start != -1:
                brace_count -= 1
                if brace_count == 0:
                    examples_end = i
                    break
        else:
            if char == '\\' and j + 1 < len(line):
                j += 1
                continue
            elif char == string_char:
                in_string = False
    
    if examples_end != -1:
        break

print(f"Examples 对象范围: 行 {examples_start} 到 {examples_end}")

# 只在示例代码部分替换冒号
fixed_lines = []
for i, line in enumerate(lines):
    if examples_start <= i <= examples_end:
        # 只在行尾的 ` 符号之前替换冒号
        # 这样可以避免破坏 JavaScript 代码
        if '`' in line and ':' in line:
            # 找到反引号的位置
            backtick_pos = line.rfind('`')
            # 只替换反引号之前的冒号
            before_backtick = line[:backtick_pos]
            after_backtick = line[backtick_pos:]
            
            # 在反引号之前的内容中替换冒号
            before_backtick = before_backtick.replace(':', '：')
            
            line = before_backtick + after_backtick
    
    fixed_lines.append(line)

# 保存文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ 已修复所有示例中的英文冒号")
