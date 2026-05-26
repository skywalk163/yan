import sys

# 更新 test_smart_block.py 中剩余的关键字
keyword_mapping = {
    '当x': '当时x',
    '当i': '当时i',
    '当j': '当时j',
}

with open('tests/test_smart_block.py', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in keyword_mapping.items():
    content = content.replace(old, new)

with open('tests/test_smart_block.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')