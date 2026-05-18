#!/usr/bin/env python3
"""
言语言优化词法分析器

使用有限状态机和缓存机制提升性能
"""

from typing import Optional, List, Tuple, Set, Dict
from enum import Enum, auto
from dataclasses import dataclass
import re


class TokenType(Enum):
    """Token类型"""
    WORD = "WORD"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OPERATOR = "OPERATOR"
    DOT = "DOT"  # 句号
    COMMA = "COMMA"  # 逗号
    COLON = "COLON"  # 冒号
    SEMI = "SEMI"  # 分号
    EQUALS = "EQUALS"
    ELLIPSIS = "ELLIPSIS"  # 省略号
    EOF = "EOF"
    ERROR = "ERROR"
    PYTHON_CODE = "PYTHON_CODE"
    MATH_EXPR = "MATH_EXPR"
    COMMENT = "COMMENT"


@dataclass
class Token:
    """Token"""
    type: TokenType
    value: str
    line: int
    col: int


class LexerState(Enum):
    """词法分析器状态"""
    INITIAL = auto()
    IN_WORD = auto()
    IN_NUMBER = auto()
    IN_STRING = auto()
    IN_PYTHON_CODE = auto()
    IN_MATH_EXPR = auto()


class CharBuffer:
    """字符缓冲区，减少字符串切片开销"""
    
    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """查看指定偏移的字符"""
        pos = self.pos + offset
        if 0 <= pos < self.length:
            return self.source[pos]
        return None
    
    def peek_range(self, start: int, end: int) -> str:
        """查看字符范围"""
        return self.source[start:end]
    
    def advance(self, count: int = 1) -> str:
        """前进指定字符数"""
        result = self.source[self.pos:self.pos + count]
        self.pos += count
        return result
    
    def match(self, expected: str) -> bool:
        """匹配字符串"""
        return self.source[self.pos:self.pos + len(expected)] == expected
    
    def reset(self, pos: int = 0):
        """重置位置"""
        self.pos = pos


