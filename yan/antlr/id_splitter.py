#!/usr/bin/env python3
"""
ID 拆分工具
检测并拆分包含关键字的 ID
"""

# 关键字列表（按优先级排序）
KEYWORDS = {
    # Lambda 关键字
    '函': 'FUNC',
    # 定义关键字
    '定': 'DEFINE',
    '等于': 'DENGYU',
    # 中缀动词
    '加': 'ADD',
    '减': 'SUB',
    '乘': 'MUL',
    '除': 'DIV',
    '模': 'MOD',
    '幂': 'POW',
    '大': 'GT',
    '小': 'LT',
    '等': 'EQ',
    '不等': 'NE',
    '且': 'AND',
    '或': 'OR',
    # 前缀动词
    '印': 'PRINT',
    '绝对': 'ABS',
    '负': 'NEG',
    '非': 'NOT',
    '首': 'HEAD',
    '余': 'TAIL',
    '入': 'APPEND',
    '长': 'LEN',
    '连': 'CONCAT',
    '含': 'CONTAINS',
    '皆': 'MAP',
    '只': 'FILTER',
    '归': 'REDUCE',
}

def split_id(id_text):
    """
    拆分包含关键字的 ID
    返回: [(类型, 文本), ...]
    类型: 'ID', 'FUNC', 'EQ', 'SUB', 等
    """
    result = []
    i = 0
    
    while i < len(id_text):
        matched = False
        
        # 尝试匹配最长的关键字（优先匹配"不等"、"等于"等双字关键字）
        for keyword in sorted(KEYWORDS.keys(), key=len, reverse=True):
            if id_text[i:i+len(keyword)] == keyword:
                if result and result[-1][0] == 'ID':
                    # 前面有 ID，添加关键字
                    result.append((KEYWORDS[keyword], keyword))
                else:
                    # 开头就是关键字
                    result.append((KEYWORDS[keyword], keyword))
                i += len(keyword)
                matched = True
                break
        
        if not matched:
            # 没有匹配到关键字，累积为 ID
            if result and result[-1][0] == 'ID':
                # 追加到上一个 ID
                result[-1] = ('ID', result[-1][1] + id_text[i])
            else:
                # 创建新的 ID
                result.append(('ID', id_text[i]))
            i += 1
    
    return result

# 测试
test_cases = [
    '函盘子数',
    '盘子数等',
    '汉诺塔盘子数减1',
    '印张三',
    '定汉诺塔',
]

for test in test_cases:
    result = split_id(test)
    print(f'{test} → {result}')
