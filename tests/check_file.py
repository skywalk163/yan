#!/usr/bin/env python3
# 检查文件中的隐藏字符
with open('yan/examples/basic.yan', 'rb') as f:
    data = f.read()

# 找到第40行
lines = data.split(b'\n')
print('第40行:', repr(lines[39]))
print()

# 检查是否有隐藏字符
for i, b in enumerate(lines[39]):
    if b not in range(32, 127) and b != 9 and b != 10 and b != 13:
        print(f'发现异常字节: 位置{i+1}, 值={hex(b)}')
    elif chr(b) in '<>{}[]':
        print(f'位置{i+1}: {hex(b)} = {chr(b)}')