"""
言语言词法分析器
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Set, Any


class TokenType(Enum):
    NUM = auto()       # 数字：1, 2.5, -3
    STR = auto()       # 字符串："hello"
    WORD = auto()      # 动词/标识符：加, 乘, 列, x, y
    QUOTE = auto()     # ' (引用)
    COMMA = auto()     # ，
    DOT = auto()       # 。
    SEMI = auto()      # ；
    COLON = auto()     # ：（块开始）
    EQUALS = auto()    # =
    MATH = auto()      # $(...) 数学表达式
    PYTHON = auto()    # {{...}} Python 代码块
    EOF = auto()       # 结束


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"


class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"词法错误 (行{line}, 列{col}): {message}")


class Lexer:
    """词法分析器：无空格分词 + 多字贪心匹配"""

    # CJK 汉字范围
    HAN_START = 0x4E00
    HAN_END = 0x9FFF

    def __init__(self, keywords: Optional[Set[str]] = None, user_words: Optional[Set[str]] = None):
        self.keywords = keywords or {
            # 多字动词
            '定义', '阶乘', '平方', '否则', '如果', '那么', '不等',
            # 数学库
            '正弦', '余弦', '正切', '反正弦', '反余弦', '反正切',
            '指数', '对数', '对数10', '开方', '取整', '进位', '四舍五入',
            '随机', '随机整数', '圆周率', '自然常数',
            # 字符串库
            '长度', '连接', '分割', '替换', '截取', '小写', '大写',
            '查找', '包含', '去空', '开头是', '结尾是',
            # 文件库
            '读文件', '写文件', '追加文件', '存在', '是文件', '是目录',
            '列目录', '建目录', '删文件', '删目录', '当前目录',
            '文件名', '目录名', '扩展名',
            # 时间库
            '当前时间', '日期', '时间', '日期时间', '格式化时间', '睡眠',
            # 类型检查
            '是数', '是串', '是表', '是函', '是真', '是空', '类型',
            # 单字动词
            '加', '减', '乘', '除', '模', '幂', '绝对', '负',
            '大', '小', '等',
            '且', '或', '非',
            '列', '典', '序', '对',
            '首', '余', '入', '长', '添', '连', '含', '空', '范围',
            '皆', '只', '归', '潜',
            '印', '读', '写',
            '若', '则', '定', '函', '行',
            '真', '假',
        }
        self.user_words = user_words or set()  # 用户定义的词（不拆分）
        self.max_keyword_len = max(len(k) for k in self.keywords) if self.keywords else 1

    def _is_han(self, ch: str) -> bool:
        """判断是否为汉字"""
        if not ch:
            return False
        cp = ord(ch)
        return self.HAN_START <= cp <= self.HAN_END

    def _is_ident_char(self, ch: str) -> bool:
        """判断是否为标识符字符（汉字或字母或下划线或数字）"""
        if not ch:
            return False
        return self._is_han(ch) or ch.isalnum() or ch == '_'

    def _is_same_type(self, ch1: str, ch2: str) -> bool:
        """判断两个字符是否属于同一类型（用于分词）"""
        if not ch1 or not ch2:
            return False
        # 汉字只能和汉字连续（不能和数字混合）
        if self._is_han(ch1):
            return self._is_han(ch2)
        # 字母、数字、下划线（非汉字）可以连续
        # 但要注意：如果 ch2 是汉字，应该分开
        if self._is_han(ch2):
            return False
        if ch1 == '_' or ch1.isalnum():
            return ch2 == '_' or ch2.isalnum()
        return False

    def tokenize(self, source: str) -> List[Token]:
        """将源码转为 Token 流"""
        tokens = []
        i = 0
        line, col = 1, 1

        while i < len(source):
            ch = source[i]

            # 跳过空白符
            if ch in ' \t\r':
                col += 1
                i += 1
                continue

            if ch == '\n':
                line += 1
                col = 1
                i += 1
                continue

            # 注释：-- 开头到行尾
            if source[i:i+2] == '--':
                while i < len(source) and source[i] != '\n':
                    i += 1
                continue

            # 注释：注 开头到行尾
            if ch == '注':
                while i < len(source) and source[i] != '\n':
                    i += 1
                continue

            # 引用符号：' (Lisp-style quote)
            if ch == "'":
                tokens.append(Token(TokenType.QUOTE, "'", line, col))
                i += 1; col += 1
                continue

            # 结构符
            if ch == '。':
                tokens.append(Token(TokenType.DOT, '。', line, col))
                i += 1; col += 1
                continue

            if ch == '，':
                tokens.append(Token(TokenType.COMMA, '，', line, col))
                i += 1; col += 1
                continue

            if ch == '；':
                tokens.append(Token(TokenType.SEMI, '；', line, col))
                i += 1; col += 1
                continue

            if ch == '=':
                tokens.append(Token(TokenType.EQUALS, '=', line, col))
                i += 1; col += 1
                continue

            # 冒号：块开始标记
            if ch == '：':
                tokens.append(Token(TokenType.COLON, '：', line, col))
                i += 1; col += 1
                continue

            # 数学表达式：$(...)
            if ch == '$' and i + 1 < len(source) and source[i + 1] == '(':
                start_line, start_col = line, col
                i += 2  # 跳过 $(
                col += 2
                j = i
                depth = 1
                while j < len(source) and depth > 0:
                    if source[j] == '(':
                        depth += 1
                    elif source[j] == ')':
                        depth -= 1
                    elif source[j] == '\n':
                        line += 1
                        col = 0
                    j += 1
                    col += 1
                if depth > 0:
                    raise LexerError("数学表达式未闭合", start_line, start_col)
                value = source[i:j-1]  # 不包含最后的 )
                tokens.append(Token(TokenType.MATH, value, start_line, start_col))
                i = j
                continue

            # Python 代码块：{{...}}
            if ch == '{' and i + 1 < len(source) and source[i + 1] == '{':
                start_line, start_col = line, col
                i += 2  # 跳过 {{
                col += 2
                j = i
                depth = 1
                while j < len(source) and depth > 0:
                    if j + 1 < len(source) and source[j:j+2] == '{{':
                        depth += 1
                        j += 2
                        col += 2
                    elif j + 1 < len(source) and source[j:j+2] == '}}':
                        depth -= 1
                        if depth == 0:
                            break
                        j += 2
                        col += 2
                    elif source[j] == '\n':
                        line += 1
                        col = 0
                        j += 1
                    else:
                        j += 1
                        col += 1
                if depth > 0:
                    raise LexerError("Python 代码块未闭合", start_line, start_col)
                value = source[i:j]  # 不包含最后的 }}
                tokens.append(Token(TokenType.PYTHON, value, start_line, start_col))
                i = j + 2  # 跳过 }}
                continue

            # 字符串："..."
            if ch == '"':
                j = i + 1
                while j < len(source) and source[j] != '"':
                    if source[j] == '\n':
                        line += 1
                        col = 1
                    j += 1
                if j >= len(source):
                    raise LexerError("字符串未闭合", line, col)
                value = source[i+1:j]
                tokens.append(Token(TokenType.STR, value, line, col))
                col += j - i + 1
                i = j + 1
                continue

            # 数字
            if ch.isdigit() or (ch == '-' and i + 1 < len(source) and source[i+1].isdigit()):
                j = i
                has_dot = False
                while j < len(source):
                    c = source[j]
                    if c.isdigit():
                        j += 1
                    elif c == '.' and not has_dot:
                        has_dot = True
                        j += 1
                    else:
                        break

                value_str = source[i:j]
                try:
                    value = float(value_str) if '.' in value_str else int(value_str)
                    tokens.append(Token(TokenType.NUM, value, line, col))
                    col += j - i
                    i = j
                except ValueError:
                    raise LexerError(f"无效数字: {value_str}", line, col)
                continue

            # 汉字或字母标识符
            if self._is_ident_char(ch):
                # 尝试最长匹配用户定义的词
                if self._is_han(ch) and self.user_words:
                    for length in range(min(10, len(source) - i), 0, -1):  # 最多10个字
                        candidate = source[i:i+length]
                        if candidate in self.user_words:
                            tokens.append(Token(TokenType.WORD, candidate, line, col))
                            col += length
                            i += length
                            continue
                
                # 尝试最长匹配关键字（只对汉字关键字）
                if self._is_han(ch):
                    # 特殊处理：如果前一个 token 是 '定'，检查整个连续汉字序列后面是否跟着 '='
                    # 如果是，则不拆分关键字（这是变量/函数名）
                    should_not_split = False
                    if tokens and tokens[-1].type == TokenType.WORD and tokens[-1].value == '定':
                        j = i
                        while j < len(source) and self._is_han(source[j]):
                            j += 1
                        # 跳过空白
                        k = j
                        while k < len(source) and source[k] in ' \t':
                            k += 1
                        # 检查是否跟着 '='
                        if k < len(source) and source[k] == '=':
                            should_not_split = True
                            # 不拆分，整个序列作为一个标识符
                            value = source[i:j]
                            tokens.append(Token(TokenType.WORD, value, line, col))
                            col += len(value)
                            i = j
                            continue
                    
                    # 否则，尝试匹配关键字
                    matched = None
                    matched_len = 0
                    for length in range(min(self.max_keyword_len, len(source) - i), 0, -1):
                        candidate = source[i:i+length]
                        if candidate in self.keywords:
                            matched = candidate
                            matched_len = length
                            break

                    if matched:
                        tokens.append(Token(TokenType.WORD, matched, line, col))
                        col += matched_len
                        i += matched_len
                        continue

                    # 非关键字的汉字：收集连续的汉字作为一个标识符
                    # 这样 "安全" 会被作为一个标识符
                    j = i
                    while j < len(source) and self._is_han(source[j]):
                        # 检查是否遇到关键字
                        candidate = source[j:j+1]
                        if candidate in self.keywords:
                            break
                        # 检查下一个多字是否是关键字
                        found_keyword = False
                        for length in range(min(self.max_keyword_len, len(source) - j), 1, -1):
                            if source[j:j+length] in self.keywords:
                                found_keyword = True
                                break
                        if found_keyword:
                            break
                        j += 1
                    value = source[i:j]
                    tokens.append(Token(TokenType.WORD, value, line, col))
                    col += len(value)
                    i = j
                    continue

                # 收集连续的同类型标识符字符（非汉字，如拉丁字母）
                j = i
                while j < len(source) and self._is_same_type(ch, source[j]):
                    j += 1
                value = source[i:j]
                tokens.append(Token(TokenType.WORD, value, line, col))
                col += len(value)
                i = j
                continue

            # 未知字符
            raise LexerError(f"未知字符: {ch}", line, col)

        tokens.append(Token(TokenType.EOF, None, line, col))
        return tokens


if __name__ == "__main__":
    # 测试
    lexer = Lexer()
    tests = [
        "列1 2 3皆乘2。",
        "10加5，乘2。",
        "定平方=函x乘x x。",
        '"Hello World"',
    ]

    for source in tests:
        print(f"\n源码: {source}")
        tokens = lexer.tokenize(source)
        for tok in tokens:
            print(f"  {tok}")
