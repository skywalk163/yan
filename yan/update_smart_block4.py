import sys

# 更新 test_smart_block.py 中剩余的关键字
keyword_mapping = {
    '定阶乘=': '定义阶乘=',
    '否那么': '否则',
    '若差': '如果差',
    '若i': '如果i',
    '若j': '如果j',
}

with open('tests/test_smart_block.py', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in keyword_mapping.items():
    content = content.replace(old, new)

with open('tests/test_smart_block.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')