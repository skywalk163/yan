import sys

# 更新 test_smart_block.py 中的关键字
keyword_mapping = {
    # 控制流关键字
    '定x=': '定义x=',
    '定y=': '定义y=',
    '定结果=': '定义结果=',
    '定n=': '定义n=',
    '定i=': '定义i=',
    '定j=': '定义j=',
    '函x': '函数x',
    '函n': '函数n',
    '若真': '如果真',
    '若假': '如果假',
    '若小': '如果小于',
    '若大': '如果大于',
    '则': '那么',
    '否则': '否则',
    '遍历': '遍历',
    '当时': '当时',
    '于': '于',
    
    # 比较运算符
    '小': '小于',
    '大': '大于',
    '等': '等于',
    
    # 列表
    '列': '列表',
    
    # 输出
    '印': '输出',
}

with open('tests/test_smart_block.py', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in keyword_mapping.items():
    content = content.replace(old, new)

with open('tests/test_smart_block.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')