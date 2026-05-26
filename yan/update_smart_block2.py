import sys

# 更新 test_smart_block.py 中剩余的关键字
keyword_mapping = {
    '定距离=': '定义距离=',
    '定差=': '定义差=',
    '定z=': '定义z=',
    '定result=': '定义result=',
    '定sum=': '定义sum=',
    '定i=': '定义i=',
    '定j=': '定义j=',
    '定found=': '定义found=',
    '定count=': '定义count=',
    '定total=': '定义total=',
    '定factorial=': '定义factorial=',
    '定n=': '定义n=',
    '函a': '函数a',
    '函n': '函数n',
    '函x': '函数x',
    '小0': '小于0',
    '大0': '大于0',
    '小n': '小于n',
    '小10': '小于10',
    '小9': '小于9',
    '等0': '等于0',
    '等1': '等于1',
    '小于0': '小于0',
    '小于1': '小于1',
    '小于n': '小于n',
    '大于0': '大于0',
    '大于x': '大于x',
    '大于5': '大于5',
}

with open('tests/test_smart_block.py', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in keyword_mapping.items():
    content = content.replace(old, new)

with open('tests/test_smart_block.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')