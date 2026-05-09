"""
中文数字转换工具
"""

# 中文数字映射
CHINESE_NUMBERS = {
    '零': 0, '〇': 0,
    '一': 1, '壹': 1,
    '二': 2, '贰': 2, '两': 2,
    '三': 3, '叁': 3,
    '四': 4, '肆': 4,
    '五': 5, '伍': 5,
    '六': 6, '陆': 6,
    '七': 7, '柒': 7,
    '八': 8, '捌': 8,
    '九': 9, '玖': 9,
    '十': 10, '拾': 10,
    '百': 100, '佰': 100,
    '千': 1000, '仟': 1000,
    '万': 10000, '萬': 10000,
    '亿': 100000000, '億': 100000000,
}

# 单位映射
UNITS = {
    '十': 10, '拾': 10,
    '百': 100, '佰': 100,
    '千': 1000, '仟': 1000,
    '万': 10000, '萬': 10000,
    '亿': 100000000, '億': 100000000,
}


def chinese_to_number(chinese_str: str) -> int:
    """
    将中文数字转换为阿拉伯数字
    """
    if not chinese_str:
        raise ValueError("空字符串")

    # 检查是否是纯中文数字
    for ch in chinese_str:
        if ch not in CHINESE_NUMBERS:
            raise ValueError(f"非中文数字字符: {ch}")

    # 特殊情况：单个字符
    if len(chinese_str) == 1:
        return CHINESE_NUMBERS[chinese_str]

    # 解析多位数字
    result = 0
    current = 0  # 当前累积的值

    for i, ch in enumerate(chinese_str):
        if ch in UNITS:
            unit = UNITS[ch]
            
            if unit >= 10000:  # 万、亿
                # 大单位
                if current == 0:
                    current = 1
                result += current * unit
                current = 0
            else:
                # 小单位：十、百、千
                if current == 0:
                    current = 1
                current *= unit
                result += current
                current = 0
        else:
            # 数字
            num = CHINESE_NUMBERS[ch]
            current = num

    result += current
    return result


def is_chinese_number(s: str) -> bool:
    """判断字符串是否是中文数字"""
    if not s:
        return False

    for ch in s:
        if ch not in CHINESE_NUMBERS:
            return False

    return True
