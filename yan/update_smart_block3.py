import sys

# 更新 test_smart_block.py 中剩余的关键字
keyword_mapping = {
    # 控制流关键字
    '若x': '如果x',
    '若n': '如果n',
    '若i': '如果i',
    '否则么': '否则',
    
    # 比较运算符
    '大于0': '大于0',
    '小于0': '小于0',
    '小于1': '小于1',
    '小于5': '小于5',
    '小于9': '小于9',
    '小于10': '小于10',
    '小于n': '小于n',
    '小于len': '小于len',
    '大于5': '大于5',
    '大于x': '大于x',
    '大于max': '大于max',
}

with open('tests/test_smart_block.py', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in keyword_mapping.items():
    content = content.replace(old, new)

with open('tests/test_smart_block.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')