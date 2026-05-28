"""
言语言 Token 定义 - 统一版本
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(Enum):
    NUM = 1       # 数字：1, 2.5, -3
    STR = 2       # 字符串："hello"
    WORD = 3      # 动词/标识符：加, 乘, 列, x, y
    QUOTE = 4     # ' (引用)
    COMMA = 5     # ，
    DOT = 6       # 。（中文句号，语句结束）
    DOT_EN = 7    # .（英文句号，成员访问）
    SEMI = 8      # ；
    ELLIPSIS = 9  # ... (可变参数)
    COLON = 10    # ：（块开始）
    EQUALS = 11   # =
    MATH = 12     # $(...) 数学表达式
    PYTHON = 13   # {{...}} Python 代码块
    LPAREN = 14  # ( 左括号
    RPAREN = 15  # ) 右括号
    INDENT = 16   # 缩进增加（用于块开始）
    DEDENT = 17   # 缩进减少（用于块结束）
    NEWLINE = 18  # 换行符
    EOF = 19      # 结束


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    col: int
