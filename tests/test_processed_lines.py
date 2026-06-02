import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

with open('yan/examples/basic.yan', 'r', encoding='utf-8') as f:
    source = f.read()

lexer = Lexer()

# Simulate the tokenize method to check processed_lines
lines = source.splitlines()
processed_lines = []

statement_start_keywords = {'定义', '如果', '那么', '否则', '遍历', '当时', '函数', '返回', '结构', '套', '测', '打印', '读', '写', '引', '导', '出'}
block_start_keywords = {'函数', '如果', '遍历', '当时', '结构', '套', '测'}

i = 0
while i < len(lines):
    line = lines[i]
    
    # 检查行内容
    stripped = line.strip()
    
    # 如果是空行或注释，直接保留（不进行续行处理）
    if not stripped or stripped.startswith('--') or stripped.startswith('注'):
        processed_lines.append(line)
        i += 1
        continue
    
    # 检查是否需要续行
    current_indent = 0
    j = 0
    while j < len(line) and line[j] in ' \t':
        current_indent += 1
        j += 1
    
    has_dot = line.rstrip().endswith('。') or line.rstrip().endswith('．')
    
    # 检查是否以块开始关键字结尾
    ends_with_block_start = False
    for kw in block_start_keywords:
        if stripped.endswith(kw):
            ends_with_block_start = True
            break
    
    # 检查是否以语句开始关键字开头
    starts_with_statement = False
    for kw in statement_start_keywords:
        if stripped.startswith(kw):
            starts_with_statement = True
            break
    
    # 查看下一行
    should_merge = False
    if i + 1 < len(lines):
        next_line = lines[i + 1]
        next_stripped = next_line.strip()
        
        # 如果下一行不是空行或注释
        if next_stripped and not next_stripped.startswith('--') and not next_stripped.startswith('注'):
            next_indent = 0
            k = 0
            while k < len(next_line) and next_line[k] in ' \t':
                next_indent += 1
                k += 1
            
            # 如果满足以下条件，则续行
            if (next_indent == current_indent and 
                not has_dot and 
                not ends_with_block_start and 
                not starts_with_statement):
                should_merge = True
                line = line.rstrip() + ' ' + next_stripped
                i += 1  # 跳过下一行
    
    processed_lines.append(line)
    i += 1

print('Processed lines:')
for i, line in enumerate(processed_lines, 1):
    print(i, ':', repr(line))
