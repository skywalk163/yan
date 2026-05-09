
# 关键字列表（按优先级排序，双字关键字优先）
KEYWORDS = {
    '函': 'FUNC',
    '定': 'DEFINE',
    '等于': 'DENGYU',
    '若': 'IF',
    '则': 'THEN',
    '否则': 'ELSE',
    '遍历': 'FOREACH',
    '于': 'IN',
    '当': 'WHILE',
    '真': 'TRUE',
    '假': 'FALSE',
    '空': 'NIL',
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
    """拆分包含关键字的 ID"""
    result = []
    i = 0

    while i < len(id_text):
        matched = False

        for keyword in sorted(KEYWORDS.keys(), key=len, reverse=True):
            if id_text[i:i+len(keyword)] == keyword:
                if result and result[-1][0] == 'ID':
                    result.append((KEYWORDS[keyword], keyword))
                else:
                    result.append((KEYWORDS[keyword], keyword))
                i += len(keyword)
                matched = True
                break

        if not matched:
            if result and result[-1][0] == 'ID':
                result[-1] = ('ID', result[-1][1] + id_text[i])
            else:
                result.append(('ID', id_text[i]))
            i += 1

    return result

