#!/usr/bin/env python3
# 检查第39行的 {{...}} 语法
with open('yan/examples/basic.yan', 'rb') as f:
    data = f.read()

lines = data.split(b'\n')
print('第39行:', repr(lines[38]))
print('长度:', len(lines[38]))

# 找到 {{ 的位置
line = lines[38]
for i in range(len(line)-1):
    if line[i:i+2] == b'{{':
        print(f'找到 {{ 在位置 {i+1}')
    if line[i:i+2] == b'}}':
        print(f'找到 }} 在位置 {i+1}')