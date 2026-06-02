with open('yan/examples/basic.yan', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if '减' in line or '除' in line or '范围' in line or '只大2' in line:
        print(f'{i}: {line}', end='')
    if '10' in line and '5' in line and ('印' in line or '印' not in line):
        print(f'{i}: {line}', end='')
