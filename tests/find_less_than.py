#!/usr/bin/env python3
# 找到文件中所有 < 字符的位置
with open('yan/examples/basic.yan', 'rb') as f:
    data = f.read()

lines = data.split(b'\n')
for line_num, line in enumerate(lines, 1):
    if b'<' in line:
        for i in range(len(line)):
            if line[i:i+1] == b'<':
                print(f'第{line_num}行，第{i+1}列找到 <')