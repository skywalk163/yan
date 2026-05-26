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
    INDENT = auto()    # 缩进增加（用于块开始）
    DEDENT = auto()    # 缩进减少（用于块结束）
    NEWLINE = auto()   # 换行符
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

    # 预定义的多字关键字集合（类级缓存）
    _MULTI_CHAR_KEYWORDS = frozenset({
        '定义', '函数', '如果', '那么', '当时', '否则', '不等于',
        '等于', '遍历', '于', '导入', '模块', '导出', '从', '引', '出',
        '结构', '类型', '字段', '正弦', '余弦', '正切', '反正弦', '反余弦', '反正切',
        '指数', '对数', '对数10', '开方', '取整', '进位', '四舍五入',
        '随机', '随机整数', '圆周率', '自然常数', '长度', '添加', '连接', '分割', '替换', '截取',
        '小写', '大写', '查找', '包含', '去空', '开头是', '结尾是',
        '读文件', '写文件', '追加文件', '存在', '是文件', '是目录',
        '列目录', '建目录', '删文件', '删目录', '当前目录',
        '文件名', '目录名', '扩展名', '当前时间', '日期', '时间', '日期时间',
        '格式化时间', '睡眠', '是数', '是串', '是表', '是函', '是真', '是空',
        '大于', '大等于', '小于', '小等于', '最大', '最小', '求和', '计数',
        '键', '值', '项', '删键', '求值', '套', '测', '范围',
        '列表', '字典', '序列', '对组', '输出', '读取', '写入', '映射', '过滤', '归约',
        '阶乘', '平方',
        # 双字关键字（原单字关键字转换）
        '相加', '相减', '相乘', '相除', '取余', '幂方', '绝对值', '负数',
        '并且', '或者', '非也',
        '首个', '其余', '加入', '为空',
        '潜在', '换行', '空值',
        '反转', '排序',
        '当满足', '打印',
    })

    # 预定义的单字关键字集合（类级缓存）
    _SINGLE_CHAR_KEYWORDS = frozenset({
        '真', '假', '读行', '返回',
    })

    def __init__(self, keywords: Optional[Set[str]] = None, user_words: Optional[Set[str]] = None):
        self._source = None  # 保存源代码用于错误显示
        
        # 合并用户关键字和预定义关键字
        self.keywords = set(self._MULTI_CHAR_KEYWORDS) | set(self._SINGLE_CHAR_KEYWORDS)
        if keywords:
            self.keywords.update(keywords)
        
        # 预计算关键字长度相关数据
        self.keywords_by_length = {}
        self.max_keyword_len = 0
        for kw in self.keywords:
            l = len(kw)
            if l not in self.keywords_by_length:
                self.keywords_by_length[l] = set()
            self.keywords_by_length[l].add(kw)
            if l > self.max_keyword_len:
                self.max_keyword_len = l
        
        self.user_words = user_words or set()  # 用户定义的词（不拆分）
        
        # 百家姓变量识别
        self.surnames = BAIJIAXING
        self.conflicting_surnames = CONFLICTING_SURNAMES
        self.max_surname_len = max(len(k) for k in self.surnames) if self.surnames else 2
        
        # 已知多字符词：这些词即使以关键字开头，也应该作为整体输出
        # （由于关键字已双字化，此集合已大大简化）
        self.known_multi_char_words = frozenset({
            '数据', '结果', '变量', '方法', '类', '对象',
            '字符串', '数字', '布尔', '数组', '集合', '元组',
            '文件', '目录', '路径', '模块', '包', '库',
            '网络', '请求', '响应', '连接', '端口', '协议',
            '错误', '异常', '警告', '信息', '调试',
            '配置', '设置', '选项', '参数', '返回值',
        })
        
        # 预编译常用字符判断函数
        self._is_han = self._create_han_check()
        self._is_ident_char_func = self._create_ident_char_check()

    def _create_han_check(self):
        """创建优化的汉字检查函数"""
        HAN_START, HAN_END = self.HAN_START, self.HAN_END
        def check(ch):
            if not ch:
                return False
            cp = ord(ch)
            return HAN_START <= cp <= HAN_END
        return check

    def _create_ident_char_check(self):
        """创建优化的标识符字符检查函数"""
        is_han = self._is_han
        def check(ch):
            if not ch:
                return False
            return is_han(ch) or ch.isalnum() or ch == '_'
        return check

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
            
            # 查找 '定义'
            if source[i:i+2] == '定义':
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

    @staticmethod
    def _is_chinese(ch: str) -> bool:
        """检查字符是否是中文"""
        return '\u4e00' <= ch <= '\u9fff'

    def _create_error(self, message: str, line: int, col: int) -> EnhancedLexerError:
        """创建增强版词法分析错误"""
        location = SourceLocation(line, col)
        suggestion = ErrorSuggester.suggest(message)
        return EnhancedLexerError(message, location, self._source, suggestion)

    def tokenize(self, source: str) -> List[Token]:
        """将源码转为 Token 流（支持缩进语法和续行）"""
        self._source = source  # 保存源代码用于错误显示
        
        # 第一阶段：轻量扫描收集所有用户定义的标识符
        user_defined_names = self._scan_user_defs(source)
        
        # 第二阶段：预处理续行，然后逐行处理缩进
        # 续行规则：
        # - 如果下一行缩进 == 当前行缩进，且当前行不以句号结尾，则视为续行
        # - 但是，如果当前行以块开始关键字开头或结尾，则不续行
        
        lines = source.splitlines()
        processed_lines = []
        
        # 语句开始关键字（这些关键字开头的行不应与下一行续行）
        statement_start_keywords = {'定义', '如果', '那么', '否则', '遍历', '当时', '函数', '返回', '结构', '套', '测', '打印', '读', '写', '引', '导', '出'}
        # 块开始关键字（这些关键字结尾的行不应与下一行续行）
        block_start_keywords = {'函数', '如果', '遍历', '当时', '结构', '套', '测'}
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 检查行内容
            stripped = line.strip()
            
            # 如果是空行或注释，直接保留（不进行续行处理）
            if not stripped or stripped.startswith('--') or stripped.startswith('注'):
                processed_lines.append(line)
                i += 1
                continue
            
            # 检查是否需要续行
            current_indent = self._count_indent(line)
            has_dot = line.rstrip().endswith('。') or line.rstrip().endswith('．')
            
            # 检查是否以块开始关键字结尾
            ends_with_block_start = False
            for kw in block_start_keywords:
                if stripped.endswith(kw):
                    ends_with_block_start = True
                    break
            
            # 检查是否以语句开始关键字开头
            starts_with_statement = False
            for kw in statement_start_keywords:
                if stripped.startswith(kw):
                    starts_with_statement = True
                    break
            
            # 查看下一行
            should_merge = False
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.strip()
                
                # 如果下一行不是空行或注释
                if next_stripped and not next_stripped.startswith('--') and not next_stripped.startswith('注'):
                    next_indent = self._count_indent(next_line)
                    
                    # 如果满足以下条件，则续行：
                    # 1. 下一行缩进 == 当前行缩进
                    # 2. 当前行不以句号结尾
                    # 3. 当前行不以块开始关键字结尾
                    # 4. 当前行不以语句开始关键字开头
                    if (next_indent == current_indent and 
                        not has_dot and 
                        not ends_with_block_start and 
                        not starts_with_statement):
                        should_merge = True
                        line = line.rstrip() + ' ' + next_stripped
                        i += 1  # 跳过下一行
            
            processed_lines.append(line)
            i += 1
        
        # 第三阶段：处理缩进和 token 化
        tokens = []
        indent_stack = [0]  # 当前缩进栈
        current_indent = 0
        
        for line_num, line in enumerate(processed_lines, 1):
            # 计算当前行的缩进
            line_indent = 0
            col = 1
            i = 0
            while i < len(line) and line[i] in ' \t':
                if line[i] == '\t':
                    line_indent += 4
                else:
                    line_indent += 1
                i += 1
                col += 1
            
            # 处理缩进变化
            if line_indent > current_indent:
                # 缩进增加
                tokens.append(Token(TokenType.INDENT, str(line_indent), line_num, 1))
                indent_stack.append(line_indent)
                current_indent = line_indent
            elif line_indent < current_indent:
                # 缩进减少，生成 DEDENT
                while current_indent > line_indent:
                    indent_stack.pop()
                    current_indent = indent_stack[-1] if indent_stack else 0
                    tokens.append(Token(TokenType.DEDENT, str(current_indent), line_num, 1))
            
            # 处理行内容（跳过前面的空白）
            self._tokenize_line(line[i:], line_num, col, tokens, user_defined_names)
        
        # 文件结束：生成剩余的 DEDENT
        while len(indent_stack) > 1:
            indent_stack.pop()
            current_indent = indent_stack[-1]
            # 使用最后一个有效 token 的位置信息
            last_tok = None
            for tok in reversed(tokens):
                if tok.type != TokenType.EOF:
                    last_tok = tok
                    break
            if last_tok:
                tokens.append(Token(TokenType.DEDENT, str(current_indent), last_tok.line, last_tok.col))
            else:
                tokens.append(Token(TokenType.DEDENT, str(current_indent), 1, 1))
        
        # 添加 EOF token
        last_line, last_col = 1, 1
        if tokens:
            last_tok = tokens[-1]
            last_line, last_col = last_tok.line, last_tok.col
        tokens.append(Token(TokenType.EOF, None, last_line, last_col))
        
        return tokens
    
    def _count_indent(self, line: str) -> int:
        """计算行的缩进级别"""
        indent = 0
        for ch in line:
            if ch == '\t':
                indent += 4
            elif ch == ' ':
                indent += 1
            else:
                break
        return indent
    
    def _tokenize_line(self, line: str, line_num: int, start_col: int, tokens: List[Token], user_defined_names: Set[str]) -> None:
        """处理单行的 token 化"""
        i = 0
        col = start_col
        n = len(line)
        
        while i < n:
            ch = line[i]
            
            # 跳过行内空白
            if ch in ' \t\r':
                col += 1
                i += 1
                continue
            
            # 注释：-- 开头到行尾
            if i + 1 < n and line[i:i+2] == '--':
                return
            
            # 注释：注 开头到行尾
            if ch == '注':
                return
            
            # 字符串
            if ch == '"':
                # 双引号字符串
                i += 1
                col += 1
                start_col_in = col
                chars = []
                while i < n and line[i] != '"':
                    if line[i] == '\\' and i + 1 < n:
                        if line[i+1] == 't':
                            chars.append('\t')
                        elif line[i+1] == 'n':
                            chars.append('\n')
                        elif line[i+1] == 'r':
                            chars.append('\r')
                        elif line[i+1] == '\\':
                            chars.append('\\')
                        elif line[i+1] == '"':
                            chars.append('"')
                        else:
                            chars.append(line[i+1])
                        i += 2
                        col += 2
                    else:
                        chars.append(line[i])
                        i += 1
                        col += 1
                if i >= n:
                    raise self._create_error("字符串未闭合", line_num, start_col)
                tokens.append(Token(TokenType.STR, ''.join(chars), line_num, start_col_in))
                i += 1
                col += 1
                continue
            
            # 单引号字符串或引用符
            if ch == "'":
                j = i + 1
                found_closing = False
                while j < n:
                    if line[j] == "'":
                        found_closing = True
                        break
                    j += 1
                if found_closing:
                    # 单引号字符串
                    i += 1
                    content = line[i:j]
                    tokens.append(Token(TokenType.STR, content, line_num, col))
                    i = j + 1
                    col = col + (j - i + 2)
                    continue
                else:
                    # 引用符
                    tokens.append(Token(TokenType.QUOTE, "'", line_num, col))
                    i += 1
                    col += 1
                    continue
            
            # 数字
            if ch.isdigit() or (ch == '-' and i+1 < n and line[i+1].isdigit()):
                start = i
                if ch == '-':
                    i += 1
                    col += 1
                while i < n and line[i].isdigit():
                    i += 1
                    col += 1
                if i < n and line[i] == '.':
                    i += 1
                    col += 1
                    while i < n and line[i].isdigit():
                        i += 1
                        col += 1
                num_str = line[start:i]
                # 转换为数字
                if '.' in num_str:
                    num_value = float(num_str)
                else:
                    num_value = int(num_str)
                tokens.append(Token(TokenType.NUM, num_value, line_num, start_col + start - 1))
                continue
            
            # 数学表达式
            if i + 1 < n and line[i:i+2] == '$(':
                j = i + 2
                depth = 1
                while j < n and depth > 0:
                    if line[j] == '(':
                        depth += 1
                    elif line[j] == ')':
                        depth -= 1
                    j += 1
                if depth > 0:
                    raise self._create_error("数学表达式括号未闭合", line_num, col)
                content = line[i+2:j-1]
                tokens.append(Token(TokenType.MATH, content, line_num, col))
                i = j
                col += (j - i)
                continue
            
            # Python 嵌入代码
            if i + 1 < n and line[i:i+2] == '{{':
                j = i + 2
                depth = 1
                while j < n and depth > 0:
                    if j + 1 < n and line[j:j+2] == '{{':
                        depth += 1
                        j += 2
                    elif j + 1 < n and line[j:j+2] == '}}':
                        depth -= 1
                        j += 2
                    else:
                        j += 1
                content = line[i+2:j-2]
                tokens.append(Token(TokenType.PYTHON, content, line_num, col))
                i = j
                col += (j - i)
                continue
            
            # 符号
            if ch == '。' or ch == '．':
                tokens.append(Token(TokenType.DOT, '。', line_num, col))
                i += 1
                col += 1
                continue
            if ch == '，':
                tokens.append(Token(TokenType.COMMA, '，', line_num, col))
                i += 1
                col += 1
                continue
            if ch == ',':
                tokens.append(Token(TokenType.COMMA, '，', line_num, col))
                i += 1
                col += 1
                continue
            if ch == '；':
                tokens.append(Token(TokenType.SEMI, '；', line_num, col))
                i += 1
                col += 1
                continue
            if ch == '：':
                tokens.append(Token(TokenType.COLON, '：', line_num, col))
                i += 1
                col += 1
                continue
            if ch == '=':
                tokens.append(Token(TokenType.EQUALS, '=', line_num, col))
                i += 1
                col += 1
                continue
            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, '(', line_num, col))
                i += 1
                col += 1
                continue
            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, ')', line_num, col))
                i += 1
                col += 1
                continue
            
            # 省略号
            if i + 2 < n and line[i:i+3] == '...':
                tokens.append(Token(TokenType.ELLIPSIS, '...', line_num, col))
                i += 3
                col += 3
                continue
            
            # 英文点号
            if ch == '.':
                tokens.append(Token(TokenType.DOT_EN, '.', line_num, col))
                i += 1
                col += 1
                continue
            
            # 标识符和关键字（优化版本）
            if self._is_chinese(ch) or ch.isalpha() or ch in '_':
                start = i
                
                # 如果是汉字开头，优先收集完整的汉字标识符
                if self._is_chinese(ch):
                    # 先收集所有连续汉字（不包含数字）
                    han_end = i + 1
                    while han_end < n and self._is_chinese(line[han_end]):
                        han_end += 1
                    
                    # 继续收集后面的数字（支持 "变量0" 这样的标识符）
                    end = han_end
                    while end < n and line[end].isdigit():
                        end += 1
                    
                    # 获取汉字部分和完整标识符
                    han_part = line[i:han_end]
                    full_identifier = line[i:end]
                    
                    # 首先尝试最长匹配关键字（贪心算法）
                    matched_length = self._match_keyword(line, i, n)
                    if matched_length > 0:
                        keyword = line[i:i+matched_length]
                        # 检查剩余部分是否应该合并
                        remaining = line[i+matched_length:end]
                        # 只有当剩余部分是单个非关键字汉字时才考虑合并
                        # 但如果剩余部分是数字，不合并（如 "列表1" -> "列表" + "1"）
                        # 如果剩余部分是多个字符，不合并（如 "函数数" -> "函数" + "数"）
                        if len(remaining) == 1 and remaining not in self.keywords and self._is_chinese(remaining):
                            # 剩余部分是单个非关键字汉字，作为整体标识符输出（如 "排序后" -> "排序后"）
                            tokens.append(Token(TokenType.WORD, full_identifier, line_num, col))
                            i = end
                            col += len(full_identifier)
                            continue
                        # 正常输出关键字
                        tokens.append(Token(TokenType.WORD, keyword, line_num, col))
                        i += matched_length
                        col += matched_length
                        continue
                    elif end > i + 1:
                        # 完整标识符不是关键字（如 "列表"），但有多个汉字
                        # 优先检查是否是用户定义的名称（避免拆分用户变量名）
                        if full_identifier in user_defined_names:
                            tokens.append(Token(TokenType.WORD, full_identifier, line_num, col))
                            i = end
                            col += len(full_identifier)
                            continue
                        
                        # 检查第一个汉字是否是关键字
                        first_char = line[i]
                        if first_char in self.keywords:
                            # 检查是否是已知多字符词
                            if full_identifier in self.known_multi_char_words:
                                # 已知多字符词，输出完整标识符
                                tokens.append(Token(TokenType.WORD, full_identifier, line_num, col))
                                i = end
                                col += len(full_identifier)
                                continue
                            # 第一个汉字是关键字符，输出第一个字符
                            # 继续处理剩余部分
                            tokens.append(Token(TokenType.WORD, first_char, line_num, col))
                            i = i + 1
                            col += 1
                            # 继续循环，让后面的字符重新处理
                            continue
                        elif end > i + 2 and line[i:i+2] in self.keywords:
                            # 前两个字符是关键字符（如 "否则"），但只有在不是用户定义名称时才拆分
                            # 检查剩余部分是否能组成有效标识符（避免错误拆分）
                            remaining = line[i+2:end]
                            if remaining == '' or remaining in self.keywords or remaining[0] in self.keywords:
                                # 剩余部分是关键字或空，安全拆分
                                tokens.append(Token(TokenType.WORD, line[i:i+2], line_num, col))
                                i = i + 2
                                col += 2
                                continue
                            else:
                                # 剩余部分不是关键字，作为整体标识符输出
                                tokens.append(Token(TokenType.WORD, full_identifier, line_num, col))
                                i = end
                                col += len(full_identifier)
                                continue
                        else:
                            # 第一个汉字也不是关键字，输出完整标识符
                            tokens.append(Token(TokenType.WORD, full_identifier, line_num, col))
                            i = end
                            col += len(full_identifier)
                            continue
                    else:
                        # 只有一个汉字，检查是否是关键字
                        matched_length = self._match_keyword(line, i, n)
                        if matched_length > 0:
                            keyword = line[i:i+matched_length]
                            tokens.append(Token(TokenType.WORD, keyword, line_num, col))
                            i += matched_length
                            col += matched_length
                            continue
                        else:
                            # 不是关键字，输出单个汉字作为标识符
                            tokens.append(Token(TokenType.WORD, ch, line_num, col))
                            i += 1
                            col += 1
                            continue
                
                # 如果是字母或下划线开头，只收集 ASCII 字母、数字和下划线
                end = i + 1
                while end < n and (line[end].isascii() and (line[end].isalnum() or line[end] == '_')):
                    end += 1
                word = line[i:end]
                tokens.append(Token(TokenType.WORD, word, line_num, col))
                i = end
                col += len(word)
                continue
            
            # 未知字符
            raise self._create_error(f"未知字符: {ch}", line_num, col)
    
    def _match_keyword(self, line: str, pos: int, length: int) -> int:
        """快速匹配关键字，返回匹配长度，未匹配返回0
        
        使用预计算的按长度分组的关键字集合进行高效查找
        """
        max_possible = min(self.max_keyword_len, length - pos)
        
        # 从最长可能的长度开始尝试匹配
        for l in range(max_possible, 0, -1):
            if l in self.keywords_by_length:
                candidate = line[pos:pos+l]
                if candidate in self.keywords_by_length[l]:
                    return l
        return 0

    def _collect_chinese_identifier(self, line: str, start: int, length: int) -> str:
        """收集连续的汉字标识符
        
        收集所有连续的汉字（可能包含数字后缀），然后检查是否匹配关键字
        如果完整标识符匹配关键字，优先返回完整标识符
        否则返回完整标识符作为一个整体（用户自定义变量名）
        """
        # 先收集所有连续汉字
        end = start
        while end < length and self._is_chinese(line[end]):
            end += 1
        
        # 继续收集后面的数字（支持 "变量0" 这样的标识符）
        while end < length and line[end].isdigit():
            end += 1
        
        # 返回完整的标识符
        return line[start:end]
    
    def _tokenize_raw(self, source: str, user_defined_names: Set[str]) -> List[Token]:
        """生成基础 tokens（包含换行符和原始缩进信息）"""
        tokens = []
        i = 0
        line, col = 1, 1
        indent_stack = [0]  # 保存当前缩进级别栈
        
        while i < len(source):
            ch = source[i]
            
            # 处理换行和缩进
            if ch == '\n':
                # 记录换行前的内容结束位置
                tokens.append(Token(TokenType.NEWLINE, '\n', line, col))
                line += 1
                col = 1
                i += 1
                
                # 读取下一行的缩进
                indent = 0
                while i < len(source) and source[i] in ' \t':
                    if source[i] == '\t':
                        indent += 4  # 制表符视为4个空格
                    else:
                        indent += 1
                    col += 1
                    i += 1
                
                # 将缩进信息存储在特殊 token 中
                if indent > 0:
                    tokens.append(Token(TokenType.INDENT, str(indent), line, 1))
                continue
            
            # 跳过空白符（行内的空格和制表符）
            if ch in ' \t\r':
                col += 1
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
            
            # 支持英文逗号
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
            
            # 英文点号：用于模块成员访问
            if ch == '.':
                tokens.append(Token(TokenType.DOT_EN, '.', line, col))
                i += 1; col += 1
                continue
            
            # 英文左括号
            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, '(', line, col))
                i += 1; col += 1
                continue
            
            # 英文右括号
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
                    # 优先级1：检查是否是"定义"后面的变量名
                    if tokens and tokens[-1].type == TokenType.WORD and tokens[-1].value == '定义':
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
                    # 每个参数跟在函数后面，按关键字边界分割
                    if tokens and tokens[-1].type == TokenType.WORD and tokens[-1].value == '函数':
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
                                    verbs = {'相加', '相减', '相乘', '相除', '取余', '幂方',
                                             '并且', '或者', '非也', '首个', '其余', '加入', '长', '添', '连',
                                             '含', '为空', '皆', '只', '归', '潜在', '打印', '读', '写',
                                             '如果', '那么', '定义', '函数', '换行', '真', '假'}
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
                            # "那么"、"如果"、"定义"、"函数"、"真"、"假"等结构关键字
                            # 仅在后面恰好只跟一个汉字时才作为标识符的一部分
                            # 如"规那么表"（那么+表=1字）是合法标识符
                            # 如"带那么扩展"（那么+扩展=2字）、"符号那么"（那么后非汉字）都应按关键字处理
                            if candidate in {'真', '假'}:
                                if (j + 2 < len(source) and 
                                    self._is_han(source[j+1]) and 
                                    not self._is_han(source[j+2])):
                                    j += 1
                                    continue  # 关键字后恰跟一个汉字，作为标识符一部分
                                if (j + 1 == len(source) - 1 and 
                                    self._is_han(source[j+1])):
                                    j += 1
                                    continue  # 关键字后恰跟一个汉字（行尾），作为标识符一部分
                            # 检查双字关键字
                            two_char = source[j:j+2] if j+2 <= len(source) else ''
                            if two_char in {'那么', '如果', '定义', '函数'}:
                                if (j + 3 < len(source) and 
                                    self._is_han(source[j+2]) and 
                                    not self._is_han(source[j+3])):
                                    j += 2
                                    continue  # 双字关键字后恰跟一个汉字，作为标识符一部分
                                if (j + 2 == len(source) - 1 and 
                                    self._is_han(source[j+2])):
                                    j += 2
                                    continue  # 双字关键字后恰跟一个汉字（行尾），作为标识符一部分
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
    
    def _process_indent(self, raw_tokens: List[Token]) -> List[Token]:
        """
        处理缩进，将原始缩进信息转换为 INDENT/DEDENT tokens
        
        规则：
        1. 缩进增加 → 生成 INDENT
        2. 缩进减少 → 生成相应数量的 DEDENT
        3. 缩进不变 → 不生成任何 token
        """
        result = []
        indent_stack = [0]  # 保存当前缩进级别栈，初始为0
        current_indent = 0
        
        for tok in raw_tokens:
            if tok.type == TokenType.INDENT:
                # 解析缩进级别
                new_indent = int(tok.value)
                
                if new_indent > current_indent:
                    # 缩进增加，生成 INDENT token
                    result.append(Token(TokenType.INDENT, str(new_indent), tok.line, tok.col))
                    indent_stack.append(new_indent)
                    current_indent = new_indent
                elif new_indent < current_indent:
                    # 缩进减少，生成 DEDENT tokens
                    while current_indent > new_indent:
                        indent_stack.pop()
                        current_indent = indent_stack[-1] if indent_stack else 0
                        result.append(Token(TokenType.DEDENT, str(current_indent), tok.line, tok.col))
                # 缩进不变，不生成 token
                
                # 不将原始 INDENT token 添加到结果中
                continue
            
            elif tok.type == TokenType.NEWLINE:
                # 保留换行符，但在块结构中会被忽略
                # 我们将换行符转换为 DOT 来保持向后兼容
                # 或者直接忽略换行符，让解析器处理
                continue
            
            # 其他 tokens 直接添加
            result.append(tok)
        
        # 文件结束时，生成所有剩余的 DEDENT
        while len(indent_stack) > 1:
            indent_stack.pop()
            current_indent = indent_stack[-1]
            # 使用最后一个 token 的位置信息
            last_tok = result[-1] if result else Token(TokenType.EOF, None, 1, 1)
            result.append(Token(TokenType.DEDENT, str(current_indent), last_tok.line, last_tok.col))
        
        return result


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