class TokenCache:
    """Token缓存"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: Dict[int, List[Token]] = {}
    
    def get(self, key: int) -> Optional[List[Token]]:
        """获取缓存的tokens"""
        return self._cache.get(key)
    
    def set(self, key: int, tokens: List[Token]):
        """设置缓存"""
        if len(self._cache) >= self.max_size:
            # 简单策略：清除一半
            keys_to_remove = list(self._cache.keys())[:self.max_size // 2]
            for k in keys_to_remove:
                del self._cache[k]
        self._cache[key] = tokens
    
    def clear(self):
        """清除缓存"""
        self._cache.clear()


class KeywordSet:
    """优化的关键字集合"""
    
    def __init__(self):
        # 关键字集合（用于O(1)查找）
        self._keywords: Set[str] = set()
        # 关键字到token类型的映射
        self._keyword_types: Dict[str, TokenType] = {}
        self._init_keywords()
    
    def _init_keywords(self):
        """初始化关键字"""
        keywords = [
            # 控制流
            '若', '则', '否则', '若非',
            '遍历', '当', '循环',
            # 定义
            '定', '函', '结构', '构',
            # 布尔
            '真', '假', '空', '无', '是', '否',
            # 列表
            '列', '典', '序', '范围',
            # 高阶函数
            '皆', '只', '归', '潜',
            # I/O
            '印', '读', '写', '行',
            # 模块
            '引', '入', '出',
            # 其他
            '首', '余', '长', '添', '连', '含',
            '测', '套', '注',
        ]
        
        for kw in keywords:
            self._keywords.add(kw)
    
    def add_user_keyword(self, keyword: str):
        """添加用户定义的关键字"""
        self._keywords.add(keyword)
    
    def is_keyword(self, word: str) -> bool:
        """检查是否是关键字"""
        return word in self._keywords


class OptimizedLexer:
    """优化的词法分析器"""
    
    def __init__(self, user_keywords: Optional[Set[str]] = None):
        self.buffer: Optional[CharBuffer] = None
        self.pos: int = 0
        self.line: int = 1
        self.col: int = 1
        self.source: str = ""
        
        self.cache = TokenCache()
        self.keywords = KeywordSet()
        
        # 添加用户关键字
        if user_keywords:
            for kw in user_keywords:
                self.keywords.add_user_keyword(kw)
        
        # 编译正则表达式（缓存）
        self._re_number = re.compile(r'^-?\d+\.?\d*$')
        self._re_word = re.compile(r'^[\u4e00-\u9fff\w]+$')
    
    def tokenize(self, source: str) -> List[Token]:
        """分词
        
        Args:
            source: 源代码
        
        Returns:
            Token列表
        """
        # 检查缓存
        cache_key = hash(source)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        self.source = source
        self.buffer = CharBuffer(source)
        self.buffer.reset()
        self.pos = 0
        self.line = 1
        self.col = 1
        
        tokens = []
        
        while not self._is_at_end():
            token = self._next_token()
            if token.type != TokenType.COMMENT:
                tokens.append(token)
        
        tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        
        # 缓存结果
        self.cache.set(cache_key, tokens)
        
        return tokens
    
    def _next_token(self) -> Token:
        """获取下一个token"""
        start_line = self.line
        start_col = self.col
        
        # 跳过空白
        self._skip_whitespace()
        
        if self._is_at_end():
            return Token(TokenType.EOF, None, start_line, start_col)
        
        ch = self._peek()
        
        # 注释
        if self._match('--') or ch == '注':
            return self._read_comment(start_line, start_col)
        
        # Python代码块
        if self._match('{{'):
            return self._read_python_code(start_line, start_col)
        
        # 数学表达式
        if self._match('$('):
            return self._read_math_expr(start_line, start_col)
        
        # 数字
        if ch.isdigit() or (ch == '-' and self._peek_next().isdigit()):
            return self._read_number(start_line, start_col)
        
        # 字符串
        if ch in '""「」':
            return self._read_string(start_line, start_col)
        
        # 单引号字符串
        if ch == "'":
            return self._read_single_quote_string(start_line, start_col)
        
        # 中文标点
        if ch == '。':
            self._advance()
            return Token(TokenType.DOT, '。', start_line, start_col)
        
        if ch == '，':
            self._advance()
            return Token(TokenType.COMMA, '，', start_line, start_col)
        
        if ch == '；':
            self._advance()
            return Token(TokenType.SEMI, '；', start_line, start_col)
        
        if ch == '：':
            self._advance()
            return Token(TokenType.COLON, '：', start_line, start_col)
        
        # 省略号
        if self._match('...'):
            return Token(TokenType.ELLIPSIS, '...', start_line, start_col)
        
        # 英文点号
        if ch == '.':
            self._advance()
            return Token(TokenType.DOT, '.', start_line, start_col)
        
        # 英文括号
        if ch == '(':
            self._advance()
            return Token(TokenType.WORD, '(', start_line, start_col)
        
        if ch == ')':
            self._advance()
            return Token(TokenType.WORD, ')', start_line, start_col)
        
        # 等号
        if ch == '=':
            self._advance()
            return Token(TokenType.EQUALS, '=', start_line, start_col)
        
        # 单词
        if self._is_word_char(ch):
            return self._read_word(start_line, start_col)
        
        # 未知字符
        self._advance()
        return Token(TokenType.ERROR, ch, start_line, start_col)
    
    def _read_word(self, line: int, col: int) -> Token:
        """读取单词"""
        start = self.pos
        while not self._is_at_end() and self._is_word_char(self._peek()):
            self._advance()
        value = self.source[start:self.pos]
        
        # 检查是否是关键字
        if self.keywords.is_keyword(value):
            return Token(TokenType.WORD, value, line, col)
        
        return Token(TokenType.WORD, value, line, col)
    
    def _read_number(self, line: int, col: int) -> Token:
        """读取数字"""
        start = self.pos
        
        # 负号
        if self._peek() == '-':
            self._advance()
        
        # 整数部分
        while not self._is_at_end() and self._peek().isdigit():
            self._advance()
        
        # 小数部分
        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance()  # 吃掉点
            while not self._is_at_end() and self._peek().isdigit():
                self._advance()
        
        value = self.source[start:self.pos]
        
        try:
            if '.' in value:
                return Token(TokenType.NUMBER, float(value), line, col)
            else:
                return Token(TokenType.NUMBER, int(value), line, col)
        except ValueError:
            return Token(TokenType.ERROR, value, line, col)
    
    def _read_string(self, line: int, col: int) -> Token:
        """读取字符串"""
        quote = self._peek()
        self._advance()  # 开始引号
        
        chars = []
        while not self._is_at_end() and self._peek() != quote:
            ch = self._peek()
            if ch == '\\':
                self._advance()
                if not self._is_at_end():
                    escaped = self._advance()
                    escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"'}
                    chars.append(escape_map.get(escaped, escaped))
            else:
                chars.append(ch)
                self._advance()
        
        if self._is_at_end():
            return Token(TokenType.ERROR, '未闭合的字符串', line, col)
        
        self._advance()  # 结束引号
        value = ''.join(chars)
        return Token(TokenType.STRING, value, line, col)
    
    def _read_single_quote_string(self, line: int, col: int) -> Token:
        """读取单引号字符串"""
        return self._read_string(line, col)
    
    def _read_comment(self, line: int, col: int) -> Token:
        """读取注释"""
        start = self.pos
        while not self._is_at_end() and self._peek() != '\n':
            self._advance()
        value = self.source[start:self.pos]
        return Token(TokenType.COMMENT, value, line, col)
    
    def _read_python_code(self, line: int, col: int) -> Token:
        """读取Python代码块"""
        start = self.pos
        depth = 1
        
        while not self._is_at_end() and depth > 0:
            if self._match('{{'):
                depth += 1
            elif self._match('}}'):
                depth -= 1
                if depth == 0:
                    break
            self._advance()
        
        value = self.source[start:self.pos]
        if not self._is_at_end():
            self._advance()  # 吃掉 }}
            self._advance()  # 吃掉最后一个 }
        value = value[:-2]  # 去掉 {{
        
        return Token(TokenType.PYTHON_CODE, value.strip(), line, col)
    
    def _read_math_expr(self, line: int, col: int) -> Token:
        """读取数学表达式"""
        start = self.pos - 2  # 包含 $(
        
        while not self._is_at_end() and self._peek() != ')':
            self._advance()
        
        if not self._is_at_end():
            self._advance()  # 吃掉 )
        
        value = self.source[start:self.pos]
        return Token(TokenType.MATH_EXPR, value[2:-1], line, col)
    
    def _skip_whitespace(self):
        """跳过空白字符"""
        while not self._is_at_end():
            ch = self._peek()
            if ch in ' \t\r':
                self._advance()
            elif ch == '\n':
                self._advance()
                self.line += 1
                self.col = 1
            else:
                break
    
    def _is_word_char(self, ch: str) -> bool:
        """检查是否是单词字符"""
        if not ch:
            return False
        # 中文
        if '\u4e00' <= ch <= '\u9fff':
            return True
        # 字母数字下划线
        if ch.isalnum() or ch == '_':
            return True
        return False
    
    def _peek(self) -> Optional[str]:
        """查看当前字符"""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None
    
    def _peek_next(self) -> Optional[str]:
        """查看下一个字符"""
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return None
    
    def _advance(self) -> str:
        """前进一个字符"""
        ch = self.source[self.pos]
        self.pos += 1
        self.col += 1
        return ch
    
    def _match(self, expected: str) -> bool:
        """匹配字符串"""
        return self.source[self.pos:self.pos + len(expected)] == expected
    
    def _is_at_end(self) -> bool:
        """检查是否到达末尾"""
        return self.pos >= len(self.source)
