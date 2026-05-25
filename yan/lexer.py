"""
言语言词法分析器
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Set, Any
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入错误处理模块
from error import SourceLocation, LexerError as EnhancedLexerError, ErrorSuggester

# 导入百家姓数据
try:
    from data.surnames import BAIJIAXING, CONFLICTING_SURNAMES
except ImportError:
    BAIJIAXING = set()
    CONFLICTING_SURNAMES = set()

# 导入中文数字转换
try:
    from chinese_number import chinese_to_number, is_chinese_number
except ImportError:
    chinese_to_number = None
    is_chinese_number = None


class TokenType(Enum):
    NUM = auto()       # 数字：1, 2.5, -3
    STR = auto()       # 字符串："hello"
    WORD = auto()      # 动词/标识符：加, 乘, 列, x, y
    QUOTE = auto()     # ' (引用)
    COMMA = auto()     # ，
    DOT = auto()       # 。（中文句号，语句结束）
    DOT_EN = auto()    # .（英文句号，成员访问）
    SEMI = auto()      # ；
    ELLIPSIS = auto()  # ... (可变参数)
    COLON = auto()     # ：（块开始）
    EQUALS = auto()    # =
    MATH = auto()      # $(...) 数学表达式
    PYTHON = auto()    # {{...}} Python 代码块
    LPAREN = auto()    # ( 左括号
    RPAREN = auto()    # ) 右括号
    EOF = auto()       # 结束


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"


# 向后兼容：保留旧的 LexerError 类
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
        self._source = None  # 保存源代码用于错误显示
        self.keywords = keywords or {
            # 多字动词
            '定义', '阶乘', '平方', '否则', '如果', '那么', '不等',
            # 赋值
            '等于',
            # 循环
            '遍历', '当', '于',
            # 模块系统（新增）
            '导入', '模块', '导出', '从', '引', '出',
            # 结构体系统（新增）
            '结构', '类型', '字段',
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
            '大', '大于', '大等于', '小', '小于', '小等于', '等', '等于', '不等于', '不等',
            '且', '或', '非',
            '列', '典', '序', '对',
            '首', '余', '入', '长', '添', '连', '含', '空', '范围',
            '皆', '只', '归', '潜',
            '印', '读', '写', '读行',
            '若', '则', '定', '函', '返回', '行', '无',
            '真', '假',
            # 新增列表操作
            '反', '排', '最大', '最小', '求和', '计数',
            # 新增字典操作
            '键', '值', '项', '删键',
            # 表达式求值
            '求值',
            # 测试框架
            '套', '测',
        }
        self.user_words = user_words or set()  # 用户定义的词（不拆分）
        self.max_keyword_len = max(len(k) for k in self.keywords) if self.keywords else 1

        # 百家姓变量识别
        self.surnames = BAIJIAXING
        self.conflicting_surnames = CONFLICTING_SURNAMES
        self.max_surname_len = max(len(k) for k in self.surnames) if self.surnames else 2

    def _scan_user_defs(self, source: str) -> Set[str]:
        """轻量扫描：收集所有用户定义的函数名/变量名
        
        寻找 '定 X =' 或 '定 X = 函' 模式的标识符 X
        """
        names = set()
        i = 0
        while i < len(source):
            # 跳过空白和注释
            while i < len(source) and source[i] in ' \t\r\n':
                i += 1
            if i >= len(source):
                break
            if source[i:i+2] == '--' or source[i] == '注':
                while i < len(source) and source[i] != '\n':
                    i += 1
                continue
            
            # 查找 '定'
            if source[i] == '定':
                j = i + 1
                # 跳过空白
                while j < len(source) and source[j] in ' \t':
                    j += 1
                # 收集标识符
                k = j
                while k < len(source) and (source[k].isalnum() or ord(source[k]) >= 0x4E00 and ord(source[k]) <= 0x9FFF):
                    k += 1
                if k > j:
                    name = source[j:k]
                    # 跳过空白检查 '='
                    m = k
                    while m < len(source) and source[m] in ' \t':
                        m += 1
                    if m < len(source) and source[m] == '=':
                        names.add(name)
                    i = k
                    continue
            i += 1
        return names

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

    def _try_match_surname(self, source: str, i: int):
        """尝试匹配姓氏（支持复姓）"""
        if not self.surnames:
            return None

        # 尝试最长匹配（复姓最长2字）
        for length in range(min(self.max_surname_len, len(source) - i), 0, -1):
            candidate = source[i:i+length]
            if candidate in self.surnames and candidate not in self.conflicting_surnames:
                return candidate
        return None

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

    def _create_error(self, message: str, line: int, col: int):
        """创建增强的词法错误"""
        location = SourceLocation(line, col)
        suggestion = ErrorSuggester.suggest(message)
        return EnhancedLexerError(message, location, self._source, suggestion)

    def tokenize(self, source: str) -> List[Token]:
        """将源码转为 Token 流"""
        self._source = source  # 保存源代码用于错误显示
        tokens = []
        i = 0
        line, col = 1, 1

        # 第一阶段：轻量扫描收集所有用户定义的标识符
        # 这些标识符在后续 tokenize 过程中不会被关键字拆分
        user_defined_names = self._scan_user_defs(source)

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

            # 单引号字符串：'...'（用于转义序列）
            # 检测逻辑：找到开始的 ' 后，向前看是否有结束的 '
            if ch == "'":
                j = i + 1
                found_closing = False
                temp_j = j
                while temp_j < len(source):
                    if source[temp_j] == '\\' and temp_j + 1 < len(source):
                        temp_j += 2
                    elif source[temp_j] == "'":
                        found_closing = True
                        break
                    elif source[temp_j] == '\n':
                        break
                    else:
                        temp_j += 1
                if found_closing:
                    chars = []
                    has_escape = False
                    while j < len(source) and source[j] != "'":
                        if source[j] == '\\' and j + 1 < len(source):
                            has_escape = True
                            next_ch = source[j + 1]
                            if next_ch == 't':
                                chars.append('\t')
                                j += 2
                            elif next_ch == 'n':
                                chars.append('\n')
                                j += 2
                            elif next_ch == 'r':
                                chars.append('\r')
                                j += 2
                            elif next_ch == '\\':
                                chars.append('\\')
                                j += 2
                            elif next_ch == "'":
                                chars.append("'")
                                j += 2
                            else:
                                chars.append(source[j])
                                j += 1
                        elif source[j] == '\n':
                            break
                        else:
                            chars.append(source[j])
                            j += 1
                    if j >= len(source) or source[j] != "'":
                        raise self._create_error("单引号字符串未闭合", line, col)
                    value = ''.join(chars)
                    tokens.append(Token(TokenType.STR, value, line, col))
                    col += j - i + 1
                    i = j + 1
                    continue

            # 引用符号：' (Lisp-style quote)
            if ch == "'":
                tokens.append(Token(TokenType.QUOTE, "'", line, col))
                i += 1; col += 1
                continue

            # 结构符
            if ch == '。' or ch == '．':
                tokens.append(Token(TokenType.DOT, '。', line, col))
                i += 1; col += 1
                continue

            if ch == '，':
                tokens.append(Token(TokenType.COMMA, '，', line, col))
                i += 1; col += 1
                continue

            # 支持英文逗号（作为中文逗号的别名）
            if ch == ',':
                tokens.append(Token(TokenType.COMMA, '，', line, col))
                i += 1; col += 1
                continue

            if ch == '；':
                tokens.append(Token(TokenType.SEMI, '；', line, col))
                i += 1; col += 1
                continue

            # 省略号：可变参数
            if ch == '.' and i + 2 < len(source) and source[i:i+3] == '...':
                tokens.append(Token(TokenType.ELLIPSIS, '...', line, col))
                i += 3; col += 3
                continue

            # 英文点号：用于模块成员访问（如 JSON.解析）
            if ch == '.':
                tokens.append(Token(TokenType.DOT_EN, '.', line, col))
                i += 1; col += 1
                continue

            # 英文左括号：用于分组表达式
            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, '(', line, col))
                i += 1; col += 1
                continue

            # 英文右括号：用于分组表达式
            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, ')', line, col))
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
                    raise self._create_error("数学表达式未闭合", start_line, start_col)
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
                    raise self._create_error("Python 代码块未闭合", start_line, start_col)
                value = source[i:j]  # 不包含最后的 }}
                tokens.append(Token(TokenType.PYTHON, value, start_line, start_col))
                i = j + 2  # 跳过 }}
                continue

            # 字符串："..."（支持转义序列）
            if ch == '"':
                j = i + 1
                chars = []
                while j < len(source) and source[j] != '"':
                    if source[j] == '\\' and j + 1 < len(source):
                        next_ch = source[j + 1]
                        if next_ch == 't':
                            chars.append('\t')
                            j += 2
                        elif next_ch == 'n':
                            chars.append('\n')
                            j += 2
                        elif next_ch == 'r':
                            chars.append('\r')
                            j += 2
                        elif next_ch == '\\':
                            chars.append('\\')
                            j += 2
                        elif next_ch == '"':
                            chars.append('"')
                            j += 2
                        else:
                            chars.append(source[j])
                            j += 1
                    elif source[j] == '\n':
                        line += 1
                        col = 1
                        j += 1
                    else:
                        chars.append(source[j])
                        j += 1
                if j >= len(source):
                    raise self._create_error("字符串未闭合", line, col)
                value = ''.join(chars)
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
                    raise self._create_error(f"无效数字: {value_str}", line, col)
                continue

            # 汉字或字母标识符
            if self._is_ident_char(ch):
                # 尝试最长匹配用户定义的词
                if self._is_han(ch) and self.user_words:
                    matched_user_word = False
                    for length in range(min(10, len(source) - i), 0, -1):  # 最多10个字
                        candidate = source[i:i+length]
                        if candidate in self.user_words:
                            tokens.append(Token(TokenType.WORD, candidate, line, col))
                            col += length
                            i += length
                            matched_user_word = True
                            break
                    if matched_user_word:
                        continue

                # 尝试最长匹配关键字（只对汉字关键字）
                if self._is_han(ch):
                    # 优先级1：检查是否是"定"后面的变量名
                    if tokens and tokens[-1].type == TokenType.WORD and tokens[-1].value == '定':
                        j = i
                        while j < len(source) and (self._is_han(source[j]) or source[j].isdigit() or (source[j].isascii() and source[j].isalpha())):
                            j += 1
                        # 跳过空白
                        k = j
                        while k < len(source) and source[k] in ' \t':
                            k += 1
                        # 检查是否跟着 '='
                        if k < len(source) and source[k] == '=':
                            # 不拆分，整个序列作为一个标识符
                            value = source[i:j]
                            tokens.append(Token(TokenType.WORD, value, line, col))
                            col += len(value)
                            i = j
                            continue

                    # 优先级1.5：处理"函"后面的参数
                    # 每个参数跟在函后面，按关键字边界分割
                    if tokens and tokens[-1].type == TokenType.WORD and tokens[-1].value == '函':
                        j = i
                        # 只收集非关键字的连续汉字作为单个参数
                        while j < len(source) and self._is_han(source[j]):
                            # 检查从j开始是否有匹配的关键字
                            is_keyword = False
                            for kl in range(min(self.max_keyword_len, len(source) - j), 0, -1):
                                candidate = source[j:j+kl]
                                if candidate in self.keywords:
                                    is_keyword = True
                                    break
                            if is_keyword and j > i:
                                # 关键字开始，参数收集结束
                                break
                            if is_keyword:
                                # 当前字符是关键字的开始，不是参数
                                break
                            j += 1
                        value = source[i:j]
                        if value:
                            tokens.append(Token(TokenType.WORD, value, line, col))
                            col += len(value)
                            i = j
                            continue

                    # 优先级1.75：检查用户定义的函数名（优先于关键字拆分）
                    # 如"更新"中的"更"是关键字，"扩展"中的"扩"也是关键字
                    # 但用户定义的函数名应该保持完整
                    found_user_name = False
                    if self._is_han(ch):
                        for length in range(min(10, len(source) - i), 1, -1):
                            candidate = source[i:i+length]
                            if candidate in user_defined_names:
                                tokens.append(Token(TokenType.WORD, candidate, line, col))
                                col += length
                                i += length
                                found_user_name = True
                                break
                    if found_user_name:
                        continue

                    # 优先级2：尝试匹配关键字（最长匹配优先）
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

                    # 优先级3：尝试百家姓变量识别
                    if self.surnames:
                        surname = self._try_match_surname(source, i)
                        if surname:
                            # 找到姓氏，收集完整的变量名（姓氏 + 0-3个汉字）
                            # 注意：变量名中可能包含关键字字符（如"王小明"中的"小"）
                            # 但遇到动词时应停止收集
                            j = i + len(surname)
                            while j < len(source) and self._is_han(source[j]) and j - i < 4:
                                # 检查当前位置是否是关键字
                                found_keyword = False
                                found_keyword_len = 0
                                for length in range(min(self.max_keyword_len, len(source) - j), 0, -1):
                                    if source[j:j+length] in self.keywords:
                                        found_keyword = True
                                        found_keyword_len = length
                                        break
                                
                                if found_keyword:
                                    # 检查这个关键字是否是动词（单字动词）
                                    # 如果是动词，停止收集；如果不是动词，继续收集
                                    keyword = source[j:j+found_keyword_len]
                                    # 单字动词列表（不包括比较操作符，因为它们可能出现在变量名中）
                                    verbs = {'加', '减', '乘', '除', '模', '幂',
                                             '且', '或', '非', '首', '余', '入', '长', '添', '连',
                                             '含', '空', '皆', '只', '归', '潜', '印', '读', '写',
                                             '若', '则', '定', '函', '行', '真', '假'}
                                    if keyword in verbs:
                                        # 是动词，停止收集
                                        break
                                    else:
                                        # 不是动词（如"小"），继续收集
                                        j += found_keyword_len
                                        continue
                                j += 1

                            # 提取变量名
                            var_name = source[i:j]

                            # 跳过空白
                            k = j
                            while k < len(source) and source[k] in ' \t':
                                k += 1

                            # 检查后面是否跟着 '=' 或动词（确认是变量名）
                            should_be_var = False
                            if k < len(source):
                                # 如果跟着 '='，肯定是变量定义
                                if source[k] == '=':
                                    should_be_var = True
                                # 如果跟着动词，说明这是变量名
                                elif self._is_han(source[k]):
                                    # 检查下一个token是否是动词
                                    next_is_verb = False
                                    for length in range(min(self.max_keyword_len, len(source) - k), 0, -1):
                                        if source[k:k+length] in self.keywords:
                                            next_is_verb = True
                                            break

                                    # 只有当下一个token是动词时，才确认是变量名
                                    if next_is_verb:
                                        should_be_var = True
                                # 如果跟着句号，也确认为变量名
                                elif source[k] == '。':
                                    should_be_var = True

                            if should_be_var:
                                tokens.append(Token(TokenType.WORD, var_name, line, col))
                                col += len(var_name)
                                i = j
                                continue

                    # 尝试中文数字识别
                    if is_chinese_number:
                        # 尝试匹配最长的中文数字
                        j = i
                        while j < len(source) and self._is_han(source[j]):
                            candidate = source[i:j+1]
                            if is_chinese_number(candidate):
                                j += 1
                            else:
                                break
                        
                        if j > i:
                            chinese_num = source[i:j]
                            try:
                                value = chinese_to_number(chinese_num)
                                tokens.append(Token(TokenType.NUM, value, line, col))
                                col += j - i
                                i = j
                                continue
                            except (ValueError, KeyError):
                                # 不是有效的中文数字，继续正常处理
                                pass

                    # 非关键字的汉字：收集连续的汉字作为一个标识符
                    # 这样 "安全" 会被作为一个标识符
                    j = i
                    while j < len(source) and self._is_han(source[j]):
                        # 检查是否遇到关键字
                        candidate = source[j:j+1]
                        if candidate in self.keywords:
                            # 如果是用户定义的标识符的一部分，不拆分
                            full_so_far = source[i:j+1]
                            if full_so_far in user_defined_names:
                                j += 1
                                continue
                            # "则"、"若"、"定"、"函"、"真"、"假"等结构关键字
                            # 仅在后面恰好只跟一个汉字时才作为标识符的一部分
                            # 如"规则表"（则+表=1字）是合法标识符
                            # 如"带则扩展"（则+扩展=2字）、"符号则"（则后非汉字）都应按关键字处理
                            if candidate in {'则', '若', '定', '函', '真', '假'}:
                                if (j + 2 < len(source) and 
                                    self._is_han(source[j+1]) and 
                                    not self._is_han(source[j+2])):
                                    j += 1
                                    continue  # 关键字后恰跟一个汉字，作为标识符一部分
                                if (j + 1 == len(source) - 1 and 
                                    self._is_han(source[j+1])):
                                    j += 1
                                    continue  # 关键字后恰跟一个汉字（行尾），作为标识符一部分
                            # 检查是否为多字关键字且整个是用户定义的标识符
                            for length in range(min(self.max_keyword_len, len(source) - j), 1, -1):
                                kw_candidate = source[j:j+length]
                                if kw_candidate in self.keywords:
                                    full_kw = source[i:j+length]
                                    if full_kw in user_defined_names:
                                        j += length
                                        break
                            else:
                                break  # 遇到关键字，停止收集
                            continue
                        # 检查下一个多字是否是关键字（长度>=2）
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
            raise self._create_error(f"未知字符: {ch}", line, col)

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
